# ArrowViewCube

[![Release](https://img.shields.io/github/v/release/HookyMaster/fusion360-arrow-viewcube?label=release)](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

适用于 Windows 和 macOS 的 Autodesk Fusion 360 插件。Fusion 窗口位于前台时，使用键盘旋转、平移和缩放当前三维视图。

A cross-platform Autodesk Fusion 360 add-in for Windows and macOS. Rotate, pan and zoom the active 3D view with the keyboard while Fusion is in the foreground.

## 下载 / Download

最新版本 **v1.4.0**（支持 Windows 和 macOS）：
[直接下载 ArrowViewCube-v1.4.0.zip](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/download/v1.4.0/ArrowViewCube-v1.4.0.zip)，或前往 [Releases](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/latest) 页面查看所有版本。

Latest release **v1.4.0** (Windows and macOS):
[Download ArrowViewCube-v1.4.0.zip directly](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/download/v1.4.0/ArrowViewCube-v1.4.0.zip), or visit the [Releases](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/latest) page for all versions.

## 操作 / Controls

所有操作在 Fusion 窗口位于前台时生效。**按住按键可连续操作**（初始延迟后自动重复），松开即停。

### 旋转（轨道环绕）

| 按键 | 效果 |
|------|------|
| `←` / `→` | 绕模型**水平旋转**（左右环绕观察） |
| `↑` / `↓` | 绕模型**垂直旋转**（俯仰观察） |

- 旋转以当前视角中心（相机目标点）为轴心。
- 每步旋转 **5°**（可在代码中调整，见下文）。

### 桶滚（画面倾斜）

需同时按住**修饰键**（Windows: `Ctrl`；macOS: `⌘ Command`）：

| 按键 | 效果 |
|------|------|
| `Ctrl+←` / `⌘+←` | 画面逆时针倾斜 |
| `Ctrl+→` / `⌘+→` | 画面顺时针倾斜 |

- 桶滚围绕当前视线方向旋转画面，不改变观察角度。
- 每步同样 5°。

### 平移

按住 `Shift` + 方向键，视图沿屏幕方向平移（相机与目标点一起移动，视角方向不变）：

| 按键 | 效果 |
|------|------|
| `Shift+←` | 向左平移 |
| `Shift+→` | 向右平移 |
| `Shift+↑` | 向上平移 |
| `Shift+↓` | 向下平移 |

- 行为与 Fusion 的 **Ctrl+鼠标中键拖动**一致：画面内容跟随按键方向移动，**ViewCube 保持不动**（因为视角方向没有改变）。
- 每步平移量为当前视图范围的 **10%**（`PAN_FRACTION`，可在代码中调整）：视野越大平移越快，缩放后平移自动变慢，手感符合直觉。

### 缩放

提供**两套等价方式**，可任选其一或组合使用：

| 按键 | 效果 |
|------|------|
| `PageUp` | **放大**（拉近视图） |
| `PageDown` | **缩小**（拉远视图） |
| `Ctrl+↑` / `⌘+↑` | **放大**（等价于 PageUp） |
| `Ctrl+↓` / `⌘+↓` | **缩小**（等价于 PageDown） |

- 缩放通过调整相机 `viewExtents` 实现（Fusion 原生方式），不改变相机位置。
- 每步缩放约 **1.18 倍**（放大时视图范围 ×0.85，缩小时 ÷0.85）。
- macOS 笔记本无独立 PageUp/PageDown 键时，可用 `Fn+↑`/`Fn+↓` 代替，或直接用 `⌘+↑`/`⌘+↓`。

### 注意事项

- 插件**不会修改任何模型几何**，只更新当前视口的相机参数。
- 操作仅在 Fusion 位于前台（活动窗口）时响应，切走即暂停。
- 方向键的作用（旋转 / 平移 / 桶滚缩放）在**按下瞬间锁定**，松手前不会改变——即使修饰键先于方向键松开也不会串键。
- `PageUp`/`PageDown` 缩放在任何修饰键状态下都生效。

---

All controls work while Fusion is the foreground window. **Hold a key for continuous operation** (auto-repeats after a short initial delay); release to stop.

### Orbit (rotation)

| Key | Effect |
|-----|--------|
| `←` / `→` | **Horizontal orbit** (pan around the model) |
| `↑` / `↓` | **Vertical orbit** (tilt up/down) |

- Rotation pivots around the camera target (current view center).
- Each step is **5°** (adjustable in code, see below).

### Roll (tilt the viewport)

Hold the **modifier key** (Windows: `Ctrl`; macOS: `⌘ Command`) simultaneously:

| Key | Effect |
|-----|--------|
| `Ctrl+←` / `⌘+←` | Tilt counter-clockwise |
| `Ctrl+→` / `⌘+→` | Tilt clockwise |

- Roll rotates the view around the current line of sight without changing the viewing angle.
- Each step is also 5°.

### Pan

Hold `Shift` + an arrow key to slide the view along the screen axes (camera and target move together; the viewing direction stays fixed):

| Key | Effect |
|-----|--------|
| `Shift+←` | Pan left |
| `Shift+→` | Pan right |
| `Shift+↑` | Pan up |
| `Shift+↓` | Pan down |

- Behaves exactly like Fusion's **Ctrl+middle-mouse-button drag**: the content follows the arrow direction and the **ViewCube stays still** (the viewing direction never changes).
- Each pan step moves **10%** of the current view extents (`PAN_FRACTION`, adjustable in code): panning is faster when zoomed out and automatically slows down when zoomed in.

### Zoom

Two equivalent methods — use whichever is convenient:

| Key | Effect |
|-----|--------|
| `PageUp` | **Zoom in** (closer) |
| `PageDown` | **Zoom out** (farther) |
| `Ctrl+↑` / `⌘+↑` | **Zoom in** (same as PageUp) |
| `Ctrl+↓` / `⌘+↓` | **Zoom out** (same as PageDown) |

- Zoom adjusts the camera `viewExtents` (Fusion's native method) without moving the camera.
- Each step is approximately **1.18×** (view extents ×0.85 to zoom in, ÷0.85 to zoom out).
- On MacBook keyboards without dedicated PageUp/PageDown, use `Fn+↑`/`Fn+↓` or simply `⌘+↑`/`⌘+↓`.

### Notes

- The add-in **never modifies model geometry** — it only updates the active viewport camera.
- Controls respond only while Fusion is the foreground (active) window.
- What an arrow key does (orbit / pan / roll-zoom) is **latched the instant it is pressed** and never changes until released — even if you release the modifier before the arrow key, the action stays consistent.
- `PageUp`/`PageDown` zoom works regardless of which modifier is held.

## 自定义按键绑定 / Custom Key Bindings

> ⚠️ **警告 / Warning**
>
> **强烈不建议修改默认按键绑定。** 默认配置经过充分测试，在 Windows 和 macOS 上均工作良好。擅自修改可能导致：
> - 按键与 Fusion 内置命令冲突，触发意外操作；
> - 多个动作绑定到同一按键，导致行为混乱；
> - 配置错误时插件回退到默认值（但不会报错提示）。
>
> 如确需修改，请**只改必须改的项**，保留其余默认值，修改后立即在 Fusion 中验证。
>
> **We strongly advise against changing the default key bindings.** The defaults are well-tested on both Windows and macOS. Modifying them may cause:
> - Conflicts with Fusion's built-in shortcuts, triggering unintended actions;
> - Multiple actions bound to the same key, causing erratic behavior;
> - Silent fallback to defaults if the config is invalid (no error is shown).
>
> If you must change bindings, **modify only what you need**, keep everything else at defaults, and test in Fusion immediately after saving.

编辑插件目录中的 `settings.json`。文件采用**增量覆盖**设计：只需写出要修改的项，未列出的自动使用默认值。

Edit `settings.json` in the add-in folder. The file uses **incremental override**: list only the entries you want to change; anything omitted falls back to its default.

### 默认绑定 / Default bindings

```json
{
  "bindings": {
    "left": "LEFT",
    "right": "RIGHT",
    "up": "UP",
    "down": "DOWN",
    "roll_modifier": "CTRL",
    "pan_modifier": "SHIFT",
    "zoom_in": "PAGEUP",
    "zoom_out": "PAGEDOWN"
  }
}
```

| 键名 | 作用 | 默认值（Windows / macOS） |
|------|------|---------------------------|
| `left` / `right` | 水平旋转 | `LEFT` / `RIGHT` |
| `up` / `down` | 垂直旋转 | `UP` / `DOWN` |
| `roll_modifier` | 桶滚 + 缩放修饰键 | `CTRL` / `COMMAND` |
| `pan_modifier` | 平移修饰键 | `SHIFT` / `SHIFT` |
| `zoom_in` / `zoom_out` | 独立缩放键 | `PAGEUP` / `PAGEDOWN` |

> `roll_modifier` 在 macOS 上默认为 `COMMAND`（无需在 settings.json 中写出，代码自动适配平台）。

### 修改示例 / Example

例如想把旋转改为 WASD、修饰键改为 Alt：

For example, to switch orbit to WASD and the modifier to Alt:

```json
{
  "bindings": {
    "left": "A",
    "right": "D",
    "up": "W",
    "down": "S",
    "roll_modifier": "ALT"
  }
}
```

此时 `Alt+A`/`Alt+D` 执行桶滚，`Alt+W`/`Alt+S` 执行缩放；`PageUp`/`PageDown` 仍可用于缩放，`Shift+方向键` 仍可平移（未改动的项保持默认）。

Here `Alt+A`/`Alt+D` roll, `Alt+W`/`Alt+S` zoom; `PageUp`/`PageDown` still zoom and `Shift+arrows` still pan (unchanged entries keep their defaults).

### 支持的键名 / Supported key names

- 方向键 / Arrows: `LEFT`、`RIGHT`、`UP`、`DOWN`
- 字母 / Letters: `A`–`Z`
- 数字 / Digits: `0`–`9`
- 功能键 / Function keys: `F1`–`F12`
- 修饰键 / Modifiers: `CTRL`、`SHIFT`、`ALT`、`COMMAND`（COMMAND 仅 macOS）
- 常用键 / Common: `SPACE`、`ENTER`、`TAB`、`ESC`、`HOME`、`END`、`PAGEUP`、`PAGEDOWN`、`INSERT`、`DELETE`

### 约束 / Constraints

- `left`/`right`/`up`/`down` 四个动作**必须绑定到不同按键**，否则配置无效。
- `roll_modifier` 与 `pan_modifier` **不要设为同一个键**（否则桶滚/缩放修饰键优先生效，平移将不可用）。
- 配置无效时，插件**静默回退到默认方向键**，错误原因写入 Fusion 日志和插件目录下的 `debug.log`。
- 保存后**立即生效**，无需重启插件。
- `settings.json` 在 Windows 与 macOS 上通用，键名写法一致，路径自动适配。

- The four orbit actions **must each use a different key**, otherwise the config is rejected.
- Do **not** set `roll_modifier` and `pan_modifier` to the same key (the roll modifier takes precedence and pan would become unreachable).
- On invalid config the add-in **silently falls back to the default arrow keys**; the reason is logged to Fusion's log and to `debug.log` in the add-in folder.
- Changes take effect **immediately** on save — no restart needed.
- `settings.json` works identically on Windows and macOS with the same key names.

## 安装 / Install

1. 将整个 `ArrowViewCube` 文件夹复制到插件目录：
   - Windows: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`
   - macOS: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`
2. 在 Fusion 360 中打开“实用程序”→“附加模块”。
3. 选择 `ArrowViewCube`，点击“运行”。
4. 若要随 Fusion 启动，请勾选“启动时运行”。

> macOS 注意：首次运行时，系统可能要求为 Fusion 360 授予“输入监控 / 辅助功能”权限
> （系统设置 → 隐私与安全性）。未授权时插件无法读取方向键。授权后需重启 Fusion。

1. Copy the entire `ArrowViewCube` folder into the add-ins directory:
   - Windows: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`
   - macOS: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`
2. In Fusion 360 open Utilities → Add-Ins.
3. Select `ArrowViewCube` and click Run.
4. Tick "Run on startup" to load it automatically.

> macOS note: on first run the system may ask you to grant Fusion 360
> "Input Monitoring / Accessibility" permission (System Settings → Privacy & Security).
> Without it the add-in cannot read the arrow keys. Restart Fusion after granting access.

## 调整旋转、缩放和平移速度

编辑 `ArrowViewCube.py` 顶部的：

```python
STEP_DEGREES = 5.0
ZOOM_STEP = 0.85
PAN_FRACTION = 0.10
```

`STEP_DEGREES` 越大，每次按键旋转得越快。`ZOOM_STEP` 越接近 0，每次按键缩放幅度越大（小于 1，放大时视图范围乘以该值）。`PAN_FRACTION` 越大，每次平移的步长越大（占当前视图范围的比例）。修改后，在 Fusion 的"附加模块"窗口中停止并重新运行插件。

## Adjusting rotation, zoom and pan speed

Edit the constants at the top of `ArrowViewCube.py`:

```python
STEP_DEGREES = 5.0
ZOOM_STEP = 0.85
PAN_FRACTION = 0.10
```

A larger `STEP_DEGREES` rotates faster per key press. The closer `ZOOM_STEP` is to 0, the larger the zoom step (it is below 1; zoom-in multiplies the view extents by this value). A larger `PAN_FRACTION` makes each pan step longer (as a fraction of the current view extents). After editing, stop and re-run the add-in in Fusion's Add-Ins window.

## 限制 / Limitations

- 支持 Windows 与 macOS（不支持 Linux，这是 Fusion 360 本身的限制）。
- macOS 上需要为 Fusion 360 授予输入监控权限才能读取按键。
- 方向键由系统状态轮询读取，不会吞掉原有按键事件；若某个 Fusion 命令本身使用方向键，两个行为可能同时发生。

- Supports Windows and macOS (Linux is not supported, a Fusion 360 limitation).
- On macOS, Fusion 360 must be granted input-monitoring permission to read key presses.
- Arrow keys are read by polling system key state and do not swallow the original key events; if a Fusion command itself uses the arrow keys, both actions may occur at once.

## 故障排查 / Troubleshooting

插件启动时会把诊断信息写入插件目录下的 `debug.log`（按键分派、相机变化等）。如果按键没有按预期工作，先查看该文件；报告问题时附上它有助于定位。

The add-in writes diagnostics to `debug.log` in the add-in folder (key dispatch, camera changes, etc.). If a key does not behave as expected, check that file first; attach it when reporting an issue.

## 许可证 / License

本项目采用 [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0) 开源许可证。详见 [LICENSE](LICENSE)。

This project is licensed under the [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0) License. See [LICENSE](LICENSE) for details.
