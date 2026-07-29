import adsk.core
import ctypes
import math
import os
import json
import platform
import threading
import time
import traceback


IS_MAC = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'


EVENT_ID = 'hookmaster.arrow_view_cube.rotate'
STEP_DEGREES = 5.0
ZOOM_FACTOR = 1.2
POLL_INTERVAL_SECONDS = 0.015
INITIAL_REPEAT_DELAY_SECONDS = 0.28
REPEAT_INTERVAL_SECONDS = 0.045

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
DEFAULT_BINDINGS = {
    'left': 'LEFT',
    'right': 'RIGHT',
    'up': 'UP',
    'down': 'DOWN',
    # Platform-appropriate default modifier: Command on macOS, Ctrl on Windows.
    'roll_modifier': 'COMMAND' if IS_MAC else 'CTRL',
    'zoom_in': 'PAGEUP',
    'zoom_out': 'PAGEDOWN',
}
WINDOWS_KEYS = {
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
# macOS virtual key codes (kVK_ constants from Carbon/HIToolbox).
MAC_KEYS = {
    'BACKSPACE': 0x33,
    'TAB': 0x30,
    'ENTER': 0x24,
    'SHIFT': 0x38,
    'CTRL': 0x3B,
    'ALT': 0x3A,
    'COMMAND': 0x37,
    'ESC': 0x35,
    'SPACE': 0x31,
    'PAGEUP': 0x74,
    'PAGEDOWN': 0x79,
    'END': 0x77,
    'HOME': 0x73,
    'LEFT': 0x7B,
    'UP': 0x7E,
    'RIGHT': 0x7C,
    'DOWN': 0x7D,
    'INSERT': 0x72,
    'DELETE': 0x75,
    'F1': 0x7A,
    'F2': 0x78,
    'F3': 0x63,
    'F4': 0x76,
    'F5': 0x60,
    'F6': 0x61,
    'F7': 0x62,
    'F8': 0x64,
    'F9': 0x65,
    'F10': 0x6D,
    'F11': 0x67,
    'F12': 0x6F,
}
# macOS ANSI letter keycodes (kVK_ANSI_*). Unlike Windows, macOS letter codes
# are not ASCII values, so they must be mapped explicitly.
MAC_LETTERS = {
    'A': 0x00, 'B': 0x0B, 'C': 0x08, 'D': 0x02, 'E': 0x0E, 'F': 0x03,
    'G': 0x05, 'H': 0x04, 'I': 0x22, 'J': 0x26, 'K': 0x28, 'L': 0x25,
    'M': 0x2E, 'N': 0x2D, 'O': 0x1F, 'P': 0x23, 'Q': 0x0C, 'R': 0x0F,
    'S': 0x01, 'T': 0x11, 'U': 0x20, 'V': 0x09, 'W': 0x0D, 'X': 0x07,
    'Y': 0x10, 'Z': 0x06,
}
# macOS ANSI digit keycodes (kVK_ANSI_*).
MAC_DIGITS = {
    '0': 0x1D, '1': 0x12, '2': 0x13, '3': 0x14, '4': 0x15,
    '5': 0x17, '6': 0x16, '7': 0x1A, '8': 0x1C, '9': 0x19,
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
_pending_zoom = 0
_event_queued = False


def _key_name_to_vk(name):
    normalized = str(name).strip().upper()
    if IS_MAC:
        if normalized in MAC_KEYS:
            return MAC_KEYS[normalized]
        if normalized in MAC_LETTERS:
            return MAC_LETTERS[normalized]
        if normalized in MAC_DIGITS:
            return MAC_DIGITS[normalized]
    else:
        if normalized in WINDOWS_KEYS:
            return WINDOWS_KEYS[normalized]
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
        # utf-8-sig strips an optional BOM so files saved by editors that add
        # one (e.g. Windows Notepad) still parse correctly on both platforms.
        with open(SETTINGS_PATH, 'r', encoding='utf-8-sig') as settings_file:
            settings = json.load(settings_file)
        configured = settings.get('bindings', {})
        for action in DEFAULT_BINDINGS:
            if action in configured:
                bindings[action] = configured[action]
        resolved = {action: _key_name_to_vk(name) for action, name in bindings.items()}
        action_keys = [resolved[action] for action in ('left', 'right', 'up', 'down', 'zoom_in', 'zoom_out')]
        if len(set(action_keys)) != len(action_keys):
            raise ValueError('Each action must use a different key.')
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


def _rotate_camera(dx, dy, roll, zoom=0):
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

    # Zoom: scale the eye-target distance (positive zoom = closer to target).
    if zoom:
        scale = ZOOM_FACTOR ** (-zoom)
        eye_offset = _scaled(eye_offset, scale)

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
        global _pending_dx, _pending_dy, _pending_roll, _pending_zoom, _event_queued
        try:
            with _state_lock:
                dx = _pending_dx
                dy = _pending_dy
                roll = _pending_roll
                zoom = _pending_zoom
                _pending_dx = 0
                _pending_dy = 0
                _pending_roll = 0
                _pending_zoom = 0
                _event_queued = False
            if dx or dy or roll or zoom:
                _rotate_camera(dx, dy, roll, zoom)
        except Exception:
            _app.log('ArrowViewCube error:\n' + traceback.format_exc())


_mac_carbon = None


def _mac_load_carbon():
    global _mac_carbon
    if _mac_carbon is None:
        carbon = ctypes.cdll.LoadLibrary(
            '/System/Library/Frameworks/Carbon.framework/Carbon'
        )
        carbon.GetKeys.argtypes = [ctypes.c_void_p]
        carbon.GetKeys.restype = None
        _mac_carbon = carbon
    return _mac_carbon


def _key_down_windows(code):
    return bool(ctypes.windll.user32.GetAsyncKeyState(code) & 0x8000)


def _key_down_mac(code):
    # Carbon GetKeys fills a 128-bit bitmap of currently pressed keys.
    key_map = (ctypes.c_uint8 * 16)()
    _mac_load_carbon().GetKeys(ctypes.byref(key_map))
    return bool(key_map[code >> 3] & (1 << (code & 7)))


def _key_down(code):
    if IS_MAC:
        return _key_down_mac(code)
    return _key_down_windows(code)


def _fusion_is_foreground_windows():
    user32 = ctypes.windll.user32
    foreground = user32.GetForegroundWindow()
    if not foreground:
        return False
    process_id = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(foreground, ctypes.byref(process_id))
    return process_id.value == os.getpid()


def _fusion_is_foreground_mac():
    # Compare the frontmost app's PID with ours via the AppKit ObjC runtime.
    try:
        libobjc = ctypes.cdll.LoadLibrary('libobjc.dylib')
        ctypes.cdll.LoadLibrary(
            '/System/Library/Frameworks/AppKit.framework/AppKit'
        )
        objc_getClass = libobjc.objc_getClass
        objc_getClass.restype = ctypes.c_void_p
        objc_getClass.argtypes = [ctypes.c_char_p]
        sel_registerName = libobjc.sel_registerName
        sel_registerName.restype = ctypes.c_void_p
        sel_registerName.argtypes = [ctypes.c_char_p]
        objc_msgSend = libobjc.objc_msgSend

        workspace_cls = objc_getClass(b'NSWorkspace')
        shared_sel = sel_registerName(b'sharedWorkspace')
        frontmost_sel = sel_registerName(b'frontmostApplication')
        pid_sel = sel_registerName(b'processIdentifier')

        objc_msgSend.restype = ctypes.c_void_p
        objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        workspace = objc_msgSend(workspace_cls, shared_sel)
        frontmost = objc_msgSend(workspace, frontmost_sel)

        objc_msgSend.restype = ctypes.c_int32
        objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        front_pid = objc_msgSend(frontmost, pid_sel)
        return front_pid == os.getpid()
    except Exception:
        # Fail open: keep rotating if foreground state cannot be determined.
        return True


def _fusion_is_foreground():
    if IS_MAC:
        return _fusion_is_foreground_mac()
    return _fusion_is_foreground_windows()


def _queue_rotation(dx, dy, roll=0, zoom=0):
    global _pending_dx, _pending_dy, _pending_roll, _pending_zoom, _event_queued
    should_fire = False
    with _state_lock:
        _pending_dx += dx
        _pending_dy += dy
        _pending_roll += roll
        _pending_zoom += zoom
        if not _event_queued:
            _event_queued = True
            should_fire = True
    if should_fire and _app:
        _app.fireCustomEvent(EVENT_ID)


def _poll_keyboard():
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
            is_down = _key_down(key)
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
        vertical = int(bindings['up'] in fired) - int(bindings['down'] in fired)
        modifier_down = _key_down(bindings['roll_modifier'])

        if IS_MAC:
            # Command reassigns both axes: horizontal->roll, vertical->zoom.
            dx = 0 if modifier_down else horizontal
            roll = horizontal if modifier_down else 0
            dy = 0 if modifier_down else vertical
            zoom = vertical if modifier_down else 0
        else:
            # Ctrl reassigns horizontal only; vertical stays pitch.
            # Zoom uses dedicated PageUp/PageDown keys, independent of modifier.
            dx = 0 if modifier_down else horizontal
            roll = horizontal if modifier_down else 0
            dy = vertical
            zoom = (
                int(bindings['zoom_in'] in fired)
                - int(bindings['zoom_out'] in fired)
            )

        if dx or dy or roll or zoom:
            _queue_rotation(dx, dy, roll, zoom)


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
