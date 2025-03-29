import os
import sys
import time
import signal
import argparse
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QObject, pyqtSignal

# 添加资源目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# 确保app模块可以被导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入版本信息
from version import __version__, __title__, __copyright__, get_about_text

# 导入应用日志模块
from app.log import log, setup_logger, shutdown_logger

# 导入应用初始化模块
from app._init_app import initialize_app

# 导入设置管理器
from ui.utils.settings_manager import SettingsManager

# 导入墨水绘图类
from app.ink_painter import InkPainter, set_debug_mode

# 导入主窗口
from ui.main_window_new import MainWindow

# 导入资源管理器
from ui.utils.resource_manager import ResourceManager

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
            
            # 强制重新初始化墨水绘图对象以应用最新设置
            if self.ink_painter is not None:
                log.info("重置墨水绘图器以应用最新设置")
                try:
                    # 尝试重置现有实例来应用新设置
                    if hasattr(self.ink_painter, 'reset_painter'):
                        self.ink_painter.reset_painter()
                        log.debug(f"重置后的墨水绘图器颜色设置: {self.ink_painter.line_color}")
                    else:
                        # 如果没有reset_painter方法，关闭现有实例并重新创建
                        self.ink_painter.shutdown()
                        self.ink_painter = None
                except Exception as e:
                    log.warning(f"重置墨水绘图器实例时出错: {str(e)}")
                    # 失败时关闭并重新创建
                    try:
                        self.ink_painter.shutdown()
                    except:
                        pass
                    self.ink_painter = None
            
            # 如果需要，创建新的墨水绘图对象
            if self.ink_painter is None:
                try:
                    log.info("初始化墨水绘图器")
                    self.ink_painter = InkPainter()
                    log.debug(f"墨水绘图器当前颜色设置: {self.ink_painter.line_color}")
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
            
        Returns:
            是否成功应用设置
        """
        log.info("正在应用新设置: " + str(settings.keys()))
        
        success = True
        
        try:
            # 如果墨水绘图对象已初始化，更新其设置
            if self.ink_painter is not None:
                try:
                    # 检查是否有绘画设置的直接更新
                    if "drawing_settings" in settings:
                        # 获取传递过来的绘画设置
                        drawing_settings = settings.get("drawing_settings", {})
                        if drawing_settings:
                            log.info(f"更新墨水绘图器设置（通过绘画设置直接更新）: {list(drawing_settings.keys())}")
                            log.debug(f"绘画颜色设置: {drawing_settings.get('color', '未设置')}")
                            if self.ink_painter.update_drawing_settings(drawing_settings):
                                log.info("墨水绘图器设置已直接更新成功")
                                log.debug(f"更新后的颜色: {self.ink_painter.line_color if hasattr(self.ink_painter, 'line_color') else '未知'}")
                            else:
                                log.warning("墨水绘图器设置更新可能部分失败")
                                success = False
                    # 或者从settings中的drawing分类获取
                    elif "drawing" in settings:
                        drawing_settings = settings.get("drawing", {})
                        if drawing_settings:
                            log.info(f"更新墨水绘图器设置（通过settings.drawing更新）: {list(drawing_settings.keys())}")
                            log.debug(f"绘画颜色设置: {drawing_settings.get('color', '未设置')}")
                            if self.ink_painter.update_drawing_settings(drawing_settings):
                                log.info("墨水绘图器设置已更新成功")
                                log.debug(f"更新后的颜色: {self.ink_painter.line_color if hasattr(self.ink_painter, 'line_color') else '未知'}")
                            else:
                                log.warning("墨水绘图器设置更新可能部分失败")
                                success = False
                except Exception as e:
                    log.error(f"更新绘图设置失败: {str(e)}")
                    import traceback
                    log.error(f"异常堆栈: {traceback.format_exc()}")
                    success = False
                    
            # 应用其他设置
            if "app" in settings:
                app_settings = settings.get("app", {})
                log.info(f"应用app设置: {list(app_settings.keys())}")
                # 可以在此处理应用设置...
                
            if "gesture" in settings:
                gesture_settings = settings.get("gesture", {})
                log.info(f"应用gesture设置: {list(gesture_settings.keys())}")
                # 可以在此处理手势设置...
            
            log.info("已应用新设置，状态: " + ("成功" if success else "部分失败"))
            return success
            
        except Exception as e:
            log.error(f"应用设置过程中发生错误: {str(e)}")
            import traceback
            log.error(f"异常堆栈: {traceback.format_exc()}")
            return False
        
    def cleanup(self):
        """清理资源"""
        log.info("应用控制器正在清理资源...")
        
        # 停止手势识别
        if self.gesture_recognition_active:
            try:
                self.stop_gesture_recognition()
                log.debug("已停止手势识别")
            except Exception as e:
                log.error(f"停止手势识别失败: {str(e)}")
        
        # 释放墨水绘图器资源
        if self.ink_painter is not None:
            try:
                log.info("正在关闭墨水绘图器...")
                self.ink_painter.shutdown()
                self.ink_painter = None
                log.info("墨水绘图器已成功关闭")
            except Exception as e:
                log.error(f"关闭墨水绘图器失败: {str(e)}")
                try:
                    import traceback
                    log.error(f"异常详情: {traceback.format_exc()}")
                except:
                    pass
        
        # 断开所有信号连接
        try:
            # 断开状态更新信号
            if hasattr(self, 'sigStatusUpdate'):
                try:
                    # 使用QObject的方法断开所有连接
                    self.sigStatusUpdate.disconnect()
                except:
                    pass
                    
            # 其他需要断开的信号可以在这里添加
            
            log.debug("已断开信号连接")
        except Exception as e:
            log.error(f"断开信号连接失败: {str(e)}")
        
        # 释放其他资源
        # ...
            
        log.info("应用控制器资源已完全清理")

def parse_arguments():
    """解析命令行参数
    
    Returns:
        解析后的参数对象
    """
    parser = argparse.ArgumentParser(description="GestroKey - 手势控制应用")
    parser.add_argument("--debug", "-d", action="store_true", help="启用调试模式，显示详细日志")
    return parser.parse_args()

def main():
    """应用程序入口函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='GestroKey - 一款基于鼠标手势的自动化工具')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    args = parser.parse_args()
    
    # 设置调试模式
    debug_mode = args.debug
    setup_logger(debug_mode)
    set_debug_mode(debug_mode)
    
    # 记录启动信息
    log.info(f"{__title__} v{__version__} 启动中...")
    if debug_mode:
        log.info("调试模式已启用")
    
    # 预初始化应用程序组件，提高后续响应速度
    startup_time = time.time()
    log.info("开始预初始化应用程序组件...")
    initialize_app(async_init=True)  # 异步初始化，不阻塞UI加载
    log.info(f"应用预初始化启动耗时: {time.time() - startup_time:.3f}秒")
    
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 设置应用程序信息
    QApplication.setApplicationName(__title__)
    QApplication.setApplicationVersion(__version__)
    QApplication.setOrganizationName("GestroKey")
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 添加资源管理器初始化
    ResourceManager.register_resources()
    
    # 初始化设置管理器
    settings_manager = SettingsManager()
    
    # 初始化应用控制器
    app_controller = AppController(settings_manager)
    
    # 定义清理函数，用于关闭资源
    def cleanup():
        """清理函数"""
        try:
            # 确保控制器资源被正确释放
            app_controller.cleanup()
            
            # 关闭操作执行进程池
            try:
                from app.operation_executor import shutdown as shutdown_executor
                shutdown_executor()
                log.info("操作执行进程池已关闭")
            except Exception as e:
                log.error(f"关闭操作执行进程池失败: {e}")
                  
            # 在调试模式下弹出问题解决情况反馈对话框
            if debug_mode:
                from PyQt5.QtWidgets import QInputDialog, QLineEdit
                
                feedback, ok = QInputDialog.getText(
                    None, 
                    "调试反馈", 
                    "请输入问题解决情况（取消则不记录）:", 
                    QLineEdit.Normal, 
                    ""
                )
                
                if ok and feedback:
                    log.info(f"调试反馈: {feedback}")
                    print(f"已记录调试反馈: {feedback}")
            
            # 确保日志系统正确关闭
            shutdown_logger()
            
        except Exception as e:
            print(f"清理资源时出错: {str(e)}")
            
        log.info("GestroKey正常退出")
    
    # 创建主窗口
    main_window = MainWindow(app, settings_manager, app_controller)
    
    # 显示主窗口
    main_window.show()
    
    # 加载应用程序设置
    all_settings = settings_manager.get_settings()
    app_settings = all_settings.get("app", {})
    
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
    app.aboutToQuit.connect(cleanup)
    
    # 启动应用程序主循环
    ret = app.exec_()
    
    # 确保在返回退出码前执行清理
    cleanup()
    
    return ret

if __name__ == "__main__":
    main()