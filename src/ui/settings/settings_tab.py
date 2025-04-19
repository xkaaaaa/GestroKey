import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QApplication, QFileDialog, 
                            QGroupBox, QCheckBox, QSlider, QColorDialog, QPushButton,
                            QSizePolicy, QSpacerItem, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon

try:
    from core.logger import get_logger
    from ui.settings.settings import get_settings
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.scrollbar import AnimatedScrollArea  # 导入自定义滚动区域
    from ui.components.slider import AnimatedSlider  # 导入自定义滑块组件
    from ui.components.color_picker import AnimatedColorPicker  # 导入自定义色彩选择器
    from ui.components.number_spinner import AnimatedNumberSpinner  # 导入自定义数字选择器
    from ui.components.toast_notification import show_info, show_error, show_warning, show_success, ensure_toast_system_initialized  # 导入Toast通知组件
    from ui.components.dialog import connect_page_to_main_window  # 使用dialog.py中的辅助方法连接到主窗口
    from ui.components.navigation_menu import SideNavigationMenu  # 导入导航菜单组件
    from version import APP_NAME  # 导入应用名称
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger
    from ui.settings.settings import get_settings
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.scrollbar import AnimatedScrollArea  # 导入自定义滚动区域
    from ui.components.slider import AnimatedSlider  # 导入自定义滑块组件
    from ui.components.color_picker import AnimatedColorPicker  # 导入自定义色彩选择器
    from ui.components.number_spinner import AnimatedNumberSpinner  # 导入自定义数字选择器
    from ui.components.toast_notification import show_info, show_error, show_warning, show_success, ensure_toast_system_initialized  # 导入Toast通知组件
    from ui.components.dialog import connect_page_to_main_window  # 使用dialog.py中的辅助方法连接到主窗口
    from ui.components.navigation_menu import SideNavigationMenu  # 导入导航菜单组件
    from version import APP_NAME  # 导入应用名称

class SettingsPage(QWidget):
    """设置页面
    包含应用程序的各种设置选项，如主题、语言、快捷键等。
    """
    # 添加信号用于请求显示对话框
    request_dialog = pyqtSignal(str, str, str, object)  # message_type, title, message, callback
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("SettingsPage")
        self.settings = get_settings()
        
        # 预加载通知系统
        ensure_toast_system_initialized()
        self.logger.debug("通知组件已预加载")
        
        self.initUI()
        self.logger.debug("设置页面初始化完成")
    
    def showEvent(self, event):
        """窗口显示事件，确保连接到主窗口"""
        super().showEvent(event)
        connect_page_to_main_window(self)
    
    def initUI(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建标题标签
        title_layout = QHBoxLayout()
        title_label = QLabel("设置")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)
        main_layout.addLayout(title_layout)
        
        # 创建横向导航菜单
        self.nav_menu = SideNavigationMenu(orientation=SideNavigationMenu.ORIENTATION_HORIZONTAL)
        
        # 创建画笔设置页面
        brush_settings_page = self.create_brush_settings_page()
        
        # 创建应用设置页面
        app_settings_page = self.create_app_settings_page()
        
        # 添加页面到导航菜单
        self.nav_menu.addPage(brush_settings_page, "画笔设置", QIcon())
        self.nav_menu.addPage(app_settings_page, "应用设置", QIcon())
        
        # 添加导航菜单到主布局
        main_layout.addWidget(self.nav_menu)
        
        # 创建底部按钮区域
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(10, 10, 10, 10)
        
        # 使用自定义动画按钮替换标准按钮
        reset_button = AnimatedButton("重置为默认设置", primary_color=[108, 117, 125])  # 灰色
        reset_button.setMinimumSize(140, 36)  # 设置最小大小而不是固定大小
        reset_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        reset_button.clicked.connect(self.reset_settings)
        
        save_button = AnimatedButton("保存设置", primary_color=[41, 128, 185])  # 蓝色
        save_button.setMinimumSize(120, 36)  # 设置最小大小而不是固定大小
        save_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        save_button.clicked.connect(self.save_settings)
        
        buttons_layout.addWidget(reset_button)
        buttons_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        buttons_layout.addWidget(save_button)
        
        main_layout.addWidget(buttons_widget)
        
        # 设置布局和大小策略
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 记录自适应布局启用
        self.logger.debug("设置页面自适应布局已启用")

    def create_brush_settings_page(self):
        """创建画笔设置页面"""
        brush_page = QWidget()
        
        # 创建滚动区域
        scroll_area = AnimatedScrollArea()
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建内容部件
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 绘制设置组
        drawing_group = QGroupBox("绘制设置")
        drawing_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        drawing_layout = QVBoxLayout()
        
        # 笔尖粗细设置
        pen_layout = QHBoxLayout()
        pen_label = QLabel("笔尖粗细:")
        pen_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        
        # 使用自定义动画滑块替代普通SpinBox
        self.pen_width_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.pen_width_slider.setRange(1, 20)
        self.pen_width_slider.setValue(self.settings.get("pen_width"))
        self.pen_width_slider.valueChanged.connect(self.pen_width_changed)
        self.pen_width_slider.setMinimumWidth(200)
        self.pen_width_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # 使用自定义数字选择器替代普通SpinBox
        self.pen_width_spinner = AnimatedNumberSpinner(
            min_value=1, 
            max_value=20, 
            step=1, 
            value=self.settings.get("pen_width"),
            primary_color=[52, 152, 219]  # 蓝色主题
        )
        self.pen_width_spinner.valueChanged.connect(self.pen_width_spinner_sync)
        self.pen_width_spinner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        pen_layout.addWidget(pen_label)
        pen_layout.addWidget(self.pen_width_slider)
        pen_layout.addWidget(self.pen_width_spinner)
        drawing_layout.addLayout(pen_layout)
        
        # 笔尖颜色设置
        color_layout = QVBoxLayout()  # 改为垂直布局
        color_label = QLabel("笔尖颜色:")
        color_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        
        # 使用自定义色彩选择器组件替代简单的按钮
        self.color_picker = AnimatedColorPicker()
        self.color_picker.set_color(self.settings.get("pen_color"))
        self.color_picker.colorChanged.connect(self.color_changed)
        self.color_picker.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_picker)
        drawing_layout.addLayout(color_layout)
        
        # 绘制预览框
        preview_layout = QHBoxLayout()
        preview_label = QLabel("笔尖预览:")
        preview_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        
        self.preview_widget = PenPreviewWidget(
            self.settings.get("pen_width"), 
            self.settings.get("pen_color")
        )
        self.preview_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.preview_widget)
        preview_layout.addStretch()
        drawing_layout.addLayout(preview_layout)
        
        drawing_group.setLayout(drawing_layout)
        content_layout.addWidget(drawing_group)
        
        # 添加弹性空间
        content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # 设置内容部件
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        # 创建布局
        page_layout = QVBoxLayout(brush_page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll_area)
        
        return brush_page
    
    def create_app_settings_page(self):
        """创建应用设置页面"""
        app_page = QWidget()
        
        # 创建滚动区域
        scroll_area = AnimatedScrollArea()
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建内容部件
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 应用设置组
        app_group = QGroupBox("应用设置")
        app_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        app_layout = QVBoxLayout()
        
        # 添加临时标签
        temp_label = QLabel("应用设置页面 - 敬请期待")
        temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temp_label.setStyleSheet("font-size: 14pt; color: #888; margin: 20px;")
        app_layout.addWidget(temp_label)
        
        app_group.setLayout(app_layout)
        content_layout.addWidget(app_group)
        
        # 添加弹性空间
        content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # 设置内容部件
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        # 创建布局
        page_layout = QVBoxLayout(app_page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll_area)
        
        return app_page
    
    def resizeEvent(self, event):
        """窗口尺寸变化事件处理，用于调整UI布局"""
        # 调用父类方法
        super().resizeEvent(event)
        
        # 记录窗口大小变化
        self.logger.debug(f"设置页面大小已调整: {self.width()}x{self.height()}")
    
    def color_changed(self, color):
        """处理颜色变化事件"""
        self.logger.debug(f"设置笔尖颜色: RGB({color[0]}, {color[1]}, {color[2]})")
        self.settings.set("pen_color", color)
        self.preview_widget.update_color(color)
        
        # 不再立即更新绘制管理器，只在保存或重置时更新
    
    def pen_width_changed(self, value):
        """笔尖粗细变化时的回调"""
        self.logger.debug(f"设置笔尖粗细: {value}")
        self.settings.set("pen_width", value)
        # 更新微调框
        if self.pen_width_spinner.value() != value:
            self.pen_width_spinner.setValue(value)
        
        # 更新预览
        self.preview_widget.update_width(value)
    
    def pen_width_spinner_sync(self, value):
        """微调框值变化时同步滑块的值"""
        if self.pen_width_slider.value() != value:
            self.pen_width_slider.setValue(value)
            # 设置值（通过滑块的valueChanged信号间接调用pen_width_changed）
    
    def reset_settings(self):
        """重置为默认设置"""
        # 使用信号请求主窗口显示对话框
        self.request_dialog.emit(
            "question",
            f"确认重置",
            "是否确定将所有设置重置为默认值？",
            self._on_reset_dialog_result
        )
    
    def _on_reset_dialog_result(self, button_text):
        """对话框结果处理 - 重置确认"""
        if button_text == "是":
            try:
                self.logger.info("重置为默认设置")
                # 重置设置
                success = self.settings.reset_to_default()
                
                if success:
                    # 更新UI显示
                    self.update_ui_from_settings()
                    
                    # 应用设置到绘制管理器
                    self.logger.debug("尝试应用默认设置到绘制管理器")
                    self._update_drawing_manager()
                    
                    # 显示提示
                    show_success(self, "已恢复默认设置并应用")
                else:
                    # 失败提示
                    self.logger.error("重置设置失败")
                    show_error(self, "恢复默认设置失败")
            except Exception as e:
                self.logger.error(f"重置设置时出错: {e}")
                show_error(self, f"重置设置时出错: {str(e)}")
    
    def save_settings(self):
        """保存设置"""
        try:
            # 获取设置值
            pen_width = self.pen_width_spinner.value()
            
            # 直接从preview_widget获取颜色值
            pen_color = self.preview_widget.pen_color
            
            # 确保设置值更新
            self.settings.set("pen_width", pen_width)
            self.settings.set("pen_color", pen_color)
            
            # 检查是否真的有改变需要保存
            if not self.settings.has_changes():
                self.logger.info("设置未发生实际变化，无需保存")
                show_info(self, "设置未发生实际变化，无需保存")
                return True
                
            # 保存设置
            success = self.settings.save()
            
            if success:
                self.logger.info("设置已保存")
                # 应用设置到绘制管理器
                self._update_drawing_manager()
                # 显示成功消息
                show_success(self, "设置已保存并应用")
                return True
            else:
                self.logger.error("保存设置失败")
                show_warning(self, "无法保存设置")
                return False
        except Exception as e:
            self.logger.error(f"保存设置时出错: {e}")
            show_error(self, f"保存设置时出错: {str(e)}")
            return False
    
    def _update_drawing_manager(self):
        """更新绘制管理器的参数（内部方法）"""
        try:
            # 尝试获取主窗口
            main_window = self.window()
            success = False
            
            # 方法1：直接通过主窗口访问console_tab
            if hasattr(main_window, 'console_tab') and main_window.console_tab:
                console_tab = main_window.console_tab
                if hasattr(console_tab, 'drawing_manager') and console_tab.drawing_manager:
                    drawing_manager = console_tab.drawing_manager
                    if drawing_manager.update_settings():
                        self.logger.debug("方法1: 已通过主窗口直接访问更新绘制管理器参数")
                        success = True
            
            # 方法2：尝试通过控制台选项卡访问
            if not success:
                from ui.console import ConsolePage
                console_tabs = main_window.findChildren(ConsolePage)
                if console_tabs:
                    console_tab = console_tabs[0]
                    if hasattr(console_tab, 'drawing_manager') and console_tab.drawing_manager:
                        drawing_manager = console_tab.drawing_manager
                        if drawing_manager.update_settings():
                            self.logger.debug("方法2: 已通过findChildren更新绘制管理器参数")
                            success = True
            
            # 方法3：通过中央组件的方式寻找控制台选项卡
            if not success and hasattr(main_window, 'centralWidget'):
                central = main_window.centralWidget()
                if central:
                    # 查找控制台选项卡
                    from ui.console import ConsolePage
                    console_tabs = central.findChildren(ConsolePage)
                    if console_tabs:
                        console_tab = console_tabs[0]
                        if hasattr(console_tab, 'drawing_manager') and console_tab.drawing_manager:
                            drawing_manager = console_tab.drawing_manager
                            if drawing_manager.update_settings():
                                self.logger.debug("方法3: 已通过中央组件更新绘制管理器参数")
                                success = True
            
            # 尝试创建新的绘制管理器并更新设置
            if not success:
                self.logger.debug("尝试创建新的绘制管理器并更新设置")
                from core.drawer import DrawingManager
                temp_manager = DrawingManager()
                temp_manager.update_settings()
                self.logger.debug("已通过临时绘制管理器更新设置，下次启动绘制时将应用")
                success = True
                
            if not success:
                self.logger.warning("未能找到任何可用的绘制管理器")
                
        except Exception as e:
            self.logger.error(f"尝试更新绘制管理器参数时发生错误: {e}")
            self.logger.error(f"错误详情: {str(e)}")
    
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        try:
            return self.settings.has_changes()
        except Exception as e:
            self.logger.error(f"检查设置更改状态时出错: {e}")
            return False
    
    def update_ui_from_settings(self):
        """从设置更新UI控件"""
        try:
            # 获取设置值
            pen_width = self.settings.get("pen_width")
            pen_color = self.settings.get("pen_color")
            
            # 更新笔尖粗细控件
            self.pen_width_slider.setValue(pen_width)
            self.pen_width_spinner.setValue(pen_width)
            
            # 更新笔尖颜色
            self.color_picker.set_color(pen_color)
            
            # 更新预览
            self.preview_widget.update_width(pen_width)
            self.preview_widget.update_color(pen_color)
            
            self.logger.debug(f"UI已从设置更新: 笔尖粗细={pen_width}, 笔尖颜色={pen_color}")
            return True
        except Exception as e:
            self.logger.error(f"从设置更新UI时出错: {e}")
            return False


class PenPreviewWidget(QWidget):
    """笔尖预览小部件"""
    
    def __init__(self, width=3, color=[0, 120, 255], parent=None):
        super().__init__(parent)
        self.pen_width = width
        self.pen_color = color
        self.setFixedSize(100, 50)
    
    def update_width(self, width):
        """更新笔尖粗细"""
        self.pen_width = width
        self.update()  # 触发重绘
    
    def update_color(self, color):
        """更新笔尖颜色"""
        self.pen_color = color
        self.update()  # 触发重绘
    
    def paintEvent(self, event):
        """绘制预览"""
        import math
        from PyQt6.QtGui import QPainter, QPen, QColor
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置画笔
        r, g, b = self.pen_color[0], self.pen_color[1], self.pen_color[2]
        pen = QPen(QColor(r, g, b))
        pen.setWidth(self.pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # 绘制水平线
        w = self.width()
        h = self.height()
        mid_y = int(h / 2)  # 将浮点数转换为整数
        
        # 绘制水平线
        painter.drawLine(10, mid_y, w - 10, mid_y)
        
        # 绘制两端的圆点
        painter.drawPoint(10, mid_y)
        painter.drawPoint(w - 10, mid_y)


if __name__ == "__main__":
    # 独立运行测试
    app = QApplication(sys.argv)
    widget = SettingsPage()
    widget.show()
    sys.exit(app.exec()) 