# GestroKey 源代码目录说明

GestroKey是一款手势控制工具，允许用户通过鼠标绘制手势来执行各种操作（如快捷键、启动程序等）。本工具的核心特性包括全局鼠标手势识别、方向分析、手势库管理以及自定义UI组件，适用于日常办公、创意设计和编程开发等场景。

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
      - [2.1.2.2 手势选项卡](#2122-手势选项卡-uigesturesgestures_tabpy)
      - [2.1.2.3 手势绘制组件](#2123-手势绘制组件-uigesturesdrawing_widgetpy)
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
│   ├── settings/            # 设置模块
│   │   ├── settings_tab.py  # 设置选项卡
│   │   ├── settings.py      # 设置管理器
│   │   ├── default_settings.json # 默认设置定义（JSON格式）
│   │   └── __init__.py      # 设置模块初始化文件
│   ├── gestures/            # 手势管理模块
│   │   ├── gestures_tab.py  # 手势管理选项卡
│   │   ├── gestures.py      # 手势库管理模块
│   │   ├── drawing_widget.py # 手势绘制组件（支持可视化路径显示）
│   │   └── default_gestures.json # 默认手势库定义（JSON格式）
│   └── __init__.py          # UI模块初始化文件
├── assets/                  # 资源文件目录
│   └── images/              # 图像资源
│       ├── console.svg      # 控制台图标
│       ├── gestures.svg     # 手势管理图标
│       ├── icon.svg         # 应用程序图标
│       └── settings.svg     # 设置图标
├── version.py               # 版本信息模块
└── main.py                  # 主程序入口
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

# 或从其他Python代码中导入并创建实例
from main import GestroKeyApp
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = GestroKeyApp()
window.show()
sys.exit(app.exec())
```

**GUI页面**：
- 控制台页面：提供绘制功能的开启和停止控制，以及系统资源监测
- 设置页面：提供应用程序设置的配置，包括笔尖粗细和笔尖颜色设置
- 手势管理页面：提供手势库的管理界面，可添加、编辑、删除手势

#### 1.2 version.py

**功能说明**：版本信息模块，存储和管理版本号、构建日期等应用程序基本信息。

**主要变量**：
- `VERSION`：版本号，如"2.0.0"
- `APP_NAME`：应用程序名称，固定为"GestroKey"
- `APP_DESCRIPTION`：应用程序描述
- `BUILD_DATE`：构建日期，格式为"YYYY-MM-DD"
- `AUTHOR`：作者信息
- `LICENSE`：许可证信息
- `VERSION_TYPE_RELEASE`：正式发布版本的类型标识
- `VERSION_TYPE_PREVIEW`：预览版本的类型标识
- `VERSION_TYPE_DEVELOPMENT`：未发布版本的类型标识
- `CURRENT_VERSION_TYPE`：当前版本的类型，可设置为上述三种类型之一

**主要函数**：
- `get_version_string()`：获取格式化的版本字符串，如"GestroKey v0.0.0"
- `get_full_version_info()`：获取完整的版本信息，返回包含所有版本相关信息的字典

**使用方法**：
```python
from version import VERSION, APP_NAME, CURRENT_VERSION_TYPE, get_version_string, get_full_version_info

# 获取版本号
current_version = VERSION  # 如："0.0.0"

# 获取应用名称
app_name = APP_NAME  # 返回："GestroKey"

# 获取当前版本类型
version_type = CURRENT_VERSION_TYPE  # 返回："未发布版"、"预览版"或"正式版"

# 获取格式化的版本字符串
version_string = get_version_string()  # 返回："GestroKey v0.0.0"

# 获取完整的版本信息
version_info = get_full_version_info()  # 返回包含所有版本信息的字典
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
手势库管理模块，负责保存和加载用户手势库，提供添加、删除、修改手势的功能。作为后端模块，专注于数据管理和持久化，与前端界面逻辑分离。

**主要类和方法**：
- `GestureLibrary`：手势库类
  - `__init__(self)`：初始化手势库
  - `_load_default_gestures(self)`：从JSON文件加载默认手势库
  - `_ensure_valid_ids(self, gestures)`：确保所有手势都有有效的整数ID，并且ID是连续的
  - `_get_next_id(self)`：获取下一个可用的ID
  - `_get_gestures_file_path(self)`：获取手势库文件路径
  - `load(self)`：从文件加载手势库
  - `save(self)`：保存手势库到文件
  - `get_gesture(self, name)`：获取指定名称的手势
  - `get_gesture_by_id(self, gesture_id)`：根据ID获取手势
  - `get_all_gestures(self, use_saved=False)`：获取所有手势
  - `get_all_gestures_sorted(self, use_saved=False)`：获取按ID排序的所有手势
  - `get_gesture_by_direction(self, direction)`：根据方向序列获取匹配的手势
  - `add_gesture(self, name, direction, action_type, action_value, gesture_id=None)`：添加新手势
  - `update_gesture_name(self, old_name, new_name)`：更新手势名称
  - `remove_gesture(self, name)`：删除指定名称的手势
  - `reset_to_default(self)`：重置手势库为默认设置
  - `has_changes(self)`：检查是否有未保存的更改

- `get_gesture_library()`：单例函数，获取手势库实例

**手势数据结构**：
```json
{
  "复制": {
    "id": 1,
    "direction": "右-下",
    "action": {
      "type": "shortcut",
      "value": "Ctrl+C"
    }
  }
}
```

**使用方法**：
```python
# 获取手势库实例
from ui.gestures.gestures import get_gesture_library
gesture_library = get_gesture_library()

# 获取所有手势
all_gestures = gesture_library.get_all_gestures()
print(f"当前有 {len(all_gestures)} 个手势")

# 添加新手势
gesture_library.add_gesture(
    name="截图",
    direction="右-下-左",
    action_type="shortcut",
    action_value="win+shift+s"
)
print(f"添加了新手势：截图")

# 更新手势名称
gesture_library.update_gesture_name("截图", "屏幕截图")
print(f"更新了手势名称")

# 查找匹配手势
direction = "右-下"
name, gesture = gesture_library.get_gesture_by_direction(direction)
if name:
    print(f"匹配到手势: {name}")
    print(f"执行动作: {gesture['action']['type']} - {gesture['action']['value']}")
else:
    print(f"未找到匹配的手势: {direction}")

# 删除手势
result = gesture_library.remove_gesture("屏幕截图")
print(f"删除结果: {'成功' if result else '失败'}")

# 重置手势库
gesture_library.reset_to_default()
print("手势库已重置为默认设置")

# 保存手势库
gesture_library.save()
print("手势库已保存")
```

###### 2.1.2.2 手势选项卡 (ui/gestures/gestures_tab.py)

**功能说明**：
手势管理界面，为用户提供可视化的手势添加、编辑和删除功能。作为前端模块，专注于用户界面展示和交互，通过调用手势库后端模块完成实际的数据操作。

**关联模块**：
- `ui/gestures/drawing_widget.py`：手势绘制组件，提供手势路径的可视化绘制和显示功能

**主要类和方法**：
- `GesturesPage`：手势管理页面类
  - `__init__(self, parent=None)`：初始化手势管理页面
  - `showEvent(self, event)`：页面显示时刷新按钮状态
  - `_init_ui(self)`：初始化UI组件和布局
  - `_create_gesture_list_panel(self)`：创建左侧手势列表面板
  - `_create_gesture_editor_panel(self)`：创建右侧手势编辑面板
  - `_load_gesture_list(self)`：加载并显示手势列表
  - `_on_gesture_selected(self, item)`：处理手势选择事件
  - `_load_gesture_to_editor(self, gesture_name)`：加载手势数据到编辑器
  - `_auto_apply_changes(self)`：自动应用表单变更到手势库（不保存到文件）
  - `_update_button_states(self)`：更新按钮启用状态
  - `_new_gesture(self)`：创建新手势
  - `_undo_changes(self)`：撤销当前修改
  - `_clear_editor(self)`：清空编辑器
  - `_delete_gesture(self)`：删除选中手势
  - `_reset_gestures(self)`：重置手势库
  - `_save_gestures(self)`：保存手势库到文件
  - `has_unsaved_changes(self)`：检查是否有未保存的更改

**界面特性**：
- **自动应用变更**：表单修改自动应用到手势库，无需手动保存
- **实时列表更新**：右侧表单修改时，左侧列表实时更新显示所有要素
- **智能按钮状态**：
  - 撤销按钮：有表单变更时启用
  - 保存手势库按钮：有手势库变更时启用
  - 页面显示时自动刷新按钮状态

**组件布局**：
- 左侧：手势列表面板
  - 手势列表（显示编号、名称、类型、快捷键）
  - 添加新手势、删除手势、重置、保存手势库按钮
- 右侧：手势编辑面板
  - 手势名称输入框
  - 快捷键输入框
  - 手势路径绘制组件（支持可视化绘制和显示）
  - 新建、清空表单、撤销按钮

**使用方法**：
```python
# 创建手势管理页面
from ui.gestures.gestures_tab import GesturesPage

# 创建页面实例
gestures_page = GesturesPage()

# 页面会自动加载并显示所有手势到左侧列表中

# 编辑手势
# 1. 点击左侧列表中的手势项
# 2. 右侧编辑器会显示手势信息
# 3. 修改名称、快捷键或绘制新路径（自动应用到手势库）
# 4. 左侧列表实时更新显示

# 添加新手势
gestures_page._add_new_gesture()    # 添加新手势（通过按钮触发）

# 删除手势
gestures_page._delete_gesture()     # 删除当前选中的手势

# 撤销和清空
gestures_page._undo_changes()       # 撤销当前修改
gestures_page._clear_editor()       # 清空表单

# 保存和重置
gestures_page._save_gestures()      # 保存手势库到文件
gestures_page._reset_gestures()     # 重置为默认手势库

# 检查未保存更改
has_changes = gestures_page.has_unsaved_changes()
```

**手势编辑界面示例**：
```python
# 手势编辑界面示例
from ui.gestures.gestures_tab import GesturesPage
from PyQt6.QtWidgets import QApplication

# 创建手势管理页面
app = QApplication([])
gestures_page = GesturesPage()

# 访问编辑器组件
name_input = gestures_page.edit_name            # QLineEdit组件
shortcut_input = gestures_page.edit_shortcut    # QLineEdit组件
drawing_widget = gestures_page.drawing_widget   # 手势绘制组件

# 设置输入字段值（会自动应用到手势库）
name_input.setText("新手势名称")
shortcut_input.setText("Ctrl+C")

# 读取输入字段值
print(f"手势名称: {name_input.text()}")
print(f"快捷键: {shortcut_input.text()}")

# 显示并运行应用程序
gestures_page.show()
app.exec()
```

###### 2.1.2.3 手势绘制组件 (ui/gestures/drawing_widget.py)

**功能说明**：
手势绘制组件，提供手势路径的可视化绘制和显示功能。支持用户在界面中直接绘制手势，并以可视化方式显示手势的路径信息，包括起点、终点、关键点和绘制方向。

**主要类和方法**：
- `GestureDrawingWidget`：手势绘制组件类
  - `__init__(self, parent=None)`：初始化绘制组件
  - `mousePressEvent(self, event)`：处理鼠标按下事件，开始绘制（自动清除之前内容）
  - `mouseMoveEvent(self, event)`：处理鼠标移动事件，记录轨迹
  - `mouseReleaseEvent(self, event)`：处理鼠标释放事件，完成绘制并自动使用路径
  - `paintEvent(self, event)`：绘制事件，负责显示手势路径
  - `_draw_formatted_path(self, painter, path)`：绘制格式化的手势路径
  - `_draw_direction_arrow(self, painter, start_point, end_point)`：绘制方向箭头
  - `clear_drawing(self)`：清除当前绘制内容
  - `load_path(self, path)`：加载并显示指定的手势路径

**可视化显示特性**：
- **起点标识**：绿色大圆点（直径12px）标识手势起点
- **终点标识**：红色圆点标识手势终点
  - 多点路径：红色圆点（直径8px）
  - 单点路径：红色小圆点（直径6px）显示在绿色起点内部
- **中间关键点**：蓝色小圆点（直径4px）显示路径的关键转折点
- **方向指示**：橙色三角形箭头显示手势的绘制方向，位于连接线的中点
- **路径连线**：蓝色线条连接各个关键点，显示完整的手势轨迹
- **自动缩放**：手势路径自动缩放以适应显示区域，保持最佳观看效果

**信号**：
- `pathCompleted`：路径绘制完成信号，发送格式化的路径数据

**使用方法**：
```python
# 创建手势绘制组件
from ui.gestures.drawing_widget import GestureDrawingWidget

# 创建绘制组件实例
drawing_widget = GestureDrawingWidget()

# 连接路径完成信号（绘制完成后自动触发）
drawing_widget.pathCompleted.connect(lambda path: print(f"绘制完成并自动使用: {path}"))

# 加载现有手势路径进行显示（自动缩放和居中）
gesture_path = {
    'points': [(100, 100), (200, 150), (300, 100)],
    'connections': [{'from': 0, 'to': 1}, {'from': 1, 'to': 2}]
}
drawing_widget.load_path(gesture_path)

# 显示组件
drawing_widget.show()

# 交互操作：
# 1. 左键拖拽：绘制新手势路径
# 2. 中键拖拽：平移画布
# 3. 空格+左键拖拽：平移画布
# 4. Alt+滚轮：缩放画布（围绕鼠标位置）
# 5. 双击中键：重置视图到默认状态
```

**绘制流程**：
1. 用户在绘制区域按下左键开始绘制（自动清除之前的路径）
2. 拖拽鼠标记录轨迹点，实时显示红色绘制线条
3. 释放鼠标完成绘制，系统自动分析路径并使用
4. 格式化后的路径以蓝色显示，包含：
   - 绿色起点标识
   - 红色终点标识（根据路径类型调整大小）
   - 蓝色中间关键点
   - 橙色方向箭头
   - 蓝色连接线

**画布交互功能**：
- **视图拖拽**：
  - 按住鼠标中键拖拽：平移画布视图
  - 空格键+鼠标左键拖拽：平移画布视图
  - 拖拽时鼠标光标自动变为手型
- **视图缩放**：
  - Alt+滚轮向上：以鼠标位置为中心放大画布
  - Alt+滚轮向下：以鼠标位置为中心缩小画布
  - 缩放范围：0.1倍到5.0倍
- **视图重置**：
  - 双击鼠标中键：自动归位，恢复到默认视图（1:1缩放，无偏移）
- **自动适配**：
  - 加载手势路径时自动缩放和居中显示，充分利用显示区域
  - 保持路径宽高比，选择合适的缩放比例
  - 自动居中显示在画布中央

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
    - Windows：通过注册表实现
    - macOS：通过LaunchAgents的plist文件实现
    - Linux：通过~/.config/autostart目录下的.desktop文件实现

- `get_settings()`：获取设置管理器实例的单例函数

**设置文件管理**：
- 默认设置来源：`ui/settings/default_settings.json`
- 用户设置保存路径：`~/.xkaaaaa/gestrokey/config/settings.json`
- 支持的设置项：
  - `pen_width`：笔尖粗细，范围1-20像素
  - `pen_color`：笔尖颜色，RGB格式数组
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
    - 笔尖预览组件
  - 应用设置组：
    - 开机自启动选项（QCheckBox）
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
  - `startDrawing(self, x, y, pressure)`：开始绘制，同时停止任何正在进行的淡出效果
  - `continueDrawing(self, x, y, pressure)`：继续绘制轨迹
  - `stopDrawing(self)`：停止绘制并开始淡出效果，同时分析手势并执行
  - `get_stroke_direction(self, stroke_id)`：获取指定笔画的方向
  - `paintEvent(self, event)`：绘制事件处理，负责绘制当前笔画
  - `_log_stroke_data(self, stroke_data, ...)`：记录笔画数据，简化后只记录必要信息
  - `fade_path(self)`：实现路径的淡出效果

- `DrawingManager`：绘制管理器
  - `__init__(self)`：初始化绘制管理器，创建鼠标钩子和参数
  - `start(self)`：开始绘制功能，启动监听
  - `stop(self)`：停止绘制功能，清理资源
  - `update_settings(self)`：更新设置参数
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

**功能说明**：路径分析模块，负责分析用户绘制的路径轨迹，将原始点数据转换为格式化路径，并计算路径相似度。

**主要类和方法**：
- `PathAnalyzer`：路径分析器
  - `format_raw_path(self, raw_points)`：将原始绘制点转换为格式化路径，包含路径预处理缩放
  - `calculate_similarity(self, path1, path2)`：计算两个路径的相似度
  - `_scale_small_path(self, coords)`：对过小的路径进行等比缩放预处理，提高格式化准确性
  - `_extract_key_points(self, coords)`：提取路径的关键点，简化路径数据
  - `_get_path_bbox(self, points)`：获取路径的边界框信息

**路径预处理功能**：
- 自动检测过小的路径（小于50像素）
- 对小路径进行等比缩放到合适大小（200像素）
- 以路径中心为基准进行缩放，保持形状不变
- 显著提高小路径的格式化准确性和关键点提取效果

**智能关键点提取算法**：
- **道格拉斯-普克算法**：初步简化路径，去除冗余点
- **角度变化分析**：检测方向变化超过30度的重要转折点
- **动态距离阈值**：根据路径总长度调整关键点间距
- **复杂图形优化**：区分轻微偏差和真正的线条转折
- 保留图形的重要特征，避免过度简化

**使用方法**：
```python
from core.path_analyzer import PathAnalyzer

# 创建路径分析器
analyzer = PathAnalyzer()

# 格式化原始绘制点
raw_points = [(100, 100, 0.5, 1.0, 1), (150, 100, 0.5, 1.1, 1), (200, 150, 0.5, 1.2, 1)]
formatted_path = analyzer.format_raw_path(raw_points)
print(f"格式化路径: {formatted_path}")

# 计算路径相似度
similarity = analyzer.calculate_similarity(path1, path2)
print(f"相似度: {similarity}")
```

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