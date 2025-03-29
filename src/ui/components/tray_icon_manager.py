import os
import sys
import logging
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# 导入日志模块
try:
    from app.log import log
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log

class TrayIconManager:
    """系统托盘图标管理器，用于管理应用程序的系统托盘图标和菜单"""
    
    def __init__(self, main_window, icon=None):
        """初始化系统托盘图标管理器
        
        Args:
            main_window: 主窗口实例，用于关联菜单动作
            icon: 托盘图标
        """
        self.main_window = main_window
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(main_window)
        
        # 设置图标
        if icon:
            self.tray_icon.setIcon(icon)
            log.debug("已设置系统托盘图标")
        else:
            log.warning("没有为系统托盘设置图标")
            
        # 创建托盘菜单
        self.tray_menu = QMenu()
        
        # 创建托盘菜单项
        self.setup_menu()
        
        # 设置菜单
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # 连接信号
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
        
        log.info("系统托盘图标初始化完成")
        
    def setup_menu(self):
        """设置托盘菜单"""
        try:
            # 打开主窗口动作
            self.show_action = QAction("显示主窗口", self.main_window)
            self.show_action.triggered.connect(self.show_main_window)
            
            # 切换手势识别状态动作
            self.toggle_action = QAction("启动手势识别", self.main_window)
            self.toggle_action.triggered.connect(self.toggle_drawing)
            
            # 设置页面动作
            self.settings_action = QAction("设置", self.main_window)
            self.settings_action.triggered.connect(self.main_window.show_settings_page)
            
            # 关于动作
            self.about_action = QAction("关于", self.main_window)
            self.about_action.triggered.connect(self.main_window.show_about_dialog)
            
            # 退出动作
            self.exit_action = QAction("退出", self.main_window)
            self.exit_action.triggered.connect(self.main_window.force_exit)
            
            # 添加动作到菜单
            self.tray_menu.addAction(self.show_action)
            self.tray_menu.addSeparator()
            self.tray_menu.addAction(self.toggle_action)
            self.tray_menu.addSeparator()
            self.tray_menu.addAction(self.settings_action)
            self.tray_menu.addAction(self.about_action)
            self.tray_menu.addSeparator()
            self.tray_menu.addAction(self.exit_action)
            
            log.debug("系统托盘菜单已设置")
        except Exception as e:
            log.error(f"设置托盘菜单时出错: {str(e)}")
            
    def update_menu(self, drawing_active=False):
        """更新托盘菜单状态
        
        Args:
            drawing_active: 绘制是否处于活动状态
        """
        try:
            # 更新显示/隐藏主窗口菜单项
            if self.main_window.isVisible():
                self.show_action.setText("隐藏主窗口")
            else:
                self.show_action.setText("显示主窗口")
                
            # 更新启动/停止手势识别菜单项
            if drawing_active:
                self.toggle_action.setText("停止手势识别")
            else:
                self.toggle_action.setText("启动手势识别")
                
            log.debug(f"已更新托盘菜单状态，绘制状态: {drawing_active}")
        except Exception as e:
            log.error(f"更新托盘菜单状态时出错: {str(e)}")
            
    def on_tray_icon_activated(self, reason):
        """处理托盘图标激活事件
        
        Args:
            reason: 激活原因
        """
        # 双击或单击显示/隐藏主窗口
        if reason == QSystemTrayIcon.DoubleClick or reason == QSystemTrayIcon.Trigger:
            self.toggle_window_visibility()
            log.debug(f"托盘图标被激活，原因: {reason}")
            
    def show_main_window(self):
        """显示主窗口"""
        # 如果窗口已经可见，则隐藏，否则显示
        self.toggle_window_visibility()
        
    def toggle_window_visibility(self):
        """切换窗口可见性"""
        if self.main_window.isVisible():
            self.main_window.hide()
            log.debug("主窗口已隐藏")
        else:
            # 显示窗口并激活
            self.main_window.show()
            self.main_window.activateWindow()
            log.debug("主窗口已显示并激活")
            
        # 更新菜单
        self.update_menu(self.main_window.drawing_active)
        
    def toggle_drawing(self):
        """切换绘制状态"""
        # 调用主窗口的切换方法
        self.main_window.toggle_drawing()
        
    def show_message(self, title, message, icon=QSystemTrayIcon.Information, timeout=5000):
        """显示托盘通知
        
        Args:
            title: 通知标题
            message: 通知消息
            icon: 通知图标类型
            timeout: 超时时间（毫秒）
        """
        try:
            # 检查系统是否支持托盘通知
            if QSystemTrayIcon.supportsMessages():
                self.tray_icon.showMessage(title, message, icon, timeout)
                log.debug(f"显示系统托盘通知: {title}")
            else:
                log.warning("系统不支持托盘通知")
        except Exception as e:
            log.error(f"显示托盘通知时出错: {str(e)}")
            
    def hide(self):
        """隐藏系统托盘图标"""
        try:
            if self.tray_icon:
                self.tray_icon.hide()
                log.debug("系统托盘图标已隐藏")
        except Exception as e:
            log.error(f"隐藏系统托盘图标时出错: {str(e)}")
            
    def is_visible(self):
        """检查托盘图标是否可见
        
        Returns:
            bool: 托盘图标是否可见
        """
        return self.tray_icon.isVisible() if self.tray_icon else False 