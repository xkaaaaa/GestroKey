# GestroKey 源代码目录说明

GestroKey是一款手势控制工具，允许用户通过鼠标绘制手势来执行各种操作（如快捷键、启动程序等）。本工具的核心特性包括全局鼠标手势识别、方向分析、手势库管理以及自定义UI组件，适用于日常办公、创意设计和编程开发等场景。

## 主要功能特性

- **全局手势识别**：支持在任何应用程序中绘制手势
- **路径分析**：手势方向识别和相似度匹配
- **可视化手势编辑**：手势绘制和编辑界面
- **系统托盘集成**：支持最小化到托盘，后台运行
- **静默启动模式**：支持`--silent`参数，适用于开机自启动
- **跨平台兼容**：支持Windows、macOS和Linux系统
- **开机自启动**：一键设置开机自动启动（静默模式）
- **多 Qt 框架支持**：通过 QtPy 兼容 PyQt5/6 和 PySide2/6，可根据需要切换

本文档详细介绍了GestroKey项目`src`目录下各文件和文件夹的功能及使用方法。

## 目录索引

- [1. 主程序模块](#1-主程序模块)
  - [1.1 main.py](#11-mainpy)
  - [1.2 version.py](#12-versionpy)
- [2. 用户界面模块](#2-用户界面模块-ui)
  - [2.1 控制台选项卡](#21-控制台选项卡-uiconsolepy)
  - [2.2 手势管理模块](#22-手势管理模块)
    - [2.2.1 手势库](#221-手势库-uigesturesgesturespy)
    - [2.2.2 手势管理主页面](#222-手势管理主页面-uigesturesgestures_tabpy)
    - [2.2.3 手势编辑对话框](#223-手势编辑对话框-uigesturesgesture_dialogspy)
    - [2.2.4 手势绘制组件](#224-手势绘制组件-uigesturesdrawing_widgetpy)
  - [2.3 设置模块](#23-设置模块)
    - [2.3.1 设置管理器](#231-设置管理器-uisettingssettingspy)
    - [2.3.2 设置主页面](#232-设置主页面-uisettingssettings_tabpy)
    - [2.3.3 应用设置选项卡](#233-应用设置选项卡-uisettingsapplication_settings_tabpy)
    - [2.3.4 画笔设置选项卡](#234-画笔设置选项卡-uisettingsbrush_settings_tabpy)
    - [2.3.5 判断器设置选项卡](#235-判断器设置选项卡-uisettingsrecognizer_settings_tabpy)
    - [2.3.6 动态预览组件](#236-动态预览组件-uisettingspen_preview_widgetpy)
- [3. 核心功能模块](#3-核心功能模块)
  - [3.1 core/brush/](#31-corebrush)
    - [3.1.1 core/brush/manager.py](#311-corebrushmanagerpy)
    - [3.1.2 core/brush/overlay.py](#312-corebrushoverlaypy)
    - [3.1.3 core/brush/drawing.py](#313-corebrushdrawingpy)
    - [3.1.4 core/brush/fading.py](#314-corebrushfadingpy)
  - [3.2 core/path_analyzer.py](#32-corepath_analyzerpy)
  - [3.3 core/gesture_executor.py](#33-coregesture_executorpy)
  - [3.4 core/system_monitor.py](#34-coresystem_monitorpy)
  - [3.5 core/self_check.py](#35-coreself_checkpy)
  - [3.6 core/logger.py](#36-coreloggerpy)

## 目录结构

```
src/
├── core/                    # 核心功能模块
│   ├── brush/               # 画笔绘制模块
│   │   ├── manager.py       # 绘制管理器
│   │   ├── overlay.py       # 绘制覆盖层
│   │   ├── drawing.py       # 画笔绘制逻辑
│   │   └── fading.py        # 淡出效果模块
│   ├── path_analyzer.py     # 路径分析模块
│   ├── gesture_executor.py  # 手势执行模块
│   ├── system_monitor.py    # 系统监测模块
│   ├── self_check.py        # 自检模块
│   └── logger.py            # 日志记录模块
├── ui/                      # 用户界面模块
│   ├── console.py           # 控制台选项卡
│   ├── settings/            # 设置模块
│   │   ├── application_settings_tab.py # 应用设置选项卡
│   │   ├── brush_settings_tab.py # 画笔设置选项卡
│   │   ├── default_settings.json # 默认设置配置文件
│   │   ├── pen_preview_widget.py # 动态笔尖预览组件
│   │   ├── recognizer_settings_tab.py # 判断器设置选项卡
│   │   ├── settings.py      # 设置管理器
│   │   └── settings_tab.py  # 设置主页面（包含三个子选项卡）
│   └── gestures/            # 手势管理模块
│       ├── default_gestures.json # 默认手势库定义（JSON格式）
│       ├── drawing_widget.py # 手势绘制组件
│       ├── gesture_dialogs.py # 手势编辑/添加对话框
│       ├── gestures.py      # 手势库管理模块
│       └── gestures_tab.py  # 手势管理主页面
├── assets/                  # 资源文件目录
│   └── images/              # 图像资源，按功能分类组织
│       ├── app/             # 应用程序图标
│       │   ├── icon.svg     # 主应用程序图标（SVG格式）
│       │   └── icons/       # 多尺寸应用图标
│       │       ├── icon.ico     # Windows图标文件
│       │       ├── icon.icns    # macOS图标文件
│       │       └── icon-*.png   # 各种尺寸的PNG图标（16px到1024px）
│       ├── ui/              # 用户界面图标
│       │   ├── console.svg      # 控制台选项卡图标
│       │   ├── gestures.svg     # 手势管理选项卡图标
│       │   ├── settings.svg     # 设置选项卡图标
│       │   ├── start-drawing.svg    # 开始绘制按钮图标
│       │   ├── stop-drawing.svg     # 停止绘制按钮图标
│       │   ├── edit.svg         # 编辑操作图标
│       │   ├── delete.svg       # 删除操作图标
│       │   ├── add.svg          # 添加操作图标
│       │   ├── app-settings.svg     # 应用设置选项卡图标
│       │   ├── brush-settings.svg   # 画笔设置选项卡图标
│       │   ├── recognizer-settings.svg # 识别器设置选项卡图标
│       │   ├── reset.svg        # 重置为默认图标
│       │   ├── cancel.svg       # 放弃修改图标
│       │   ├── save.svg         # 保存修改图标
│       │   ├── exit.svg         # 退出程序图标
│       │   ├── tray-start.svg   # 托盘开始监听图标
│       │   ├── tray-stop.svg    # 托盘停止监听图标
│       │   └── tray-show.svg    # 托盘显示主窗口图标
│       └── tools/           # 工具图标
│           ├── brush.svg        # 画笔工具图标
│           ├── pointer.svg      # 指针工具图标
│           ├── undo.svg         # 撤销操作图标
│           ├── redo.svg         # 重做操作图标
│           └── test.svg         # 测试功能图标
├── version.py               # 版本信息模块
├── main.py                  # 主程序入口
└── README.md               # 本文档
```

## 详细模块说明

### 1. 主程序模块

#### 1.1 main.py

**功能说明**：程序的主入口文件，提供选项卡式的图形用户界面，包含控制台、设置界面和手势管理界面。

**主要类和方法**：

**全局辅助函数**：
- `show_dialog(parent, message_type="warning", title_text=None, message="", content_widget=None, custom_icon=None, custom_buttons=None, custom_button_colors=None, callback=None)`：通用对话框显示函数，支持信息、警告、错误、问题类型对话框，支持自定义按钮和回调
- `get_system_tray(parent)`：创建系统托盘图标和右键菜单，包含显示窗口、启动/停止监听、设置、退出等菜单项，返回的托盘对象具有update_drawing_state方法用于更新状态显示，包含内部辅助函数_get_icon_path和_set_action_icon

**GestroKeyApp主窗口类**：继承自`QMainWindow`
- `__init__(self, silent_start=False)`：初始化应用程序主窗口，设置日志记录器、全局资源、UI界面和系统托盘，支持静默启动模式
- `init_global_resources(self)`：初始化设置管理器和手势库管理器等全局资源
- `init_system_tray(self)`：初始化系统托盘图标
- `toggle_drawing(self)`：切换绘制状态（启动/停止手势监听）
- `_silent_start_drawing(self)`：静默启动时的绘制启动方法，延迟启动确保初始化完成
- `start_drawing(self)`：启动绘制功能
- `stop_drawing(self)`：停止绘制功能
- `show_and_activate(self)`：多平台窗口显示和激活方法，针对Windows、macOS和Linux平台进行了优化
- `show_settings_page(self)`：显示设置页面并切换到设置选项卡
- `initUI(self)`：初始化用户界面，设置窗口属性、创建页面选项卡、堆栈布局和底部状态栏，包含内部函数_create_tab_button用于统一创建选项卡按钮
- `switch_page(self, index)`：切换到指定索引的页面并更新按钮样式
- `_select_initial_page(self)`：选择初始页面（默认为控制台页面）
- `onPageChanged(self, index)`：处理页面切换事件，记录切换日志
- `resizeEvent(self, event)`：处理窗口尺寸变化事件，当前为空实现，仅调用父类方法
- `closeEvent(self, event)`：处理窗口X按钮关闭事件，始终忽略并调用内部退出逻辑
- `_show_exit_dialog(self)`：显示退出确认对话框，包含最小化到托盘、退出程序和取消选项，内部定义ExitDialog类处理用户选择并自动保存设置
- `_handle_close_request(self, is_window_close)`：统一的关闭请求处理，根据设置决定显示对话框或执行默认行为
- `_prepare_for_close(self)`：退出前的准备工作，停止绘制和释放按键状态
- `_notify_settings_changed(self)`：通知设置已更改，重新加载设置到内存并刷新设置页面UI
- `_minimize_to_tray(self)`：将窗口最小化到系统托盘
- `_exit_application(self)`：退出应用程序的入口点（强制退出）
- `_exit_with_save_check(self)`：退出程序并检查未保存项目
- `_check_unsaved_and_exit(self)`：检查未保存的设置和手势库更改，显示保存确认对话框
- `_force_exit(self)`：强制退出程序，调用sys.exit(0)
- `_handle_save_changes_response(self, button_text)`：处理保存更改对话框的用户响应（是/否/取消）
- `show_global_dialog(self, parent=None, message_type="warning", title_text=None, message="", content_widget=None, custom_icon=None, custom_buttons=None, custom_button_colors=None, callback=None)`：显示全局对话框，支持多种类型和自定义参数
- `handle_dialog_close(self, dialog)`：处理对话框关闭事件，清除引用
- `on_drawing_state_changed(self, is_active)`：响应绘制状态变化，更新托盘图标状态

**使用方法**：
```python
# 直接运行该文件启动应用程序
python src/main.py

# 静默启动（自动开始监听并最小化到托盘）
python src/main.py --silent
# 或使用短参数
python src/main.py -s

# 或从其他Python代码中导入并创建实例
import os
import sys

# 设置 Qt API（必须在导入任何 Qt 相关模块之前）
from version import QT_API
os.environ['QT_API'] = QT_API

from main import GestroKeyApp
from qtpy.QtWidgets import QApplication

app = QApplication(sys.argv)
window = GestroKeyApp()
window.show()
sys.exit(app.exec())
```

**命令行参数**：
- `--silent` 或 `-s`：静默启动模式，应用程序将：
  - 不显示主窗口
  - 自动开始手势监听
  - 直接最小化到系统托盘
  - 适用于开机自启动场景

**GUI页面**：
- 控制台页面：提供绘制功能的开启和停止控制，以及系统资源监测
- 设置页面：提供应用程序设置的配置，包括笔尖粗细和笔尖颜色设置
- 手势管理页面：提供手势库的管理界面，可添加、编辑、删除手势

#### 1.2 version.py

**功能说明**：版本信息模块，存储和管理版本号、构建日期等应用程序基本信息，以及打包配置。

**主要变量**：
- `VERSION`：版本号，如"0.0.1-beta.2"
- `APP_NAME`：应用程序名称，固定为"GestroKey"
- `APP_DESCRIPTION`：应用程序描述
- `BUILD_DATE`：构建日期，格式为"YYYY-MM-DD"，使用当前日期自动生成
- `AUTHOR`：作者信息
- `LICENSE`：许可证类型，固定为"GPL-3.0"
- `REPO_URL`：仓库URL地址
- `QT_API`：Qt API配置，支持"pyqt5"、"pyqt6"、"pyside2"、"pyside6"
- `VERSION_TYPE_RELEASE`：正式版类型标识，值为"正式版"
- `VERSION_TYPE_PREVIEW`：预览版类型标识，值为"预览版"
- `VERSION_TYPE_DEVELOPMENT`：开发版类型标识，值为"未发布版"
- `CURRENT_VERSION_TYPE`：当前版本类型，默认为开发版

**打包配置变量**：
- `ENABLE_PACKAGING`：是否启用打包流程
- `PACKAGE_WINDOWS`：是否打包Windows版本
- `PACKAGE_MACOS`：是否打包macOS版本
- `PACKAGE_LINUX`：是否打包Linux版本
- `PACKAGE_STANDALONE`：是否生成单文件版本
- `PACKAGE_PORTABLE`：是否生成便携版本
- `PACKAGER_WINDOWS`：Windows打包工具选择（"nuitka"或"pyinstaller"）
- `PACKAGER_MACOS`：macOS打包工具选择（"nuitka"或"pyinstaller"）
- `PACKAGER_LINUX`：Linux打包工具选择（"nuitka"或"pyinstaller"）
- `PACKAGE_INCLUDE_DEBUG_SYMBOLS`：是否包含调试符号
- `PACKAGE_OPTIMIZE_LEVEL`：优化级别（0-2）
- `PACKAGE_COMPRESS_ASSETS`：是否压缩资源文件
- `PACKAGE_UPXIFY`：是否使用UPX压缩可执行文件
- `PACKAGE_OUTPUT_DIR`：输出目录名称
- `PACKAGE_NAMING_PATTERN`：命名模式，支持占位符

**主要函数**：
- `get_version_string()`：获取格式化的版本字符串，如"GestroKey v0.0.1-beta.2"
- `get_full_version_info()`：获取完整的版本信息，返回包含所有版本相关信息的字典
- `get_packaging_config()`：获取打包配置信息，返回包含所有打包设置的字典

**使用方法**：
```python
from version import VERSION, APP_NAME, CURRENT_VERSION_TYPE, get_version_string, get_full_version_info, get_packaging_config

# 获取版本号
current_version = VERSION  # 如："0.0.1-beta.2"

# 获取应用名称
app_name = APP_NAME  # 返回："GestroKey"

# 获取当前版本类型
version_type = CURRENT_VERSION_TYPE  # 返回："未发布版"、"预览版"或"正式版"

# 获取格式化的版本字符串
version_string = get_version_string()  # 返回："GestroKey v0.0.1-beta.2"

# 获取完整的版本信息
version_info = get_full_version_info()  # 返回包含所有版本信息的字典

# 获取打包配置信息
packaging_config = get_packaging_config()  # 返回包含所有打包设置的字典

# Qt API 配置
from version import QT_API
print(f"当前使用的 Qt API: {QT_API}")

# 修改 Qt API（需要在导入 qtpy 之前设置）
# 注意：修改此配置后需要重启应用程序才能生效
# 示例：切换到 PyQt5
# QT_API = "pyqt5"

# 切换到 PyQt5 的完整步骤：
# 1. 安装 PyQt5 依赖：pip install -r requirements-pyqt5.txt
# 2. 在 version.py 中设置：QT_API = "pyqt5"
# 3. 重启应用程序
```

**版本管理说明**：
- 更新应用程序版本时，只需修改`VERSION`和相关变量
- 构建日期`BUILD_DATE`自动设置为当前日期
- 版本类型`CURRENT_VERSION_TYPE`根据发布阶段设置为对应的值：
  - 开发阶段设置为`VERSION_TYPE_DEVELOPMENT`(未发布版)
  - 预发布阶段设置为`VERSION_TYPE_PREVIEW`(预览版)
  - 正式发布阶段设置为`VERSION_TYPE_RELEASE`(正式版)

### 2. 用户界面模块 (UI)

#### 2.1 控制台选项卡 (ui/console.py)

**功能说明**：
控制台界面，应用程序的主要交互界面，提供启动/停止绘制功能，显示系统资源监控信息。

**主要类和方法**：
- `create_styled_progress_bar(color_theme="default")`：创建带样式的原生QProgressBar，支持不同颜色主题

- `ConsolePage`：控制台页面类，继承自QWidget
  - `drawing_state_changed`：绘制状态变化信号，参数为是否处于绘制状态
  - `__init__(self, parent=None)`：初始化控制台页面，设置系统监测器和UI
  - `_get_icon_path(self, icon_name)`：获取图标文件路径，检查文件是否存在
  - `_set_button_icon(self, button, icon_name, size=(24, 24))`：为按钮设置图标和尺寸
  - `_setup_ui(self)`：初始化UI组件和布局
  - `_create_system_info_card(self, title, value, color)`：创建系统信息卡片，使用QFrame实现
  - `update_system_info(self, data)`：更新系统信息显示，包括CPU、内存、运行时间和进程资源
  - `toggle_drawing(self)`：切换绘制状态
  - `start_drawing(self)`：开始绘制功能
  - `stop_drawing(self)`：停止绘制功能
  - `closeEvent(self, event)`：关闭事件处理，停止绘制和系统监测

**组件布局**：
- 顶部：标题和状态标签
- 中部：控制按钮区域，包含开始/停止绘制按钮
- 底部：系统信息卡片区域，显示CPU使用率、内存使用率、运行时间和进程资源信息

**交互操作**：
- 绘制切换：通过动作按钮切换绘制状态
- 系统监测：自动监测并显示系统资源信息

**系统信息卡片**：
- CPU使用率卡片：显示当前CPU使用率，带颜色渐变进度条
- 内存使用率卡片：显示当前内存使用率，带颜色渐变进度条
- 运行时间卡片：显示应用程序运行时间
- 进程资源卡片：显示当前进程的CPU和内存使用情况

**使用方法**：
```python
# 创建控制台页面
from ui.console import ConsolePage

# 创建页面实例
console_page = ConsolePage()

# 页面会自动显示系统信息和控制按钮

# 控制绘制状态（通过按钮触发）
console_page.toggle_drawing() # 切换绘制状态
console_page.start_drawing()  # 开始绘制
console_page.stop_drawing()   # 停止绘制

# 更新系统信息
system_data = {
    'cpu_percent': 25.5,
    'memory_percent': 60.2,
    'process_cpu': 2.1,
    'process_memory': 45.6
}
console_page.update_system_info(system_data)
```

#### 2.2 手势管理模块

##### 2.2.1 手势库 (ui/gestures/gestures.py)

**功能说明**：
手势库管理器，负责保存和加载用户手势库。采用新的三部分架构：触发路径、执行操作和手势映射，提供更灵活的手势管理方式。作为后端模块，专注于数据管理和持久化，与前端界面逻辑分离。

**架构设计**：
新的手势库结构分为三个独立的部分：
1. **trigger_paths**: 触发路径（绘制的轨迹数据）
2. **execute_actions**: 执行操作（要执行的动作定义）
3. **gesture_mappings**: 手势映射（将路径和操作关联起来）

**主要类和方法**：
- `GestureLibrary`：手势库类
  - `__init__(self)`：初始化手势库，加载默认手势和用户配置，设置路径分析器
  - `_load_default_gestures(self)`：从JSON文件加载默认手势库
  - `_convert_actions_for_current_platform(self)`：转换操作的快捷键格式为当前平台格式
  - `_convert_shortcut_for_current_platform(self, shortcut)`：将快捷键转换为当前平台的格式
  - `_get_gestures_file_path(self)`：获取手势库文件路径，支持多平台
  - `load(self)`：从文件加载手势库
  - `_convert_loaded_actions_for_current_platform(self, loaded_data)`：转换加载的操作快捷键格式为当前平台格式
  - `_update_saved_state(self)`：更新已保存状态，深拷贝当前数据作为保存状态基准
  - `save(self)`：保存手势库到文件，返回保存成功状态
  - `has_changes(self)`：检查是否有未保存的更改，对比当前数据与保存状态
  - `mark_data_changed(self, change_type)`：标记数据已更改，记录更改类型和时间戳
  - `get_last_change_info(self)`：获取最后一次更改的类型和时间戳信息
  - `clear_change_marker(self)`：清除更改标记，重置更改类型和时间戳
  - `get_gesture_by_path(self, drawn_path, similarity_threshold=0.70)`：根据绘制路径获取匹配的手势，核心逻辑包括路径对比、相似度计算、映射查找和操作获取，返回手势名称、操作数据和相似度
  - `get_gesture_count(self, use_saved=False)`：获取手势数量，可选择获取当前数据或已保存数据的数量
  - `_get_next_mapping_id(self)`：获取下一个可用的映射ID，遍历现有映射获取最大ID后加1
  - `_get_next_path_id(self)`：获取下一个可用的路径ID，遍历现有路径获取最大ID后加1
  - `_get_next_action_id(self)`：获取下一个可用的操作ID，遍历现有操作获取最大ID后加1
  - `reset_to_default(self)`：重置手势库为默认设置，重新加载默认手势并保存

- `get_gesture_library()`：单例函数，获取手势库实例

**数据结构**：
```json
{
  "trigger_paths": {
    "1": {
      "name": "向右滑动",
      "path": {
        "points": [[0, 0], [100, 0]],
        "connections": [{"from": 0, "to": 1, "type": "line"}]
      }
    }
  },
  "execute_actions": {
    "1": {
      "name": "复制",
      "type": "shortcut",
      "value": "Ctrl+C"
    }
  },
  "gesture_mappings": {
    "1": {
      "name": "复制手势",
      "trigger_path_id": 1,
      "execute_action_id": 1
    }
  }
}
```

**使用方法**：
```python
# 获取手势库实例
from ui.gestures.gestures import get_gesture_library
gesture_library = get_gesture_library()

# 获取各部分数据
trigger_paths = gesture_library.trigger_paths
execute_actions = gesture_library.execute_actions
gesture_mappings = gesture_library.gesture_mappings

# 检查是否有未保存变更
if gesture_library.has_changes():
    print("有未保存的变更")

# 根据绘制路径查找匹配手势
drawn_path = {"points": [[0, 0], [100, 0]], "connections": [...]}
gesture_name, action, similarity = gesture_library.get_gesture_by_path(drawn_path)
if action:
    print(f"识别到手势: {gesture_name}, 操作: {action['name']}")

# 保存手势库
success = gesture_library.save()
if success:
    print("手势库已保存")

# 重置为默认
gesture_library.reset_to_default()
```

##### 2.2.2 手势管理主页面 (ui/gestures/gestures_tab.py)

**功能说明**：
手势管理主页面，提供可视化的手势映射界面。采用左右卡片布局和中间连线设计，用户可以直观地看到执行操作和触发路径的映射关系，并通过卡片上的按钮进行编辑和管理。

**界面架构**：
- **左侧操作列**：显示所有执行操作卡片，每个卡片包含操作名称、内容预览和映射状态
- **中间连线区**：显示操作与路径之间的映射连线，支持可视化连接关系
- **右侧路径列**：显示所有触发路径卡片，每个卡片包含路径名称和映射状态
- **底部固定按钮**：重置、放弃修改、保存设置按钮，不随内容滚动

**主要类和方法**：

**辅助工具函数**：
- `_find_parent_with_refresh(widget)`：查找具有refresh_list方法的父级容器
- `_create_card_button(text, tooltip, style_extra, size)`：统一创建卡片上的小按钮
- `_find_key_by_id(data_dict, target_id)`：通过ID在数据字典中查找对应的key

**ConnectionWidget**：连线绘制组件
- `add_connection(action_id, path_id, start_point, end_point)`：添加映射连线
- `remove_connection(path_id)`：移除指定连线
- `clear_connections()`：清空所有连线
- `mousePressEvent(event)`：鼠标点击选择连线
- `keyPressEvent(event)`：键盘Delete键删除选中连线
- `paintEvent(event)`：绘制所有连线和箭头

**ActionCardWidget**：操作卡片组件
- `__init__(action_id, action_name, action_value)`：初始化操作卡片
- `set_selected(is_selected)`：设置选中状态
- `set_mapped_count(count)`：设置映射的路径数量
- `_edit_action()`：编辑操作，弹出编辑对话框
- `_delete_action()`：删除操作，确认后删除

**PathCardWidget**：路径卡片组件
- `__init__(path_id, path_name)`：初始化路径卡片
- `set_mapped(is_mapped, action_name)`：设置映射状态和对应操作名称
- `_edit_path()`：编辑路径，弹出编辑对话框
- `_delete_path()`：删除路径，确认后删除

**ActionCardsWidget**：操作卡片容器
- `add_action_card(action_id, action_name, action_value)`：添加操作卡片
- `_add_new_action()`：添加新操作，弹出添加对话框
- `clear_all_selections()`：清除所有选中状态

**PathCardsWidget**：路径卡片容器
- `add_path_card(path_id, path_name)`：添加路径卡片
- `_add_new_path()`：添加新路径，弹出添加对话框

**GesturesPage**：手势管理主页面类
- `__init__(parent=None)`：初始化手势管理主页面，设置变更检测定时器
- `initUI()`：初始化用户界面，创建滚动区域和固定按钮布局
- `_create_actions_panel()`：创建左侧操作卡片面板
- `_create_paths_panel()`：创建右侧路径卡片面板
- `_load_data()`：加载所有数据，包括操作、路径和映射
- `_load_actions()`：加载执行操作卡片
- `_load_paths()`：加载触发路径卡片
- `_load_existing_mappings()`：加载现有映射关系
- `_on_action_clicked(action_id, global_pos)`：处理操作卡片点击
- `_on_path_clicked(path_id, global_pos)`：处理路径卡片点击
- `_create_mapping(action_id, path_id)`：创建新的映射关系
- `_update_connections()`：更新连线显示
- `_check_library_changes()`：定时检查手势库变更状态
- `_save_gesture_library()`：保存手势库到文件
- `_reset_to_default()`：重置手势库为默认设置
- `_discard_changes()`：放弃所有未保存的修改
- `refresh_list()`：刷新整个页面显示

**交互流程**：
1. **创建映射**：点击左侧操作卡片选中，再点击右侧路径卡片完成映射
2. **编辑元素**：点击卡片右上角的编辑按钮(✏)打开编辑对话框
3. **删除元素**：点击卡片右上角的删除按钮(✕)确认删除
4. **添加元素**：点击列表底部的"+ 添加"按钮打开添加对话框
5. **删除映射**：选中连线后按Delete键删除映射关系

**自动化功能**：
- **变更检测**：每秒自动检查手势库变更状态，更新按钮状态
- **实时刷新**：检测到数据变更后自动刷新显示
- **状态同步**：卡片状态与数据模型保持同步

**使用方法**：
```python
# 创建手势管理主页面
from ui.gestures.gestures_tab import GesturesPage

# 创建页面实例
gestures_page = GesturesPage()

# 页面会自动加载数据并显示
# 用户可以通过界面进行交互操作

# 程序化操作
gestures_page.refresh_list()              # 刷新显示
gestures_page._save_gesture_library()     # 保存手势库
gestures_page._reset_to_default()         # 重置为默认
gestures_page._discard_changes()          # 放弃修改
```

##### 2.2.3 手势编辑对话框 (ui/gestures/gesture_dialogs.py)

**功能说明**：
手势编辑对话框模块，提供操作和路径的添加、编辑功能。这些对话框重用了原有选项卡中的表单组件，保持了界面一致性和功能完整性。对话框采用模态设计，确保用户专注于当前编辑任务。

**主要类和方法**：

**TriggerPathEditDialog**：触发路径编辑对话框
- `__init__(self, path_key=None, parent=None)`：初始化路径编辑对话框，支持添加新路径或编辑现有路径
- `initUI(self)`：初始化对话框界面，包含基本信息组和路径绘制组
- `_load_path_data(self)`：加载现有路径数据到表单和绘制组件
- `_on_path_completed(self, path)`：处理路径绘制完成事件
- `_on_path_updated(self)`：处理路径更新事件
- `_clear_drawing(self)`：清空绘制内容
- `_save_and_accept(self)`：保存路径数据并接受对话框

**ExecuteActionEditDialog**：执行操作编辑对话框
- `__init__(self, action_key=None, parent=None)`：初始化操作编辑对话框，支持添加新操作或编辑现有操作
- `initUI(self)`：初始化对话框界面，包含操作信息输入组
- `_load_action_data(self)`：加载现有操作数据到表单
- `_save_and_accept(self)`：保存操作数据并接受对话框

**TestSimilarityDialog**：测试相似度对话框
- `__init__(self, reference_path, parent=None)`：初始化相似度测试对话框，接收参考路径
- `_init_ui(self)`：初始化对话框界面，包含参考路径显示、测试绘制区域和相似度结果面板
- `_create_reference_panel(self)`：创建参考路径显示面板
- `_create_test_panel(self)`：创建测试绘制面板
- `_create_similarity_panel(self)`：创建相似度结果显示面板
- `_on_test_path_completed(self, path)`：处理测试路径绘制完成事件
- `_calculate_similarity(self)`：计算参考路径与测试路径的相似度
- `_update_similarity_display(self)`：更新相似度显示，包含颜色编码的结果状态
- `_clear_test(self)`：清除测试绘制内容

**ReferencePathDisplay**：参考路径显示组件
- `__init__(self, path, parent=None)`：初始化参考路径显示组件
- `paintEvent(self, event)`：绘制参考路径，包含自动缩放和居中显示

**TestDrawingWidget**：测试绘制组件
- `pathCompleted = Signal(dict)`：路径完成信号
- `__init__(self, parent=None)`：初始化测试绘制组件
- `mousePressEvent(self, event)`：处理鼠标按下事件，开始绘制
- `mouseMoveEvent(self, event)`：处理鼠标移动事件，添加绘制点
- `mouseReleaseEvent(self, event)`：处理鼠标释放事件，完成绘制并发送信号
- `paintEvent(self, event)`：绘制事件处理，显示当前绘制和完成的路径
- `_draw_completed_path(self, painter)`：绘制已完成的路径
- `clear_drawing(self)`：清空绘制内容

**对话框特性**：
- **模态设计**：确保用户专注于当前编辑任务
- **数据验证**：自动验证输入数据的完整性和有效性
- **实时预览**：操作和路径的实时预览和编辑
- **自动保存**：确认后自动保存到手势库
- **错误处理**：友好的错误提示和处理

**界面布局**：

**操作编辑对话框布局(ExecuteActionEditDialog)**：
- **操作信息组**：包含操作名称、类型和值的表单输入
  - **操作名称**：文本输入框，用于设置操作的显示名称
  - **操作类型**：下拉选择框，当前支持"快捷键"类型
  - **操作值**：文本输入框，用于输入具体的快捷键组合（如"Ctrl+C"）
- **按钮区域**：确定和取消按钮

**路径编辑对话框布局(TriggerPathEditDialog)**：
- **基本信息组**：包含路径名称输入
  - **路径名称**：文本输入框，用于设置路径的显示名称
- **路径绘制组**：集成的手势绘制组件，支持路径绘制和编辑
- **按钮区域**：确定、取消和清空绘制按钮

**相似度测试对话框布局(TestSimilarityDialog)**：
- **标题区域**：显示"手势相似度测试"标题
- **内容区域**：左右分栏布局
  - **左侧面板**：参考路径显示区域，显示原始手势路径
  - **右侧面板**：测试绘制区域，用户可在此绘制测试手势
- **相似度结果面板**：显示计算结果、进度条和识别阈值
- **按钮区域**：清除测试和关闭按钮

**数据流程**：
1. **打开对话框**：从主页面卡片的编辑/添加按钮触发
2. **加载数据**：如果是编辑模式，自动加载现有数据到表单
3. **用户编辑**：用户修改名称、类型、值或绘制路径
4. **验证输入**：确认时自动验证数据完整性
5. **保存数据**：验证通过后保存到手势库
6. **刷新界面**：自动刷新主页面显示最新数据

**使用方法**：
```python
# 添加新操作
from ui.gestures.gesture_dialogs import ExecuteActionEditDialog

# 创建添加对话框
add_dialog = ExecuteActionEditDialog(parent=main_window)
if add_dialog.exec() == QDialog.Accepted:
    print("操作已添加")

# 编辑现有操作
edit_dialog = ExecuteActionEditDialog(action_key="action_1", parent=main_window)
if edit_dialog.exec() == QDialog.Accepted:
    print("操作已更新")

# 添加新路径
from ui.gestures.gesture_dialogs import TriggerPathEditDialog

# 创建添加对话框
add_dialog = TriggerPathEditDialog(parent=main_window)
if add_dialog.exec() == QDialog.Accepted:
    print("路径已添加")

# 编辑现有路径
edit_dialog = TriggerPathEditDialog(path_key="path_1", parent=main_window)
if edit_dialog.exec() == QDialog.Accepted:
    print("路径已更新")

# 测试手势相似度
from ui.gestures.gesture_dialogs import TestSimilarityDialog

# 创建相似度测试对话框
reference_path = {"points": [[0, 0], [100, 100]], "connections": [...]}
test_dialog = TestSimilarityDialog(reference_path, parent=main_window)
test_dialog.exec()

# 对话框会自动处理数据验证和保存
# 主页面会自动刷新显示最新数据
```

##### 2.2.4 手势绘制组件 (ui/gestures/drawing_widget.py)

**功能说明**：
手势绘制组件，提供可视化的手势路径绘制和编辑功能。支持多种绘制工具、历史记录、视图变换和路径测试等功能。集成在路径编辑对话框中，为用户提供直观的手势路径创建和编辑体验。

**主要类和信号**：
- `GestureDrawingWidget`：手势绘制组件类
  - `pathCompleted = Signal(dict)`：路径完成信号，发送格式化的路径数据
  - `pathUpdated = Signal()`：路径更新信号，用于通知路径已修改
  - `testSimilarity = Signal()`：测试相似度信号

**核心属性**：
- **绘制状态**：`drawing`、`current_path`、`completed_paths`
- **历史记录**：`path_history`、`history_index`（支持撤回/还原）
- **工具状态**：`current_tool`（brush/pointer）、`selected_point_index`、`dragging_point`
- **视图变换**：`view_scale`、`view_offset`、`min_scale`、`max_scale`
- **交互状态**：`panning`、`space_pressed`、`left_shift_pressed`、`right_shift_pressed`

**主要方法分类**：

**初始化和UI**：
- `__init__(self, parent=None)`：初始化绘制组件，设置默认状态和事件处理
- `initUI(self)`：初始化用户界面，创建工具栏和绘制区域
- `create_toolbar(self)`：创建左侧工具栏，包含所有绘制工具

**工具管理**：
- `load_svg_icon(self, filename)`：加载SVG图标，支持SVG不可用时的降级处理
- `select_brush_tool(self)`：选择画笔工具，用于连续路径绘制
- `select_pointer_tool(self)`：选择点击工具，用于精确点编辑
- `update_toolbar_buttons(self)`：更新工具栏按钮的启用/禁用状态

**历史记录系统**：
- `undo_action(self)`：撤回操作（快捷键Ctrl+Z）
- `redo_action(self)`：还原操作（快捷键Ctrl+Y）
- `save_to_history(self)`：保存当前状态到历史记录，支持分支历史

**事件处理**：
- `keyPressEvent(self, event)`：键盘按下事件，支持Ctrl+Z/Y、Space、Delete等
- `keyReleaseEvent(self, event)`：键盘释放事件，处理修饰键状态
- `wheelEvent(self, event)`：滚轮事件，实现缩放和平移功能
- `mousePressEvent(self, event)`：鼠标按下事件，处理绘制开始和工具选择
- `mouseMoveEvent(self, event)`：鼠标移动事件，处理绘制进行和点拖拽
- `mouseReleaseEvent(self, event)`：鼠标释放事件，完成绘制和点操作

**视图变换**：
- `_screen_to_view(self, screen_pos)`：屏幕坐标转换为视图坐标
- `_reset_view(self)`：重置视图变换到默认状态
- `_is_in_drawing_area(self, pos)`：检查位置是否在绘制区域内
- `_adjust_for_drawing_area(self, pos)`：调整坐标到绘制区域范围

**点操作（点击工具模式）**：
- `_handle_pointer_click(self, screen_pos)`：处理点击工具的单击事件
- `_find_point_at_position(self, screen_pos, tolerance=15)`：查找指定位置附近的点
- `_add_new_point(self, screen_pos)`：在指定位置添加新点
- `_update_dragging_point(self, screen_pos)`：更新正在拖拽的点位置
- `_apply_angle_snap(self, path_index, point_index, new_pos, use_left_shift)`：应用角度约束功能，约束到30度和45度的整数倍角度
- `_delete_selected_point(self)`：删除当前选中的点

**绘制和渲染**：
- `paintEvent(self, event)`：主绘制事件，渲染所有路径、工具状态和UI元素
- `_get_point_position(self, point)`：获取点的屏幕坐标位置
- `_draw_formatted_path(self, painter, path)`：绘制格式化的路径数据
- `_draw_direction_arrow(self, painter, start_point, end_point)`：绘制路径方向箭头

**路径管理**：
- `clear_drawing(self)`：清空所有绘制内容，重置到初始状态
- `load_path(self, path)`：加载外部路径数据到绘制区域
- `test_similarity(self)`：发送测试相似度信号

**工具栏组件**：
- **画笔工具**：用于连续路径绘制，支持平滑绘制
- **点击工具**：用于精确点编辑，支持添加、移动、删除点
- **撤回/还原按钮**：历史记录操作，支持多级撤回
- **测试相似度按钮**：触发路径相似度测试功能

**交互模式详解**：

**画笔工具模式**：
- 左键按下并拖拽：开始绘制连续路径
- 鼠标移动：添加路径点，自动连接前一个点
- 左键释放：完成当前路径段
- 双击：完成整个路径绘制，触发`pathCompleted`信号

**点击工具模式**：
- 左键单击空白区域：添加新的独立点
- 左键单击现有点：选中该点（高亮显示）
- 左键拖拽选中点：移动点位置，支持角度吸附
- 右键点击选中点：删除该点
- Delete键：删除当前选中点

**视图操作**：
- 滚轮上下滚动：缩放视图（0.1x到5.0x范围）
- Space键+鼠标拖拽：平移视图
- Shift+滚轮：水平滚动
- 自动限制缩放和平移范围

**角度约束功能**：
- 左Shift+拖拽点：以前一个连接点为参考，约束到30度和45度的整数倍角度
- 右Shift+拖拽点：以后一个连接点为参考，约束到30度和45度的整数倍角度
- 支持的约束角度：0°、30°、45°、60°、90°、120°、135°、150°等

**键盘快捷键**：
- `Ctrl+Z`：撤回上一步操作
- `Ctrl+Y`：还原被撤回的操作
- `Space`：临时启用平移模式
- `Delete`：删除选中的点（点击工具模式）
- `Left Shift`：拖拽点时以前一个点为参考进行角度约束（30度和45度的整数倍）
- `Right Shift`：拖拽点时以后一个点为参考进行角度约束（30度和45度的整数倍）

**信号系统**：
- `pathCompleted(dict)`：路径绘制完成时发出，携带完整的路径数据
- `testSimilarity()`：用户请求测试相似度时发出

**使用示例**：
```python
# 创建绘制组件
from ui.gestures.drawing_widget import GestureDrawingWidget

# 创建组件实例
drawing_widget = GestureDrawingWidget()

# 连接信号处理
def on_path_completed(path_data):
    """处理路径完成事件"""
    points = path_data['points']
    connections = path_data['connections']
    print(f"路径完成: {len(points)}个点, {len(connections)}个连接")
    
    # 保存路径到手势库
    from ui.gestures.gestures import get_gesture_library
    gesture_lib = get_gesture_library()
    # 处理路径数据...

def on_test_similarity():
    """处理相似度测试请求"""
    # 打开相似度测试对话框
    current_path = drawing_widget.completed_paths[-1] if drawing_widget.completed_paths else None
    if current_path:
        # 启动相似度测试...
        pass

drawing_widget.pathCompleted.connect(on_path_completed)
drawing_widget.testSimilarity.connect(on_test_similarity)

# 设置工具模式
drawing_widget.select_brush_tool()    # 切换到画笔工具
drawing_widget.select_pointer_tool()  # 切换到点击工具

# 程序化操作
drawing_widget.undo_action()          # 撤回
drawing_widget.redo_action()          # 还原
drawing_widget.clear_drawing()        # 清空
drawing_widget.test_similarity()      # 测试相似度

# 加载已有路径
existing_path = {
    "points": [[10, 10], [50, 50], [90, 10]],
    "connections": [
        {"from": 0, "to": 1, "type": "line"},
        {"from": 1, "to": 2, "type": "line"}
    ]
}
drawing_widget.load_path(existing_path)

# 获取当前状态
current_tool = drawing_widget.current_tool      # "brush" 或 "pointer"
is_drawing = drawing_widget.drawing             # 是否正在绘制
scale = drawing_widget.view_scale               # 当前缩放比例
has_content = len(drawing_widget.completed_paths) > 0  # 是否有绘制内容
```

#### 2.3 设置模块

##### 2.3.1 设置管理器 (ui/settings/settings.py)

**功能说明**：
设置管理模块，负责保存和加载用户设置，提供设置的持久化和访问机制。

**主要类和方法**：
- `Settings`：设置管理器类
  - `__init__(self)`：初始化设置管理器
  - `_load_default_settings(self)`：加载默认设置
  - `_get_settings_file_path(self)`：获取设置文件路径
  - `load(self)`：从文件加载设置
  - `save(self)`：保存设置到文件
  - `get(self, key, default=None)`：获取设置项，支持点分隔的嵌套键访问
  - `set(self, key, value)`：设置设置项，支持点分隔的嵌套键设置
  - `reset_to_default(self)`：重置为默认设置
  - `has_changes(self)`：检查是否有未保存的更改
  - `get_app_path(self)`：获取应用程序可执行文件路径
  - `get_app_path_with_silent(self)`：获取带有静默启动参数的应用程序路径，专用于开机自启设置
  - `_get_autostart_dir(self)`：获取自启动目录路径，支持macOS和Linux
  - `_get_autostart_file_path(self)`：获取自启动文件完整路径
  - `_normalize_app_path(self, app_path)`：规范化应用路径格式，为包含空格的路径添加引号
  - `_get_icon_path(self)`：获取应用图标路径，支持多种可能的图标位置
  - `_create_macos_plist(self, app_path)`：创建macOS plist自启动文件内容
  - `_create_linux_desktop(self, app_path)`：创建Linux desktop自启动文件内容
  - `is_autostart_enabled(self)`：检查应用程序是否设置为开机自启动，支持Windows、macOS和Linux系统
  - `set_autostart(self, enable)`：设置开机自启动状态，在不同系统上使用不同的实现方式
  - `_set_windows_autostart(self, enable, app_path)`：Windows平台特定的自启动设置，通过注册表实现
  - `_set_macos_autostart(self, enable, app_path)`：macOS平台特定的自启动设置，通过LaunchAgents的plist文件实现
  - `_set_linux_autostart(self, enable, app_path)`：Linux平台特定的自启动设置，通过~/.config/autostart目录下的.desktop文件实现

- `get_settings()`：获取设置管理器实例的单例函数

**设置文件管理**：
- 默认设置来源：`ui/settings/default_settings.json`
- 用户设置保存路径：`~/.xkaaaaa/gestrokey/config/settings.json`
- 支持的设置项：
  - `pen_width`：笔尖粗细，范围1-20像素
  - `pen_color`：笔尖颜色，RGB格式数组
  - `brush_type`：画笔类型，支持 "pencil"(铅笔)、"water"(水性笔)、"calligraphy"(毛笔)
  - `brush.force_topmost`：绘制时强制置顶，布尔值，默认true
  - `gesture.similarity_threshold`：手势相似度阈值，范围0.0-1.0，默认0.70

**使用方法**：
```python
from ui.settings.settings import get_settings

# 获取设置管理器实例
settings = get_settings()

# 读取设置
pen_width = settings.get("pen_width")  # 返回笔尖粗细设置，默认为3
pen_color = settings.get("pen_color")  # 返回笔尖颜色设置，默认为[0, 120, 255]

# 修改设置
settings.set("pen_width", 5)
settings.set("pen_color", [255, 0, 0])  # 设置为红色

# 保存设置
settings.save()

# 检查是否有未保存的更改
has_changes = settings.has_changes()

# 重置为默认设置
settings.reset_to_default()

# 检查开机自启动状态
is_autostart = settings.is_autostart_enabled()

# 设置开机自启动
settings.set_autostart(True)  # 启用
settings.set_autostart(False)  # 禁用
```

##### 2.3.2 设置主页面 (ui/settings/settings_tab.py)

**功能说明**：
设置主页面，提供选项卡式布局，包含应用设置、画笔设置、判断器设置三个子选项卡。采用模块化设计，每个选项卡独立管理自己的设置项。

**主要类和方法**：
- `SettingsPage`：设置主页面类，继承自QWidget
  - `__init__(self, parent=None)`：初始化设置主页面，创建三个子选项卡
  - `_init_ui(self)`：初始化用户界面，创建选项卡控件和底部操作按钮
  - `_on_tab_changed(self, index)`：选项卡切换事件处理
  - `_check_settings_changes(self)`：定时检查设置是否有变更，自动更新保存和放弃按钮状态
  - `has_unsaved_changes(self)`：检查是否有未保存的更改，综合检查所有子选项卡的状态
  - `_mark_changed(self)`：标记设置已更改（由子选项卡调用）
  - `_save_settings(self)`：保存设置到文件，调用所有子选项卡的apply_settings方法
  - `_reset_settings(self)`：重置设置为默认值
  - `_discard_changes(self)`：放弃所有未保存的修改
  - `_reload_all(self)`：重新加载所有子选项卡
  - `_load_settings(self)`：加载设置（调用_reload_all）
  - `_apply_settings(self)`：应用所有子选项卡的设置

**界面结构**：
- **选项卡容器**：包含三个子选项卡
  - 应用设置选项卡（ApplicationSettingsTab）
  - 画笔设置选项卡（BrushSettingsTab）
  - 判断器设置选项卡（RecognizerSettingsTab）
- **底部操作区域**：
  - 重置为默认按钮（120x35px）
  - 放弃修改按钮（100x35px，有变更时自动启用）
  - 保存设置按钮（100x35px，有变更时自动启用）

**自动化功能**：
- **变更检测**：每秒自动检查设置变更状态
- **按钮状态管理**：保存和放弃按钮根据变更状态自动启用/禁用
- **子选项卡协调**：统一管理所有子选项卡的加载、保存和重置操作

**使用方法**：
```python
# 创建设置主页面
from ui.settings.settings_tab import SettingsPage

# 创建页面实例
settings_page = SettingsPage()

# 访问子选项卡
application_tab = settings_page.application_tab     # 应用设置选项卡
brush_tab = settings_page.brush_tab                 # 画笔设置选项卡
recognizer_tab = settings_page.recognizer_tab       # 判断器设置选项卡

# 手动触发操作
settings_page._save_settings()    # 保存所有设置
settings_page._reset_settings()   # 重置为默认值
settings_page._discard_changes()  # 放弃修改
settings_page._reload_all()       # 重新加载所有选项卡

# 获取选项卡控件
tab_widget = settings_page.tab_widget               # QTabWidget控件
current_index = tab_widget.currentIndex()          # 当前选项卡索引
```

##### 2.3.3 应用设置选项卡 (ui/settings/application_settings_tab.py)

**功能说明**：
应用设置选项卡，处理开机自启动、退出行为等应用程序全局设置。

**主要类和方法**：
- `ApplicationSettingsTab`：应用设置选项卡类，继承自QWidget
  - `__init__(self, parent=None)`：初始化应用设置选项卡
  - `_init_ui(self)`：初始化用户界面
  - `_load_settings(self)`：加载设置
  - `_on_autostart_changed(self, state)`：处理开机自启动状态变化
  - `_on_exit_dialog_changed(self, state)`：处理退出对话框设置变化
  - `_on_close_behavior_changed(self)`：处理默认关闭行为变化
  - `_mark_changed(self)`：标记设置已更改，通知父级容器
  - `has_unsaved_changes(self)`：检查是否有未保存的更改
  - `apply_settings(self)`：应用设置

**设置项目**：
- **开机自启动**：设置应用程序是否在系统启动时自动运行（静默模式）
- **退出确认对话框**：关闭程序时是否显示确认对话框
- **默认关闭行为**：当不显示退出对话框时的默认行为（最小化到托盘/退出程序）

**使用方法**：
```python
from ui.settings.application_settings_tab import ApplicationSettingsTab

# 创建应用设置选项卡
app_tab = ApplicationSettingsTab()

# 检查未保存更改
has_changes = app_tab.has_unsaved_changes()

# 应用设置
success = app_tab.apply_settings()
```

##### 2.3.4 画笔设置选项卡 (ui/settings/brush_settings_tab.py)

**功能说明**：
画笔设置选项卡，处理笔尖粗细、颜色、画笔类型等绘制相关设置，包含动态预览功能。

**主要类和方法**：
- `BrushSettingsTab`：画笔设置选项卡类，继承自QWidget
  - `__init__(self, parent=None)`：初始化画笔设置选项卡
  - `_init_ui(self)`：初始化用户界面
  - `_load_settings(self)`：加载设置
  - `showEvent(self, event)`：显示事件处理，启动预览动画
  - `_on_thickness_changed(self, value)`：处理笔尖粗细滑块变化事件
  - `_on_thickness_spinbox_changed(self, value)`：处理笔尖粗细数字框变化事件
  - `_on_color_button_clicked(self)`：处理颜色选择按钮点击事件
  - `_on_brush_type_changed(self)`：处理画笔类型变化事件
  - `_on_force_topmost_changed(self, state)`：处理强制置顶选项变化事件
  - `_mark_changed(self)`：标记设置已更改，通知父级容器
  - `has_unsaved_changes(self)`：检查是否有未保存的更改
  - `apply_settings(self)`：应用设置
  - `_apply_pen_settings_to_drawing_module(self, width, color)`：实时应用画笔设置到绘制模块
  - `_find_main_window(self)`：查找主窗口实例

- `ColorPreviewWidget`：颜色预览控件类，继承自QWidget
  - `set_color(self, color)`：设置颜色
  - `get_color(self)`：获取颜色
  - `paintEvent(self, event)`：绘制颜色预览

**设置项目**：
- **笔尖粗细**：1-20像素，滑块和数字框双向同步
- **笔尖颜色**：RGB颜色选择，带颜色预览
- **画笔类型**：铅笔、水性笔、毛笔三种类型
- **绘制时强制置顶**：确保绘画窗口始终保持在最前面
- **动态预览**：实时显示画笔效果

**使用方法**：
```python
from ui.settings.brush_settings_tab import BrushSettingsTab

# 创建画笔设置选项卡
brush_tab = BrushSettingsTab()

# 访问设置组件
thickness_slider = brush_tab.thickness_slider        # 粗细滑块
color_preview = brush_tab.color_preview              # 颜色预览
pen_preview = brush_tab.pen_preview                  # 动态预览
```

##### 2.3.5 判断器设置选项卡 (ui/settings/recognizer_settings_tab.py)

**功能说明**：
判断器设置选项卡，处理手势识别相似度阈值等识别相关设置。

**主要类和方法**：
- `RecognizerSettingsTab`：判断器设置选项卡类，继承自QWidget
  - `__init__(self, parent=None)`：初始化判断器设置选项卡
  - `_init_ui(self)`：初始化用户界面
  - `_load_settings(self)`：加载设置
  - `_on_threshold_changed(self, value)`：处理相似度阈值变化事件
  - `_mark_changed(self)`：标记设置已更改，通知父级容器
  - `has_unsaved_changes(self)`：检查是否有未保存的更改
  - `apply_settings(self)`：应用设置

**设置项目**：
- **相似度阈值**：手势识别的相似度阈值（0.0-1.0），值越高要求越严格

**使用方法**：
```python
from ui.settings.recognizer_settings_tab import RecognizerSettingsTab

# 创建判断器设置选项卡
recognizer_tab = RecognizerSettingsTab()

# 访问阈值设置
threshold = recognizer_tab.threshold_spinbox.value()
```

##### 2.3.6 动态预览组件 (ui/settings/pen_preview_widget.py)

**功能说明**：
动态预览组件，用于在设置页面实时预览不同画笔效果。支持随机生成多种类型的手势路径，具备智能的路径优化和合理性检测功能。

**主要类和方法**：
- `PenPreviewWidget`：动态预览组件类，继承自QWidget
  - `__init__(self, parent=None)`：初始化预览组件，设置接近正方形的尺寸(160x140到300x280)
  - `_generate_random_gesture_path(self)`：生成随机手势路径，支持多种路径类型
  - `_generate_path_by_type(self, path_type, safe_margin, safe_width, safe_height)`：根据指定类型生成路径
  - `_validate_and_optimize_path(self, points)`：验证和优化路径，防止笔画粘连和超出区域
  - `_generate_simple_fallback_path(self)`：生成简单的后备路径
  - `update_pen(self, width, color, brush_type)`：更新画笔参数并重新生成路径
  - `_start_animation(self)`：开始播放绘制动画
  - `_update_animation(self)`：更新动画帧，支持20FPS的流畅动画
  - `paintEvent(self, event)`：绘制预览效果，包含实时绘制光标和状态信息
  - `mousePressEvent(self, event)`：处理鼠标点击，重新生成随机路径并播放

**路径类型**：
- **曲线路径(curved)**：基于正弦函数的平滑曲线
- **锯齿路径(zigzag)**：规律的锯齿形状
- **环形路径(loop)**：完整的圆形或椭圆形路径
- **波浪路径(wave)**：多频率的波浪形状
- **螺旋路径(spiral)**：从中心向外的螺旋形状

**智能优化功能**：
- **尺寸自适应**：根据组件尺寸自动调整路径生成参数
- **笔画粗细检测**：基于笔画粗细动态调整安全边距和最小点距离
- **粘连防护**：自动检测并避免笔画过于密集导致的粘连问题
- **边界约束**：确保所有路径点都在安全边界内，防止超出绘制区域
- **路径验证**：对生成的路径进行合理性检测，不合理时自动生成后备路径

**动画特性**：
- **20FPS动画**：50ms间隔的流畅动画播放
- **实时光标**：红色圆点显示当前绘制位置
- **进度显示**：实时显示绘制进度百分比
- **多画笔支持**：支持铅笔、水性笔、毛笔三种画笔类型的真实效果预览
- **参数响应**：参数变更时自动重新生成路径并播放动画

**使用方法**：
```python
# 创建动态预览组件
from ui.settings.pen_preview_widget import PenPreviewWidget

# 创建组件实例（接近正方形）
preview = PenPreviewWidget()

# 更新画笔参数（会自动重新生成随机路径）
preview.update_pen(width=5, color=[255, 0, 0], brush_type="water")

# 手动触发重新预览（生成新的随机路径）
# 用户点击组件即可触发

# 组件自动处理：
# - 尺寸变化时重新生成适应的路径
# - 笔画粗细变化时调整安全边距
# - 不同画笔类型的真实绘制效果
# - 路径合理性验证和优化
```

**技术特点**：
- **模块化设计**：独立的预览组件，可在任何需要画笔预览的地方使用
- **性能优化**：使用QPixmap缓冲区避免重复绘制，提高动画流畅度
- **真实绘制**：直接使用核心画笔模块进行绘制，确保预览效果与实际绘制一致
- **随机多样性**：支持5种不同的路径类型，每次点击都有不同的预览效果
- **智能约束**：基于笔画粗细的智能边距和距离控制，确保预览效果合理美观

### 3. 核心功能模块

#### 3.1 core/brush/

**功能说明**：
画笔绘制模块，负责全局鼠标手势的捕获、绘制和路径分析。提供透明覆盖层用于显示绘制轨迹，支持实时手势识别和执行。该模块采用模块化设计，分为管理器、覆盖层、绘制逻辑和淡出效果四个子模块。

##### 3.1.1 core/brush/manager.py

**主要类和方法**：
- `DrawingManager`：绘制管理器类，负责整体绘制功能的控制
  - `__init__(self)`：初始化管理器，创建信号对象、透明覆盖层和鼠标监听器
  - `start(self)`：启动绘制功能，加载设置并开始全局鼠标监听
  - `stop(self)`：停止绘制功能，清理资源并停止监听
  - `update_settings(self)`：更新绘制参数，无需重启即可应用新设置
  - `get_last_direction(self)`：获取最后一次绘制的方向信息
  - `_init_mouse_hook(self)`：初始化全局鼠标钩子，监听右键绘制

- `DrawingSignals`：信号类，用于线程间安全通信
  - `start_drawing_signal`：开始绘制信号 (x, y, pressure)
  - `continue_drawing_signal`：继续绘制信号 (x, y, pressure)
  - `stop_drawing_signal`：停止绘制信号

**使用方法**：
```python
from core.brush.manager import DrawingManager

# 创建绘制管理器
manager = DrawingManager()

# 开始绘制功能（启动全局监听）
manager.start()

# 用户现在可以使用鼠标右键进行绘制
# 绘制完成后会自动进行手势识别和执行

# 更新设置参数
manager.update_settings()

# 停止绘制功能
manager.stop()
```

##### 3.1.2 core/brush/overlay.py

**主要类和方法**：
- `DrawingSignals`：信号类，用于在线程间安全地传递信号，继承自QObject
  - `start_drawing_signal`：开始绘制信号 (x, y, pressure)
  - `continue_drawing_signal`：继续绘制信号 (x, y, pressure)
  - `stop_drawing_signal`：停止绘制信号

- `TransparentDrawingOverlay`：透明绘制覆盖层类
  - `__init__(self)`：初始化覆盖层，设置透明窗口、绘制参数和定时器
  - `initUI(self)`：初始化UI，创建全屏透明窗口
  - `set_pen_width(self, width)`：设置笔尖粗细
  - `set_pen_color(self, color)`：设置笔尖颜色 [r, g, b] 格式
  - `set_brush_type(self, brush_type)`：设置画笔类型 ("pencil"、"water"或"calligraphy")
  - `set_force_topmost(self, enabled)`：设置是否启用强制置顶功能
  - `startDrawing(self, x, y, pressure=0.5)`：开始绘制，创建画笔实例并显示窗口
  - `continueDrawing(self, x, y, pressure=0.5)`：继续绘制，添加轨迹点
  - `stopDrawing(self)`：停止绘制，分析路径并发送给手势识别器
  - `paintEvent(self, event)`：绘制事件处理，渲染不同类型的画笔效果

##### 3.1.3 core/brush/drawing.py

**主要类和方法**：

**BaseBrush (画笔基类)**：
- `__init__(self, width=2, color=None)`：初始化画笔基本属性
- `start_stroke(self, x, y, pressure=0.5)`：开始一笔 (抽象方法)
- `add_point(self, x, y, pressure=0.5)`：添加点到当前笔画 (抽象方法)
- `end_stroke(self)`：结束当前笔画 (抽象方法)
- `draw(self, painter, points=None)`：绘制笔画 (抽象方法)

**PencilBrush (铅笔画笔)**：
- 传统绘制效果，线条粗细恒定
- 使用 `QPainterPath` 绘制平滑连续线条
- 支持圆角端点和连接点
- 最小绘制距离阈值防止过密集的点

**WaterBrush (水性笔画笔)**：
- 动态效果，新出现的点由细变粗
- `growth_duration = 0.15秒`：点变粗的时间
- `min_size_ratio = 0.1`：最小尺寸比例
- 支持笔画结束后所有点保持最大尺寸

**CalligraphyBrush (毛笔画笔)**：
- 模拟毛笔书法效果，具有传统水墨韵味
- 动态笔画宽度，根据速度和距离调整粗细
- 墨色渐变效果，每个笔画段支持深浅变化
- 毛丝效果，添加细小的毛笔纤维模拟
- 随机墨滴和墨晕效果，增强真实感
- 基于随机算法生成自然的毛笔质感

**DrawingModule (绘制模块管理器)**：
- `set_brush_type(self, brush_type)`：设置当前画笔类型
- `get_brush_types(self)`：获取所有可用的画笔类型列表
- `create_brush(self, width, color)`：创建当前类型的画笔实例
- `get_current_brush_type(self)`：获取当前画笔类型
- 支持的画笔类型：
  - `"pencil"`：铅笔，传统绘制效果
  - `"water"`：水性笔，动态变粗效果
  - `"calligraphy"`：毛笔，书法墨色效果

##### 3.1.4 core/brush/fading.py

**主要类和方法**：
- `FadingModule`：淡出效果管理器，继承自QObject
  - `fade_update`：淡出更新信号，用于通知重绘
  - `fade_complete`：淡出完成信号，用于通知淡出结束
  - `__init__(self, parent=None)`：初始化淡出模块
  - `start_fade(self)`：开始淡出动画
  - `stop_fade(self)`：停止淡出动画
  - `get_fade_alpha(self)`：获取当前透明度值 (0-255)
  - `_update_fade(self)`：内部方法，更新淡出状态

**淡出机制**：
- 绘制完成后，线条在指定时间内逐渐变透明
- 使用 `QTimer` 实现平滑的透明度变化
- 淡出完成后自动隐藏覆盖层并清理数据
- 支持中途打断淡出过程（新绘制开始时）

#### 3.2 core/path_analyzer.py

**功能说明**：
路径分析模块，负责将用户绘制的原始轨迹转换为结构化路径数据，并提供手势相似度计算。该模块是GestroKey手势识别系统的核心，专注于形状轮廓识别和绘制顺序分析。

**主要类和方法**：

**PathAnalyzer 路径分析器类**：
- `__init__(self)`：初始化路径分析器，设置日志记录器
- `format_raw_path(self, raw_points: List[Tuple]) -> Dict`：将原始绘制点转换为格式化路径，流程包括坐标转换、尺寸缩放、关键点提取、连接生成
- `calculate_similarity(self, path1: Dict, path2: Dict) -> float`：计算两个路径的相似度，结果范围[0,1]，综合考虑形状轮廓和笔画顺序，支持正向和反向匹配
- `normalize_path_scale(self, path: Dict, target_size: int = 100) -> Dict`：将路径归一化到指定的边界框尺寸，保持宽高比
- `_scale_small_path(self, coords: List[Tuple[int, int]]) -> List[Tuple[int, int]]`：对尺寸过小的路径进行等比放大，提高后续处理的精度
- `_extract_key_points(self, coords: List[Tuple[int, int]]) -> List[Tuple[int, int]]`：从坐标点中智能提取关键点，保留路径的核心特征
- `_douglas_peucker(self, points: List[Tuple[int, int]], tolerance: float) -> List[Tuple[int, int]]`：使用道格拉斯-普克算法简化路径
- `_analyze_direction_changes(self, points: List[Tuple[int, int]]) -> List[Tuple[int, int]]`：通过分析角度和距离变化，识别重要的转折点
- `_preprocess_for_comparison(self, path: Dict, target_size: int = 200, resample_n: int = 64) -> np.ndarray | None`：为相似度计算准备路径，归一化和重采样
- `_resample_points(self, pts: np.ndarray, target_n: int) -> np.ndarray`：沿曲线总长度等距采样指定数量的点
- `_compute_scores(self, pts1: np.ndarray, pts2: np.ndarray) -> Tuple[float, float]`：计算两条点集的形状得分和方向得分
- `_procrustes_align(self, A: np.ndarray, B: np.ndarray) -> np.ndarray`：通过旋转和平移将点集A对齐到点集B
- `_get_path_bbox(self, points: List[Tuple]) -> Dict`：计算路径的边界框
- `_calculate_path_length(self, points: List[Tuple[int, int]]) -> float`：计算路径的总长度
- `_calculate_angle_change(self, p1: Tuple, p2: Tuple, p3: Tuple) -> float`：计算三点构成的夹角变化
- `_distance_to_line(self, p1: Tuple, p2: Tuple, point: Tuple) -> float`：计算一个点到由另外两点确定的线段的距离

**核心算法特性**：
- **路径预处理**：自动识别并放大小于50像素的微小路径至200像素，提高识别精度
- **关键点提取**：道格拉斯-普克算法（容忍度8.0像素）结合转折点检测（角度阈值30度）
- **相似度计算**：综合形状轮廓（55%权重）和笔画顺序（45%权重），支持正向和反向匹配
- **路径归一化**：保持宽高比的尺寸标准化，支持多种目标尺寸
- **重采样技术**：沿路径等距采样64个点，确保比较的一致性

**路径数据结构**：
```python
# 输入原始点格式
raw_points = [(x, y, pressure, tilt, button), ...]

# 输出格式化路径
formatted_path = {
    'points': [(x1, y1), (x2, y2), ...],    # 关键点坐标列表
    'connections': [                         # 连接关系列表
        {'from': 0, 'to': 1, 'type': 'line'},
        {'from': 1, 'to': 2, 'type': 'line'},
        ...
    ]
}
```

**使用方法**：
```python
from core.path_analyzer import PathAnalyzer

# 创建路径分析器实例
analyzer = PathAnalyzer()

# 格式化原始绘制轨迹
raw_points = [(100, 100, 0.5, 0.0, 1), (150, 120, 0.6, 0.0, 1), ...]
formatted_path = analyzer.format_raw_path(raw_points)

# 计算两个路径的相似度
similarity = analyzer.calculate_similarity(path1, path2)
print(f"相似度: {similarity:.3f}")

# 归一化路径尺寸
normalized_path = analyzer.normalize_path_scale(path, target_size=200)
```

#### 3.3 core/gesture_executor.py

**功能说明**：
手势执行模块，负责执行识别到的手势对应的操作，主要支持快捷键操作。采用单例模式确保全局唯一实例，基于pynput库实现跨平台键盘控制。

**主要类和方法**：
- `GestureExecutor`：手势执行器类（单例模式）
  - `get_instance()`：类方法，获取手势执行器的全局唯一实例
  - `__init__(self)`：初始化手势执行器，设置键盘控制器和特殊键映射，初始化手势库
  - `execute_gesture_by_path(self, drawn_path)`：根据绘制路径执行对应的手势动作，核心执行入口
  - `_execute_shortcut(self, shortcut_str)`：执行快捷键操作，支持多种快捷键格式
  - `_press_keys(self, modifier_keys, regular_keys)`：按下并释放快捷键组合，采用线程化执行
  - `release_all_keys(self)`：释放所有可能按下的键，用于程序退出前的清理操作

**全局函数**：
- `get_gesture_executor()`：获取手势执行器的全局实例

**手势执行流程**：
1. **路径匹配**：将绘制路径与手势库中的触发路径逐一对比
2. **相似度计算**：选出相似度大于阈值中相似度最高的手势
3. **操作查找**：通过映射关系找到对应的执行操作
4. **动作执行**：将执行操作交给相应的执行模块处理

**支持的快捷键格式**：
- **修饰键**：ctrl, alt, shift, win/cmd/command/meta/super
- **功能键**：f1-f12, esc, tab, enter, space, backspace, delete等
- **方向键**：up/↑, down/↓, left/←, right/→
- **特殊键**：home, end, page_up, page_down, insert等
- **符号键**：支持Unicode符号如⌃⌥⇧⌘

**特殊键映射字典**：
包含100+个键位的映射关系，支持多种别名和Unicode符号，确保跨平台兼容性。

**使用方法**：
```python
from core.gesture_executor import get_gesture_executor

# 获取执行器实例
executor = get_gesture_executor()

# 根据路径执行手势
drawn_path = {
    'points': [(100, 100), (200, 100)],
    'connections': [{'from': 0, 'to': 1, 'type': 'line'}]
}
success = executor.execute_gesture_by_path(drawn_path)
if success:
    print("手势执行成功")
else:
    print("手势执行失败")

# 程序退出前清理
executor.release_all_keys()
```

#### 3.4 core/system_monitor.py

**功能说明**：
系统监测模块，基于psutil库提供CPU、内存使用率等系统信息的实时监测功能，使用Qt信号机制进行数据更新通知。

**主要类和方法**：
- `SystemMonitor`：系统监测器类，继承自QObject
  - `dataUpdated`：数据更新信号，参数为包含系统信息的字典
  - `__init__(self, update_interval=1000)`：初始化系统监测器，设置更新间隔（毫秒）
  - `start(self)`：开始监测，启动定时器，返回启动成功状态
  - `stop(self)`：停止监测，停止定时器，返回停止成功状态
  - `is_running(self)`：检查监测器是否正在运行
  - `get_data(self)`：获取当前系统信息数据的副本
  - `_update_data(self)`：内部方法，更新系统数据并发送信号
  - `set_update_interval(self, interval)`：设置更新间隔，运行中会重启定时器
  - `get_update_interval(self)`：获取当前更新间隔
  - `reset_start_time(self)`：重置运行时间计算的起始时间

**监测数据结构**：
```python
{
    "cpu_percent": 25.5,        # CPU使用率百分比
    "memory_percent": 60.2,     # 内存使用率百分比
    "memory_used": 8589934592,  # 已用内存字节数
    "memory_total": 17179869184, # 总内存字节数
    "runtime": "01:23:45",      # 运行时间字符串
    "process_memory": 2.1,      # 当前进程内存使用率
    "process_cpu": 1.5          # 当前进程CPU使用率
}
```

**辅助函数**：
- `format_bytes(bytes_value)`：将字节数格式化为可读的单位（B, KB, MB, GB, TB, PB）

**使用方法**：
```python
from core.system_monitor import SystemMonitor, format_bytes

# 创建监测器实例
monitor = SystemMonitor(update_interval=1500)  # 1.5秒更新一次

# 连接数据更新信号
monitor.dataUpdated.connect(lambda data: print(f"CPU: {data['cpu_percent']:.1f}%"))

# 启动监测
monitor.start()

# 获取当前数据
current_data = monitor.get_data()
print(f"内存使用: {format_bytes(current_data['memory_used'])}")

# 停止监测
monitor.stop()
```

#### 3.5 core/self_check.py

**功能说明**：
自检模块，负责系统启动时的完整性检查和测试。该模块会在程序启动时自动运行，检查手势库和设置文件的格式完整性，验证核心模块功能，并提供损坏文件的备份机制。

**主要类和方法**：
- `SelfChecker`：自检器类
  - `__init__(self)`：初始化自检器，设置日志记录器
  - `run_full_check(self)`：运行完整自检流程，包含所有检查项目
  - `check_json_files(self)`：检查JSON文件格式和完整性，验证手势库和设置文件
  - `backup_damaged_file(self, file_path, error_info)`：备份损坏的文件，使用base64编码输出
  - `check_gesture_library_integrity(self)`：检查手势库数据结构完整性和ID引用关系
  - `check_settings_integrity(self)`：检查设置文件的数据结构和必需字段
  - `test_path_analyzer(self)`：测试路径分析器的基本功能
  - `test_gesture_executor(self)`：测试手势执行器的初始化和基本功能
  - `test_drawing_module(self)`：测试绘制模块的画笔创建功能
  - `test_gestures_module(self)`：测试手势库模块的加载和查询功能
  - `test_settings_module(self)`：测试设置模块的读写功能
  - `_validate_gesture_ids(self, trigger_paths, execute_actions, gesture_mappings)`：验证手势库中的ID引用关系

**全局函数**：
- `run_self_check()`：执行自检的入口函数，创建检查器实例并运行检查

**检查项目**：
- **JSON文件完整性**：验证手势库和设置文件的JSON格式正确性
- **数据结构验证**：检查手势库的三部分数据结构和设置文件结构
- **ID引用关系**：验证手势映射中引用的路径ID和操作ID是否存在
- **核心模块测试**：路径分析器、手势执行器、绘制模块、手势库、设置模块的功能测试
- **损坏文件备份**：发现损坏文件时自动生成base64编码的备份输出

**自动化功能**：
- **启动时检查**：集成到main.py的init_global_resources方法中，每次程序启动自动运行
- **错误恢复**：检测到问题时提供详细的错误信息和修复建议
- **日志记录**：详细记录所有检查过程和结果

**使用方法**：
```python
from core.self_check import run_self_check, SelfChecker

# 运行完整自检（程序启动时自动调用）
success = run_self_check()
if success:
    print("自检通过，系统正常")
else:
    print("自检发现问题，请查看日志")

# 手动创建检查器进行特定检查
checker = SelfChecker()
json_ok = checker.check_json_files()
gesture_ok = checker.check_gesture_library_integrity()
settings_ok = checker.check_settings_integrity()

# 测试特定模块
path_analyzer_ok = checker.test_path_analyzer()
gesture_executor_ok = checker.test_gesture_executor()
```

**集成方式**：
在main.py的init_global_resources方法中自动调用：
```python
def init_global_resources(self):
    """初始化设置管理器和手势库管理器等全局资源"""
    from core.self_check import run_self_check
    
    # 运行自检
    self_check_passed = run_self_check()
    if not self_check_passed:
        self.logger.warning("自检发现潜在问题，请检查日志")
    
    # ... 其他初始化代码
```

#### 3.6 core/logger.py

**功能说明**：
日志记录模块，提供统一的日志记录功能，支持多平台的日志文件存储和控制台输出。

**主要类和方法**：
- `Logger`：日志记录器类
  - `__init__(self, module_name=None)`：初始化日志记录器，设置模块名称
  - `setup_logger(self)`：设置日志记录器，配置文件和控制台处理器
  - `debug(self, message)`：记录调试级别日志
  - `info(self, message)`：记录信息级别日志
  - `warning(self, message)`：记录警告级别日志
  - `error(self, message)`：记录错误级别日志
  - `critical(self, message)`：记录严重错误级别日志
  - `exception(self, message)`：记录异常信息，包含堆栈跟踪

**全局函数**：
- `get_logger(module_name=None)`：获取指定模块名称的日志记录器实例

**日志存储路径**：
- **Windows**: `~/.{AUTHOR}/{APP_NAME}/log/`
- **macOS**: `~/Library/Application Support/{AUTHOR}/{APP_NAME}/log/`
- **Linux**: `~/.config/{AUTHOR}/{APP_NAME}/log/`

**日志文件格式**：
- 文件名：按日期命名，如 `2024-01-01.log`
- 格式：`[时间戳] [级别] [模块名] - 消息内容`
- 编码：UTF-8
- 级别：文件记录DEBUG及以上，控制台记录INFO及以上

**使用方法**：
```python
from core.logger import get_logger

# 获取日志记录器
logger = get_logger("MyModule")

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")

# 记录异常
try:
    1 / 0
except Exception as e:
    logger.exception(f"发生异常: {e}")
```

**集成到主程序**：
在main.py中，系统托盘图标被初始化并连接到相应的处理方法：
```python
def init_system_tray(self):
    """初始化系统托盘图标"""
    self.tray_icon = get_system_tray(self)
    # 连接信号
    self.tray_icon.toggle_drawing_signal.connect(self.toggle_drawing)
    self.tray_icon.show_window_signal.connect(self.show_and_activate)
    self.tray_icon.show_settings_signal.connect(self.show_settings_page)
    self.tray_icon.exit_app_signal.connect(self.close)
    # 显示托盘图标
    self.tray_icon.show()
```

**状态同步机制**：
应用程序状态变化会自动同步到托盘图标，确保界面状态与托盘状态的一致性：
```python
def on_drawing_state_changed(self, is_active):
    """响应控制台页面的绘制状态变化"""
    self.is_drawing_active = is_active
    if hasattr(self, 'tray_icon'):
        self.tray_icon.update_drawing_state(is_active)
```

### 3. 核心功能模块

#### 3.1 core/brush/

**功能说明**：
画笔绘制模块，负责在屏幕上创建透明覆盖层并处理用户的绘制操作。该模块包含绘制管理器、透明覆盖层、画笔实现和淡出效果等组件。

##### 3.1.1 core/brush/manager.py

**功能说明**：
绘制管理器，负责管理绘制功能的启动、停止和设置更新，协调鼠标监听和绘制覆盖层的工作。

**主要类和方法**：
- `DrawingManager`：绘制管理器类
  - `__init__(self)`：初始化绘制管理器，创建信号对象和透明覆盖层，设置鼠标事件限流
  - `start(self)`：开始绘制功能，从设置中加载参数并启动鼠标监听器
  - `update_settings(self)`：更新设置参数，无需重启绘制功能即可应用修改的参数
  - `stop(self)`：停止绘制功能，关闭绘制窗口并停止监听
  - `_init_mouse_hook(self)`：初始化全局鼠标监听，设置右键绘制逻辑
  - `_calculate_simulated_pressure(self, x, y)`：计算模拟压力值，基于移动速度动态调整
  - `get_last_direction(self)`：获取最后一次绘制的方向信息

**核心功能**：
- **设置集成**：自动从设置中加载笔尖粗细、颜色、画笔类型和强制置顶等参数
- **鼠标监听**：使用pynput库实现全局鼠标监听，右键绘制逻辑
- **性能优化**：鼠标移动事件限流（5ms间隔），减少处理频率
- **压力模拟**：基于移动速度计算模拟压力值，速度越快压力越小
- **信号通信**：使用Qt信号机制实现线程间安全通信

**使用方法**：
```python
from core.brush.manager import DrawingManager

# 创建绘制管理器
manager = DrawingManager()

# 启动绘制功能
success = manager.start()
if success:
    print("绘制功能已启动")

# 更新设置
manager.update_settings()

# 停止绘制功能
manager.stop()
```