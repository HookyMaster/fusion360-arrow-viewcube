# ArrowViewCube

[![Release](https://img.shields.io/github/v/release/HookyMaster/fusion360-arrow-viewcube?label=release)](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Windows 版 Autodesk Fusion 360 插件。Fusion 窗口位于前台时，使用键盘方向键旋转当前三维视图。

## 下载 / Download

从 [Releases](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/latest) 页面下载最新的 `ArrowViewCube-vX.Y.Z.zip`。

Download the latest `ArrowViewCube-vX.Y.Z.zip` from the [Releases](https://github.com/HookyMaster/fusion360-arrow-viewcube/releases/latest) page.

## 操作

- `←` / `→`：水平旋转
- `↑` / `↓`：垂直旋转
- `Ctrl+→`：向右桶滚
- `Ctrl+←`：向左桶滚
- 按住方向键：连续旋转

每次旋转 5°。插件不会修改模型，只会更新当前视口相机。

## 自定义按键绑定

编辑插件目录中的 `settings.json`：

```json
{
  "bindings": {
    "left": "A",
    "right": "D",
    "up": "W",
    "down": "S",
    "roll_modifier": "CTRL"
  }
}
```

保存后会自动生效，无需重启插件。默认旋转键为 `LEFT`、`RIGHT`、`UP`、`DOWN`，桶滚修饰键为 `CTRL`。例如改用 `SHIFT` 后，`Shift+Right` 和 `Shift+Left` 执行桶滚。

支持：

- 方向键：`LEFT`、`RIGHT`、`UP`、`DOWN`
- 字母：`A`–`Z`
- 数字：`0`–`9`
- 功能键：`F1`–`F12`
- 常用键：`SPACE`、`ENTER`、`TAB`、`ESC`、`HOME`、`END`、`PAGEUP`、`PAGEDOWN`、`INSERT`、`DELETE`

四个动作必须绑定到不同按键。配置无效时，插件会自动回退到默认方向键，并将原因写入 Fusion 日志。

## 安装

1. 将整个 `ArrowViewCube` 文件夹复制到：
   `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`
2. 在 Fusion 360 中打开“实用程序”→“附加模块”。
3. 选择 `ArrowViewCube`，点击“运行”。
4. 若要随 Fusion 启动，请勾选“启动时运行”。

## 调整旋转速度

编辑 `ArrowViewCube.py` 顶部的：

```python
STEP_DEGREES = 5.0
```

数值越大，每次按键旋转得越快。修改后，在 Fusion 的“附加模块”窗口中停止并重新运行插件。

## 限制

- 仅支持 Windows。
- 方向键由系统状态轮询读取，不会吞掉原有按键事件；若某个 Fusion 命令本身使用方向键，两个行为可能同时发生。

## 许可证 / License

本项目采用 [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0) 开源许可证。详见 [LICENSE](LICENSE)。

This project is licensed under the [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0) License. See [LICENSE](LICENSE) for details.
