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
        
        # 设置文本
        self.setText(text)
        
        # 加载图标
        if self.icon_path and os.path.exists(self.icon_path):
            log.debug(f"加载按钮图标: {self.icon_path}")
            self.setIcon(QIcon(self.icon_path))
            self.setIconSize(QSize(20, 20))
        else:
            log.warning(f"按钮图标路径不存在: {self.icon_path}")
        
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
        
        # 设置文本对齐
        self.setLayoutDirection(Qt.LeftToRight)
        
        log.debug(f"侧边栏按钮已创建: {text} ({page_name})")
        
    def setChecked(self, checked):
        """重写setChecked方法，确保视觉状态正确更新
        
        Args:
            checked: 是否选中
        """
        # 调用父类方法设置选中状态
        super().setChecked(checked)
        
        # 强制更新样式，确保视觉效果正确
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        
    def setActive(self, active):
        """设置按钮活动状态"""
        self.setChecked(active)
        
        # 确保更新视觉状态
        self.update()
        
    def setCollapsed(self, collapsed):
        """设置折叠状态"""
        if collapsed:
            # 折叠状态：不显示文本，只显示图标
            self.setText("")
            self.setToolTip(self.button_text)  # 添加工具提示
            
            # 确保图标显示正确尺寸
            if self.icon_path and os.path.exists(self.icon_path):
                self.setIconSize(QSize(24, 24))
            
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
            # 展开状态：显示文本并恢复图标
            self.setText(self.button_text)
            
            # 恢复图标尺寸
            if self.icon_path and os.path.exists(self.icon_path):
                self.setIconSize(QSize(20, 20))
                self.setIcon(QIcon(self.icon_path))
            
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
            
        log.debug(f"按钮 '{self.button_text}' 折叠状态已更新: {collapsed}")

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
        
        # 应用名称
        self.app_name = QLabel("GestroKey")
        self.app_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A90E2;")
        
        # 折叠状态下显示的"G"标签
        self.collapsed_label = QLabel("G")
        self.collapsed_label.setAlignment(Qt.AlignCenter)
        self.collapsed_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #4A90E2;
            background-color: transparent;
        """)
        self.collapsed_label.setVisible(False)
        
        # 添加到品牌容器
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
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #E2E8F0;")
        self.layout.addWidget(separator)
        
        # 添加导航按钮
        self.nav_buttons = {}
        
        # 按钮容器，用于组织布局
        self.button_container = QWidget()
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(6)
        
        # 添加导航按钮
        self.add_nav_button("console", "控制台", "ui/assets/icons/console.svg")
        self.add_nav_button("gestures", "手势管理", "ui/assets/icons/gestures.svg")
        self.add_nav_button("settings", "设置", "ui/assets/icons/settings.svg")
        
        # 添加按钮容器到主布局
        self.layout.addWidget(self.button_container)
        
        # 在按钮容器下方添加伸缩项，使按钮靠上对齐
        self.layout.addStretch()
        
        # 设置背景样式
        self.setStyleSheet("""
            Sidebar {
                background-color: white;
                border-right: 1px solid #E2E8F0;
            }
        """)
        
        # 默认激活控制台按钮
        first_button = self.nav_buttons.get("console")
        if first_button:
            first_button.setActive(True)
            log.debug("默认激活控制台按钮")
        
        log.debug("侧边栏UI组件初始化完成")
        
    def add_nav_button(self, page_name, text, icon_path):
        """添加导航按钮
        
        Args:
            page_name: 页面名称
            text: 按钮文本
            icon_path: 图标路径
        """
        # 确保图标路径是绝对路径
        if not os.path.isabs(icon_path):
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), icon_path)
        
        button = SidebarButton(text, icon_path, page_name, self)
        button.clicked.connect(lambda: self.change_page(page_name))
        self.button_layout.addWidget(button)
        self.nav_buttons[page_name] = button
        
        log.debug(f"添加导航按钮: {text} ({page_name}), 图标: {icon_path}")
        
    def change_page(self, page_name):
        """切换页面
        
        Args:
            page_name: 要切换到的页面名称
        """
        log.debug(f"收到页面切换请求: 从 {list(filter(lambda x: self.nav_buttons[x].isChecked(), self.nav_buttons.keys()))[0] if any(button.isChecked() for button in self.nav_buttons.values()) else 'None'} 到 {page_name}")
        
        # 禁用所有按钮的autoExclusive属性，确保能完全控制选中状态
        for button in self.nav_buttons.values():
            button.setAutoExclusive(False)
        
        # 确保所有按钮都处于未选中状态
        for button in self.nav_buttons.values():
            button.setChecked(False)
            
        # 然后只将要切换到的页面的按钮设为选中
        if page_name in self.nav_buttons:
            self.nav_buttons[page_name].setChecked(True)
        
        # 重新启用autoExclusive属性，确保今后的按钮点击能正确互斥
        for button in self.nav_buttons.values():
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
        if collapsed == self.is_collapsed:
            return
            
        self.is_collapsed = collapsed
        
        # 保存当前宽度
        current_width = self.width()
        target_width = self.collapsed_width if collapsed else self.expanded_width
        
        # 更新折叠按钮文本和工具提示
        if collapsed:
            self.toggle_button.setText("▶")
            self.toggle_button.setToolTip("展开侧边栏")
            
            # 隐藏应用名称，显示折叠标签
            self.app_name.setVisible(False)
            if hasattr(self, 'collapsed_label'):
                self.collapsed_label.setVisible(True)
                self.brand_layout.addWidget(self.collapsed_label)
        else:
            self.toggle_button.setText("◀")
            self.toggle_button.setToolTip("折叠侧边栏")
            
            # 显示应用名称，隐藏折叠标签
            self.app_name.setVisible(True)
            if hasattr(self, 'collapsed_label'):
                self.collapsed_label.setVisible(False)
                self.brand_layout.removeWidget(self.collapsed_label)
        
        # 更新按钮样式
        for button in self.nav_buttons.values():
            button.setCollapsed(collapsed)
            
        # 创建动画
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(current_width)
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 连接动画结束信号
        self.animation.finished.connect(lambda: self.collapsedChanged.emit(collapsed))
        
        # 开始动画
        self.animation.start()
        
        log.info(f"侧边栏折叠状态已变更: {'已折叠' if collapsed else '已展开'}")
        
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
        if page_name in self.nav_buttons:
            # 设置按钮为选中状态
            self.nav_buttons[page_name].setChecked(True)
            
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
        if page_name in self.nav_buttons:
            # 禁用所有按钮的autoExclusive属性，确保能完全控制选中状态
            for btn in self.nav_buttons.values():
                btn.blockSignals(True)  # 阻止信号发送
                btn.setAutoExclusive(False)
            
            # 先取消所有按钮的选中状态
            for btn in self.nav_buttons.values():
                btn.setChecked(False)
                
            # 只选中指定页面的按钮
            self.nav_buttons[page_name].setChecked(True)
            
            # 恢复所有按钮的autoExclusive属性和信号
            for btn in self.nav_buttons.values():
                btn.setAutoExclusive(True)
                btn.blockSignals(False)
            
            log.debug(f"侧边栏选择状态已重置并设置为: {page_name}")
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