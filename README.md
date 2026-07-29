# ArrowViewCube

[![Release](https://img.shields.io/github/v/release/HookyMaster/fusion360-arrow-viewcube?label=release)](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

适用于 Windows 和 macOS 的 Autodesk Fusion 360 插件。Fusion 窗口位于前台时，使用键盘方向键旋转当前三维视图。

A cross-platform Autodesk Fusion 360 add-in for Windows and macOS. Rotate the active 3D view with the keyboard arrow keys while Fusion is in the foreground.

## 下载 / Download

从 [Releases](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/latest) 页面下载最新的 `ArrowViewCube-vX.Y.Z.zip`。

Download the latest `ArrowViewCube-vX.Y.Z.zip` from the [Releases](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/latest) page.

## 操作 / Controls

**Windows**（桶滚修饰键默认 `Ctrl`）：

- `←` / `→`：水平旋转
- `↑` / `↓`：垂直旋转
- `Ctrl+→`：向右桶滚
- `Ctrl+←`：向左桶滚

**macOS**（桶滚修饰键默认 `⌘ Command`）：

- `←` / `→`：水平旋转
- `↑` / `↓`：垂直旋转
- `⌘+→`：向右桶滚
- `⌘+←`：向左桶滚

按住方向键可连续旋转。每次旋转 5°。插件不会修改模型，只会更新当前视口相机。

**Windows** (barrel-roll modifier defaults to `Ctrl`):

- `←` / `→`: horizontal orbit
- `↑` / `↓`: vertical orbit
- `Ctrl+→`: roll right
- `Ctrl+←`: roll left

**macOS** (barrel-roll modifier defaults to `⌘ Command`):

- `←` / `→`: horizontal orbit
- `↑` / `↓`: vertical orbit
- `⌘+→`: roll right
- `⌘+←`: roll left

Hold an arrow key to rotate continuously. Each step is 5°. The add-in never modifies the model; it only updates the active viewport camera.

## 自定义按键绑定

编辑插件目录中的 `settings.json`：

```json
{
  "bindings": {
    "left": "A",
    "right": "D",
    "up": "W",
    "down": "S",
    "roll_modifier": "SHIFT"
  }
}
```

保存后会自动生效，无需重启插件。默认旋转键为 `LEFT`、`RIGHT`、`UP`、`DOWN`；桶滚修饰键默认 Windows 为 `CTRL`、macOS 为 `COMMAND`。例如改用 `SHIFT` 后，`Shift+Right` 和 `Shift+Left` 执行桶滚。`settings.json` 在 Windows 与 macOS 上通用（路径自动适配），键名写法一致。

支持：

- 方向键：`LEFT`、`RIGHT`、`UP`、`DOWN`
- 字母：`A`–`Z`
- 数字：`0`–`9`
- 功能键：`F1`–`F12`
- 修饰键：`CTRL`、`SHIFT`、`ALT`，以及仅 macOS 的 `COMMAND`
- 常用键：`SPACE`、`ENTER`、`TAB`、`ESC`、`HOME`、`END`、`PAGEUP`、`PAGEDOWN`、`INSERT`、`DELETE`

四个动作必须绑定到不同按键。配置无效时，插件会自动回退到默认方向键，并将原因写入 Fusion 日志。

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

## 调整旋转速度

编辑 `ArrowViewCube.py` 顶部的：

```python
STEP_DEGREES = 5.0
```

数值越大，每次按键旋转得越快。修改后，在 Fusion 的“附加模块”窗口中停止并重新运行插件。

## 限制 / Limitations

- 支持 Windows 与 macOS（不支持 Linux，这是 Fusion 360 本身的限制）。
- macOS 上需要为 Fusion 360 授予输入监控权限才能读取按键。
- 方向键由系统状态轮询读取，不会吞掉原有按键事件；若某个 Fusion 命令本身使用方向键，两个行为可能同时发生。

- Supports Windows and macOS (Linux is not supported, a Fusion 360 limitation).
- On macOS, Fusion 360 must be granted input-monitoring permission to read key presses.
- Arrow keys are read by polling system key state and do not swallow the original key events; if a Fusion command itself uses the arrow keys, both actions may occur at once.

## 许可证 / License

本项目采用 [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0) 开源许可证。详见 [LICENSE](LICENSE)。

This project is licensed under the [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0) License. See [LICENSE](LICENSE) for details.
