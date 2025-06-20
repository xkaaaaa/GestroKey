from qtpy.QtCore import Qt, QTimer, QPoint, QRect, QSize, Signal
from qtpy.QtGui import QPainter, QPen, QColor, QFont, QBrush
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QGroupBox, QMessageBox, QScrollArea, QFrame
)

from core.logger import get_logger
from ui.gestures.gestures import get_gesture_library


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
                while parent_tab and not isinstance(parent_tab, GestureMappingsTab):
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
        
        name_label = QLabel(action_name)
        name_label.setFont(QFont("", 10, QFont.Weight.Bold))
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
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


class PathCardWidget(QWidget):
    """路径卡片组件"""
    path_clicked = Signal(int, QPoint)
    
    def __init__(self, path_id, path_name, path_directions, parent=None):
        super().__init__(parent)
        self.path_id = path_id
        self.path_name = path_name
        self.path_directions = path_directions
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
        
        name_label = QLabel(path_name)
        name_label.setFont(QFont("", 10, QFont.Weight.Bold))
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
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


class ActionCardsWidget(QWidget):
    """操作卡片容器组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.action_cards = {}
        
        self.cards_layout = QVBoxLayout(self)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        
    def add_action_card(self, action_id, action_name, action_value):
        """添加操作卡片"""
        card = ActionCardWidget(action_id, action_name, action_value)
        self.action_cards[action_id] = card
        self.cards_layout.addWidget(card)
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
        
    def add_path_card(self, path_id, path_name, path_directions):
        """添加路径卡片"""
        card = PathCardWidget(path_id, path_name, path_directions)
        self.path_cards[path_id] = card
        self.cards_layout.addWidget(card)
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


class GestureMappingsTab(QWidget):
    """手势映射管理选项卡 - 连线式映射界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("GestureMappingsTab")
        self.gesture_library = get_gesture_library()
        
        self.selected_action_id = None
        
        self.initUI()
        self._load_data()
        
    def initUI(self):
        """初始化用户界面"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        title_layout = QVBoxLayout()
        title = QLabel("手势映射")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        title_layout.addWidget(title)
        
        instruction = QLabel("点击左侧操作卡片，然后点击右侧路径卡片进行映射。一个路径只能映射一个操作。")
        instruction.setStyleSheet("color: #666; margin-bottom: 10px;")
        instruction.setWordWrap(True)
        title_layout.addWidget(instruction)
        
        scroll_layout.addLayout(title_layout)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        left_panel = self._create_actions_panel()
        content_layout.addWidget(left_panel)
        
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
        
        right_panel = self._create_paths_panel()
        content_layout.addWidget(right_panel)
        
        scroll_layout.addLayout(content_layout, 1)
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        self.btn_clear_all = QPushButton("清空所有映射")
        self.btn_clear_all.setMinimumSize(120, 35)
        self.btn_clear_all.clicked.connect(self._clear_all_mappings)
        button_layout.addWidget(self.btn_clear_all)
        
        button_layout.addStretch()
        
        scroll_layout.addLayout(button_layout)
        
        self.scroll_area.setWidget(scroll_content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area)
        
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
            directions = path_data.get('directions', [])
            directions_str = " → ".join(directions) if directions else "无方向"
            
            card = self.path_cards_widget.add_path_card(path_id, path_name, directions_str)
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
        for action_data in self.gesture_library.execute_actions.values():
            if action_data.get('id') == action_id:
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
        for path_data in self.gesture_library.trigger_paths.values():
            if path_data.get('id') == path_id:
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
                    
    def _clear_all_mappings(self):
        """清空所有映射"""
        reply = QMessageBox.question(
            self, "确认清空", 
            "确定要清空所有手势映射吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.gesture_library.gesture_mappings.clear()
            
            for path_card in self.path_cards_widget.path_cards.values():
                path_card.set_mapped(False)
                
            for action_card in self.action_cards_widget.action_cards.values():
                action_card.set_mapped_count(0)
                
            self.connection_widget.clear_connections()
            
            self.logger.info("已清空所有手势映射")
            
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
                path_card = self.path_cards_widget.get_path_card(path_id)
                if path_card:
                    path_card.set_mapped(False)
                    
                self._update_action_mapped_counts()
                    
                self.connection_widget.selected_connection = None
                self._update_connections()
                
                self.logger.info(f"已删除路径{path_id}的映射")
            
        except Exception as e:
            self.logger.error(f"删除映射时出错: {e}")
            
    def refresh_list(self):
        """刷新列表"""
        self._load_data()
        
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        QTimer.singleShot(50, self._update_connections)