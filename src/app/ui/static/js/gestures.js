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
    
    // 注册代码示例插入事件
    document.querySelectorAll('.insert-example').forEach(button => {
        button.addEventListener('click', function() {
            insertCodeExample(this.dataset.example);
        });
    });

    // 初始加载手势列表
    loadGesturesList();
    
    // 初始化代码编辑器
    initCodeEditorForGestures();
});

// 初始化代码编辑器
let codeEditor = null;
function initCodeEditorForGestures() {
    // 等待CodeMirror完全加载
    if (typeof CodeMirror === 'undefined' || !window.CodeEditorManager) {
        setTimeout(initCodeEditorForGestures, 100);
        return;
    }
    
    // 获取编辑器元素
    const editorTextarea = document.getElementById('gesture-action');
    if (!editorTextarea) return;
    
    // 确保textarea有唯一ID
    if (!editorTextarea.id) {
        editorTextarea.id = 'gesture-action-' + Date.now();
    }
    
    // 使用CodeEditorManager创建编辑器
    codeEditor = window.CodeEditorManager.create(editorTextarea, {
        mode: 'python',
        lineNumbers: true,
        theme: 'dracula',
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true
    });
    
    // 添加事件监听
    if (codeEditor) {
        // 当编辑器内容变化时，更新隐藏的textarea
        codeEditor.on('change', function() {
            editorTextarea.value = codeEditor.getValue();
        });
    }
}

// 插入代码示例
function insertCodeExample(code) {
    if (codeEditor) {
        // 获取当前光标位置
        const cursor = codeEditor.getCursor();
        // 在光标位置插入代码
        codeEditor.replaceRange(code, cursor);
        // 聚焦编辑器
        codeEditor.focus();
        // 显示成功提示
        showToast('示例代码已插入', 'success');
    } else {
        // 兼容旧版本
        const textarea = document.getElementById('gesture-action');
        if (textarea) {
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            textarea.value = textarea.value.substring(0, start) + code + textarea.value.substring(end);
            textarea.focus();
            showToast('示例代码已插入', 'success');
        }
    }
}

// 加载手势列表（用于局部刷新）
function loadGesturesList() {
    fetch('/api/gestures')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateGesturesListUI(data.gestures);
            } else {
                showToast('加载手势列表失败', 'error');
            }
        })
        .catch(error => {
            console.error('加载手势列表失败:', error);
            showToast('加载手势列表失败，请重试', 'error');
        });
}

// 更新手势列表UI
function updateGesturesListUI(gestures) {
    const gesturesList = document.querySelector('.gesture-list');
    if (!gesturesList) return;

    // 先清空现有列表
    gesturesList.innerHTML = '';

    // 如果没有手势，显示提示信息
    if (Object.keys(gestures).length === 0) {
        gesturesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-hand-pointer"></i>
                <p>暂无手势，点击"添加手势"创建第一个手势</p>
            </div>
        `;
        return;
    }

    // 添加所有手势到列表
    for (const [name, gesture] of Object.entries(gestures)) {
        gesturesList.innerHTML += `
            <div class="gesture-item" data-name="${name}" data-directions="${gesture.directions}" data-action="${btoa(gesture.action)}">
                <div class="gesture-info">
                    <h3 class="gesture-name">${name}</h3>
                    <div class="gesture-details">
                        <span class="gesture-directions">方向: ${gesture.directions}</span>
                    </div>
                </div>
                <div class="gesture-actions">
                    <button class="icon-btn edit-gesture-btn" title="编辑">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="icon-btn delete-gesture-btn" title="删除">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // 重新绑定事件
    bindGestureItemEvents();
}

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

// 初始化手势编辑器
function initGestureEditor() {
    // 获取DOM元素
    const addGestureBtn = document.getElementById('add-gesture-btn');
    const cancelEditBtn = document.getElementById('cancel-edit-btn');
    const gestureForm = document.getElementById('gesture-form');
    const directionBtns = document.querySelectorAll('.direction-btn');
    const clearDirectionBtn = document.querySelector('.clear-direction-btn');
    const testGestureBtn = document.getElementById('test-gesture-btn');
    
    // 添加手势按钮事件
    if (addGestureBtn) {
        addGestureBtn.addEventListener('click', () => {
            showGestureEditor('add');
        });
    }
    
    // 取消编辑按钮事件
    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', hideGestureEditor);
    }
    
    // 方向按钮事件
    directionBtns.forEach(btn => {
        if (!btn.classList.contains('clear-direction-btn')) {
            btn.addEventListener('click', () => {
                const direction = btn.textContent.trim();
                const directionsInput = document.getElementById('gesture-directions');
                directionsInput.value += direction;
            });
        }
    });
    
    // 清除方向按钮事件
    if (clearDirectionBtn) {
        clearDirectionBtn.addEventListener('click', () => {
            const directionsInput = document.getElementById('gesture-directions');
            if (directionsInput.value.length > 0) {
                directionsInput.value = directionsInput.value.slice(0, -1);
            }
        });
    }
    
    // 测试手势按钮事件
    if (testGestureBtn) {
        testGestureBtn.addEventListener('click', () => {
            // 获取当前代码
            let code;
            if (codeEditor) {
                code = codeEditor.getValue();
            } else {
                code = document.getElementById('gesture-action').value;
            }
            
            if (!code.trim()) {
                showToast('请先输入要测试的代码', 'warning');
                return;
            }
            
            // 发送测试请求
            fetch('/api/test_gesture', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action: btoa(code) })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('代码测试成功', 'success');
                } else {
                    showToast(`测试失败: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                console.error('测试手势失败:', error);
                showToast('测试请求失败，请重试', 'error');
            });
        });
    }
    
    // 表单提交事件
    if (gestureForm) {
        gestureForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 表单验证
            const nameInput = document.getElementById('gesture-name');
            const directionsInput = document.getElementById('gesture-directions');
            const operationInput = document.querySelector('input[name="operation"]');
            
            // 获取代码编辑器内容
            let actionCode;
            if (codeEditor) {
                actionCode = codeEditor.getValue();
            } else {
                actionCode = document.getElementById('gesture-action').value;
            }
            
            if (!actionCode.trim()) {
                showToast('请输入执行动作代码', 'warning');
                return;
            }
            
            if (!directionsInput.value) {
                showToast('请添加至少一个方向', 'warning');
                return;
            }
            
            // 准备提交数据
            const formData = new FormData(this);
            const data = {
                operation: operationInput ? operationInput.value : 'add',
                directions: directionsInput.value,
                action: btoa(actionCode) // Base64编码
            };
            
            // 添加手势名称（如果存在）
            if (nameInput && data.operation === 'add') {
                data.name = nameInput.value;
            } else if (data.operation === 'update') {
                data.name = document.querySelector('input[name="name"]').value;
            }
            
            // 发送到服务器
            fetch('/api/gestures', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    hideGestureEditor();
                    showToast(data.operation === 'add' ? '手势添加成功' : '手势更新成功', 'success');
                    
                    // 刷新手势列表
                    loadGesturesList();
                } else {
                    showToast(`操作失败: ${result.message}`, 'error');
                }
            })
            .catch(error => {
                console.error('保存手势失败:', error);
                showToast('保存失败，请重试', 'error');
            });
        });
    }
    
    // 绑定手势项事件
    bindGestureItemEvents();
}

// 绑定手势项事件
function bindGestureItemEvents() {
    // 编辑按钮事件
    document.querySelectorAll('.edit-gesture-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const item = this.closest('.gesture-item');
            const name = item.getAttribute('data-name');
            const directions = item.getAttribute('data-directions');
            const action = item.getAttribute('data-action');
            
            showGestureEditor('edit', {
                name: name,
                directions: directions,
                action: action
            });
        });
    });
    
    // 删除按钮事件
    document.querySelectorAll('.delete-gesture-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const item = this.closest('.gesture-item');
            const name = item.getAttribute('data-name');
            
            showConfirm(`确定要删除手势 "${name}" 吗？`, () => {
                deleteGesture(name);
            });
        });
    });
}

// 删除手势
function deleteGesture(name) {
    fetch('/api/gestures', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            operation: 'delete',
            name: name
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('手势已删除', 'success');
            loadGesturesList();
        } else {
            showToast(`删除失败: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('删除手势失败:', error);
        showToast('删除失败，请重试', 'error');
    });
}

// 显示手势编辑器
function showGestureEditor(mode = 'add', data = null) {
    const editorContainer = document.getElementById('gesture-editor-container');
    
    // 处理编辑模式
    if (mode === 'edit' && data) {
        document.getElementById('editor-title').textContent = '编辑手势';
        
        // 创建或更新隐藏字段
        let operationInput = document.querySelector('input[name="operation"]');
        if (!operationInput) {
            operationInput = document.createElement('input');
            operationInput.type = 'hidden';
            operationInput.name = 'operation';
            document.getElementById('gesture-form').appendChild(operationInput);
        }
        operationInput.value = 'update';
        
        // 创建或更新隐藏的名称字段
        let nameInput = document.querySelector('input[name="name"]');
        if (!nameInput) {
            nameInput = document.createElement('input');
            nameInput.type = 'hidden';
            nameInput.name = 'name';
            document.getElementById('gesture-form').appendChild(nameInput);
        }
        nameInput.value = data.name || '';
        
        // 填充表单数据
        document.getElementById('gesture-directions').value = data.directions || '';
        
        // 设置动作代码 - 使用代码编辑器
        const actionCode = atob(data.action || '');
        if (codeEditor) {
            codeEditor.setValue(actionCode);
        } else {
            document.getElementById('gesture-action').value = actionCode;
        }
        
        // 更新名称容器显示
        const nameContainer = document.getElementById('gesture-name-container');
        nameContainer.innerHTML = `
            <label>手势名称</label>
            <div class="input-readonly">
                <span>${data.name || ''}</span>
                <div class="input-icon"><i class="fas fa-lock"></i></div>
            </div>
            <div class="input-helper-text">编辑模式下无法修改名称</div>
        `;
    } else {
        // 添加模式
        document.getElementById('editor-title').textContent = '添加手势';
        
        // 创建或更新隐藏字段
        let operationInput = document.querySelector('input[name="operation"]');
        if (!operationInput) {
            operationInput = document.createElement('input');
            operationInput.type = 'hidden';
            operationInput.name = 'operation';
            document.getElementById('gesture-form').appendChild(operationInput);
        }
        operationInput.value = 'add';
        
        // 重置表单
        document.getElementById('gesture-form').reset();
        document.getElementById('gesture-directions').value = '';
        
        // 清除代码编辑器内容
        if (codeEditor) {
            codeEditor.setValue('');
        } else {
            document.getElementById('gesture-action').value = '';
        }
        
        // 更新名称容器显示
        const nameContainer = document.getElementById('gesture-name-container');
        nameContainer.innerHTML = `
            <label for="gesture-name">手势名称</label>
            <input type="text" id="gesture-name" name="name" required placeholder="输入手势名称">
            <div class="input-helper-text">名称必须唯一，保存后无法修改</div>
        `;
    }
    
    // 显示编辑器
    editorContainer.style.display = 'block';
    
    // 刷新代码编辑器，确保正常显示
    if (codeEditor) {
        setTimeout(() => {
            codeEditor.refresh();
            codeEditor.focus();
        }, 50);
    }
}

// 隐藏手势编辑器
function hideGestureEditor() {
    const editorContainer = document.getElementById('gesture-editor-container');
    editorContainer.style.display = 'none';
    
    // 重置方向序列
    document.getElementById('gesture-directions').value = '';
    
    // 重置代码编辑器
    if (codeEditor) {
        codeEditor.setValue('');
    } else {
        document.getElementById('gesture-action').value = '';
    }
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
                // 关闭编辑器
                hideGestureEditor();
                // 重新加载手势列表（局部刷新）
                loadGesturesList();
            } else {
                showToast(`操作失败: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('保存手势失败:', error);
            showToast('操作失败，请重试', 'error');
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