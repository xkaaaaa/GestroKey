# GestroKey 源代码目录说明

本文档详细介绍了GestroKey项目`src`目录下各文件和文件夹的功能及使用方法。

## 目录结构

```
src/
├── core/                    # 核心功能模块
│   ├── drawer.py            # 绘画核心模块
│   ├── stroke_analyzer.py   # 笔画分析模块
│   └── logger.py            # 日志记录模块
└── main.py                  # 主程序入口
```

## 详细说明

### 1. main.py

**功能说明**：程序的主入口文件，提供了简洁的图形用户界面，用于控制绘画功能的开启和关闭。

**主要类和方法**：
- `GestroKeyApp`：主窗口类，继承自`QMainWindow`
  - `initUI()`：初始化用户界面，设置窗口属性和控件
  - `start_drawing()`：开始绘制功能
  - `stop_drawing()`：停止绘制功能
  - `closeEvent(event)`：处理窗口关闭事件

**使用方法**：
```python
# 直接运行该文件启动应用程序
python src/main.py
```

**GUI控件**：
- 开始绘制按钮：启动绘制功能，激活鼠标右键绘制
- 停止绘制按钮：停止绘制功能，关闭绘制窗口
- 退出程序按钮：完全退出应用程序

### 2. core/drawer.py

**功能说明**：绘画核心模块，实现了透明绘制覆盖层、右键绘制功能和绘制管理。

**主要类和方法**：
- `DrawingSignals`：信号类，处理线程间通信
- `TransparentDrawingOverlay`：透明绘制覆盖层
  - `startDrawing(x, y, pressure)`：开始绘制
  - `continueDrawing(x, y, pressure)`：继续绘制轨迹
  - `stopDrawing()`：停止绘制并启动淡出效果
  - `get_stroke_direction(stroke_id)`：获取指定笔画的方向
- `DrawingManager`：绘制管理器
  - `start()`：开始绘制功能，启动监听
  - `stop()`：停止绘制功能，清理资源
  - `get_last_direction()`：获取最后一次绘制的方向

**使用方法**：
```python
from core.drawer import DrawingManager

# 创建绘制管理器
drawer = DrawingManager()

# 开始绘制功能
drawer.start()  # 此时可以使用鼠标右键进行绘制

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

### 3. core/stroke_analyzer.py

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

### 4. core/logger.py

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

2. 在GUI界面中点击"开始绘制"按钮
3. 使用鼠标右键进行绘制（按住右键移动）
4. 绘制完成后释放右键，绘制会有淡出效果
5. 完成后点击"停止绘制"按钮关闭绘制功能
6. 点击"退出程序"按钮退出应用

## 编程接口使用示例

```python
from core.drawer import DrawingManager
from core.logger import get_logger

# 创建日志记录器
logger = get_logger("MyApp")

# 创建绘制管理器
drawer = DrawingManager()

try:
    # 启动绘制功能
    drawer.start()
    logger.info("绘制功能已启动，可以使用鼠标右键绘制")
    
    # 应用程序主循环
    # ...
    
    # 获取方向信息
    direction = drawer.get_last_direction()
    logger.info(f"检测到的方向: {direction}")
    
    # 停止绘制功能
    drawer.stop()
    logger.info("绘制功能已停止")
    
except Exception as e:
    logger.exception(f"应用运行时发生错误: {e}")
``` 