# GestroKey 源代码目录说明

本文档详细介绍了GestroKey项目`src`目录下各文件和文件夹的功能及使用方法。

## 目录结构

```
src/
├── core/                    # 核心功能模块
│   ├── drawer.py            # 绘画核心模块
│   ├── stroke_analyzer.py   # 笔画分析模块
│   ├── gesture_executor.py  # 手势执行模块
│   └── logger.py            # 日志记录模块
├── ui/                      # 用户界面模块
│   ├── console.py           # 控制台选项卡
│   ├── components/          # UI组件模块
│   │   ├── button.py        # 自定义动画按钮组件
│   │   ├── card.py          # 自定义卡片组件
│   │   └── side_tab.py      # 左侧选项卡组件
│   ├── settings/            # 设置相关界面
│   │   ├── settings_tab.py  # 设置选项卡
│   │   ├── settings.py      # 设置管理模块
│   │   └── default_settings.json # 默认设置定义（JSON格式）
│   └── gestures/            # 手势管理相关界面
│       ├── gestures_tab.py  # 手势管理选项卡
│       ├── gestures.py      # 手势库管理模块
│       └── default_gestures.json # 默认手势库定义（JSON格式）
├── assets/                  # 资源文件目录
│   └── images/              # 图像资源
│       ├── icon.svg         # 应用图标
│       ├── console.svg      # 控制台选项卡图标
│       ├── settings.svg     # 设置选项卡图标
│       └── gestures.svg     # 手势管理选项卡图标
├── version.py               # 版本信息模块
└── main.py                  # 主程序入口
```

## 详细说明

### 1. main.py

**功能说明**：程序的主入口文件，提供带有选项卡的图形用户界面，包含控制台、设置界面和手势管理界面。

**主要类和方法**：
- `GestroKeyApp`：主窗口类，继承自`QMainWindow`
  - `initUI()`：初始化用户界面，设置选项卡和窗口属性
  - `closeEvent(event)`：处理窗口关闭事件，确保正确保存设置和停止绘制

**使用方法**：
```python
# 直接运行该文件启动应用程序
python src/main.py
```

**GUI选项卡**：
- 控制台选项卡：提供绘制功能的开启和停止控制
- 设置选项卡：提供应用程序设置的配置，包括笔尖粗细和笔尖颜色设置
- 手势管理选项卡：提供手势库的管理界面，可添加、编辑、删除手势

### 2. version.py

**功能说明**：版本信息模块，存储和管理所有随时间变化的变量，如版本号、构建日期等。

**主要变量**：
- `VERSION`：版本号，如"1.0.0"
- `VERSION_NAME`：版本名称，如"初始版本"
- `BUILD_DATE`：构建日期，格式为"YYYY-MM-DD"
- `BUILD_NUMBER`：构建编号
- `APP_NAME`：应用程序名称
- `APP_DESCRIPTION`：应用程序描述
- `AUTHOR`：作者信息
- `COPYRIGHT`：版权信息
- `DEFAULT_PEN_WIDTH`：默认笔尖粗细
- `DEFAULT_PEN_COLOR`：默认笔尖颜色，RGB格式

**主要函数**：
- `get_version_string()`：获取格式化的版本字符串，如"v1.0.0"
- `get_full_version_string()`：获取完整的版本字符串，包含版本名称和构建信息
- `get_about_text()`：获取关于信息文本

**使用方法**：
```python
from version import VERSION, APP_NAME, get_version_string

# 获取版本号
current_version = VERSION  # 如："1.0.0"

# 获取应用名称
app_name = APP_NAME  # 如："GestroKey"

# 获取格式化的版本字符串
version_string = get_version_string()  # 如："v1.0.0"
```

### 3. ui/console.py

**功能说明**：控制台选项卡模块，实现绘制功能的控制界面。

**主要类和方法**：
- `ConsoleTab`：控制台选项卡类，继承自`QWidget`
  - `initUI()`：初始化控制台选项卡界面
  - `start_drawing()`：开始绘制功能
  - `stop_drawing()`：停止绘制功能

**使用方法**：
```python
from ui.console import ConsoleTab

# 创建控制台选项卡
console = ConsoleTab()

# 添加到界面
# ...
```

### 4. ui/components/button.py

**功能说明**：自定义动画按钮组件，提供美观的、带有动画效果的按钮，可以轻松集成到任何界面。

**主要类和方法**：
- `AnimatedButton`：动画按钮类，继承自`QPushButton`
  - `__init__(text, parent, icon, primary_color, ...)`：初始化按钮，支持多种自定义参数
  - `set_primary_color(color)`：设置按钮主色调
  - `set_hover_color(color)`：设置按钮悬停色调
  - `set_text_color(color)`：设置按钮文本颜色
  - `set_border_radius(radius)`：设置按钮边框圆角半径

**特性说明**：
- 精美的扁平化设计，主题色为蓝色系
- 鼠标悬停时文字轻微上浮和放大的动画效果
- 按下时文字下沉和缩小的动画效果，与按钮主体动画保持一致
- 平滑的鼠标离开过渡动画，避免视觉上的生硬跳变
- 支持自定义颜色、图标、文本颜色和圆角半径
- 自动计算悬停色调，如未指定则基于主色调生成更亮的颜色，保持色彩统一性
- 阴影和高光效果，提供现代感视觉体验
- 可直接运行文件查看示例效果，便于单独调试
- 已应用于整个应用程序的界面按钮，提供统一的视觉风格

**应用场景**：
- 主窗口的退出按钮
- 控制台选项卡的开始和停止绘制按钮，均使用主题蓝色保持统一风格
- 设置选项卡的保存和重置设置按钮

**使用方法**：
```python
from ui.components.button import AnimatedButton

# 创建基本按钮
button = AnimatedButton("按钮文本")

# 创建自定义按钮
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

# 添加到布局
layout.addWidget(button)

# 动态修改按钮属性
button.set_primary_color([25, 80, 160])  # 修改为深蓝色
button.set_border_radius(16)             # 修改圆角半径
```

### 3.1 ui/components/side_tab.py

**功能说明**：左侧选项卡组件，提供美观的垂直选项卡界面，包含切换动画效果，符合应用主题风格。

**主要类和方法**：
- `AnimatedTabButton`：动画选项卡按钮类，用于显示单个选项卡
  - `setSelected(selected)`：设置选项卡选中状态，并触发动画
  - `setText(text)`：设置选项卡文本
  - `setIcon(icon)`：设置选项卡图标
- `SideTabWidget`：左侧选项卡容器类
  - `addTab(widget, text, icon=None, position=POSITION_TOP)`：添加新的选项卡，支持指定位置
  - `setCurrentIndex(index)`：设置当前选项卡，触发动画切换
  - `currentIndex()`：获取当前选项卡索引
  - `widget(index)`：获取指定索引的内容窗口
  - `setTabText(index, text)`：设置指定索引的选项卡文本
  - `setTabIcon(index, icon)`：设置指定索引的选项卡图标
  - `setTabPosition(index, position)`：更改已有选项卡的位置
  - `tabPosition(index)`：获取选项卡的位置

**特性说明**：
- 精美的扁平化设计，与应用主题风格一致
- 垂直布局的选项卡位于窗口左侧
- 选项卡支持两种位置定位：顶部(POSITION_TOP)和底部(POSITION_BOTTOM)
- 支持将重要和常用选项卡（如控制台）放在顶部，将设置等辅助功能放在底部，优化用户体验
- 可灵活调整选项卡位置，无需改变选项卡的添加顺序
- 选项卡切换时的平滑动画过渡效果
- 选项卡支持图标和文本
- 选中状态和悬停状态的动画效果
- 鼠标离开选项卡时的平滑过渡动画效果，避免视觉上的生硬变化
- 选中选项卡的高亮指示器动画
- 自动适应内容区域大小
- 可直接运行文件查看示例效果，便于单独调试
- 已应用于整个应用程序的主界面，替代了标准的QTabWidget

**使用方法**：
```python
from ui.components.side_tab import SideTabWidget

# 创建左侧选项卡组件
tab_widget = SideTabWidget()

# 添加带图标的选项卡（放在顶部）
console_tab = QWidget()  # 或任何QWidget子类
console_icon = QIcon("path/to/icon.png")
tab_widget.addTab(console_tab, "控制台", console_icon, tab_widget.POSITION_TOP)

# 添加手势管理选项卡（也放在顶部）
gestures_tab = QWidget()
gestures_icon = QIcon("path/to/gestures_icon.png")
tab_widget.addTab(gestures_tab, "手势管理", gestures_icon, tab_widget.POSITION_TOP)

# 将设置选项卡放在底部
settings_tab = QWidget()
settings_icon = QIcon("path/to/settings_icon.png")
tab_widget.addTab(settings_tab, "设置", settings_icon, tab_widget.POSITION_BOTTOM)

# 切换到指定选项卡
tab_widget.setCurrentIndex(0)  # 切换到控制台选项卡

# 监听选项卡切换事件
tab_widget.currentChanged.connect(onTabChanged)

# 动态更改选项卡位置
tab_widget.setTabPosition(1, tab_widget.POSITION_BOTTOM)  # 将手势管理选项卡移到底部

# 添加到界面布局
layout.addWidget(tab_widget)
```

### 3.2 ui/components/card.py

**功能说明**：卡片组件，提供精美的、有交互效果的卡片容器，可以容纳其他组件，适合展示结构化信息。

**主要类和方法**：
- `CardWidget`：卡片组件类，继承自`QWidget`
  - `__init__(parent, primary_color, hover_color, ...)`：初始化卡片，支持多种自定义参数
  - `add_widget(widget)`：向卡片内添加组件
  - `set_selected(selected)`：设置卡片的选中状态
  - `is_selected()`：获取卡片的选中状态
  - `set_title(title)`：设置卡片标题
  - `get_title()`：获取卡片标题
  - `set_primary_color(color)`：设置卡片主色调
  - `set_hover_color(color)`：设置卡片悬停色调
  - `set_selected_color(color)`：设置卡片选中状态的颜色
  - `set_text_color(color)`：设置卡片文本颜色
  - `set_border_radius(radius)`：设置卡片边框圆角半径

**特性说明**：
- 精美的扁平化设计，默认使用淡蓝色系主题
- 支持鼠标悬停、点击的动画效果
- 具有选中状态，默认使用更淡的主题蓝色作为选中状态颜色，视觉效果更柔和
- 动态阴影效果，悬停时阴影增强，增加立体感
- 适当的内边距设计，确保内容不会覆盖卡片边框
- 内容随卡片一起动画效果，提供更连贯的交互体验
- 支持添加标题和内容组件
- 完全可定制的外观，包括颜色、圆角、阴影等
- 发射点击信号，便于处理用户交互
- 可直接运行文件查看示例效果，便于单独调试
- 适合用于展示列表项、信息卡片、设置面板等场景

**使用方法**：
```python
from ui.components.card import CardWidget

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

# 添加到布局
layout.addWidget(card)

# 设置选中状态
card.set_selected(True)

# 监听点击事件
card.clicked.connect(on_card_clicked)

# 动态修改卡片属性
card.set_title("新标题")
card.set_primary_color([240, 255, 240])  # 淡绿色
```

### 4. ui/settings/settings_tab.py

**功能说明**：设置选项卡模块，提供应用程序设置的配置界面。

**主要类和方法**：
- `SettingsTab`：设置选项卡类，继承自`QWidget`
  - `initUI()`：初始化设置选项卡界面
  - `pen_width_changed(value)`：处理笔尖粗细变化，并实时更新绘制管理器参数
  - `show_color_dialog()`：显示颜色选择对话框，设置笔尖颜色
  - `update_color_button(color)`：更新颜色按钮的外观显示
  - `reset_settings()`：重置为默认设置，并更新绘制管理器参数
  - `save_settings()`：保存设置到文件，并更新绘制管理器参数
  - `_update_drawing_manager()`：内部方法，负责更新绘制管理器的参数
- `PenPreviewWidget`：笔尖预览小部件，显示笔尖粗细和颜色效果
  - `update_width(width)`：更新笔尖粗细预览
  - `update_color(color)`：更新笔尖颜色预览

**特性说明**：
- 笔尖粗细设置使用数字微调框 (QSpinBox)，支持1-20像素范围
- 笔尖颜色设置使用标准QPushButton显示当前颜色，点击后打开颜色对话框
- 笔尖预览实时显示当前设置的效果
- 使用自定义AnimatedButton组件作为重置和保存设置按钮
- 所有设置变更都实时应用到绘制管理器，无需重启绘制功能

**使用方法**：
```python
from ui.settings.settings_tab import SettingsTab

# 创建设置选项卡
settings = SettingsTab()

# 添加到界面
# ...
```

### 5. ui/settings/settings.py

**功能说明**：设置管理模块，负责保存和加载用户设置。

**主要类和方法**：
- `Settings`：设置管理器类
  - `_load_default_settings()`：从JSON文件加载默认设置
  - `load()`：从文件加载设置
  - `save()`：保存设置到文件
  - `get(key, default=None)`：获取设置项
  - `set(key, value)`：设置设置项
  - `reset_to_default()`：重置为默认设置
- `get_settings()`：获取设置管理器的全局实例

**特性说明**：
- 默认设置完全从`default_settings.json`文件加载，不存在内置硬编码的默认值
- 如果默认设置文件不存在或无法加载，程序将抛出异常

**使用方法**：
```python
from ui.settings.settings import get_settings

# 获取设置管理器
settings = get_settings()

# 获取设置项
pen_width = settings.get("pen_width")
pen_color = settings.get("pen_color")
print(f"当前笔尖粗细: {pen_width}")
print(f"当前笔尖颜色: RGB({pen_color[0]},{pen_color[1]},{pen_color[2]})")

# 修改设置项
settings.set("pen_width", 5)
settings.set("pen_color", [255, 0, 0])  # 红色

# 保存设置
settings.save()

# 重置为默认设置
settings.reset_to_default()
```

### 6. ui/settings/default_settings.json

**功能说明**：默认设置定义文件（JSON格式），提供应用程序的默认设置值。这是唯一的默认设置源，程序不包含任何内置默认值。

**文件内容**：
```json
{
    "pen_width": 3,
    "pen_color": [0, 120, 255]
}
```

**使用方法**：
文件由设置管理器（settings.py）自动加载，通常不需要直接操作此文件。如需修改默认设置，应当编辑此文件。

**重要说明**：
这个文件是必需的，程序启动时会尝试从这里加载所有默认设置。如果文件不存在或格式不正确，程序将无法正常启动。

### 7. ui/gestures/gestures.py

**功能说明**：手势库管理模块，负责保存和加载用户手势库。

**主要类和方法**：
- `GestureLibrary`：手势库管理器类
  - `__init__()`：初始化手势库管理器
  - `load()`：从文件加载手势库
  - `save()`：保存手势库到文件
  - `get_gesture(name)`：获取指定名称的手势
  - `get_gesture_by_id(gesture_id)`：根据ID获取手势
  - `get_all_gestures()`：获取所有手势
  - `get_all_gestures_sorted()`：获取按ID排序的所有手势
  - `get_gesture_by_direction(direction)`：根据方向序列获取匹配的手势
  - `add_gesture(name, direction, action_type, action_value, gesture_id=None)`：添加或更新手势
  - `update_gesture_name(old_name, new_name)`：更新手势名称
  - `remove_gesture(name)`：删除手势并重新排序剩余手势的ID
  - `reset_to_default()`：重置为默认手势库
  - `list_gestures()`：获取所有手势名称列表
  - `has_changes()`：检查是否有未保存的更改

**数据结构**：
- 手势使用一个整数ID进行标识，从1开始按顺序排列，ID决定手势在列表中的显示顺序
- 手势对象的结构：
  ```json
  {
    "id": 1,              // 整数ID，从1开始，按顺序排列
    "direction": "上-下",   // 手势方向序列
    "action": {
      "type": "shortcut",  // 动作类型
      "value": "ctrl+c"    // 动作值
    }
  }
  ```

**特性说明**：
- 支持从用户配置目录加载和保存手势库
- 为每个手势分配唯一的整数ID，ID从1开始连续编号
- ID决定手势在列表中的显示顺序，ID越小排在越前面
- 删除手势后自动重排后续手势的ID，保持ID的连续性
- 提供重命名功能，在变更手势名称时保留所有手势属性
- 通过名称、ID或方向序列多种方式查找手势
- 跟踪更改状态，确保在有未保存更改时提示用户
- 内置默认手势库，包含常用的快捷键手势
- 支持重置为默认手势库
- 提供获取全部手势和手势名称列表等批量操作

**使用方法**：
```python
from ui.gestures.gestures import get_gesture_library

# 获取手势库实例
gesture_library = get_gesture_library()

# 获取所有手势
all_gestures = gesture_library.get_all_gestures()

# 获取按ID排序的所有手势
sorted_gestures = gesture_library.get_all_gestures_sorted()

# 添加新手势
gesture_library.add_gesture(
    name="复制",
    direction="右-下",
    action_type="shortcut",
    action_value="ctrl+c"
)

# 更新手势名称
gesture_library.update_gesture_name("复制", "复制文本")

# 根据方向获取手势
name, gesture = gesture_library.get_gesture_by_direction("右-下")
if gesture:
    print(f"找到手势：{name}")

# 删除手势并自动重排后续ID
gesture_library.remove_gesture("复制文本")

# 保存手势库
gesture_library.save()

# 检查是否有未保存的更改
if gesture_library.has_changes():
    print("有未保存的更改")
```

### 8. ui/gestures/gestures_tab.py

**功能说明**：手势管理选项卡，提供手势库的管理功能，包括添加、编辑、删除和重置手势。

**主要类和方法**：
- `GesturesTab`：手势管理选项卡类，继承自`QWidget`
  - `initUI()`：初始化用户界面
  - `createGestureCardsList(parent_layout)`：创建左侧手势卡片列表区域
  - `createGestureEditor(parent_layout)`：创建右侧手势编辑区域
  - `updateGestureCards(maintain_selected)`：更新手势卡片列表，按照ID顺序排列卡片，支持保持选中状态
  - `onGestureCardClicked(card)`：处理手势卡片点击事件
  - `addNewGesture()`：添加新手势，分配新的ID
  - `deleteGesture()`：删除手势，并重排后续手势的ID
  - `resetGestures()`：重置为默认手势库
  - `saveGestureLibrary()`：保存手势库
  - `onFormChanged()`：表单内容变化时自动应用更改，实时更新左侧卡片显示
  - `name_input_textChanged()`：名称输入框文本变化时的处理
  - `direction_combo_changed()`：方向下拉框变化时的处理
  - `action_type_combo_changed()`：动作类型下拉框变化时的处理
  - `action_value_input_textChanged()`：动作值输入框文本变化时的处理

**特性说明**：
- 左侧显示手势卡片列表，按照ID顺序排列，ID越小排在越前面
- 右侧为编辑区域，提供手势详情的编辑功能
- 支持添加、编辑、删除和重置手势操作
- 卡片点击后显示详细信息，可以编辑手势属性
- **智能实时更新**：仅在编辑已有手势时，表单字段（名称、方向、动作类型、动作值）的变更会**即时**反映到左侧卡片列表中
- 未选择任何手势时，表单变更不会自动应用，需要用户点击"添加新手势"按钮才会创建新手势
- 左侧底部的"保存更改"按钮用于保存所有手势更改
- 添加新手势时使用当前表单内容创建，并自动分配新的ID（当前最大ID+1）
- 删除手势后会自动重排所有后续手势的ID，保持ID的连续性
- 支持更改手势名称而不丢失关联数据，基于手势ID系统
- 编辑手势时保持其在列表中的原有位置，不会改变ID
- 支持智能检测重命名操作，确保卡片位置和ID保持一致

**使用方法**：
```python
from ui.gestures.gestures_tab import GesturesTab

# 创建手势管理选项卡
gestures_tab = GesturesTab()

# 添加到界面
# ...
```

### 9. core/drawer.py

**功能说明**：绘画核心模块，实现了透明绘制覆盖层、右键绘制功能和绘制管理。

**主要类和方法**：
- `DrawingSignals`：信号类，处理线程间通信
- `TransparentDrawingOverlay`：透明绘制覆盖层
  - `set_pen_width(width)`：设置笔尖粗细
  - `set_pen_color(color)`：设置笔尖颜色
  - `startDrawing(x, y, pressure)`：开始绘制，同时停止任何正在进行的淡出效果
  - `continueDrawing(x, y, pressure)`：继续绘制轨迹
  - `stopDrawing()`：停止绘制并开始淡出效果，同时分析手势并执行
  - `get_stroke_direction(stroke_id)`：获取指定笔画的方向
- `DrawingManager`：绘制管理器
  - `start()`：开始绘制功能，启动监听，并从设置加载笔尖粗细和颜色
  - `stop()`：停止绘制功能，清理资源
  - `update_settings()`：更新设置参数，无需重启绘制功能即可应用修改的参数（如笔尖粗细和颜色）
  - `get_last_direction()`：获取最后一次绘制的方向

**特性说明**：
- 所有设置值完全从settings模块获取，不存在内置默认值
- 如果设置模块不可用，会使用当前已设置的值继续工作，而不会回退到固定的默认值
- 绘制结束后会自动分析笔画方向，并在手势库中查找匹配的手势进行执行
- 手势执行功能集成在绘制流程中，无需额外调用

**使用方法**：
```python
from core.drawer import DrawingManager

# 创建绘制管理器
drawer = DrawingManager()

# 开始绘制功能
drawer.start()  # 此时可以使用鼠标右键进行绘制

# 更新设置参数（无需重启绘制功能）
drawer.update_settings()  # 从设置中重新读取参数并应用

# 获取最后一次绘制的方向
direction = drawer.get_last_direction()
print(f"最后绘制的方向: {direction}")

# 停止绘制功能
drawer.stop()
```

### 10. core/stroke_analyzer.py

**功能说明**：笔画分析模块，负责分析用户绘制的笔画轨迹，识别方向变化和绘制趋势。

**主要类和方法**：
- `StrokeAnalyzer`：笔画分析器
  - `analyze_direction(points)`：分析一系列点的方向变化，返回方向序列和方向详细信息
  - `get_direction_description(direction_str)`：将方向字符串转换为人类可读的描述
  - `_segment_stroke(coords)`：将笔画分割为不同方向的段
  - `_analyze_segment_directions(coords)`：分析一个段内的方向分布
  - `_determine_direction(dx, dy)`：根据位移确定基本方向

**使用方法**：
```python
from core.stroke_analyzer import StrokeAnalyzer

# 创建分析器
analyzer = StrokeAnalyzer()

# 假设有一系列点 [(x1,y1,pressure1,time1,id1), (x2,y2,pressure2,time2,id1), ...]
points = [(100, 100, 0.5, 1631234567.89, 1), (150, 120, 0.6, 1631234567.95, 1), ...]

# 分析方向
direction_sequence, direction_details = analyzer.analyze_direction(points)
print(f"方向序列: {direction_sequence}")
print(f"方向详细信息: {direction_details}")

# 获取人类可读描述
description = analyzer.get_direction_description(direction_sequence)
print(f"描述: {description}")  # 例如: "先右后上"
```

**方向常量**：
- `UP`：上
- `DOWN`：下
- `LEFT`：左
- `RIGHT`：右
- `UP_LEFT`：左上
- `UP_RIGHT`：右上
- `DOWN_LEFT`：左下
- `DOWN_RIGHT`：右下

### 11. core/gesture_executor.py

**功能说明**：手势执行模块，负责根据识别的手势方向执行相应的操作，目前主要支持快捷键操作。

**主要类和方法**：
- `GestureExecutor`：手势执行器类
  - `execute_gesture(direction)`：根据方向序列执行对应的手势动作
  - `_execute_shortcut(shortcut_str)`：执行快捷键操作
  - `_press_keys(modifier_keys, regular_keys)`：内部方法，按下并释放指定的按键
- `get_gesture_executor()`：获取手势执行器的全局单例实例

**支持的动作类型**：
- `shortcut`：执行键盘快捷键，如"ctrl+c"、"alt+tab"等

**使用方法**：
```python
from core.gesture_executor import get_gesture_executor

# 获取手势执行器
executor = get_gesture_executor()

# 执行特定方向的手势
result = executor.execute_gesture("右-下")
print(f"手势执行{'成功' if result else '失败'}")
```

**特性说明**：
- 支持组合键快捷方式（如Ctrl+Alt+Del）
- 使用独立线程执行按键操作，不会阻塞主线程
- 支持大量特殊键（如功能键、修饰键等）
- 自动处理按键的正确顺序（先修饰键，后普通键）和释放顺序（先普通键，后修饰键）
- 集成到绘画模块中，能够自动识别并执行与绘制方向匹配的手势
- 从ui.gestures.gestures模块获取手势库，确保使用统一的手势管理系统

### 12. core/logger.py

**功能说明**：日志记录模块，提供统一的日志记录功能，支持不同日志级别和输出目标。

**主要类和方法**：
- `Logger`：日志记录工具类
  - `setup_logger()`：设置日志记录器
  - `debug(message)`：记录调试级别日志
  - `info(message)`：记录信息级别日志
  - `warning(message)`：记录警告级别日志
  - `error(message)`：记录错误级别日志
  - `critical(message)`：记录严重错误级别日志
  - `exception(message)`：记录异常信息，包含堆栈跟踪
- `get_logger(module_name)`：获取一个命名的日志记录器

**使用方法**：
```python
from core.logger import get_logger

# 获取一个命名的日志记录器
logger = get_logger("MyModule")

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")

# 记录异常
try:
    # 某些可能导致异常的代码
    result = 1 / 0
except Exception as e:
    logger.exception(f"发生异常: {e}")
```

**日志配置**：
- 日志文件存储在用户目录下的`.gestrokey/log/`文件夹中
- 日志文件按日期命名：`YYYY-MM-DD.log`
- 日志同时输出到控制台和文件（如可写）
- 日志格式：`[时间] [级别] [模块名] - 消息`

## 代码优化说明

GestroKey代码库遵循以下优化原则，确保代码高效、简洁和可维护：

1. **代码清理**：
   - 删除所有未使用的导入语句
   - 移除注释掉的废弃代码块
   - 消除未使用的变量和函数
   - 简化冗余的条件判断和循环

2. **资源管理**：
   - 及时释放不再需要的资源
   - 使用上下文管理器（with语句）处理文件操作
   - 在适当的时机卸载UI元素和事件处理器
   - 遵循对象生命周期管理最佳实践

3. **性能优化**：
   - 避免深层嵌套循环
   - 减少不必要的对象创建
   - 优化频繁调用的方法
   - 使用更高效的数据结构和算法

4. **内存管理**：
   - 避免大型对象的不必要复制
   - 限制缓存大小
   - 清理不再使用的引用
   - 按需加载资源

5. **UI响应性**：
   - 将耗时操作放入后台线程
   - 避免在UI线程中进行阻塞操作
   - 使用信号槽机制保持UI响应
   - 优化绘制操作，减少重绘开销

6. **模块化设计**：
   - 遵循单一职责原则
   - 使用适当的抽象和封装
   - 设计清晰的接口
   - 避免紧耦合

这些优化措施共同确保GestroKey能够在各种环境下高效运行，同时保持代码的可读性和可维护性。

## 一般使用流程

1. 运行主程序
```bash
python src/main.py
```

2. 在控制台选项卡中点击"开始绘制"按钮
3. 使用鼠标右键进行绘制（按住右键移动）
4. 绘制完成后释放右键，系统会自动识别绘制方向
5. 如果识别的方向与手势库中的手势匹配，系统会自动执行相应的操作（如快捷键）
6. 可以在设置选项卡中调整笔尖粗细和颜色，设置实时应用而无需重启绘制功能
7. 可以在手势管理选项卡中查看、添加、编辑和删除手势：
   - 左侧卡片列表展示所有可用手势
   - 点击卡片可在右侧编辑区域修改手势
   - 可添加新手势、删除现有手势或重置为默认手势库
8. 点击"停止绘制"按钮关闭绘制功能
9. 点击"退出程序"按钮退出应用

## 设置管理

用户设置保存在以下位置：
- Windows: `%USERPROFILE%\.gestrokey\config\settings.json`
- Linux/Mac: `~/.gestrokey/config/settings.json`

设置项包括：
- `pen_width`：笔尖粗细（默认为3像素）
- `pen_color`：笔尖颜色，RGB格式的数组（默认为[0, 120, 255]，蓝色）

**重要提示**：所有默认设置都保存在`default_settings.json`文件中，应用程序不包含任何硬编码的默认值。

## 手势系统

GestroKey实现了完整的手势识别和执行系统：

1. **手势识别流程**：
   - 用户使用鼠标右键绘制手势
   - 系统记录绘制的点坐标
   - StrokeAnalyzer模块分析绘制轨迹，识别方向变化
   - 生成方向序列描述（如"上-右-下"）

2. **手势执行流程**：
   - 系统将识别出的方向序列与手势库中定义的手势进行匹配
   - 如找到匹配的手势，获取其对应的动作类型和值
   - GestureExecutor模块执行相应的动作（如按下快捷键）
   - 执行结果记录到日志中

3. **手势库管理**：
   - 手势库存储于`%USERPROFILE%\.gestrokey\config\gestures.json`
   - 手势库管理模块位于`ui/gestures/gestures.py`，提供完整的手势管理API
   - 默认手势库定义在`ui/gestures/default_gestures.json`
   - 如果文件不存在或损坏，系统自动创建包含常用操作的默认手势库
   - 通过手势管理选项卡(`ui/gestures/gestures_tab.py`)提供可视化的手势管理界面
   - 采用左右分栏布局，左侧使用卡片组件展示手势，右侧为编辑区域
   - 支持对手势库的添加、编辑、删除和重置操作
   - 每个手势有一个从1开始的整数ID，ID决定手势在列表中的显示顺序
   - 删除手势后系统会自动重排后续手势的ID，保持ID的连续性
   - 卡片式界面提供直观的视觉反馈，按照ID顺序排列显示手势

4. **支持的手势动作**：
   - 快捷键执行：支持绝大多数单键和组合键操作
   - 未来可扩展支持：程序启动、文件操作、自定义脚本等

**手势示例**：
- "右-下"手势执行"复制"操作（Ctrl+C）
- "下-右"手势执行"粘贴"操作（Ctrl+V）
- "左-上"手势执行"撤销"操作（Ctrl+Z）
- "上-下"手势执行"刷新"操作（F5）

## UI组件系统

GestroKey使用模块化UI组件系统，所有自定义UI组件都位于`ui/components`目录下：

- `button.py`：精美的动画按钮组件，可用于替代标准QPushButton
  - 特性：扁平化设计、文字动画效果、点击缩放、阴影效果
  - 优点：现代感的UI体验，简单的接口，可单独测试
  - 应用：已在整个应用程序中替代标准按钮，包括主窗口、控制台和设置面板

- `card.py`：精美的卡片容器组件，可容纳其他UI组件
  - 特性：扁平化设计、悬停和点击动画、选中状态、动态阴影效果
  - 优点：整洁的信息展示，交互反馈，一致的视觉风格
  - 应用：用于手势管理选项卡中展示手势信息，替代传统表格视图

- `side_tab.py`：左侧垂直选项卡组件，替代标准QTabWidget
  - 特性：垂直布局、平滑切换动画、选中状态指示、扁平化设计
  - 优点：更好的空间利用率，更现代的界面布局，符合主题风格
  - 应用：已用于主窗口，整合了控制台选项卡和设置选项卡

**使用组件的优势**：
- 统一的视觉风格
- 可重复使用的代码
- 简化的接口
- 独立测试能力
- 提升用户体验
- 一致的动画效果
- 更好的空间布局和组织

## 编程接口使用示例

```python
from core.drawer import DrawingManager
from core.logger import get_logger
from ui.settings.settings import get_settings
from ui.components.button import AnimatedButton
from ui.components.card import CardWidget
from ui.gestures.gestures import get_gesture_library

# 创建日志记录器
logger = get_logger("MyApp")

# 获取设置
settings = get_settings()
pen_width = settings.get("pen_width")
pen_color = settings.get("pen_color")
logger.info(f"使用笔尖粗细: {pen_width}")
logger.info(f"使用笔尖颜色: RGB({pen_color[0]},{pen_color[1]},{pen_color[2]})")

# 获取手势库
gesture_lib = get_gesture_library()
gestures = gesture_lib.get_all_gestures()
logger.info(f"已加载 {len(gestures)} 个手势")

# 创建绘制管理器
drawer = DrawingManager()

# 创建自定义按钮
start_button = AnimatedButton("开始绘制", primary_color=[41, 128, 185])
stop_button = AnimatedButton("停止绘制", primary_color=[52, 73, 94])

# 创建手势信息卡片
gesture_card = CardWidget(title="复制")
gesture_label = QLabel("方向: 右-下\n动作: Ctrl+C")
gesture_label.setAlignment(Qt.AlignCenter)
gesture_card.add_widget(gesture_label)
gesture_card.clicked.connect(on_card_clicked)

# 连接信号
start_button.clicked.connect(drawer.start)
stop_button.clicked.connect(drawer.stop)

try:
    # 启动绘制功能
    drawer.start()  # 此时会自动应用笔尖粗细和颜色设置
    logger.info("绘制功能已启动，可以使用鼠标右键绘制")
    
    # 应用程序主循环
    # ...
    
    # 修改设置
    settings.set("pen_width", 5)
    settings.set("pen_color", [255, 0, 0])  # 红色
    settings.save()
    
    # 应用新设置，无需重启绘制功能
    drawer.update_settings()
    logger.info("已更新笔尖设置")
    
    # 获取方向信息
    direction = drawer.get_last_direction()
    logger.info(f"检测到的方向: {direction}")
    
    # 停止绘制功能
    drawer.stop()
    logger.info("绘制功能已停止")
    
except Exception as e:
    logger.exception(f"应用运行时发生错误: {e}")
```

### 5. assets/images 目录

**功能说明**：存放应用程序使用的图像资源，包括图标和SVG矢量图形。

**包含文件**：
- `icon.svg`：应用主图标，用于窗口标题栏和任务栏
- `console.svg`：控制台选项卡图标
- `settings.svg`：设置选项卡图标
- `gestures.svg`：手势管理选项卡图标

**注意事项**：
- 所有SVG文件都经过优化，移除了空的image标签和不必要的元素，避免Qt SVG渲染器产生"Image filename is empty"警告
- 选项卡图标使用本地SVG文件而非系统主题图标，确保在不同操作系统上一致显示
- 图标推荐使用SVG格式，以获得更好的缩放效果和显示质量

**如何使用**：
```python
# 加载应用图标
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'images', 'icon.svg')
if os.path.exists(icon_path):
    app_icon = QIcon(icon_path)
    self.setWindowIcon(app_icon)
    
# 加载选项卡图标
icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'images')
console_icon_path = os.path.join(icons_dir, 'console.svg')
console_icon = QIcon(console_icon_path) if os.path.exists(console_icon_path) else QIcon()
```

**SVG问题排查**：
如果遇到SVG渲染警告"QSvgHandler: Image filename is empty"，请检查SVG文件中是否包含空的image标签或引用了不存在的外部资源，移除这些元素可以解决警告问题。 