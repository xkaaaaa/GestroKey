import os
import sys
import logging
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QSizePolicy
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QCursor

# 导入日志模块
try:
    from app.log import log
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log

# 导入版本信息
try:
    from version import __version__, __title__, __copyright__, get_about_text
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from version import __version__, __title__, __copyright__, get_about_text

class TitleBar(QFrame):
    """自定义标题栏"""
    
    # 定义信号
    windowClose = pyqtSignal()  # 窗口关闭信号
    windowMinimize = pyqtSignal()  # 窗口最小化信号
    windowMaximize = pyqtSignal()  # 窗口最大化信号
    
    def __init__(self, parent=None):
        """初始化标题栏
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # 设置固定高度
        self.setFixedHeight(48)
        
        # 设置标题栏样式
        self.setStyleSheet("""
            TitleBar {
                background-color: #F8F9FA;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: 1px solid #E0E4E8;
            }
            
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2D3748;
            }
            
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
            
            QToolButton:pressed {
                background-color: rgba(0, 0, 0, 0.1);
            }
            
            #closeButton:hover {
                background-color: #E53E3E;
            }
            
            #closeButton:hover:pressed {
                background-color: #C53030;
            }
            
            #closeButton:hover .qicon {
                color: white;
            }
        """)
        
        # 初始化布局
        self.init_ui()
        
        # 跟踪鼠标
        self.setMouseTracking(True)
        
        # 标记拖动状态
        self.dragging = False
        self.drag_start_position = None
        
        log.debug("标题栏初始化完成")
        
    def init_ui(self):
        """初始化UI组件"""
        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)
        
        # 应用图标
        self.icon_label = QLabel()
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    "assets", "icons", "logo.svg")
            if os.path.exists(icon_path):
                self.icon_label.setPixmap(QPixmap(icon_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                log.debug(f"已加载标题栏图标: {icon_path}")
            else:
                log.warning(f"找不到标题栏图标: {icon_path}")
        except Exception as e:
            log.error(f"加载标题栏图标时出错: {str(e)}")
            
        self.icon_label.setFixedSize(24, 24)
        layout.addWidget(self.icon_label)
        
        # 标题文本
        self.title_label = QLabel("GestroKey")
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.title_label)
        
        # 最小化按钮
        self.min_button = self._create_title_button(
            "minimize", 
            "最小化", 
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        "assets", "icons", "minimize.svg")
        )
        self.min_button.clicked.connect(self.windowMinimize)
        layout.addWidget(self.min_button)
        
        # 最大化/还原按钮
        self.max_button = self._create_title_button(
            "maximize", 
            "最大化", 
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        "assets", "icons", "maximize.svg")
        )
        self.max_button.clicked.connect(self.windowMaximize)
        layout.addWidget(self.max_button)
        
        # 关闭按钮
        self.close_button = self._create_title_button(
            "closeButton", 
            "关闭", 
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        "assets", "icons", "close.svg")
        )
        self.close_button.clicked.connect(self.windowClose)
        layout.addWidget(self.close_button)
        
        # 设置布局
        self.setLayout(layout)
        
        log.debug("标题栏UI组件初始化完成")
        
    def _create_title_button(self, object_name, tooltip, icon_path):
        """创建标题栏按钮
        
        Args:
            object_name: 对象名称
            tooltip: 工具提示
            icon_path: 图标路径
            
        Returns:
            QToolButton: 创建的按钮
        """
        button = QToolButton(self)
        button.setObjectName(object_name)
        button.setToolTip(tooltip)
        
        # 设置固定大小
        button.setFixedSize(32, 32)
        button.setIconSize(QSize(16, 16))
        
        # 加载图标
        try:
            if os.path.exists(icon_path):
                button.setIcon(QIcon(icon_path))
                log.debug(f"已加载按钮图标: {icon_path}")
            else:
                log.warning(f"找不到按钮图标: {icon_path}")
        except Exception as e:
            log.error(f"加载按钮图标时出错: {str(e)}")
            
        return button
        
    def update_maximized_state(self, is_maximized):
        """更新最大化按钮状态
        
        Args:
            is_maximized: 是否最大化
        """
        try:
            # 根据窗口状态更改图标和提示
            if is_maximized:
                # 更改为"还原"图标
                restore_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                "assets", "icons", "restore.svg")
                if os.path.exists(restore_icon_path):
                    self.max_button.setIcon(QIcon(restore_icon_path))
                    self.max_button.setToolTip("还原")
                    log.debug("窗口已最大化，更新为还原图标")
                else:
                    log.warning(f"找不到还原图标: {restore_icon_path}")
            else:
                # 更改为"最大化"图标
                maximize_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                "assets", "icons", "maximize.svg")
                if os.path.exists(maximize_icon_path):
                    self.max_button.setIcon(QIcon(maximize_icon_path))
                    self.max_button.setToolTip("最大化")
                    log.debug("窗口已还原，更新为最大化图标")
                else:
                    log.warning(f"找不到最大化图标: {maximize_icon_path}")
                
            # 更新标题栏样式
            if is_maximized:
                self.setStyleSheet(self.styleSheet().replace("border-top-left-radius: 10px; border-top-right-radius: 10px;", "border-radius: 0px;"))
            else:
                if "border-radius: 0px;" in self.styleSheet():
                    self.setStyleSheet(self.styleSheet().replace("border-radius: 0px;", "border-top-left-radius: 10px; border-top-right-radius: 10px;"))
                    
        except Exception as e:
            log.error(f"更新最大化状态时出错: {str(e)}")
                
    def mousePressEvent(self, event):
        """处理鼠标按下事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_position = event.globalPos()
            # 设置鼠标样式为手状
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            log.debug("开始拖动窗口")
            
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件
        
        Args:
            event: 鼠标事件
        """
        # 如果正在拖动窗口
        if self.dragging and event.buttons() == Qt.LeftButton:
            # 计算移动的差值
            delta = event.globalPos() - self.drag_start_position
            
            # 获取主窗口
            main_window = self.window()
            
            # 检查窗口是否最大化，如果是则还原
            if main_window.isMaximized():
                # 在窗口变为正常大小时，更新窗口的位置
                # 计算相对点击位置的百分比
                title_bar_width = self.width()
                relative_x = event.pos().x() / title_bar_width
                
                # 还原窗口
                main_window.showNormal()
                
                # 更新拖动起始位置
                new_width = main_window.width()
                self.drag_start_position = QPoint(
                    event.globalPos().x() - int(new_width * relative_x),
                    event.globalPos().y() - 10  # 鼠标位于标题栏顶部附近
                )
                log.debug("从最大化状态恢复并开始拖动")
                return
                
            # 移动窗口
            main_window.move(main_window.pos() + delta)
            
            # 更新拖动起始位置
            self.drag_start_position = event.globalPos()
        
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            self.dragging = False
            # 恢复鼠标样式
            self.setCursor(QCursor(Qt.ArrowCursor))
            log.debug("停止拖动窗口")
            
        super().mouseReleaseEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            # 触发最大化/还原信号
            self.windowMaximize.emit()
            log.debug("标题栏双击 - 触发最大化/还原")
            
        super().mouseDoubleClickEvent(event)
        
    def enterEvent(self, event):
        """鼠标进入事件
        
        Args:
            event: 事件对象
        """
        if not self.dragging:
            self.setCursor(QCursor(Qt.OpenHandCursor))
            
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件
        
        Args:
            event: 事件对象
        """
        if not self.dragging:
            self.setCursor(QCursor(Qt.ArrowCursor))
            
        super().leaveEvent(event)
        
    def update_title(self, title):
        """更新标题文本
        
        Args:
            title: 新标题
        """
        # 直接返回，不再更新标题（因为标题标签已移除）
        log.debug(f"标题更新请求被忽略: {title}")
        return 