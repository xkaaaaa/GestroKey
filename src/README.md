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
  - [2.1 界面UI模块](#21-界面ui模块)
    - [2.1.1 控制台选项卡](#211-控制台选项卡-uiconsolepy)
    - [2.1.2 手势管理模块](#212-手势管理模块)
      - [2.1.2.1 手势库](#2121-手势库-uigesturesgesturespy)
      - [2.1.2.2 手势选项卡主页面](#2122-手势选项卡主页面-uigesturesgestures_tabpy)
      - [2.1.2.3 触发路径选项卡](#2123-触发路径选项卡-uigesturestrigger_paths_tabpy)
      - [2.1.2.4 执行操作选项卡](#2124-执行操作选项卡-uigesturesexecute_actions_tabpy)
      - [2.1.2.5 手势映射选项卡](#2125-手势映射选项卡-uigesturesgesture_mappings_tabpy)
      - [2.1.2.6 手势绘制组件](#2126-手势绘制组件-uigesturesdrawing_widgetpy)
    - [2.1.3 设置模块](#213-设置模块)
      - [2.1.3.1 设置管理器](#2131-设置管理器-uisettingssettingspy)
      - [2.1.3.2 设置主页面](#2132-设置主页面-uisettingssettings_tabpy)
      - [2.1.3.3 应用设置选项卡](#2133-应用设置选项卡-uisettingsapplication_settings_tabpy)
      - [2.1.3.4 画笔设置选项卡](#2134-画笔设置选项卡-uisettingsbrush_settings_tabpy)
      - [2.1.3.5 判断器设置选项卡](#2135-判断器设置选项卡-uisettingsrecognizer_settings_tabpy)
      - [2.1.3.6 动态预览组件](#2136-动态预览组件-uisettingspen_preview_widgetpy)
- [3. 核心功能模块](#3-核心功能模块)
  - [3.1 core/brush/](#31-corebrush)
    - [3.1.1 core/brush/manager.py](#311-corebrushmanagerpy)
    - [3.1.2 core/brush/overlay.py](#312-corebrushoverlaypy)
    - [3.1.3 core/brush/drawing.py](#313-corebrushdrawingpy)
    - [3.1.4 core/brush/fading.py](#314-corebrushfadingpy)
  - [3.2 core/path_analyzer.py](#32-corepath_analyzerpy)
  - [3.3 core/gesture_executor.py](#33-coregesture_executorpy)
  - [3.4 core/system_monitor.py](#34-coresystem_monitorpy)
  - [3.5 core/logger.py](#35-coreloggerpy)
- [4. 应用程序集成](#4-应用程序集成)
  - [4.1 应用程序架构](#41-应用程序架构)
  - [4.2 程序流程](#42-程序流程)
  - [4.3 使用场景与示例](#43-使用场景与示例)
  - [4.4 扩展开发指南](#44-扩展开发指南)
- [5. 跨平台兼容性](#5-跨平台兼容性)
  - [5.1 多平台支持概述](#51-多平台支持概述)
  - [5.2 Windows平台适配](#52-windows平台适配)
  - [5.3 macOS平台适配](#53-macos平台适配)
  - [5.4 Linux平台适配](#54-linux平台适配)
- [6. 总结](#6-总结)

## 目录结构

```
src/
├── core/                    # 核心功能模块
│   ├── brush/               # 画笔绘制模块
│   │   ├── __init__.py      # 包初始化文件
│   │   ├── manager.py       # 绘制管理器
│   │   ├── overlay.py       # 绘制覆盖层
│   │   ├── drawing.py       # 画笔绘制逻辑
│   │   └── fading.py        # 淡出效果模块
│   ├── path_analyzer.py     # 路径分析模块
│   ├── gesture_executor.py  # 手势执行模块
│   ├── system_monitor.py    # 系统监测模块
│   └── logger.py            # 日志记录模块
├── ui/                      # 用户界面模块
│   ├── __init__.py          # 包初始化文件
│   ├── console.py           # 控制台选项卡
│   ├── settings/            # 设置模块
│   │   ├── settings_tab.py  # 设置主页面（包含三个子选项卡）
│   │   ├── application_settings_tab.py # 应用设置选项卡
│   │   ├── brush_settings_tab.py # 画笔设置选项卡
│   │   ├── recognizer_settings_tab.py # 判断器设置选项卡
│   │   ├── pen_preview_widget.py # 动态笔尖预览组件
│   │   ├── settings.py      # 设置管理器
│   │   └── default_settings.json # 默认设置配置文件
│   └── gestures/            # 手势管理模块
│       ├── gestures_tab.py  # 手势管理选项卡（主页面）
│       ├── trigger_paths_tab.py # 触发路径选项卡
│       ├── execute_actions_tab.py # 执行操作选项卡
│       ├── gesture_mappings_tab.py # 手势映射选项卡
│       ├── gestures.py      # 手势库管理模块
│       ├── drawing_widget.py # 手势绘制组件
│       └── default_gestures.json # 默认手势库定义（JSON格式）
├── assets/                  # 资源文件目录
│   └── images/              # 图像资源
│       ├── console.svg      # 控制台图标
│       ├── gestures.svg     # 手势管理图标
│       ├── settings.svg     # 设置图标
│       ├── icon.svg         # 应用程序图标
│       ├── brush.svg        # 画笔工具图标
│       ├── pointer.svg      # 指针工具图标
│       ├── undo.svg         # 撤销操作图标
│       ├── redo.svg         # 重做操作图标
│       ├── test.svg         # 测试功能图标
│       └── icons/           # 多尺寸应用图标
│           ├── icon.ico     # Windows图标文件
│           ├── icon.icns    # macOS图标文件
│           └── icon-*.png   # 各种尺寸的PNG图标
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
- `show_dialog(parent, message_type, title_text, message, ...)`：通用对话框显示函数，支持自定义按钮和回调
- `show_info(parent, message)`：显示信息对话框
- `show_warning(parent, message)`：显示警告对话框
- `show_error(parent, message)`：显示错误对话框
- `get_system_tray(parent)`：创建系统托盘图标和右键菜单
- `get_toast_manager()`：获取虚拟Toast管理器实例（当前为占位实现）

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
- `initUI(self)`：初始化用户界面，设置窗口属性、创建页面选项卡、堆栈布局和底部状态栏
- `switch_page(self, index)`：切换到指定索引的页面并更新按钮样式
- `_select_initial_page(self)`：选择初始页面（默认为控制台页面）
- `onPageChanged(self, index)`：处理页面切换事件，记录切换日志
- `resizeEvent(self, event)`：处理窗口尺寸变化事件
- `closeEvent(self, event)`：处理窗口X按钮关闭事件，始终忽略并调用内部退出逻辑
- `_show_exit_dialog(self)`：显示退出确认对话框，包含最小化到托盘、退出程序和取消选项
- `_handle_close_request(self, is_window_close)`：统一的关闭请求处理，根据设置决定显示对话框或执行默认行为
- `_prepare_for_close(self)`：退出前的准备工作，停止绘制和释放按键状态
- `_minimize_to_tray(self)`：将窗口最小化到系统托盘
- `_exit_application(self)`：退出应用程序的入口点
- `_exit_with_save_check(self)`：退出程序并检查未保存项目
- `_check_unsaved_and_exit(self)`：检查未保存的设置和手势库更改，显示保存确认对话框
- `_force_exit(self)`：强制退出程序，调用sys.exit(0)
- `_handle_save_changes_response(self, button_text)`：处理保存更改对话框的用户响应（是/否/取消）
- `show_global_dialog(self, ...)`：显示全局对话框，支持多种类型和自定义参数
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

#### 2.1 界面UI模块

##### 2.1.1 控制台选项卡 (ui/console.py)

**功能说明**：
控制台界面，应用程序的主要交互界面，提供启动/停止绘制功能，显示系统资源监控信息。

**主要类和方法**：
- `create_styled_progress_bar(color_theme="default")`：创建带样式的原生QProgressBar，支持不同颜色主题

- `ConsolePage`：控制台页面类，继承自QWidget
  - `drawing_state_changed`：绘制状态变化信号，参数为是否处于绘制状态
  - `__init__(self, parent=None)`：初始化控制台页面，设置系统监测器和UI
  - `_setup_ui(self)`：初始化UI组件和布局
  - `_create_system_info_card(self, title, value, color)`：创建系统信息卡片，使用QFrame实现
  - `update_system_info(self, data)`：更新系统信息显示，包括CPU、内存、运行时间和进程资源
  - `resizeEvent(self, event)`：处理窗口尺寸变化事件
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

##### 2.1.2 手势管理模块

###### 2.1.2.1 手势库 (ui/gestures/gestures.py)

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
    "path_1": {
      "id": 1,
      "name": "向右滑动",
      "path": {
        "points": [[0, 0], [100, 0]],
        "connections": [{"from": 0, "to": 1, "type": "line"}]
      }
    }
  },
  "execute_actions": {
    "action_1": {
      "id": 1,
      "name": "复制",
      "type": "shortcut",
      "value": "Ctrl+C"
    }
  },
  "gesture_mappings": {
    "gesture_1": {
      "id": 1,
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

###### 2.1.2.2 手势选项卡主页面 (ui/gestures/gestures_tab.py)

**功能说明**：
手势管理主页面，包含三个子选项卡的容器页面。提供统一的手势库操作界面，管理触发路径、执行操作和手势映射三个部分。

**主要类和方法**：
- `GesturesPage`：手势管理主页面类
  - `__init__(self, parent=None)`：初始化手势管理主页面，创建三个子选项卡
  - `initUI(self)`：初始化用户界面，创建选项卡控件和底部操作按钮
  - `_on_tab_changed(self, index)`：选项卡切换事件处理
  - `_check_library_changes(self)`：定时检查手势库是否有变更，自动更新保存和放弃按钮状态
  - `_save_gesture_library(self)`：保存手势库到文件
  - `_refresh_all(self)`：刷新所有子选项卡的显示
  - `_reset_to_default(self)`：重置手势库为默认设置
  - `_discard_changes(self)`：放弃所有未保存的修改

- `SimilarityTestDialog`：相似度测试对话框类
  - `__init__(self, reference_path, parent=None)`：初始化相似度测试对话框
  - `_init_ui(self)`：初始化测试界面
  - `_on_test_path_completed(self, path)`：处理测试路径绘制完成事件
  - `_setup_test_widget_events(self)`：设置测试绘制组件的事件处理
  - `_calculate_similarity(self)`：计算两个路径的相似度

**界面结构**：
- **选项卡容器**：包含三个子选项卡
  - 触发路径选项卡（`TriggerPathsTab`）
  - 执行操作选项卡（`ExecuteActionsTab`）
  - 手势映射选项卡（`GestureMappingsTab`）
- **底部操作区域**：
  - 重置为默认按钮（120x35px）
  - 放弃修改按钮（100x35px，有变更时自动启用）
  - 保存设置按钮（100x35px，有变更时自动启用）

**自动化功能**：
- **变更检测**：每秒自动检查手势库变更状态
- **按钮状态管理**：保存和放弃按钮根据变更状态自动启用/禁用
- **子选项卡刷新**：保存或重置后自动刷新所有子选项卡

**使用方法**：
```python
# 创建手势管理主页面
from ui.gestures.gestures_tab import GesturesPage

# 创建页面实例
gestures_page = GesturesPage()

# 访问子选项卡
trigger_paths_tab = gestures_page.trigger_paths_tab     # 触发路径选项卡
execute_actions_tab = gestures_page.execute_actions_tab # 执行操作选项卡
gesture_mappings_tab = gestures_page.gesture_mappings_tab # 手势映射选项卡

# 手动触发操作
gestures_page._save_gesture_library()    # 保存手势库
gestures_page._reset_to_default()        # 重置为默认
gestures_page._discard_changes()         # 放弃修改
gestures_page._refresh_all()             # 刷新所有选项卡

# 获取选项卡控件
tab_widget = gestures_page.tab_widget    # QTabWidget控件
current_index = tab_widget.currentIndex() # 当前选项卡索引
```

###### 2.1.2.3 触发路径选项卡 (ui/gestures/trigger_paths_tab.py)

**功能说明**：
触发路径管理选项卡，用于管理手势的触发路径数据。提供路径的添加、编辑、删除功能，以及可视化的路径绘制和相似度测试工具。

**主要类和方法**：
- `TriggerPathsTab`：触发路径管理选项卡类
  - `__init__(self, parent=None)`：初始化触发路径选项卡
  - `initUI(self)`：初始化用户界面，创建左右分栏布局
  - `_create_path_list_panel(self)`：创建左侧路径列表面板
  - `_create_path_editor_panel(self)`：创建右侧路径编辑器面板
  - `_load_path_list(self)`：加载并显示路径列表，按ID排序
  - `_on_path_selected(self, item)`：处理路径选择事件
  - `_load_path_to_editor(self, path_key)`：将路径数据加载到编辑器
  - `_on_form_changed(self)`：表单内容变化事件处理
  - `_auto_save_changes(self)`：自动保存变更到手势库变量中
  - `_has_form_changes(self)`：检查表单是否有未保存的更改
  - `_paths_different(self, path1, path2)`：比较两个路径是否不同
  - `_on_path_completed(self, path)`：处理路径绘制完成事件
  - `_on_path_updated(self)`：处理路径更新事件（撤销/重做等操作）
  - `_create_new_path_from_drawing(self)`：从绘制区域创建新路径
  - `_add_new_path(self)`：添加新路径
  - `_clear_form(self)`：清空表单
  - `_select_path_in_list(self, path_key)`：在列表中选择指定路径
  - `_delete_path(self)`：删除选中的路径
  - `has_unsaved_changes(self)`：检查是否有未保存的更改
  - `refresh_list(self)`：刷新路径列表显示
  - `_on_test_similarity(self)`：触发相似度测试
  - `_show_similarity_results(self, test_path, results)`：显示相似度测试结果

**界面布局**：
- **左侧路径列表面板**：
  - 路径列表（显示ID、名称、点数）
  - 添加路径按钮
  - 删除路径按钮（选中路径时启用）
- **右侧路径编辑器面板**：
  - 路径名称输入框
  - 手势绘制组件（支持绘制、显示、测试相似度）
  - 清空按钮

**核心功能**：
- **路径绘制**：使用绘制组件绘制手势路径
- **自动保存**：表单修改自动保存到手势库变量
- **相似度测试**：测试绘制路径与参考路径的相似度
- **列表同步**：编辑后自动刷新列表显示

**使用方法**：
```python
# 创建触发路径选项卡
from ui.gestures.trigger_paths_tab import TriggerPathsTab

# 创建选项卡实例
paths_tab = TriggerPathsTab()

# 访问组件
path_list = paths_tab.path_list              # 路径列表控件
name_input = paths_tab.edit_name             # 路径名称输入框
drawing_widget = paths_tab.drawing_widget    # 绘制组件

# 手动操作
paths_tab._add_new_path()        # 添加新路径
paths_tab._delete_path()         # 删除当前选中路径
paths_tab._clear_form()          # 清空表单
paths_tab.refresh_list()         # 刷新列表

# 检查变更状态
has_changes = paths_tab.has_unsaved_changes()

# 访问当前路径数据
current_path_key = paths_tab.current_path_key
current_path = paths_tab.current_path
```

###### 2.1.2.4 执行操作选项卡 (ui/gestures/execute_actions_tab.py)

**功能说明**：
执行操作管理选项卡，用于管理手势要执行的操作。支持快捷键操作的定义、编辑和删除。

**主要类和方法**：
- `ExecuteActionsTab`：执行操作管理选项卡类
  - `__init__(self, parent=None)`：初始化执行操作选项卡
  - `initUI(self)`：初始化用户界面，创建左右分栏布局
  - `_create_action_list_panel(self)`：创建左侧操作列表面板
  - `_create_action_editor_panel(self)`：创建右侧操作编辑器面板
  - `_load_action_list(self)`：加载并显示操作列表，按ID排序
  - `_on_action_selected(self, item)`：处理操作选择事件
  - `_load_action_to_editor(self, action_key)`：将操作数据加载到编辑器
  - `_on_form_changed(self)`：表单内容变化事件处理
  - `_auto_save_changes(self)`：自动保存变更到手势库变量中
  - `_has_form_changes(self)`：检查表单是否有未保存的更改
  - `_clear_form(self)`：清空表单
  - `_add_new_action(self)`：添加新操作
  - `_select_action_in_list(self, action_key)`：在列表中选择指定操作
  - `_delete_action(self)`：删除选中的操作
  - `has_unsaved_changes(self)`：检查是否有未保存的更改
  - `refresh_list(self)`：刷新操作列表显示

**界面布局**：
- **左侧操作列表面板**：
  - 操作列表（显示ID、名称、类型、值）
  - 添加操作按钮
  - 删除操作按钮（选中操作时启用）
- **右侧操作编辑器面板**：
  - 操作名称输入框
  - 操作类型下拉框（当前支持"快捷键"）
  - 操作值输入框（如"Ctrl+C"）
  - 清空按钮

**支持的操作类型**：
- **快捷键（shortcut）**：执行键盘快捷键组合

**使用方法**：
```python
# 创建执行操作选项卡
from ui.gestures.execute_actions_tab import ExecuteActionsTab

# 创建选项卡实例
actions_tab = ExecuteActionsTab()

# 访问组件
action_list = actions_tab.action_list        # 操作列表控件
name_input = actions_tab.edit_name           # 操作名称输入框
type_combo = actions_tab.combo_type          # 操作类型下拉框
value_input = actions_tab.edit_value         # 操作值输入框

# 手动操作
actions_tab._add_new_action()        # 添加新操作
actions_tab._delete_action()         # 删除当前选中操作
actions_tab._clear_form()            # 清空表单
actions_tab.refresh_list()           # 刷新列表

# 检查变更状态
has_changes = actions_tab.has_unsaved_changes()

# 访问当前操作数据
current_action_key = actions_tab.current_action_key
```

###### 2.1.2.5 手势映射选项卡 (ui/gestures/gesture_mappings_tab.py)

**功能说明**：
手势映射管理选项卡，提供可视化的手势映射创建和管理界面。使用卡片式布局显示执行操作和触发路径，通过连线的方式直观地展示映射关系。支持点击连接、可视化删除和状态显示等功能。

**主要类和方法**：

**核心组件类**：
- `ConnectionWidget`：连线绘制组件，处理映射关系的可视化连线
  - `add_connection(action_id, path_id, start_point, end_point)`：添加连线
  - `remove_connection(path_id)`：移除指定路径的连线
  - `clear_connections()`：清空所有连线
  - `mousePressEvent(event)`：鼠标点击选择连线
  - `keyPressEvent(event)`：键盘删除选中连线（Delete键）
  - `paintEvent(event)`：绘制所有连线和箭头

- `ActionCardWidget`：执行操作卡片组件
  - `action_clicked = Signal(int, QPoint)`：操作卡片点击信号
  - `set_selected(is_selected)`：设置选中状态
  - `set_mapped_count(count)`：更新已映射的路径数量显示

- `PathCardWidget`：触发路径卡片组件
  - `path_clicked = Signal(int, QPoint)`：路径卡片点击信号
  - `set_mapped(is_mapped, action_name)`：设置映射状态和关联操作名

- `ActionCardsWidget` / `PathCardsWidget`：卡片容器组件
  - 管理多个卡片的布局和操作
  - 支持动态添加、删除和刷新卡片

**主要管理类**：
- `GestureMappingsTab`：手势映射管理选项卡主类
  - `initUI()`：初始化三面板布局界面
  - `_create_actions_panel()`：创建左侧执行操作面板
  - `_create_paths_panel()`：创建右侧触发路径面板
  - `_load_data()`：加载所有数据（操作、路径、映射）
  - `_load_actions()`：加载执行操作卡片
  - `_load_paths()`：加载触发路径卡片
  - `_load_existing_mappings()`：加载现有映射关系
  - `_on_action_clicked(action_id, global_pos)`：处理操作卡片点击
  - `_on_path_clicked(path_id, global_pos)`：处理路径卡片点击
  - `_create_mapping(action_id, path_id)`：创建新的映射关系
  - `_delete_mapping_by_path_id(path_id)`：根据路径ID删除映射
  - `_update_connections()`：更新连线可视化
  - `_clear_all_mappings()`：清除所有映射关系
  - `refresh_list()`：刷新整个界面数据

**界面布局**：
- **左侧执行操作面板**：
  - 执行操作卡片网格布局
  - 每个卡片显示操作名称、内容和状态
  - 支持悬停高亮和点击选择
  - 显示已映射的路径数量

- **中间连线可视化区域**：
  - 动态绘制操作与路径之间的连线
  - 支持连线选择（点击高亮）
  - 支持键盘删除选中连线（Delete键）
  - 箭头指示连接方向

- **右侧触发路径面板**：
  - 触发路径卡片网格布局
  - 每个卡片显示路径名称和方向信息
  - 映射状态可视化显示（已连接/未连接）
  - 显示关联的操作名称

**可视化特性**：
- **卡片式设计**：直观的操作和路径展示
- **连线动画**：实时可视化映射关系
- **状态指示**：清晰的连接状态显示
- **交互式操作**：点击创建、删除连接
- **颜色编码**：不同状态使用不同颜色区分

**操作流程**：
1. **创建映射**：先点击左侧操作卡片，再点击右侧路径卡片
2. **删除映射**：点击选中连线，按Delete键删除
3. **查看状态**：卡片颜色和文字显示当前连接状态
4. **批量操作**：支持清除所有映射功能

**使用方法**：
```python
# 创建手势映射选项卡
from ui.gestures.gesture_mappings_tab import GestureMappingsTab

# 创建选项卡实例
mappings_tab = GestureMappingsTab()

# 访问主要组件
actions_widget = mappings_tab.actions_widget      # 左侧操作卡片容器
paths_widget = mappings_tab.paths_widget          # 右侧路径卡片容器
connection_widget = mappings_tab.connection_widget # 中间连线组件

# 操作方法
mappings_tab._load_data()                          # 重新加载所有数据
mappings_tab._create_mapping(action_id, path_id)   # 创建映射关系
mappings_tab._delete_mapping_by_path_id(path_id)   # 删除指定映射
mappings_tab._clear_all_mappings()                 # 清除所有映射
mappings_tab.refresh_list()                        # 刷新界面显示

# 获取信息
action_name = mappings_tab._get_action_name_by_id(action_id)  # 获取操作名
path_name = mappings_tab._get_path_name_by_id(path_id)        # 获取路径名

# 组件操作
action_card = actions_widget.get_action_card(action_id)       # 获取操作卡片
path_card = paths_widget.get_path_card(path_id)               # 获取路径卡片
```

###### 2.1.2.6 手势绘制组件 (ui/gestures/drawing_widget.py)

**功能说明**：
手势绘制组件，提供可视化的手势路径绘制和编辑功能。支持多种绘制工具、历史记录、视图变换和路径测试等功能。集成在触发路径选项卡中，为用户提供直观的手势路径创建和编辑体验。

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
- `_apply_angle_snap(self, path_index, point_index, new_pos, use_left_shift)`：应用角度吸附功能
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

**角度吸附功能**：
- 左Shift+拖拽点：启用45度角度吸附（0°、45°、90°、135°等）
- 右Shift+拖拽点：启用任意角度吸附到最近连线
- 吸附时显示虚线指示参考线

**键盘快捷键**：
- `Ctrl+Z`：撤回上一步操作
- `Ctrl+Y`：还原被撤回的操作
- `Space`：临时启用平移模式
- `Delete`：删除选中的点（点击工具模式）
- `Left Shift`：启用45度角度吸附
- `Right Shift`：启用自由角度吸附

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

###### 2.1.2.6 手势绘制组件 (ui/gestures/drawing_widget.py)

**功能说明**：
手势绘制组件，提供可视化的手势路径绘制和编辑功能。支持多种绘制工具、历史记录、视图变换和路径测试等功能。

**主要类和信号**：
- `GestureDrawingWidget`：手势绘制组件类
  - `pathCompleted = Signal(dict)`：路径完成信号，发送格式化的路径数据
  - `testSimilarity = Signal()`：测试相似度信号

**主要方法**：
- **初始化和UI**：
  - `__init__(self, parent=None)`：初始化绘制组件
  - `initUI(self)`：初始化用户界面，创建工具栏和绘制区域
  - `create_toolbar(self)`：创建左侧工具栏

- **工具管理**：
  - `load_svg_icon(self, filename)`：加载SVG图标
  - `select_brush_tool(self)`：选择画笔工具
  - `select_pointer_tool(self)`：选择点击工具
  - `update_toolbar_buttons(self)`：更新工具栏按钮状态

- **历史记录**：
  - `undo_action(self)`：撤回操作（Ctrl+Z）
  - `redo_action(self)`：还原操作（Ctrl+Y）
  - `save_to_history(self)`：保存当前状态到历史记录

- **事件处理**：
  - `keyPressEvent(self, event)`：键盘按下事件（支持Ctrl+Z/Y、Space等）
  - `keyReleaseEvent(self, event)`：键盘释放事件
  - `wheelEvent(self, event)`：滚轮事件（缩放和平移）
  - `mousePressEvent(self, event)`：鼠标按下事件
  - `mouseMoveEvent(self, event)`：鼠标移动事件
  - `mouseReleaseEvent(self, event)`：鼠标释放事件

- **视图变换**：
  - `_screen_to_view(self, screen_pos)`：屏幕坐标转视图坐标
  - `_reset_view(self)`：重置视图变换

- **点操作（点击工具）**：
  - `_handle_pointer_click(self, screen_pos)`：处理点击工具的点击
  - `_find_point_at_position(self, screen_pos, tolerance=15)`：查找指定位置的点
  - `_add_new_point(self, screen_pos)`：添加新点
  - `_update_dragging_point(self, screen_pos)`：更新拖拽的点
  - `_apply_angle_snap(self, path_index, point_index, new_pos, use_left_shift)`：应用角度吸附
  - `_delete_selected_point(self)`：删除选中的点

- **绘制和显示**：
  - `paintEvent(self, event)`：绘制事件，渲染所有路径和UI元素
  - `_get_point_position(self, point)`：获取点的位置
  - `_draw_formatted_path(self, painter, path)`：绘制格式化路径
  - `_draw_direction_arrow(self, painter, start_point, end_point)`：绘制方向箭头

- **路径管理**：
  - `clear_drawing(self)`：清空绘制内容
  - `load_path(self, path)`：加载路径到绘制区域
  - `test_similarity(self)`：发送测试相似度信号

**工具栏功能**：
- **画笔工具**：绘制连续路径
- **点击工具**：添加和编辑单个点
- **撤回/还原**：支持历史记录操作
- **测试相似度**：测试当前路径的相似度

**交互功能**：
- **绘制模式**：
  - 左键拖拽：绘制连续路径（画笔工具）
  - 左键点击：添加单个点（点击工具）
  - 右键点击：删除选中点（点击工具）
  - 双击：完成路径绘制

- **视图操作**：
  - 滚轮：缩放视图
  - Space+拖拽：平移视图
  - Shift+滚轮：水平滚动

- **角度吸附**：
  - 左Shift+拖拽：45度角度吸附
  - 右Shift+拖拽：自由角度吸附

**键盘快捷键**：
- `Ctrl+Z`：撤回
- `Ctrl+Y`：还原
- `Space`：启用平移模式
- `Delete`：删除选中点
- `Left Shift`：45度角度吸附
- `Right Shift`：自由角度吸附

**使用方法**：
```python
# 创建绘制组件
from ui.gestures.drawing_widget import GestureDrawingWidget

# 创建组件实例
drawing_widget = GestureDrawingWidget()

# 连接信号
drawing_widget.pathCompleted.connect(on_path_completed)      # 路径完成处理
drawing_widget.testSimilarity.connect(on_test_similarity)   # 相似度测试处理

def on_path_completed(path):
    """处理路径完成事件"""
    print(f"路径完成: {len(path['points'])}个点")
    print(f"连接数: {len(path['connections'])}")

def on_test_similarity():
    """处理测试相似度请求"""
    print("用户请求测试相似度")

# 设置工具模式
drawing_widget.current_tool = "brush"     # 画笔工具
drawing_widget.current_tool = "pointer"   # 点击工具

# 加载路径
path_data = {
    "points": [[10, 10], [50, 50], [90, 10]],
    "connections": [
        {"from": 0, "to": 1, "type": "line"},
        {"from": 1, "to": 2, "type": "line"}
    ]
}
drawing_widget.load_path(path_data)

# 清空绘制
drawing_widget.clear_drawing()

# 手动操作
drawing_widget.undo_action()              # 撤回
drawing_widget.redo_action()              # 还原
drawing_widget.test_similarity()          # 测试相似度

# 访问状态
current_tool = drawing_widget.current_tool           # 当前工具
is_drawing = drawing_widget.drawing                  # 是否正在绘制
completed_paths = drawing_widget.completed_paths     # 已完成的路径
view_scale = drawing_widget.view_scale               # 当前缩放比例
```

##### 2.1.3 设置模块

###### 2.1.3.1 设置管理器 (ui/settings/settings.py)

**功能说明**：
设置管理模块，负责保存和加载用户设置，提供设置的持久化和访问机制。

**主要类和方法**：
- `Settings`：设置管理器类
  - `__init__(self)`：初始化设置管理器
  - `_load_default_settings(self)`：加载默认设置
  - `_get_settings_file_path(self)`：获取设置文件路径
  - `load(self)`：从文件加载设置
  - `save(self)`：保存设置到文件
  - `get(self, key, default=None)`：获取设置项
  - `set(self, key, value)`：设置设置项
  - `reset_to_default(self)`：重置为默认设置
  - `has_changes(self)`：检查是否有未保存的更改
  - `get_app_path(self)`：获取应用程序可执行文件路径
  - `is_autostart_enabled(self)`：检查应用程序是否设置为开机自启动，支持Windows、macOS和Linux系统
  - `set_autostart(self, enable)`：设置开机自启动状态，在不同系统上使用不同的实现方式：
    - Windows：通过注册表实现，自动添加`--silent`参数
    - macOS：通过LaunchAgents的plist文件实现，自动添加`--silent`参数
    - Linux：通过~/.config/autostart目录下的.desktop文件实现，自动添加`--silent`参数
  - `get_app_path_with_silent(self)`：获取带有静默启动参数的应用程序路径，专用于开机自启设置

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

###### 2.1.3.2 设置主页面 (ui/settings/settings_tab.py)

**功能说明**：
设置主页面，提供选项卡式布局，包含应用设置、画笔设置、判断器设置三个子选项卡。采用模块化设计，每个选项卡独立管理自己的设置项。

**主要类和方法**：
- `SettingsPage`：设置主页面类，继承自QWidget
  - `__init__(self, parent=None)`：初始化设置主页面，创建三个子选项卡
  - `_init_ui(self)`：初始化用户界面，创建选项卡控件和底部操作按钮
  - `_on_tab_changed(self, index)`：选项卡切换事件处理
  - `_check_settings_changes(self)`：定时检查设置是否有变更，自动更新保存和放弃按钮状态
  - `has_unsaved_changes(self)`：检查是否有未保存的更改，综合检查所有子选项卡的状态
  - `_save_settings(self)`：保存设置到文件，调用所有子选项卡的apply_settings方法
  - `_reset_settings(self)`：重置设置为默认值
  - `_discard_changes(self)`：放弃所有未保存的修改
  - `_reload_all(self)`：重新加载所有子选项卡
  - `_mark_changed(self)`：标记设置已更改（由子选项卡调用）

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

###### 2.1.3.3 应用设置选项卡 (ui/settings/application_settings_tab.py)

**功能说明**：
应用设置选项卡，处理开机自启动、退出行为等应用程序全局设置。

**主要类和方法**：
- `ApplicationSettingsTab`：应用设置选项卡类，继承自QWidget
  - `__init__(self, parent=None)`：初始化应用设置选项卡
  - `_init_ui(self)`：初始化用户界面
  - `_create_app_settings_group(self)`：创建应用设置组
  - `_load_settings(self)`：加载设置
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

###### 2.1.3.4 画笔设置选项卡 (ui/settings/brush_settings_tab.py)

**功能说明**：
画笔设置选项卡，处理笔尖粗细、颜色、画笔类型等绘制相关设置，包含动态预览功能。

**主要类和方法**：
- `BrushSettingsTab`：画笔设置选项卡类，继承自QWidget
  - `__init__(self, parent=None)`：初始化画笔设置选项卡
  - `_init_ui(self)`：初始化用户界面
  - `_create_brush_settings_group(self)`：创建画笔设置组
  - `_load_settings(self)`：加载设置
  - `has_unsaved_changes(self)`：检查是否有未保存的更改
  - `apply_settings(self)`：应用设置
  - `_apply_pen_settings_to_drawing_module(self, width, color)`：实时应用画笔设置到绘制模块

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

###### 2.1.3.5 判断器设置选项卡 (ui/settings/recognizer_settings_tab.py)

**功能说明**：
判断器设置选项卡，处理手势识别相似度阈值等识别相关设置。

**主要类和方法**：
- `RecognizerSettingsTab`：判断器设置选项卡类，继承自QWidget
  - `__init__(self, parent=None)`：初始化判断器设置选项卡
  - `_init_ui(self)`：初始化用户界面
  - `_create_recognizer_settings_group(self)`：创建判断器设置组
  - `_load_settings(self)`：加载设置
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

###### 2.1.3.6 动态预览组件 (ui/settings/pen_preview_widget.py)

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
- `create_brush(self, width, color)`：创建当前类型的画笔实例
- `get_current_brush_type(self)`：获取当前画笔类型
- 支持的画笔类型：
  - `"pencil"`：铅笔，传统绘制效果
  - `"water"`：水性笔，动态变粗效果
  - `"calligraphy"`：毛笔，书法墨色效果

##### 3.1.4 core/brush/fading.py

**主要类和方法**：
- `FadingModule`：淡出效果管理器
  - `__init__(self, parent_widget)`：初始化淡出模块
  - `start_fade(self)`：开始淡出动画
  - `stop_fade(self)`：停止淡出动画
  - `get_fade_alpha(self)`：获取当前透明度值 (0-255)

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
- `format_raw_path(self, raw_points: List[Tuple]) -> Dict`：将原始绘制点转换为格式化路径，流程包括缩放、简化、提取关键点、生成连接
- `calculate_similarity(self, path1: Dict, path2: Dict) -> float`：计算两个路径的相似度，结果范围[0,1]，综合考虑形状轮廓和笔画顺序
- `normalize_path_scale(self, path: Dict, target_size: int = 100) -> Dict`：将路径归一化到指定尺寸，保持宽高比
- `_scale_small_path(self, coords: List[Tuple]) -> List[Tuple]`：对尺寸过小的路径进行等比放大，提高处理精度
- `_extract_key_points(self, coords: List[Tuple]) -> List[Tuple]`：从坐标点中提取关键点，保留路径核心特征
- `_douglas_peucker(self, points: List[Tuple], tolerance: float) -> List[Tuple]`：使用道格拉斯-普克算法简化路径
- `_analyze_direction_changes(self, points: List[Tuple]) -> List[Tuple]`：通过分析角度和距离变化识别重要转折点
- `_preprocess_for_comparison(self, path: Dict, target_size: int, resample_n: int) -> np.ndarray`：为相似度计算准备路径，归一化和重采样
- `_resample_points(self, pts: np.ndarray, target_n: int) -> np.ndarray`：沿曲线总长度等距采样指定数量的点
- `_compute_scores(self, pts1: np.ndarray, pts2: np.ndarray) -> Tuple[float, float]`：计算形状和方向得分
- `_procrustes_align(self, A: np.ndarray, B: np.ndarray) -> np.ndarray`：使用Procrustes分析对齐两个点集
- `_get_path_bbox(self, points: List[Tuple]) -> Dict`：计算路径边界框
- `_calculate_path_length(self, points: List[Tuple]) -> float`：计算路径总长度
- `_calculate_angle_change(self, p1: Tuple, p2: Tuple, p3: Tuple) -> float`：计算三点夹角变化
- `_distance_to_line(self, p1: Tuple, p2: Tuple, point: Tuple) -> float`：计算点到线段的距离

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
  - `__init__(self)`：初始化手势执行器，设置键盘控制器和特殊键映射
  - `execute_gesture_by_path(self, drawn_path)`：根据绘制路径执行对应的手势动作，核心执行入口
  - `_execute_shortcut(self, shortcut_str)`：执行快捷键操作，支持多种快捷键格式
  - `_press_keys(self, modifier_keys, regular_keys)`：按下并释放快捷键组合
  - `release_all_keys(self)`：释放所有可能按下的键，用于程序退出前的清理
  - `refresh_gestures(self)`：刷新手势库，确保使用最新的已保存手势库
  - `find_similar_paths(self, test_path)`：查找与测试路径相似的所有触发路径，返回相似度排序结果

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

# 查找相似路径
similar_paths = executor.find_similar_paths(test_path)
for path_key, similarity, path_data in similar_paths:
    print(f"路径: {path_data['name']}, 相似度: {similarity:.3f}")

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

#### 3.5 core/logger.py

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