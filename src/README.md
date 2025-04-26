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
    - [2.1.3 设置模块](#213-设置模块)
      - [2.1.3.1 设置管理器](#2131-设置管理器-uisettingssettingspy)
      - [2.1.3.2 设置选项卡](#2132-设置选项卡-uisettingssettings_tabpy)
  - [2.2 UI组件模块](#22-ui组件模块)
    - [2.2.1 按钮组件](#221-uicomponentsbuttonpy)
    - [2.2.2 卡片组件](#222-uicomponentscardpy)
    - [2.2.3 滚动条组件](#223-uicomponentsscrollbarpy)
    - [2.2.4 导航菜单组件](#224-uicomponentsnavigation_menupy)
    - [2.2.5 下拉菜单组件](#225-uicomponentscustom_comboboxpy)
    - [2.2.6 输入框组件](#226-uicomponentsinput_fieldpy)
    - [2.2.7 滑块组件](#227-uicomponentssliderpy)
    - [2.2.8 取色器组件](#228-uicomponentscolor_pickerpy)
    - [2.2.9 数字选择器组件](#229-uicomponentsnumber_spinnerpy)
    - [2.2.10 消息提示组件](#2210-uicomponentstoast_notificationpy)
    - [2.2.11 对话框组件](#2211-uicomponentsdialogpy)
    - [2.2.12 快捷键输入组件](#2212-uicomponentshotkey_inputpy)
    - [2.2.13 复选框组件](#2213-uicomponentscheckboxpy)
    - [2.2.14 悬浮提示组件](#2214-uicomponentsanimated_tooltippy)
    - [2.2.15 系统托盘组件](#2215-uicomponentssystem_traypy)
- [3. 核心功能模块](#3-核心功能模块)
  - [3.1 core/drawer.py](#31-coredrawerpy)
  - [3.2 core/stroke_analyzer.py](#32-corestroke_analyzerpy)
  - [3.3 core/gesture_executor.py](#33-coregesture_executorpy)
  - [3.4 core/system_monitor.py](#34-coresystem_monitorpy)
  - [3.5 core/logger.py](#35-coreloggerpy)
- [4. 应用程序集成](#4-应用程序集成)
  - [4.1 应用程序架构](#41-应用程序架构)
  - [4.2 程序流程](#42-程序流程)
  - [4.3 使用场景与示例](#43-使用场景与示例)
  - [4.4 扩展开发指南](#44-扩展开发指南)
- [5. 总结](#5-总结)

## 目录结构

```
src/
├── core/                    # 核心功能模块
│   ├── drawer.py            # 绘画核心模块
│   ├── stroke_analyzer.py   # 笔画分析模块
│   ├── gesture_executor.py  # 手势执行模块
│   ├── system_monitor.py    # 系统监测模块
│   └── logger.py            # 日志记录模块
├── ui/                      # 用户界面模块
│   ├── console.py           # 控制台选项卡
│   ├── settings/            # 设置模块
│   │   ├── settings_tab.py  # 设置选项卡
│   │   ├── settings.py      # 设置管理器
│   │   ├── __init__.py      # 设置模块初始化文件
│   │   └── default_settings.json # 默认设置定义（JSON格式）
│   ├── gestures/            # 手势管理模块
│   │   ├── gestures_tab.py  # 手势管理选项卡
│   │   ├── gestures.py      # 手势库管理模块
│   │   └── default_gestures.json # 默认手势库定义（JSON格式）
│   ├── components/          # UI组件模块
│   │   ├── button.py        # 自定义动画按钮组件
│   │   ├── card.py          # 自定义卡片组件
│   │   ├── scrollbar.py     # 自定义滚动条和滚动区域组件
│   │   ├── navigation_menu.py # 导航菜单组件
│   │   ├── input_field.py   # 自定义动画输入框组件
│   │   ├── slider.py        # 自定义动画滑块组件
│   │   ├── color_picker.py  # 自定义颜色选择器组件
│   │   ├── custom_combobox.py # 自定义下拉菜单组件
│   │   ├── toast_notification.py  # 通知提示组件
│   │   ├── dialog.py        # 自定义对话框组件
│   │   ├── hotkey_input.py  # 快捷键输入组件
│   │   ├── number_spinner.py # 数字选择器组件
│   │   ├── checkbox.py       # 自定义动画复选框组件
│   │   ├── animated_tooltip.py # 美化版悬浮提示组件
│   │   └── system_tray.py   # 系统托盘图标组件
│   └── __init__.py          # UI模块初始化文件
├── assets/                  # 资源文件目录
│   └── images/              # 图像资源
├── version.py               # 版本信息模块
└── main.py                  # 主程序入口
```

## 详细模块说明

### 1. 主程序模块

#### 1.1 main.py

**功能说明**：程序的主入口文件，提供带有侧边导航菜单的图形用户界面，包含控制台、设置界面和手势管理界面。

**主要类和方法**：
- `GestroKeyApp`：主窗口类，继承自`QMainWindow`
  - `__init__(self)`：初始化应用程序主窗口，设置日志记录器和全局资源
  - `init_global_resources(self)`：初始化设置管理器和手势库管理器等全局资源
  - `initUI(self)`：初始化用户界面，设置窗口属性、创建页面和底部状态栏
  - `_select_initial_page(self)`：选择初始页面（默认为控制台页面）
  - `onPageChanged(self, index)`：处理页面切换事件
  - `resizeEvent(self, event)`：处理窗口尺寸变化事件
  - `closeEvent(self, event)`：处理窗口关闭事件，检查未保存的设置和手势库更改
  - `show_global_dialog(self, ...)`：显示全局对话框
  - `_handle_save_changes_response(self, button_text)`：处理保存更改对话框的响应
  - `handle_dialog_close(self, dialog)`：处理对话框关闭事件

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
sys.exit(app.exec())
```

**GUI页面**：
- 控制台页面：提供绘制功能的开启和停止控制，以及系统资源监测
- 设置页面：提供应用程序设置的配置，包括笔尖粗细和笔尖颜色设置
- 手势管理页面：提供手势库的管理界面，可添加、编辑、删除手势

**主窗口功能**：
- 高DPI缩放支持
- 自适应布局，在窗口尺寸变化时维持界面结构
- 自动加载应用图标和页面图标
- 底部状态栏显示退出按钮和版本信息
- 窗口关闭时提示保存未保存的更改
- 异常处理，确保用户操作不会导致程序崩溃

#### 1.2 version.py

**功能说明**：版本信息模块，存储和管理版本号、构建日期等应用程序基本信息。

**主要变量**：
- `VERSION`：版本号，如"2.0.0"
- `APP_NAME`：应用程序名称，固定为"GestroKey"
- `APP_DESCRIPTION`：应用程序描述
- `BUILD_DATE`：构建日期，格式为"YYYY-MM-DD"
- `AUTHOR`：作者信息
- `LICENSE`：许可证信息

**主要函数**：
- `get_version_string()`：获取格式化的版本字符串，如"GestroKey v0.0.0"
- `get_full_version_info()`：获取完整的版本信息，返回包含所有版本相关信息的字典

**使用方法**：
```python
from version import VERSION, APP_NAME, get_version_string, get_full_version_info

# 获取版本号
current_version = VERSION  # 如："0.0.0"

# 获取应用名称
app_name = APP_NAME  # 返回："GestroKey"

# 获取格式化的版本字符串
version_string = get_version_string()  # 返回："GestroKey v0.0.0"

# 获取完整的版本信息
version_info = get_full_version_info()  # 返回包含所有版本信息的字典
```

**版本管理说明**：
- 更新应用程序版本时，只需修改`VERSION`和相关变量
- 构建日期`BUILD_DATE`自动设置为当前日期

### 2. 用户界面模块 (UI)

#### 2.1 界面UI模块

##### 2.1.1 控制台选项卡 (ui/console.py)

**功能说明**：
控制台界面，应用程序的主要交互界面，提供启动/停止绘制功能，显示系统资源监控信息。

**主要类和方法**：
- `AnimatedProgressBar`：动画进度条类
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

**特性说明**：
- 直观控制：提供切换绘制状态的按钮，根据状态自动切换文本和颜色
- 实时系统监控：显示CPU、内存使用率和运行时间
- 动画效果：资源使用率变化时有动画过渡
- 颜色反馈：根据资源使用率变化颜色，低(绿)→中(黄)→高(红)
- 卡片式布局：使用卡片组件展示系统信息
- 定时更新：自动定期更新系统资源信息
- 自适应设计：适应窗口尺寸变化

**使用方法**：
```python
# 创建控制台页面
from ui.console import ConsolePage

# 创建页面实例
console_page = ConsolePage()

# 将页面添加到导航菜单
navigation_menu.addPage(console_page, "控制台", console_icon, navigation_menu.POSITION_TOP)

# 控制绘制状态
console_page.start_drawing()  # 开始绘制
console_page.stop_drawing()   # 停止绘制
console_page.toggle_drawing() # 切换绘制状态
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

**特性说明**：
- 前后端分离：作为后端模块，专注于数据存储和管理，不涉及UI操作
- 自动初始化：首次运行时自动创建默认手势库
- 配置持久化：所有更改自动保存到配置文件
- ID管理：自动分配和管理手势ID，确保连续性
- 手势匹配：提供方向序列匹配功能
- 格式验证：验证手势数据格式，确保数据一致性
- 错误处理：提供详细的错误日志和恢复机制
- 智能更改检测：通过`has_changes()`方法精确比较当前手势库与已保存的手势库，识别未保存的更改

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

**主要类和方法**：
- `GestureContentWidget`：手势内容显示组件类
  - `__init__(self, direction, action_type, action_value, parent=None)`：初始化手势内容组件
  - `updateContent(self, direction, action_type, action_value)`：更新内容显示

- `GesturesPage`：手势管理页面类
  - `__init__(self, parent=None)`：初始化手势管理页面
  - `initUI(self)`：初始化UI组件和布局
  - `createGestureCardsList(self, parent_widget)`：创建左侧手势卡片列表区域
  - `createGestureEditor(self, parent_widget)`：创建右侧手势编辑区域
  - `updateGestureCards(self, maintain_selected=True)`：更新手势卡片列表
  - `onGestureCardClicked(self, card)`：处理手势卡片被点击事件
  - `addNewGesture(self)`：添加新手势
  - `deleteGesture(self)`：删除选中手势
  - `resetGestures(self)`：重置手势库
  - `saveGestureLibrary(self)`：保存手势库
  - `add_direction(self, direction)`：添加方向到方向序列
  - `remove_last_direction(self)`：移除最后一个方向
  - `clearEditor(self)`：清空编辑区域
  - `has_unsaved_changes(self)`：检查是否有未保存的更改

**组件布局**：
- 左侧：滚动区域，显示手势卡片列表
- 右侧：编辑区域，包含以下字段：
  - 手势名称输入框（使用AnimatedInputField组件）
  - 方向序列管理：
    - 方向显示框（使用AnimatedInputField组件）
    - 方向按钮组
  - 动作类型下拉菜单（使用CustomComboBox组件）
  - 动作值输入框（使用AnimatedInputField或HotkeyInput组件）
  - 操作按钮组（使用AnimatedButton组件）

**特性说明**：
- 前后端分离：界面层只负责UI展示和用户交互，通过调用手势库管理器完成实际数据操作
- 卡片式管理：通过卡片形式展示所有手势
- 方向编辑：通过方向按钮和方向序列显示框管理方向输入
- 响应式表单：使用自定义输入组件提供更好的用户体验
- 实时预览：编辑时实时更新卡片显示
- 方向验证：防止添加无效方向，保持手势逻辑合理性
- 操作界面：提供添加、删除和编辑功能
- 输入验证：自动验证输入数据格式
- 排序显示：按照ID顺序排列手势卡片
- 状态反馈：操作后提供状态反馈
- 对话框确认：重要操作需要对话框确认

**使用方法**：
```python
# 创建手势管理页面
from ui.gestures.gestures_tab import GesturesPage

# 创建页面实例
gestures_page = GesturesPage()

# 将页面添加到导航菜单
navigation_menu.addPage(gestures_page, "手势管理", gestures_icon, navigation_menu.POSITION_TOP)

# 卡片管理
gestures_page.updateGestureCards()  # 更新所有手势卡片
gestures_page.addNewGesture()       # 添加新手势
gestures_page.deleteGesture()       # 删除当前选中的手势

# 方向管理
gestures_page.add_direction("上")    # 添加向上方向
gestures_page.add_direction("右")    # 添加向右方向
gestures_page.remove_last_direction() # 删除最后添加的方向

# 保存和重置
gestures_page.saveGestureLibrary()  # 保存手势库
gestures_page.resetGestures()       # 重置为默认手势库
```

**方向选择界面示例**：
```python
# 手势方向选择界面示例
from ui.gestures.gestures_tab import GesturesPage
from PyQt6.QtWidgets import QApplication
from ui.components.input_field import AnimatedInputField

# 创建手势管理页面
app = QApplication([])
gestures_page = GesturesPage()

# 选择一个手势卡片
# ...

# 使用方向按钮添加方向序列
gestures_page.add_direction("上")
gestures_page.add_direction("右")
gestures_page.add_direction("下")

# 查看当前方向序列
current_direction = gestures_page.direction_text.text()
print(f"当前方向序列: {current_direction}")  # 输出: 当前方向序列: 上-右-下

# 删除最后一个方向
gestures_page.remove_last_direction()
print(f"删除后的方向序列: {gestures_page.direction_text.text()}")  # 输出: 删除后的方向序列: 上-右

# 访问其他输入字段
name_input = gestures_page.name_input           # AnimatedInputField组件
action_value_input = gestures_page.action_value_input  # AnimatedInputField组件

# 设置输入字段值
name_input.setText("新手势名称")
action_value_input.setText("ctrl+c")

# 读取输入字段值
print(f"手势名称: {name_input.text()}")
print(f"动作值: {action_value_input.text()}")

# 显示并运行应用程序
gestures_page.show()
app.exec()
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
  - `is_autostart_enabled(self)`：检查应用程序是否设置为开机自启动
  - `set_autostart(self, enable)`：设置开机自启动状态

- `get_settings()`：获取设置管理器实例的单例函数

**设置文件管理**：
- 默认设置来源：`ui/settings/default_settings.json`
- 用户设置保存路径：`~/.gestrokey/config/settings.json`
- 支持的设置项：
  - `pen_width`：笔尖粗细，范围1-20像素
  - `pen_color`：笔尖颜色，RGB格式数组

**特性说明**：
- 自动初始化：首次运行时自动创建默认配置目录和文件
- 设置持久化：所有设置保存到用户目录下的配置文件
- 参数验证：验证设置值是否有效
- 默认值回退：缺少设置项时使用默认值
- 错误处理：提供错误日志和恢复机制
- 更改检测：识别未保存的更改，避免误报

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
- 中部：横向导航菜单，包含以下页面：
  - 画笔设置页面：
    - 笔尖粗细设置（滑块和数字选择器）
    - 笔尖颜色选择（色彩选择器）
    - 笔尖预览组件
  - 应用设置页面：
    - 开机自启动选项（复选框）
- 底部：操作按钮区域
  - 重置设置按钮
  - 保存设置按钮

**特性说明**：
- 前后端分离：界面层只负责UI展示和用户交互，实际设置操作通过调用设置管理器完成
- 实时预览：设置变更时实时更新预览效果
- 直观调节：通过滑块和数字选择器调整参数
- 色彩选择器：集成色彩选择组件
- 参数验证：自动验证输入值的有效性
- 默认值恢复：一键恢复默认设置
- 分组设置：将相关设置分组显示
- 设置持久化：保存设置时调用设置管理器
- 对话框确认：重要操作需要对话框确认
- 开机自启动：支持设置应用为开机自启动（通过调用设置管理器实现），在点击保存设置按钮后应用而非立即生效

**使用方法**：
```python
# 创建设置页面
from ui.settings.settings_tab import SettingsPage

# 创建页面实例
settings_page = SettingsPage()

# 将页面添加到导航菜单
navigation_menu.addPage(settings_page, "设置", settings_icon, navigation_menu.POSITION_BOTTOM)

# 控制设置
settings_page.update_ui_from_settings()  # 从设置更新UI
settings_page.save_settings()            # 保存设置
settings_page.reset_settings()           # 重置为默认设置

# 检查未保存更改
has_changes = settings_page.has_unsaved_changes()
```

#### 2.2 UI组件模块

##### GestroKey 用户界面主题风格

GestroKey采用现代扁平化设计风格，主要特点包括：

- **主色调**：蓝色系为主（#2980b9，即RGB:41,128,185），搭配白色背景，形成清新简约的视觉效果
- **设计风格**：扁平化设计，减少立体感和阴影，注重内容的清晰呈现
- **交互动效**：丰富的动画效果，包括按钮悬停、点击的缩放动画，页面切换的滑动过渡，以及颜色渐变效果
- **组件特点**：圆角矩形设计，统一的边框半径（通常为8px），微妙的阴影效果增强层次感
- **排版设计**：清晰的字体层次结构，默认使用系统无衬线字体，标题加粗，正文保持轻量
- **图标风格**：简约线条图标，搭配主题色，确保视觉一致性
- **响应式设计**：组件自适应调整，支持不同屏幕尺寸
- **交互反馈**：所有可交互元素提供明确的视觉反馈，如颜色变化、形状变化或动画效果

##### 2.2.1 ui/components/button.py

**功能说明**：自定义动画按钮组件，提供带有动画效果的按钮，可以集成到任何界面。

**主要类和方法**：
- `AnimatedButton`：动画按钮类，继承自`QPushButton`
  - `__init__(text, parent=None, icon=None, primary_color=None, hover_color=None, text_color=None, border_radius=None, icon_size=None, min_width=None, min_height=None, border_color=None, shadow_color=None)`：初始化按钮，支持多种自定义参数
    - `text`：按钮文本
    - `parent`：父窗口组件
    - `icon`：按钮图标，可以是QIcon对象或图标文件路径
    - `primary_color`：按钮主色调，RGB格式的数组，如[41, 128, 185]或十六进制颜色字符串"#2980b9"
    - `hover_color`：按钮悬停色调，RGB格式的数组或十六进制颜色字符串
    - `text_color`：按钮文本颜色，RGB格式的数组或十六进制颜色字符串
    - `border_radius`：按钮边框圆角半径，整数值（像素）
    - `icon_size`：图标大小，整数值（像素）
    - `min_width`：按钮最小宽度，整数值（像素）
    - `min_height`：按钮最小高度，整数值（像素）
    - `border_color`：边框颜色，RGB格式的数组或十六进制颜色字符串
    - `shadow_color`：阴影颜色，RGB格式的数组或十六进制颜色字符串
  - `_parse_color(color)`：解析颜色参数，支持RGB列表和十六进制颜色字符串
  - `_setup_animations()`：设置动画效果
  - `set_primary_color(color)`：设置按钮主色调
    - `color`：RGB格式的数组，如[41, 128, 185]或十六进制颜色字符串
  - `set_hover_color(color)`：设置按钮悬停色调
    - `color`：RGB格式的数组，如[52, 152, 219]或十六进制颜色字符串
  - `set_text_color(color)`：设置按钮文本颜色
    - `color`：RGB格式的数组，如[255, 255, 255]或十六进制颜色字符串
  - `set_border_radius(radius)`：设置按钮边框圆角半径
    - `radius`：整数值（像素）
  - `setEnabled(enabled)`：重写的设置按钮可用状态方法，提供禁用状态的视觉反馈
    - `enabled`：布尔值，True表示启用，False表示禁用

**特性说明**：
- 扁平化设计，主题色为蓝色系
- 动画效果：
  - 鼠标悬停时文字轻微上浮和放大的动画效果
  - 按下时文字下沉和缩小的动画效果
  - 按钮整体的缩放动画，按下时缩小至96%
  - 颜色过渡动画
- 可定制：
  - 支持自定义颜色、图标、图标大小、文本颜色和圆角半径
  - 支持边框颜色和阴影颜色的单独设置
- 自动颜色计算：
  - 自动计算悬停色调，如未指定则基于主色调生成更亮的颜色
  - 当主色调通过set_primary_color方法变更时，悬停色调会自动更新
- 支持动态颜色切换
- 视觉细节：
  - 阴影和高光效果
  - 按下状态时的内阴影
  - 禁用状态时的灰色外观
- 状态管理：
  - 支持禁用状态，禁用时无动画效果，鼠标指针变为普通箭头
  - 状态切换时平滑过渡

**应用场景**：
- 主窗口的退出按钮
- 控制台页面的开始和停止绘制按钮
- 设置页面的保存和重置设置按钮
- 手势管理页面的添加、删除和保存手势按钮

**使用方法**：
```python
from ui.components.button import AnimatedButton
from PyQt6.QtWidgets import QVBoxLayout, QWidget

# 创建基本按钮（使用默认样式）
button = AnimatedButton("按钮文本")

# 创建自定义按钮（设置所有可选参数）
custom_button = AnimatedButton(
    text="自定义按钮", 
    primary_color=[41, 128, 185],  # 蓝色
    hover_color=[52, 152, 219],    # 悬停时的颜色（可选，不提供时会自动基于主色计算）
    text_color=[255, 255, 255],    # 白色文本
    icon="path/to/icon.png",       # 设置图标
    icon_size=24,                  # 设置图标大小
    border_radius=12,              # 设置圆角半径
    min_width=120,                 # 最小宽度
    min_height=40,                 # 最小高度
    border_color=[30, 100, 160],   # 边框颜色
    shadow_color=[0, 0, 0, 60]     # 阴影颜色，带透明度
)

# 创建具有特定功能的按钮
save_button = AnimatedButton("保存", primary_color=[46, 204, 113])  # 绿色保存按钮
cancel_button = AnimatedButton("取消", primary_color=[231, 76, 60])  # 红色取消按钮

# 添加按钮到布局
layout = QVBoxLayout()
layout.addWidget(button)
layout.addWidget(custom_button)
layout.addWidget(save_button)
layout.addWidget(cancel_button)

# 连接信号
button.clicked.connect(on_button_clicked)

# 动态修改按钮属性
button.set_primary_color([25, 80, 160])  # 修改为深蓝色
button.set_border_radius(16)             # 修改圆角半径
button.set_text_color([240, 240, 240])   # 修改文本颜色为浅灰色

# 设置按钮为禁用状态
button.setEnabled(False)  # 按钮变为灰色，不再响应鼠标事件和显示动画效果

# 创建包含图标的按钮
from PyQt6.QtGui import QIcon
icon = QIcon("path/to/icon.png")
icon_button = AnimatedButton("图标按钮", icon=icon)
```

**样式自定义**：
```python
# 创建红色主题按钮
red_button = AnimatedButton(
    text="危险操作",
    primary_color=[220, 53, 69],   # 红色
    hover_color=[220, 53, 69, 50], # 可选：自定义悬停色（更淡的红色）
    text_color=[255, 255, 255],    # 白色文本
    border_radius=4                # 小圆角半径
)

# 创建扁平风格按钮
flat_button = AnimatedButton(
    text="扁平风格",
    primary_color=[248, 249, 250], # 白色背景
    text_color=[52, 58, 64],       # 深灰色文本
    border_radius=0                # 无圆角
)

# 创建高对比度按钮
high_contrast_button = AnimatedButton(
    text="高对比度",
    primary_color=[52, 58, 64],    # 深灰色背景 
    text_color=[248, 249, 250],    # 白色文本
    border_radius=20               # 大圆角半径
)
```

##### 2.2.2 ui/components/card.py

**功能说明**：卡片组件，提供有交互效果的卡片容器，可以容纳其他组件，适合展示结构化信息。

**主要类和方法**：
- `CardWidget`：卡片组件类，继承自`QWidget`
  - `__init__(parent=None, primary_color=None, hover_color=None, selected_color=None, text_color=None, border_radius=None, min_width=None, min_height=None, title=None, shadow_color=None)`：初始化卡片，支持多种自定义参数
    - `parent`：父窗口组件
    - `primary_color`：卡片主色调，RGB格式的数组或十六进制颜色字符串，默认为淡蓝色[248, 253, 255]
    - `hover_color`：卡片悬停色调，RGB格式的数组或十六进制颜色字符串，默认自动基于主色调生成
    - `selected_color`：卡片选中状态颜色，RGB格式的数组或十六进制颜色字符串，默认为更淡的主题蓝色[180, 220, 250]
    - `text_color`：卡片文本颜色，RGB格式的数组或十六进制颜色字符串，默认为深灰色[50, 50, 50]
    - `border_radius`：卡片边框圆角半径，整数值（像素），默认为12
    - `min_width`：卡片最小宽度，整数值（像素），默认为180
    - `min_height`：卡片最小高度，整数值（像素），默认为120
    - `title`：卡片标题，字符串，如果提供将在卡片顶部显示标题
    - `shadow_color`：卡片阴影颜色，RGB格式的数组或十六进制颜色字符串，默认为半透明黑色[0, 0, 0, 30]
  - `add_widget(widget)`：向卡片内添加组件
    - `widget`：任何QWidget子类的实例，将被添加到卡片内容区域
  - `set_selected(selected)`：设置卡片的选中状态
    - `selected`：布尔值，True表示选中，False表示未选中
  - `is_selected()`：获取卡片的选中状态
    - 返回值：布尔值，True表示卡片当前被选中，False表示未选中
  - `set_title(title)`：设置卡片标题
    - `title`：字符串，卡片的新标题
  - `get_title()`：获取卡片标题
    - 返回值：字符串，当前卡片标题
  - `set_primary_color(color)`：设置卡片主色调
    - `color`：RGB格式的数组或十六进制颜色字符串
  - `set_hover_color(color)`：设置卡片悬停色调
    - `color`：RGB格式的数组或十六进制颜色字符串
  - `set_selected_color(color)`：设置卡片选中状态的颜色
    - `color`：RGB格式的数组或十六进制颜色字符串
  - `set_text_color(color)`：设置卡片文本颜色
    - `color`：RGB格式的数组或十六进制颜色字符串
  - `set_border_radius(radius)`：设置卡片边框圆角半径
    - `radius`：整数值（像素）

**特性说明**：
- 扁平化设计，默认使用淡蓝色系主题，视觉效果柔和
- 丰富的动画效果：
  - 鼠标悬停时的背景颜色平滑过渡动画
  - 鼠标按下时的缩放动画，缩小到97%提供明确的视觉反馈
  - 阴影高度动画，悬停时阴影增强，离开时平滑过渡回原始状态
  - 动态阴影效果，悬停和按下状态有不同的阴影表现
- 选中状态管理：
  - 支持设置卡片选中状态，选中时使用特定颜色（默认为更淡的蓝色）
  - 选中时可显示加粗边框，增强视觉区分度
- 视觉细节优化：
  - 微妙的高光效果，增强立体感
  - 按下状态时的内阴影效果，提供更真实的按压感
  - 颜色智能计算，自动基于主色调生成悬停色和选中色
- 内容管理：
  - 支持添加标题，自动在卡片顶部显示
  - 内容随卡片一起应用动画效果，提供更连贯的交互体验
  - 适当的内边距设计，确保内容不会覆盖卡片边框，保持美观
- 完全可定制的外观：
  - 颜色、圆角、最小尺寸和阴影等参数可自定义
  - 动态更新外观，支持运行时更改属性
- 信号支持：
  - 提供`clicked`信号，便于处理用户交互
- 其他功能：
  - 可直接运行文件查看示例效果，便于单独调试
  - 详细的日志记录，便于开发调试

**使用方法**：
```python
from ui.components.card import CardWidget
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

# 创建基本卡片
card = CardWidget(title="卡片标题")

# 添加内容
content_label = QLabel("这是卡片内容")
content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
card.add_widget(content_label)

# 创建自定义颜色的卡片
custom_card = CardWidget(
    title="自定义卡片",
    primary_color=[230, 230, 250],  # 淡紫色
    hover_color=[200, 200, 240],    # 悬停颜色
    selected_color=[85, 170, 225],  # 选中状态颜色（更淡的主题蓝色）
    text_color=[70, 70, 120],       # 文本颜色
    border_radius=12,               # 边框圆角
    min_width=200,                  # 最小宽度
    min_height=150,                 # 最小高度
    shadow_color=[0, 0, 0, 40]      # 阴影颜色（带透明度）
)

# 创建多个卡片并添加到布局
layout = QVBoxLayout()
layout.addWidget(card)
layout.addWidget(custom_card)

# 创建带有复杂内容的卡片
info_card = CardWidget(title="用户信息")
content_widget = QWidget()
content_layout = QVBoxLayout(content_widget)
content_layout.addWidget(QLabel("姓名: 张三"))
content_layout.addWidget(QLabel("年龄: 30"))
content_layout.addWidget(QLabel("职业: 程序员"))
info_card.add_widget(content_widget)
layout.addWidget(info_card)

# 设置选中状态
card.set_selected(True)

# 监听点击事件
def on_card_clicked():
    print(f"卡片 '{card.get_title()}' 被点击")
    
card.clicked.connect(on_card_clicked)

# 动态修改卡片属性
card.set_title("新标题")
card.set_primary_color([240, 255, 240])  # 淡绿色
```

**实际应用示例**：在手势管理中使用卡片展示手势
```python
# 为每个手势创建一个卡片
gestures = get_gesture_library().get_all_gestures()
for name, gesture in gestures.items():
    # 创建手势卡片
    gesture_card = CardWidget(title=name)
    
    # 创建卡片内容
    content = QWidget()
    content_layout = QVBoxLayout(content)
    content_layout.addWidget(QLabel(f"方向: {gesture['direction']}"))
    content_layout.addWidget(QLabel(f"动作: {gesture['action']['value']}"))
    
    # 添加内容到卡片
    gesture_card.add_widget(content)
    
    # 添加卡片到列表
    cards_layout.addWidget(gesture_card)
    
    # 连接点击事件
    gesture_card.clicked.connect(lambda card=gesture_card: on_gesture_card_clicked(card))
```

##### 2.2.3 ui/components/scrollbar.py

**功能说明**：自定义滚动条和滚动区域组件，提供有动画效果的滚动体验，替代标准的QScrollBar和QScrollArea。

**主要类和方法**：
- `AnimatedScrollBar`：自定义滚动条类，继承自`QScrollBar`
  - `__init__(orientation=Qt.Orientation.Vertical, parent=None)`：初始化滚动条
    - `orientation`：滚动条方向，可以是Qt.Orientation.Vertical（垂直）或Qt.Orientation.Horizontal（水平）
    - `parent`：父窗口组件
  - `enterEvent(event)`：处理鼠标进入事件，触发透明度增加动画和展开动画
  - `leaveEvent(event)`：处理鼠标离开事件，触发透明度减少动画和延迟收缩
  - `_startCollapseAnimation()`：开始收缩动画，将滚动条收缩为细线
  - `_startExpandAnimation()`：开始展开动画，将滚动条恢复为正常宽度
  - `_onCollapseFinished()`：收缩动画完成后的回调函数
  - `_onExpandFinished()`：展开动画完成后的回调函数
  - `mousePressEvent(event)`：处理鼠标按下事件，更新滚动条样式并取消收缩
  - `mouseReleaseEvent(event)`：处理鼠标释放事件，恢复滚动条样式并启动收缩延时
  - `wheelEvent(event)`：处理鼠标滚轮事件，重置收缩计时器并调整滚动值
  - `get_color_alpha()`：获取颜色透明度值
  - `set_color_alpha(alpha)`：设置滚动条颜色的透明度，用于动画效果
    - `alpha`：透明度值，范围0-255
  - `get_handle_position()`：获取滑块位置
  - `set_handle_position(position)`：设置滑块位置，用于动画效果
  - `get_current_width()`：获取当前宽度
  - `set_current_width(width)`：设置滚动条当前宽度，用于折叠/展开动画
    - `width`：宽度值，单位像素
  - `_updateStyle()`：更新滚动条样式表，应用当前设置的颜色和宽度
  - `_setupAnimations()`：设置动画对象和参数

- `AnimatedScrollArea`：自定义滚动区域类，继承自`QScrollArea`
  - `__init__(parent=None)`：初始化滚动区域，集成自定义滚动条
    - `parent`：父窗口组件
  - `eventFilter(obj, event)`：事件过滤器，拦截滚轮事件以实现平滑滚动
  - `_handleWheelEvent(event)`：处理滚轮事件，实现动画滚动效果
  - `setVerticalScrollBarPolicy(policy)`：设置并记录垂直滚动条显示策略
    - `policy`：滚动条策略，如Qt.ScrollBarPolicy.ScrollBarAsNeeded
  - `setHorizontalScrollBarPolicy(policy)`：设置并记录水平滚动条显示策略
    - `policy`：滚动条策略，如Qt.ScrollBarPolicy.ScrollBarAsNeeded

**特性说明**：
- 扁平化设计，使用应用程序主题蓝色保持风格一致
- **默认以折叠状态显示**：滚动条初始化时即以折叠状态（细线）显示，最大程度节省界面空间
- **自动折叠功能**：鼠标离开滚动条区域后，滚动条会在短暂延迟后平滑收缩为细小的线条，节省界面空间
- **适当的滚动速度**：通过调整滚轮事件的角度增量值，提供合适的滚动步长
- **平滑动画滚动**：使用QPropertyAnimation实现内容滚动的平滑过渡，而非传统的瞬间跳转
- 滚动条宽度自适应，收缩(2px)和展开(10px)时有平滑过渡动画，视觉效果流畅
- 圆角滑块设计，符合扁平化设计风格
- 透明度动画效果，鼠标悬停时变为完全不透明(255)，离开时恢复半透明(180)
- 无边框设计，隐藏了传统滚动条的箭头和槽轨道，界面更为简洁美观
- 自动适应垂直和水平方向，提供一致的视觉体验，代码复用率高
- 动画使用缓出曲线(OutCubic)，提供自然的减速效果，模拟物理世界的惯性
- 滑块最小长度限制(30px)，确保在内容较多时仍能轻松操作
- 智能延迟系统(800ms)，防止频繁使用时的折叠/展开抖动，体验更为流畅
- 交互优化，滚动或点击时自动展开，使用完毕后自动收缩，用户体验佳
- 滚动区域无缝集成自定义滚动条，使用方式与标准QScrollArea一致，降低学习成本
- 可直接运行文件查看示例效果，便于单独调试和演示
- 详细的日志记录功能，记录滚动条状态变化，便于调试和问题排查

**使用方法**：
```python
from ui.components.scrollbar import AnimatedScrollBar, AnimatedScrollArea
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

# 方法1：使用AnimatedScrollArea（推荐，提供完整功能）
scroll_area = AnimatedScrollArea()
scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # 移除边框
scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

# 创建内容窗口
content_widget = QWidget()
content_layout = QVBoxLayout(content_widget)

# 添加多个标签作为内容
for i in range(30):
    label = QLabel(f"内容项 #{i+1}")
    label.setMinimumHeight(30)  # 设置最小高度以便看到滚动效果
    content_layout.addWidget(label)

# 设置内容到滚动区域
scroll_area.setWidget(content_widget)

# 添加到界面布局
layout = QVBoxLayout()
layout.addWidget(scroll_area)
main_widget.setLayout(layout)

# 方法2：单独使用AnimatedScrollBar（高级用法，需手动设置）
standard_scroll_area = QScrollArea()
custom_scroll_bar = AnimatedScrollBar(Qt.Orientation.Vertical)

# 设置自定义滚动条到标准滚动区域
standard_scroll_area.setVerticalScrollBar(custom_scroll_bar)

# 可以同时设置垂直和水平滚动条
horizontal_scroll_bar = AnimatedScrollBar(Qt.Orientation.Horizontal)
standard_scroll_area.setHorizontalScrollBar(horizontal_scroll_bar)

# 添加到界面布局
another_layout.addWidget(standard_scroll_area)
```

**高级用法**：
```python
# 访问AnimatedScrollArea中的内部滚动条
from PyQt6.QtWidgets import QSizePolicy

# 创建滚动区域
custom_scroll_area = AnimatedScrollArea()

# 获取内部的滚动条对象（垂直）
vertical_bar = custom_scroll_area.verticalScrollBar()
if isinstance(vertical_bar, AnimatedScrollBar):
    # 自定义滚动条颜色透明度
    vertical_bar.set_color_alpha(200)  # 设置不透明度为200
    
    # 注意：其他内部参数如_primary_color, _collapsed_width等
    # 虽然可以直接访问，但建议通过公共接口方法操作

# 设置滚动区域内容后需要调整内容大小策略
content = QWidget()
content_layout = QVBoxLayout(content)
# ... 添加内容 ...
content.setLayout(content_layout)
custom_scroll_area.setWidget(content)
content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
```

**实际应用场景**：
```python
# 在手势管理界面中使用滚动区域展示大量手势卡片
from ui.components.scrollbar import AnimatedScrollArea
from ui.components.card import CardWidget

# 创建滚动区域
gestures_scroll_area = AnimatedScrollArea()
gestures_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
gestures_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
gestures_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

# 创建内容容器
gestures_container = QWidget()
gestures_layout = QVBoxLayout(gestures_container)
gestures_layout.setContentsMargins(5, 5, 5, 5)
gestures_layout.setSpacing(10)

# 添加多个手势卡片
gestures = get_gesture_library().get_all_gestures()
for name, gesture in gestures.items():
    gesture_card = CardWidget(title=name)
    # ... 设置卡片内容 ...
    gestures_layout.addWidget(gesture_card)

# 设置内容到滚动区域
gestures_scroll_area.setWidget(gestures_container)

# 添加到界面布局
main_layout.addWidget(gestures_scroll_area)
```

##### 2.2.4 ui/components/navigation_menu.py

**功能说明**：侧边导航菜单组件，提供垂直和水平两种导航模式，包含分组功能和切换动画效果，符合应用主题风格。

**主要类和方法**：
- `AnimatedNavigationButton`：动画导航按钮类，用于显示单个导航按钮
  - `__init__(text, icon=None, parent=None, orientation=0)`：初始化导航按钮
    - `text`：按钮显示文本
    - `icon`：按钮图标，QIcon对象或图标路径
    - `parent`：父窗口组件
    - `orientation`：方向，0代表垂直，1代表水平
  - `setSelected(selected)`：设置按钮选中状态，并触发动画
    - `selected`：布尔值，True表示选中，False表示未选中
  - `setText(text)`：设置按钮文本
    - `text`：新的按钮文本
  - `setIcon(icon)`：设置按钮图标
    - `icon`：QIcon对象或图标路径
  - `setOrientation(orientation)`：设置按钮方向
    - `orientation`：0代表垂直，1代表水平
  - `paintEvent(event)`：绘制按钮外观，包括背景、图标、文本和选中指示器
  - `_startAnimation(selected)`：开始选中/未选中状态的动画效果
  - `_updateAppearance()`：更新按钮外观，根据当前状态调整颜色和指示器位置

- `AnimatedStackedWidget`：带动画效果的堆叠窗口小部件，用于切换内容页面，提供平滑过渡动画
  - `__init__(parent=None)`：初始化堆叠窗口组件
  - `addWidget(widget)`：添加子窗口组件
  - `setCurrentIndex(index, direction=None)`：设置当前显示的子窗口，并指定动画方向
  - `setCurrentWidget(widget, direction=None)`：设置当前显示的子窗口对象，并指定动画方向

- `SideNavigationMenu`：导航菜单容器类，支持垂直和水平布局，以及导航按钮分组
  - `__init__(parent=None, orientation=ORIENTATION_VERTICAL)`：初始化导航菜单
    - `parent`：父窗口组件
    - `orientation`：导航方向，ORIENTATION_VERTICAL(0)为垂直导航，ORIENTATION_HORIZONTAL(1)为水平导航
  - `addPage(widget, text, icon=None, position=POSITION_TOP, group_name=None)`：添加新的页面，支持指定位置和分组
    - `widget`：页面内容组件，通常是QWidget的子类
    - `text`：导航按钮显示文本
    - `icon`：导航按钮图标，QIcon对象或图标路径
    - `position`：按钮位置，可以是POSITION_TOP或POSITION_BOTTOM，分别表示顶部区域和底部区域
    - `group_name`：分组名称，指定按钮所属的分组
    - 返回值：新添加页面的索引
  - `createGroup(name, position=POSITION_TOP, title=None)`：创建新的导航按钮分组
    - `name`：分组名称，唯一标识
    - `position`：分组位置，POSITION_TOP或POSITION_BOTTOM
    - `title`：分组标题，可选，显示在分组顶部
  - `setCurrentIndex(index)`：设置当前页面，触发动画切换
    - `index`：页面索引，整数值
  - `setCurrentPage(index)`：设置当前页面，同setCurrentIndex
  - `currentIndex()`：获取当前页面索引
    - 返回值：当前选中的页面索引，整数值
  - `widget(index)`：获取指定索引的内容窗口
    - `index`：页面索引，整数值
    - 返回值：对应索引的内容组件
  - `setPageText(index, text)`：设置指定索引的导航按钮文本
    - `index`：页面索引，整数值
    - `text`：新的按钮文本
  - `setPageIcon(index, icon)`：设置指定索引的导航按钮图标
    - `index`：页面索引，整数值
    - `icon`：QIcon对象或图标路径
  - `setPagePosition(index, position, group_name=None)`：更改已有页面的位置和分组
    - `index`：页面索引，整数值
    - `position`：新的页面位置，POSITION_TOP或POSITION_BOTTOM
    - `group_name`：新的分组名称，可选
  - `pagePosition(index)`：获取页面的位置
    - `index`：页面索引，整数值
    - 返回值：页面位置，POSITION_TOP或POSITION_BOTTOM
  - `pageGroup(index)`：获取页面所在的分组名称
    - `index`：页面索引，整数值
    - 返回值：分组名称字符串
  - `count()`：获取页面总数
    - 返回值：页面总数，整数值
  - `currentChanged`：信号，当前页面变化时触发，传递新的索引值

**特性说明**：
- 多方向布局：支持垂直（左侧）和水平（顶部）两种导航模式
- 自动适应：根据选择的方向自动调整导航栏和内容区的位置关系
- 分组功能：支持将导航按钮分组，可以创建多个命名分组并设置分组标题
- 扁平化设计，与应用主题风格一致，视觉统一
- 导航按钮支持两种位置定位：顶部(POSITION_TOP)和底部(POSITION_BOTTOM)
- 支持将重要和常用导航按钮（如控制台）放在顶部，将设置等辅助功能放在底部，优化用户体验
- 可灵活调整导航按钮位置和分组，无需改变导航按钮的添加顺序，布局更加灵活
- 导航切换时的平滑动画过渡效果，提升用户体验
- 智能判断切换方向：根据当前页面和目标页面的位置关系，自动选择动画方向
- 区域内切换：同一区域内按钮之间切换时，动画方向跟随实际位置关系
- 跨区域和跨分组切换：不同区域或分组之间切换时，动画方向符合直观预期
- 导航按钮支持图标和文本，信息呈现更加丰富
- 选中状态和悬停状态的动画效果，视觉反馈明确
- 选中按钮的高亮指示器动画，根据导航方向自动显示垂直或水平指示条
- 自动适应内容区域大小，根据窗口尺寸调整布局
- 可直接运行文件查看示例效果，便于单独调试和演示

**使用方法**：
```python
from ui.components.navigation_menu import SideNavigationMenu
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon

# 创建垂直导航菜单组件（默认）
nav_menu = SideNavigationMenu(orientation=SideNavigationMenu.ORIENTATION_VERTICAL)

# 创建水平导航菜单组件
# nav_menu = SideNavigationMenu(orientation=SideNavigationMenu.ORIENTATION_HORIZONTAL)

# 创建要添加到菜单的内容页面
console_page = QWidget()
console_layout = QVBoxLayout(console_page)
console_layout.addWidget(QLabel("控制台内容"))

gestures_page = QWidget()
gestures_layout = QVBoxLayout(gestures_page)
gestures_layout.addWidget(QLabel("手势管理内容"))

settings_page = QWidget()
settings_layout = QVBoxLayout(settings_page)
settings_layout.addWidget(QLabel("设置内容"))

# 加载图标
console_icon = QIcon("path/to/console_icon.png")
gestures_icon = QIcon("path/to/gestures_icon.png")
settings_icon = QIcon("path/to/settings_icon.png")

# 创建分组
nav_menu.createGroup("main", nav_menu.POSITION_TOP, "主要功能")
nav_menu.createGroup("settings", nav_menu.POSITION_BOTTOM, "系统设置")

# 添加带图标的导航页面到指定分组
console_index = nav_menu.addPage(
    console_page, 
    "控制台", 
    console_icon, 
    nav_menu.POSITION_TOP,
    "main"  # 指定分组
)

# 添加手势管理导航页面
gestures_index = nav_menu.addPage(
    gestures_page, 
    "手势管理", 
    gestures_icon, 
    nav_menu.POSITION_TOP,
    "main"  # 指定分组
)

# 将设置导航页面放在底部分组
settings_index = nav_menu.addPage(
    settings_page, 
    "设置", 
    settings_icon, 
    nav_menu.POSITION_BOTTOM,
    "settings"  # 指定分组
)

# 切换到指定页面
nav_menu.setCurrentIndex(0)  # 切换到控制台页面

# 监听页面切换事件
def onPageChanged(index):
    print(f"切换到页面 {index}")
    
nav_menu.currentChanged.connect(onPageChanged)

# 动态更改页面位置和分组
nav_menu.setPagePosition(1, nav_menu.POSITION_BOTTOM, "settings")  # 将手势管理页面移到底部的settings分组

# 检查页面当前位置和分组
position = nav_menu.pagePosition(1)
group = nav_menu.pageGroup(1)
print(f"页面1的位置: {'顶部' if position == nav_menu.POSITION_TOP else '底部'}, 分组: {group}")

# 动态更改页面文本
nav_menu.setPageText(0, "主控制台")

# 获取页面内容组件
content = nav_menu.widget(0)

# 获取页面总数
page_count = nav_menu.count()
print(f"页面总数: {page_count}")

# 添加到主窗口布局
main_layout = QVBoxLayout()
main_layout.addWidget(nav_menu)
main_window.setLayout(main_layout)
```

**实际应用示例**：
```python
# 在主应用程序中使用SideNavigationMenu
from ui.components.navigation_menu import SideNavigationMenu
from ui.console import ConsoleTab
from ui.settings.settings_tab import SettingsTab
from ui.gestures.gestures_tab import GesturesTab

# 创建主窗口
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GestroKey")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建导航菜单（垂直模式）
        self.nav_menu = SideNavigationMenu(
            orientation=SideNavigationMenu.ORIENTATION_VERTICAL
        )
        
        # 创建分组
        self.nav_menu.createGroup("main", self.nav_menu.POSITION_TOP, "主要功能")
        self.nav_menu.createGroup("settings", self.nav_menu.POSITION_BOTTOM)
        
        # 创建各页面内容
        self.console_tab = ConsoleTab()
        self.gestures_tab = GesturesTab()
        self.settings_tab = SettingsTab()
        
        # 加载图标
        icons_dir = "path/to/icons"
        console_icon = QIcon(f"{icons_dir}/console.svg")
        gestures_icon = QIcon(f"{icons_dir}/gestures.svg")
        settings_icon = QIcon(f"{icons_dir}/settings.svg")
        
        # 添加页面到指定分组
        self.nav_menu.addPage(
            self.console_tab, 
            "控制台", 
            console_icon, 
            self.nav_menu.POSITION_TOP,
            "main"
        )
        self.nav_menu.addPage(
            self.gestures_tab, 
            "手势管理", 
            gestures_icon, 
            self.nav_menu.POSITION_TOP,
            "main"
        )
        self.nav_menu.addPage(
            self.settings_tab, 
            "设置", 
            settings_icon, 
            self.nav_menu.POSITION_BOTTOM,
            "settings"
        )
        
        # 添加导航菜单到主布局
        main_layout.addWidget(self.nav_menu)
```

##### 2.2.5 ui/components/custom_combobox.py

**功能说明**：自定义下拉菜单组件，提供带有动画效果的下拉选择界面，可以集成到任何界面。

**主要类和方法**：
- `CustomComboBox`：自定义下拉菜单类，继承自`QComboBox`
  - `__init__(parent=None)`：初始化下拉菜单
    - `parent`：父窗口组件
  - `setBackgroundColor(color)`：设置下拉菜单背景颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串（如"#ffffff"）
  - `setBackgroundHoverColor(color)`：设置鼠标悬停时的背景颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setBackgroundPressColor(color)`：设置鼠标按下时的背景颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setBorderColor(color)`：设置下拉菜单边框颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setTextColor(color)`：设置下拉菜单文本颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setTextHoverColor(color)`：设置鼠标悬停时的文本颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setBorderRadius(radius)`：设置下拉菜单边框圆角半径
    - `radius`：整数值（像素）
  - `setBorderWidth(width)`：设置下拉菜单边框宽度
    - `width`：整数值（像素）
  - `setHoverBorderColor(color)`：设置鼠标悬停时的边框颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setPressBorderColor(color)`：设置鼠标按下时的边框颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setDropdownBorderRadius(radius)`：设置下拉列表边框圆角半径
    - `radius`：整数值（像素）
  - `setArrowColor(color)`：设置下拉箭头颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setArrowHoverColor(color)`：设置鼠标悬停时的箭头颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setArrowPressColor(color)`：设置鼠标按下时的箭头颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setDropShadowColor(color)`：设置下拉阴影颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setDropShadowRadius(radius)`：设置下拉阴影半径
    - `radius`：整数值（像素）
  - `setArrowIcons(normal_icon, focus_icon)`：设置自定义箭头图标（此方法保留但内部已改为直接绘制箭头）
    - `normal_icon`：正常状态的图标路径
    - `focus_icon`：焦点状态的图标路径
  - `setAnimationDuration(hover_duration=200, press_duration=100, arrow_duration=300, popup_duration=250)`：设置各种动画的持续时间
    - `hover_duration`：悬停动画持续时间（毫秒）
    - `press_duration`：按下动画持续时间（毫秒）
    - `arrow_duration`：箭头旋转动画持续时间（毫秒）
    - `popup_duration`：弹出动画持续时间（毫秒）
  - `setAnimationEasingCurve(hover_curve=QEasingCurve.Type.OutCubic, press_curve=QEasingCurve.Type.OutCubic, arrow_curve=QEasingCurve.Type.OutBack, popup_curve=QEasingCurve.Type.OutCubic)`：设置各种动画的缓动曲线
    - `hover_curve`：悬停动画缓动曲线
    - `press_curve`：按下动画缓动曲线
    - `arrow_curve`：箭头旋转动画缓动曲线
    - `popup_curve`：弹出动画缓动曲线
  - `customizeCustomComboBox(**customValues)`：批量设置多个样式属性
    - `customValues`：关键字参数，可包含backgroundColor、backgroundHoverColor、textColor等
  - `showPopup()`：重写的显示下拉列表方法，添加了平滑展开动画
  - `hidePopup()`：重写的隐藏下拉列表方法，添加了平滑收起动画
  - `eventFilter(obj, event)`：事件过滤器，处理鼠标悬停、点击等事件

- `ComboBoxDelegate`：下拉菜单项的自定义渲染代理类，继承自`QStyledItemDelegate`
  - `__init__(parent=None)`：初始化代理类
    - `parent`：父组件
  - `paint(painter, option, index)`：自定义绘制下拉菜单项的方法
    - `painter`：QPainter对象，用于绘制
    - `option`：QStyleOptionViewItem对象，包含绘制选项
    - `index`：QModelIndex对象，表示要绘制的项目
  - `sizeHint(option, index)`：返回项目的理想大小
    - `option`：QStyleOptionViewItem对象，包含绘制选项
    - `index`：QModelIndex对象，表示项目
    - 返回值：QSize对象，表示项目的理想大小

**特性说明**：
- 扁平化设计，默认使用白色背景，浅灰色边框
- 鼠标悬停和点击时的背景和边框颜色变化动画效果
- 箭头旋转动画效果，打开下拉菜单时箭头旋转180度
- 下拉菜单展开和收起的动画效果，使用平滑的高度变化动画
- 下拉菜单项有圆角背景，悬停和选中时有颜色变化
- 悬停时的阴影效果，增强立体感和视觉反馈
- 箭头直接通过代码绘制，不依赖外部图标文件
- 完全可定制的外观，包括颜色、圆角、边框样式等
- 提供完善的事件处理，响应鼠标悬停、点击等事件
- 支持长文本省略显示，避免界面溢出
- 自动适配不同大小的显示区域
- 通过代理类实现下拉项的自定义绘制，统一风格
- 支持通过batch操作一次性设置多个样式属性

**使用方法**：
```python
from ui.components.custom_combobox import CustomComboBox
from PyQt6.QtWidgets import QVBoxLayout, QWidget

# 创建基本下拉菜单
combo = CustomComboBox()
combo.addItem("选项1")
combo.addItem("选项2")
combo.addItem("选项3")

# 添加到布局
layout = QVBoxLayout()
layout.addWidget(combo)

# 自定义样式
combo.customizeCustomComboBox(
    backgroundColor="#ffffff",        # 背景颜色
    backgroundHoverColor="#f5f5f5",   # 悬停时的背景颜色
    borderColor="#dddddd",            # 边框颜色
    hoverBorderColor="#3498db",       # 悬停时的边框颜色
    textColor="#333333",              # 文本颜色
    borderRadius=8,                   # 边框圆角半径
    dropdownBorderRadius=8,           # 下拉菜单边框圆角半径
    arrowColor="#888888",             # 箭头颜色
    arrowHoverColor="#3498db"         # 悬停时的箭头颜色
)

# 单独设置样式属性
combo.setBorderRadius(10)
combo.setTextColor("#444444")
combo.setDropShadowRadius(15)

# 设置动画参数
combo.setAnimationDuration(
    hover_duration=250,    # 悬停动画持续时间
    press_duration=150,    # 按下动画持续时间
    arrow_duration=350,    # 箭头旋转动画持续时间
    popup_duration=300     # 弹出动画持续时间
)

# 监听选择变化
combo.currentIndexChanged.connect(lambda index: print(f"选择了: {combo.itemText(index)}"))
```

**高级用法**：
```python
# 使用自定义图标
from PyQt6.QtCore import QSize

# 创建下拉菜单
custom_combo = CustomComboBox()

# 添加带图标的项目
from PyQt6.QtGui import QIcon
custom_combo.addItem(QIcon("path/to/icon1.png"), "选项1")
custom_combo.addItem(QIcon("path/to/icon2.png"), "选项2")

# 设置动画曲线
from PyQt6.QtCore import QEasingCurve
custom_combo.setAnimationEasingCurve(
    hover_curve=QEasingCurve.Type.OutQuad,
    press_curve=QEasingCurve.Type.OutQuad,
    arrow_curve=QEasingCurve.Type.OutBack,
    popup_curve=QEasingCurve.Type.OutExpo
)

# 应用自定义样式
custom_combo.customizeCustomComboBox(
    backgroundColor="#f0f0f0",
    backgroundHoverColor="#e0e0e0",
    backgroundPressColor="#d0d0d0",
    borderColor="#c0c0c0",
    hoverBorderColor="#3498db",
    pressBorderColor="#2980b9",
    textColor="#444444",
    textHoverColor="#222222",
    borderRadius=10,
    borderWidth=1,
    dropdownBorderRadius=8,
    arrowColor="#888888",
    arrowHoverColor="#3498db",
    arrowPressColor="#2980b9",
    dropShadowColor="#00000040",  # 带40%透明度的黑色
    dropShadowRadius=12
)
```

**实际应用示例**：
```python
# 在设置页面中使用下拉菜单选择主题
from ui.components.custom_combobox import CustomComboBox

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # 创建主题选择下拉菜单
        self.theme_label = QLabel("选择主题:")
        self.theme_combo = CustomComboBox()
        
        # 添加主题选项
        self.theme_combo.addItem("浅色主题")
        self.theme_combo.addItem("深色主题")
        self.theme_combo.addItem("蓝色主题")
        self.theme_combo.addItem("绿色主题")
        
        # 自定义样式
        self.theme_combo.customizeCustomComboBox(
            backgroundColor="#ffffff",
            borderColor="#dddddd",
            textColor="#333333",
            borderRadius=8
        )
        
        # 连接信号
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        
        # 添加到布局
        self.layout.addWidget(self.theme_label)
        self.layout.addWidget(self.theme_combo)
        self.layout.addStretch()
    
    def on_theme_changed(self, index):
        theme_name = self.theme_combo.itemText(index)
        print(f"主题已更改为: {theme_name}")
        # 在这里实现主题切换逻辑
```

##### 2.2.6 ui/components/input_field.py

**功能说明**：
提供具有动画效果和增强交互体验的输入框组件。该组件支持标签动画、焦点动画效果，以及友好的状态反馈。

**主要类和方法**：
- `AnimatedInputField`：动画输入框类
  - `__init__(self, parent=None, placeholder="", label=None, border_color=None, focus_color=None, error_color=None, success_color=None, text_color=None, label_color=None, border_radius=8)`：初始化输入框
  - `setText(self, text)`：设置输入框文本
  - `text(self)`：获取输入框文本
  - `clear(self)`：清空输入框
  - `setPlaceholder(self, placeholder)`：设置占位符文本
  - `setLabel(self, label)`：设置标签文本
  - `setValidator(self, validator)`：设置文本验证器
  - `setReadOnly(self, read_only)`：设置只读状态
  - `setDisabled(self, disabled)`：设置禁用状态

**特性**：
- **标签动画效果**：当输入框获得焦点或包含文本时，标签文本缩小并移动到顶部；失去焦点且没有文本时，标签恢复到中央位置
- **边框动画**：输入框获得或失去焦点时，边框颜色和宽度平滑过渡
- **阴影效果**：焦点状态时增强阴影效果，提供明确的视觉反馈
- **悬停动画**：鼠标悬停时平滑切换边框和背景颜色
- **状态管理**：包括普通、焦点、悬停、只读和禁用状态
- **自适应文本处理**：长文本自动截断并添加省略号
- **自定义样式支持**：可自定义边框颜色、焦点颜色、标签颜色等

**信号**：
- `textChanged`：文本变化信号
- `textEdited`：用户编辑文本信号（仅用户输入触发）
- `focusChanged`：焦点变化信号

**使用方法**：
```python
from ui.components.input_field import AnimatedInputField
from PyQt6.QtWidgets import QWidget, QVBoxLayout

# 创建Widget
widget = QWidget()
layout = QVBoxLayout(widget)

# 创建基本输入框
input_field1 = AnimatedInputField(placeholder="用户名")
layout.addWidget(input_field1)

# 创建自定义样式输入框
input_field2 = AnimatedInputField(
    placeholder="Email地址",
    label="电子邮箱",  # 自定义标签文本
    border_color="#D0D7DE",  # 边框颜色
    focus_color="#0969DA",   # 焦点状态颜色
    error_color="#FF6347",   # 错误状态颜色
    text_color="#24292F"     # 文本颜色
)
layout.addWidget(input_field2)

# 创建禁用状态输入框
input_field3 = AnimatedInputField(placeholder="禁用状态")
input_field3.setDisabled(True)
layout.addWidget(input_field3)

# 获取用户输入
def get_username():
    return input_field1.text()

# 监听文本变化
input_field1.textChanged.connect(lambda text: print(f"文本变化: {text}"))
```

**优化特点**：
1. 更紧凑的高度设计（默认32px）
2. 更小的内边距和圆角设计
3. 动态标签动画效果
4. 悬停和聚焦的平滑过渡动画
5. 优化的禁用状态样式
6. 精细的阴影效果
7. 自动文本截断处理

##### 2.2.7 ui/components/slider.py

**功能说明**：
自定义滑块组件，提供带有动画效果的滑块，支持水平和垂直方向，包含交互反馈和视觉特效。

**主要类**：
- `GesturePattern`：自定义SVG样式手势图案，用于滑块的滑块部分
  - `__init__(self, parent=None, size=24, primary_color=None)`：初始化手势图案
  - `set_value(self, value)`：设置要显示的值
  - `set_show_value(self, show)`：设置是否显示值
  - `update_animation(self)`：更新动画参数
  - `set_primary_color(self, color)`：设置主要颜色
  - `paintEvent(self, event)`：绘制自定义SVG样式手势图案

- `SliderTrack`：滑块轨道组件，绘制背景和进度
  - `__init__(self, parent=None, orientation=Qt.Orientation.Horizontal, color=None)`：初始化滑块轨道
  - `set_track_color(self, color)`：设置轨道颜色
  - `set_progress(self, progress)`：设置进度值 (0.0 到 1.0)
  - `get_progress(self)`：获取当前进度值
  - `enterEvent(self, event)`：处理鼠标进入事件，启动悬停动画
  - `leaveEvent(self, event)`：处理鼠标离开事件，启动悬停动画
  - `paintEvent(self, event)`：绘制轨道和进度，动态调整透明度和发光效果

- `AnimatedSlider`：动画滑块组件，整合手势图案和轨道组件
  - `__init__(self, orientation=Qt.Orientation.Horizontal, parent=None)`：初始化动画滑块
  - `setValue(self, value)`：设置滑块值
  - `value(self)`：获取当前值
  - `setMinimum(self, min_value)`：设置最小值
  - `minimum(self)`：获取最小值
  - `setMaximum(self, max_value)`：设置最大值
  - `maximum(self)`：获取最大值
  - `setRange(self, min_value, max_value)`：设置值范围
  - `setPrimaryColor(self, color)`：设置主题颜色
  - `setStep(self, step)`：设置步长
  - `step(self)`：获取步长

**主要信号**：
- `valueChanged`：值变化时发出，传递新值
- `sliderPressed`：滑块被按下时发出
- `sliderReleased`：滑块被释放时发出
- `sliderMoved`：滑块移动时发出，传递当前值

**特性说明**：
- 流畅动画：滑块移动、悬停和按下状态都有平滑过渡动画
- 互动反馈：鼠标悬停时轨道发光，滑块大小动态调整
- 自定义外观：支持设置颜色、大小和方向
- 优雅设计：轨道带有渐变和阴影效果，滑块使用动画SVG样式图案
- 悬停动画：鼠标经过时显示发光效果，提升用户体验
- 步长吸附：可设置值的步长，拖动时自动吸附到最近的步长值
- 双向支持：支持水平和垂直两种方向的滑块

**使用方法**：
```python
from ui.components.slider import AnimatedSlider
from PyQt6.QtCore import Qt

# 创建水平滑块
slider = AnimatedSlider(Qt.Orientation.Horizontal)
slider.setRange(0, 100)  # 设置范围
slider.setValue(50)      # 设置初始值
slider.setStep(5)        # 设置步长为5
slider.setPrimaryColor([52, 152, 219])  # 设置蓝色主题

# 连接信号
slider.valueChanged.connect(lambda value: print(f"值变化为: {value}"))
slider.sliderPressed.connect(lambda: print("滑块被按下"))
slider.sliderReleased.connect(lambda: print("滑块被释放"))

# 添加到布局
layout.addWidget(slider)

# 创建垂直滑块
v_slider = AnimatedSlider(Qt.Orientation.Vertical)
v_slider.setRange(0, 255)
v_slider.setValue(128)
v_slider.setPrimaryColor([231, 76, 60])  # 设置红色主题
layout.addWidget(v_slider)
```

##### 2.2.8 ui/components/color_picker.py

**功能说明**：
颜色选择器组件，提供预设颜色选择和自定义颜色对话框，支持RGB精确调色。

**主要类**：
- `ColorSwatch`：颜色样本组件，用于显示单一颜色
  - `__init__(self, color=[0, 120, 255], size=30, selected=False, parent=None)`：初始化颜色样本
  - `set_color(self, color)`：设置颜色
  - `set_selected(self, selected)`：设置选中状态
  - `paintEvent(self, event)`：绘制颜色样本，包括悬停和选中的视觉效果

- `RainbowColorButton`：彩虹颜色按钮，用于打开更多颜色选择
  - `__init__(self, size=30, parent=None)`：初始化彩虹按钮
  - `paintEvent(self, event)`：绘制彩虹色按钮和中心加号

- `ColorDialogPanel`：自定义颜色对话框面板
  - `__init__(self, initial_color=[52, 152, 219], parent=None)`：初始化颜色对话框
  - `initUI(self)`：初始化用户界面，创建调色板和RGB滑块
  - `updateColorDisplay(self)`：更新颜色显示
  - `onSliderColorChanged(self)`：处理滑块颜色变化
  - `onColorSelected(self, color)`：处理颜色样本选择
  - `setColor(self, color)`：设置当前颜色

- `AnimatedColorPicker`：动画色彩选择器，整合上述组件
  - `__init__(self, parent=None)`：初始化色彩选择器
  - `initUI(self)`：初始化用户界面，创建预设颜色样本
  - `open_color_dialog(self)`：打开颜色对话框
  - `on_color_selected(self, color)`：处理颜色选择事件
  - `set_color(self, color)`：设置当前颜色
  - `get_color(self)`：获取当前颜色

**主要信号**：
- `clicked` (ColorSwatch)：颜色样本被点击时发出，传递RGB颜色列表
- `clicked` (RainbowColorButton)：彩虹按钮被点击时发出
- `colorSelected` (ColorDialogPanel)：颜色对话框中选择确认颜色时发出
- `colorChanged` (AnimatedColorPicker)：颜色发生变化时发出，传递RGB颜色列表

**特性说明**：
- 预设颜色：提供16种精心设计的预设颜色供快速选择
- 动画交互：样本和按钮支持悬停和选中状态的动画效果
- 精确调色：通过RGB滑块实现精确的颜色调整
- 扩展调色板：包含40种扩展颜色样本，涵盖多种色系
- 圆形样本：使用圆形设计的颜色样本，带有渐变和阴影效果
- 彩虹按钮：直观的彩虹环形按钮，用于打开更多颜色选择
- 无缝集成：可轻松集成到任何需要色彩选择功能的界面

**使用方法**：
```python
from ui.components.color_picker import AnimatedColorPicker

# 创建色彩选择器
color_picker = AnimatedColorPicker()
color_picker.set_color([52, 152, 219])  # 设置初始颜色为蓝色

# 连接信号
def on_color_change(color):
    r, g, b = color[0], color[1], color[2]
    print(f"选择的颜色: RGB({r}, {g}, {b})")

color_picker.colorChanged.connect(on_color_change)

# 添加到布局
layout.addWidget(color_picker)

# 获取当前颜色
current_color = color_picker.get_color()  # 返回[r, g, b]列表
```

##### 2.2.9 ui/components/number_spinner.py

**功能说明**：
数字选择器组件，提供带有动画效果的数字输入和调整界面，支持直接输入和按钮/滚轮调整数值。

**主要类**：
- `SpinnerButton`：数字选择器按钮类
  - `__init__(self, button_type="add", size=24, primary_color=None, parent=None)`：初始化按钮
  - `set_primary_color(self, color)`：设置主要颜色
  - `paintEvent(self, event)`：绘制按钮

- `NumberValidator`：数字输入验证器
  - `__init__(self, min_value, max_value, step=1, parent=None)`：初始化验证器
  - `validate(self, input_text, pos)`：验证输入内容
  - `fixup(self, input_text)`：修正输入内容

- `AnimatedNumberSpinner`：动画数字选择器组件
  - `__init__(self, parent=None, min_value=0, max_value=100, step=1, value=0, primary_color=None)`：初始化数字选择器
  - `setValue(self, value)`：设置当前值
  - `value(self)`：获取当前值
  - `increment(self)`：增加数值
  - `decrement(self)`：减少数值
  - `setRange(self, min_value, max_value)`：设置数值范围
  - `setStep(self, step)`：设置步长
  - `setPrimaryColor(self, color)`：设置主题颜色

**主要信号**：
- `valueChanged`：值变化时发出，传递新值

**特性说明**：
- 动画按钮：加减按钮具有悬停和点击动画效果
- 数值动画：数值变化时有平滑过渡动画
- 多种输入方式：
  - 直接编辑输入框
  - 点击加减按钮
  - 鼠标滚轮调整
- 智能验证：验证输入文本，支持整数和小数，自动纠正无效输入
- 范围限制：自动限制数值在指定范围内
- 格式自适应：根据步长自动决定显示整数或小数(保留相应小数位)
- 自定义样式：可设置颜色、步长和范围

**使用方法**：
```python
from ui.components.number_spinner import AnimatedNumberSpinner
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel

# 创建布局和标签
layout = QVBoxLayout()
label = QLabel("数量:")
layout.addWidget(label)

# 创建整数数字选择器
int_spinner = AnimatedNumberSpinner(
    min_value=0, 
    max_value=100, 
    step=1,  # 整数步长
    value=50
)
int_spinner.valueChanged.connect(lambda v: print(f"值变化为: {v}"))
layout.addWidget(int_spinner)

# 创建小数数字选择器
float_spinner = AnimatedNumberSpinner(
    min_value=0, 
    max_value=5, 
    step=0.1,  # 小数步长
    value=2.5,
    primary_color=[231, 76, 60]  # 自定义颜色(红色)
)
layout.addWidget(float_spinner)

# 设置值
int_spinner.setValue(75)

# 获取当前值
current_value = float_spinner.value()
```

##### 2.2.10 ui/components/toast_notification.py

**功能说明**：消息提示组件，在窗口角落显示带有动画的通知提示，支持自动消失、鼠标悬停暂停计时、滚动长文本等功能，用于替代传统的弹出对话框。全局通知不会随页面切换而消失，确保重要信息始终可见。

**主要类和方法**：
- `ElegantToast`：高级消息提示类
  - `__init__(parent=None, message="", toast_type=INFO, duration=3000, icon=None, position='top-right', text_mode=TEXT_TRUNCATE)`：初始化提示组件
    - `parent`：父窗口（会被自动替换为主窗口，确保全局可见）
    - `message`：消息文本
    - `toast_type`：提示类型（INFO、SUCCESS、WARNING、ERROR）
    - `duration`：显示持续时间（毫秒）
    - `icon`：自定义图标（默认根据类型设置）
    - `position`：屏幕位置（'top-right', 'top-left', 'bottom-right', 'bottom-left'）
    - `text_mode`：文本显示模式（'truncate', 'scroll', 'wrap'）
  - `start_closing()`：开始关闭动画
  - `paintEvent(event)`：绘制通知提示效果

- `ToastManager`：管理多个通知提示的类
  - `show_toast(parent, message, toast_type, duration, ...)`：显示提示（会自动使用主窗口作为父级）
  - `arrange_toasts(position)`：排列多个提示，防止重叠
  - `get_parent_window(widget=None)`：获取主窗口作为Toast的父窗口，确保全局可见
  - `close_all()`：关闭所有活动提示
  - `update_positions_on_resize()`：窗口大小变化时更新通知位置

- 全局辅助函数
  - `show_info(parent, message, ...)`：显示信息类型提示
  - `show_success(parent, message, ...)`：显示成功类型提示
  - `show_warning(parent, message, ...)`：显示警告类型提示
  - `show_error(parent, message, ...)`：显示错误类型提示

**特性说明**：
- 渐变动画：显示和隐藏时具有平滑的渐变效果
- 自动隐藏：通知显示指定时间后自动隐藏
- 交互暂停：鼠标悬停时暂停自动隐藏计时
- 点击关闭：点击通知后立即关闭
- 多种样式：支持多种通知类型，每种类型有不同的颜色和图标
- 自适应布局：根据内容自动调整宽度和高度

#### 2.2.11 ui/components/dialog.py

**功能说明**：
对话框组件，提供多种类型的交互式对话框，支持动画效果和自定义内容。对话框包含标题、内容、自定义组件和操作按钮，设计符合UI标准，支持多种类型的消息提示和用户交互。

**主要类和方法**：
- `MessageDialog`：对话框类，继承自`QWidget`
  - `__init__(self, message_type="warning", content_widget=None, parent=None, show_title=True, show_buttons=True, title_text="消息提示", message="", custom_icon=None, custom_buttons=None, custom_button_colors=None, on_button_clicked=None)`：初始化对话框
    - `message_type`：对话框类型，可选值："warning"、"question"、"retry"、"timeout"、"custom"
    - `content_widget`：自定义内容组件
    - `parent`：父组件
    - `show_title`：是否显示标题栏
    - `show_buttons`：是否显示底部按钮
    - `title_text`：标题文本
    - `message`：消息内容
    - `custom_icon`：自定义图标
    - `custom_buttons`：自定义按钮列表
    - `custom_button_colors`：自定义按钮颜色
    - `on_button_clicked`：按钮点击回调函数
  - `setup_parent_blur(self)`：为父窗口设置模糊效果，使背景变暗
  - `remove_parent_blur(self)`：移除父窗口的模糊效果
  - `show_animated(self)`：带动画显示对话框
  - `close_animated(self)`：带动画关闭对话框
  - `handle_button_click(self, button_text)`：处理按钮点击事件
- `show_dialog(parent, message_type="warning", title_text=None, message="", content_widget=None, custom_icon=None, custom_buttons=None, custom_button_colors=None, callback=None)`：显示对话框的全局函数
- `connect_page_to_main_window(page)`：为页面提供统一的对话框连接辅助函数，确保页面可以通过信号触发主窗口显示对话框

**对话框类型说明**：
- `warning`：警告消息，提醒用户注意某些操作可能会带来的后果
  - 图标：⚠️
  - 默认按钮：确定、取消
  - 主题色：黄色
- `question`：确认消息，需要用户确认是否执行某个操作
  - 图标：❓
  - 默认按钮：是、否、取消
  - 主题色：绿色
- `retry`：重试消息，告知用户操作失败，但可以尝试再次执行
  - 图标：❌
  - 默认按钮：重试、取消
  - 主题色：红色
- `timeout`：超时消息，告知用户操作超时，需要采取措施
  - 图标：⚠️
  - 默认按钮：确定、取消
  - 主题色：黄色
- `custom`：自定义消息，开发者可以根据需要自定义消息内容、按钮和图标
  - 图标：⚙️
  - 默认按钮：确定、取消
  - 主题色：蓝色

**视觉和动画特性**：
- **平滑动画效果**：对话框打开和关闭时使用缩放和透明度动画，提供流畅的用户体验
- **背景模糊**：显示对话框时自动为父窗口应用模糊和半透明效果，使用户聚焦于对话框
- **自适应布局**：对话框大小根据内容自动调整，保持居中显示
- **圆角设计**：圆角设计，符合扁平化UI风格
- **阴影效果**：适当的阴影效果增强立体感，提高视觉层次
- **显示和关闭动画**：平滑的缩放和透明度过渡效果
- **背景覆盖层**：显示对话框时创建半透明覆盖层，阻止用户与主界面交互
- **等待用户操作**：对话框保持显示直到用户点击按钮或关闭图标

**使用方法**：
```python
from ui.components.dialog import show_dialog

# 显示警告对话框
def show_warning_dialog(self):
    show_dialog(
        parent=self,
        message_type="warning",
        title_text="操作警告",
        message="此操作可能会导致数据丢失，是否继续？",
        callback=self.handle_warning_result
    )

# 处理对话框结果
def handle_warning_result(self, button_text):
    if button_text == "确定":
        print("用户确认继续操作")
    else:
        print("用户取消操作")

# 显示带自定义内容的对话框
def show_custom_dialog(self):
    # 创建自定义内容组件
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.addWidget(QLabel("请选择一个选项："))
    combo = QComboBox()
    combo.addItems(["选项A", "选项B", "选项C"])
    layout.addWidget(combo)
    
    # 显示自定义对话框
    show_dialog(
        parent=self,
        message_type="custom",
        title_text="自定义对话框",
        message="",
        content_widget=content,
        custom_buttons=["确认选择", "取消"],
        callback=lambda btn: print(f"选择了: {combo.currentText() if btn == '确认选择' else '取消'}")
    )
```

**页面与主窗口对话框集成**：
```python
# 在页面类中
from PyQt6.QtCore import pyqtSignal

class MyPage(QWidget):
    # 定义信号
    request_dialog = pyqtSignal(str, str, str, object)  # message_type, title, message, callback
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("MyPage")
        # ... 其他初始化代码
    
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # 使用连接辅助函数
        from ui.components.dialog import connect_page_to_main_window
        connect_page_to_main_window(self)
    
    def show_confirm_dialog(self):
        """显示确认对话框"""
        self.request_dialog.emit(
            "question",
            "操作确认",
            "是否确定执行此操作？",
            self.handle_dialog_result
        )
    
    def handle_dialog_result(self, button_text):
        """处理对话框结果"""
        if button_text == "是":
            self.logger.info("用户确认操作")
            # 执行操作
        else:
            self.logger.info("用户取消操作")
```

**主窗口实现对话框处理**：
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... 其他初始化代码
    
    def show_global_dialog(self, message_type, title_text, message, callback):
        """显示全局对话框"""
        from ui.components.dialog import show_dialog
        show_dialog(
            parent=self,
            message_type=message_type,
            title_text=title_text,
            message=message,
            callback=callback
        )
```

#### 2.2.12 ui/components/hotkey_input.py

**功能说明**：
快捷键输入组件，用于捕获和显示用户输入的键盘快捷键组合，包括虚拟键盘支持和多平台兼容性。

**主要类和方法**：
- `HotkeyInput`：快捷键输入组件类
  - `__init__(self, parent=None, placeholder="请输入快捷键", enable_virtual_keyboard=True)`：初始化快捷键输入组件
  - `set_hotkey(self, hotkey)`：设置快捷键值并更新显示
  - `get_hotkey(self)`：获取当前的快捷键值
  - `clear(self)`：清除当前输入的快捷键
  - `_setup_ui(self)`：设置UI界面，包括输入框、虚拟键盘按钮和整体布局
  - `_on_key_pressed(self, key, modifiers)`：处理按键按下事件，更新当前快捷键值
  - `_show_virtual_keyboard(self)`：显示虚拟键盘对话框
  - `_virtual_key_selected(self, key_name)`：处理从虚拟键盘选择的按键
  - `_highlight_key_by_name(self, key_name)`：在虚拟键盘中高亮显示对应的按键
  - `_get_key_name(self, key)`：获取按键对应的显示名称

- `VirtualKeyboardDialog`：虚拟键盘对话框类
  - `__init__(self, parent=None)`：初始化虚拟键盘对话框
  - `setup_ui(self)`：设置虚拟键盘界面，包括各种功能键和字母数字键
  - `update_modifier_state(self, key, state)`：更新修饰键（如Ctrl、Shift等）的状态
  - `on_key_selected(self, key_name)`：处理按键选择事件，发出信号通知选择了某个按键

**使用方法**：
```python
# 创建快捷键输入组件
hotkey_input = HotkeyInput(parent_widget, "请输入快捷键")

# 设置初始快捷键值
hotkey_input.set_hotkey("Ctrl+C")

# 获取当前设置的快捷键
current_hotkey = hotkey_input.get_hotkey()

# 连接快捷键变更信号
hotkey_input.hotkeyChanged.connect(on_hotkey_changed)

# 清除快捷键
hotkey_input.clear()
```

**特性说明**：
- 实时捕获：实时捕获键盘按键，支持组合键
- 格式化显示：将按键组合格式化为易读的形式
- 虚拟键盘：内置虚拟键盘对话框，支持鼠标点击选择按键
- 视觉反馈：按键按下时提供视觉高亮反馈
- 波纹动画：点击输入框时显示水波纹动画效果
- 焦点效果：获取/失去焦点时的动画过渡效果
- 占位符文本：未设置快捷键时显示引导性占位符文本
- 跨平台支持：兼容Windows、macOS和Linux系统

#### 2.2.13 ui/components/checkbox.py

**功能说明**：
自定义动画复选框组件，提供现代化设计的复选框，带有平滑过渡动画效果。支持自定义主题颜色、大小和动画速度。

**主要类和方法**：
- `AnimatedCheckBox`：动画复选框类
  - `__init__(self, text="", parent=None, primary_color=None, check_color=None)`：初始化动画复选框
  - `_setup_animations(self)`：设置动画效果
  - `_setup_ui(self)`：设置UI样式和属性
  - `_handle_state_changed(self, state)`：处理复选框状态变化
  - `enterEvent(self, event)`：鼠标进入事件
  - `leaveEvent(self, event)`：鼠标离开事件
  - `paintEvent(self, event)`：绘制复选框
  - `set_primary_color(self, color)`：设置主题颜色
  - `set_check_color(self, color)`：设置勾选标记颜色
  - `set_box_size(self, size)`：设置复选框大小
  - `set_animation_duration(self, duration)`：设置动画持续时间

**特性说明**：
- 平滑动画：选中和取消选中状态之间有流畅的过渡动画
- 悬停效果：鼠标悬停时显示轻微扩大效果
- 自定义主题：支持设置复选框主题颜色和勾选标记颜色
- 渐进勾选：勾选标记绘制过程动画化，先绘制第一段再绘制第二段
- 现代圆角：复选框使用圆角设计，更符合现代UI审美
- 自定义大小：支持调整复选框大小
- 自定义动画速度：可设置动画持续时间

**信号**：
- `colorChanged`：主题颜色更改信号
- `stateChanged`：复选框状态更改信号（继承自QCheckBox）

**使用方法**：
```python
from ui.components.checkbox import AnimatedCheckBox

# 创建默认样式复选框
checkbox = AnimatedCheckBox("默认样式复选框")

# 创建自定义颜色复选框
green_checkbox = AnimatedCheckBox("绿色主题复选框", primary_color=[46, 204, 113])

# 设置复选框属性
checkbox.set_box_size(24)                    # 设置复选框大小
checkbox.set_primary_color([231, 76, 60])    # 设置红色主题
checkbox.set_check_color([255, 255, 255])    # 设置白色勾选标记
checkbox.set_animation_duration(300)         # 设置动画持续时间为300毫秒

# 获取和设置复选框状态
is_checked = checkbox.isChecked()            # 获取复选框状态
checkbox.setChecked(True)                    # 设置复选框为选中状态

# 监听状态变化
def on_state_changed(state):
    print(f"复选框状态变化为: {'选中' if state == 2 else '未选中'}")

checkbox.stateChanged.connect(on_state_changed)
```

**优化特点**：
1. 平滑的勾选动画，勾选标记分两段绘制
2. 自定义颜色主题支持，可匹配应用程序整体风格
3. 鼠标悬停效果增强用户体验
4. 独特的绘制方式，支持透明度渐变
5. 内置日志记录功能，便于调试
6. 异常处理机制，提高组件稳定性

#### 2.2.14 ui/components/animated_tooltip.py

**功能说明**：美化版悬浮提示组件，提供平滑动画效果和主题样式，可以替代常规的QWidget.setToolTip，呈现更丰富的视觉效果。

**主要类和方法**：
- `AnimatedToolTip`：悬浮提示类
  - `__init__(self, parent=None, show_delay=1000, direction=DIRECTION_AUTO, primary_color=None, text_color=None, border_radius=6, hide_delay=200, fade_duration=150, min_width=80, max_width=300)`：初始化悬浮提示
    - `parent`：父组件
    - `show_delay`：显示延迟时间(毫秒)
    - `direction`：提示弹出方向，支持自动、上、下、左、右
    - `primary_color`：主题颜色
    - `text_color`：文本颜色
    - `border_radius`：边框圆角半径
  - `setText(self, text)`：设置提示文本
  - `setShowDelay(self, delay_ms)`：设置显示延迟时间
  - `setDirection(self, direction)`：设置提示弹出方向
  - `setPrimaryColor(self, color)`：设置主题颜色
  - `setTextColor(self, color)`：设置文本颜色
  - `attachTo(self, widget, text)`：将提示附加到指定控件
  - `showTooltip(self)`：显示提示
  - `hideTooltip(self, force=False)`：隐藏提示

- `wrap_widget_with_tooltip(widget, text, tooltip=None, show_delay=1000, direction=AnimatedToolTip.DIRECTION_AUTO, primary_color=None, text_color=None, border_radius=6)`：为控件添加美化版提示
- `set_tooltip(widget, text, show_delay=1000, direction=AnimatedToolTip.DIRECTION_AUTO, primary_color=None, text_color=None, border_radius=6)`：使用全局单例为控件设置美化版提示

**特性说明**：
- 平滑动画：显示和隐藏时具有淡入淡出动画效果
- 方向选择：支持自动、上、下、左、右五种弹出方向
- 主题定制：可自定义主题颜色、文本颜色和边框圆角
- 智能位置：自动调整位置避免超出屏幕边界
- 全局事件处理：支持全局鼠标跟踪和键盘事件(如ESC键关闭所有提示)
- 单例模式：可复用提示实例提高效率

**使用方法**：
```python
from ui.components.animated_tooltip import wrap_widget_with_tooltip, set_tooltip
from PyQt6.QtWidgets import QPushButton

# 方法一：创建独立提示实例
button = QPushButton("测试按钮")
wrap_widget_with_tooltip(button, "这是一个按钮提示", primary_color=[52, 152, 219])

# 方法二：使用全局单例提示
label = QLabel("这是一个标签")
set_tooltip(label, "这是一个标签提示", direction=AnimatedToolTip.DIRECTION_TOP)
```

#### 2.2.15 ui/components/system_tray.py

**功能说明**：
系统托盘图标组件，为应用程序提供常驻系统托盘功能，支持自定义右键菜单、单击/双击/中键点击操作，并具有现代化的视觉样式。允许用户在关闭主窗口后继续使用程序功能。

**主要类和方法**：
- `SystemTrayIcon`：系统托盘图标类
  - `__init__(self, app_icon=None, parent=None)`：初始化系统托盘图标
  - `_create_menu(self)`：创建右键菜单，设置样式和菜单项
  - `_setup_event_handlers(self)`：设置托盘图标事件处理
  - `_on_tray_activated(self, reason)`：处理托盘图标激活事件（单击、双击等）
  - `_handle_single_click(self)`：处理延迟的单击事件（防抖处理）
  - `_on_toggle_action(self)`：处理"开始/停止监听"菜单项的触发
  - `_show_about(self)`：显示关于信息
  - `update_drawing_state(self, is_active)`：更新绘制状态，同步更新菜单项和工具提示

- `get_system_tray(parent=None)`：单例函数，获取或创建系统托盘图标实例

**自定义信号**：
- `toggle_drawing_signal`：切换绘制状态信号
- `show_settings_signal`：显示设置页面信号
- `show_window_signal`：显示主窗口信号
- `exit_app_signal`：退出应用程序信号

**特性说明**：
- 单例模式：使用全局单例模式确保只创建一个托盘图标实例
- 美观菜单：自定义样式的右键菜单，包含圆角、悬停效果和平滑过渡
- 多样交互：支持多种鼠标操作
  - 左键单击：切换开始/停止监听状态
  - 双击：显示主窗口
  - 中键点击：显示设置页面
  - 右键点击：显示自定义菜单
- 状态同步：托盘图标状态与应用程序绘制状态保持同步
- 防抖处理：智能区分单击和双击操作，避免冲突
- 菜单结构：组织合理的菜单结构，包括基本操作、分隔线和退出选项
- 工具提示：根据状态显示不同的工具提示文本
- "关于"功能：集成版本信息显示

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

**特性说明**：
- **全屏透明覆盖层**：使用透明窗口覆盖整个屏幕，不影响用户与其他应用程序的交互
- **性能优化**：
  - 区域更新：仅更新实际变化的区域，减少重绘开销
  - 基于时间的动画：淡出效果使用基于时间的计算，确保在不同性能设备上体验一致
  - 图形硬件加速：支持OpenGL渲染加速，提升绘制性能
  - 预创建画笔：减少QPainter创建/销毁次数
  - 批量绘制：减少绘制调用次数
- **贝塞尔曲线压力模拟**：基于鼠标移动速度使用贝塞尔曲线模型计算模拟压力值
- **全局鼠标监听**：使用pynput库实现全局鼠标事件监听
- **异常处理**：提供全面的错误处理和日志记录
- **可定制外观**：支持自定义笔尖颜色和粗细
- **智能淡出效果**：笔画完成后自动淡出，视觉效果平滑
- **方向识别集成**：与笔画分析器和手势执行器无缝集成
- **防止残留问题**：特殊处理机制确保新笔画开始时清除旧笔画的残留效果

**使用方法**：
```python
from core.drawer import DrawingManager

# 创建绘制管理器
drawer = DrawingManager()

# 开始绘制功能
drawer.start()  # 此时可以使用鼠标右键进行绘制

# 更新设置参数
drawer.update_settings()

# 获取最后一次绘制的方向
direction = drawer.get_last_direction()
print(f"最后绘制的方向: {direction}")

# 停止绘制功能
drawer.stop()
```

**绘制流程**：
1. 用户按下鼠标右键开始绘制
2. 鼠标移动时捕获轨迹并绘制可见线条
3. 用户释放鼠标右键停止绘制
4. 系统分析轨迹识别方向
5. 根据识别的方向执行匹配的手势动作
6. 绘制的线条缓慢淡出，提供视觉反馈

**技术实现**：
- 使用Qt的QWidget和QPainter实现绘制功能
- 使用透明窗口作为绘制覆盖层
- 线条粗细根据模拟压力值动态调整
- 线条颜色可通过设置自定义
- 通过pynput库监听全局鼠标事件
- 使用信号槽机制在线程间安全通信
- 使用QTimer实现定时更新和动画效果
- 淡出效果使用基于时间的透明度计算

#### 3.2 core/stroke_analyzer.py

**功能说明**：笔画分析模块，负责分析用户绘制的笔画轨迹，识别方向变化和绘制趋势。

**主要类和方法**：
- `StrokeAnalyzer`：笔画分析器
  - `analyze_direction(self, points)`：分析一系列点的方向变化
  - `get_direction_description(self, direction_str)`：将方向字符串转换为人类可读的描述
  - `_determine_direction(self, dx, dy)`：根据位移确定基本方向

**方向常量**：
- `UP`、`DOWN`、`LEFT`、`RIGHT`等八个基本方向

**使用方法**：
```python
from core.stroke_analyzer import StrokeAnalyzer

# 创建分析器
analyzer = StrokeAnalyzer()

# 分析点序列
points = [(100, 100, 0.5, 1.0, 1), (150, 100, 0.5, 1.1, 1), (200, 150, 0.5, 1.2, 1)]
direction, stats = analyzer.analyze_direction(points)
print(f"方向: {direction}")

# 获取方向描述
description = analyzer.get_direction_description(direction)
print(f"描述: {description}")
```

#### 3.3 core/gesture_executor.py

**功能说明**：手势执行模块，负责根据识别的手势方向序列执行对应的操作。

**主要类和方法**：
- `GestureExecutor`：手势执行器
  - `__init__(self)`：初始化手势执行器，加载键盘控制器和手势库
  - `get_instance(cls)`：获取手势执行器的单例实例
  - `execute_gesture(self, direction)`：执行与方向匹配的手势动作，经过优化简化
  - `_execute_shortcut(self, shortcut_str)`：执行键盘快捷键，简化实现，提高稳定性

**特性说明**：
- 单例模式设计，确保全局只有一个执行器实例
- 支持多种操作类型，包括快捷键执行
- 优化的错误处理机制
- 精简的日志记录
- 多线程键盘操作，避免阻塞UI线程
- 提高代码可读性和维护性

**使用方法**：
```python
from core.gesture_executor import get_gesture_executor

# 获取执行器实例
executor = get_gesture_executor()

# 执行手势
result = executor.execute_gesture("上右下")
print(f"执行结果: {'成功' if result else '失败'}")
```

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

**主要类和方法**：
- `Logger`：日志工具类
  - `__init__(self, module_name="GestroKey")`：初始化日志记录器
  - `setup_logger(self)`：设置日志记录器，经过优化简化
  - `debug(self, message)`、`info(self, message)`等：不同级别的日志记录方法
- `get_logger(module_name="GestroKey")`：获取一个命名的日志记录器

**特性说明**：
- 支持文件和控制台双重输出
- 自动处理日志目录和文件创建
- 适当的错误处理和回退机制
- 不同级别的日志控制
- 模块化设计，便于在不同组件中使用
- 简化的初始化流程

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

### 4. 应用程序集成

#### 4.1 应用程序架构

GestroKey采用模块化的架构设计，各个模块之间通过明确的接口进行交互，降低耦合度，提高代码的可维护性和可扩展性。

**核心架构组件**：
1. **主程序模块(main.py)**：提供应用程序入口点，初始化UI和功能模块
2. **核心功能模块(core/)**：实现手势识别、分析和执行的核心功能
3. **用户界面模块(ui/)**：提供用户交互界面，包括控制台、设置和手势管理
4. **UI组件模块(ui/components/)**：提供自定义的界面组件，如动画按钮、导航菜单等
5. **资源管理(assets/)**：管理应用程序资源，如图标和配置文件
6. **版本管理(version.py)**：管理应用程序版本信息和构建参数
7. **系统托盘集成**：提供后台运行能力，支持各种鼠标交互和状态显示

**数据流向**：
1. 用户通过鼠标右键在屏幕上绘制手势
2. 绘制模块(drawer.py)捕获鼠标事件并记录轨迹点
3. 笔画分析模块(stroke_analyzer.py)分析轨迹点序列，识别出方向变化
4. 手势执行模块(gesture_executor.py)查找匹配的手势并执行相应动作
5. UI模块显示状态变化和结果，并允许用户配置设置和管理手势库
6. 系统托盘图标反映程序当前状态，提供在后台控制应用的访问点

**通信机制**：
- 使用Qt的信号槽机制实现模块间的松耦合通信
- 使用事件驱动设计，降低模块间的直接依赖
- 使用单例模式管理共享资源，如日志记录器、设置管理器和手势库
- 通过自定义信号实现异步操作和UI更新
- 通过系统托盘组件实现应用程序在后台运行时的状态管理和操作接口

**界面架构**：
- 采用侧边导航菜单(SideNavigationMenu)设计，实现页面切换
- 支持页面分组，将页面组织为主要功能组和设置组
- 导航菜单支持垂直与水平两种布局模式
- 所有UI组件使用自定义设计，确保统一的视觉风格
- 页面切换采用平滑动画效果，提升用户体验
- 系统托盘提供多样化的交互方式，即使在主窗口关闭时也能操作核心功能

#### 4.2 程序流程

##### 4.2.1 启动流程

1. **程序初始化**
   - 启动PyQt应用程序(QApplication)
   - 设置高DPI支持，适应高分辨率显示器
   - 创建主窗口(GestroKeyApp)
   - 加载应用图标和资源

2. **全局资源初始化**
   - 初始化日志系统(logger.py)
   - 初始化设置管理器(settings.py)
   - 初始化手势库管理器(gestures.py)
   - 加载默认设置和手势库

3. **UI初始化**
   - 创建中央部件和主布局
   - 初始化侧边导航菜单(SideNavigationMenu)
   - 创建控制台页面(ConsolePage)、设置页面(SettingsPage)和手势管理页面(GesturesPage)
   - 将页面添加到导航菜单中，设置图标和分组
   - 设置底部状态栏和退出按钮，显示版本信息

4. **显示主窗口**
   - 应用窗口样式和布局
   - 设置默认选择的页面(控制台)
   - 显示主窗口
   - 进入应用程序主循环

##### 4.2.2 绘制流程

1. **启动绘制功能**
   - 用户点击控制台页面上的"开始绘制"按钮
   - 创建DrawingManager实例(如果尚未创建)
   - 启动鼠标监听，准备捕获右键事件
   - 创建透明覆盖层，用于绘制手势轨迹
   - 从设置加载笔尖粗细和颜色参数

2. **绘制手势**
   - 用户按住鼠标右键进行绘制
   - 透明覆盖层实时显示绘制轨迹
   - 记录绘制点的坐标、压力和时间信息
   - 绘制过程中不影响其他应用程序的正常操作

3. **手势识别**
   - 用户释放鼠标右键结束绘制
   - StrokeAnalyzer分析绘制轨迹，识别方向序列
   - 轨迹逐渐淡出，提供视觉反馈
   - 查询手势库，寻找匹配的手势

4. **手势执行**
   - 找到匹配手势后，获取对应的动作类型和值
   - GestureExecutor执行相应的动作(如快捷键)
   - 记录执行结果和相关信息
   - 准备接收下一次绘制

5. **停止绘制**
   - 用户点击"停止绘制"按钮
   - 停止鼠标监听
   - 关闭透明覆盖层
   - 释放相关资源并更新UI状态

##### 4.2.3 设置管理流程

1. **查看设置**
   - 用户通过侧边导航菜单切换到设置页面
   - 加载并显示当前设置，如笔尖粗细和颜色
   - 设置预览组件实时显示当前配置效果

2. **修改设置**
   - 用户调整笔尖粗细(使用自定义NumberSpinner组件)
   - 用户点击颜色按钮，使用AnimatedColorPicker选择新颜色
   - PenPreviewWidget实时显示预览效果
   - 设置更改只保存在内存中，不会立即应用到绘制功能

3. **保存设置**
   - 用户点击"保存设置"按钮
   - 系统检查设置是否有实际变化（智能检测）
   - 如果没有实际变化，使用Toast通知提示用户无需保存
   - 如果有实际变化，设置保存到配置文件中
   - 同时将设置应用到绘制管理器，若绘制功能正在运行，变更将立即生效
   - 使用Toast通知提示用户保存成功

4. **重置设置**
   - 用户点击"重置设置"按钮
   - 系统显示确认对话框，征求用户确认
   - 用户确认后，从default_settings.json加载默认设置
   - 更新UI显示和预览
   - 自动保存重置后的设置并立即应用到绘制功能
   - 使用Toast通知提示用户重置成功

##### 4.2.4 手势管理流程

1. **查看手势**
   - 用户通过侧边导航菜单切换到手势管理页面
   - 加载并显示当前手势库，以自定义卡片(CardWidget)形式展示每个手势
   - 按照ID顺序排列手势卡片，ID越小排在越前面
   - 使用自定义滚动区域组件显示手势卡片列表

2. **编辑手势**
   - 用户点击左侧手势卡片，卡片显示选中状态动画
   - 右侧编辑区域显示选中手势的详细信息
   - 用户可以使用自定义输入组件修改手势名称、方向和动作
   - 对于快捷键动作，用户可以使用HotkeyInput组件输入快捷键
   - 修改立即应用于内存中的手势对象，并实时更新左侧卡片显示
   - 这些修改不会影响实际的手势识别和执行，只有在保存后才会生效

3. **添加手势**
   - 用户填写右侧编辑区域的内容
   - 点击"添加新手势"按钮
   - 系统自动分配新的手势ID（当前最大ID+1）
   - 新手势添加到左侧卡片列表中，带有添加动画效果
   - 使用Toast通知提示用户添加成功

4. **删除手势**
   - 用户选中要删除的手势卡片
   - 点击"删除手势"按钮
   - 系统显示确认对话框，征求用户确认
   - 用户确认后，删除选中的手势，并自动重排后续手势的ID，保持ID连续性
   - 左侧卡片列表更新，移除已删除的手势，带有淡出动画效果
   - 使用Toast通知提示用户删除成功

5. **重置手势库**
   - 用户点击"重置手势库"按钮
   - 系统显示确认对话框，征求用户确认
   - 用户确认后，从default_gestures.json加载默认手势库
   - 重置所有手势的ID，按照默认顺序排列
   - 左侧卡片列表更新，显示默认手势库
   - 使用Toast通知提示用户重置成功
   - 自动刷新手势执行器，确保使用最新的手势库

6. **保存手势库**
   - 用户点击"保存更改"按钮
   - 系统检查手势库是否有实际变化（智能检测）
   - 如果没有实际变化，使用Toast通知提示用户无需保存
   - 如果有实际变化，手势库保存到配置文件中
   - 更新内存中的已保存手势对象，使其反映最新的保存状态
   - 保存后的手势库会立即用于手势识别和执行
   - 自动刷新手势执行器，确保使用最新的已保存手势库
   - 使用Toast通知提示用户保存成功

#### 4.3 使用场景与示例

##### 4.3.1 基础使用场景

**场景1: 使用复制粘贴手势**
1. 用户启动GestroKey并点击"开始绘制"
2. 用户选择要复制的文本或对象
3. 用户按住鼠标右键，绘制"右-下"手势（代表"复制"）
4. 系统执行Ctrl+C快捷键，复制选中内容
5. 用户移动到目标位置
6. 用户按住鼠标右键，绘制"下-右"手势（代表"粘贴"）
7. 系统执行Ctrl+V快捷键，粘贴内容

**场景2: 浏览网页时的导航**
1. 用户在浏览网页时启动GestroKey
2. 用户按住鼠标右键，绘制"左"手势（代表"后退"）
3. 系统执行Alt+Left快捷键，浏览器返回上一页
4. 用户按住鼠标右键，绘制"右"手势（代表"前进"）
5. 系统执行Alt+Right快捷键，浏览器前进到下一页

**场景3: 文档编辑中的撤销和重做**
1. 用户在文档编辑器中工作
2. 用户进行了一些编辑后想撤销
3. 用户按住鼠标右键，绘制"左-上"手势（代表"撤销"）
4. 系统执行Ctrl+Z快捷键，撤销最后的编辑
5. 用户改变主意，想恢复被撤销的编辑
6. 用户按住鼠标右键，绘制"右-上"手势（代表"重做"）
7. 系统执行Ctrl+Y快捷键，恢复被撤销的编辑

##### 4.3.2 高级使用场景

**场景4: 自定义手势**
1. 用户切换到手势管理选项卡
2. 用户点击右侧编辑区域，输入新手势信息：
   - 名称: "截图"
   - 方向: "右-下-左"
   - 动作类型: "执行快捷键"
   - 动作值: "win+shift+s"
3. 用户点击"添加新手势"按钮
4. 用户切换回控制台选项卡，点击"开始绘制"
5. 用户按住鼠标右键，绘制"右-下-左"手势
6. 系统执行Win+Shift+S快捷键，打开Windows截图工具

**场景5: 修改现有手势**
1. 用户切换到手势管理选项卡
2. 用户点击"复制"手势卡片
3. 在右侧编辑区域，用户将方向从"右-下"改为"圆形"(右-下-左-上)
4. 修改立即应用，左侧卡片更新
5. 用户点击"保存更改"按钮
6. 用户现在可以使用新的"圆形"手势执行复制操作

**场景6: 自定义笔尖样式**
1. 用户切换到设置选项卡
2. 用户将笔尖粗细从默认的3像素增加到8像素
3. 用户点击颜色按钮，选择亮红色(RGB: 255, 50, 50)
4. PenPreviewWidget显示粗红色笔尖的预览效果
5. 用户点击"保存设置"按钮
6. 用户切换回控制台选项卡，点击"开始绘制"
7. 用户按住鼠标右键绘制手势，轨迹显示为粗红色线条

##### 4.3.3 工作流程示例

**场景7: 设计师工作流程**
1. 设计师配置以下手势：
   - "Z"手势 → Ctrl+Z (撤销)
   - "圆形"手势 → Ctrl+S (保存)
   - "上-右"手势 → 切换图层 (Ctrl+])
   - "上-左"手势 → 切换图层 (Ctrl+[)
2. 设计师在Photoshop中工作时启动GestroKey
3. 使用预定义的手势执行常用操作

**场景8: 程序员编码流程**
1. 程序员配置以下手势：
   - "右-下"手势 → Ctrl+C (复制)
   - "下-右"手势 → Ctrl+V (粘贴)
   - "L"形手势 → Ctrl+F (查找)
   - "右-左"手势 → Ctrl+Tab (切换文件)
   - "上-下"手势 → F5 (运行/调试)
2. 程序员在IDE中编码时启动GestroKey
3. 使用手势执行常用操作

#### 4.4 扩展开发指南

##### 4.4.1 添加新的手势动作类型

要添加新的手势动作类型（如启动程序、执行脚本等），需要修改以下文件：

1. **ui/gestures/gestures_tab.py**
   - 在`initUI`方法中的`self.action_type_combo`添加新的动作类型选项
   - 在`onFormChanged`方法中为新动作类型添加适当的表单验证逻辑

2. **core/gesture_executor.py**
   - 修改`execute_gesture`方法，添加对新动作类型的处理
   - 为新动作类型创建专用的执行方法（如`_execute_program`）

3. **ui/gestures/default_gestures.json**
   - 可以添加使用新动作类型的默认手势示例

##### 4.4.2 修改手势识别算法

要修改手势识别算法以支持更复杂的模式，需要修改核心的笔画分析模块：

1. **core/stroke_analyzer.py**
   - 修改`analyze_stroke`方法以实现新的识别逻辑
   - 可能需要添加新的辅助方法来处理复杂的模式识别
   - 如需支持弧形或圆形等手势，需要修改`determine_direction`方法

2. **ui/gestures/gestures.py**
   - 修改`get_gesture_by_direction`方法以适应新的方向序列格式
   - 可能需要更新手势匹配逻辑以支持模糊匹配或概率匹配

##### 4.4.3 添加新的UI组件

要添加新的UI组件，遵循以下步骤：

1. 在`ui/components/`目录下创建新的组件文件
2. 遵循现有组件的代码结构和命名约定
3. 确保新组件与现有样式保持一致
4. 在适当的模块中导入并使用新组件
5. 更新README.md，添加对新组件的文档

##### 4.4.4 添加设置选项

要添加新的设置选项，需要修改以下文件：

1. **ui/settings/default_settings.json**
   - 添加新设置的默认值

2. **ui/settings/settings.py**
   - 确保`Settings`类能够正确处理新的设置项

3. **ui/settings/settings_tab.py**
   - 在UI中添加新设置的控件
   - 添加适当的验证和保存逻辑

### 5. 总结

本文档详细介绍了GestroKey项目的源代码结构和功能模块，包括：

1. **主程序模块**：提供应用程序入口点和主窗口界面，使用侧边导航菜单组织页面内容
2. **用户界面模块**：实现控制台、设置和手势管理页面，提供直观的用户操作界面
3. **UI组件模块**：提供按钮、卡片、滚动条、颜色选择器等自定义组件，实现统一的动画和视觉效果
4. **核心功能模块**：实现手势绘制、分析和执行的核心功能
5. **应用程序集成**：描述架构设计、程序流程和使用场景

GestroKey通过精心设计的UI界面和强大的核心功能，为用户提供了以下特点：

1. **用户体验优先**：
   - 所有UI操作都有平滑的动画过渡效果
   - 使用Toast通知和对话框提供清晰的操作反馈
   - 精细调整的颜色和布局，确保视觉舒适性
   - 高度可定制的绘制参数，适应不同用户习惯

2. **高效的手势管理**：
   - 手势库采用ID管理机制，保证数据一致性
   - 智能的手势匹配算法，提高识别准确率
   - 支持自定义手势及动作关联，扩展应用场景
   - 自动化的数据持久化和同步机制

3. **稳健的技术实现**：
   - 完善的异常处理和日志记录机制
   - 单例模式管理全局资源，优化内存使用
   - 模块化和松耦合设计，便于维护和扩展
   - 多线程处理关键操作，保证UI响应流畅

4. **现代化的界面组件**：
   - 自定义的AnimatedButton取代标准按钮，提供悬停和点击动画
   - CardWidget组件实现统一的卡片视觉效果和交互行为
   - SideNavigationMenu提供分组和动画支持的导航界面
   - 自定义滚动区域和滚动条，优化滚动体验
   - AnimatedColorPicker提供直观的颜色选择界面

通过合理的模块化设计和松耦合架构，GestroKey不仅实现了易用的手势控制功能，还提供了流畅的用户体验和扩展性强的开发框架。未来的扩展方向包括更多的手势动作类型、更复杂的手势识别算法和更丰富的用户界面自定义选项。

如需更详细的开发和使用信息，请参考各模块的代码注释和类文档。