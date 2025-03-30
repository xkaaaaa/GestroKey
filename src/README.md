# GestroKey 源代码目录说明

本文档详细介绍了GestroKey项目`src`目录下各文件和文件夹的功能及使用方法。

## 目录结构

```
src/
├── core/                    # 核心功能模块
│   ├── drawer.py            # 绘画核心模块
│   ├── stroke_analyzer.py   # 笔画分析模块
│   └── logger.py            # 日志记录模块
├── ui/                      # 用户界面模块
│   ├── console.py           # 控制台选项卡
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
- 设置选项卡：提供应用程序设置的配置，包括笔尖粗细设置

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

### 3. ui/settings/settings_tab.py

**功能说明**：设置选项卡模块，提供应用程序设置的配置界面。

**主要类和方法**：
- `SettingsTab`：设置选项卡类，继承自`QWidget`
  - `initUI()`：初始化设置选项卡界面
  - `pen_width_changed(value)`：处理笔尖粗细变化，并实时更新绘制管理器参数
  - `reset_settings()`：重置为默认设置，并更新绘制管理器参数
  - `save_settings()`：保存设置到文件，并更新绘制管理器参数
  - `_update_drawing_manager()`：内部方法，负责更新绘制管理器的参数
- `PenPreviewWidget`：笔尖预览小部件，显示笔尖粗细效果

**使用方法**：
```python
from ui.settings.settings_tab import SettingsTab

# 创建设置选项卡
settings = SettingsTab()

# 添加到界面
# ...
```

### 4. ui/settings/settings.py

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

**使用方法**：
```python
from ui.settings.settings import get_settings

# 获取设置管理器
settings = get_settings()

# 获取设置项
pen_width = settings.get("pen_width")
print(f"当前笔尖粗细: {pen_width}")

# 修改设置项
settings.set("pen_width", 5)

# 保存设置
settings.save()

# 重置为默认设置
settings.reset_to_default()
```

### 5. ui/settings/default_settings.json

**功能说明**：默认设置定义文件（JSON格式），提供应用程序的默认设置值。

**文件内容**：
```json
{
    "pen_width": 3
}
```

**使用方法**：
文件由设置管理器（settings.py）自动加载，通常不需要直接操作此文件。

### 6. core/drawer.py

**功能说明**：绘画核心模块，实现了透明绘制覆盖层、右键绘制功能和绘制管理。

**主要类和方法**：
- `DrawingSignals`：信号类，处理线程间通信
- `TransparentDrawingOverlay`：透明绘制覆盖层
  - `set_pen_width(width)`：设置笔尖粗细
  - `startDrawing(x, y, pressure)`：开始绘制，同时停止任何正在进行的淡出效果
  - `continueDrawing(x, y, pressure)`：继续绘制轨迹
  - `stopDrawing()`：停止绘制并开始淡出效果
  - `get_stroke_direction(stroke_id)`：获取指定笔画的方向
- `DrawingManager`：绘制管理器
  - `start()`：开始绘制功能，启动监听，并从设置加载笔尖粗细
  - `stop()`：停止绘制功能，清理资源
  - `update_settings()`：更新设置参数，无需重启绘制功能即可应用修改的参数（如笔尖粗细）
  - `get_last_direction()`：获取最后一次绘制的方向

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
- 笔尖粗细可通过设置调整，每次启动时自动从设置加载
- 支持动态更新参数，在设置变更后无需重启绘制功能
- 修复了淡出效果冲突问题：当前一个线条淡出效果还在进行时，开始新线条绘制会自动停止淡出效果，确保新线条正常显示

### 7. core/stroke_analyzer.py

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

### 8. core/logger.py

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
4. 绘制完成后释放右键，绘制会有淡出效果
5. 可以在前一个线条淡出效果还在进行时立即开始新的绘制，系统会自动处理冲突
6. 完成后点击"停止绘制"按钮关闭绘制功能
7. 可以在设置选项卡中调整笔尖粗细，设置实时应用而无需重启绘制功能
8. 点击"退出程序"按钮退出应用

## 设置管理

用户设置保存在以下位置：
- Windows: `%USERPROFILE%\.gestrokey\config\settings.json`
- Linux/Mac: `~/.gestrokey/config/settings.json`

设置项包括：
- `pen_width`：笔尖粗细（默认为3像素）

## 编程接口使用示例

```python
from core.drawer import DrawingManager
from core.logger import get_logger
from ui.settings.settings import get_settings

# 创建日志记录器
logger = get_logger("MyApp")

# 获取设置
settings = get_settings()
pen_width = settings.get("pen_width")
logger.info(f"使用笔尖粗细: {pen_width}")

# 创建绘制管理器
drawer = DrawingManager()

try:
    # 启动绘制功能
    drawer.start()  # 此时会自动应用笔尖粗细设置
    logger.info("绘制功能已启动，可以使用鼠标右键绘制")
    
    # 应用程序主循环
    # ...
    
    # 修改设置
    settings.set("pen_width", 5)
    settings.save()
    
    # 应用新设置，无需重启绘制功能
    drawer.update_settings()
    logger.info("已更新笔尖粗细设置")
    
    # 获取方向信息
    direction = drawer.get_last_direction()
    logger.info(f"检测到的方向: {direction}")
    
    # 停止绘制功能
    drawer.stop()
    logger.info("绘制功能已停止")
    
except Exception as e:
    logger.exception(f"应用运行时发生错误: {e}")
``` 