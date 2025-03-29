import logging
from PyQt5.QtWidgets import QStyleFactory, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

# 导入日志模块
try:
    from app.log import log
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log

class StyleManager:
    """样式管理器，用于集中管理应用程序的样式设置"""
    
    @staticmethod
    def apply_styles(app):
        """应用全局样式到应用程序
        
        Args:
            app: QApplication实例
        """
        try:
            # 设置应用程序样式
            app.setStyle("Fusion")
            
            # 设置调色板
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(255, 255, 255))
            palette.setColor(QPalette.WindowText, QColor(45, 55, 72))
            palette.setColor(QPalette.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
            palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ToolTipText, QColor(45, 55, 72))
            palette.setColor(QPalette.Text, QColor(45, 55, 72))
            palette.setColor(QPalette.Button, QColor(248, 249, 250))
            palette.setColor(QPalette.ButtonText, QColor(45, 55, 72))
            palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
            palette.setColor(QPalette.Link, QColor(66, 153, 225))
            palette.setColor(QPalette.Highlight, QColor(66, 153, 225))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
            
            # 设置禁用状态的颜色
            palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(160, 174, 192))
            palette.setColor(QPalette.Disabled, QPalette.Text, QColor(160, 174, 192))
            palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(160, 174, 192))
            
            # 应用调色板
            app.setPalette(palette)
            
            # 设置样式表
            app.setStyleSheet("""
                /* QWidget样式 */
                QWidget {
                    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                    font-size: 14px;
                    color: #2D3748;
                }
                
                /* QScrollBar样式 */
                QScrollBar:vertical {
                    border: none;
                    background: #F7FAFC;
                    width: 12px;
                    margin: 0px;
                }
                
                QScrollBar::handle:vertical {
                    background: #CBD5E0;
                    min-height: 20px;
                    border-radius: 6px;
                }
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                
                QScrollBar:horizontal {
                    border: none;
                    background: #F7FAFC;
                    height: 12px;
                    margin: 0px;
                }
                
                QScrollBar::handle:horizontal {
                    background: #CBD5E0;
                    min-width: 20px;
                    border-radius: 6px;
                }
                
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
                
                /* QToolButton样式 */
                QToolButton {
                    background-color: transparent;
                    border: none;
                    padding: 4px;
                    border-radius: 4px;
                }
                
                QToolButton:hover {
                    background-color: rgba(0, 0, 0, 0.05);
                }
                
                QToolButton:pressed {
                    background-color: rgba(0, 0, 0, 0.1);
                }
                
                /* QCheckBox样式 */
                QCheckBox {
                    spacing: 8px;
                }
                
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 1px solid #CBD5E0;
                    border-radius: 3px;
                }
                
                QCheckBox::indicator:unchecked {
                    background-color: #FFFFFF;
                }
                
                QCheckBox::indicator:checked {
                    background-color: #4299E1;
                    border-color: #4299E1;
                    /* 使用CSS实现勾选图标 */
                    image: url(icons:internal/checkbox_checked.svg);
                }
                
                /* QRadioButton样式 */
                QRadioButton {
                    spacing: 8px;
                }
                
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                    border: 1px solid #CBD5E0;
                    border-radius: 9px;
                }
                
                QRadioButton::indicator:unchecked {
                    background-color: #FFFFFF;
                }
                
                QRadioButton::indicator:checked {
                    background-color: #FFFFFF;
                    border: 1px solid #4299E1;
                    /* 使用CSS实现选中圆点 */
                    image: url(icons:internal/radio_checked.svg);
                }
                
                /* QPushButton样式 */
                QPushButton {
                    background-color: #4299E1;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                
                QPushButton:hover {
                    background-color: #3182CE;
                }
                
                QPushButton:pressed {
                    background-color: #2B6CB0;
                }
                
                QPushButton:disabled {
                    background-color: #A0AEC0;
                }
                
                QPushButton#secondaryButton {
                    background-color: #EDF2F7;
                    color: #4A5568;
                    border: 1px solid #CBD5E0;
                }
                
                QPushButton#secondaryButton:hover {
                    background-color: #E2E8F0;
                }
                
                QPushButton#secondaryButton:pressed {
                    background-color: #CBD5E0;
                }
                
                /* QLineEdit样式 */
                QLineEdit {
                    border: 1px solid #CBD5E0;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: #FFFFFF;
                    selection-background-color: #4299E1;
                }
                
                QLineEdit:focus {
                    border: 1px solid #4299E1;
                }
                
                /* QComboBox样式 */
                QComboBox {
                    border: 1px solid #CBD5E0;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: #FFFFFF;
                    min-width: 6em;
                }
                
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: center right;
                    width: 24px;
                    border-left: none;
                }
                
                QComboBox::down-arrow {
                    /* 使用CSS实现下拉箭头 */
                    image: url(icons:internal/arrow_down.svg);
                    width: 12px;
                    height: 12px;
                }
                
                QComboBox QAbstractItemView {
                    border: 1px solid #CBD5E0;
                    border-radius: 4px;
                    selection-background-color: #EBF8FF;
                    selection-color: #2D3748;
                }
                
                /* QSlider样式 */
                QSlider::groove:horizontal {
                    border: none;
                    height: 6px;
                    background-color: #EDF2F7;
                    border-radius: 3px;
                }
                
                QSlider::handle:horizontal {
                    background-color: #4299E1;
                    border: none;
                    width: 18px;
                    height: 18px;
                    margin: -6px 0;
                    border-radius: 9px;
                }
                
                QSlider::sub-page:horizontal {
                    background-color: #4299E1;
                    border-radius: 3px;
                }
                
                /* QTabWidget样式 */
                QTabWidget::pane {
                    border: 1px solid #E2E8F0;
                    border-radius: 4px;
                    background-color: #FFFFFF;
                }
                
                QTabBar::tab {
                    background-color: #F7FAFC;
                    color: #4A5568;
                    border: 1px solid #E2E8F0;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 12px;
                    min-width: 8ex;
                    margin-right: 2px;
                }
                
                QTabBar::tab:selected {
                    background-color: #FFFFFF;
                    color: #2D3748;
                    border-bottom: none;
                }
                
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
                
                /* QTableView样式 */
                QTableView {
                    border: 1px solid #E2E8F0;
                    border-radius: 4px;
                    background-color: #FFFFFF;
                    gridline-color: #EDF2F7;
                    selection-background-color: #EBF8FF;
                    selection-color: #2D3748;
                }
                
                QTableView::item {
                    padding: 4px;
                }
                
                QHeaderView::section {
                    background-color: #F7FAFC;
                    border: 1px solid #E2E8F0;
                    padding: 4px;
                    font-weight: bold;
                }
                
                /* QMainWindow样式 */
                QMainWindow {
                    background-color: #FFFFFF;
                }
                
                /* 主容器样式 */
                #mainContainer {
                    background-color: #FFFFFF;
                    border-radius: 10px;
                }
                
                /* 内容容器样式 */
                #contentContainer {
                    background-color: #FFFFFF;
                }
                
                /* 控制台页面样式 */
                #consolePage {
                    background-color: #FFFFFF;
                    border-left: 1px solid #E2E8F0;
                }
                
                /* 设置页面样式 */
                #settingsPage {
                    background-color: #FFFFFF;
                    border-left: 1px solid #E2E8F0;
                }
                
                /* 手势页面样式 */
                #gesturesPage {
                    background-color: #FFFFFF;
                    border-left: 1px solid #E2E8F0;
                }
            """)
            
            log.info("全局样式已应用到应用程序")
        except Exception as e:
            log.error(f"应用样式时出错: {str(e)}")
            
    @staticmethod
    def get_shadow_effect(color=QColor(0, 0, 0, 60), blur_radius=20, x_offset=0, y_offset=2):
        """获取阴影效果
        
        Args:
            color: 阴影颜色
            blur_radius: 模糊半径
            x_offset: 水平偏移
            y_offset: 垂直偏移
            
        Returns:
            QGraphicsDropShadowEffect: 阴影效果对象
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(color)
        shadow.setOffset(x_offset, y_offset)
        
        log.debug(f"创建阴影效果: blur={blur_radius}, offset=({x_offset}, {y_offset})")
        return shadow
        
    @staticmethod
    def update_button_style_for_unsaved_changes(button, has_changes):
        """更新按钮样式以反映未保存的更改
        
        Args:
            button: QPushButton对象
            has_changes: 是否有未保存的更改
        """
        try:
            if has_changes:
                # 强调保存按钮
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #4299E1;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        text-decoration: underline;
                        border: 2px solid #3182CE;
                    }
                    
                    QPushButton:hover {
                        background-color: #3182CE;
                    }
                    
                    QPushButton:pressed {
                        background-color: #2B6CB0;
                    }
                """)
                
                # 启用保存按钮
                button.setEnabled(True)
                log.debug("已更新保存按钮样式: 有未保存的更改")
            else:
                # 恢复默认样式
                button.setStyleSheet("")
                
                # 禁用保存按钮
                button.setEnabled(False)
                log.debug("已更新保存按钮样式: 无未保存的更改")
        except Exception as e:
            log.error(f"更新按钮样式时出错: {str(e)}") 