import logging
from PyQt5.QtCore import Qt, QPoint, QSize, QRect
from PyQt5.QtGui import QCursor

# 导入日志模块
from app.log import log

class WindowResizeHandler:
    """窗口大小调整处理器，用于实现无边框窗口的调整大小功能"""
    
    # 定义大小调整区域的枚举
    NONE = 0
    LEFT = 1
    TOP = 2
    RIGHT = 4
    BOTTOM = 8
    TOP_LEFT = TOP | LEFT
    TOP_RIGHT = TOP | RIGHT
    BOTTOM_LEFT = BOTTOM | LEFT
    BOTTOM_RIGHT = BOTTOM | RIGHT
    
    # 边缘宽度
    EDGE_WIDTH = 8
    
    def __init__(self, window):
        """初始化窗口大小调整处理器
        
        Args:
            window: 要处理的窗口
        """
        self.window = window
        self.resize_area = self.NONE
        self.drag_position = QPoint()
        self.drag_rect = None
        self.resizing = False
        
        log.debug("窗口大小调整处理器初始化完成")
        
    def _get_resize_area(self, pos, window_rect):
        """获取鼠标所在的调整区域
        
        Args:
            pos: 鼠标位置
            window_rect: 窗口矩形
            
        Returns:
            int: 调整区域代码
        """
        x, y = pos.x(), pos.y()
        width, height = window_rect.width(), window_rect.height()
        edge_width = self.EDGE_WIDTH
        
        # 判断鼠标位置
        is_left = x <= edge_width
        is_right = x >= width - edge_width
        is_top = y <= edge_width
        is_bottom = y >= height - edge_width
        
        # 确定调整区域
        if is_top and is_left:
            return self.TOP_LEFT
        elif is_top and is_right:
            return self.TOP_RIGHT
        elif is_bottom and is_left:
            return self.BOTTOM_LEFT
        elif is_bottom and is_right:
            return self.BOTTOM_RIGHT
        elif is_top:
            return self.TOP
        elif is_bottom:
            return self.BOTTOM
        elif is_left:
            return self.LEFT
        elif is_right:
            return self.RIGHT
        else:
            return self.NONE
            
    def update_cursor(self, pos, is_maximized=False):
        """更新鼠标样式
        
        Args:
            pos: 鼠标位置
            is_maximized: 窗口是否最大化
            
        Returns:
            bool: 是否在调整区域
        """
        # 如果窗口最大化，不需要调整大小
        if is_maximized:
            return False
            
        # 获取调整区域
        resize_area = self._get_resize_area(pos, self.window.rect())
        
        # 根据调整区域设置鼠标样式
        if resize_area == self.TOP_LEFT or resize_area == self.BOTTOM_RIGHT:
            self.window.setCursor(Qt.SizeFDiagCursor)
        elif resize_area == self.TOP_RIGHT or resize_area == self.BOTTOM_LEFT:
            self.window.setCursor(Qt.SizeBDiagCursor)
        elif resize_area == self.LEFT or resize_area == self.RIGHT:
            self.window.setCursor(Qt.SizeHorCursor)
        elif resize_area == self.TOP or resize_area == self.BOTTOM:
            self.window.setCursor(Qt.SizeVerCursor)
        else:
            self.window.setCursor(Qt.ArrowCursor)
            return False
            
        return True
        
    def handle_mouse_press(self, event, is_maximized=False):
        """处理鼠标按下事件
        
        Args:
            event: 鼠标事件
            is_maximized: 窗口是否最大化
            
        Returns:
            bool: 是否处理了事件
        """
        # 如果窗口最大化，不处理调整大小
        if is_maximized:
            return False
            
        # 只处理左键点击
        if event.button() != Qt.LeftButton:
            return False
            
        # 获取调整区域
        self.resize_area = self._get_resize_area(event.pos(), self.window.rect())
        
        # 如果不在调整区域，不处理
        if self.resize_area == self.NONE:
            return False
            
        # 记录拖动信息
        self.resizing = True
        self.drag_position = event.globalPos()
        self.drag_rect = self.window.geometry()
        
        log.debug(f"开始调整窗口大小，区域: {self.resize_area}")
        return True
        
    def handle_mouse_move(self, event, is_maximized=False):
        """处理鼠标移动事件
        
        Args:
            event: 鼠标事件
            is_maximized: 窗口是否最大化
            
        Returns:
            bool: 是否处理了事件
        """
        # 如果窗口最大化，不处理调整大小
        if is_maximized:
            self.window.setCursor(Qt.ArrowCursor)
            return False
            
        # 如果不在调整状态，只更新鼠标样式
        if not self.resizing:
            return self.update_cursor(event.pos())
            
        # 计算位置差异
        delta = event.globalPos() - self.drag_position
        
        # 新的几何信息
        new_rect = QRect(self.drag_rect)
        
        try:
            # 根据调整区域调整大小
            if self.resize_area & self.LEFT:
                # 左边界调整
                new_rect.setLeft(self.drag_rect.left() + delta.x())
            if self.resize_area & self.RIGHT:
                # 右边界调整
                new_rect.setRight(self.drag_rect.right() + delta.x())
            if self.resize_area & self.TOP:
                # 上边界调整
                new_rect.setTop(self.drag_rect.top() + delta.y())
            if self.resize_area & self.BOTTOM:
                # 下边界调整
                new_rect.setBottom(self.drag_rect.bottom() + delta.y())
                
            # 确保窗口不会小于最小大小
            min_size = self.window.minimumSize()
            if new_rect.width() < min_size.width():
                if self.resize_area & self.LEFT:
                    new_rect.setLeft(new_rect.right() - min_size.width())
                else:
                    new_rect.setRight(new_rect.left() + min_size.width())
                    
            if new_rect.height() < min_size.height():
                if self.resize_area & self.TOP:
                    new_rect.setTop(new_rect.bottom() - min_size.height())
                else:
                    new_rect.setBottom(new_rect.top() + min_size.height())
                    
            # 应用新的几何信息
            self.window.setGeometry(new_rect)
            
            log.debug(f"调整窗口大小: {new_rect.width()}x{new_rect.height()}")
        except Exception as e:
            log.error(f"调整窗口大小时出错: {str(e)}")
            
        return True
        
    def handle_mouse_release(self, event):
        """处理鼠标释放事件
        
        Args:
            event: 鼠标事件
            
        Returns:
            bool: 是否处理了事件
        """
        # 如果不是左键释放，不处理
        if event.button() != Qt.LeftButton:
            return False
            
        # 如果不在调整状态，不处理
        if not self.resizing:
            return False
            
        # 结束调整状态
        self.resizing = False
        self.resize_area = self.NONE
        
        # 更新鼠标样式
        self.update_cursor(event.pos())
        
        log.debug("结束调整窗口大小")
        return True 