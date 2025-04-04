import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QApplication, QLineEdit, QComboBox,
                            QScrollArea, QSizePolicy, QSpacerItem,
                            QGroupBox, QMessageBox, QPushButton,
                            QFrame, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

try:
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library
    from ui.components.button import AnimatedButton
    from ui.components.card import CardWidget
except ImportError:
    sys.path.append('../../')
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library
    from ui.components.button import AnimatedButton
    from ui.components.card import CardWidget

class GestureContentWidget(QWidget):
    """自定义的手势内容显示组件，专门用于解决刷新问题"""
    
    def __init__(self, direction="", action_type="", action_value="", parent=None):
        super().__init__(parent)
        self.setObjectName("GestureContentWidget")
        
        # 创建布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        
        # 方向标签
        self.direction_label = QLabel(f"方向: {direction}")
        self.direction_label.setWordWrap(True)
        self.layout.addWidget(self.direction_label)
        
        # 动作标签
        self.action_label = QLabel(f"动作: {action_type} - {action_value}")
        self.action_label.setWordWrap(True)
        self.layout.addWidget(self.action_label)
        
        self.setLayout(self.layout)
        
        # 设置大小策略，允许水平拉伸
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    
    def updateContent(self, direction="", action_type="", action_value=""):
        """更新内容"""
        self.direction_label.setText(f"方向: {direction}")
        self.action_label.setText(f"动作: {action_type} - {action_value}")
        
        # 强制刷新
        self.direction_label.repaint()
        self.action_label.repaint()
        self.repaint()
        return True

class GesturesTab(QWidget):
    """手势管理选项卡，提供手势库管理功能"""
    
    # 定义方向选项
    DIRECTIONS = [
        "上", "下", "左", "右", 
        "上-下", "下-上", "左-右", "右-左",
        "上-左", "上-右", "下-左", "下-右",
        "左-上", "左-下", "右-上", "右-下"
    ]
    
    # 定义动作类型
    ACTION_TYPES = ["shortcut"]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("GesturesTab")
        self.gestures = get_gesture_library()
        self.gesture_cards = {}  # 存储手势卡片的引用
        self.current_selected_card = None  # 当前选中的卡片
        
        self.initUI()
        self.logger.debug("手势管理选项卡初始化完成")
    
    def initUI(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QHBoxLayout(self)  # 使用水平布局，左侧卡片列表，右侧编辑区域
        main_layout.setContentsMargins(5, 5, 5, 5)  # 减小边距，使用更多空间
        
        # 创建可调整的分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)  # 防止某个部分被完全折叠
        
        # 创建左侧手势卡片列表区域
        left_widget = QWidget()
        self.createGestureCardsList(left_widget)
        
        # 创建右侧手势编辑区域
        right_widget = QWidget()
        self.createGestureEditor(right_widget)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # 设置初始分割比例
        splitter.setSizes([int(self.width() * 0.3), int(self.width() * 0.7)])
        
        # 添加分割器到主布局
        main_layout.addWidget(splitter)
        
        # 设置布局
        self.setLayout(main_layout)
        
        # 连接实时更新信号
        self.name_input.textChanged.connect(self.name_input_textChanged)
        self.direction_combo.currentIndexChanged.connect(self.direction_combo_changed)
        self.action_type_combo.currentIndexChanged.connect(self.action_type_combo_changed)
        self.action_value_input.textChanged.connect(self.action_value_input_textChanged)
        
        # 更新手势列表
        self.updateGestureCards()
        
        # 启用响应式设计
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.logger.debug("手势管理选项卡启用了响应式设计")
    
    def createGestureCardsList(self, parent_widget):
        """创建左侧手势卡片列表区域"""
        # 创建左侧布局
        left_layout = QVBoxLayout(parent_widget)
        left_layout.setContentsMargins(0, 0, 5, 0)  # 减小内部边距
        
        # 标题标签
        title_label = QLabel("手势库")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        left_layout.addWidget(title_label)
        
        # 创建滚动区域，放置卡片
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 改为需要时才显示滚动条
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 创建卡片容器
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_layout.setSpacing(10)
        
        scroll_area.setWidget(self.cards_container)
        left_layout.addWidget(scroll_area, 1)  # 使用比例系数1让它可以拉伸
        
        # 添加操作按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 5, 0, 5)
        
        # 添加新手势按钮
        self.add_button = AnimatedButton("添加新手势", primary_color=[46, 204, 113])
        self.add_button.setMinimumSize(100, 36)  # 设置最小尺寸而不是固定尺寸
        self.add_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_button.clicked.connect(self.addNewGesture)
        
        # 重置按钮
        self.reset_button = AnimatedButton("重置为默认", primary_color=[108, 117, 125])
        self.reset_button.setMinimumSize(100, 36)  # 设置最小尺寸而不是固定尺寸
        self.reset_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.reset_button.clicked.connect(self.resetGestures)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.reset_button)
        
        left_layout.addLayout(buttons_layout)
        
        # 添加保存更改按钮
        save_layout = QHBoxLayout()
        save_layout.setContentsMargins(0, 5, 0, 0)
        
        self.save_button = AnimatedButton("保存更改", primary_color=[52, 152, 219])
        self.save_button.setMinimumSize(100, 50)  # 设置最小尺寸而不是固定尺寸
        self.save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.save_button.clicked.connect(self.saveGestureLibrary)
        
        save_layout.addWidget(self.save_button)
        
        left_layout.addLayout(save_layout)
        
        # 设置布局
        parent_widget.setLayout(left_layout)
        parent_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)  # 允许水平方向调整
    
    def createGestureEditor(self, parent_widget):
        """创建右侧手势编辑区域"""
        # 创建右侧布局
        right_layout = QVBoxLayout(parent_widget)
        right_layout.setContentsMargins(5, 0, 0, 0)  # 减小内部边距
        
        # 标题标签
        title_label = QLabel("编辑手势")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        right_layout.addWidget(title_label)
        
        # 创建滚动区域，以便在窗口较小时可以滚动查看表单
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 创建表单内容部件
        form_content = QWidget()
        form_content_layout = QVBoxLayout(form_content)
        form_content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 编辑表单
        form_group = QGroupBox("手势详情")
        form_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)  # 增加表单元素之间的间距
        
        # 名称输入
        name_layout = QHBoxLayout()
        name_label = QLabel("名称:")
        name_label.setMinimumWidth(80)
        name_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        self.name_input = QLineEdit()
        self.name_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        # 方向选择
        direction_layout = QHBoxLayout()
        direction_label = QLabel("方向:")
        direction_label.setMinimumWidth(80)
        direction_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(self.DIRECTIONS)
        self.direction_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(self.direction_combo)
        form_layout.addLayout(direction_layout)
        
        # 动作类型选择
        action_type_layout = QHBoxLayout()
        action_type_label = QLabel("动作类型:")
        action_type_label.setMinimumWidth(80)
        action_type_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems(self.ACTION_TYPES)
        self.action_type_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        action_type_layout.addWidget(action_type_label)
        action_type_layout.addWidget(self.action_type_combo)
        form_layout.addLayout(action_type_layout)
        
        # 动作值输入
        action_value_layout = QHBoxLayout()
        action_value_label = QLabel("动作值:")
        action_value_label.setMinimumWidth(80)
        action_value_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        self.action_value_input = QLineEdit()
        self.action_value_input.setPlaceholderText("例如: ctrl+c")
        self.action_value_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        action_value_layout.addWidget(action_value_label)
        action_value_layout.addWidget(self.action_value_input)
        form_layout.addLayout(action_value_layout)
        
        # 先定义按钮
        self.delete_button = AnimatedButton("删除手势", primary_color=[231, 76, 60])
        self.delete_button.setMinimumSize(120, 36)
        self.delete_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.delete_button.clicked.connect(self.deleteGesture)

        self.clear_button = AnimatedButton("清空表单", primary_color=[149, 165, 166])
        self.clear_button.setMinimumSize(120, 36)
        self.clear_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.clear_button.clicked.connect(self.clearEditor)

        # 添加按钮到布局
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        buttons_layout.addWidget(self.delete_button)

        # 设置表单布局
        form_group.setLayout(form_layout)
        form_content_layout.addWidget(form_group)

        # 添加按钮布局到内容布局
        form_content_layout.addLayout(buttons_layout)
        
        # 添加底部空白区域，确保内容在滚动区域中有足够的空间
        form_content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # 设置表单内容
        form_content.setLayout(form_content_layout)
        
        # 添加到滚动区域
        scroll_area.setWidget(form_content)
        
        # 添加到右侧布局
        right_layout.addWidget(scroll_area)
        
        # 设置布局
        parent_widget.setLayout(right_layout)
        parent_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def resizeEvent(self, event):
        """窗口尺寸变化事件处理，用于调整UI布局"""
        super().resizeEvent(event)
        self.logger.debug(f"手势管理选项卡大小已调整: {self.width()}x{self.height()}")
    
    def updateGestureCards(self, maintain_selected=True):
        """更新手势卡片列表
        
        Args:
            maintain_selected: 是否保持当前选中的卡片
        """
        self.logger.debug("更新手势卡片列表")
        current_gesture_name = None
        current_gesture_id = None
        
        # 记录当前选择的卡片
        if self.current_selected_card and maintain_selected:
            current_gesture_name, current_gesture_id = self.current_selected_card
        
        # 清除当前手势卡片
        self.clearGestureCards()
        
        try:
            # 按ID排序获取所有手势
            gestures = self.gestures.get_all_gestures_sorted()
            
            # 添加所有手势卡片
            for i, (name, gesture) in enumerate(gestures.items()):
                gesture_id = gesture.get("id")
                direction = gesture.get("direction", "")
                action_type = gesture.get("action", {}).get("type", "")
                action_value = gesture.get("action", {}).get("value", "")
                
                # 添加手势卡片
                card = self.addGestureCard(name, gesture_id, direction, action_type, action_value)
                
                # 如果是之前选中的手势，重新选中
                if maintain_selected and current_gesture_id is not None and gesture_id == current_gesture_id:
                    self.current_selected_card = (name, gesture_id)
                    self.highlightCard(card)
                    
                    # 更新表单内容
                    self.name_input.setText(name)
                    self.direction_combo.setCurrentText(direction)
                    self.action_type_combo.setCurrentText(action_type)
                    self.action_value_input.setText(action_value)
        except Exception as e:
            self.logger.error(f"更新手势卡片失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def onGestureCardClicked(self, card):
        """处理手势卡片点击事件"""
        self.logger.debug("手势卡片被点击")
        
        # 获取卡片的名称和ID
        name = card.property("name") if card.property("name") else card.get_title()
        gesture_id = card.property("id") if card.property("id") is not None else card.gesture_id
        
        # 确保ID是整数
        if isinstance(gesture_id, str):
            try:
                gesture_id = int(gesture_id)
            except (ValueError, TypeError):
                pass
        
        # 检查是否点击了当前已选中的卡片
        if self.current_selected_card and self.current_selected_card[0] == name and self.current_selected_card[1] == gesture_id:
            # 如果点击的是已选中的卡片，取消选中
            self.logger.debug(f"取消选中卡片: {name}, ID: {gesture_id}")
            card.set_selected(False)
            self.current_selected_card = None
            self.clearEditor()
            self.delete_button.setEnabled(False)
            return
        
        # 高亮选中的卡片
        self.highlightCard(card)
        
        # 设置当前选中的卡片
        self.current_selected_card = (name, gesture_id)
        self.logger.debug(f"当前选中卡片: {name}, ID: {gesture_id}")
        
        # 获取手势信息
        gesture = self.gestures.get_gesture(name)
        if gesture:
            # 更新表单内容
            self.name_input.setText(name)
            self.direction_combo.setCurrentText(gesture.get("direction", ""))
            action_type = gesture.get("action", {}).get("type", "")
            action_value = gesture.get("action", {}).get("value", "")
            self.action_type_combo.setCurrentText(action_type)
            self.action_value_input.setText(action_value)
            
            # 这里不要设置was_selected=True，因为我们期望表单变化时自动更新
            self.is_form_ready = True
        
        # 更新删除按钮状态
        self.delete_button.setEnabled(True)
    
    def addNewGesture(self):
        """添加新手势"""
        self.logger.debug("添加新手势")
        was_selected = self.current_selected_card is not None
        
        try:
            # 获取表单数据
            name = self.name_input.text().strip()
            direction = self.direction_combo.currentText()
            action_type = self.action_type_combo.currentText()
            action_value = self.action_value_input.text().strip()
            
            # 验证数据
            if not name:
                self.logger.warning("手势名称不能为空")
                return
                
            if not action_value:
                self.logger.warning("动作值不能为空")
                return
                
            # 检查名称是否已存在
            if name in self.gestures.list_gestures():
                self.logger.warning(f"手势名称已存在: {name}")
                return
                
            # 获取下一个可用ID
            next_id = self.gestures._get_next_id()
            
            # 添加新手势
            success = self.gestures.add_gesture(
                name, 
                direction, 
                action_type, 
                action_value,
                gesture_id=next_id
            )
            
            if success:
                self.logger.info(f"成功添加新手势: {name}, ID: {next_id}")
                
                # 更新手势卡片列表，不保持选择状态
                self.updateGestureCards(maintain_selected=False)
                
                # 选中新添加的手势卡片
                for i in range(self.cards_layout.count()):
                    card = self.cards_layout.itemAt(i).widget()
                    if card and card.property("name") == name:
                        self.onGestureCardClicked(card)
                        break
                
                # 保存手势库
                self.gestures.save()
            else:
                self.logger.warning(f"添加手势时没有变化: {name}")
        except Exception as e:
            self.logger.error(f"添加新手势失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def clearEditor(self):
        """清空编辑区域"""
        # 暂时断开信号连接，避免触发onFormChanged
        self.name_input.blockSignals(True)
        self.direction_combo.blockSignals(True)
        self.action_type_combo.blockSignals(True)
        self.action_value_input.blockSignals(True)
        
        self.name_input.clear()
        self.direction_combo.setCurrentIndex(0)
        self.action_type_combo.setCurrentIndex(0)
        self.action_value_input.clear()
        
        # 恢复信号连接
        self.name_input.blockSignals(False)
        self.direction_combo.blockSignals(False)
        self.action_type_combo.blockSignals(False)
        self.action_value_input.blockSignals(False)
        
        # 清除当前选中状态
        if self.current_selected_card:
            name, gesture_id = self.current_selected_card
            if name in self.gesture_cards:
                self.gesture_cards[name].set_selected(False)
        
        # 重置当前选中的卡片
        self.current_selected_card = None
    
    def updateCardContent(self, name, gesture):
        """直接更新卡片内容，不重新创建卡片"""
        if name not in self.gesture_cards:
            return False
            
        try:
            card = self.gesture_cards[name]
            
            # 查找自定义内容组件
            content_widget = card.findChild(GestureContentWidget)
            if not content_widget:
                return False
            
            # 获取最新的数据
            direction = gesture.get('direction', '未知')
            action = gesture.get("action", {})
            action_type = action.get("type", "未知")
            action_value = action.get("value", "")
            
            # 使用自定义组件的更新方法
            success = content_widget.updateContent(direction, action_type, action_value)
            
            # 记录成功或失败
            if success:
                self.logger.debug(f"直接更新卡片内容成功: {name} - 方向: '{direction}', 动作: '{action_type} - {action_value}'")
            else:
                self.logger.debug(f"直接更新卡片内容失败: {name}")
            
            return success
        except Exception as e:
            self.logger.error(f"更新卡片内容失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
            
    def onFormChanged(self):
        """表单内容变化时自动应用更改"""
        # 获取表单数据
        name = self.name_input.text().strip()
        direction = self.direction_combo.currentText()
        action_type = self.action_type_combo.currentText()
        action_value = self.action_value_input.text().strip()
        
        # 表单数据不完整，不处理
        if not name or not action_value:
            return
            
        # 如果没有选中任何手势，不进行自动应用和UI更新
        # 用户需要点击"添加新手势"按钮来创建新手势
        if not self.current_selected_card:
            return
            
        # 获取当前选中手势的名称和ID
        current_name, current_id = self.current_selected_card
        
        # 检查是否修改了名称
        is_rename = current_name != name
        
        try:
            if is_rename:
                # 检查新名称是否已存在
                if name in self.gestures.list_gestures():
                    # 名称已存在，不自动保存，用户需要修改名称
                    return
                    
                # 执行重命名操作
                success = self.gestures.update_gesture_name(current_name, name)
                if not success:
                    self.logger.warning(f"重命名手势失败: {current_name} -> {name}")
                    return
                    
                # 更新当前选中的手势名称
                self.current_selected_card = (name, current_id)
                self.logger.debug(f"手势已重命名: {current_name} -> {name}")
                
                # 重命名情况下需要更新整个列表（使用updateGestureCards方法）
                self.gestures.add_gesture(name, direction, action_type, action_value, current_id)
                self.updateGestureCards(maintain_selected=True)
            else:
                # 获取当前手势的ID（如果存在）
                gesture_id = current_id
                current_gesture = self.gestures.get_gesture(current_name)
                if not current_gesture:
                    # 如果手势不存在，不进行更新
                    return
                
                # 记录更新前的卡片内容（调试用）
                self.logger.debug(f"更新前卡片内容:")
                self.dumpCardContents(current_name)
                
                # 添加或更新手势 - 这会标记有未保存更改
                result = self.gestures.add_gesture(name, direction, action_type, action_value, gesture_id)
                self.logger.debug(f"添加/更新手势结果: {result}, 手势名称: {name}, 方向: {direction}")
                
                # 只有在编辑现有手势时才更新UI
                if name in self.gesture_cards:
                    # 创建临时手势数据结构用于更新
                    temp_gesture = {
                        "id": gesture_id,
                        "direction": direction,
                        "action": {
                            "type": action_type,
                            "value": action_value
                        }
                    }
                    
                    # 直接尝试更新卡片内容，无需重新获取手势数据
                    updated = self.updateCardContent(name, temp_gesture)
                    self.logger.debug(f"卡片内容更新结果: {updated}")
                    
                    # 如果直接更新失败，使用完整的刷新方法
                    if not updated:
                        self.logger.debug(f"直接更新失败，尝试完整刷新")
                        self.updateGestureCards(maintain_selected=True)
                    
                    # 记录更新后的卡片内容（调试用）
                    self.logger.debug(f"更新后卡片内容:")
                    self.dumpCardContents(name)
                
                self.logger.debug(f"手势已修改: {name}")
        except Exception as e:
            self.logger.error(f"自动应用手势修改失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def onDeleteGestureConfirmed(self):
        """确认删除手势"""
        if not self.current_selected_card:
            return
        
        name, gesture_id = self.current_selected_card
        
        # 删除手势并重新排序ID
        if self.gestures.remove_gesture(name):
            # 保存手势库
            self.gestures.save()
            
            # 清除表单
            self.clearEditor()
            
            # 重置当前选中的卡片
            self.current_selected_card = None
        
        # 更新手势卡片列表
            self.updateGestureCards(maintain_selected=False)
        
            # 禁用删除按钮
            self.delete_button.setEnabled(False)
        
            self.logger.info(f"成功删除手势: {name}, ID: {gesture_id}")
        else:
            self.logger.warning(f"删除手势失败: {name}")
    
    def deleteGesture(self):
        """删除当前编辑的手势"""
        # 如果没有选中的手势，则返回
        if not self.current_selected_card:
            QMessageBox.warning(self, "删除错误", "请先选择要删除的手势")
            return
        
        name, gesture_id = self.current_selected_card
        
        # 确认删除
        reply = QMessageBox.question(self, "确认删除", 
                                    f"确定要删除手势 '{name}' 吗?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.onDeleteGestureConfirmed()
    
    def resetGestures(self):
        """重置为默认手势库"""
        reply = QMessageBox.question(self, "确认重置", 
                                    "确定要重置为默认手势库吗? 这将覆盖所有当前的手势设置。",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 重置手势库
            self.gestures.reset_to_default()
            
            # 更新列表
            self.updateGestureCards()
            
            # 清空编辑区域
            self.clearEditor()
            
            self.logger.info("重置为默认手势库")
            QMessageBox.information(self, "重置成功", "已重置为默认手势库，记得点击「保存更改」按钮保存更改。")
    
    def saveGestureLibrary(self):
        """保存手势库"""
        try:
        # 保存手势库
            success = self.gestures.save()
            
            if success:
                self.logger.info("手势库保存成功")
                # 显示成功消息
                QMessageBox.information(self, "保存成功", "所有手势更改已成功保存")
                return True
            else:
                self.logger.error("手势库保存失败")
                QMessageBox.warning(self, "保存失败", "无法保存手势库")
                return False
        except Exception as e:
            self.logger.error(f"保存手势库时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存手势库时出错: {str(e)}")
            return False

    def name_input_textChanged(self):
        """名称输入框文本变化时的处理"""
        self.onFormChanged()

    def direction_combo_changed(self):
        """方向下拉框变化时的处理"""
        self.onFormChanged()

    def action_type_combo_changed(self):
        """动作类型下拉框变化时的处理"""
        self.onFormChanged()

    def action_value_input_textChanged(self):
        """动作值输入框文本变化时的处理"""
        self.onFormChanged()

    def dumpCardContents(self, name=None):
        """打印卡片内容，用于调试"""
        if name and name in self.gesture_cards:
            # 打印单个卡片的内容
            card = self.gesture_cards[name]
            content_widget = card.findChild(GestureContentWidget)
            if content_widget:
                direction_text = content_widget.direction_label.text()
                action_text = content_widget.action_label.text()
                self.logger.debug(f"卡片 '{name}' 内容: 标题={card.get_title()}, {direction_text}, {action_text}")
        else:
            # 打印所有卡片的内容
            for card_name, card in self.gesture_cards.items():
                content_widget = card.findChild(GestureContentWidget)
                if content_widget:
                    direction_text = content_widget.direction_label.text()
                    action_text = content_widget.action_label.text()
                    self.logger.debug(f"卡片 '{card_name}' 内容: 标题={card.get_title()}, {direction_text}, {action_text}")

    def highlightCard(self, card):
        """高亮显示选中的卡片
        
        Args:
            card: 要高亮的卡片控件
        """
        # 清除所有卡片的选中状态
        for name, stored_card in self.gesture_cards.items():
            stored_card.set_selected(False)
        
        # 设置当前卡片为选中状态
        card.set_selected(True)
        
    def clearGestureCards(self):
        """清除所有手势卡片"""
        # 清空所有卡片
        for name, card in list(self.gesture_cards.items()):
            self.cards_layout.removeWidget(card)
            card.setParent(None)
            card.deleteLater()
        
        # 清空字典
        self.gesture_cards.clear()
        
    def addGestureCard(self, name, gesture_id, direction, action_type, action_value):
        """添加手势卡片
        
        Args:
            name: 手势名称
            gesture_id: 手势ID
            direction: 手势方向
            action_type: 动作类型
            action_value: 动作值
            
        Returns:
            CardWidget: 手势卡片控件
        """
        # 确保ID是整数
        if isinstance(gesture_id, str):
            try:
                gesture_id = int(gesture_id)
            except (ValueError, TypeError):
                gesture_id = 0
        
        self.logger.debug(f"添加手势卡片: {name}, ID: {gesture_id}")
        
        # 创建卡片控件
        card = CardWidget(title=name)
        card.gesture_id = gesture_id
        
        # 使用Qt属性系统设置name和id属性
        card.setProperty("name", name)
        card.setProperty("id", gesture_id)
        
        # 创建并添加自定义内容组件
        content_widget = GestureContentWidget(direction, action_type, action_value)
        card.add_widget(content_widget)
        
        # 添加点击事件 - 使用函数工厂模式避免闭包问题
        def create_click_handler(card_widget):
            return lambda checked=False: self.onGestureCardClicked(card_widget)
        card.clicked.connect(create_click_handler(card))
        
        # 添加到布局和字典
        self.cards_layout.addWidget(card)
        self.gesture_cards[name] = card
        
        return card

# 以下代码用于测试手势管理选项卡
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("手势管理选项卡测试")
    window.resize(900, 600)
    window.setStyleSheet("background-color: #f0f0f0;")
    
    layout = QVBoxLayout(window)
    
    # 创建手势管理选项卡
    gestures_tab = GesturesTab()
    layout.addWidget(gestures_tab)
    
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec_()) 