import sys
import os
import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QToolButton
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QPainter, QPen, QColor, QPolygon, QTransform, QIcon
from PyQt6.QtSvgWidgets import QSvgWidget

try:
    from core.logger import get_logger
    from core.path_analyzer import PathAnalyzer
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger
    from core.path_analyzer import PathAnalyzer


class GestureDrawingWidget(QWidget):
    """手势绘制组件，用于在手势管理界面绘制手势路径"""
    
    pathCompleted = pyqtSignal(dict)  # 路径完成信号，发送格式化的路径
    testSimilarity = pyqtSignal()  # 测试相似度信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("GestureDrawingWidget")
        self.path_analyzer = PathAnalyzer()
        
        # 绘制状态
        self.drawing = False
        self.current_path = []
        self.completed_paths = []
        
        # 历史记录（用于撤回/还原）
        self.path_history = []  # 历史记录
        self.history_index = -1  # 当前历史索引
        
        # 工具状态
        self.current_tool = "brush"  # 当前工具：brush 或 pointer
        self.selected_point_index = -1  # 选中的点索引
        self.dragging_point = False  # 是否正在拖拽点

        
        # 视图变换属性
        self.view_scale = 1.0  # 缩放因子
        self.view_offset = QPoint(0, 0)  # 视图偏移
        self.min_scale = 0.1  # 最小缩放
        self.max_scale = 5.0  # 最大缩放
        

        
        # 拖拽状态
        self.panning = False
        self.last_pan_point = QPoint()
        self.space_pressed = False
        
        # 双击检测
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self._single_click_timeout)
        self.click_count = 0
        
        # 设置最小尺寸
        self.setMinimumSize(350, 200)  # 增加宽度以容纳工具栏
        self.setStyleSheet("background-color: white;")
        
        # 启用键盘焦点和滚轮事件
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.initUI()
        
    def initUI(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # 创建左侧工具栏（在画布外）
        self.create_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # 创建右侧绘制区域占位（用于布局计算）
        self.drawing_area = QWidget()
        self.drawing_area.setStyleSheet("background-color: transparent;")
        self.drawing_area.setMinimumSize(300, 200)
        main_layout.addWidget(self.drawing_area, 1)  # 让绘制区域占据剩余空间
        
        self.setLayout(main_layout)
        
    def create_toolbar(self):
        """创建左侧工具栏"""
        self.toolbar = QFrame()
        self.toolbar.setFrameStyle(QFrame.Shape.Box)
        self.toolbar.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-right: 2px solid #aaa;
            }
            QToolButton {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #bbb;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
                border: 1px solid #999;
            }
            QToolButton:checked {
                background-color: #c0c0ff;
                border: 1px solid #8080ff;
            }
        """)
        self.toolbar.setFixedWidth(50)
        
        toolbar_layout = QVBoxLayout()
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout.setSpacing(5)
        
        # 画笔工具按钮
        self.brush_btn = QToolButton()
        self.brush_btn.setIcon(self.load_svg_icon("brush.svg"))
        self.brush_btn.setIconSize(QSize(24, 24))
        self.brush_btn.setToolTip("画笔工具")
        self.brush_btn.setCheckable(True)
        self.brush_btn.setChecked(True)  # 默认选中
        self.brush_btn.clicked.connect(self.select_brush_tool)
        toolbar_layout.addWidget(self.brush_btn)
        
        # 点击工具按钮
        self.pointer_btn = QToolButton()
        self.pointer_btn.setIcon(self.load_svg_icon("pointer.svg"))
        self.pointer_btn.setIconSize(QSize(24, 24))
        self.pointer_btn.setToolTip("点击工具 - 添加和移动点")
        self.pointer_btn.setCheckable(True)
        self.pointer_btn.clicked.connect(self.select_pointer_tool)
        toolbar_layout.addWidget(self.pointer_btn)
        
        # 分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #aaa;")
        toolbar_layout.addWidget(separator)
        
        # 撤回按钮
        self.undo_btn = QToolButton()
        self.undo_btn.setIcon(self.load_svg_icon("undo.svg"))
        self.undo_btn.setIconSize(QSize(24, 24))
        self.undo_btn.setToolTip("撤回 (Ctrl+Z)")
        self.undo_btn.clicked.connect(self.undo_action)
        toolbar_layout.addWidget(self.undo_btn)
        
        # 还原按钮
        self.redo_btn = QToolButton()
        self.redo_btn.setIcon(self.load_svg_icon("redo.svg"))
        self.redo_btn.setIconSize(QSize(24, 24))
        self.redo_btn.setToolTip("还原 (Ctrl+Y)")
        self.redo_btn.clicked.connect(self.redo_action)
        toolbar_layout.addWidget(self.redo_btn)
        
        # 第二个分割线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet("color: #aaa;")
        toolbar_layout.addWidget(separator2)
        
        # 测试相似度按钮
        self.test_btn = QToolButton()
        self.test_btn.setIcon(self.load_svg_icon("test.svg"))
        self.test_btn.setIconSize(QSize(24, 24))
        self.test_btn.setToolTip("测试相似度")
        self.test_btn.clicked.connect(self.test_similarity)
        toolbar_layout.addWidget(self.test_btn)
        
        # 弹性空间
        toolbar_layout.addStretch()
        
        self.toolbar.setLayout(toolbar_layout)
        
        # 更新按钮状态
        self.update_toolbar_buttons()
        
    def load_svg_icon(self, filename):
        """加载SVG图标"""
        try:
            # 构建图标文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))  # src/ui/gestures/
            ui_dir = os.path.dirname(current_dir)  # src/ui/
            src_dir = os.path.dirname(ui_dir)  # src/
            icon_path = os.path.join(src_dir, "assets", "images", filename)
            
            if os.path.exists(icon_path):
                return QIcon(icon_path)
            else:
                self.logger.warning(f"图标文件不存在: {icon_path}")
                return QIcon()  # 返回空图标
        except Exception as e:
            self.logger.error(f"加载图标失败 {filename}: {e}")
            return QIcon()
    
    def select_brush_tool(self):
        """选择画笔工具"""
        self.current_tool = "brush"
        self.brush_btn.setChecked(True)
        self.pointer_btn.setChecked(False)
        self.selected_point_index = -1
        self.dragging_point = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.logger.info("切换到画笔工具")
        
    def select_pointer_tool(self):
        """选择点击工具"""
        self.current_tool = "pointer"
        self.brush_btn.setChecked(False)
        self.pointer_btn.setChecked(True)
        self.drawing = False  # 停止绘制模式
        self.selected_point_index = -1
        self.dragging_point = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logger.info("切换到点击工具")
        
    def undo_action(self):
        """撤回操作"""
        if self.history_index > 0:
            self.history_index -= 1
            import copy
            self.completed_paths = copy.deepcopy(self.path_history[self.history_index])
            self.update()
            self.update_toolbar_buttons()
            self.logger.info(f"撤回到历史记录 {self.history_index}，路径数量: {len(self.completed_paths)}")
            
    def redo_action(self):
        """还原操作"""
        if self.history_index < len(self.path_history) - 1:
            self.history_index += 1
            import copy
            self.completed_paths = copy.deepcopy(self.path_history[self.history_index])
            self.update()
            self.update_toolbar_buttons()
            self.logger.info(f"还原到历史记录 {self.history_index}，路径数量: {len(self.completed_paths)}")
            
    def update_toolbar_buttons(self):
        """更新工具栏按钮状态"""
        # 更新撤回按钮状态
        self.undo_btn.setEnabled(self.history_index > 0)
        
        # 更新还原按钮状态
        self.redo_btn.setEnabled(self.history_index < len(self.path_history) - 1)
        
        # 更新测试按钮状态：有路径时启用
        self.test_btn.setEnabled(bool(self.completed_paths))
    
    def test_similarity(self):
        """测试相似度"""
        self.testSimilarity.emit()
        
    def save_to_history(self):
        """保存当前状态到历史记录"""
        import copy
        
        # 删除当前索引之后的历史记录（如果用户在撤回后进行了新操作）
        if self.history_index < len(self.path_history) - 1:
            self.path_history = self.path_history[:self.history_index + 1]
        
        # 添加新的历史状态（深拷贝）
        self.path_history.append(copy.deepcopy(self.completed_paths))
        self.history_index = len(self.path_history) - 1
        
        # 限制历史记录数量（避免内存占用过多）
        max_history = 50
        if len(self.path_history) > max_history:
            self.path_history = self.path_history[-max_history:]
            self.history_index = len(self.path_history) - 1
            
        self.update_toolbar_buttons()
        self.logger.debug(f"保存历史记录，当前索引: {self.history_index}, 总数: {len(self.path_history)}")
        
    def keyPressEvent(self, event):
        """键盘按下事件"""
        if event.key() == Qt.Key.Key_Space:
            self.space_pressed = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif event.key() == Qt.Key.Key_Z and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Z 撤回
            self.undo_action()
        elif event.key() == Qt.Key.Key_Y and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Y 还原
            self.redo_action()
        elif event.key() == Qt.Key.Key_Delete and self.current_tool == "pointer" and self.selected_point_index >= 0:
            # Delete键删除选中的点
            self._delete_selected_point()
        super().keyPressEvent(event)
        
    def keyReleaseEvent(self, event):
        """键盘释放事件"""
        if event.key() == Qt.Key.Key_Space:
            self.space_pressed = False
            if not self.panning:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        super().keyReleaseEvent(event)
        
    def wheelEvent(self, event):
        """滚轮事件 - Alt+滚轮缩放"""
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            # 计算缩放中心点（鼠标位置）
            try:
                zoom_center = event.position().toPoint()
            except:
                # 兼容性处理
                zoom_center = event.pos()
            
            # 计算缩放因子 - 使用angleDelta().y()或pixelDelta().y()
            angle_delta = event.angleDelta()
            pixel_delta = event.pixelDelta()
            
            # 获取滚动增量 - 通常在y()，但在某些情况下可能在x()
            if not angle_delta.isNull():
                delta = angle_delta.y() if angle_delta.y() != 0 else angle_delta.x()
            elif not pixel_delta.isNull():
                delta = pixel_delta.y() if pixel_delta.y() != 0 else pixel_delta.x()
            else:
                delta = 0
            
            # 如果没有有效的delta值，跳过处理
            if delta == 0:
                event.accept()
                return
            
            # 修正缩放方向：向上滚动(delta>0)放大，向下滚动(delta<0)缩小
            if delta > 0:
                scale_factor = 1.2  # 放大
            else:
                scale_factor = 1.0 / 1.2  # 缩小
            new_scale = self.view_scale * scale_factor
            
            # 限制缩放范围
            new_scale = max(self.min_scale, min(self.max_scale, new_scale))
            
            if new_scale != self.view_scale:
                # 计算缩放后的偏移调整，使缩放围绕鼠标位置进行
                # 将鼠标位置转换为视图坐标
                view_center_x = (zoom_center.x() - self.view_offset.x()) / self.view_scale
                view_center_y = (zoom_center.y() - self.view_offset.y()) / self.view_scale
                
                # 更新缩放
                self.view_scale = new_scale
                
                # 调整偏移以保持鼠标位置不变
                new_offset_x = zoom_center.x() - view_center_x * self.view_scale
                new_offset_y = zoom_center.y() - view_center_y * self.view_scale
                self.view_offset = QPoint(int(new_offset_x), int(new_offset_y))
                
                self.update()
                
            event.accept()
        else:
            super().wheelEvent(event)
            
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.setFocus()  # 获取键盘焦点
        
        # 检查是否在绘制区域内
        if not self._is_in_drawing_area(event.pos()):
            return
        
        if event.button() == Qt.MouseButton.MiddleButton:
            # 中键双击检测
            self.click_count += 1
            if self.click_count == 1:
                self.click_timer.start(300)  # 300ms内等待第二次点击
            elif self.click_count == 2:
                self.click_timer.stop()
                self._reset_view()  # 双击中键归位
                self.click_count = 0
                return
                
            # 开始拖拽
            self.panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            
        elif event.button() == Qt.MouseButton.LeftButton:
            if self.space_pressed:
                # 空格+左键拖拽
                self.panning = True
                self.last_pan_point = event.pos()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            else:
                if self.current_tool == "brush":
                    # 画笔工具 - 正常绘制，开始新笔画时清除之前的内容
                    if not self.drawing:  # 只在开始新笔画时清除
                        self.current_path = []
                        self.completed_paths = []
                    self.drawing = True
                    # 调整坐标为绘制区域坐标，然后转换为视图坐标
                    adjusted_pos = self._adjust_for_drawing_area(event.pos())
                    view_pos = self._screen_to_view(adjusted_pos)
                    self.current_path = [view_pos]
                    self.update()
                elif self.current_tool == "pointer":
                    # 点击工具 - 添加点或选择/移动点（使用屏幕坐标）
                    self._handle_pointer_click(event.pos())
                
    def _single_click_timeout(self):
        """单击超时"""
        self.click_count = 0
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.panning:
            # 拖拽画布
            delta = event.pos() - self.last_pan_point
            self.view_offset += delta
            self.last_pan_point = event.pos()
            self.update()
        elif self.current_tool == "brush" and self.drawing and self._is_in_drawing_area(event.pos()):
            # 画笔工具 - 绘制手势
            adjusted_pos = self._adjust_for_drawing_area(event.pos())
            view_pos = self._screen_to_view(adjusted_pos)
            self.current_path.append(view_pos)
            self.update()
        elif self.current_tool == "pointer" and self.dragging_point and self._is_in_drawing_area(event.pos()):
            # 点击工具 - 拖拽点（使用屏幕坐标）
            self._update_dragging_point(event.pos())
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.panning and (event.button() == Qt.MouseButton.MiddleButton or 
                           (event.button() == Qt.MouseButton.LeftButton and self.space_pressed)):
            self.panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor if self.space_pressed else Qt.CursorShape.PointingHandCursor if self.current_tool == "pointer" else Qt.CursorShape.ArrowCursor)
            
        elif self.current_tool == "brush" and self.drawing and event.button() == Qt.MouseButton.LeftButton and not self.space_pressed:
            # 画笔工具 - 完成绘制
            self.drawing = False
            if len(self.current_path) > 1:
                # 格式化路径 - 注意这里current_path已经是视图坐标
                raw_points = [(p.x(), p.y(), 0.5, 0.0, 1) for p in self.current_path]
                formatted_path = self.path_analyzer.format_raw_path(raw_points)
                
                if formatted_path and formatted_path.get('points'):
                    self.completed_paths.append(formatted_path)
                    # 保存到历史记录
                    self.save_to_history()
                    # 绘制完成后重置视图以适应新路径
                    self._reset_view()
                    # 自动使用此路径
                    self.pathCompleted.emit(formatted_path)
                    self.logger.info(f"自动使用格式化路径：{len(formatted_path.get('points', []))}个关键点")
            
            self.current_path = []
            self.update()
            
        elif self.current_tool == "pointer" and self.dragging_point and event.button() == Qt.MouseButton.LeftButton:
            # 点击工具 - 完成拖拽
            self.dragging_point = False
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            # 保存到历史记录
            self.save_to_history()
            
            # 不发送路径更新信号，避免路径被替换
            self.logger.info(f"完成拖拽点 {self.selected_point_index}")
            # 保持选中状态，不清除 self.selected_point_index
            
    def _is_in_drawing_area(self, pos):
        """检查位置是否在绘制区域内"""
        if not hasattr(self, 'drawing_area'):
            return True
        # 获取绘制区域在主窗口中的位置
        drawing_area_pos = self.drawing_area.mapTo(self, QPoint(0, 0))
        drawing_area_rect = self.drawing_area.geometry()
        drawing_area_rect.moveTopLeft(drawing_area_pos)
        return drawing_area_rect.contains(pos)
        
    def _adjust_for_drawing_area(self, pos):
        """调整坐标为绘制区域相对坐标"""
        if not hasattr(self, 'drawing_area'):
            return pos
        # 获取绘制区域在主窗口中的位置
        drawing_area_pos = self.drawing_area.mapTo(self, QPoint(0, 0))
        return QPoint(pos.x() - drawing_area_pos.x(), pos.y() - drawing_area_pos.y())
    
    def _screen_to_view(self, screen_pos):
        """将屏幕坐标转换为视图坐标"""
        view_x = (screen_pos.x() - self.view_offset.x()) / self.view_scale
        view_y = (screen_pos.y() - self.view_offset.y()) / self.view_scale
        return QPoint(int(view_x), int(view_y))


    def _reset_view(self):
        """重置视图到最佳状态，自适应当前路径"""
        if not self.completed_paths or not hasattr(self, 'drawing_area'):
            # 如果没有路径或绘制区域，重置到默认状态
            self.view_scale = 1.0
            self.view_offset = QPoint(0, 0)
            self.update()
            self.logger.info("视图已重置到默认状态")
            return
        
        # 计算所有路径的边界框
        all_points = []
        for path in self.completed_paths:
            points = path.get('points', [])
            all_points.extend(points)
        
        if not all_points:
            self.view_scale = 1.0
            self.view_offset = QPoint(0, 0)
            self.update()
            return
        
        # 计算边界框
        min_x = min(p[0] for p in all_points)
        max_x = max(p[0] for p in all_points)
        min_y = min(p[1] for p in all_points)
        max_y = max(p[1] for p in all_points)
        
        path_width = max_x - min_x
        path_height = max_y - min_y
        
        # 获取绘制区域的尺寸
        area_width = self.drawing_area.width() - 80  # 增加边距
        area_height = self.drawing_area.height() - 80
        
        if path_width == 0 and path_height == 0:
            # 单点的情况
            self.view_scale = 1.0
            center_x = area_width / 2 - min_x
            center_y = area_height / 2 - min_y
        else:
            # 计算缩放比例
            if path_width > 0 and path_height > 0:
                scale_x = area_width / path_width
                scale_y = area_height / path_height
                # 使用较小的缩放比例，并且限制最大缩放为2倍
                self.view_scale = min(scale_x, scale_y, 2.0) * 0.8  # 再缩小到80%
            else:
                self.view_scale = 1.0
            
            # 计算居中偏移
            path_center_x = (min_x + max_x) / 2
            path_center_y = (min_y + max_y) / 2
            area_center_x = area_width / 2
            area_center_y = area_height / 2
            
            center_x = area_center_x - path_center_x * self.view_scale
            center_y = area_center_y - path_center_y * self.view_scale
        
        self.view_offset = QPoint(int(center_x), int(center_y))
        self.update()
        self.logger.info(f"视图已重置：缩放={self.view_scale:.2f}, 偏移=({self.view_offset.x()}, {self.view_offset.y()})")
        

        
    def _handle_pointer_click(self, screen_pos):
        """处理点击工具的点击事件"""
        # 检查是否点击了现有的点
        clicked_point_index = self._find_point_at_position(screen_pos)
        
        if clicked_point_index >= 0:
            # 解析点索引
            path_index = clicked_point_index // 1000
            point_index = clicked_point_index % 1000
            
            if self.selected_point_index == clicked_point_index:
                # 已经选中的点，开始拖拽
                self.dragging_point = True
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.logger.info(f"开始拖拽点 {clicked_point_index}")
            else:
                # 选中新点
                self.selected_point_index = clicked_point_index
                self.update()  # 重绘以显示选中状态
                self.logger.info(f"选中点 {clicked_point_index}")
        else:
            # 点击空白区域，取消选择并添加新点
            self.selected_point_index = -1
            self._add_new_point(screen_pos)
            self.update()  # 重绘以清除选中状态
            
    def _find_point_at_position(self, screen_pos, tolerance=15):
        """查找指定位置的点，返回点索引，如果没找到返回-1"""
        if not self.completed_paths:
            return -1
            
        # 调整鼠标位置到绘制区域坐标
        adjusted_pos = self._adjust_for_drawing_area(screen_pos)
        
        # 将调整后的坐标转换为视图坐标
        view_pos = self._screen_to_view(adjusted_pos)
        
        # 遍历所有路径的所有点
        for path_index, path in enumerate(self.completed_paths):
            points = path.get('points', [])
            if not points:
                continue
            
            # 检查每个点的位置（在视图坐标系中）
            for point_index, point in enumerate(points):
                # 计算距离（在视图坐标系中）
                distance = ((view_pos.x() - point[0]) ** 2 + (view_pos.y() - point[1]) ** 2) ** 0.5
                if distance <= tolerance:
                    # 返回全局点索引（路径索引 * 1000 + 点索引）
                    return path_index * 1000 + point_index
        return -1
        

    def _add_new_point(self, screen_pos):
        """添加新点"""
        # 调整鼠标位置到绘制区域坐标，然后转换为视图坐标
        adjusted_pos = self._adjust_for_drawing_area(screen_pos)
        view_pos = self._screen_to_view(adjusted_pos)
        
        if not self.completed_paths:
            # 如果没有路径，创建新路径，使用视图坐标
            new_path = {
                'points': [(view_pos.x(), view_pos.y())],  # 使用视图坐标
                'connections': [],  # 单点没有连接
                'color': 'blue',  # 设置颜色属性
                'width': 2  # 设置线宽属性
            }
            self.completed_paths.append(new_path)
            updated_path = new_path
            should_emit = True  # 新路径需要发送信号
        else:
            # 在最后一个路径中添加点
            last_path = self.completed_paths[-1]
            if 'points' not in last_path:
                last_path['points'] = []
            if 'connections' not in last_path:
                last_path['connections'] = []
                
            # 添加新点，使用视图坐标
            new_point_index = len(last_path['points'])
            last_path['points'].append((view_pos.x(), view_pos.y()))
            
            # 添加连接（如果不是第一个点）
            if new_point_index > 0:
                # 连接前一个点到新点
                new_connection = {
                    'from': new_point_index - 1,
                    'to': new_point_index,
                    'type': 'line'  # 添加连接类型
                }
                last_path['connections'].append(new_connection)
            
            # 确保路径具有标准属性
            if 'color' not in last_path:
                last_path['color'] = 'blue'
            if 'width' not in last_path:
                last_path['width'] = 2
            
            updated_path = last_path
            should_emit = False  # 修改现有路径不发送信号，避免替换整个路径
            
        self.save_to_history()
        
        # 只在创建新路径时发送信号
        if should_emit:
            self.pathCompleted.emit(updated_path)
        
        self.update()
        self.logger.info(f"添加新点: 视图坐标({view_pos.x()}, {view_pos.y()}), 发送信号: {should_emit}")
        
    def _update_dragging_point(self, screen_pos):
        """更新拖拽点的位置"""
        if self.selected_point_index < 0:
            return
            
        # 解析全局点索引
        path_index = self.selected_point_index // 1000
        point_index = self.selected_point_index % 1000
        
        if (path_index < len(self.completed_paths) and 
            self.completed_paths[path_index].get('points') and
            point_index < len(self.completed_paths[path_index]['points'])):
            
            # 调整鼠标位置到绘制区域坐标，然后转换为视图坐标
            adjusted_pos = self._adjust_for_drawing_area(screen_pos)
            view_pos = self._screen_to_view(adjusted_pos)
            
            # 更新点位置，使用视图坐标
            self.completed_paths[path_index]['points'][point_index] = (view_pos.x(), view_pos.y())
            self.update()
            
    def _delete_selected_point(self):
        """删除选中的点"""
        if self.selected_point_index < 0:
            return
            
        # 解析全局点索引
        path_index = self.selected_point_index // 1000
        point_index = self.selected_point_index % 1000
        
        if (path_index < len(self.completed_paths) and 
            self.completed_paths[path_index].get('points') and
            point_index < len(self.completed_paths[path_index]['points'])):
            
            path = self.completed_paths[path_index]
            points = path['points']
            connections = path.get('connections', [])
            
            # 删除点
            del points[point_index]
            
            # 如果路径没有点了，删除整个路径
            if not points:
                del self.completed_paths[path_index]
            else:
                # 更新连接关系：找到涉及被删除点的连接，建立新的桥接连接
                new_connections = []
                incoming_points = []  # 指向被删除点的连接的起点
                outgoing_points = []  # 从被删除点出发的连接的终点
                
                # 分析现有连接，收集需要桥接的信息
                for conn in connections:
                    from_idx = conn.get('from', 0)
                    to_idx = conn.get('to', 0)
                    
                    if to_idx == point_index:
                        # 指向被删除点的连接
                        incoming_points.append(from_idx)
                    elif from_idx == point_index:
                        # 从被删除点出发的连接
                        outgoing_points.append(to_idx)
                    else:
                        # 不涉及被删除点的连接，调整索引后保留
                        adjusted_from = from_idx - 1 if from_idx > point_index else from_idx
                        adjusted_to = to_idx - 1 if to_idx > point_index else to_idx
                        new_connections.append({
                            'from': adjusted_from,
                            'to': adjusted_to,
                            'type': conn.get('type', 'line')
                        })
                
                # 建立桥接连接：每个incoming点连接到每个outgoing点
                for incoming in incoming_points:
                    for outgoing in outgoing_points:
                        # 调整索引
                        adjusted_incoming = incoming - 1 if incoming > point_index else incoming
                        adjusted_outgoing = outgoing - 1 if outgoing > point_index else outgoing
                        
                        # 避免自连接
                        if adjusted_incoming != adjusted_outgoing:
                            new_connections.append({
                                'from': adjusted_incoming,
                                'to': adjusted_outgoing,
                                'type': 'line'
                            })
                
                path['connections'] = new_connections
            
            # 清除选择状态
            self.selected_point_index = -1
            
            # 保存到历史记录
            self.save_to_history()
            
            # 更新显示
            self.update()
            
            self.logger.info(f"删除点 {point_index} from path {path_index}")
            
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 先绘制背景
        if hasattr(self, 'drawing_area'):
            # 获取绘制区域的位置和大小
            drawing_area_pos = self.drawing_area.mapTo(self, QPoint(0, 0))
            drawing_rect = self.drawing_area.geometry()
            drawing_rect.moveTopLeft(drawing_area_pos)
            
            # 绘制白色背景和边框
            painter.fillRect(drawing_rect, QColor("white"))
            painter.setPen(QPen(QColor("#ccc"), 1))
            painter.drawRect(drawing_rect.adjusted(0, 0, -1, -1))
            
            # 应用视图变换（考虑绘制区域偏移 + 用户的缩放和平移）
            transform = QTransform()
            transform.translate(drawing_area_pos.x() + self.view_offset.x(), drawing_area_pos.y() + self.view_offset.y())
            transform.scale(self.view_scale, self.view_scale)
            painter.setTransform(transform)
        else:
            # 如果没有drawing_area，使用默认变换
            transform = QTransform()
            transform.translate(self.view_offset.x(), self.view_offset.y())
            transform.scale(self.view_scale, self.view_scale)
            painter.setTransform(transform)
        
        # 绘制已完成的路径（蓝色）
        painter.setPen(QPen(QColor(0, 120, 255), 2))
        for path in self.completed_paths:
            # 统一使用自动缩放绘制，保持显示一致性
            self._draw_formatted_path(painter, path)
        
        # 点击工具模式下不需要特殊标记
        
        # 绘制当前路径（红色）
        if self.current_path:
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            for i in range(len(self.current_path) - 1):
                painter.drawLine(self.current_path[i], self.current_path[i + 1])
        
    def _get_point_position(self, point):
        """获取点的位置，兼容不同的数据格式"""
        if isinstance(point, (list, tuple)) and len(point) >= 2:
            return QPoint(int(point[0]), int(point[1]))
        elif isinstance(point, dict):
            return QPoint(int(point.get('x', 0)), int(point.get('y', 0)))
        else:
            self.logger.warning(f"未知的点格式: {point} (类型: {type(point)})")
        return None

    def _draw_formatted_path(self, painter, path):
        """绘制格式化路径（直接使用点坐标，与点击检测保持一致）"""
        points = path.get('points', [])
        connections = path.get('connections', [])
        
        if not points:
            return
        
        # 直接使用点坐标，转换为QPoint
        def get_point(point):
            return QPoint(int(point[0]), int(point[1]))
        
        # 绘制连接线和方向箭头（如果有连接）
        if connections:
            painter.setPen(QPen(QColor(0, 120, 255), 2))
            for conn in connections:
                from_idx = conn.get('from', 0)
                to_idx = conn.get('to', 0)
                
                if from_idx < len(points) and to_idx < len(points):
                    start_point = get_point(points[from_idx])
                    end_point = get_point(points[to_idx])
                    painter.drawLine(start_point, end_point)
                    
                    # 在线条中间绘制方向箭头
                    self._draw_direction_arrow(painter, start_point, end_point)
        
        # 绘制关键点 - 起点、终点、中间点用不同颜色
        old_pen = painter.pen()
        
        for i, point in enumerate(points):
            point_pos = get_point(point)
            
            # 绘制选中状态的黄色半透明圆环
            global_point_index = -1
            for path_idx, p in enumerate(self.completed_paths):
                if p == path:
                    global_point_index = path_idx * 1000 + i
                    break
            
            if global_point_index >= 0 and global_point_index == self.selected_point_index:
                # 根据点型确定选择圆环的基础大小（视图坐标下的像素）
                if i == 0:
                    # 起点 - 圆环半径比点大4像素
                    base_ring_radius = 10  # 6 + 4
                elif i == len(points) - 1:
                    # 终点 - 圆环半径比点大4像素  
                    if len(points) == 1:
                        base_ring_radius = 10  # 单点情况，与起点相同
                    else:
                        base_ring_radius = 8   # 4 + 4
                else:
                    # 中间点 - 圆环半径比点大4像素
                    base_ring_radius = 6   # 2 + 4
                
                # 根据当前缩放比例调整圆环大小，确保在屏幕上显示一致
                actual_ring_radius = int(base_ring_radius / self.view_scale)
                
                # 绘制选中状态的黄色半透明圆环
                painter.setPen(QPen(QColor(255, 255, 0, 180), max(1, int(3 / self.view_scale))))
                painter.setBrush(QColor(255, 255, 0, 60))  # 半透明黄色
                ring_size = actual_ring_radius * 2
                painter.drawEllipse(point_pos.x() - actual_ring_radius, point_pos.y() - actual_ring_radius, ring_size, ring_size)
            
            if i == 0:
                # 起点 - 绿色，较大
                start_radius = int(6 / self.view_scale)
                painter.setPen(QPen(QColor(0, 200, 0), max(1, int(3 / self.view_scale))))
                painter.setBrush(QColor(0, 200, 0))
                painter.drawEllipse(point_pos.x() - start_radius, point_pos.y() - start_radius, start_radius * 2, start_radius * 2)
            elif i == len(points) - 1:
                # 终点 - 红色
                if len(points) == 1:
                    # 只有一个点时，绘制一个小一点的红色圆点在绿色内部
                    end_radius = int(3 / self.view_scale)
                    painter.setPen(QPen(QColor(255, 0, 0), max(1, int(2 / self.view_scale))))
                    painter.setBrush(QColor(255, 0, 0))
                    painter.drawEllipse(point_pos.x() - end_radius, point_pos.y() - end_radius, end_radius * 2, end_radius * 2)
                else:
                    # 有多个点时，终点稍微小一点
                    end_radius = int(4 / self.view_scale)
                    painter.setPen(QPen(QColor(255, 0, 0), max(1, int(3 / self.view_scale))))
                    painter.setBrush(QColor(255, 0, 0))
                    painter.drawEllipse(point_pos.x() - end_radius, point_pos.y() - end_radius, end_radius * 2, end_radius * 2)
            else:
                # 中间点 - 蓝色，最小
                mid_radius = int(2 / self.view_scale)
                painter.setPen(QPen(QColor(0, 120, 255), max(1, int(2 / self.view_scale))))
                painter.setBrush(QColor(0, 120, 255))
                painter.drawEllipse(point_pos.x() - mid_radius, point_pos.y() - mid_radius, mid_radius * 2, mid_radius * 2)
        
        painter.setPen(old_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)  # 重置画刷
    
    def _draw_direction_arrow(self, painter, start_point, end_point):
        """在线条中间绘制方向箭头"""
        # 计算中点
        mid_x = (start_point.x() + end_point.x()) / 2
        mid_y = (start_point.y() + end_point.y()) / 2
        
        # 计算方向向量
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        
        # 如果线条太短，不画箭头
        length = math.sqrt(dx * dx + dy * dy)
        if length < 20:
            return
        
        # 标准化方向向量
        dx /= length
        dy /= length
        
        # 箭头大小
        arrow_length = 8
        arrow_width = 4
        
        # 计算箭头的三个点
        # 箭头顶点（指向前进方向）
        arrow_tip_x = mid_x + dx * arrow_length / 2
        arrow_tip_y = mid_y + dy * arrow_length / 2
        
        # 箭头两侧的点
        # 垂直向量 (-dy, dx)
        arrow_left_x = mid_x - dx * arrow_length / 2 - dy * arrow_width
        arrow_left_y = mid_y - dy * arrow_length / 2 + dx * arrow_width
        
        arrow_right_x = mid_x - dx * arrow_length / 2 + dy * arrow_width
        arrow_right_y = mid_y - dy * arrow_length / 2 - dx * arrow_width
        
        # 创建箭头多边形
        arrow_polygon = QPolygon([
            QPoint(int(arrow_tip_x), int(arrow_tip_y)),
            QPoint(int(arrow_left_x), int(arrow_left_y)),
            QPoint(int(arrow_right_x), int(arrow_right_y))
        ])
        
        # 绘制箭头
        old_pen = painter.pen()
        old_brush = painter.brush()
        painter.setPen(QPen(QColor(255, 100, 0), 1))  # 橙色箭头
        painter.setBrush(QColor(255, 100, 0))
        painter.drawPolygon(arrow_polygon)
        painter.setPen(old_pen)
        painter.setBrush(old_brush)
    
    def clear_drawing(self):
        """清除绘制内容"""
        self.current_path = []
        self.completed_paths = []
        # 重置历史记录
        self.path_history = []
        self.history_index = -1
        # 重置到默认视图
        self.view_scale = 1.0
        self.view_offset = QPoint(0, 0)
        # 保存初始空状态到历史记录
        self.save_to_history()
        self.update()
        

    def load_path(self, path):
        """加载并显示指定路径（用于编辑现有手势）"""
        if path and path.get('points'):
            # 清除现有内容但不保存空状态到历史记录
            self.current_path = []
            self.completed_paths = []
            
            # 重置历史记录
            self.path_history = []
            self.history_index = -1
            
            # 加载新路径
            self.completed_paths = [path]
            
            # 将加载的路径保存为第一个历史记录
            self.save_to_history()
            
            # 重置视图以适应新路径
            self._reset_view()
            self.update()
        else:
            self.clear_drawing() 