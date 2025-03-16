// 手势管理页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化界面
    initGestureEditor();
    
    // 添加ESC键监听，关闭编辑器
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const editorContainer = document.getElementById('gesture-editor-container');
            if (editorContainer && editorContainer.style.display === 'block') {
                hideGestureEditor();
            }
        }
    });
});

// 编辑模式类型
const EDIT_MODE = {
    CREATE: 'create',
    EDIT: 'edit'
};

// 方向映射表
const DIRECTION_MAP = {
    '上': '↑',
    '右上': '↗',
    '右': '→',
    '右下': '↘',
    '下': '↓',
    '左下': '↙',
    '左': '←',
    '左上': '↖'
};

// 反向方向映射表
const REVERSE_DIRECTION_MAP = {
    '↑': '上',
    '↗': '右上',
    '→': '右',
    '↘': '右下',
    '↓': '下',
    '↙': '左下',
    '←': '左',
    '↖': '左上'
};

// 当前编辑模式
let currentMode = null;
// 当前编辑中的手势名称（编辑模式下使用）
let currentGestureName = null;

// 初始化手势编辑界面
function initGestureEditor() {
    // 添加手势按钮
    const addBtn = document.getElementById('add-gesture-btn');
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            showGestureEditor(EDIT_MODE.CREATE);
        });
    }
    
    // 取消按钮
    const cancelBtn = document.getElementById('cancel-edit-btn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', hideGestureEditor);
    }
    
    // 关闭按钮
    const closeBtn = document.getElementById('close-editor-btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', hideGestureEditor);
    }
    
    // 初始化方向按钮
    initDirectionButtons();
    
    // 初始化手势项事件
    initGestureItems();
    
    // 初始化表单提交
    initGestureForm();
    
    // 初始化测试按钮
    initTestButton();
}

// 显示手势编辑器
function showGestureEditor(mode, gestureName = null) {
    const editorContainer = document.getElementById('gesture-editor-container');
    const editorTitle = document.getElementById('editor-title');
    const form = document.getElementById('gesture-form');
    
    // 设置当前模式
    currentMode = mode;
    currentGestureName = gestureName;
    
    // 更新标题
    if (mode === EDIT_MODE.CREATE) {
        editorTitle.textContent = '添加手势';
        form.reset(); // 清空表单
        
        // 初始化名称输入框
        initGestureNameInput();
        // 清空方向序列显示
        const directionsInput = document.getElementById('gesture-directions');
        if (directionsInput) {
            directionsInput.value = '';
        }
    } else {
        editorTitle.textContent = '编辑手势';
        
        // 查找并加载手势数据
        const gestureItem = document.querySelector(`.gesture-item[data-name="${gestureName}"]`);
        if (gestureItem) {
            const directions = gestureItem.getAttribute('data-directions');
            const action = gestureItem.getAttribute('data-action');
            
            // 初始化名称输入框
            initGestureNameInput(gestureName);
            
            // 设置方向序列
            const directionsInput = document.getElementById('gesture-directions');
            if (directionsInput) {
                directionsInput.value = directions;
            }
            
            // 设置动作字段值
            document.getElementById('gesture-action').value = atob(action); // 解码base64
        }
    }
    
    // 显示编辑器
    editorContainer.style.display = 'block';
    
    // 聚焦第一个输入框
    setTimeout(() => {
        const gestureName = document.getElementById('gesture-name');
        if (gestureName) {
            gestureName.focus();
        }
    }, 100);
}

// 隐藏手势编辑器
function hideGestureEditor() {
    const editorContainer = document.getElementById('gesture-editor-container');
    
    // 添加渐出动画
    editorContainer.style.opacity = '0';
    
    // 动画完成后隐藏
    setTimeout(() => {
        editorContainer.style.display = 'none';
        
        // 重置模式
        currentMode = null;
        currentGestureName = null;
        
        // 移除所有高亮
        document.querySelectorAll('.gesture-item').forEach(item => {
            item.classList.remove('active');
        });
    }, 300);
}

// 初始化手势名称输入框
function initGestureNameInput(initialValue = '') {
    const container = document.getElementById('gesture-name-container');
    if (!container) return;
    
    // 清空容器
    container.innerHTML = '';
    
    // 创建输入框组件
    const inputContainer = createInputField('gesture-name', '手势名称', {
        icon: 'fas fa-signature',
        placeholder: '请输入手势名称',
        hint: '',
        validator: function(value) {
            if (!value || value.trim() === '') {
                return { valid: false, message: '手势名称不能为空' };
            }
            
            // 检查名称长度
            if (value.length > 20) {
                return { valid: false, message: '手势名称不能超过20个字符' };
            }
            
            // 检查是否存在重名（仅在创建新手势时）
            if (currentMode === EDIT_MODE.CREATE) {
                const existingGesture = document.querySelector(`.gesture-item[data-name="${value}"]`);
                if (existingGesture) {
                    return { valid: false, message: '此手势名称已存在' };
                }
            } else if (currentMode === EDIT_MODE.EDIT && value !== currentGestureName) {
                // 编辑模式下，如果更改了名称，也要检查重名
                const existingGesture = document.querySelector(`.gesture-item[data-name="${value}"]`);
                if (existingGesture) {
                    return { valid: false, message: '此手势名称已存在' };
                }
            }
            
            return { valid: true, success: true };
        }
    });
    
    // 添加到容器
    container.appendChild(inputContainer);
    
    // 设置初始值（如果有）
    if (initialValue) {
        setInputValue('gesture-name', initialValue);
    }
}

// 验证方向输入
function validateDirections(directions) {
    const validArrows = Object.values(DIRECTION_MAP);
    
    if (!directions || directions.trim() === '') {
        return false;
    }
    
    // 分割输入的方向
    const dirArray = directions.trim().split(/\s+/);
    
    // 检查每个方向是否有效
    for (const dir of dirArray) {
        if (!validArrows.includes(dir)) {
            return false;
        }
    }
    
    // 检查至少有一个方向
    if (dirArray.length === 0) {
        return false;
    }
    
    return true;
}

// 初始化方向按钮
function initDirectionButtons() {
    // 方向箭头按钮
    const dirButtons = document.querySelectorAll('.direction-btn:not(.clear-direction-btn)');
    
    dirButtons.forEach(button => {
        button.addEventListener('click', () => {
            const direction = button.getAttribute('data-direction');
            const arrowDirection = DIRECTION_MAP[direction] || direction;
            
            const directionsInput = document.getElementById('gesture-directions');
            if (directionsInput) {
                const currentVal = directionsInput.value;
                
                // 检查是否需要添加空格
                let newVal = '';
                if (currentVal && !currentVal.endsWith(' ')) {
                    newVal = currentVal + ' ' + arrowDirection;
                } else {
                    newVal = currentVal + arrowDirection;
                }
                
                // 设置新值
                directionsInput.value = newVal;
            }
        });
    });
    
    // 清除按钮功能
    const clearButton = document.querySelector('.clear-direction-btn');
    if (clearButton) {
        clearButton.addEventListener('click', () => {
            const directionsInput = document.getElementById('gesture-directions');
            if (directionsInput) {
                // 获取当前值
                let currentValue = directionsInput.value;
                
                // 如果有内容，则删除最后一个方向（及其前面的空格）
                if (currentValue) {
                    // 去除尾部可能的空格
                    currentValue = currentValue.trim();
                    
                    // 查找最后一个箭头符号位置
                    const lastArrowIndex = Math.max(
                        currentValue.lastIndexOf('↑'),
                        currentValue.lastIndexOf('↗'),
                        currentValue.lastIndexOf('→'),
                        currentValue.lastIndexOf('↘'),
                        currentValue.lastIndexOf('↓'),
                        currentValue.lastIndexOf('↙'),
                        currentValue.lastIndexOf('←'),
                        currentValue.lastIndexOf('↖')
                    );
                    
                    // 去除最后一个箭头及其前面的空格
                    if (lastArrowIndex > 0) {
                        // 找到最后一个箭头前的空格
                        const lastSpaceBeforeArrow = currentValue.lastIndexOf(' ', lastArrowIndex - 1);
                        directionsInput.value = currentValue.substring(0, lastSpaceBeforeArrow + 1);
                    } else if (lastArrowIndex === 0) {
                        // 如果是第一个箭头，则清空
                        directionsInput.value = '';
                    }
                }
            }
        });
    }
}

// 初始化表单提交
function initGestureForm() {
    const form = document.getElementById('gesture-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 获取表单数据
        const name = getInputValue('gesture-name').trim();
        const directionsInput = document.getElementById('gesture-directions');
        let directions = directionsInput ? directionsInput.value.trim() : '';
        const action = document.getElementById('gesture-action').value.trim();
        
        // 验证
        if (!name) {
            showToast('请输入手势名称', 'error');
            return;
        }
        
        if (!directions) {
            showToast('请添加至少一个方向', 'error');
            return;
        }
        
        if (!validateDirections(directions)) {
            showToast('无效的方向设置', 'error');
            return;
        }
        
        if (!action) {
            showToast('请输入执行动作', 'error');
            return;
        }

        // 确保方向序列格式正确且使用箭头符号
        directions = directions.split(/\s+/).map(dir => {
            // 如果输入的是中文方向名称，转换为箭头符号
            for (const [dirName, arrow] of Object.entries(DIRECTION_MAP)) {
                if (dir === dirName) {
                    return arrow;
                }
            }
            return dir;
        }).join(' ');
        
        // 显示保存中提示
        showToast('正在保存...', 'info');
        
        // 编码动作为Base64
        const actionBase64 = btoa(action);
        
        // 确定操作类型：添加或更新
        const operationType = currentMode === EDIT_MODE.CREATE ? 'add' : 'update';
        
        // 构建请求数据
        let requestData = {
            operation: operationType,
            directions: directions,
            action: actionBase64
        };
        
        // 根据操作类型添加不同的参数
        if (operationType === 'add') {
            requestData.name = name;
            console.log('添加手势', requestData);
        } else {
            requestData.old_name = currentGestureName;
            requestData.new_name = name; // 修改操作使用new_name而不是name
            console.log('修改手势', requestData);
        }
        
        // 发送到服务器
        fetch('/api/gestures', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(operationType === 'add' ? '手势添加成功' : '手势更新成功', 'success');
                // 刷新页面以显示更新后的手势列表
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showToast(`操作失败: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('保存手势失败:', error);
            showToast('保存手势失败，请重试', 'error');
        });
    });
}

// 初始化手势项点击事件
function initGestureItems() {
    // 编辑按钮
    document.querySelectorAll('.edit-gesture-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡
            const gestureItem = this.closest('.gesture-item');
            const gestureName = gestureItem.getAttribute('data-name');
            showGestureEditor(EDIT_MODE.EDIT, gestureName);
        });
    });
    
    // 删除按钮
    document.querySelectorAll('.delete-gesture-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡
            const gestureItem = this.closest('.gesture-item');
            const gestureName = gestureItem.getAttribute('data-name');
            
            // 显示确认对话框
            showConfirm(`确定要删除手势 "${gestureName}" 吗？`, function() {
                deleteGesture(gestureName);
            });
        });
    });
    
    // 手势项点击 - 编辑
    document.querySelectorAll('.gesture-item').forEach(item => {
        item.addEventListener('click', function() {
            const gestureName = this.getAttribute('data-name');
            showGestureEditor(EDIT_MODE.EDIT, gestureName);
        });
    });
}

// 删除手势
function deleteGesture(name) {
    // 显示删除中提示
    showToast('正在删除...', 'info');
    
    fetch('/api/gestures', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            operation: 'delete',
            name: name
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('手势删除成功', 'success');
            // 刷新页面以显示更新后的手势列表
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showToast(`删除失败: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('删除手势失败:', error);
        showToast('删除手势失败，请重试', 'error');
    });
}

// 初始化测试按钮
function initTestButton() {
    const testBtn = document.getElementById('test-gesture-btn');
    if (!testBtn) return;
    
    testBtn.addEventListener('click', function() {
        const action = document.getElementById('gesture-action').value.trim();
        
        if (!action) {
            showToast('请先输入要测试的操作代码', 'warning');
            return;
        }
        
        // 添加确认对话框
        showConfirm('确定要测试此操作吗？测试将直接执行代码。', function() {
            // 显示测试中提示
            showToast('正在执行测试...', 'info');
            
            // 编码为Base64
            const actionBase64 = btoa(action);
            
            // 发送测试请求
            fetch('/api/test_gesture', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ action: actionBase64 })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('操作执行成功', 'success');
                } else {
                    showToast(`操作执行失败: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                console.error('测试操作失败:', error);
                showToast('测试操作失败，请检查代码', 'error');
            });
        });
    });
} 