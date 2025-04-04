import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QSizePolicy, QSpacerItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor

try:
    from core.logger import get_logger
    from core.drawer import DrawingManager
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from version import APP_NAME  # 导入应用名称
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger
    from core.drawer import DrawingManager
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from version import APP_NAME  # 导入应用名称

class ConsoleTab(QWidget):
    """控制台选项卡，提供基本的绘制控制功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("ConsoleTab")
        
        # 状态变量
        self.drawing_manager = None
        self.is_drawing_active = False
        
        self.initUI()
        self.logger.debug("控制台选项卡初始化完成")
    
    def initUI(self):
        """初始化用户界面"""
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)  # 改为顶部对齐，与其他选项卡一致
        
        # 顶部空白间距，增加灵活性
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # 标题标签 - 去掉APP_NAME前缀
        title_label = QLabel("控制台")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(title_label)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("font-size: 10pt; margin-bottom: 20px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.status_label)
        
        # 使用单个按钮，根据状态切换文本和颜色
        self.action_button = AnimatedButton("开始绘制", primary_color=[41, 128, 185])  # 初始为蓝色"开始绘制"按钮
        self.action_button.setMinimumSize(150, 40)
        self.action_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.action_button.clicked.connect(self.toggle_drawing)
        layout.addWidget(self.action_button, 0, Qt.AlignCenter)
        
        # 方向信息标签
        self.direction_label = QLabel("最后一次绘制方向: -")
        self.direction_label.setStyleSheet("font-size: 10pt; margin-top: 20px;")
        self.direction_label.setAlignment(Qt.AlignCenter)
        self.direction_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.direction_label)
        
        # 添加说明文本
        info_label = QLabel("使用鼠标右键绘制手势，系统将自动识别并执行对应操作")
        info_label.setStyleSheet("font-size: 10pt; color: #666; margin-top: 15px;")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(info_label)
        
        # 底部空白间距，增加灵活性
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # 设置布局和大小策略
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 设置尺寸变化事件处理
        self.logger.debug("已启用自适应布局")
    
    def resizeEvent(self, event):
        """窗口尺寸变化事件处理，用于调整UI布局"""
        # 调用父类方法
        super().resizeEvent(event)
        
        # 可以在这里添加特定的尺寸调整逻辑
        self.logger.debug(f"控制台选项卡大小已调整: {self.width()}x{self.height()}")
    
    def toggle_drawing(self):
        """切换绘制状态"""
        if self.is_drawing_active:
            self.stop_drawing()
        else:
            self.start_drawing()
    
    def start_drawing(self):
        """开始绘制功能"""
        try:
            self.logger.info("启动绘制功能")
            
            # 创建绘制管理器（如果不存在）
            if not self.drawing_manager:
                self.drawing_manager = DrawingManager()
            
            # 开始绘制
            success = self.drawing_manager.start()
            
            if success:
                self.status_label.setText("绘制中 - 使用鼠标右键进行绘制")
                # 切换按钮为"停止绘制"，并改为红色
                self.action_button.setText("停止绘制")
                self.action_button.set_primary_color([220, 53, 69])  # 红色
                self.is_drawing_active = True
                self.logger.debug("绘制功能已启动")
                # 清空方向信息
                self.direction_label.setText("最后一次绘制方向: -")
            
        except Exception as e:
            self.logger.exception(f"启动绘制功能时发生错误: {e}")
            self.status_label.setText(f"启动失败: {str(e)}")
    
    def stop_drawing(self):
        """停止绘制功能"""
        if self.drawing_manager and self.is_drawing_active:
            try:
                self.logger.info("停止绘制功能")
                
                # 获取最后一次绘制的方向信息
                direction = self.drawing_manager.get_last_direction()
                self.direction_label.setText(f"最后一次绘制方向: {direction}")
                
                # 停止绘制
                success = self.drawing_manager.stop()
                
                if success:
                    self.status_label.setText("准备就绪")
                    # 切换按钮为"开始绘制"，并改为蓝色
                    self.action_button.setText("开始绘制")
                    self.action_button.set_primary_color([41, 128, 185])  # 蓝色
                    self.is_drawing_active = False
                    self.logger.debug("绘制功能已停止")
                
            except Exception as e:
                self.logger.exception(f"停止绘制功能时发生错误: {e}")
                self.status_label.setText(f"停止失败: {str(e)}")
    
    def closeEvent(self, event):
        """关闭事件处理"""
        self.stop_drawing()


if __name__ == "__main__":
    # 独立运行测试
    app = QApplication(sys.argv)
    widget = ConsoleTab()
    widget.show()
    sys.exit(app.exec_()) 