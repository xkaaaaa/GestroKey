import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath, QPixmap
from pynput import mouse

# 动态导入日志模块，处理不同运行方式下的导入路径问题
try:
    # 当作为包导入时（从主程序运行）
    from logger import get_logger
except ImportError:
    from core.logger import get_logger

class DrawingSignals(QObject):
    """信号类，用于在线程间安全地传递信号"""
    start_drawing_signal = pyqtSignal(int, int)
    continue_drawing_signal = pyqtSignal(int, int)
    stop_drawing_signal = pyqtSignal()

class TransparentDrawingOverlay(QWidget):
    """透明绘制覆盖层，用于捕获鼠标移动并绘制轨迹"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("DrawingOverlay")
        self.path = QPainterPath()
        self.drawing = False
        self.last_point = QPoint()
        self.points = []  # 存储所有轨迹点，每个元素为 (point, timestamp)
        self.point_lifetime = 0.8  # 每个点的生存时间（秒）
        self.buffer = None  # 绘图缓冲
        self.update_timer = QTimer(self)  # 确保计时器与窗口在同一线程
        self.update_timer.timeout.connect(self.delayed_update)
        self.update_timer.setInterval(16)  # 约60fps的更新频率
        
        # 优化绘图设置
        self.simplified_path = True  # 使用简化路径
        self.batch_update = True  # 批量更新
        self.batch_size = 5  # 每5个点更新一次
        self.point_counter = 0
        
        self.initUI()
        self.logger.debug("绘制覆盖层初始化完成")
        
    def initUI(self):
        # 创建一个全屏、透明、无边框的窗口，用于绘制
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # 完全透明，不影响鼠标事件
        # 获取屏幕尺寸
        screen_geometry = QApplication.desktop().screenGeometry()
        self.setGeometry(screen_geometry)
        # 创建绘图缓冲区
        self.buffer = QPixmap(screen_geometry.width(), screen_geometry.height())
        self.buffer.fill(Qt.transparent)
        # 隐藏窗口，仅在绘制时显示
        self.hide()
        self.logger.debug(f"UI初始化完成，屏幕尺寸: {screen_geometry.width()}x{screen_geometry.height()}")

    def startDrawing(self, x, y):
        """开始绘制"""
        # 验证坐标有效性，防止(0,0)点错误
        if x <= 0 or y <= 0:
            self.logger.warning(f"忽略无效的起始坐标: ({x}, {y})")
            return
            
        point = QPoint(x, y)
        self.path = QPainterPath()
        self.path.moveTo(point)
        self.last_point = point
        self.points = [(point, time.time())]  # 存储点和时间戳
        self.drawing = True
        self.point_counter = 0
        
        # 清空缓冲区
        self.buffer.fill(Qt.transparent)
        
        self.show()
        # 确保计时器在UI线程启动
        if not self.update_timer.isActive():
            self.update_timer.start()
        self.update()
        self.logger.debug(f"开始绘制，坐标: ({x}, {y})")
        
    def continueDrawing(self, x, y):
        """继续绘制轨迹"""
        if not self.drawing:
            return
            
        # 验证坐标有效性，防止无效坐标
        if x <= 0 or y <= 0:
            self.logger.warning(f"忽略无效的坐标: ({x}, {y})")
            return
            
        # 添加额外的防护：检查坐标与上一点的距离，防止跳跃性连线
        if self.last_point and not self.points:
            # 如果没有点但有last_point，说明发生了异常情况
            self.logger.warning("检测到异常状态：有last_point但points为空，重置路径")
            self.path = QPainterPath()
            self.path.moveTo(QPoint(x, y))
            self.points = [(QPoint(x, y), time.time())]
            self.last_point = QPoint(x, y)
            return
            
        # 计算与上一点的距离
        last_x = self.last_point.x()
        last_y = self.last_point.y()
        distance = ((x - last_x) ** 2 + (y - last_y) ** 2) ** 0.5
        
        # 如果距离过大(超过200像素)，说明可能是异常跳跃，不连接这两点
        if distance > 200:
            self.logger.warning(f"检测到点跳跃，距离: {distance:.2f}像素，重置路径")
            # 结束当前路径，开始新路径
            self.path = QPainterPath()
            point = QPoint(x, y)
            self.path.moveTo(point)
            self.points = [(point, time.time())]
            self.last_point = point
            return
            
        current_time = time.time()
        point = QPoint(x, y)
        
        # 添加点到列表，带时间戳
        self.points.append((point, current_time))
        self.point_counter += 1
        
        # 移除超过生存时间的点
        self.prune_expired_points(current_time)
        
        # 如果是第一个点或者点列表被完全清空了（极少发生）
        if not self.points:
            self.logger.warning("所有点已过期，重置路径")
            self.path = QPainterPath()
            return
        
        # 简化的路径更新方式
        if self.simplified_path:
            # 直接连接到新点，而不是使用曲线
            self.path.lineTo(point)
        else:
            # 使用线性插值代替复杂的贝塞尔曲线
            self.path.lineTo(point)
        
        self.last_point = point
            
        # 批量更新，而不是每个点都更新
        if self.batch_update:
            if self.point_counter >= self.batch_size:
                self.point_counter = 0
                self.update()
    
    def prune_expired_points(self, current_time=None):
        """移除过期的点"""
        if current_time is None:
            current_time = time.time()
            
        # 计算超时时间点
        expire_time = current_time - self.point_lifetime
        
        # 移除所有过期的点
        old_count = len(self.points)
        valid_points = [(pt, ts) for pt, ts in self.points if ts >= expire_time]
        new_count = len(valid_points)
        
        # 如果有点被移除，需要重建路径
        if new_count < old_count:
            self.logger.debug(f"移除 {old_count - new_count} 个过期点，剩余 {new_count} 个点")
            self.points = valid_points
            if self.points:  # 确保还有点存在
                self.rebuildPath()
            else:
                self.path = QPainterPath()
        
    def rebuildPath(self):
        """重新构建路径，使用简化的算法"""
        if not self.points:
            return
            
        self.path = QPainterPath()
        first_point = self.points[0][0]  # 获取第一个点（不包括时间戳）
        self.path.moveTo(first_point)
        
        # 简化路径构建，只使用直线连接
        for point_data in self.points[1:]:
            point = point_data[0]  # 只获取点，不需要时间戳
            self.path.lineTo(point)
        
        self.logger.debug(f"路径已重建，共 {len(self.points)} 个点")
    
    def delayed_update(self):
        """计时器触发的延迟更新，用于控制重绘频率"""
        if self.drawing:
            # 每次更新时检查并移除过期点
            self.prune_expired_points()
            self.update()
    
    def stopDrawing(self):
        """停止绘制并清除"""
        if not self.drawing:
            return
            
        self.drawing = False
        self.path = QPainterPath()
        self.points = []
        # 清空缓冲区
        self.buffer.fill(Qt.transparent)
        
        # 确保在UI线程停止计时器
        if self.update_timer.isActive():
            self.update_timer.stop()
        
        self.hide()
        self.logger.debug("停止绘制，清除路径")
    
    def paintEvent(self, event):
        """绘制事件处理 - 优化绘制性能"""
        if not self.drawing:
            return
            
        # 在缓冲区上绘制
        buffer_painter = QPainter(self.buffer)
        buffer_painter.setRenderHint(QPainter.Antialiasing, True)
        
        # 清除之前的绘制内容，保留透明背景
        self.buffer.fill(Qt.transparent)
        
        # 简化绘制 - 只绘制一种线条样式
        pen = QPen(QColor(0, 120, 255, 200), 3)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        buffer_painter.setPen(pen)
        buffer_painter.drawPath(self.path)
        
        buffer_painter.end()
        
        # 将缓冲区内容绘制到窗口
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.buffer)


class DrawingManager:
    """绘制管理器，只负责管理绘制功能"""
    
    def __init__(self):
        # 初始化日志记录器
        self.logger = get_logger("DrawingManager")
        self.logger.info("初始化绘制管理器")
        
        # 创建应用程序实例
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
            self.logger.debug("创建新的QApplication实例")
        else:
            self.logger.debug("使用现有的QApplication实例")
        
        # 创建信号对象，用于线程间通信
        self.signals = DrawingSignals()
        
        # 创建透明绘制覆盖层
        self.overlay = TransparentDrawingOverlay()
        
        # 连接信号到绘制方法
        self.signals.start_drawing_signal.connect(self.overlay.startDrawing)
        self.signals.continue_drawing_signal.connect(self.overlay.continueDrawing)
        self.signals.stop_drawing_signal.connect(self.overlay.stopDrawing)
        
        # 设置全局鼠标钩子
        self.init_mouse_hook()
        
        self.right_mouse_down = False
        
        self.logger.info("绘制模块初始化完成")
    
    def init_mouse_hook(self):
        """初始化全局鼠标监听"""
        try:
            def on_move(x, y):
                # 鼠标移动时，如果正在绘制，则通过信号更新绘制路径
                if self.right_mouse_down:
                    # 确保坐标有效
                    if x > 0 and y > 0:
                        self.signals.continue_drawing_signal.emit(x, y)
            
            def on_click(x, y, button, pressed):
                # 右键按下时开始绘制，松开时停止
                if button == mouse.Button.right:
                    if pressed:
                        # 确保坐标有效
                        if x > 0 and y > 0:
                            self.right_mouse_down = True
                            self.signals.start_drawing_signal.emit(x, y)
                            self.logger.info(f"开始绘制，坐标: ({x}, {y})")
                    else:
                        self.right_mouse_down = False
                        self.signals.stop_drawing_signal.emit()
                        self.logger.info("停止绘制")
            
            # 设置监听器
            self.mouse_listener = mouse.Listener(
                on_move=on_move,
                on_click=on_click
            )
            self.mouse_listener.start()
            self.logger.info("鼠标监听器已启动")
            
        except ImportError as e:
            self.logger.error(f"无法导入pynput库: {e}，请确保已安装: pip install pynput")
            self.quit()
        except Exception as e:
            self.logger.exception(f"初始化鼠标监听器时发生错误: {e}")
            self.quit()
    
    def run(self):
        """运行应用程序"""
        self.logger.info("绘制模块已启动")
        try:
            sys.exit(self.app.exec_())
        except Exception as e:
            self.logger.exception(f"应用程序运行时发生错误: {e}")
    
    def quit(self):
        """退出应用程序"""
        self.logger.info("退出应用程序")
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
            self.logger.debug("鼠标监听器已停止")
        self.app.quit()


if __name__ == "__main__":
    try:
        drawer = DrawingManager()
        drawer.run()
    except Exception as e:
        # 获取一个独立的日志记录器记录主程序异常
        error_logger = get_logger("MainError")
        error_logger.exception(f"主程序发生未捕获的异常: {e}") 