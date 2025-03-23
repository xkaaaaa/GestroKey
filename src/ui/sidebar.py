from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                              QSpacerItem, QSizePolicy, QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QFont

import os
import sys

try:
    from app.log import log
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.log import log

class SidebarButton(QPushButton):
    """侧边栏按钮"""
    
    def __init__(self, text, icon_path, page_name, parent=None):
        """初始化侧边栏按钮
        
        Args:
            text: 按钮文本
            icon_path: 图标路径
            page_name: 页面名称，用于导航
            parent: 父部件
        """
        super().__init__(parent)
        
        # 保存页面名称
        self.page_name = page_name
        
        # 保存图标路径和文本
        self.icon_path = icon_path
        self.button_text = text
        
        # 设置图标
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        
        # 设置文本
        self.setText(text)
        
        # 设置样式
        self.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
                color: #4A5568;
                background-color: transparent;
                border-radius: 8px;
            }
            
            QPushButton:hover {
                background-color: #EDF2F7;
                color: #2D3748;
            }
            
            QPushButton:pressed {
                background-color: #E2E8F0;
            }
            
            QPushButton:checked {
                background-color: #4299E1;
                color: white;
            }
        """)
        
        # 设置按钮属性
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.PointingHandCursor)
        
        # 设置固定高度
        self.setFixedHeight(48)
        
        # 设置图标和文本对齐
        self.setLayoutDirection(Qt.LeftToRight)
        
    def setActive(self, active):
        """设置按钮活动状态"""
        self.setChecked(active)
        
    def setCollapsed(self, collapsed):
        """设置折叠状态"""
        if collapsed:
            # 折叠状态：只显示图标，不显示文本
            self.setText("")
            self.setToolTip(self.button_text)  # 添加工具提示
            self.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 12px;
                    text-align: center;
                    background-color: transparent;
                    border-radius: 8px;
                }
                
                QPushButton:hover {
                    background-color: #EDF2F7;
                }
                
                QPushButton:pressed {
                    background-color: #E2E8F0;
                }
                
                QPushButton:checked {
                    background-color: #4299E1;
                }
            """)
        else:
            # 展开状态：显示图标和文本
            self.setText(self.button_text)
            self.setToolTip("")  # 清除工具提示
            self.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 500;
                    color: #4A5568;
                    background-color: transparent;
                    border-radius: 8px;
                }
                
                QPushButton:hover {
                    background-color: #EDF2F7;
                    color: #2D3748;
                }
                
                QPushButton:pressed {
                    background-color: #E2E8F0;
                }
                
                QPushButton:checked {
                    background-color: #4299E1;
                    color: white;
                }
            """)

class Sidebar(QWidget):
    """侧边栏组件"""
    
    # 定义信号
    pageChanged = pyqtSignal(str)  # 页面切换信号
    collapsedChanged = pyqtSignal(bool)  # 折叠状态变更信号
    
    def __init__(self, parent=None):
        """初始化侧边栏
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # 设置初始大小
        self.expanded_width = 200
        self.collapsed_width = 60
        self.setFixedWidth(self.expanded_width)
        
        # 折叠状态
        self.is_collapsed = False
        
        # 初始化布局
        self.init_ui()
        
        log.info("侧边栏初始化完成")
        
    def init_ui(self):
        """初始化UI组件"""
        # 主布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 20, 10, 20)
        self.layout.setSpacing(10)
        
        # 标题栏
        self.header = QWidget()
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(5, 0, 5, 0)
        
        # 应用图标和名称容器
        self.brand_container = QWidget()
        self.brand_layout = QHBoxLayout(self.brand_container)
        self.brand_layout.setContentsMargins(0, 0, 0, 0)
        self.brand_layout.setSpacing(8)
        
        # 应用图标
        self.app_icon = QLabel()
        self.app_icon.setFixedSize(24, 24)
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/logo.svg")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.app_icon.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # 如果找不到图标文件，使用文本代替
            self.app_icon.setText("G")
            self.app_icon.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A90E2; background-color: #EDF2F7; border-radius: 4px; padding: 2px;")
            log.warning(f"找不到应用图标: {logo_path}")
        
        # 应用名称
        self.app_name = QLabel("GestroKey")
        self.app_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A90E2;")
        
        # 添加到品牌容器
        self.brand_layout.addWidget(self.app_icon)
        self.brand_layout.addWidget(self.app_name)
        
        # 折叠按钮
        self.toggle_button = QPushButton()
        self.toggle_button.setFixedSize(24, 24)
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #4A90E2;
                font-size: 18px;
            }
            QPushButton:hover {
                color: #2D8CDB;
            }
        """)
        self.toggle_button.setText("◀")  # 使用字符作为图标
        self.toggle_button.clicked.connect(self.toggle_collapsed)
        
        # 添加到标题栏布局
        self.header_layout.addWidget(self.brand_container)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.toggle_button)
        
        # 添加标题栏到主布局
        self.layout.addWidget(self.header)
        
        # 添加分割线
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Sunken)
        self.divider.setStyleSheet("background-color: #E2E8F0;")
        self.layout.addWidget(self.divider)
        
        # 主导航按钮容器
        self.nav_container = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 10, 0, 10)
        self.nav_layout.setSpacing(5)
        
        # 添加导航按钮
        self.buttons = {}
        
        # 添加控制台按钮
        console_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/console.svg")
        self.add_nav_button("console", "控制台", console_icon)
        
        # 添加手势管理按钮
        gestures_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/gestures.svg")
        self.add_nav_button("gestures", "手势管理", gestures_icon)
        
        # 添加导航容器到主布局
        self.layout.addWidget(self.nav_container)
        
        # 添加弹性空间，将设置按钮推到底部
        self.layout.addStretch()
        
        # 底部导航容器 (用于设置按钮)
        self.bottom_nav_container = QWidget()
        self.bottom_nav_layout = QVBoxLayout(self.bottom_nav_container)
        self.bottom_nav_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_nav_layout.setSpacing(5)
        
        # 添加分割线
        bottom_divider = QFrame()
        bottom_divider.setFrameShape(QFrame.HLine)
        bottom_divider.setFrameShadow(QFrame.Sunken)
        bottom_divider.setStyleSheet("background-color: #E2E8F0;")
        self.bottom_nav_layout.addWidget(bottom_divider)
        
        # 添加设置按钮
        settings_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/settings.svg")
        settings_button = SidebarButton("设置", settings_icon, "settings", self)
        settings_button.clicked.connect(lambda: self.change_page("settings"))
        self.bottom_nav_layout.addWidget(settings_button)
        self.buttons["settings"] = settings_button
        
        # 添加底部导航容器到主布局
        self.layout.addWidget(self.bottom_nav_container)
        
        # 设置背景样式
        self.setStyleSheet("""
            Sidebar {
                background-color: white;
                border-right: 1px solid #E2E8F0;
            }
        """)
        
        # 默认激活第一个按钮
        if self.buttons:
            first_button = self.buttons.get("console")
            if first_button:
                first_button.setActive(True)
        
    def add_nav_button(self, page_name, text, icon_path):
        """添加导航按钮
        
        Args:
            page_name: 页面名称
            text: 按钮文本
            icon_path: 图标路径
        """
        button = SidebarButton(text, icon_path, page_name, self)
        button.clicked.connect(lambda: self.change_page(page_name))
        self.nav_layout.addWidget(button)
        self.buttons[page_name] = button
        
    def change_page(self, page_name):
        """切换页面
        
        Args:
            page_name: 要切换到的页面名称
        """
        log.debug(f"收到页面切换请求: 从 {list(filter(lambda x: self.buttons[x].isChecked(), self.buttons.keys()))[0] if any(button.isChecked() for button in self.buttons.values()) else 'None'} 到 {page_name}")
        
        # 确保所有按钮都取消选中状态，然后只将当前页面的按钮设为选中
        for name, button in self.buttons.items():
            # 先取消所有按钮的自动互斥
            button.setAutoExclusive(False)
            # 然后设置正确的状态
            button.setActive(name == page_name)
            # 恢复自动互斥
            button.setAutoExclusive(True)
            
        # 发送页面切换信号
        self.pageChanged.emit(page_name)
        log.info(f"页面切换: {page_name}")
        
    def toggle_collapsed(self):
        """切换折叠状态"""
        self.setCollapsed(not self.is_collapsed)
        
    def setCollapsed(self, collapsed):
        """设置折叠状态
        
        Args:
            collapsed: 是否折叠
        """
        if self.is_collapsed == collapsed:
            return  # 状态未变，不需要处理
            
        self.is_collapsed = collapsed
        
        # 更新折叠按钮文本
        self.toggle_button.setText("▶" if collapsed else "◀")
        
        # 更新应用名称和图标显示
        if collapsed:
            # 折叠状态：只显示图标，隐藏应用名称
            self.app_name.setVisible(False)
            self.app_icon.setVisible(True)
            self.brand_container.setToolTip("GestroKey")  # 添加工具提示
        else:
            # 展开状态：显示图标和应用名称
            self.app_name.setVisible(True)
            self.app_icon.setVisible(True)
            self.brand_container.setToolTip("")  # 移除工具提示
        
        # 更新导航按钮显示
        for button in self.buttons.values():
            button.setCollapsed(collapsed)
            
        # 动画切换宽度
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        if collapsed:
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
        else:
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
            
        self.animation.start()
        
        # 发送折叠状态变更信号
        self.collapsedChanged.emit(collapsed)
        log.info(f"侧边栏折叠状态变更: {'已折叠' if collapsed else '已展开'}")
        
    def isCollapsed(self):
        """获取折叠状态
        
        Returns:
            是否折叠
        """
        return self.is_collapsed
        
    def navigate_to(self, page_name):
        """导航到指定页面
        
        Args:
            page_name: 页面名称
        """
        if page_name in self.buttons:
            # 设置按钮为选中状态
            self.buttons[page_name].setChecked(True)
            
            # 发出页面切换信号
            self.pageChanged.emit(page_name)
            
            log.info(f"导航到页面: {page_name}")
        else:
            log.warning(f"导航到未知页面: {page_name}")
            
    def set_active_page(self, page_name):
        """仅设置活动页面，不触发页面切换
        
        用于在用户取消页面切换时恢复正确的选中状态
        
        Args:
            page_name: 页面名称
        """
        if page_name in self.buttons:
            # 静默更新按钮状态，不触发信号
            for btn_name, btn in self.buttons.items():
                # 直接设置按钮状态而不触发信号
                btn.blockSignals(True)  # 阻止信号发送
                btn.setChecked(btn_name == page_name)
                btn.blockSignals(False)  # 恢复信号
            
            log.debug(f"静默更新侧边栏选中状态: {page_name}")
        else:
            log.warning(f"尝试设置未知页面为活动页: {page_name}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    sidebar = Sidebar()
    sidebar.show()
    
    # 测试导航
    sidebar.navigate_to("console")
    
    # 连接信号
    sidebar.pageChanged.connect(lambda page: print(f"切换到页面: {page}"))
    
    sys.exit(app.exec_()) 