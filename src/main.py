import os
import sys
import time
import signal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QObject, pyqtSignal

# 确保app模块可以被导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用日志模块
from app.log import log, setup_logger

# 导入设置管理器
from ui.utils.settings_manager import SettingsManager

# 导入墨水绘图类
from app.ink_painter import InkPainter

# 导入主窗口
from ui.main_window import MainWindow

# 导入应用控制器
class AppController(QObject):
    """应用控制器类，负责处理应用程序的主要逻辑"""
    
    # 信号定义
    sigStatusUpdate = pyqtSignal(str, str)  # 状态更新信号（类型，值）
    
    def __init__(self, settings_manager):
        """初始化应用控制器
        
        Args:
            settings_manager: 设置管理器实例
        """
        super().__init__()
        
        # 保存设置管理器
        self.settings_manager = settings_manager
        
        # 初始化InkPainter（延迟初始化，等到真正需要时再创建）
        self.ink_painter = None
        
        # 状态变量
        self.gesture_recognition_active = False
        self.current_status = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "os_name": f"{os.name} {sys.platform}",
            "runtime": 0,
            "status": "ready"
        }
        
        # 记录启动时间
        self.start_time = time.time()
        
        # 初始化时间戳
        self.last_update_time = time.time()
        
        log.info("应用控制器已初始化")
        
    def start_gesture_recognition(self):
        """启动手势识别"""
        if not self.gesture_recognition_active:
            log.debug("开始准备启动手势识别")
            
            # 如果墨水绘图对象未初始化，先初始化
            if self.ink_painter is None:
                try:
                    log.info("初始化墨水绘图器")
                    self.ink_painter = InkPainter()
                    log.info("墨水绘图器初始化成功")
                except Exception as e:
                    log.error(f"初始化墨水绘图器失败: {str(e)}")
                    import traceback
                    log.error(f"异常堆栈: {traceback.format_exc()}")
                    # 通知UI更新状态
                    self.update_status("status", "error")
                    return
            
            # 启动绘图模式
            try:
                log.info("启动墨水绘图模式")
                self.ink_painter.canvas.show()  # 显示绘图画布
                log.info("绘图画布已显示")
                
                self.gesture_recognition_active = True
                self.update_status("status", "running")
                
                log.info("手势识别已启动")
            except Exception as e:
                log.error(f"启动手势识别失败: {str(e)}")
                import traceback
                log.error(f"异常堆栈: {traceback.format_exc()}")
                # 通知UI更新状态
                self.update_status("status", "error")
            
    def stop_gesture_recognition(self):
        """停止手势识别"""
        if self.gesture_recognition_active:
            log.debug("准备停止手势识别")
            
            # 停止绘图模式
            if self.ink_painter is not None:
                try:
                    log.info("隐藏绘图画布")
                    self.ink_painter.canvas.hide()  # 隐藏绘图画布
                    log.info("绘图画布已隐藏")
                except Exception as e:
                    log.error(f"隐藏绘图画布失败: {str(e)}")
                    import traceback
                    log.error(f"异常堆栈: {traceback.format_exc()}")
            
            self.gesture_recognition_active = False
            self.update_status("status", "stopped")
            
            log.info("手势识别已停止")
            
    def update_status(self, key, value):
        """更新状态信息
        
        Args:
            key: 状态键名
            value: 状态值
        """
        if key in self.current_status and self.current_status[key] != value:
            self.current_status[key] = value
            
            # 发出状态更新信号
            self.sigStatusUpdate.emit(key, str(value))
            
    def apply_settings(self, settings):
        """应用设置
        
        Args:
            settings: 要应用的设置
        """
        # 如果墨水绘图对象已初始化，更新其设置
        if self.ink_painter is not None:
            try:
                # 获取绘图相关设置
                drawing_settings = settings.get("drawing_settings", {})
                if drawing_settings:
                    log.info("更新墨水绘图器设置")
                    self.ink_painter.update_drawing_settings(drawing_settings)
                    log.info("墨水绘图器设置已更新")
            except Exception as e:
                log.error(f"更新绘图设置失败: {str(e)}")
                import traceback
                log.error(f"异常堆栈: {traceback.format_exc()}")
        
        log.info("已应用新设置")
        
    def cleanup(self):
        """清理资源"""
        # 停止手势识别
        if self.gesture_recognition_active:
            self.stop_gesture_recognition()
        
        # 释放墨水绘图器资源
        if self.ink_painter is not None:
            try:
                log.info("关闭墨水绘图器")
                self.ink_painter.shutdown()
                log.info("墨水绘图器已关闭")
            except Exception as e:
                log.error(f"关闭墨水绘图器失败: {str(e)}")
                import traceback
                log.error(f"异常堆栈: {traceback.format_exc()}")
            
        log.info("应用控制器资源已清理")

def main():
    """主函数"""
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 设置应用程序信息
    QApplication.setApplicationName("GestroKey")
    QApplication.setApplicationVersion("1.0.0")
    QApplication.setOrganizationName("GestroKey")
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 初始化日志
    setup_logger()
    
    # 记录启动信息
    log.info("GestroKey启动")
    
    # 初始化设置管理器
    settings_manager = SettingsManager()
    
    # 初始化应用控制器
    app_controller = AppController(settings_manager)
    
    # 创建主窗口
    main_window = MainWindow(app, settings_manager, app_controller)
    
    # 显示主窗口
    main_window.show()
    
    # 应用设置
    app_settings = settings_manager.get_settings().get("app", {})
    
    # 如果设置为启动时最小化
    if app_settings.get("start_minimized", False):
        main_window.hide()
        
    # 如果设置为自动开始识别
    if app_settings.get("auto_start_recognition", False):
        # 延迟一秒后启动，确保UI已经完全加载
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, main_window.toggle_drawing)
    
    # 捕获SIGINT信号，确保应用能够正常退出
    def signal_handler(signum, frame):
        """信号处理函数"""
        log.info(f"收到信号 {signum}，准备退出")
        app.quit()
        
    signal.signal(signal.SIGINT, signal_handler)
    
    # 在主循环结束前进行清理
    def cleanup():
        """清理函数"""
        app_controller.cleanup()
        log.info("GestroKey正常退出")
        
    app.aboutToQuit.connect(cleanup)
    
    # 运行应用程序主循环
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 