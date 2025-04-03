# GestroKey 源代码目录说明

本文档详细介绍了GestroKey项目`src`目录下各文件和文件夹的功能及使用方法。

## 目录结构

```
src/
├── core/                    # 核心功能模块
│   ├── drawer.py            # 绘画核心模块
│   ├── stroke_analyzer.py   # 笔画分析模块
│   ├── gesture_library.py   # 手势库管理模块
│   ├── gesture_executor.py  # 手势执行模块
│   ├── default_gestures.json # 默认手势库配置文件
│   └── logger.py            # 日志记录模块
├── ui/                      # 用户界面模块
│   ├── console.py           # 控制台选项卡
│   ├── components/          # UI组件模块
│   │   ├── button.py        # 自定义动画按钮组件
│   │   └── side_tab.py      # 左侧选项卡组件
│   └── settings/            # 设置相关界面
│       ├── settings_tab.py  # 设置选项卡
│       ├── settings.py      # 设置管理模块
│       └── default_settings.json # 默认设置定义（JSON格式）
└── main.py                  # 主程序入口
```

## 详细说明

### 1. main.py

**功能说明**：程序的主入口文件，提供带有选项卡的图形用户界面，包含控制台和设置界面。

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

### 2. ui/console.py

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

### 3. ui/components/button.py

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
  - `addTab(widget, text, icon=None)`：添加新的选项卡
  - `setCurrentIndex(index)`：设置当前选项卡，触发动画切换
  - `currentIndex()`：获取当前选项卡索引
  - `widget(index)`：获取指定索引的内容窗口
  - `setTabText(index, text)`：设置指定索引的选项卡文本
  - `setTabIcon(index, icon)`：设置指定索引的选项卡图标

**特性说明**：
- 精美的扁平化设计，与应用主题风格一致
- 垂直布局的选项卡位于窗口左侧
- 选项卡切换时的平滑动画过渡效果
- 选项卡支持图标和文本
- 选中状态和悬停状态的动画效果
- 选中选项卡的高亮指示器动画
- 自动适应内容区域大小
- 可直接运行文件查看示例效果，便于单独调试
- 已应用于整个应用程序的主界面，替代了标准的QTabWidget

**使用方法**：
```python
from ui.components.side_tab import SideTabWidget

# 创建左侧选项卡组件
tab_widget = SideTabWidget()

# 添加带图标的选项卡
console_tab = QWidget()  # 或任何QWidget子类
console_icon = QIcon("path/to/icon.png")  # 也可使用QIcon.fromTheme获取系统图标
tab_widget.addTab(console_tab, "控制台", console_icon)

# 添加不带图标的选项卡
settings_tab = QWidget()
tab_widget.addTab(settings_tab, "设置")

# 切换到指定选项卡
tab_widget.setCurrentIndex(1)  # 切换到第二个选项卡（索引从0开始）

# 监听选项卡切换事件
tab_widget.currentChanged.connect(onTabChanged)

# 添加到界面布局
layout.addWidget(tab_widget)
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

### 7. core/drawer.py

**功能说明**：绘画核心模块，实现了透明绘制覆盖层、右键绘制功能和绘制管理。

**主要类和方法**：
- `DrawingSignals`：信号类，处理线程间通信
- `TransparentDrawingOverlay`：透明绘制覆盖层
  - `set_pen_width(width)`：设置笔尖粗细
  - `set_pen_color(color)`：设置笔尖颜色
  - `startDrawing(x, y, pressure)`：开始绘制，同时停止任何正在进行的淡出效果
  - `continueDrawing(x, y, pressure)`：继续绘制轨迹
  - `stopDrawing()`：停止绘制并开始淡出效果
  - `get_stroke_direction(stroke_id)`：获取指定笔画的方向
- `DrawingManager`：绘制管理器
  - `start()`：开始绘制功能，启动监听，并从设置加载笔尖粗细和颜色
  - `stop()`：停止绘制功能，清理资源
  - `update_settings()`：更新设置参数，无需重启绘制功能即可应用修改的参数（如笔尖粗细和颜色）
  - `get_last_direction()`：获取最后一次绘制的方向

**特性说明**：
- 所有设置值完全从settings模块获取，不存在内置默认值
- 如果设置模块不可用，会使用当前已设置的值继续工作，而不会回退到固定的默认值

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

**特性说明**：
- 鼠标右键按住可以绘制
- 绘制完成后有淡出动画效果
- 自动记录绘制点和分析方向
- 自动计算压力值（基于移动速度）
- 笔尖粗细和颜色可通过设置调整，每次启动时自动从设置加载
- 支持动态更新参数，在设置变更后无需重启绘制功能
- 修复了淡出效果冲突问题：当前一个线条淡出效果还在进行时，开始新线条绘制会自动停止淡出效果，确保新线条正常显示

### 8. core/stroke_analyzer.py

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

### 9. core/gesture_library.py

**功能说明**：手势库管理模块，负责加载、保存和管理用户定义的手势，包括对手势的增加、删除、查询等操作。

**主要类和方法**：
- `GestureLibrary`：手势库管理器类
  - `load()`：从文件加载手势库，如不存在则创建默认手势库
  - `save()`：保存手势库到文件
  - `get_gesture(name)`：根据名称获取特定手势
  - `get_gesture_by_direction(direction)`：根据方向序列获取匹配的手势
  - `add_gesture(name, direction, action_type, action_value)`：添加新手势
  - `remove_gesture(name)`：删除指定名称的手势
  - `list_gestures()`：获取所有手势名称列表
  - `reset_to_default()`：重置为默认手势库
  - `_load_default_gestures()`：加载默认手势库
- `get_gesture_library()`：获取手势库的全局单例实例

**使用方法**：
```python
from core.gesture_library import get_gesture_library

# 获取手势库
gesture_lib = get_gesture_library()

# 获取所有手势
gestures = gesture_lib.list_gestures()
print(f"当前手势库中共有 {len(gestures)} 个手势")

# 获取特定手势
copy_gesture = gesture_lib.get_gesture("复制")
if copy_gesture:
    print(f"复制手势的方向是: {copy_gesture['direction']}")
    print(f"复制手势执行的动作是: {copy_gesture['action']['value']}")

# 添加新手势
gesture_lib.add_gesture(
    name="我的手势",
    direction="上-右-下",
    action_type="shortcut",
    action_value="ctrl+alt+t"
)

# 根据方向获取手势
name, gesture = gesture_lib.get_gesture_by_direction("上-右-下")
if gesture:
    print(f"识别到手势: {name}")

# 保存手势库
gesture_lib.save()

# 重置为默认手势库
gesture_lib.reset_to_default()
```

**手势库结构**：
- 手势库以JSON格式存储在用户目录下的`.gestrokey/config/gestures.json`文件中
- 每个手势包含名称、方向序列和要执行的动作
- 如果手势库文件不存在或损坏，程序会自动创建默认手势库

### 10. core/default_gestures.json

**功能说明**：默认手势库配置文件（JSON格式），包含预定义的常用手势及其对应的操作，作为初始手势库或备用手势库。

**文件内容**：包含以下预定义手势：
- 复制 (Ctrl+C)：右-下方向
- 粘贴 (Ctrl+V)：下-右方向
- 剪切 (Ctrl+X)：左-下方向
- 撤销 (Ctrl+Z)：左-上方向
- 重做 (Ctrl+Y)：右-上方向
- 保存 (Ctrl+S)：下-左方向
- 全选 (Ctrl+A)：上-左方向
- 新建 (Ctrl+N)：上-右方向
- 刷新 (F5)：上-下方向

**使用方法**：
文件由手势库管理器（gesture_library.py）自动加载，通常不需要直接操作此文件。当需要修改默认手势库时，可编辑此文件。

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
7. 点击"停止绘制"按钮关闭绘制功能
8. 点击"退出程序"按钮退出应用

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
   - 如果文件不存在或损坏，系统自动创建包含常用操作的默认手势库
   - 支持对手势库的修改、扩展和重置

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

# 创建日志记录器
logger = get_logger("MyApp")

# 获取设置
settings = get_settings()
pen_width = settings.get("pen_width")
pen_color = settings.get("pen_color")
logger.info(f"使用笔尖粗细: {pen_width}")
logger.info(f"使用笔尖颜色: RGB({pen_color[0]},{pen_color[1]},{pen_color[2]})")

# 创建绘制管理器
drawer = DrawingManager()

# 创建自定义按钮
start_button = AnimatedButton("开始绘制", primary_color=[41, 128, 185])
stop_button = AnimatedButton("停止绘制", primary_color=[52, 73, 94])

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