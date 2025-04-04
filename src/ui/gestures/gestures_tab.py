import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QApplication, QLineEdit, QComboBox,
                            QScrollArea, QHeaderView, QSizePolicy,
                            QGroupBox, QMessageBox, QPushButton, QAbstractItemView,
                            QFrame, QGridLayout, QSpacerItem)
from PyQt5.QtCore import Qt, QSize
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
        
        # 创建左侧手势卡片列表区域
        self.createGestureCardsList(main_layout)
        
        # 创建右侧手势编辑区域
        self.createGestureEditor(main_layout)
        
        # 设置布局
        self.setLayout(main_layout)
        
        # 更新手势列表
        self.updateGestureCards()
    
    def createGestureCardsList(self, parent_layout):
        """创建左侧手势卡片列表区域"""
        # 创建左侧区域容器
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        # 标题标签
        title_label = QLabel("手势库")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)
        
        # 创建滚动区域，放置卡片
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 创建卡片容器
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_layout.setSpacing(10)
        
        scroll_area.setWidget(self.cards_container)
        left_layout.addWidget(scroll_area)
        
        # 添加操作按钮
        buttons_layout = QHBoxLayout()
        
        # 添加新手势按钮
        self.add_button = AnimatedButton("添加新手势", primary_color=[46, 204, 113])
        self.add_button.clicked.connect(self.addNewGesture)
        
        # 重置按钮
        self.reset_button = AnimatedButton("重置为默认", primary_color=[108, 117, 125])
        self.reset_button.clicked.connect(self.resetGestures)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.reset_button)
        
        left_layout.addLayout(buttons_layout)
        
        # 设置左侧容器的固定宽度
        left_container.setFixedWidth(300)
        left_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        # 添加到主布局
        parent_layout.addWidget(left_container)
        
        # 添加垂直分割线
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        parent_layout.addWidget(line)
    
    def createGestureEditor(self, parent_layout):
        """创建右侧手势编辑区域"""
        # 创建右侧区域容器
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        
        # 标题标签
        title_label = QLabel("编辑手势")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(title_label)
        
        # 编辑表单
        form_group = QGroupBox("手势详情")
        form_layout = QVBoxLayout()
        
        # 名称输入
        name_layout = QHBoxLayout()
        name_label = QLabel("名称:")
        name_label.setMinimumWidth(80)
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        # 方向选择
        direction_layout = QHBoxLayout()
        direction_label = QLabel("方向:")
        direction_label.setMinimumWidth(80)
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(self.DIRECTIONS)
        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(self.direction_combo)
        form_layout.addLayout(direction_layout)
        
        # 动作类型选择
        action_type_layout = QHBoxLayout()
        action_type_label = QLabel("动作类型:")
        action_type_label.setMinimumWidth(80)
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems(self.ACTION_TYPES)
        action_type_layout.addWidget(action_type_label)
        action_type_layout.addWidget(self.action_type_combo)
        form_layout.addLayout(action_type_layout)
        
        # 动作值输入
        action_value_layout = QHBoxLayout()
        action_value_label = QLabel("动作值:")
        action_value_label.setMinimumWidth(80)
        self.action_value_input = QLineEdit()
        self.action_value_input.setPlaceholderText("例如: ctrl+c")
        action_value_layout.addWidget(action_value_label)
        action_value_layout.addWidget(self.action_value_input)
        form_layout.addLayout(action_value_layout)
        
        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        
        # 保存按钮
        self.save_gesture_button = AnimatedButton("保存更改", primary_color=[41, 128, 185])
        self.save_gesture_button.clicked.connect(self.saveGesture)
        
        # 删除按钮
        self.delete_button = AnimatedButton("删除手势", primary_color=[231, 76, 60])
        self.delete_button.clicked.connect(self.deleteGesture)
        
        # 清空按钮
        self.clear_button = AnimatedButton("清空表单", primary_color=[149, 165, 166])
        self.clear_button.clicked.connect(self.clearEditor)
        
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.save_gesture_button)
        
        right_layout.addLayout(buttons_layout)
        
        # 保存所有更改按钮
        save_all_layout = QHBoxLayout()
        self.save_all_button = AnimatedButton("保存所有更改", primary_color=[52, 152, 219])
        self.save_all_button.clicked.connect(self.saveGestureLibrary)
        self.save_all_button.setMinimumHeight(50)
        save_all_layout.addWidget(self.save_all_button)
        
        right_layout.addLayout(save_all_layout)
        
        # 添加弹性空间
        right_layout.addStretch()
        
        # 添加到主布局
        parent_layout.addWidget(right_container, 1)  # 设置右侧区域占据更多空间
    
    def onCardClicked(self):
        """卡片点击事件处理器"""
        # 获取发送信号的卡片
        card = self.sender()
        if not card:
            return
            
        # 遍历查找对应的手势名称
        for name, stored_card in self.gesture_cards.items():
            if stored_card == card:
                self.onGestureCardClicked(name)
                break
    
    def updateGestureCards(self):
        """更新手势卡片列表"""
        # 清空现有卡片
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.gesture_cards = {}  # 重置卡片引用字典
        
        # 获取所有手势
        all_gestures = self.gestures.get_all_gestures()
        if not all_gestures:
            # 如果没有手势，显示一个提示卡片
            empty_card = CardWidget(title="没有手势")
            empty_label = QLabel("点击「添加新手势」按钮\n创建第一个手势")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_card.add_widget(empty_label)
            self.cards_layout.addWidget(empty_card)
            return
        
        # 添加手势卡片
        for name, gesture in all_gestures.items():
            # 创建卡片
            card = CardWidget(title=name)
            
            # 创建卡片内容
            content_layout = QVBoxLayout()
            content_layout.setContentsMargins(5, 5, 5, 5)  # 添加内边距
            
            # 添加方向信息
            direction_layout = QHBoxLayout()
            direction_label = QLabel("方向:")
            direction_label.setStyleSheet("font-weight: bold;")
            direction_value = QLabel(gesture.get("direction", ""))
            direction_layout.addWidget(direction_label)
            direction_layout.addWidget(direction_value)
            content_layout.addLayout(direction_layout)
            
            # 添加动作信息
            action = gesture.get("action", {})
            action_layout = QHBoxLayout()
            action_label = QLabel("动作:")
            action_label.setStyleSheet("font-weight: bold;")
            action_value = QLabel(f"{action.get('type', '')}: {action.get('value', '')}")
            action_layout.addWidget(action_label)
            action_layout.addWidget(action_value)
            content_layout.addLayout(action_layout)
            
            # 创建内容容器
            content_widget = QWidget()
            content_widget.setLayout(content_layout)
            card.add_widget(content_widget)
            
            # 连接点击事件 - 使用通用的处理器
            card.clicked.connect(self.onCardClicked)
            
            # 添加到布局
            self.cards_layout.addWidget(card)
            
            # 存储卡片引用
            self.gesture_cards[name] = card
    
    def onGestureCardClicked(self, name):
        """当点击手势卡片时，更新编辑区域并更新卡片选中状态"""
        # 先清除所有卡片的选中状态
        for card_name, card in self.gesture_cards.items():
            if card_name != name:
                card.set_selected(False)
        
        # 设置当前卡片为选中状态
        current_card = self.gesture_cards.get(name)
        if current_card:
            current_card.set_selected(True)
            self.current_selected_card = name
        
        # 获取手势详情
        gesture = self.gestures.get_gesture(name)
        if not gesture:
            return
        
        # 更新编辑区域
        self.name_input.setText(name)
        
        # 查找并设置方向下拉框
        direction = gesture.get("direction", "")
        direction_index = self.direction_combo.findText(direction)
        if direction_index != -1:
            self.direction_combo.setCurrentIndex(direction_index)
        
        # 查找并设置动作类型下拉框
        action = gesture.get("action", {})
        action_type = action.get("type", "")
        action_type_index = self.action_type_combo.findText(action_type)
        if action_type_index != -1:
            self.action_type_combo.setCurrentIndex(action_type_index)
        
        # 设置动作值
        action_value = action.get("value", "")
        self.action_value_input.setText(action_value)
    
    def addNewGesture(self):
        """添加新手势"""
        # 清空编辑区域
        self.clearEditor()
        
        # 清除所有卡片的选中状态
        for card_name, card in self.gesture_cards.items():
            card.set_selected(False)
        
        self.current_selected_card = None
    
    def clearEditor(self):
        """清空编辑区域"""
        self.name_input.clear()
        self.direction_combo.setCurrentIndex(0)
        self.action_type_combo.setCurrentIndex(0)
        self.action_value_input.clear()
        
        # 清除当前选中状态
        if self.current_selected_card and self.current_selected_card in self.gesture_cards:
            self.gesture_cards[self.current_selected_card].set_selected(False)
        self.current_selected_card = None
    
    def saveGesture(self):
        """保存当前编辑的手势"""
        # 获取输入
        name = self.name_input.text().strip()
        direction = self.direction_combo.currentText()
        action_type = self.action_type_combo.currentText()
        action_value = self.action_value_input.text().strip()
        
        # 验证输入
        if not name:
            QMessageBox.warning(self, "输入错误", "手势名称不能为空")
            return
            
        if not action_value:
            QMessageBox.warning(self, "输入错误", "动作值不能为空")
            return
        
        # 检查是否是新增还是更新
        is_new = self.current_selected_card is None or self.current_selected_card != name
        
        # 如果是新增，并且手势名称已存在，则提示错误
        if is_new and name in self.gestures.get_all_gestures():
            QMessageBox.warning(self, "输入错误", f"手势名称 '{name}' 已存在")
            return
        
        # 保存手势
        self.gestures.add_gesture(name, direction, action_type, action_value)
        
        # 如果是修改了手势名称，则需要删除旧的手势
        if self.current_selected_card and self.current_selected_card != name:
            self.gestures.remove_gesture(self.current_selected_card)
        
        # 更新手势卡片列表
        self.updateGestureCards()
        
        # 设置新保存的手势为选中状态
        if name in self.gesture_cards:
            self.onGestureCardClicked(name)
        
        self.logger.debug(f"保存手势: {name}")
        QMessageBox.information(self, "保存成功", f"手势 '{name}' 已保存")
    
    def deleteGesture(self):
        """删除当前编辑的手势"""
        # 如果没有选中的手势，则返回
        if not self.current_selected_card:
            QMessageBox.warning(self, "删除错误", "请先选择要删除的手势")
            return
        
        # 确认删除
        reply = QMessageBox.question(self, "确认删除", 
                                    f"确定要删除手势 '{self.current_selected_card}' 吗?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除手势
            self.gestures.remove_gesture(self.current_selected_card)
            
            # 更新列表
            self.updateGestureCards()
            
            # 清空编辑区域
            self.clearEditor()
            
            self.logger.debug(f"删除手势: {self.current_selected_card}")
            QMessageBox.information(self, "删除成功", "手势已删除")
    
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
            
            self.logger.debug("重置为默认手势库")
            QMessageBox.information(self, "重置成功", "已重置为默认手势库")
    
    def saveGestureLibrary(self):
        """保存手势库到文件"""
        # 保存手势库
        self.gestures.save()
        
        self.logger.debug("保存手势库到文件")
        QMessageBox.information(self, "保存成功", "手势库已保存到文件")


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