# GestroKey 源代码目录说明

GestroKey是一款手势控制工具，允许用户通过鼠标绘制手势来执行各种操作（如快捷键、启动程序等）。本工具的核心特性包括全局鼠标手势识别、方向分析、手势库管理以及自定义UI组件，适用于日常办公、创意设计和编程开发等场景。

## 主要功能特性

- **全局手势识别**：支持在任何应用程序中绘制手势
- **智能路径分析**：精确的手势方向识别和相似度匹配
- **可视化手势编辑**：直观的手势绘制和编辑界面
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
      - [2.1.3.2 设置选项卡](#2132-设置选项卡-uisettingssettings_tabpy)
- [3. 核心功能模块](#3-核心功能模块)
  - [3.1 core/drawer.py](#31-coredrawerpy)
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
│   ├── drawer.py            # 绘画核心模块
│   ├── path_analyzer.py     # 路径分析模块
│   ├── gesture_executor.py  # 手势执行模块
│   ├── system_monitor.py    # 系统监测模块
│   └── logger.py            # 日志记录模块
├── ui/                      # 用户界面模块
│   ├── console.py           # 控制台选项卡
│   ├── __init__.py          # UI模块初始化文件
│   ├── settings/            # 设置模块
│   │   ├── settings_tab.py  # 设置选项卡
│   │   ├── settings.py      # 设置管理器
│   │   └── __init__.py      # 设置模块初始化文件
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
│       ├── icon.svg         # 应用程序图标
│       └── settings.svg     # 设置图标
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
- `__init__(self)`：初始化应用程序主窗口，设置日志记录器、全局资源、UI界面和系统托盘
- `init_global_resources(self)`：初始化设置管理器和手势库管理器等全局资源
- `init_system_tray(self)`：初始化系统托盘图标
- `toggle_drawing(self)`：切换绘制状态（启动/停止手势监听）
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
- `_exit_application(self)`：强制退出应用程序的入口点
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
- `LICENSE`：许可证信息，如"GPL-3.0"
- `REPO_URL`：仓库地址，基于作者和应用名称自动生成
- `VERSION_TYPE_RELEASE`：正式发布版本的类型标识
- `VERSION_TYPE_PREVIEW`：预览版本的类型标识
- `VERSION_TYPE_DEVELOPMENT`：未发布版本的类型标识
- `CURRENT_VERSION_TYPE`：当前版本的类型，可设置为上述三种类型之一

**Qt API 配置**：
- `QT_API`：指定使用的 Qt API，支持以下值：
  - `"pyqt6"`：使用 PyQt6（默认）
  - `"pyqt5"`：使用 PyQt5
  - `"pyside6"`：使用 PySide6
  - `"pyside2"`：使用 PySide2

**打包配置变量**：
- `ENABLE_PACKAGING`：是否启用打包流程
- `PACKAGE_WINDOWS`、`PACKAGE_MACOS`、`PACKAGE_LINUX`：各平台是否启用打包
- `PACKAGE_STANDALONE`、`PACKAGE_PORTABLE`：打包类型控制
- `PACKAGER_WINDOWS`、`PACKAGER_MACOS`、`PACKAGER_LINUX`：各平台打包工具选择（nuitka或pyinstaller）
- `PACKAGE_INCLUDE_DEBUG_SYMBOLS`：是否包含调试符号
- `PACKAGE_OPTIMIZE_LEVEL`：优化级别（0-2）
- `PACKAGE_COMPRESS_ASSETS`：是否压缩资源文件
- `PACKAGE_UPXIFY`：是否使用UPX压缩可执行文件
- `PACKAGE_OUTPUT_DIR`：输出目录名称
- `PACKAGE_NAMING_PATTERN`：命名模式，支持占位符{app_name}、{version}、{platform}、{type}

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
- `AnimatedProgressBar`：动画进度条类（自定义组件）
  - `__init__(self, parent=None)`：初始化动画进度条
  - `_update_style(self, value)`：根据值更新进度条样式和颜色
  - `set_animated_value(self, value)`：设置进度条值，带动画效果
  - `set_color_theme(self, base_color, mid_color, high_color)`：设置进度条的颜色主题

- `ConsolePage`：控制台页面类
  - `__init__(self, parent=None)`：初始化控制台页面
  - `_setup_ui(self)`：初始化UI组件和布局
  - `_create_system_info_card(self, title, value, color)`：创建系统信息卡片
  - `toggle_drawing(self)`：切换绘制状态
  - `start_drawing(self)`：开始绘制功能
  - `stop_drawing(self)`：停止绘制功能
  - `update_system_info(self, data)`：更新系统信息显示

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
  - `__init__(self)`：初始化手势库，加载默认手势和用户配置
  - `_load_default_gestures(self)`：从JSON文件加载默认手势库
  - `_convert_actions_for_current_platform(self)`：转换操作的快捷键格式为当前平台格式
  - `_convert_shortcut_for_current_platform(self, shortcut)`：将快捷键转换为当前平台的格式
  - `_get_gestures_file_path(self)`：获取手势库文件路径，支持多平台
  - `load(self)`：从文件加载手势库
  - `_convert_loaded_actions_for_current_platform(self, loaded_data)`：转换加载的操作快捷键格式
  - `_update_saved_state(self)`：更新已保存状态（深拷贝）
  - `save(self)`：保存手势库到文件
  - `has_changes(self)`：检查是否有未保存的更改
  - `get_gesture_by_path(self, drawn_path, similarity_threshold=0.70)`：根据绘制路径获取匹配的手势
  - `get_gesture_count(self, use_saved=False)`：获取手势数量
  - `_get_next_mapping_id(self)`：获取下一个可用的映射ID
  - `_get_next_path_id(self)`：获取下一个可用的路径ID
  - `_get_next_action_id(self)`：获取下一个可用的操作ID
  - `reset_to_default(self)`：重置手势库为默认设置

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
  - `_check_library_changes(self)`：定时检查手势库是否有变更，自动更新保存按钮状态
  - `_save_gesture_library(self)`：保存手势库到文件
  - `_refresh_all(self)`：刷新所有子选项卡的显示
  - `_reset_to_default(self)`：重置手势库为默认设置

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
  - 提示标签："修改后需要保存手势库才能生效"
  - 保存手势库按钮（有变更时自动启用）
  - 重置为默认手势库按钮

**自动化功能**：
- **变更检测**：每秒自动检查手势库变更状态
- **按钮状态管理**：保存按钮根据变更状态自动启用/禁用
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
手势映射管理选项卡，用于将触发路径和执行操作关联起来，形成完整的手势定义。提供映射关系的创建、编辑和删除功能。

**主要类和方法**：
- `GestureMappingsTab`：手势映射管理选项卡类
  - `__init__(self, parent=None)`：初始化手势映射选项卡
  - `initUI(self)`：初始化用户界面，创建左右分栏布局
  - `_create_mapping_list_panel(self)`：创建左侧映射列表面板
  - `_create_mapping_editor_panel(self)`：创建右侧映射编辑器面板
  - `_load_mapping_list(self)`：加载并显示映射列表，按ID排序
  - `_load_combo_options(self)`：加载下拉框选项
  - `_get_path_name_by_id(self, path_id)`：根据ID获取路径名称
  - `_get_action_name_by_id(self, action_id)`：根据ID获取操作名称
  - `_on_mapping_selected(self, item)`：处理映射选择事件
  - `_load_mapping_to_editor(self, mapping_key)`：将映射数据加载到编辑器
  - `_on_form_changed(self)`：表单内容变化事件处理
  - `_auto_save_changes(self)`：自动保存变更到手势库变量中
  - `_update_button_states(self)`：更新按钮启用状态
  - `_add_new_mapping(self)`：添加新映射
  - `_select_mapping_in_list(self, mapping_key)`：在列表中选择指定映射
  - `_delete_mapping(self)`：删除选中的映射
  - `_clear_form(self)`：清空表单
  - `has_unsaved_changes(self)`：检查是否有未保存的更改
  - `refresh_list(self)`：刷新映射列表显示

**界面布局**：
- **左侧映射列表面板**：
  - 映射列表（显示ID、手势名称、路径→操作）
  - 添加映射按钮
  - 删除映射按钮（选中映射时启用）
- **右侧映射编辑器面板**：
  - 手势名称输入框
  - 触发路径下拉框（显示可用路径）
  - 执行操作下拉框（显示可用操作）
  - 清空按钮

**核心功能**：
- **关联管理**：将触发路径和执行操作关联成完整手势
- **下拉框同步**：自动加载并显示可用的路径和操作
- **名称解析**：根据ID自动解析并显示路径和操作名称
- **完整性检查**：确保映射引用的路径和操作存在

**使用方法**：
```python
# 创建手势映射选项卡
from ui.gestures.gesture_mappings_tab import GestureMappingsTab

# 创建选项卡实例
mappings_tab = GestureMappingsTab()

# 访问组件
mapping_list = mappings_tab.mapping_list              # 映射列表控件
name_input = mappings_tab.edit_name                   # 手势名称输入框
path_combo = mappings_tab.combo_trigger_path          # 触发路径下拉框
action_combo = mappings_tab.combo_execute_action      # 执行操作下拉框

# 手动操作
mappings_tab._add_new_mapping()      # 添加新映射
mappings_tab._delete_mapping()       # 删除当前选中映射
mappings_tab._clear_form()           # 清空表单
mappings_tab.refresh_list()          # 刷新列表

# 检查变更状态
has_changes = mappings_tab.has_unsaved_changes()

# 访问当前映射数据
current_mapping_key = mappings_tab.current_mapping_key

# 获取名称解析方法
path_name = mappings_tab._get_path_name_by_id(1)      # 根据ID获取路径名
action_name = mappings_tab._get_action_name_by_id(1)  # 根据ID获取操作名
```

###### 2.1.2.6 手势绘制组件 (ui/gestures/drawing_widget.py)

**功能说明**：
手势绘制组件，提供可视化的手势路径绘制和编辑功能。支持多种绘制工具、历史记录、视图变换和路径测试等功能。集成在触发路径选项卡中，为用户提供直观的手势路径创建和编辑体验。

**主要类和信号**：
- `GestureDrawingWidget`：手势绘制组件类
  - `pathCompleted = Signal(dict)`：路径完成信号，发送格式化的路径数据
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

###### 2.1.3.2 设置选项卡 (ui/settings/settings_tab.py)

**功能说明**：
设置界面，允许用户自定义笔迹样式和应用行为，提供直观的设置选项。

**主要类和方法**：
- `PenPreviewWidget`：笔迹预览组件类
  - `__init__(self, width=3, color=[0, 120, 255], parent=None)`：初始化预览组件
  - `update_width(self, width)`：设置笔迹宽度
  - `update_color(self, color)`：设置笔迹颜色
  - `paintEvent(self, event)`：绘制预览效果

- `SettingsPage`：设置页面类
  - `__init__(self, parent=None)`：初始化设置页面
  - `initUI(self)`：初始化UI组件和布局
  - `create_brush_settings_page(self)`：创建画笔设置页面
  - `create_app_settings_page(self)`：创建应用设置页面
  - `apply_autostart_settings(self)`：应用开机自启动设置
  - `color_changed(self, color)`：处理颜色变化
  - `pen_width_changed(self, value)`：处理笔尖粗细变化
  - `pen_width_spinner_sync(self, value)`：同步数字选择器的值
  - `reset_settings(self)`：重置设置为默认值
  - `save_settings(self)`：保存设置
  - `_update_drawing_manager(self)`：更新绘制管理器的参数
  - `has_unsaved_changes(self)`：检查是否有未保存的更改
  - `update_ui_from_settings(self)`：从设置更新UI组件状态

**组件布局**：
- 顶部：设置标题
- 中部：滚动区域，包含以下设置组：
  - 画笔设置组：
    - 笔尖粗细设置（QSlider和QSpinBox）
    - 笔尖颜色选择（QPushButton和颜色预览）
    - 绘制时强制置顶（QCheckBox）：开启后在绘制过程中重复执行置顶命令，确保绘画窗口始终保持在最前面
    - 笔尖预览组件
  - 应用设置组：
    - 开机自启动选项（QCheckBox）：启用后将以静默模式自动启动并开始监听
    - 退出行为设置（QCheckBox和QRadioButton）
    - 手势相似度阈值设置（QDoubleSpinBox）
- 底部：操作按钮区域
  - 重置设置按钮
  - 保存设置按钮

**使用方法**：
```python
# 创建设置页面
from ui.settings.settings_tab import SettingsPage

# 创建页面实例
settings_page = SettingsPage()

# 页面会自动从设置管理器加载当前设置

# 访问设置组件
thickness_slider = settings_page.thickness_slider    # QSlider组件
thickness_spinbox = settings_page.thickness_spinbox  # QSpinBox组件
color_button = settings_page.color_button           # QPushButton组件
autostart_checkbox = settings_page.autostart_checkbox # QCheckBox组件

# 手动触发设置操作
settings_page._apply_settings()   # 应用设置
settings_page._save_settings()    # 保存设置
settings_page._reset_settings()   # 重置为默认设置

# 检查未保存更改
has_changes = settings_page.has_unsaved_changes()
```

**功能说明**：
系统托盘图标组件，为应用程序提供常驻系统托盘功能，支持自定义右键菜单、单击/双击/中键点击操作，并具有现代化的视觉样式。允许用户在关闭主窗口后继续使用程序功能。

**主要类和方法**：
- `SystemTrayIcon`：系统托盘图标类，继承自`QSystemTrayIcon`
  - `__init__(self, app_icon=None, parent=None)`：初始化系统托盘图标，检测操作系统类型
  - `_create_menu(self)`：创建托盘图标右键菜单，根据不同操作系统应用不同样式
  - `_setup_event_handlers(self)`：设置托盘图标事件处理器
  - `_on_tray_activated(self, reason)`：处理托盘图标激活事件，包含平台特定行为处理
  - `_handle_single_click(self)`：处理延迟的单击事件（防抖处理）
  - `_on_toggle_action(self)`：处理"开始/停止监听"菜单项的触发
  - `_show_about(self)`：显示关于信息
  - `update_drawing_state(self, is_active)`：更新绘制状态，同步更新菜单项和工具提示

- `get_system_tray(parent=None)`：获取系统托盘图标单例实例，支持不同平台优先加载适合的图标格式

**自定义信号**：
- `toggle_drawing_signal`：切换绘制状态信号
- `show_settings_signal`：显示设置页面信号
- `show_window_signal`：显示主窗口信号
- `exit_app_signal`：退出应用程序信号

**使用方法**：
```python
# 获取系统托盘实例
from ui.components.system_tray import get_system_tray

# 创建并显示托盘图标
tray_icon = get_system_tray(parent_window)
tray_icon.show()

# 连接信号到相应的处理方法
tray_icon.toggle_drawing_signal.connect(toggle_drawing_function)
tray_icon.show_window_signal.connect(show_window_function)
tray_icon.show_settings_signal.connect(show_settings_function)
tray_icon.exit_app_signal.connect(exit_app_function)

# 更新托盘图标状态
tray_icon.update_drawing_state(is_active)
```

**菜单项说明**：
- **开始/停止监听**：切换绘制功能的启动状态
- **显示主窗口**：显示并激活主窗口
- **设置**：直接跳转到设置页面
- **关于**：显示应用程序版本信息
- **退出**：完全退出应用程序

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

#### 3.1 core/drawer.py

**功能说明**：绘画核心模块，实现了透明绘制覆盖层、右键绘制功能和绘制管理。

**主要类和方法**：
- `DrawingSignals`：信号类，处理线程间通信
  - `start_drawing_signal`：信号，开始绘制时发出
  - `continue_drawing_signal`：信号，继续绘制时发出
  - `stop_drawing_signal`：信号，停止绘制时发出

- `TransparentDrawingOverlay`：透明绘制覆盖层
  - `__init__(self)`：初始化绘制覆盖层，创建透明窗口和绘制参数
  - `initUI(self)`：设置窗口属性和创建绘图缓冲区
  - `set_pen_width(self, width)`：设置笔尖粗细
  - `set_pen_color(self, color)`：设置笔尖颜色
  - `set_force_topmost(self, enabled)`：设置是否启用强制置顶功能
  - `_force_window_topmost(self)`：强制窗口置顶的内部方法
  - `startDrawing(self, x, y, pressure)`：开始绘制，同时停止任何正在进行的淡出效果，启用强制置顶时开始定时置顶
  - `continueDrawing(self, x, y, pressure)`：继续绘制轨迹
  - `stopDrawing(self)`：停止绘制并开始淡出效果，同时分析手势并执行，停止强制置顶定时器
  - `get_stroke_direction(self, stroke_id)`：获取指定笔画的方向
  - `paintEvent(self, event)`：绘制事件处理，负责绘制当前笔画
  - `_log_stroke_data(self, stroke_data, ...)`：记录笔画数据，简化后只记录必要信息
  - `fade_path(self)`：实现路径的淡出效果

- `DrawingManager`：绘制管理器
  - `__init__(self)`：初始化绘制管理器，创建鼠标钩子和参数
  - `start(self)`：开始绘制功能，启动监听
  - `stop(self)`：停止绘制功能，清理资源
  - `update_settings(self)`：更新设置参数，包括笔尖粗细、颜色和强制置顶设置
  - `get_last_direction(self)`：获取最后一次绘制的方向
  - `_init_mouse_hook(self)`：初始化全局鼠标监听
  - `_calculate_simulated_pressure(self, x, y)`：根据鼠标移动速度计算模拟压力值
  - `get_last_direction(self)`：获取最后一次绘制的方向序列

**使用方法**：
```python
from core.drawer import DrawingManager

# 创建绘制管理器
drawer = DrawingManager()

# 开始绘制功能
drawer.start()  # 此时可以使用鼠标右键进行绘制

# 更新设置参数
drawer.update_settings()

# 获取最后一次绘制的信息
info = drawer.get_last_direction()
print(f"最后绘制的信息: {info}")

# 停止绘制功能
drawer.stop()
```

**绘制流程**：
1. 用户按下鼠标右键开始绘制
2. 鼠标移动时捕获轨迹并绘制可见线条
3. 用户释放鼠标右键停止绘制
4. 系统分析轨迹并格式化为路径数据
5. 根据路径形状执行匹配的手势动作
6. 绘制的线条缓慢淡出，提供视觉反馈

#### 3.2 core/path_analyzer.py

**功能说明**：
路径分析模块，负责将用户绘制的原始轨迹转换为结构化路径数据，并提供手势相似度计算。该模块是GestroKey手势识别系统的核心，专注于形状轮廓识别和绘制顺序分析。

**主要类和方法**：

**PathAnalyzer 路径分析器类**：
- `__init__(self)`：初始化路径分析器，设置日志记录器
- `format_raw_path(self, raw_points: List[Tuple]) -> Dict`：将原始绘制点转换为格式化路径
- `calculate_similarity(self, path1: Dict, path2: Dict) -> float`：计算两个路径的相似度（当前版本固定返回1.0）
- `normalize_path_scale(self, path: Dict, target_size: int = 100) -> Dict`：将路径归一化到指定尺寸

**核心路径格式化流程**：
1. **路径预处理**：`_scale_small_path(coords)` - 对过小路径进行智能缩放
2. **关键点提取**：`_extract_key_points(coords)` - 提取路径的核心特征点
3. **路径简化**：`_douglas_peucker(points, tolerance)` - 道格拉斯-普克算法简化
4. **方向分析**：`_analyze_direction_changes(points)` - 检测重要的转折点

**路径预处理功能**：
- **小路径检测**：自动识别尺寸小于50像素的微小路径
- **路径缩放**：将小路径等比放大到200像素，保持形状比例
- **中心对称缩放**：以路径几何中心为基准进行缩放，避免位置偏移
- **精度提升**：改善小手势的识别准确性和关键点提取效果

**关键点提取算法**：
- **道格拉斯-普克简化**：
  - 容忍度设置为8.0像素，平衡简化效果与细节保留
  - 递归算法自动去除冗余的中间点
  - 保持路径的整体形状特征
  
- **转折点检测**：
  - 角度变化阈值：30度，识别重要的方向改变
  - 动态距离阈值：基于路径总长度的10%或最小20像素
  - 特征点保留：确保关键的几何特征不被过度简化

- **起点终点保护**：
  - 强制保留原始路径的起点和终点
  - 去除连续重复的点位，避免数据冗余
  - 确保路径连通性和完整性

**路径数据结构**：
输入原始点格式：`[(x, y, pressure, tilt, button), ...]`
输出格式化路径：
```python
{
    'points': [(x1, y1), (x2, y2), ...],    # 关键点坐标列表
    'connections': [                         # 连接关系列表
        {'from': 0, 'to': 1, 'type': 'line'},
        {'from': 1, 'to': 2, 'type': 'line'},
        ...
    ]
}
```

**几何计算工具方法**：
- `_calculate_path_length(points)`：计算路径总长度
- `_calculate_angle_change(p1, p2, p3)`：计算三点夹角变化
- `_distance_to_line(p1, p2, point)`：点到线段的距离计算
- `_get_path_bbox(points)`：计算路径边界框

**相似度计算系统**：
- **当前实现**：`calculate_similarity()` 固定返回1.0
- **设计意图**：为开发者预留的相似度算法接口
- **输入输出规范**：
  - 输入：两个标准格式的路径字典
  - 输出：0.0-1.0范围的相似度值
  - 阈值建议：≥0.7认为相似，<0.5认为不相似

**使用方法示例**：
```python
from core.path_analyzer import PathAnalyzer

# 创建路径分析器实例
analyzer = PathAnalyzer()

# 示例1：格式化原始绘制轨迹
raw_points = [
    (100, 100, 0.5, 0.0, 1),  # (x, y, pressure, tilt, button)
    (150, 100, 0.6, 0.1, 1),
    (200, 150, 0.7, 0.2, 1),
    (200, 200, 0.5, 0.0, 1)
]

formatted_path = analyzer.format_raw_path(raw_points)
print(f"格式化路径包含 {len(formatted_path['points'])} 个关键点")
print(f"连接关系: {formatted_path['connections']}")

# 示例2：路径归一化
normalized_path = analyzer.normalize_path_scale(formatted_path, target_size=200)
print(f"归一化后的路径: {normalized_path}")

# 示例3：相似度计算
path1 = {'points': [(0, 0), (100, 0), (100, 100)], 'connections': [...]}
path2 = {'points': [(10, 5), (110, 5), (110, 105)], 'connections': [...]}
similarity = analyzer.calculate_similarity(path1, path2)
print(f"路径相似度: {similarity}")  # 当前固定输出 1.0
```

**应用场景**：
- **手势识别前处理**：将用户绘制的轨迹转换为可比较的结构化数据
- **路径优化**：去除绘制过程中的抖动和冗余点位
- **几何分析**：提取手势的核心几何特征用于匹配
- **尺寸标准化**：消除绘制尺寸差异对识别精度的影响

**技术特点**：
- **容错性**：能够处理各种不规则的用户输入
- **性能优化**：算法复杂度经过优化，支持实时处理
- **平台无关**：纯Python实现，跨平台兼容
- **扩展性**：为未来的相似度算法预留了标准接口

#### 3.3 core/gesture_executor.py

**功能说明**：负责执行手势对应的动作，如模拟键盘快捷键、鼠标操作或启动程序等。设计为完全跨平台兼容，确保手势在不同操作系统上表现一致。

**主要类和方法**：
- `GestureExecutor`：手势执行器类
  - `__init__(self)`：初始化手势执行器，检测平台并设置平台特定的按键映射
  - `execute_gesture(self, gesture)`：执行手势动作，根据动作类型调用相应的执行方法
  - `_execute_hotkey(self, gesture)`：执行快捷键，根据操作系统自动转换快捷键格式
  - `_execute_mouse_action(self, gesture)`：执行鼠标动作
  - `_execute_text(self, gesture)`：执行文本输入
  - `_execute_command(self, gesture)`：执行系统命令
  - `convert_hotkey_for_platform(self, hotkey_str)`：将通用格式的快捷键字符串转换为当前平台的特定格式
  - `_parse_hotkey(self, hotkey_str)`：解析快捷键字符串，提取修饰键和主键
  - `_is_special_key(self, key)`：检查是否为特殊键（如Ctrl、Alt等）
  - `_get_platform_mapping(self, key)`：获取键的平台特定映射（例如Windows的"win"对应macOS的"command"）
  - `send_keys(self, keys)`：发送键盘按键，使用适合当前平台的方法
  - `release_all_keys(self)`：释放所有可能的按键状态，防止按键卡住

- `get_gesture_executor()`：获取手势执行器的单例实例

**平台特定实现**：
- **Windows平台**：
  - 使用`ctypes`和Windows API发送按键，支持特殊按键和组合键
  - 支持Windows特有的键如`Win`键
  - 实现windows注册表操作支持系统设置相关功能
  - 快捷键通常格式为`Ctrl+C`，`Alt+Tab`等

- **macOS平台**：
  - 使用`AppKit`和`Quartz`库发送按键事件
  - 支持macOS特有的键如`Command`(⌘)、`Option`(⌥)键
  - 快捷键映射：Windows的`Ctrl`→macOS的`Command`，`Alt`→`Option`，`Win`→`Control`
  - 快捷键通常以符号表示：如`⌘C`，`⌥⇥`等

- **Linux平台**：
  - 使用`Xlib`或`XTest`发送按键事件（X11环境）
  - 在Wayland环境下使用替代方法
  - 支持`Super`键（相当于Windows键）
  - 快捷键通常格式为`Ctrl+C`，`Alt+Tab`等

**键名映射表**：
| 通用键名 | Windows | macOS | Linux |
|---------|---------|-------|-------|
| ctrl    | Ctrl    | ⌘ Command | Ctrl |
| alt     | Alt     | ⌥ Option  | Alt  |
| shift   | Shift   | ⇧ Shift   | Shift |
| win     | Win     | ⌃ Control | Super |
| escape  | Esc     | ⎋ Esc     | Escape |
| return  | Enter   | ↩ Return  | Return |
| space   | Space   | Space     | space |

**使用方法**：
```python
# 获取手势执行器实例
from core.gesture_executor import get_gesture_executor

# 执行手势
executor = get_gesture_executor()
executor.execute_gesture(gesture_object)

# 转换快捷键格式（通用格式 → 平台特定格式）
platform_hotkey = executor.convert_hotkey_for_platform("ctrl+c")
# 在Windows上返回 "Ctrl+C"
# 在macOS上返回 "Command+C"
# 在Linux上返回 "Ctrl+C"

# 直接发送按键
executor.send_keys(["ctrl", "c"])  # 发送Ctrl+C组合键

# 确保释放所有按键
executor.release_all_keys()  # 防止按键卡住
```

**执行流程**：
1. 从`get_gesture_executor()`获取单例实例
2. 调用`execute_gesture(gesture)`执行手势
3. 根据手势的动作类型选择不同的执行方法
4. 对于快捷键动作，自动将通用格式转换为平台特定格式
5. 使用平台特定的方法发送按键或执行其他操作
6. 完成后确保所有按键都已释放

#### 3.4 core/system_monitor.py

**功能说明**：系统监测模块，提供CPU、内存使用情况和程序运行时间等信息。

**主要类和方法**：
- `SystemMonitor`：系统监测器
  - `__init__(self, update_interval=1000)`：初始化系统监测器
  - `start(self)`：开始监测系统信息
  - `stop(self)`：停止监测系统信息
  - `get_data(self)`：获取当前监测数据
  - `_update_data(self)`：更新系统信息数据，经过优化简化
  - `set_update_interval(self, interval)`：设置更新间隔
- `format_bytes(bytes_value)`：将字节数转换为可读格式

**使用方法**：
```python
from core.system_monitor import SystemMonitor
import time

# 创建系统监测器
monitor = SystemMonitor(update_interval=2000)  # 2秒更新一次

# 定义数据更新回调
def on_data_updated(data):
    print(f"CPU: {data['cpu_percent']}%, 内存: {data['memory_percent']}%")

# 连接信号
monitor.dataUpdated.connect(on_data_updated)

# 开始监测
monitor.start()

# 运行一段时间
time.sleep(10)

# 获取最新数据
latest_data = monitor.get_data()
print(f"运行时间: {latest_data['runtime']}")

# 停止监测
monitor.stop()
```

#### 3.5 core/logger.py

**功能说明**：日志记录模块，提供统一的日志记录接口。

**主要组件**：
- `Logger`：日志工具类
- `__init__(self, module_name=None)`：初始化日志记录器，默认使用APP_NAME
- `setup_logger(self)`：设置日志记录器，经过优化简化
- `debug(self, message)`、`info(self, message)`等：不同级别的日志记录方法
- `get_logger(module_name=None)`：获取一个命名的日志记录器

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
```