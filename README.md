# GestroKey - 手势控制应用

GestroKey是一个基于PyQt5开发的手势控制应用程序，它允许用户通过定义和使用鼠标手势来控制Windows系统和应用程序。

## 主要功能

- **手势识别**: 识别用户绘制的鼠标手势并触发相应操作
- **操作控制**: 控制窗口最大化、最小化、前后切换等系统操作
- **自定义手势**: 允许用户创建和管理自定义手势
- **直观的用户界面**: 现代、简洁的用户界面，使用PyQt5构建
- **系统托盘支持**: 支持最小化到系统托盘，在后台运行
- **配置设置**: 提供丰富的设置选项，包括绘制参数、手势灵敏度等

## 截图

*截图将在完成后添加*

## 安装

### 依赖项

- Python 3.6+
- PyQt5
- PyWin32（用于Windows系统交互）

### 安装步骤

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/GestroKey.git
   cd GestroKey
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

3. 运行应用：
   ```
   cd src
   python main.py
   ```

## 使用说明

1. **启动应用**：进入src目录运行main.py或使用已编译的可执行文件
2. **绘制手势**：按住鼠标右键并拖动以绘制手势
3. **管理手势**：在"手势管理"标签页中添加、编辑或删除手势
4. **调整设置**：在"设置"标签页中调整应用参数
5. **最小化到托盘**：点击"最小化到托盘"按钮或关闭窗口，应用将继续在后台运行

## 自定义手势

GestroKey允许您创建自定义手势：

1. 打开"手势管理"标签页
2. 点击"添加手势"按钮
3. 输入手势名称
4. 指定手势方向（例如：up,down,left,right）
5. 选择触发的操作
6. 点击"确定"保存手势

## 项目结构

```
GestroKey/
└── src/              # 项目源代码
    ├── app/              # 应用核心功能
    │   └── log.py        # 日志模块
    ├── ui/               # 用户界面组件
    │   ├── assets/       # 资源文件
    │   │   └── icons/    # 图标资源
    │   ├── pages/        # 页面组件
    │   │   ├── console_page.py     # 控制台页面
    │   │   ├── settings_page.py    # 设置页面
    │   │   └── gestures_page.py    # 手势管理页面
    │   ├── utils/        # 工具类
    │   │   ├── gesture_manager.py  # 手势管理器
    │   │   └── settings_manager.py # 设置管理器
    │   ├── sidebar.py    # 侧边栏组件
    │   └── main_window.py # 主窗口组件
    ├── main.py           # 应用入口
    ├── settings.json     # 设置文件
    ├── gestures.json     # 手势配置文件
    └── README.md         # 项目说明文档
```

## 许可证

MIT

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issues
- 发送邮件至：your.email@example.com

## 贡献

欢迎贡献代码、报告问题或提出功能建议。请通过Pull Request或Issue参与项目开发。