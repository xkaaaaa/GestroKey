import logging
from PyQt5.QtWidgets import QApplication, QMessageBox, QDesktopWidget
from PyQt5.QtCore import QRect, QSize, QPoint, QSettings

# 导入日志模块
try:
    from app.log import log
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log

class WindowManager:
    """窗口管理器，用于处理窗口状态、位置和大小的保存和恢复"""
    
    @staticmethod
    def center_window(window):
        """将窗口居中显示
        
        Args:
            window: 要居中的窗口
        """
        frame_geo = window.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_geo.moveCenter(center_point)
        window.move(frame_geo.topLeft())
        log.debug("窗口已居中显示")
    
    @staticmethod
    def ensure_on_screen(window):
        """确保窗口在屏幕范围内
        
        Args:
            window: 要检查的窗口
        """
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry(window)
        window_rect = window.frameGeometry()
        
        # 如果窗口完全在屏幕外，将其移至屏幕中央
        if not screen_rect.intersects(window_rect):
            WindowManager.center_window(window)
        else:
            # 如果窗口部分超出屏幕，调整位置
            if window_rect.left() < screen_rect.left():
                window.move(screen_rect.left(), window.y())
            if window_rect.top() < screen_rect.top():
                window.move(window.x(), screen_rect.top())
            if window_rect.right() > screen_rect.right():
                window.move(screen_rect.right() - window_rect.width(), window.y())
            if window_rect.bottom() > screen_rect.bottom():
                window.move(window.x(), screen_rect.bottom() - window_rect.height())
                
        log.debug("已确保窗口在屏幕范围内")
    
    @staticmethod
    def save_window_state(window, settings_manager=None):
        """保存窗口状态到设置
        
        Args:
            window: 窗口实例
            settings_manager: 设置管理器，如果为None则使用QSettings
        """
        try:
            # 如果提供了settings_manager，使用它
            if settings_manager and hasattr(settings_manager, 'save_window_state'):
                # 获取窗口位置、大小和状态
                window_state = {
                    'pos_x': window.x(),
                    'pos_y': window.y(),
                    'width': window.width(),
                    'height': window.height(),
                    'maximized': window.isMaximized(),
                }
                
                # 保存到设置管理器
                settings_manager.save_window_state(window_state)
                
                log.debug(f"通过设置管理器保存窗口状态: {window_state}")
            else:
                # 使用QSettings直接保存
                settings = QSettings("GestroKey", "WindowState")
                
                # 保存窗口几何信息
                settings.setValue("geometry", window.saveGeometry())
                
                # 保存窗口状态
                settings.setValue("maximized", window.isMaximized())
                
                # 如果窗口处于正常状态，保存位置和大小
                if not window.isMaximized():
                    settings.setValue("pos", window.pos())
                    settings.setValue("size", window.size())
                    
                # 如果有保存的正常几何信息，也保存它
                if hasattr(window, 'normal_geometry') and window.normal_geometry:
                    settings.setValue("normal_geometry", window.normal_geometry)
                    
                log.debug("窗口状态已保存到QSettings")
        except Exception as e:
            log.error(f"保存窗口状态时出错: {str(e)}")
            
    @staticmethod
    def restore_window_state(window, settings_manager=None):
        """从设置恢复窗口状态
        
        Args:
            window: 窗口实例
            settings_manager: 设置管理器，如果为None则使用QSettings
        """
        try:
            # 如果提供了settings_manager，使用它
            if settings_manager and hasattr(settings_manager, 'get_window_state'):
                # 从设置管理器获取窗口状态
                window_state = settings_manager.get_window_state()
                
                if window_state:
                    # 恢复窗口位置和大小
                    if 'pos_x' in window_state and 'pos_y' in window_state:
                        window.move(int(window_state['pos_x']), int(window_state['pos_y']))
                        
                    if 'width' in window_state and 'height' in window_state:
                        window.resize(int(window_state['width']), int(window_state['height']))
                        
                    # 恢复最大化状态
                    if 'maximized' in window_state and window_state['maximized']:
                        window.showMaximized()
                    else:
                        window.showNormal()
                        
                    log.debug(f"通过设置管理器恢复窗口状态: {window_state}")
                else:
                    # 如果没有保存的状态，使用默认值
                    WindowManager.set_default_window_position(window)
            else:
                # 使用QSettings直接恢复
                settings = QSettings("GestroKey", "WindowState")
                
                # 恢复窗口几何信息
                geometry = settings.value("geometry")
                if geometry:
                    window.restoreGeometry(geometry)
                    
                # 恢复保存的正常几何信息
                normal_geometry = settings.value("normal_geometry")
                if normal_geometry:
                    window.normal_geometry = normal_geometry
                    
                # 恢复窗口状态
                maximized = settings.value("maximized", False, type=bool)
                
                if maximized:
                    window.showMaximized()
                else:
                    # 恢复位置和大小
                    pos = settings.value("pos")
                    size = settings.value("size")
                    
                    if pos:
                        window.move(pos)
                    if size:
                        window.resize(size)
                        
                    # 确保窗口在屏幕范围内
                    WindowManager.ensure_on_screen(window)
                    
                log.debug("窗口状态已从QSettings恢复")
        except Exception as e:
            log.error(f"恢复窗口状态时出错: {str(e)}")
            # 出错时使用默认位置
            WindowManager.set_default_window_position(window)
            
    @staticmethod
    def set_default_window_position(window):
        """设置默认窗口位置（居中）
        
        Args:
            window: 窗口实例
        """
        try:
            # 确保窗口有基本大小
            if window.width() < 800 or window.height() < 600:
                window.resize(1000, 600)
                
            # 获取屏幕几何信息
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            
            # 计算居中位置
            x = (screen_geometry.width() - window.width()) // 2
            y = (screen_geometry.height() - window.height()) // 2
            
            # 设置位置
            window.move(x, y)
            
            log.debug(f"窗口已设置为默认位置: ({x}, {y})")
        except Exception as e:
            log.error(f"设置默认窗口位置时出错: {str(e)}")
            
    @staticmethod
    def check_unsaved_changes(window):
        """检查是否有未保存的更改
        
        Args:
            window: 窗口实例
            
        Returns:
            bool: 是否有未保存的更改
        """
        try:
            # 检查设置页面
            if hasattr(window, 'current_page') and window.current_page == "settings":
                if hasattr(window, 'settings_page') and hasattr(window.settings_page, 'has_pending_changes'):
                    if window.settings_page.has_pending_changes():
                        log.debug("检测到设置页面有未保存的更改")
                        return True
                        
            # 检查手势页面
            if hasattr(window, 'current_page') and window.current_page == "gestures":
                if hasattr(window, 'gestures_page') and hasattr(window.gestures_page, 'has_unsaved_changes'):
                    if window.gestures_page.has_unsaved_changes():
                        log.debug("检测到手势页面有未保存的更改")
                        return True
                        
            # 如果没有检测到未保存的更改
            return False
        except Exception as e:
            log.error(f"检查未保存更改时出错: {str(e)}")
            return False
            
    @staticmethod
    def show_unsaved_changes_dialog(parent=None):
        """显示未保存更改对话框
        
        Args:
            parent: 父窗口
            
        Returns:
            str: 'save'保存, 'discard'放弃, 'cancel'取消
        """
        try:
            # 创建消息框
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("未保存的更改")
            msg_box.setText("您有未保存的更改。")
            msg_box.setInformativeText("您想要保存这些更改吗？")
            
            # 添加按钮
            save_button = msg_box.addButton("保存", QMessageBox.AcceptRole)
            discard_button = msg_box.addButton("放弃", QMessageBox.DestructiveRole)
            cancel_button = msg_box.addButton("取消", QMessageBox.RejectRole)
            
            # 设置默认按钮
            msg_box.setDefaultButton(save_button)
            
            # 显示对话框
            msg_box.exec_()
            
            # 返回结果
            clicked_button = msg_box.clickedButton()
            if clicked_button == save_button:
                log.debug("用户选择保存更改")
                return 'save'
            elif clicked_button == discard_button:
                log.debug("用户选择放弃更改")
                return 'discard'
            else:
                log.debug("用户取消操作")
                return 'cancel'
        except Exception as e:
            log.error(f"显示未保存更改对话框时出错: {str(e)}")
            return 'cancel'  # 出错时默认取消 