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
    const cancelBtn = document.getElementById('cancel-btn');
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
    } else {
        editorTitle.textContent = '编辑手势';
        
        // 填充表单数据
        const gestureItem = document.querySelector(`.gesture-item[data-name="${gestureName}"]`);
        if (gestureItem) {
            document.getElementById('gesture-name').value = gestureName;
            document.getElementById('gesture-directions').value = gestureItem.getAttribute('data-directions');
            
            // 解码 Base64 编码的操作
            const action = gestureItem.getAttribute('data-action');
            try {
                const decodedAction = atob(action);
                document.getElementById('gesture-action').value = decodedAction;
            } catch (e) {
                console.error('无法解码动作:', e);
                document.getElementById('gesture-action').value = '';
            }
        }
    }
    
    // 高亮选中的手势项
    if (mode === EDIT_MODE.EDIT) {
        document.querySelectorAll('.gesture-item').forEach(item => {
            item.classList.remove('active');
        });
        const activeItem = document.querySelector(`.gesture-item[data-name="${gestureName}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }
    
    // 显示编辑器
    editorContainer.style.display = 'block';
    editorContainer.style.opacity = '0';
    
    // 添加渐入动画
    setTimeout(() => {
        editorContainer.style.opacity = '1';
        editorContainer.style.transform = 'translateY(0)';
    }, 10);
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

// 初始化方向按钮
function initDirectionButtons() {
    const dirButtons = document.querySelectorAll('.direction-btn');
    const directionsInput = document.getElementById('gesture-directions');
    
    dirButtons.forEach(button => {
        button.addEventListener('click', () => {
            const direction = button.getAttribute('data-direction');
            const arrowDirection = DIRECTION_MAP[direction] || direction;
            
            if (directionsInput) {
                const currentVal = directionsInput.value;
                
                // 检查是否需要添加空格
                let newVal = '';
                if (currentVal && !currentVal.endsWith(' ')) {
                    newVal = currentVal + ' ' + arrowDirection;
                } else {
                    newVal = currentVal + arrowDirection;
                }
                
                directionsInput.value = newVal;
                validateDirections(newVal);
            }
        });
    });
    
    // 验证输入的方向
    if (directionsInput) {
        directionsInput.addEventListener('input', function() {
            validateDirections(this.value);
        });
    }
}

// 验证方向输入
function validateDirections(directions) {
    const validArrows = Object.values(DIRECTION_MAP);
    const validation = document.getElementById('directions-validation');
    
    if (!directions || directions.trim() === '') {
        validation.textContent = '';
        return true;
    }
    
    // 分割输入的方向
    const dirArray = directions.trim().split(/\s+/);
    
    // 检查每个方向是否有效
    for (const dir of dirArray) {
        if (!validArrows.includes(dir)) {
            validation.textContent = `无效的方向: ${dir}。请使用有效箭头符号。`;
            return false;
        }
    }
    
    // 检查至少有一个方向
    if (dirArray.length === 0) {
        validation.textContent = '请至少输入一个方向。';
        return false;
    }
    
    validation.textContent = '';
    return true;
}

// 初始化表单提交
function initGestureForm() {
    const form = document.getElementById('gesture-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 获取表单数据
        const name = document.getElementById('gesture-name').value.trim();
        let directions = document.getElementById('gesture-directions').value.trim();
        const action = document.getElementById('gesture-action').value.trim();
        
        // 验证
        if (!name) {
            showToast('请输入手势名称', 'error');
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
        
        // 发送到服务器
        fetch('/api/gestures', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                operation: operationType,
                old_name: currentGestureName,
                name: name,
                directions: directions,
                action: actionBase64
            })
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