# GestroKey - 手势控制应用

GestroKey是一个基于PyQt5开发的手势控制应用程序，它允许用户通过定义和使用鼠标手势来控制Windows系统和应用程序。

## 主要功能

- **手势识别**: 识别用户绘制的鼠标手势并触发相应操作
- **操作控制**: 控制窗口最大化、最小化、前后切换等系统操作
- **自定义手势**: 允许用户创建和管理自定义手势
- **直观的用户界面**: 现代、简洁的用户界面，使用PyQt5构建
- **绘画效果优化**: 平滑的笔画绘制和渐隐动画效果
- **资源优化**: 使用对象池管理绘图对象，减少内存占用
- **高性能渲染**: 支持硬件加速和批量绘制，提高绘图性能

## 安装要求

1. Python 3.8+
2. 依赖库：见`requirements.txt`文件

## 安装步骤

```bash
# 克隆仓库
git clone https://github.com/xkxkaaaaa/GestroKey.git

# 进入项目目录
cd GestroKey

# 安装依赖
pip install -r requirements.txt
```

## 使用说明

1. **启动应用**：
   ```bash
   python src/main.py
   ```
   或使用调试模式:
   ```bash
   python src/main.py -d
   ```

2. **绘制手势**：按住鼠标右键并拖动以绘制手势
3. **管理手势**：在"手势管理"标签页中添加、编辑或删除手势
4. **调整设置**：在"设置"标签页中调整应用参数

## 项目结构

```
src/
├── app/              # 应用核心功能
│   ├── gesture_parser.py  # 手势解析模块
│   ├── ink_painter.py     # 墨水绘图模块
│   ├── log.py             # 日志模块
│   ├── operation_executor.py  # 操作执行器
│   └── __init__.py
├── ui/               # 用户界面组件
│   ├── pages/        # 页面组件
│   │   ├── console_page.py     # 控制台页面
│   │   ├── settings_page.py    # 设置页面
│   │   ├── gestures_page.py    # 手势管理页面
│   │   └── __init__.py
│   ├── utils/        # 工具类
│   │   ├── gesture_manager.py  # 手势管理器
│   │   ├── settings_manager.py # 设置管理器
│   │   └── __init__.py
│   ├── main_window.py # 主窗口组件
│   ├── sidebar.py    # 侧边栏组件
│   └── __init__.py
├── gestures.json     # 手势配置文件
├── settings.json     # 应用设置文件
└── main.py           # 应用入口
```

## 核心组件说明

- **ink_painter.py**: 绘图核心，处理鼠标轨迹捕获、笔画绘制和渐隐效果
- **gesture_parser.py**: 手势解析器，分析绘图轨迹并识别对应手势
- **operation_executor.py**: 执行识别到的手势对应操作
- **settings_manager.py**: 管理应用配置，保存/加载用户设置
- **gesture_manager.py**: 管理用户定义的手势和对应操作

## 手势识别原理

GestroKey使用方向序列匹配算法识别手势，通过以下步骤处理：

1. 捕获鼠标轨迹点
2. 对轨迹点进行平滑和简化处理
3. 将平滑后的轨迹转换为方向序列（上、下、左、右等）
4. 将方向序列与预定义手势库进行匹配
5. 执行匹配到的手势对应的操作

## 主要特点

- **高性能绘图**: 使用对象池和批量处理优化绘图性能
- **智能平滑**: 自适应平滑算法，保证手势绘制流畅
- **资源管理**: 智能管理内存和CPU资源，减少系统负担
- **易扩展**: 模块化设计，便于添加新功能和自定义操作

## 贡献指南

欢迎贡献代码、报告问题或提出新功能建议。请fork本仓库并提交PR。

## 许可证

本项目使用GNU通用公共许可证第3版（GPLv3）- 详见LICENSE文件 