import adsk.core
import ctypes
import math
import os
import json
import threading
import time
import traceback


EVENT_ID = 'hookmaster.arrow_view_cube.rotate'
STEP_DEGREES = 5.0
POLL_INTERVAL_SECONDS = 0.015
INITIAL_REPEAT_DELAY_SECONDS = 0.28
REPEAT_INTERVAL_SECONDS = 0.045

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
DEFAULT_BINDINGS = {
    'left': 'LEFT',
    'right': 'RIGHT',
    'up': 'UP',
    'down': 'DOWN',
    'roll_modifier': 'CTRL',
}
NAMED_KEYS = {
    'BACKSPACE': 0x08,
    'TAB': 0x09,
    'ENTER': 0x0D,
    'SHIFT': 0x10,
    'CTRL': 0x11,
    'ALT': 0x12,
    'ESC': 0x1B,
    'SPACE': 0x20,
    'PAGEUP': 0x21,
    'PAGEDOWN': 0x22,
    'END': 0x23,
    'HOME': 0x24,
    'LEFT': 0x25,
    'UP': 0x26,
    'RIGHT': 0x27,
    'DOWN': 0x28,
    'INSERT': 0x2D,
    'DELETE': 0x2E,
}

_app = None
_custom_event = None
_event_handler = None
_poll_thread = None
_stop_event = threading.Event()
_state_lock = threading.Lock()
_pending_dx = 0
_pending_dy = 0
_pending_roll = 0
_event_queued = False


def _key_name_to_vk(name):
    normalized = str(name).strip().upper()
    if normalized in NAMED_KEYS:
        return NAMED_KEYS[normalized]
    if len(normalized) == 1 and (
        'A' <= normalized <= 'Z' or '0' <= normalized <= '9'
    ):
        return ord(normalized)
    if normalized.startswith('F') and normalized[1:].isdigit():
        number = int(normalized[1:])
        if 1 <= number <= 12:
            return 0x6F + number
    raise ValueError(
        'Unsupported key "{}". Use arrows, A-Z, 0-9, F1-F12, SPACE, '
        'ENTER, TAB, ESC, HOME, END, PAGEUP, PAGEDOWN, INSERT, or DELETE.'.format(name)
    )


def _load_bindings():
    bindings = dict(DEFAULT_BINDINGS)
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as settings_file:
            settings = json.load(settings_file)
        configured = settings.get('bindings', {})
        for action in DEFAULT_BINDINGS:
            if action in configured:
                bindings[action] = configured[action]
        resolved = {action: _key_name_to_vk(name) for action, name in bindings.items()}
        action_keys = [resolved[action] for action in ('left', 'right', 'up', 'down')]
        if len(set(action_keys)) != len(action_keys):
            raise ValueError('Each rotation action must use a different key.')
        return resolved
    except FileNotFoundError:
        return {action: _key_name_to_vk(name) for action, name in DEFAULT_BINDINGS.items()}
    except Exception as error:
        if _app:
            _app.log(
                'ArrowViewCube settings error; using default arrow keys: {}'.format(error)
            )
        return {action: _key_name_to_vk(name) for action, name in DEFAULT_BINDINGS.items()}


def _dot(a, b):
    return a.x * b.x + a.y * b.y + a.z * b.z


def _cross(a, b):
    return adsk.core.Vector3D.create(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x,
    )


def _scaled(v, scale):
    return adsk.core.Vector3D.create(v.x * scale, v.y * scale, v.z * scale)


def _add(a, b):
    return adsk.core.Vector3D.create(a.x + b.x, a.y + b.y, a.z + b.z)


def _normalized(v):
    result = adsk.core.Vector3D.create(v.x, v.y, v.z)
    if not result.normalize():
        raise RuntimeError('Cannot normalize a zero-length camera vector.')
    return result


def _rotate_vector(vector, axis, angle_radians):
    """Rodrigues rotation around a normalized axis."""
    axis = _normalized(axis)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    term_1 = _scaled(vector, cos_a)
    term_2 = _scaled(_cross(axis, vector), sin_a)
    term_3 = _scaled(axis, _dot(axis, vector) * (1.0 - cos_a))
    return _add(_add(term_1, term_2), term_3)


def _rotate_camera(dx, dy, roll):
    viewport = _app.activeViewport
    if not viewport:
        return

    camera = viewport.camera
    target = camera.target
    eye_offset = target.vectorTo(camera.eye)
    up = _normalized(camera.upVector)

    # Horizontal arrows orbit around the current camera-up direction.
    if dx:
        yaw = math.radians(-STEP_DEGREES * dx)
        eye_offset = _rotate_vector(eye_offset, up, yaw)

    # Vertical arrows orbit around the current screen-right direction.
    if dy:
        view_direction = _normalized(_scaled(eye_offset, -1.0))
        right = _normalized(_cross(view_direction, up))
        pitch = math.radians(STEP_DEGREES * dy)
        eye_offset = _rotate_vector(eye_offset, right, pitch)
        up = _rotate_vector(up, right, pitch)

    # Ctrl+horizontal arrows roll around the current viewing axis.
    if roll:
        view_direction = _normalized(_scaled(eye_offset, -1.0))
        # Camera orientation moves opposite to the rendered scene. Negating the
        # angle makes Ctrl+Right roll the visible model clockwise/right.
        roll_angle = math.radians(-STEP_DEGREES * roll)
        up = _rotate_vector(up, view_direction, roll_angle)

    camera.eye = adsk.core.Point3D.create(
        target.x + eye_offset.x,
        target.y + eye_offset.y,
        target.z + eye_offset.z,
    )
    camera.upVector = _normalized(up)
    camera.isSmoothTransition = False
    camera.isFitView = False
    viewport.camera = camera
    viewport.refresh()


class _RotateEventHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, _args):
        global _pending_dx, _pending_dy, _pending_roll, _event_queued
        try:
            with _state_lock:
                dx = _pending_dx
                dy = _pending_dy
                roll = _pending_roll
                _pending_dx = 0
                _pending_dy = 0
                _pending_roll = 0
                _event_queued = False
            if dx or dy or roll:
                _rotate_camera(dx, dy, roll)
        except Exception:
            _app.log('ArrowViewCube error:\n' + traceback.format_exc())


def _fusion_is_foreground():
    user32 = ctypes.windll.user32
    foreground = user32.GetForegroundWindow()
    if not foreground:
        return False
    process_id = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(foreground, ctypes.byref(process_id))
    return process_id.value == os.getpid()


def _queue_rotation(dx, dy, roll=0):
    global _pending_dx, _pending_dy, _pending_roll, _event_queued
    should_fire = False
    with _state_lock:
        _pending_dx += dx
        _pending_dy += dy
        _pending_roll += roll
        if not _event_queued:
            _event_queued = True
            should_fire = True
    if should_fire and _app:
        _app.fireCustomEvent(EVENT_ID)


def _poll_keyboard():
    user32 = ctypes.windll.user32
    bindings = _load_bindings()
    settings_mtime = None
    pressed_since = {}
    last_repeat = {}

    while not _stop_event.wait(POLL_INTERVAL_SECONDS):
        try:
            current_mtime = os.path.getmtime(SETTINGS_PATH)
        except OSError:
            current_mtime = None
        if current_mtime != settings_mtime:
            settings_mtime = current_mtime
            bindings = _load_bindings()
            pressed_since.clear()
            last_repeat.clear()

        keys = tuple(bindings.values())
        if not _fusion_is_foreground():
            pressed_since.clear()
            continue

        now = time.monotonic()
        fired = []
        for key in keys:
            is_down = bool(user32.GetAsyncKeyState(key) & 0x8000)
            if not is_down:
                pressed_since.pop(key, None)
                continue

            if key not in pressed_since:
                pressed_since[key] = now
                last_repeat[key] = now
                fired.append(key)
            elif (
                now - pressed_since[key] >= INITIAL_REPEAT_DELAY_SECONDS
                and now - last_repeat[key] >= REPEAT_INTERVAL_SECONDS
            ):
                last_repeat[key] = now
                fired.append(key)

        horizontal = int(bindings['right'] in fired) - int(bindings['left'] in fired)
        dy = int(bindings['up'] in fired) - int(bindings['down'] in fired)
        modifier_down = bool(
            user32.GetAsyncKeyState(bindings['roll_modifier']) & 0x8000
        )
        dx = 0 if modifier_down else horizontal
        roll = horizontal if modifier_down else 0
        if dx or dy or roll:
            _queue_rotation(dx, dy, roll)


def run(_context):
    global _app, _custom_event, _event_handler, _poll_thread
    try:
        _app = adsk.core.Application.get()
        try:
            _app.unregisterCustomEvent(EVENT_ID)
        except Exception:
            pass

        _custom_event = _app.registerCustomEvent(EVENT_ID)
        _event_handler = _RotateEventHandler()
        _custom_event.add(_event_handler)

        _stop_event.clear()
        _poll_thread = threading.Thread(
            target=_poll_keyboard,
            name='ArrowViewCubeKeyboardPoller',
            daemon=True,
        )
        _poll_thread.start()
        _app.log('ArrowViewCube started. Keyboard bindings loaded from settings.json.')
    except Exception:
        if _app:
            _app.log('ArrowViewCube startup error:\n' + traceback.format_exc())
        raise


def stop(_context):
    global _custom_event, _event_handler, _poll_thread, _app
    _stop_event.set()
    if _poll_thread and _poll_thread.is_alive():
        _poll_thread.join(timeout=0.5)
    _poll_thread = None

    if _custom_event and _event_handler:
        try:
            _custom_event.remove(_event_handler)
        except Exception:
            pass
    if _app:
        try:
            _app.unregisterCustomEvent(EVENT_ID)
        except Exception:
            pass
        _app.log('ArrowViewCube stopped.')

    _custom_event = None
    _event_handler = None
    _app = None
