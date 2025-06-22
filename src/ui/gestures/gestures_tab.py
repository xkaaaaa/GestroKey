from qtpy.QtCore import Qt, QTimer, QPoint, Signal, QSize
from qtpy.QtGui import QPainter, QPen, QColor, QFont, QBrush, QIcon
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGroupBox, QMessageBox, QScrollArea, QDialog
)

from core.logger import get_logger
from ui.gestures.gestures import get_gesture_library


def _find_parent_with_refresh(widget):
    """查找具有refresh_list方法的父级容器"""
    parent = widget.parent()
    while parent and not hasattr(parent, 'refresh_list'):
        parent = parent.parent()
    return parent


def _create_card_button(text, tooltip, style_extra="", size=(20, 20), icon_name=None):
    """创建卡片上的小按钮"""
    btn = QPushButton(text)
    btn.setFixedSize(*size)
    btn.setToolTip(tooltip)
    btn.setStyleSheet(f"font-size: 10px; padding: 0px; {style_extra}")
    
    # 设置图标
    if icon_name:
        import os
        assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "assets", "images", "ui"
        )
        icon_path = os.path.join(assets_dir, f"{icon_name}.svg")
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(16, 16))
            btn.setText("")  # 隐藏文本，只显示图标
    
    return btn


def _find_key_by_id(data_dict, target_id):
    """通过ID在数据字典中查找对应的key"""
    for key, data in data_dict.items():
        if data.get('id') == target_id:
            return key
    return None


class ConnectionWidget(QWidget):
    """连线绘制组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connections = []
        self.selected_connection = None
        self.setMinimumHeight(400)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def add_connection(self, action_id, path_id, start_point, end_point):
        """添加连线"""
        self.connections = [conn for conn in self.connections if conn[1] != path_id]
        self.connections.append((action_id, path_id, start_point, end_point))
        self.update()
        
    def remove_connection(self, path_id):
        """移除连线"""
        self.connections = [conn for conn in self.connections if conn[1] != path_id]
        if self.selected_connection is not None:
            if self.selected_connection >= len(self.connections):
                self.selected_connection = None
        self.update()
        
    def clear_connections(self):
        """清空所有连线"""
        self.connections = []
        self.selected_connection = None
        self.update()
        
    def mousePressEvent(self, event):
        """鼠标点击事件 - 选择连线"""
        if event.button() == Qt.MouseButton.LeftButton:
            click_pos = event.pos()
            selected_index = self._get_connection_at_point(click_pos)
            
            if selected_index is not None:
                self.selected_connection = selected_index
                self.setFocus()
                self.update()
            else:
                self.selected_connection = None
                self.update()
                
        super().mousePressEvent(event)
        
    def keyPressEvent(self, event):
        """键盘事件 - 删除选中的连线"""
        if event.key() == Qt.Key.Key_Delete and self.selected_connection is not None:
            if 0 <= self.selected_connection < len(self.connections):
                action_id, path_id, _, _ = self.connections[self.selected_connection]
                
                parent_tab = self.parent()
                while parent_tab and not isinstance(parent_tab, GesturesPage):
                    parent_tab = parent_tab.parent()
                    
                if parent_tab:
                    parent_tab._delete_mapping_by_path_id(path_id)
                    
        super().keyPressEvent(event)
        
    def _get_connection_at_point(self, point):
        """获取指定点位置的连线索引"""
        for i, (action_id, path_id, start_point, end_point) in enumerate(self.connections):
            if self._point_to_line_distance(point, start_point, end_point) < 10:
                return i
        return None
        
    def _point_to_line_distance(self, point, line_start, line_end):
        """计算点到线段的距离"""
        dx = line_end.x() - line_start.x()
        dy = line_end.y() - line_start.y()
        
        if dx == 0 and dy == 0:
            return ((point.x() - line_start.x()) ** 2 + (point.y() - line_start.y()) ** 2) ** 0.5
            
        t = ((point.x() - line_start.x()) * dx + (point.y() - line_start.y()) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        
        closest_x = line_start.x() + t * dx
        closest_y = line_start.y() + t * dy
        
        return ((point.x() - closest_x) ** 2 + (point.y() - closest_y) ** 2) ** 0.5
        
    def paintEvent(self, event):
        """绘制连线"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for i, (action_id, path_id, start_point, end_point) in enumerate(self.connections):
            if i == self.selected_connection:
                pen = QPen(QColor(220, 53, 69), 3)
            else:
                pen = QPen(QColor(0, 120, 215), 2)
                
            painter.setPen(pen)
            painter.drawLine(start_point, end_point)
            
            self._draw_arrow(painter, start_point, end_point, i == self.selected_connection)
            
    def _draw_arrow(self, painter, start_point, end_point, is_selected=False):
        """绘制箭头"""
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        length = (dx*dx + dy*dy) ** 0.5
        
        if length == 0:
            return
            
        ux = dx / length
        uy = dy / length
        
        arrow_length = 10
        arrow_width = 5
        
        tip_x = end_point.x()
        tip_y = end_point.y()
        
        base1_x = tip_x - arrow_length * ux + arrow_width * uy
        base1_y = tip_y - arrow_length * uy - arrow_width * ux
        base2_x = tip_x - arrow_length * ux - arrow_width * uy
        base2_y = tip_y - arrow_length * uy + arrow_width * ux
        
        color = QColor(220, 53, 69) if is_selected else QColor(0, 120, 215)
        painter.setBrush(QBrush(color))
        points = [QPoint(int(tip_x), int(tip_y)), 
                 QPoint(int(base1_x), int(base1_y)), 
                 QPoint(int(base2_x), int(base2_y))]
        painter.drawPolygon(points)


class ActionCardWidget(QWidget):
    """操作卡片组件"""
    action_clicked = Signal(int, QPoint)
    
    def __init__(self, action_id, action_name, action_value, parent=None):
        super().__init__(parent)
        self.action_id = action_id
        self.action_name = action_name
        self.action_value = action_value
        self.is_selected = False
        self.mapped_paths_count = 0
        
        self.setFixedSize(200, 120)
        self.setStyleSheet("""
            ActionCardWidget {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            ActionCardWidget:hover {
                border-color: #0078d4;
                background-color: #f3f9ff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # 顶部布局：标题和按钮
        top_layout = QHBoxLayout()
        
        name_label = QLabel(action_name)
        name_label.setFont(QFont("", 10, QFont.Weight.Bold))
        name_label.setWordWrap(True)
        top_layout.addWidget(name_label)
        
        top_layout.addStretch()
        
        # 右上角按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(3)
        
        self.btn_edit = _create_card_button("✏", "编辑操作", icon_name="edit")
        self.btn_edit.clicked.connect(lambda: self._edit_action())
        buttons_layout.addWidget(self.btn_edit)
        
        self.btn_delete = _create_card_button("✕", "删除操作", "color: red;", icon_name="delete")
        self.btn_delete.clicked.connect(lambda: self._delete_action())
        buttons_layout.addWidget(self.btn_delete)
        
        top_layout.addLayout(buttons_layout)
        layout.addLayout(top_layout)
        
        display_value = action_value if len(action_value) <= 30 else action_value[:30] + "..."
        value_label = QLabel(f"内容: {display_value}")
        value_label.setFont(QFont("", 9))
        value_label.setStyleSheet("color: #666;")
        value_label.setWordWrap(True)
        value_label.setToolTip(action_value)
        layout.addWidget(value_label)
        
        self.status_label = QLabel("可连接")
        self.status_label.setFont(QFont("", 9))
        self.status_label.setStyleSheet("color: #999;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            global_pos = self.mapToGlobal(event.pos())
            self.action_clicked.emit(self.action_id, global_pos)
        super().mousePressEvent(event)
        
    def set_selected(self, is_selected):
        """设置选中状态"""
        self.is_selected = is_selected
        
        if is_selected:
            self.setStyleSheet("""
                ActionCardWidget {
                    border: 3px solid #0078d4;
                    border-radius: 8px;
                    background-color: #e6f3ff;
                }
                ActionCardWidget:hover {
                    border-color: #106ebe;
                    background-color: #d1e9ff;
                }
            """)
            self.status_label.setText("已选中 - 请选择路径")
            self.status_label.setStyleSheet("color: #0078d4; font-weight: bold;")
        else:
            self.setStyleSheet("""
                ActionCardWidget {
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    background-color: white;
                }
                ActionCardWidget:hover {
                    border-color: #0078d4;
                    background-color: #f3f9ff;
                }
            """)
            if self.mapped_paths_count > 0:
                self.status_label.setText(f"已连接 {self.mapped_paths_count} 个路径")
                self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            else:
                self.status_label.setText("可连接")
                self.status_label.setStyleSheet("color: #999;")
                
    def set_mapped_count(self, count):
        """设置映射的路径数量"""
        self.mapped_paths_count = count
        if not self.is_selected:
            if count > 0:
                self.status_label.setText(f"已连接 {count} 个路径")
                self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            else:
                self.status_label.setText("可连接")
                self.status_label.setStyleSheet("color: #999;")
                
    def _edit_action(self):
        """编辑操作"""
        from ui.gestures.gesture_dialogs import ExecuteActionEditDialog
        
        gesture_library = get_gesture_library()
        action_key = _find_key_by_id(gesture_library.execute_actions, self.action_id)
        
        if action_key:
            dialog = ExecuteActionEditDialog(action_key, self.parent())
            if dialog.exec() == QDialog.DialogCode.Accepted:
                parent = _find_parent_with_refresh(self)
                if parent:
                    parent.refresh_list()
                    
    def _delete_action(self):
        """删除操作"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除操作 '{self.action_name}' 吗？\\n\\n注意：删除操作可能会影响使用此操作的手势映射。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                gesture_library = get_gesture_library()
                action_key = _find_key_by_id(gesture_library.execute_actions, self.action_id)
                
                if action_key:
                    del gesture_library.execute_actions[action_key]
                    gesture_library.mark_data_changed("execute_actions")
                    
                    parent = _find_parent_with_refresh(self)
                    if parent:
                        parent.refresh_list()
                        
                    QMessageBox.information(self, "成功", "操作已删除")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除操作失败: {str(e)}")


class PathCardWidget(QWidget):
    """路径卡片组件"""
    path_clicked = Signal(int, QPoint)
    
    def __init__(self, path_id, path_name, parent=None):
        super().__init__(parent)
        self.path_id = path_id
        self.path_name = path_name
        self.is_mapped = False
        self.mapped_action_name = ""
        
        self.setFixedSize(200, 120)
        self.setStyleSheet("""
            PathCardWidget {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            PathCardWidget:hover {
                border-color: #0078d4;
                background-color: #f3f9ff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # 顶部布局：标题和按钮
        top_layout = QHBoxLayout()
        
        name_label = QLabel(path_name)
        name_label.setFont(QFont("", 10, QFont.Weight.Bold))
        name_label.setWordWrap(True)
        top_layout.addWidget(name_label)
        
        top_layout.addStretch()
        
        # 右上角按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(3)
        
        self.btn_edit = _create_card_button("✏", "编辑路径", icon_name="edit")
        self.btn_edit.clicked.connect(lambda: self._edit_path())
        buttons_layout.addWidget(self.btn_edit)
        
        self.btn_delete = _create_card_button("✕", "删除路径", "color: red;", icon_name="delete")
        self.btn_delete.clicked.connect(lambda: self._delete_path())
        buttons_layout.addWidget(self.btn_delete)
        
        top_layout.addLayout(buttons_layout)
        layout.addLayout(top_layout)
        
        self.status_label = QLabel("未映射")
        self.status_label.setFont(QFont("", 9))
        self.status_label.setStyleSheet("color: #999;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            global_pos = self.mapToGlobal(event.pos())
            self.path_clicked.emit(self.path_id, global_pos)
        super().mousePressEvent(event)
        
    def set_mapped(self, is_mapped, action_name=""):
        """设置映射状态"""
        self.is_mapped = is_mapped
        self.mapped_action_name = action_name
        
        if is_mapped:
            self.status_label.setText(f"→ {action_name}")
            self.status_label.setStyleSheet("color: #0078d4; font-weight: bold;")
            self.setStyleSheet("""
                PathCardWidget {
                    border: 2px solid #0078d4;
                    border-radius: 8px;
                    background-color: #f3f9ff;
                }
                PathCardWidget:hover {
                    border-color: #106ebe;
                    background-color: #e6f3ff;
                }
            """)
        else:
            self.status_label.setText("未映射")
            self.status_label.setStyleSheet("color: #999;")
            self.setStyleSheet("""
                PathCardWidget {
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    background-color: white;
                }
                PathCardWidget:hover {
                    border-color: #0078d4;
                    background-color: #f3f9ff;
                }
            """)
            
    def _edit_path(self):
        """编辑路径"""
        from ui.gestures.gesture_dialogs import TriggerPathEditDialog
        
        gesture_library = get_gesture_library()
        path_key = _find_key_by_id(gesture_library.trigger_paths, self.path_id)
        
        if path_key:
            dialog = TriggerPathEditDialog(path_key, self.parent())
            if dialog.exec() == QDialog.DialogCode.Accepted:
                parent = _find_parent_with_refresh(self)
                if parent:
                    parent.refresh_list()
                    
    def _delete_path(self):
        """删除路径"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除路径 '{self.path_name}' 吗？\\n\\n注意：删除路径可能会影响使用此路径的手势映射。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                gesture_library = get_gesture_library()
                path_key = _find_key_by_id(gesture_library.trigger_paths, self.path_id)
                
                if path_key:
                    del gesture_library.trigger_paths[path_key]
                    gesture_library.mark_data_changed("trigger_paths")
                    
                    parent = _find_parent_with_refresh(self)
                    if parent:
                        parent.refresh_list()
                        
                    QMessageBox.information(self, "成功", "路径已删除")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除路径失败: {str(e)}")


class ActionCardsWidget(QWidget):
    """操作卡片容器组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.action_cards = {}
        
        self.cards_layout = QVBoxLayout(self)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        
        # 添加弹性空间，用于在底部放置添加按钮
        self.cards_layout.addStretch()
        
        # 添加"添加操作"按钮
        self.btn_add = QPushButton("添加操作")
        self.btn_add.setMinimumSize(180, 40)
        self.btn_add.setStyleSheet("""
            QPushButton {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f9f9f9;
                color: #666;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #0078d4;
                background-color: #f3f9ff;
                color: #0078d4;
            }
        """)
        # 设置添加图标
        import os
        assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "assets", "images", "ui"
        )
        add_icon_path = os.path.join(assets_dir, "add.svg")
        if os.path.exists(add_icon_path):
            self.btn_add.setIcon(QIcon(add_icon_path))
            self.btn_add.setIconSize(QSize(20, 20))
        
        self.btn_add.clicked.connect(self._add_new_action)
        self.cards_layout.addWidget(self.btn_add)
        
    def _add_new_action(self):
        """添加新操作"""
        from ui.gestures.gesture_dialogs import ExecuteActionEditDialog
        
        dialog = ExecuteActionEditDialog(None, self.parent())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            parent = _find_parent_with_refresh(self)
            if parent:
                parent.refresh_list()
        
    def add_action_card(self, action_id, action_name, action_value):
        """添加操作卡片"""
        card = ActionCardWidget(action_id, action_name, action_value)
        self.action_cards[action_id] = card
        # 插入到添加按钮之前（倒数第二个位置）
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        return card
        
    def remove_action_card(self, action_id):
        """移除操作卡片"""
        if action_id in self.action_cards:
            card = self.action_cards[action_id]
            self.cards_layout.removeWidget(card)
            card.deleteLater()
            del self.action_cards[action_id]
            
    def clear_action_cards(self):
        """清空所有操作卡片"""
        for card in self.action_cards.values():
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        self.action_cards.clear()
        
    def get_action_card(self, action_id):
        """获取操作卡片"""
        return self.action_cards.get(action_id)
        
    def clear_all_selections(self):
        """清除所有选中状态"""
        for card in self.action_cards.values():
            card.set_selected(False)


class PathCardsWidget(QWidget):
    """路径卡片容器组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.path_cards = {}
        
        self.cards_layout = QVBoxLayout(self)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        
        # 添加弹性空间，用于在底部放置添加按钮
        self.cards_layout.addStretch()
        
        # 添加"添加路径"按钮
        self.btn_add = QPushButton("添加路径")
        self.btn_add.setMinimumSize(180, 40)
        self.btn_add.setStyleSheet("""
            QPushButton {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f9f9f9;
                color: #666;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #0078d4;
                background-color: #f3f9ff;
                color: #0078d4;
            }
        """)
        # 设置添加图标
        import os
        assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "assets", "images", "ui"
        )
        add_icon_path = os.path.join(assets_dir, "add.svg")
        if os.path.exists(add_icon_path):
            self.btn_add.setIcon(QIcon(add_icon_path))
            self.btn_add.setIconSize(QSize(20, 20))
        
        self.btn_add.clicked.connect(self._add_new_path)
        self.cards_layout.addWidget(self.btn_add)
        
    def _add_new_path(self):
        """添加新路径"""
        from ui.gestures.gesture_dialogs import TriggerPathEditDialog
        
        dialog = TriggerPathEditDialog(None, self.parent())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            parent = _find_parent_with_refresh(self)
            if parent:
                parent.refresh_list()
        
    def add_path_card(self, path_id, path_name):
        """添加路径卡片"""
        card = PathCardWidget(path_id, path_name)
        self.path_cards[path_id] = card
        # 插入到添加按钮之前（倒数第二个位置）
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        return card
        
    def remove_path_card(self, path_id):
        """移除路径卡片"""
        if path_id in self.path_cards:
            card = self.path_cards[path_id]
            self.cards_layout.removeWidget(card)
            card.deleteLater()
            del self.path_cards[path_id]
            
    def clear_path_cards(self):
        """清空所有路径卡片"""
        for card in self.path_cards.values():
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        self.path_cards.clear()
        
    def get_path_card(self, path_id):
        """获取路径卡片"""
        return self.path_cards.get(path_id)


class GesturesPage(QWidget):
    """手势管理主页面 - 连线式映射界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("GesturesPage")
        self.gesture_library = get_gesture_library()
        
        self.selected_action_id = None
        
        self.initUI()
        self._load_data()
        
        # 定时检查手势库变更状态
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_library_changes)
        self.check_timer.start(1000)  # 每秒检查一次
        
        self.last_checked_timestamp = 0
        
    def initUI(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("手势管理")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 创建滚动区域用于核心内容
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 滚动区域内容
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
                
        # 核心内容布局
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # 左侧操作面板
        left_panel = self._create_actions_panel()
        content_layout.addWidget(left_panel)
        
        # 中间连线面板
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        
        connection_title = QLabel("映射连线")
        connection_title.setFont(QFont("", 12, QFont.Weight.Bold))
        connection_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        connection_title.setStyleSheet("color: #666; margin: 10px 0;")
        middle_layout.addWidget(connection_title)
        
        self.connection_widget = ConnectionWidget()
        middle_layout.addWidget(self.connection_widget, 1)
        
        content_layout.addWidget(middle_panel, 1)
        
        # 右侧路径面板
        right_panel = self._create_paths_panel()
        content_layout.addWidget(right_panel)
        
        scroll_layout.addLayout(content_layout, 1)
        
        self.scroll_area.setWidget(scroll_content)
        layout.addWidget(self.scroll_area)
        
        # 底部统一操作按钮 - 与设置页面保持完全一致
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        # 重置为默认按钮
        self.btn_reset = QPushButton("重置为默认")
        self.btn_reset.setMinimumSize(120, 35)
        self.btn_reset.clicked.connect(self._reset_to_default)
        # 设置重置图标
        import os
        assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "assets", "images", "ui"
        )
        reset_icon_path = os.path.join(assets_dir, "reset.svg")
        if os.path.exists(reset_icon_path):
            self.btn_reset.setIcon(QIcon(reset_icon_path))
            self.btn_reset.setIconSize(QSize(18, 18))
        bottom_layout.addWidget(self.btn_reset)
        
        bottom_layout.addStretch()
        
        # 放弃修改按钮
        self.btn_discard = QPushButton("放弃修改")
        self.btn_discard.setMinimumSize(100, 35)
        self.btn_discard.clicked.connect(self._discard_changes)
        self.btn_discard.setEnabled(False)
        # 设置取消图标
        cancel_icon_path = os.path.join(assets_dir, "cancel.svg")
        if os.path.exists(cancel_icon_path):
            self.btn_discard.setIcon(QIcon(cancel_icon_path))
            self.btn_discard.setIconSize(QSize(18, 18))
        bottom_layout.addWidget(self.btn_discard)
        
        # 保存设置按钮
        self.btn_save_library = QPushButton("保存设置")
        self.btn_save_library.setMinimumSize(100, 35)
        self.btn_save_library.clicked.connect(self._save_gesture_library)
        self.btn_save_library.setEnabled(False)
        # 设置保存图标
        save_icon_path = os.path.join(assets_dir, "save.svg")
        if os.path.exists(save_icon_path):
            self.btn_save_library.setIcon(QIcon(save_icon_path))
            self.btn_save_library.setIconSize(QSize(18, 18))
        bottom_layout.addWidget(self.btn_save_library)
        
        layout.addLayout(bottom_layout)
        
    def _create_actions_panel(self):
        """创建操作卡片面板"""
        panel = QGroupBox("执行操作")
        panel.setMaximumWidth(250)
        panel.setMinimumWidth(250)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 10, 5, 10)
        
        self.action_cards_widget = ActionCardsWidget()
        layout.addWidget(self.action_cards_widget)
        
        layout.addStretch()
        
        return panel
        
    def _create_paths_panel(self):
        """创建路径卡片面板"""
        panel = QGroupBox("触发路径")
        panel.setMaximumWidth(250)
        panel.setMinimumWidth(250)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 10, 5, 10)
        
        self.path_cards_widget = PathCardsWidget()
        layout.addWidget(self.path_cards_widget)
        
        layout.addStretch()
        
        return panel
        
    def _load_data(self):
        """加载数据"""
        self._load_actions()
        self._load_paths()
        self._load_existing_mappings()
        
    def _load_actions(self):
        """加载操作卡片"""
        self.action_cards_widget.clear_action_cards()
        
        execute_actions = self.gesture_library.execute_actions
        sorted_actions = sorted(execute_actions.items(), key=lambda x: x[1].get('id', 0))
        
        for action_key, action_data in sorted_actions:
            action_id = action_data.get('id')
            action_name = action_data.get('name', f'操作{action_id}')
            action_value = action_data.get('value', '')
            
            card = self.action_cards_widget.add_action_card(action_id, action_name, action_value)
            card.action_clicked.connect(self._on_action_clicked)
            
        self.logger.debug(f"已加载 {len(execute_actions)} 个执行操作")
        
    def _load_paths(self):
        """加载路径卡片"""
        self.path_cards_widget.clear_path_cards()
        
        trigger_paths = self.gesture_library.trigger_paths
        sorted_paths = sorted(trigger_paths.items(), key=lambda x: x[1].get('id', 0))
        
        for path_key, path_data in sorted_paths:
            path_id = path_data.get('id')
            path_name = path_data.get('name', f'路径{path_id}')
            
            card = self.path_cards_widget.add_path_card(path_id, path_name)
            card.path_clicked.connect(self._on_path_clicked)
            
        self.logger.debug(f"已加载 {len(trigger_paths)} 个触发路径")
        
    def _load_existing_mappings(self):
        """加载现有映射"""
        self.connection_widget.clear_connections()
        
        action_path_counts = {}
        
        gesture_mappings = self.gesture_library.gesture_mappings
        
        for mapping_key, mapping_data in gesture_mappings.items():
            trigger_path_id = mapping_data.get('trigger_path_id')
            execute_action_id = mapping_data.get('execute_action_id')
            
            if trigger_path_id and execute_action_id:
                action_path_counts[execute_action_id] = action_path_counts.get(execute_action_id, 0) + 1
                
                path_card = self.path_cards_widget.get_path_card(trigger_path_id)
                if path_card:
                    action_name = self._get_action_name_by_id(execute_action_id)
                    path_card.set_mapped(True, action_name)
                    
        for action_id, count in action_path_counts.items():
            action_card = self.action_cards_widget.get_action_card(action_id)
            if action_card:
                action_card.set_mapped_count(count)
                
        QTimer.singleShot(100, lambda: self._update_connections())
                
        self.logger.debug(f"已加载 {len(gesture_mappings)} 个手势映射")
        
    def _get_action_name_by_id(self, action_id):
        """根据ID获取操作名称"""
        action_key = _find_key_by_id(self.gesture_library.execute_actions, action_id)
        if action_key:
            action_data = self.gesture_library.execute_actions[action_key]
            return action_data.get('name', f'操作{action_id}')
        return f'操作{action_id}(未找到)'
        
    def _on_action_clicked(self, action_id, global_pos):
        """操作被点击"""
        self.action_cards_widget.clear_all_selections()
        
        self.selected_action_id = action_id
        action_card = self.action_cards_widget.get_action_card(action_id)
        if action_card:
            action_card.set_selected(True)
        
        self.logger.debug(f"选中操作: {action_id}")
        
    def _on_path_clicked(self, path_id, global_pos):
        """路径被点击"""
        if self.selected_action_id is None:
            QMessageBox.information(self, "提示", "请先选择一个执行操作")
            return
            
        self._create_mapping(self.selected_action_id, path_id)
        
        self.selected_action_id = None
        self.action_cards_widget.clear_all_selections()
        
    def _create_mapping(self, action_id, path_id):
        """创建映射"""
        try:
            existing_ids = [data.get('id', 0) for data in self.gesture_library.gesture_mappings.values()]
            new_id = max(existing_ids, default=0) + 1
            
            old_mapping_keys = []
            for mapping_key, mapping_data in self.gesture_library.gesture_mappings.items():
                if mapping_data.get('trigger_path_id') == path_id:
                    old_mapping_keys.append(mapping_key)
                    
            for old_key in old_mapping_keys:
                del self.gesture_library.gesture_mappings[old_key]
            
            mapping_key = f"mapping_{new_id}"
            action_name = self._get_action_name_by_id(action_id)
            path_name = self._get_path_name_by_id(path_id)
            
            self.gesture_library.gesture_mappings[mapping_key] = {
                'id': new_id,
                'name': f"{path_name} → {action_name}",
                'trigger_path_id': path_id,
                'execute_action_id': action_id
            }
            
            self.gesture_library.mark_data_changed("gesture_mappings")
            
            path_card = self.path_cards_widget.get_path_card(path_id)
            if path_card:
                path_card.set_mapped(True, action_name)
                
            self._update_action_mapped_counts()
                
            self._update_connections()
            
            self.logger.info(f"创建映射: 操作{action_id} → 路径{path_id}")
            
        except Exception as e:
            self.logger.error(f"创建映射时出错: {e}")
            QMessageBox.critical(self, "错误", f"创建映射失败: {str(e)}")
            
    def _get_path_name_by_id(self, path_id):
        """根据ID获取路径名称"""
        path_key = _find_key_by_id(self.gesture_library.trigger_paths, path_id)
        if path_key:
            path_data = self.gesture_library.trigger_paths[path_key]
            return path_data.get('name', f'路径{path_id}')
        return f'路径{path_id}(未找到)'
        
    def _update_action_mapped_counts(self):
        """更新操作卡片的映射数量"""
        action_path_counts = {}
        
        gesture_mappings = self.gesture_library.gesture_mappings
        for mapping_data in gesture_mappings.values():
            execute_action_id = mapping_data.get('execute_action_id')
            if execute_action_id:
                action_path_counts[execute_action_id] = action_path_counts.get(execute_action_id, 0) + 1
        
        for action_id, card in self.action_cards_widget.action_cards.items():
            count = action_path_counts.get(action_id, 0)
            card.set_mapped_count(count)
        
    def _update_connections(self):
        """更新连线显示"""
        self.connection_widget.clear_connections()
        
        gesture_mappings = self.gesture_library.gesture_mappings
        
        for mapping_data in gesture_mappings.values():
            trigger_path_id = mapping_data.get('trigger_path_id')
            execute_action_id = mapping_data.get('execute_action_id')
            
            if trigger_path_id and execute_action_id:
                action_card = self.action_cards_widget.get_action_card(execute_action_id)
                path_card = self.path_cards_widget.get_path_card(trigger_path_id)
                
                if action_card and path_card:
                    action_global = action_card.mapToGlobal(action_card.rect().center())
                    action_local = self.connection_widget.mapFromGlobal(action_global)
                    
                    path_global = path_card.mapToGlobal(path_card.rect().center())
                    path_local = self.connection_widget.mapFromGlobal(path_global)
                    
                    self.connection_widget.add_connection(
                        execute_action_id, trigger_path_id, action_local, path_local
                    )
                    
    def _save_gesture_library(self):
        """保存手势库"""
        try:
            success = self.gesture_library.save()
            if success:
                QMessageBox.information(self, "成功", "设置已保存")
                self.logger.info("手势库已保存")
            else:
                QMessageBox.critical(self, "错误", "保存设置失败")
                    
        except Exception as e:
            self.logger.error(f"保存手势库时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
            
    def _reset_to_default(self):
        """重置为默认手势库"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置为默认手势库吗？这将丢失所有自定义的手势设置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.gesture_library.reset_to_default()
                if success:
                    QMessageBox.information(self, "成功", "已重置为默认手势库")
                    self.logger.info("手势库已重置为默认")
                else:
                    QMessageBox.critical(self, "错误", "重置手势库失败")
                    
            except Exception as e:
                self.logger.error(f"重置手势库时出错: {e}")
                QMessageBox.critical(self, "错误", f"重置手势库失败: {str(e)}")
                
    def _discard_changes(self):
        """放弃修改"""
        reply = QMessageBox.question(
            self, "确认放弃", 
            "确定要放弃所有修改吗？这将丢失所有未保存的更改。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 重新加载手势库数据，放弃内存中的修改
                self.gesture_library.load()
                QMessageBox.information(self, "成功", "所有未保存的更改已放弃")
                self.logger.info("已放弃所有修改")
            except Exception as e:
                self.logger.error(f"放弃修改时出错: {e}")
                QMessageBox.critical(self, "错误", f"放弃修改失败: {str(e)}")
            
    def _delete_mapping_by_path_id(self, path_id):
        """根据路径ID删除映射"""
        try:
            mapping_keys_to_delete = []
            for mapping_key, mapping_data in self.gesture_library.gesture_mappings.items():
                if mapping_data.get('trigger_path_id') == path_id:
                    mapping_keys_to_delete.append(mapping_key)
                    
            for mapping_key in mapping_keys_to_delete:
                del self.gesture_library.gesture_mappings[mapping_key]
                
            if mapping_keys_to_delete:
                self.gesture_library.mark_data_changed("gesture_mappings")
                
                path_card = self.path_cards_widget.get_path_card(path_id)
                if path_card:
                    path_card.set_mapped(False)
                    
                self._update_action_mapped_counts()
                    
                self.connection_widget.selected_connection = None
                self._update_connections()
                
                self.logger.info(f"已删除路径{path_id}的映射")
            
        except Exception as e:
            self.logger.error(f"删除映射时出错: {e}")
        
    def _check_library_changes(self):
        """检查手势库是否有变更"""
        has_changes = self.gesture_library.has_changes()
        self.btn_save_library.setEnabled(has_changes)
        self.btn_discard.setEnabled(has_changes)
        
        change_type, change_timestamp = self.gesture_library.get_last_change_info()
        if change_type and change_timestamp > self.last_checked_timestamp:
            self.last_checked_timestamp = change_timestamp
            self.logger.debug(f"检测到数据变更: {change_type}, 时间戳: {change_timestamp}")
            # 自动刷新页面显示
            self.refresh_list()
            
    def refresh_list(self):
        """刷新列表"""
        self._load_data()
        
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        QTimer.singleShot(50, self._update_connections)