# GestroKey 源代码目录说明

GestroKey是一款功能强大的手势控制工具，允许用户通过鼠标绘制简单手势来执行各种操作（如快捷键、启动程序等）。本工具的核心特性包括全局鼠标手势识别、智能方向分析、手势库管理以及自定义UI组件，适用于日常办公、创意设计和编程开发等场景，显著提升工作效率。

本文档详细介绍了GestroKey项目`src`目录下各文件和文件夹的功能及使用方法。

## 目录索引

- [1. 主程序模块](#1-主程序模块)
  - [1.1 main.py](#11-mainpy)
  - [1.2 version.py](#12-versionpy)
- [2. 用户界面模块](#2-用户界面模块-ui)
  - [2.1 界面UI模块](#21-界面ui模块)
  - [2.2 UI组件模块](#22-ui组件模块)
    - [2.2.1 按钮组件](#221-uicomponentsbutton.py)
    - [2.2.2 卡片组件](#222-uicomponentscard.py)
    - [2.2.3 滚动条组件](#223-uicomponentsscrollbar.py)
    - [2.2.4 侧边选项卡](#224-uicomponentsside_tab.py)
    - [2.2.5 下拉菜单](#225-uicomponentscombobox)
    - [2.2.6 动画堆栈组件](#226-uicomponentsanimated_stacked_widget.py)
    - [2.2.7 输入框组件](#227-uicomponentsinput_field.py)
- [3. 核心功能模块](#3-核心功能模块)
  - [3.1 drawer.py](#31-coredrawerpy)
  - [3.2 stroke_analyzer.py](#32-corestroke_analyzerpy)
  - [3.3 gesture_executor.py](#33-coregesture_executorpy)
  - [3.4 system_monitor.py](#34-coresystem_monitorpy)
  - [3.5 logger.py](#35-coreloggerpy)
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
│   ├── components/          # UI组件模块
│   │   ├── button.py        # 自定义动画按钮组件
│   │   ├── card.py          # 自定义卡片组件
│   │   ├── scrollbar.py     # 自定义滚动条和滚动区域组件
│   │   ├── side_tab.py      # 左侧选项卡组件
│   │   ├── input_field.py   # 自定义动画输入框组件
│   │   ├── combobox/        # 下拉菜单组件
│   │   │       ├── icons/       # 下拉菜单图标文件
│   │   │       └── qcustomcombobox.py  # 自定义下拉菜单实现
│   │   ├── animated_stacked_widget.py  # 动画堆栈组件
│   │   ├── settings/            # 设置相关界面
│   │   │   ├── settings_tab.py  # 设置选项卡
│   │   │   ├── settings.py      # 设置管理模块
│   │   │   └── default_settings.json # 默认设置定义（JSON格式）
│   │   └── gestures/            # 手势管理相关界面
│   │   ├── gestures_tab.py  # 手势管理选项卡
│   │   ├── gestures.py      # 手势库管理模块
│   └── └── default_gestures.json # 默认手势库定义（JSON格式）
├── assets/                  # 资源文件目录
│   └── images/              # 图像资源
│       ├── icon.svg         # 应用图标
│       ├── console.svg      # 控制台选项卡图标
│       ├── settings.svg     # 设置选项卡图标
│       └── gestures.svg     # 手势管理选项卡图标
├── version.py               # 版本信息模块
└── main.py                  # 主程序入口
```

## 详细模块说明

### 1. 主程序模块

#### 1.1 main.py

**功能说明**：程序的主入口文件，提供带有选项卡的图形用户界面，包含控制台、设置界面和手势管理界面。

**主要类和方法**：
- `GestroKeyApp`：主窗口类，继承自`QMainWindow`
  - `__init__(self)`：初始化应用程序主窗口，设置日志记录器和全局资源
  - `init_global_resources(self)`：初始化设置管理器和手势库管理器等全局资源
  - `initUI(self)`：初始化用户界面，设置窗口属性、创建选项卡和底部状态栏
  - `_select_initial_tab(self)`：选择初始选项卡（默认为控制台选项卡）
  - `onTabChanged(self, index)`：处理选项卡切换事件
  - `resizeEvent(self, event)`：处理窗口尺寸变化事件
  - `closeEvent(self, event)`：处理窗口关闭事件，检查未保存的设置和手势库更改

**使用方法**：
```python
# 直接运行该文件启动应用程序
python src/main.py

# 或从其他Python代码中导入并创建实例
from main import GestroKeyApp
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = GestroKeyApp()
sys.exit(app.exec_())
```

**GUI选项卡**：
- 控制台选项卡：提供绘制功能的开启和停止控制，以及系统资源监测
- 设置选项卡：提供应用程序设置的配置，包括笔尖粗细和笔尖颜色设置
- 手势管理选项卡：提供手势库的管理界面，可添加、编辑、删除手势

**主窗口功能**：
- 高DPI缩放支持，适应高分辨率屏幕
- 自适应布局，在窗口尺寸变化时保持良好的界面结构
- 自动加载应用图标和选项卡图标
- 底部状态栏显示退出按钮和版本信息
- 窗口关闭时提示保存未保存的更改
- 优雅的异常处理，确保用户操作不会导致程序崩溃

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
- `get_version_string()`：获取格式化的版本字符串，如"GestroKey v2.0.0"
- `get_full_version_info()`：获取完整的版本信息，返回包含所有版本相关信息的字典

**使用方法**：
```python
from version import VERSION, APP_NAME, get_version_string, get_full_version_info

# 获取版本号
current_version = VERSION  # 如："2.0.0"

# 获取应用名称
app_name = APP_NAME  # 返回："GestroKey"

# 获取格式化的版本字符串
version_string = get_version_string()  # 返回："GestroKey v2.0.0"

# 获取完整的版本信息
version_info = get_full_version_info()  # 返回包含所有版本信息的字典
```

**版本管理说明**：
- 更新应用程序版本时，只需修改`VERSION`和相关变量
- 构建日期`BUILD_DATE`自动设置为当前日期

### 2. 用户界面模块 (UI)

#### 2.1 界面UI模块

##### 2.1.1 主应用窗口 (ui/main_window.py)

**功能说明**：
应用程序的主窗口，负责整合各个UI组件和功能模块。

**主要类和方法**：
- `GestroKeyApp`：主应用窗口类
  - `__init__(self)`：初始化主窗口
  - `initUI(self)`：初始化UI组件和布局
  - `setup_tabs(self)`：设置选项卡
  - `setup_status_bar(self)`：设置状态栏
  - `setup_exit_button(self)`：设置退出按钮
  - `closeEvent(self, event)`：处理窗口关闭事件
  - `update_status(self, message, timeout=0)`：更新状态栏消息
  - `check_for_updates(self)`：检查应用更新

**组件布局**：
- 中心区域：SideTabWidget，包含以下选项卡：
  - 控制台选项卡（ConsoleTab）
  - 设置选项卡（SettingsTab）
  - 手势管理选项卡（GesturesTab）
- 底部：状态栏，显示应用状态和系统资源信息
- 右下角：退出按钮

**窗口特性**：
- 固定尺寸：窗口大小固定，不可调整
- 半透明样式：窗口及控件采用现代半透明效果
- 圆角边框：窗口和控件采用统一的圆角设计
- 无标题栏：自定义标题栏，集成系统图标
- 快捷键支持：支持常用快捷键，如Esc关闭应用

**特性说明**：
- 一体化设计：将所有功能集成在单一窗口中
- 选项卡导航：通过侧边选项卡快速切换功能模块
- 状态反馈：底部状态栏提供操作反馈和系统信息
- 资源监控：实时显示系统资源使用情况
- 优雅退出：确保应用退出时释放所有资源
- 配置保存：退出时自动保存用户配置

**使用方法**：
```python
# 创建并运行应用程序
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import GestroKeyApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # 创建并显示主窗口
    window = GestroKeyApp()
    window.show()
    
    # 进入应用程序主循环
    sys.exit(app.exec_())
```

##### 2.1.2 控制台选项卡 (ui/console/console_tab.py)

**功能说明**：
控制台界面，应用程序的主要交互界面，提供启动/停止绘制功能，显示操作日志。

**主要类和方法**：
- `ConsoleTab`：控制台选项卡类
  - `__init__(self, parent=None)`：初始化控制台选项卡
  - `initUI(self)`：初始化UI组件和布局
  - `setup_log_viewer(self)`：设置日志查看器
  - `setup_control_buttons(self)`：设置控制按钮
  - `on_start_drawing(self)`：处理开始绘制按钮点击事件
  - `on_stop_drawing(self)`：处理停止绘制按钮点击事件
  - `add_log_entry(self, message, level="info")`：添加日志条目
  - `clear_log(self)`：清空日志查看器

**组件布局**：
- 顶部：控制按钮区域，包含开始/停止绘制按钮
- 中部：日志查看器，显示操作日志
- 底部：清除日志按钮和占位区域

**交互信号**：
- `drawing_started`：开始绘制时发出
- `drawing_stopped`：停止绘制时发出
- `log_cleared`：清除日志时发出

**日志级别**：
- `info`：一般信息，使用默认颜色
- `success`：成功信息，显示为绿色
- `warning`：警告信息，显示为黄色
- `error`：错误信息，显示为红色
- `debug`：调试信息，显示为灰色

**特性说明**：
- 直观控制：提供明确的开始/停止绘制按钮
- 实时日志：显示实时操作和系统日志
- 色彩区分：不同级别的日志使用不同颜色
- 状态反馈：按钮状态反映当前绘制状态
- 自动滚动：日志超出视图时自动滚动
- 交互反馈：操作时提供视觉和文本反馈

**使用方法**：
```python
# 在主窗口中添加控制台选项卡
from ui.console.console_tab import ConsoleTab

# 创建主窗口
main_window = QMainWindow()
side_tab = SideTabWidget(main_window)

# 创建并添加控制台选项卡
console_tab = ConsoleTab()
side_tab.add_tab("控制台", console_tab, QIcon(":/icons/console.png"))

# 连接信号到槽函数
console_tab.drawing_started.connect(lambda: print("开始绘制"))
console_tab.drawing_stopped.connect(lambda: print("停止绘制"))

# 添加不同级别的日志
console_tab.add_log_entry("应用程序已启动", "info")
console_tab.add_log_entry("成功连接到系统", "success")
console_tab.add_log_entry("配置文件缺失，使用默认设置", "warning")
console_tab.add_log_entry("无法访问资源文件", "error")
console_tab.add_log_entry("调试信息：初始化完成", "debug")

# 设置主窗口
main_window.setCentralWidget(side_tab)
main_window.show()
```

##### 2.1.3 手势管理模块

###### 2.1.3.1 手势库 (ui/gestures/gestures.py)

**功能说明**：
手势库管理模块，负责保存和加载用户手势库，提供添加、删除、修改手势的功能。

**主要类和方法**：
- `GestureLibrary`：手势库类
  - `__init__(self, gestures_file=None)`：初始化手势库
    - `gestures_file`：手势库文件路径，默认为None，会使用默认路径
  - `load_gestures(self)`：从配置文件加载手势库
  - `save_gestures(self)`：保存手势库到配置文件
  - `add_gesture(self, name, direction, action_type, action_value)`：添加新手势
    - `name`：手势名称
    - `direction`：方向序列字符串
    - `action_type`：动作类型，如"shortcut"
    - `action_value`：动作值，如"ctrl+c"
    - 返回值：新手势的ID
  - `delete_gesture(self, gesture_id)`：删除指定ID的手势
    - `gesture_id`：要删除的手势ID
    - 返回值：操作是否成功
  - `update_gesture(self, gesture_id, name=None, direction=None, action_type=None, action_value=None)`：更新手势信息
    - `gesture_id`：要更新的手势ID
    - 其他参数：要更新的手势属性，不提供则保持原值
    - 返回值：更新后的手势信息
  - `get_gesture(self, gesture_id)`：获取指定ID的手势信息
    - `gesture_id`：手势ID
    - 返回值：手势信息字典
  - `get_all_gestures(self)`：获取所有手势信息
    - 返回值：手势字典，键为ID，值为手势信息
  - `find_gesture_by_direction(self, direction)`：通过方向序列查找匹配的手势
    - `direction`：方向序列字符串
    - 返回值：匹配的手势信息，未找到则返回None
  - `reset_gesture_library(self)`：重置手势库为默认设置
    - 返回值：重置后的手势库

**手势数据结构**：
```json
{
  "id": 1,
  "name": "复制",
  "direction": "右-下",
  "action": {
    "type": "shortcut",
    "value": "ctrl+c"
  }
}
```

**特性说明**：
- 自动初始化：首次运行时自动创建默认手势库
- 配置持久化：所有更改自动保存到配置文件
- ID管理：自动分配和管理手势ID，确保连续性
- 手势匹配：提供精确的方向序列匹配功能
- 格式验证：验证手势数据格式，确保数据一致性
- 错误处理：提供详细的错误日志和恢复机制

**使用方法**：
```python
# 创建手势库实例
gesture_library = GestureLibrary()

# 获取所有手势
all_gestures = gesture_library.get_all_gestures()
print(f"当前有 {len(all_gestures)} 个手势")

# 添加新手势
new_id = gesture_library.add_gesture(
    name="截图",
    direction="右-下-左",
    action_type="shortcut",
    action_value="win+shift+s"
)
print(f"添加了新手势，ID: {new_id}")

# 更新手势
updated_gesture = gesture_library.update_gesture(
    gesture_id=new_id,
    name="屏幕截图",
    action_value="win+shift+s"
)
print(f"更新后的手势: {updated_gesture}")

# 查找匹配手势
direction = "右-下"
matched_gesture = gesture_library.find_gesture_by_direction(direction)
if matched_gesture:
    print(f"匹配到手势: {matched_gesture['name']}")
    print(f"执行动作: {matched_gesture['action']['type']} - {matched_gesture['action']['value']}")
else:
    print(f"未找到匹配的手势: {direction}")

# 删除手势
result = gesture_library.delete_gesture(new_id)
print(f"删除结果: {'成功' if result else '失败'}")

# 重置手势库
gesture_library.reset_gesture_library()
print("手势库已重置为默认设置")
```

###### 2.1.3.2 手势选项卡 (ui/gestures/gestures_tab.py)

**功能说明**：
手势管理界面，为用户提供可视化的手势添加、编辑和删除功能。

**主要类和方法**：
- `GestureCard`：手势卡片组件类
  - `__init__(self, gesture_id, name, direction, action, parent=None)`：初始化手势卡片
  - `update_info(self, name, direction, action)`：更新卡片显示的信息
  - `set_selected(self, selected)`：设置卡片的选中状态
  - `mousePressEvent(self, event)`：鼠标点击事件处理，用于选中卡片

- `GesturesTab`：手势管理选项卡类
  - `__init__(self, parent=None)`：初始化手势管理选项卡
  - `initUI(self)`：初始化UI组件和布局
  - `load_gestures(self)`：加载并显示手势库中的所有手势
  - `clear_editor(self)`：清空右侧编辑区域
  - `fill_editor(self, gesture_info)`：使用指定手势信息填充编辑区域
  - `on_gesture_card_clicked(self, gesture_id)`：处理手势卡片被点击的事件
  - `on_add_gesture(self)`：处理添加手势按钮点击事件
  - `on_delete_gesture(self)`：处理删除手势按钮点击事件
  - `on_update_gesture(self)`：处理更新手势按钮点击事件
  - `on_reset_library(self)`：处理重置手势库按钮点击事件
  - `on_save_changes(self)`：处理保存更改按钮点击事件

**组件布局**：
- 左侧：滚动区域，显示手势卡片列表
- 右侧：编辑区域，包含以下字段：
  - 手势名称输入框（使用AnimatedInputField组件）
  - 方向选择区域：
    - 方向显示框（使用AnimatedInputField组件，只读模式）
    - 九宫格按钮组，八个方向按钮（上、下、左、右、左上、右上、左下、右下）和一个中央删除按钮
  - 动作类型下拉菜单（使用QCustomComboBox组件）
  - 动作值输入框（使用AnimatedInputField组件）
  - 操作按钮组（使用AnimatedButton组件）

**交互信号**：
- `gesture_selected`：当用户选择手势卡片时发出
- `gesture_added`：当添加新手势时发出
- `gesture_deleted`：当删除手势时发出
- `gesture_updated`：当更新手势时发出
- `library_reset`：当重置手势库时发出
- `changes_saved`：当保存更改时发出

**特性说明**：
- 可视化管理：通过卡片形式直观展示所有手势
- 交互式方向编辑：通过直观的方向按钮组实现更简单的方向序列输入
- 现代化表单：使用自定义动画输入框组件（AnimatedInputField）提供更好的用户体验
- 实时预览：编辑时实时更新卡片显示
- 方向验证：自动防止连续添加相同方向，保持手势逻辑合理性
- 直观操作：提供清晰的添加、删除和编辑功能
- 验证机制：自动验证输入数据格式
- 排序显示：按照ID顺序排列手势卡片
- 状态反馈：操作后提供明确的状态反馈

**使用方法**：
```python
# 在主窗口中添加手势管理选项卡
from ui.gestures.gestures_tab import GesturesTab

# 创建主窗口
main_window = QMainWindow()
side_tab = SideTabWidget(main_window)

# 创建并添加手势管理选项卡
gestures_tab = GesturesTab()
side_tab.add_tab("手势", gestures_tab, QIcon(":/icons/gesture.png"))

# 连接信号到槽函数
gestures_tab.changes_saved.connect(lambda: print("手势库已保存"))
gestures_tab.gesture_added.connect(lambda id: print(f"添加了新手势：ID {id}"))
gestures_tab.gesture_deleted.connect(lambda id: print(f"删除了手势：ID {id}"))

# 设置主窗口
main_window.setCentralWidget(side_tab)
main_window.show()
```

**方向选择界面示例**：
```python
# 手势方向选择界面示例
from ui.gestures.gestures_tab import GesturesTab
from PyQt5.QtWidgets import QApplication
from ui.components.input_field import AnimatedInputField

# 创建手势管理选项卡
app = QApplication([])
gestures_tab = GesturesTab()

# 选择一个手势卡片
# ...

# 使用方向按钮添加方向序列
gestures_tab.add_direction("上")
gestures_tab.add_direction("右")
gestures_tab.add_direction("下")

# 查看当前方向序列
current_direction = gestures_tab.direction_text.text()
print(f"当前方向序列: {current_direction}")  # 输出: 当前方向序列: 上-右-下

# 删除最后一个方向
gestures_tab.remove_last_direction()
print(f"删除后的方向序列: {gestures_tab.direction_text.text()}")  # 输出: 删除后的方向序列: 上-右

# 访问其他输入字段
name_input = gestures_tab.name_input           # AnimatedInputField组件
action_value_input = gestures_tab.action_value_input  # AnimatedInputField组件

# 设置输入字段值
name_input.setText("新手势名称")
action_value_input.setText("ctrl+c")

# 读取输入字段值
print(f"手势名称: {name_input.text()}")
print(f"动作值: {action_value_input.text()}")

# 显示并运行应用程序
gestures_tab.show()
app.exec_()
```

##### 2.1.4 设置选项卡 (ui/settings/settings_tab.py)

**功能说明**：
设置界面，允许用户自定义笔迹样式和应用行为，提供直观的设置选项。

**主要类和方法**：
- `PenPreviewWidget`：笔迹预览组件类
  - `__init__(self, parent=None)`：初始化预览组件
  - `set_pen_width(self, width)`：设置笔迹宽度
  - `set_pen_color(self, color)`：设置笔迹颜色
  - `paintEvent(self, event)`：绘制预览效果

- `SettingsTab`：设置选项卡类
  - `__init__(self, parent=None)`：初始化设置选项卡
  - `initUI(self)`：初始化UI组件和布局
  - `setup_pen_settings(self)`：设置笔迹设置区域
  - `setup_behavior_settings(self)`：设置行为设置区域
  - `setup_action_buttons(self)`：设置操作按钮区域
  - `load_settings(self)`：加载当前设置
  - `on_pen_width_changed(self, value)`：处理笔迹宽度变化
  - `on_color_button_clicked(self)`：处理颜色按钮点击
  - `on_save_settings(self)`：处理保存设置按钮点击
  - `on_reset_settings(self)`：处理重置设置按钮点击

**组件布局**：
- 顶部：笔迹设置区域
  - 笔迹宽度调节器（QSpinBox）
  - 笔迹颜色选择按钮
  - 笔迹预览组件
- 中部：行为设置区域
  - 绘制透明度调节器（QSlider）
  - 绘制消退时间调节器（QSpinBox）
  - 其他行为选项
- 底部：操作按钮区域
  - 保存设置按钮
  - 重置设置按钮

**设置参数**：
- `pen_width`：笔迹宽度，范围1-10像素
- `pen_color`：笔迹颜色，RGB格式数组
- `overlay_opacity`：绘制层透明度，范围0.1-1.0
- `fade_duration`：绘制消退时间，单位毫秒
- `auto_save`：是否自动保存设置

**交互信号**：
- `settings_saved`：保存设置时发出
- `settings_reset`：重置设置时发出
- `pen_width_changed`：笔迹宽度变化时发出
- `pen_color_changed`：笔迹颜色变化时发出

**特性说明**：
- 实时预览：设置变更时实时更新预览效果
- 直观调节：通过滑块和微调框直观调整参数
- 颜色选择器：集成标准颜色对话框
- 参数验证：自动验证输入值的有效性
- 默认值恢复：一键恢复默认设置
- 自动应用：设置更改后可以立即应用

**使用方法**：
```python
# 在主窗口中添加设置选项卡
from ui.settings.settings_tab import SettingsTab

# 创建主窗口
main_window = QMainWindow()
side_tab = SideTabWidget(main_window)

# 创建并添加设置选项卡
settings_tab = SettingsTab()
side_tab.add_tab("设置", settings_tab, QIcon(":/icons/settings.png"))

# 连接信号到槽函数
settings_tab.settings_saved.connect(lambda: print("设置已保存"))
settings_tab.settings_reset.connect(lambda: print("设置已重置"))
settings_tab.pen_width_changed.connect(lambda w: print(f"笔迹宽度: {w}"))

# 设置主窗口
main_window.setCentralWidget(side_tab)
main_window.show()
```

#### 2.2 UI组件模块

##### 2.2.1 ui/components/button.py

**功能说明**：自定义动画按钮组件，提供美观的、带有动画效果的按钮，可以轻松集成到任何界面。

**主要类和方法**：
- `AnimatedButton`：动画按钮类，继承自`QPushButton`
  - `__init__(text, parent=None, icon=None, primary_color=None, hover_color=None, text_color=None, border_radius=None, min_width=None, min_height=None)`：初始化按钮，支持多种自定义参数
    - `text`：按钮文本
    - `parent`：父窗口组件
    - `icon`：按钮图标，可以是QIcon对象或图标文件路径
    - `primary_color`：按钮主色调，RGB格式的数组，如[41, 128, 185]
    - `hover_color`：按钮悬停色调，RGB格式的数组，如[52, 152, 219]
    - `text_color`：按钮文本颜色，RGB格式的数组，如[255, 255, 255]
    - `border_radius`：按钮边框圆角半径，整数值（像素）
    - `min_width`：按钮最小宽度，整数值（像素）
    - `min_height`：按钮最小高度，整数值（像素）
  - `set_primary_color(color)`：设置按钮主色调
    - `color`：RGB格式的数组，如[41, 128, 185]
  - `set_hover_color(color)`：设置按钮悬停色调
    - `color`：RGB格式的数组，如[52, 152, 219]
  - `set_text_color(color)`：设置按钮文本颜色
    - `color`：RGB格式的数组，如[255, 255, 255]
  - `set_border_radius(radius)`：设置按钮边框圆角半径
    - `radius`：整数值（像素）
  - `setEnabled(enabled)`：重写的设置按钮可用状态方法，提供禁用状态的视觉反馈
    - `enabled`：布尔值，True表示启用，False表示禁用
  - `enterEvent(event)`：处理鼠标进入事件，触发悬停动画效果
  - `leaveEvent(event)`：处理鼠标离开事件，触发恢复动画效果
  - `mousePressEvent(event)`：处理鼠标按下事件，触发按下动画效果
  - `mouseReleaseEvent(event)`：处理鼠标释放事件，触发释放动画效果
  - `_start_hover_animation(is_hover)`：内部方法，启动悬停/离开动画
  - `_start_press_animation(is_pressed)`：内部方法，启动按下/释放动画
  - `_update_colors()`：内部方法，根据主色调计算悬停色调和禁用色调

**特性说明**：
- 精美的扁平化设计，主题色为蓝色系，符合现代UI设计趋势
- 鼠标悬停时文字轻微上浮和放大的动画效果，提升交互体验
- 按下时文字下沉和缩小的动画效果，与按钮主体动画保持一致，提供立体感反馈
- 平滑的鼠标离开过渡动画，避免视觉上的生硬跳变
- 支持自定义颜色、图标、文本颜色和圆角半径，可适应各种界面风格
- 自动计算悬停色调，如未指定则基于主色调生成更亮的颜色，保持色彩统一性
- 当主色调通过set_primary_color方法变更时，悬停色调会自动更新以保持一致的视觉效果
- 完美支持动态颜色切换，如控制台的"开始绘制"(蓝色)和"停止绘制"(红色)按钮
- 阴影和高光效果，提供现代感视觉体验，增强按钮立体感
- 支持禁用状态，灰色外观设计，禁用时无动画效果，鼠标指针变为普通箭头
- 可直接运行文件查看示例效果，便于单独调试
- 已应用于整个应用程序的界面按钮，提供统一的视觉风格

**应用场景**：
- 主窗口的退出按钮
- 控制台选项卡的开始和停止绘制按钮，均使用主题蓝色保持统一风格
- 设置选项卡的保存和重置设置按钮
- 手势管理选项卡的添加、删除和保存手势按钮

**使用方法**：
```python
from ui.components.button import AnimatedButton
from PyQt5.QtWidgets import QVBoxLayout, QWidget

# 创建基本按钮（使用默认样式）
button = AnimatedButton("按钮文本")

# 创建自定义按钮（设置所有可选参数）
custom_button = AnimatedButton(
    text="自定义按钮", 
    primary_color=[41, 128, 185],  # 扁平化蓝色
    hover_color=[52, 152, 219],    # 悬停时的颜色（可选，不提供时会自动基于主色计算）
    text_color=[255, 255, 255],    # 白色文本
    icon="path/to/icon.png",       # 设置图标
    border_radius=12,              # 设置圆角半径
    min_width=120,                 # 最小宽度
    min_height=40                  # 最小高度
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
from PyQt5.QtGui import QIcon
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
    primary_color=[248, 249, 250], # 几乎白色背景
    text_color=[52, 58, 64],       # 深灰色文本
    border_radius=0                # 无圆角
)

# 创建高对比度按钮
high_contrast_button = AnimatedButton(
    text="高对比度",
    primary_color=[52, 58, 64],    # 深灰色背景 
    text_color=[248, 249, 250],    # 接近白色文本
    border_radius=20               # 大圆角半径
)
```

##### 2.2.2 ui/components/card.py

**功能说明**：卡片组件，提供精美的、有交互效果的卡片容器，可以容纳其他组件，适合展示结构化信息。

**主要类和方法**：
- `CardWidget`：卡片组件类，继承自`QWidget`
  - `__init__(parent=None, primary_color=None, hover_color=None, selected_color=None, text_color=None, border_radius=None, min_width=None, min_height=None, title=None)`：初始化卡片，支持多种自定义参数
    - `parent`：父窗口组件
    - `primary_color`：卡片主色调，RGB格式的数组，默认为淡蓝色[240, 248, 255]
    - `hover_color`：卡片悬停色调，RGB格式的数组，默认自动基于主色调生成
    - `selected_color`：卡片选中状态颜色，RGB格式的数组，默认为更淡的主题蓝色[85, 170, 225]
    - `text_color`：卡片文本颜色，RGB格式的数组，默认为深灰色[70, 70, 70]
    - `border_radius`：卡片边框圆角半径，整数值（像素），默认为8
    - `min_width`：卡片最小宽度，整数值（像素），默认为150
    - `min_height`：卡片最小高度，整数值（像素），默认为100
    - `title`：卡片标题，字符串
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
    - `color`：RGB格式的数组，如[240, 248, 255]
  - `set_hover_color(color)`：设置卡片悬停色调
    - `color`：RGB格式的数组，如[220, 240, 250]
  - `set_selected_color(color)`：设置卡片选中状态的颜色
    - `color`：RGB格式的数组，如[85, 170, 225]
  - `set_text_color(color)`：设置卡片文本颜色
    - `color`：RGB格式的数组，如[70, 70, 70]
  - `set_border_radius(radius)`：设置卡片边框圆角半径
    - `radius`：整数值（像素）
  - `enterEvent(event)`：处理鼠标进入事件，触发悬停效果
  - `leaveEvent(event)`：处理鼠标离开事件，恢复正常效果
  - `mousePressEvent(event)`：处理鼠标按下事件，更新样式和触发点击信号
  - `mouseReleaseEvent(event)`：处理鼠标释放事件，恢复样式

**特性说明**：
- 精美的扁平化设计，默认使用淡蓝色系主题，视觉效果柔和
- 支持鼠标悬停、点击的动画效果，增强用户交互体验
- 具有选中状态，默认使用更淡的主题蓝色作为选中状态颜色，视觉效果更柔和
- 动态阴影效果，悬停时阴影增强，增加立体感，鼠标离开时平滑过渡回原始状态
- 适当的内边距设计，确保内容不会覆盖卡片边框，保持美观
- 内容随卡片一起应用动画效果，提供更连贯的交互体验
- 支持添加标题和内容组件，适合展示结构化信息
- 完全可定制的外观，包括颜色、圆角、阴影等，可适应各种界面风格
- 发射点击信号，便于处理用户交互，可以连接到自定义槽函数
- 可直接运行文件查看示例效果，便于单独调试
- 适合用于展示列表项、信息卡片、设置面板等场景

**使用方法**：
```python
from ui.components.card import CardWidget
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# 创建基本卡片
card = CardWidget(title="卡片标题")

# 添加内容
content_label = QLabel("这是卡片内容")
content_label.setAlignment(Qt.AlignCenter)
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
    min_height=150                  # 最小高度
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

**功能说明**：自定义滚动条和滚动区域组件，提供精美的、带有动画效果的滚动体验，替代标准的QScrollBar和QScrollArea。

**主要类和方法**：
- `AnimatedScrollBar`：自定义滚动条类，继承自`QScrollBar`
  - `__init__(orientation=Qt.Vertical, parent=None)`：初始化滚动条
    - `orientation`：滚动条方向，可以是Qt.Vertical（垂直）或Qt.Horizontal（水平）
    - `parent`：父窗口组件
  - `enterEvent(event)`：处理鼠标进入事件，触发透明度增加动画和展开动画
  - `leaveEvent(event)`：处理鼠标离开事件，触发透明度减少动画和延迟收缩
  - `_startCollapseAnimation()`：开始收缩动画，将滚动条收缩为细线
  - `_startExpandAnimation()`：开始展开动画，将滚动条恢复为正常宽度
  - `_cancelCollapseTimer()`：取消收缩延时计时器
  - `mousePressEvent(event)`：处理鼠标按下事件，更新滚动条样式并取消收缩
  - `mouseReleaseEvent(event)`：处理鼠标释放事件，恢复滚动条样式并启动收缩延时
  - `wheelEvent(event)`：实现平滑滚动效果，优化滚轮体验并重置收缩计时器
  - `set_color_alpha(alpha)`：设置滚动条颜色的透明度，用于动画效果
    - `alpha`：透明度值，范围0-255
  - `set_current_width(width)`：设置滚动条当前宽度，用于折叠/展开动画
    - `width`：宽度值，单位像素
  - `update_style()`：更新滚动条样式表，应用当前设置的颜色和宽度
  - `resizeEvent(event)`：处理尺寸变化事件，更新滚动条样式

- `AnimatedScrollArea`：自定义滚动区域类，继承自`QScrollArea`
  - `__init__(parent=None)`：初始化滚动区域，集成自定义滚动条
    - `parent`：父窗口组件
  - `eventFilter(obj, event)`：事件过滤器，拦截滚轮事件以实现平滑滚动
  - `_handleWheelEvent(event)`：处理滚轮事件，实现丝滑的动画滚动效果
  - `setVerticalScrollBarPolicy(policy)`：设置并记录垂直滚动条显示策略
    - `policy`：滚动条策略，如Qt.ScrollBarAsNeeded
  - `setHorizontalScrollBarPolicy(policy)`：设置并记录水平滚动条显示策略
    - `policy`：滚动条策略，如Qt.ScrollBarAsNeeded
  - `resizeEvent(event)`：处理尺寸变化事件，更新滚动区域内容和滚动条
  - `set_animation_duration(duration)`：设置滚动动画持续时间
    - `duration`：动画持续时间，单位毫秒
  - `set_animation_curve(curve)`：设置滚动动画曲线
    - `curve`：QEasingCurve对象，如QEasingCurve.OutCubic

**特性说明**：
- 精美的扁平化设计，使用应用程序主题蓝色保持风格一致
- **默认以折叠状态显示**：滚动条初始化时即以折叠状态（细线）显示，最大程度节省界面空间
- **自动折叠功能**：鼠标离开滚动条区域后，滚动条会在短暂延迟后平滑收缩为细小的线条，节省界面空间
- **高效滚动响应**：优化的滚动参数，提供更大的滚动步长，便于快速浏览长内容
- **丝滑平滑滚动**：滚动内容时实现平滑渐变过渡，而非传统的瞬间跳转，提供更好的视觉体验
- 滚动条宽度自适应，收缩和展开时有平滑过渡动画，视觉效果流畅
- 圆角滑块设计，现代感强，视觉效果优雅，符合扁平化设计风格
- 透明度动画效果，鼠标悬停时变为完全不透明，离开时恢复半透明，提高视觉体验
- 无边框设计，隐藏了传统滚动条的箭头和槽轨道，界面更为简洁美观
- 自动适应垂直和水平方向，提供一致的视觉体验，代码复用率高
- 动画使用缓出曲线(OutCubic)，提供自然的减速效果，模拟物理世界的惯性
- 滑块最小长度限制，确保在内容较多时仍能轻松操作，提高可用性
- 智能延迟系统，防止频繁使用时的折叠/展开抖动，体验更为流畅
- 交互优化，滚动或点击时自动展开，使用完毕后自动收缩，用户体验佳
- 滚动区域无缝集成自定义滚动条，使用方式与标准QScrollArea一致，降低学习成本
- 可直接运行文件查看示例效果，便于单独调试和演示
- 详细的日志记录功能，记录滚动条状态变化，便于调试和问题排查

**使用方法**：
```python
from ui.components.scrollbar import AnimatedScrollBar, AnimatedScrollArea
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

# 方法1：使用AnimatedScrollArea（推荐，提供完整功能）
scroll_area = AnimatedScrollArea()
scroll_area.setFrameShape(AnimatedScrollArea.NoFrame)  # 移除边框
scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

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

# 自定义滚动动画（可选）
scroll_area.set_animation_duration(300)  # 设置动画持续时间为300毫秒
scroll_area.set_animation_curve(QEasingCurve.OutQuint)  # 设置动画曲线为OutQuint

# 添加到界面布局
layout = QVBoxLayout()
layout.addWidget(scroll_area)
main_widget.setLayout(layout)

# 方法2：单独使用AnimatedScrollBar（高级用法，需手动设置）
standard_scroll_area = QScrollArea()
custom_scroll_bar = AnimatedScrollBar(Qt.Vertical)

# 设置自定义滚动条到标准滚动区域
standard_scroll_area.setVerticalScrollBar(custom_scroll_bar)

# 可以同时设置垂直和水平滚动条
horizontal_scroll_bar = AnimatedScrollBar(Qt.Horizontal)
standard_scroll_area.setHorizontalScrollBar(horizontal_scroll_bar)

# 添加到界面布局
another_layout.addWidget(standard_scroll_area)
```

**高级用法**：
```python
# 创建具有特定颜色主题的滚动区域
from PyQt5.QtGui import QColor

# 创建滚动区域
custom_scroll_area = AnimatedScrollArea()

# 获取内部的滚动条对象（垂直）
vertical_bar = custom_scroll_area.verticalScrollBar()
if isinstance(vertical_bar, AnimatedScrollBar):
    # 自定义滚动条样式
    vertical_bar._base_color = QColor(52, 152, 219)  # 设置基础颜色（蓝色）
    vertical_bar._handle_color = QColor(41, 128, 185)  # 设置滑块颜色（深蓝色）
    vertical_bar._collapsed_width = 2  # 设置折叠状态宽度
    vertical_bar._expanded_width = 10  # 设置展开状态宽度
    vertical_bar._collapse_delay = 1000  # 设置折叠延迟时间（毫秒）
    vertical_bar.update_style()  # 应用更新的样式

# 设置滚动区域内容后需要调整内容大小策略
content = QWidget()
content_layout = QVBoxLayout(content)
# ... 添加内容 ...
content.setLayout(content_layout)
custom_scroll_area.setWidget(content)
content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
```

**实际应用场景**：
```python
# 在手势管理界面中使用滚动区域展示大量手势卡片
from ui.components.scrollbar import AnimatedScrollArea
from ui.components.card import CardWidget

# 创建滚动区域
gestures_scroll_area = AnimatedScrollArea()
gestures_scroll_area.setFrameShape(AnimatedScrollArea.NoFrame)
gestures_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
gestures_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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

##### 2.2.4 ui/components/side_tab.py

**功能说明**：左侧选项卡组件，提供美观的垂直选项卡界面，包含切换动画效果，符合应用主题风格。

**主要类和方法**：
- `AnimatedTabButton`：动画选项卡按钮类，用于显示单个选项卡
  - `__init__(text, icon=None, parent=None)`：初始化选项卡按钮
    - `text`：选项卡显示文本
    - `icon`：选项卡图标，QIcon对象或图标路径
    - `parent`：父窗口组件
  - `setSelected(selected)`：设置选项卡选中状态，并触发动画
    - `selected`：布尔值，True表示选中，False表示未选中
  - `setText(text)`：设置选项卡文本
    - `text`：新的选项卡文本
  - `setIcon(icon)`：设置选项卡图标
    - `icon`：QIcon对象或图标路径
  - `enterEvent(event)`：处理鼠标进入事件，触发悬停效果
  - `leaveEvent(event)`：处理鼠标离开事件，恢复正常效果
  - `paintEvent(event)`：绘制选项卡外观，包括背景、图标、文本和选中指示器
  - `_startAnimation(selected)`：开始选中/未选中状态的动画效果
  - `_updateAppearance()`：更新选项卡外观，根据当前状态调整颜色和指示器位置

- `SideTabWidget`：左侧选项卡容器类
  - `__init__(parent=None)`：初始化选项卡容器
    - `parent`：父窗口组件
  - `addTab(widget, text, icon=None, position=POSITION_TOP)`：添加新的选项卡，支持指定位置
    - `widget`：选项卡内容组件，通常是QWidget的子类
    - `text`：选项卡显示文本
    - `icon`：选项卡图标，QIcon对象或图标路径
    - `position`：选项卡位置，可以是POSITION_TOP或POSITION_BOTTOM，分别表示顶部区域和底部区域
    - 返回值：新添加选项卡的索引
  - `setCurrentIndex(index)`：设置当前选项卡，触发动画切换
    - `index`：选项卡索引，整数值
  - `currentIndex()`：获取当前选项卡索引
    - 返回值：当前选中的选项卡索引，整数值
  - `widget(index)`：获取指定索引的内容窗口
    - `index`：选项卡索引，整数值
    - 返回值：对应索引的内容组件
  - `setTabText(index, text)`：设置指定索引的选项卡文本
    - `index`：选项卡索引，整数值
    - `text`：新的选项卡文本
  - `setTabIcon(index, icon)`：设置指定索引的选项卡图标
    - `index`：选项卡索引，整数值
    - `icon`：QIcon对象或图标路径
  - `setTabPosition(index, position)`：更改已有选项卡的位置
    - `index`：选项卡索引，整数值
    - `position`：新的选项卡位置，POSITION_TOP或POSITION_BOTTOM
  - `tabPosition(index)`：获取选项卡的位置
    - `index`：选项卡索引，整数值
    - 返回值：选项卡位置，POSITION_TOP或POSITION_BOTTOM
  - `count()`：获取选项卡总数
    - 返回值：选项卡总数，整数值
  - `currentChanged`：信号，当前选项卡变化时触发，传递新的索引值

**特性说明**：
- 精美的扁平化设计，与应用主题风格一致，视觉统一
- 垂直布局的选项卡位于窗口左侧，优化空间使用，提供现代UI体验
- 选项卡支持两种位置定位：顶部(POSITION_TOP)和底部(POSITION_BOTTOM)
- 支持将重要和常用选项卡（如控制台）放在顶部，将设置等辅助功能放在底部，优化用户体验
- 可灵活调整选项卡位置，无需改变选项卡的添加顺序，布局更加灵活
- 选项卡切换时的平滑动画过渡效果，提升用户体验
- 选项卡支持图标和文本，信息呈现更加丰富
- 选中状态和悬停状态的动画效果，视觉反馈明确
- 鼠标离开选项卡时的平滑过渡动画效果，避免视觉上的生硬变化
- 选中选项卡的高亮指示器动画，清晰指示当前选中的选项卡
- 自动适应内容区域大小，根据窗口尺寸调整布局
- 可直接运行文件查看示例效果，便于单独调试和演示
- 已应用于整个应用程序的主界面，替代了标准的QTabWidget

**使用方法**：
```python
from ui.components.side_tab import SideTabWidget
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon

# 创建左侧选项卡组件
tab_widget = SideTabWidget()

# 创建要添加到选项卡的内容页面
console_tab = QWidget()
console_layout = QVBoxLayout(console_tab)
console_layout.addWidget(QLabel("控制台内容"))

gestures_tab = QWidget()
gestures_layout = QVBoxLayout(gestures_tab)
gestures_layout.addWidget(QLabel("手势管理内容"))

settings_tab = QWidget()
settings_layout = QVBoxLayout(settings_tab)
settings_layout.addWidget(QLabel("设置内容"))

# 加载图标
console_icon = QIcon("path/to/console_icon.png")
gestures_icon = QIcon("path/to/gestures_icon.png")
settings_icon = QIcon("path/to/settings_icon.png")

# 添加带图标的选项卡（放在顶部）
console_index = tab_widget.addTab(
    console_tab, 
    "控制台", 
    console_icon, 
    tab_widget.POSITION_TOP
)

# 添加手势管理选项卡（也放在顶部）
gestures_index = tab_widget.addTab(
    gestures_tab, 
    "手势管理", 
    gestures_icon, 
    tab_widget.POSITION_TOP
)

# 将设置选项卡放在底部
settings_index = tab_widget.addTab(
    settings_tab, 
    "设置", 
    settings_icon, 
    tab_widget.POSITION_BOTTOM
)

# 切换到指定选项卡
tab_widget.setCurrentIndex(0)  # 切换到控制台选项卡

# 监听选项卡切换事件
def onTabChanged(index):
    print(f"切换到选项卡 {index}")
    
tab_widget.currentChanged.connect(onTabChanged)

# 动态更改选项卡位置
tab_widget.setTabPosition(1, tab_widget.POSITION_BOTTOM)  # 将手势管理选项卡移到底部

# 检查选项卡当前位置
position = tab_widget.tabPosition(1)
print(f"选项卡1的位置: {'顶部' if position == tab_widget.POSITION_TOP else '底部'}")

# 动态更改选项卡文本
tab_widget.setTabText(0, "主控制台")

# 获取选项卡内容组件
content = tab_widget.widget(0)

# 获取选项卡总数
tab_count = tab_widget.count()
print(f"选项卡总数: {tab_count}")

# 添加到主窗口布局
main_layout = QVBoxLayout()
main_layout.addWidget(tab_widget)
main_window.setLayout(main_layout)
```

**实际应用示例**：
```python
# 在主应用程序中使用SideTabWidget
from ui.components.side_tab import SideTabWidget
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
        
        # 创建选项卡
        self.tab_widget = SideTabWidget()
        
        # 创建各选项卡内容
        self.console_tab = ConsoleTab()
        self.gestures_tab = GesturesTab()
        self.settings_tab = SettingsTab()
        
        # 加载图标
        icons_dir = "path/to/icons"
        console_icon = QIcon(f"{icons_dir}/console.svg")
        gestures_icon = QIcon(f"{icons_dir}/gestures.svg")
        settings_icon = QIcon(f"{icons_dir}/settings.svg")
        
        # 添加选项卡
        self.tab_widget.addTab(self.console_tab, "控制台", console_icon, 
                             self.tab_widget.POSITION_TOP)
        self.tab_widget.addTab(self.gestures_tab, "手势管理", gestures_icon, 
                             self.tab_widget.POSITION_TOP)
        self.tab_widget.addTab(self.settings_tab, "设置", settings_icon, 
                             self.tab_widget.POSITION_BOTTOM)
        
        # 添加到主布局
        main_layout.addWidget(self.tab_widget)

# 连接信号
        self.tab_widget.currentChanged.connect(self.onTabChanged)
    
    def onTabChanged(self, index):
        # 根据选项卡切换更新状态
        tab_name = self.tab_widget.tabText(index)
        self.statusBar().showMessage(f"当前页面: {tab_name}")
```

##### 2.2.5 ui/components/combobox

**功能说明**：动画下拉菜单组件，提供精美的、带有展开/收起动画效果的下拉菜单。

**主要特性**：
- 精美的扁平化设计，使用与应用程序主题一致的颜色
- **平滑展开动画**：下拉列表展开时平滑展开动画，而非传统的瞬间显示
- **平滑收起动画**：下拉列表收起时平滑收起动画，增强用户体验
- **自定义占位文本**：支持设置占位文本，在未选择项目时显示

###### 2.2.5.1 ui/components/combobox/qcustomcombobox.py

**功能说明**：自定义下拉菜单组件，提供美观的、带有动画效果的下拉选择界面，可以轻松集成到任何界面。

**主要类和方法**：
- `QCustomComboBox`：自定义下拉菜单类，继承自`QComboBox`
  - `__init__(parent=None)`：初始化下拉菜单，支持多种自定义参数
    - `parent`：父窗口组件
  - `setBackgroundColor(color)`：设置下拉菜单背景颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串（如"#ffffff"）
  - `setTextColor(color)`：设置下拉菜单文本颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setBorderColor(color)`：设置下拉菜单边框颜色
    - `color`：颜色值，可以是QColor对象、RGB元组或CSS颜色字符串
  - `setBorderRadius(radius)`：设置下拉菜单边框圆角半径
    - `radius`：整数值（像素）
  - `customizeQCustomComboBox(**customValues)`：批量设置多个样式属性
    - `customValues`：关键字参数，可包含backgroundColor、backgroundHoverColor、textColor等
  - `showPopup()`：重写的显示下拉列表方法，添加了平滑展开动画
  - `hidePopup()`：重写的隐藏下拉列表方法，添加了平滑收起动画
  - `setPlaceholderText(text)`：设置下拉菜单的占位文本，在未选择项目时显示
    - `text`：占位文本字符串
  - `getPlaceholderText()`：获取当前设置的占位文本
    - 返回值：占位文本字符串

- `ComboBoxDelegate`：下拉菜单项的自定义渲染代理类，继承自`QStyledItemDelegate`
  - `paint(painter, option, index)`：自定义绘制下拉菜单项的方法
  - `sizeHint(option, index)`：返回项目的理想大小

**特性说明**：
- 精美的扁平化设计，默认使用白色背景，浅灰色边框
- 鼠标悬停和点击时的背景和边框颜色变化动画效果
- 箭头旋转动画效果，打开下拉菜单时箭头旋转180度
- 下拉菜单展开和收起的动画效果，使用平滑的高度变化动画
- 下拉菜单项有圆角背景，悬停和选中时有颜色变化
- 支持SVG图标，附带默认的箭头图标
- 完全可定制的外观，包括颜色、圆角、边框样式等
- 提供完善的事件处理，响应鼠标悬停、点击等事件
- 支持长文本省略显示，避免界面溢出
- 自动适配不同大小的显示区域

**使用方法**：
```python
from ui.components.combobox.qcustomcombobox import QCustomComboBox
from PyQt5.QtWidgets import QVBoxLayout, QWidget

# 创建基本下拉菜单
combo = QCustomComboBox()
combo.addItem("选项1")
combo.addItem("选项2")
combo.addItem("选项3")

# 添加到布局
layout = QVBoxLayout()
layout.addWidget(combo)

# 自定义样式
combo.customizeQCustomComboBox(
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
combo.setTextColor("#222222")

# 设置占位文本
combo.setPlaceholderText("请选择一个选项...")

# 监听选项变化
def on_selection_changed(index):
    print(f"选中项: {combo.currentText()}, 索引: {index}")
    
combo.currentIndexChanged.connect(on_selection_changed)
```

**实际应用案例**：
```python
# 手势管理界面中使用自定义下拉菜单
from ui.components.combobox.qcustomcombobox import QCustomComboBox
from PyQt5.QtGui import QColor

# 创建自定义下拉菜单
direction_combo = QCustomComboBox()
direction_combo.addItems(["上", "下", "左", "右", "上-下", "右-左"])
direction_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

# 自定义样式
combo_style = {
    "backgroundColor": "#ffffff",
    "backgroundHoverColor": "#f5f5f5",
    "backgroundPressColor": "#e5e5e5",
    "borderColor": "#dddddd",
    "hoverBorderColor": "#3498db",
    "pressBorderColor": "#2980b9",
    "textColor": "#333333",
    "textHoverColor": "#000000",
    "borderRadius": 4,
    "borderWidth": 1,
    "dropdownBorderRadius": 4,
    "arrowColor": "#888888",
    "arrowHoverColor": "#3498db",
    "arrowPressColor": "#2980b9",
    "dropShadowColor": QColor(0, 0, 0, 80),
    "dropShadowRadius": 15
}
direction_combo.customizeQCustomComboBox(**combo_style)

# 添加到布局
direction_layout = QHBoxLayout()
direction_layout.addWidget(QLabel("方向:"))
direction_layout.addWidget(direction_combo)
main_layout.addLayout(direction_layout)

# 设置选中项
direction_combo.setCurrentText("上-下")
```

##### 2.2.6 ui/components/animated_stacked_widget.py

**功能说明**：动画堆栈组件，提供界面切换时的平滑动画效果，支持多种动画方式。

**主要类和方法**：
- `AnimatedStackedWidget`：动画堆栈组件，继承自QStackedWidget
  - `__init__(parent=None)`：初始化动画堆栈组件
    - `parent`：父窗口组件
  - `setAnimationEnabled(enabled)`：设置是否启用动画效果
    - `enabled`：布尔值，True表示启用动画，False表示禁用
  - `setAnimationType(animation_type)`：设置动画类型
    - `animation_type`：动画类型常量
      - `ANIMATION_LEFT_TO_RIGHT`：从左到右滑动
      - `ANIMATION_RIGHT_TO_LEFT`：从右到左滑动
      - `ANIMATION_TOP_TO_BOTTOM`：从上到下滑动
      - `ANIMATION_BOTTOM_TO_TOP`：从下到上滑动
      - `ANIMATION_FADE`：淡入淡出效果
  - `setAnimationDuration(duration)`：设置动画持续时间
    - `duration`：动画持续时间（毫秒）
  - `setAnimationCurve(curve)`：设置动画曲线
    - `curve`：QEasingCurve对象，定义动画的加速和减速方式
  - `setCurrentIndex(index)`：设置当前显示的部件索引
    - `index`：部件索引，整数值
  - `animationFinished`：信号，动画完成时触发

**特性说明**：
- 支持多种动画效果：滑动（左右/上下）和淡入淡出
- 可自定义动画持续时间和动画曲线
- 无缝集成到PyQt5应用程序
- 兼容所有QWidget子类作为内容部件
- 平滑过渡效果，提升用户体验
- 内部使用QPropertyAnimation进行动画处理，保证流畅性能
- 可以根据需要启用或禁用动画效果
- 提供动画完成信号，方便执行后续操作
- 自动处理部件的可见性，确保正确显示
- 可单独运行作为演示程序

**使用方法**：
```python
from ui.components.animated_stacked_widget import AnimatedStackedWidget
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

# 创建动画堆栈组件
stacked_widget = AnimatedStackedWidget()

# 设置动画类型
stacked_widget.setAnimationType(AnimatedStackedWidget.ANIMATION_RIGHT_TO_LEFT)

# 设置动画持续时间（毫秒）
stacked_widget.setAnimationDuration(300)

# 添加页面
page1 = QWidget()
page1_layout = QVBoxLayout(page1)
page1_layout.addWidget(QLabel("第一页"))

page2 = QWidget()
page2_layout = QVBoxLayout(page2)
page2_layout.addWidget(QLabel("第二页"))

stacked_widget.addWidget(page1)
stacked_widget.addWidget(page2)

# 切换到指定页面（带动画效果）
stacked_widget.setCurrentIndex(1)

# 添加动画完成处理
def on_animation_finished():
    print("动画已完成")
    
stacked_widget.animationFinished.connect(on_animation_finished)
```

**实际应用示例**（在手势选项卡中的使用）：
```python
from ui.components.animated_stacked_widget import AnimatedStackedWidget

class GesturesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化UI
        self.initUI()
    
    def createGestureEditor(self, parent_widget):
        """创建右侧手势编辑区域"""
        # 创建右侧布局
        right_layout = QVBoxLayout(parent_widget)
        
        # 创建标题
        title_label = QLabel("编辑手势")
        right_layout.addWidget(title_label)
        
        # 创建动画堆栈组件
        self.content_stack = AnimatedStackedWidget()
        self.content_stack.setAnimationType(AnimatedStackedWidget.ANIMATION_RIGHT_TO_LEFT)
        self.content_stack.setAnimationDuration(300)
        
        # 创建并添加编辑选项卡
        edit_tab = self._createEditTab()
        self.content_stack.addWidget(edit_tab)
        
        # 创建并添加其他选项卡（如预览、帮助等）
        # ...
        
        # 添加到布局
        right_layout.addWidget(self.content_stack)
```

##### 2.2.7 ui/components/input_field.py

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
from PyQt5.QtWidgets import QWidget, QVBoxLayout

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
  - `_calculate_simulated_pressure(self, x, y)`：根据鼠标移动速度计算模拟压力值，经过简化和优化

**特性说明**：
- 全局透明覆盖层，可在任何应用程序上方进行绘制
- 支持完整的绘制生命周期：开始、继续、结束
- 所有设置值从settings模块获取
- 绘制结束后自动分析笔画方向，执行匹配手势
- 支持笔画淡出动画效果
- 智能处理鼠标事件，只响应鼠标右键绘制
- 简化的日志记录，只保留关键信息
- 优化的压力计算算法
- 高效的绘制算法，保持流畅性能

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
4. **资源管理(assets/)**：管理应用程序资源，如图标和配置文件
5. **版本管理(version.py)**：管理应用程序版本信息和构建参数

**数据流向**：
1. 用户通过鼠标右键在屏幕上绘制手势
2. 绘制模块(drawer.py)捕获鼠标事件并记录轨迹点
3. 笔画分析模块(stroke_analyzer.py)分析轨迹点序列，识别出方向变化
4. 手势执行模块(gesture_executor.py)查找匹配的手势并执行相应动作
5. UI模块显示状态变化和结果，并允许用户配置设置和管理手势库

**通信机制**：
- 使用Qt的信号槽机制实现模块间的松耦合通信
- 使用事件驱动设计，降低模块间的直接依赖
- 使用单例模式管理共享资源，如日志记录器和设置管理器

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
   - 创建选项卡容器(SideTabWidget)
   - 初始化控制台选项卡(ConsoleTab)
   - 初始化设置选项卡(SettingsTab)
   - 初始化手势管理选项卡(GesturesTab)
   - 设置底部状态栏和退出按钮

4. **显示主窗口**
   - 应用窗口样式和布局
   - 设置默认选择的选项卡(控制台)
   - 显示主窗口
   - 进入应用程序主循环

##### 4.2.2 绘制流程

1. **启动绘制功能**
   - 用户点击控制台选项卡上的"开始绘制"按钮
   - 创建DrawingManager实例
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
   - 释放相关资源

##### 4.2.3 设置管理流程

1. **查看设置**
   - 用户切换到设置选项卡
   - 加载并显示当前设置，如笔尖粗细和颜色

2. **修改设置**
   - 用户调整笔尖粗细(QSpinBox)或点击颜色按钮选择新颜色
   - PenPreviewWidget实时显示预览效果
   - 设置更改立即应用于内存中的设置对象

3. **保存设置**
   - 用户点击"保存设置"按钮
   - 设置保存到配置文件中
   - 如果绘制功能正在运行，应用新设置而无需重启绘制功能

4. **重置设置**
   - 用户点击"重置设置"按钮
   - 从default_settings.json加载默认设置
   - 更新UI显示和预览
   - 如果绘制功能正在运行，应用默认设置

##### 4.2.4 手势管理流程

1. **查看手势**
   - 用户切换到手势管理选项卡
   - 加载并显示当前手势库，以卡片形式展示每个手势
   - 按照ID顺序排列手势卡片，ID越小排在越前面

2. **编辑手势**
   - 用户点击左侧手势卡片
   - 右侧编辑区域显示选中手势的详细信息
   - 用户可以修改手势名称、方向和动作
   - 修改立即应用于内存中的手势对象，并实时更新左侧卡片显示

3. **添加手势**
   - 用户填写右侧编辑区域的内容
   - 点击"添加新手势"按钮
   - 系统自动分配新的手势ID（当前最大ID+1）
   - 新手势添加到左侧卡片列表中

4. **删除手势**
   - 用户选中要删除的手势卡片
   - 点击"删除手势"按钮
   - 系统删除选中的手势，并自动重排后续手势的ID，保持ID连续性
   - 左侧卡片列表更新，移除已删除的手势

5. **重置手势库**
   - 用户点击"重置手势库"按钮
   - 系统从default_gestures.json加载默认手势库
   - 重置所有手势的ID，按照默认顺序排列
   - 左侧卡片列表更新，显示默认手势库

6. **保存手势库**
   - 用户点击"保存更改"按钮
   - 系统将当前手势库保存到配置文件中
   - 更新内存中的手势对象，使其反映最新的保存状态

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

##### 4.3.3 工作流程优化场景

**场景7: 设计师工作流程**
1. 设计师配置以下手势：
   - "Z"手势 → Ctrl+Z (撤销)
   - "圆形"手势 → Ctrl+S (保存)
   - "上-右"手势 → 切换图层 (Ctrl+])
   - "上-左"手势 → 切换图层 (Ctrl+[)
2. 设计师在Photoshop中工作时启动GestroKey
3. 使用预定义的手势快速执行常用操作，无需频繁切换键盘和鼠标

**场景8: 程序员编码助手**
1. 程序员配置以下手势：
   - "右-下"手势 → Ctrl+C (复制)
   - "下-右"手势 → Ctrl+V (粘贴)
   - "L"形手势 → Ctrl+F (查找)
   - "右-左"手势 → Ctrl+Tab (切换文件)
   - "上-下"手势 → F5 (运行/调试)
2. 程序员在IDE中编码时启动GestroKey
3. 使用手势快速执行常用操作，提高编码效率

#### 4.4 扩展开发指南

##### 4.4.1 添加新的手势动作类型

要添加新的手势动作类型（如启动程序、执行脚本等），需要修改以下文件：

1. **core/gesture_executor.py**：
```python
# 添加新的执行方法
def _execute_program(self, program_path):
    """执行指定的程序"""
    try:
        import subprocess
        subprocess.Popen(program_path)
        return True
except Exception as e:
        self.logger.error(f"执行程序失败: {e}")
        return False

# 在execute_gesture方法中添加对新动作类型的处理
def execute_gesture(self, direction):
    # ... 现有代码 ...
    
    action_type = gesture_info["action"]["type"]
    action_value = gesture_info["action"]["value"]
    
    if action_type == "shortcut":
        return self._execute_shortcut(action_value)
    elif action_type == "program":  # 新增动作类型
        return self._execute_program(action_value)
    else:
        self.logger.warning(f"不支持的动作类型: {action_type}")
        return False
```

2. **ui/gestures/gestures_tab.py**：
```python
# 在初始化方法中扩展动作类型下拉菜单
def initUI(self):
    # ... 现有代码 ...
    
    # 动作类型下拉菜单
    self.action_type_combo = QComboBox()
    self.action_type_combo.addItem("执行快捷键", "shortcut")
    self.action_type_combo.addItem("启动程序", "program")  # 新增动作类型
    
    # ... 现有代码 ...
```

3. **ui/gestures/gestures.py**：
```python
# 在文档字符串中添加新动作类型的说明
"""
手势库管理模块，负责保存和加载用户手势库。

支持的动作类型:
- shortcut: 执行键盘快捷键，如"ctrl+c"
- program: 启动指定程序，值为程序路径
"""
```

##### 4.4.2 添加新的UI组件

所有自定义UI组件都位于`ui/components`目录下，遵循以下规范：

1. **组件定义**：每个组件应该继承自适当的Qt基类，实现必要的方法和信号
```python
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

class MyCustomWidget(QWidget):
    """自定义组件类"""
    
    # 定义信号
    valueChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        # 初始化组件UI
        pass
    
    def setValue(self, value):
        # 设置组件值
        self._value = value
        self.update()  # 触发重绘
        self.valueChanged.emit(value)  # 发射信号
```

2. **组件测试**：每个组件文件末尾应包含独立测试代码，便于单独调试
```python
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # 创建并添加自定义组件
    custom_widget = MyCustomWidget()
    layout.addWidget(custom_widget)
    
    # 显示测试窗口
    window.setCentralWidget(widget)
    window.setGeometry(100, 100, 400, 300)
    window.setWindowTitle("组件测试")
    window.show()
    
    sys.exit(app.exec_())
```

3. **组件文档**：每个组件应包含详细的文档说明，描述其功能、参数和使用方法
```python
class ColorPicker(QWidget):
    """颜色选择器组件
    
    提供色相、饱和度和亮度调节，实时预览选中的颜色。
    
    Args:
        parent (QWidget, optional): 父窗口组件
        initial_color (list, optional): 初始颜色，RGB格式的数组，默认为[255, 0, 0]
        
    Signals:
        colorChanged(list): 当颜色变化时发出，传递RGB格式的颜色数组
    """
```

##### 4.4.3 调试技巧

1. **使用日志系统**：
```python
from core.logger import get_logger

# 创建日志记录器
logger = get_logger("MyModule")

# 跟踪代码执行
logger.debug("函数开始执行")

# 记录重要信息
logger.info(f"处理完成，结果: {result}")

# 异常情况
try:
    # 可能出错的代码
    result = process_data(data)
except Exception as e:
    logger.exception(f"处理数据时出错: {e}")
    # 处理异常...
```

2. **查看日志文件**：
- 日志文件位于`%USERPROFILE%\.gestrokey\log\`目录
- 按照日期命名，如`2023-01-01.log`
- 包含详细的时间戳、级别和模块信息

3. **调试绘制功能**：
```python
# 创建监听绘制事件的对象
class DrawingDebugger:
    def __init__(self):
        self.drawer = DrawingManager()
        
        # 连接信号
        self.drawer.overlay.signals.stroke_completed.connect(self.on_stroke_completed)
        self.drawer.start()
    
    def on_stroke_completed(self, stroke_id, direction):
        print(f"笔画ID: {stroke_id}")
        print(f"方向序列: {direction}")
        
        # 获取笔画点数据
        stroke_data = self.drawer.overlay.strokes.get(stroke_id, [])
        print(f"笔画点数: {len(stroke_data)}")
        
        # 输出前5个点的坐标
        for i, point in enumerate(stroke_data[:5]):
            print(f"点{i}: ({point[0]}, {point[1]})")

# 创建调试器
debugger = DrawingDebugger()
```

### 5. 总结

GestroKey是一个功能完善的手势控制工具，通过简单的鼠标绘制实现各种复杂操作。系统采用模块化设计，各个组件之间通过清晰的接口进行交互，确保代码的可维护性和可扩展性。

**核心功能亮点**：
- 全局绘制功能，可在任何应用上方进行手势绘制
- 智能方向识别，准确分析用户的绘制意图
- 丰富的手势库管理，支持自定义手势和动作
- 精美的用户界面，包含多个定制组件，提供直观的用户体验
- 完善的设置系统，支持个性化配置和即时应用
- 详细的日志记录，便于调试和问题排查
- 优秀的性能优化，确保流畅的用户体验

**开发优势**：
- 清晰的代码组织，便于理解和扩展
- 详细的文档说明，包括类、方法和示例
- 组件化设计，鼓励代码复用
- 事件驱动架构，降低模块间的耦合度
- 优秀的错误处理，提高程序的稳定性
- 全面的日志系统，便于问题诊断和解决

**未来发展方向**：
- 支持更多的动作类型，如执行程序、脚本和宏
- 增强手势识别算法，支持更复杂的手势模式
- 添加用户手势训练功能，提高识别准确率
- 实现手势录制和回放功能，便于创建复杂手势
- 提供云同步功能，在多设备间共享手势库
- 开发插件系统，支持第三方扩展

GestroKey为用户提供了一种全新的人机交互方式，通过简单的手势绘制即可执行各种操作，大大提高了工作效率。无论是日常办公、创意设计还是编程开发，GestroKey都能为用户带来全新的便捷体验。

### 最近代码优化

#### @core 目录代码优化

为了提高代码质量和可维护性，最近对 `core` 目录下的核心模块进行了以下优化：

1. **日志记录优化**
   - 减少了冗余的日志记录，保留关键信息
   - 简化了日志级别的使用，更符合日志规范
   - 优化了日志初始化流程，提高了代码清晰度

2. **代码结构优化**
   - 简化了复杂的嵌套条件判断，提高代码可读性
   - 减少了不必要的条件检查和重复代码
   - 优化了方法签名和参数列表，保持简洁性
   - 重新组织部分代码，使逻辑更加清晰

3. **性能优化**
   - 改进了模拟压力计算算法，使其更加高效
   - 优化了系统监测数据更新机制，减少资源占用
   - 简化了手势执行器中的快捷键处理逻辑

4. **错误处理优化**
   - 加强了异常捕获和处理机制
   - 简化了错误日志记录，避免重复信息
   - 提供了更清晰的错误信息，便于调试

5. **文档优化**
   - 更新了模块文档，反映当前实现
   - 简化了使用示例，更加易于理解
   - 删除了过时的参数说明和使用指南

6. **单例模式实现**
   - 改进了 `GestureExecutor` 的单例实现，确保全局只有一个实例
   - 添加了实例检查，防止误创建多个实例

这些优化保留了全部原有功能，同时提高了代码质量和可维护性。核心模块的性能和稳定性得到了提升，为后续功能扩展奠定了更加坚实的基础。