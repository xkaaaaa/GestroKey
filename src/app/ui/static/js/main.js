// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 禁用右键菜单
    disableRightClick();
    
    // 初始化导航菜单
    initNavigation();
    
    // 初始化控制台页面功能
    if (document.querySelector('.console-page')) {
        initConsole();
    }
    
    // 初始化设置页面功能
    if (document.querySelector('.settings-page')) {
        initSettings();
    }
    
    // 创建提示框组件
    createToastComponent();
});

// 禁用右键菜单
function disableRightClick() {
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        return false;
    });
    
    // 禁用选择文本
    document.addEventListener('selectstart', function(e) {
        // 允许输入框中的选择
        if (e.target.tagName === 'INPUT' || 
            e.target.tagName === 'TEXTAREA' || 
            e.target.isContentEditable) {
            return true;
        }
        e.preventDefault();
        return false;
    });
}

// 创建自定义提示框组件
function createToastComponent() {
    // 创建提示框容器
    const toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
    `;
    document.body.appendChild(toastContainer);
    
    // 覆盖原生alert
    window.originalAlert = window.alert;
    window.alert = function(message) {
        showToast(message);
    };
}

// 显示提示框
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    // 创建提示框元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        background-color: white;
        color: #333;
        padding: 12px 20px;
        border-radius: 4px;
        margin-top: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        max-width: 300px;
        opacity: 0;
        transition: opacity 0.3s;
        border-left: 4px solid var(--primary-color);
        font-size: 14px;
        word-break: break-word;
    `;
    
    // 根据类型设置边框颜色
    if (type === 'success') {
        toast.style.borderLeftColor = '#28a745';
    } else if (type === 'error') {
        toast.style.borderLeftColor = '#dc3545';
    } else if (type === 'warning') {
        toast.style.borderLeftColor = '#ffc107';
    }
    
    toast.textContent = message;
    toastContainer.appendChild(toast);
    
    // 显示提示框
    setTimeout(() => {
        toast.style.opacity = '1';
    }, 10);
    
    // 自动关闭提示框
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 300);
    }, duration);
    
    return toast;
}

// 显示确认对话框
function showConfirm(message, onConfirm, onCancel) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    // 创建确认框元素
    const confirm = document.createElement('div');
    confirm.className = 'toast toast-confirm';
    confirm.style.cssText = `
        background-color: white;
        color: #333;
        padding: 15px 20px;
        border-radius: 4px;
        margin-top: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        max-width: 300px;
        opacity: 0;
        transition: opacity 0.3s;
        border-left: 4px solid #ffc107;
        font-size: 14px;
        word-break: break-word;
    `;
    
    // 创建消息文本
    const messageEl = document.createElement('div');
    messageEl.style.marginBottom = '15px';
    messageEl.textContent = message;
    confirm.appendChild(messageEl);
    
    // 创建按钮容器
    const buttonContainer = document.createElement('div');
    buttonContainer.style.cssText = `
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    `;
    
    // 创建取消按钮
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = '取消';
    cancelBtn.style.cssText = `
        padding: 5px 12px;
        border: none;
        border-radius: 4px;
        background-color: #6c757d;
        color: white;
        cursor: pointer;
    `;
    
    // 创建确认按钮
    const confirmBtn = document.createElement('button');
    confirmBtn.textContent = '确定';
    confirmBtn.style.cssText = `
        padding: 5px 12px;
        border: none;
        border-radius: 4px;
        background-color: var(--primary-color);
        color: white;
        cursor: pointer;
    `;
    
    // 添加按钮到容器
    buttonContainer.appendChild(cancelBtn);
    buttonContainer.appendChild(confirmBtn);
    confirm.appendChild(buttonContainer);
    
    // 添加确认框到容器
    toastContainer.appendChild(confirm);
    
    // 显示确认框
    setTimeout(() => {
        confirm.style.opacity = '1';
    }, 10);
    
    // 绑定按钮事件
    cancelBtn.addEventListener('click', () => {
        confirm.style.opacity = '0';
        setTimeout(() => {
            toastContainer.removeChild(confirm);
            if (typeof onCancel === 'function') {
                onCancel();
            }
        }, 300);
    });
    
    confirmBtn.addEventListener('click', () => {
        confirm.style.opacity = '0';
        setTimeout(() => {
            toastContainer.removeChild(confirm);
            if (typeof onConfirm === 'function') {
                onConfirm();
            }
        }, 300);
    });
    
    return confirm;
}

// 导航菜单初始化
function initNavigation() {
    // 高亮当前页面对应的导航项
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
        }
    });
}

// 控制台页面功能初始化
function initConsole() {
    const toggleBtn = document.getElementById('toggle-btn');
    const minimizeBtn = document.getElementById('minimize-btn');
    const exitBtn = document.getElementById('exit-btn');
    
    // 绘画开关按钮
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            // 通过fetch API调用后端接口
            fetch('/api/toggle_painting', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 更新UI状态
                    const statusIndicator = document.querySelector('.status-indicator');
                    const statusText = document.getElementById('status-text');
                    
                    if (data.is_running) {
                        statusIndicator.classList.add('active');
                        statusText.textContent = '运行中';
                        toggleBtn.textContent = '停止绘画';
                    } else {
                        statusIndicator.classList.remove('active');
                        statusText.textContent = '已停止';
                        toggleBtn.textContent = '开始绘画';
                    }
                }
            })
            .catch(error => {
                console.error('操作失败:', error);
            });
        });
    }
    
    // 最小化到托盘按钮
    if (minimizeBtn) {
        minimizeBtn.addEventListener('click', function() {
            fetch('/api/minimize', {
                method: 'POST'
            });
        });
    }
    
    // 退出程序按钮
    if (exitBtn) {
        exitBtn.addEventListener('click', function() {
            showConfirm('确定要退出程序吗？', function() {
                fetch('/api/exit', {
                    method: 'POST'
                });
            });
        });
    }
    
    // 定时更新系统信息
    updateSystemInfo();
    setInterval(updateSystemInfo, 5000);
}

// 更新系统信息
function updateSystemInfo() {
    const runtimeElement = document.getElementById('runtime');
    const memoryUsageElement = document.getElementById('memory-usage');
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.getElementById('status-text');
    const toggleBtn = document.getElementById('toggle-btn');
    
    if (runtimeElement || memoryUsageElement || statusIndicator) {
        fetch('/api/system_info')
            .then(response => response.json())
            .then(data => {
                if (runtimeElement) {
                    runtimeElement.textContent = data.runtime;
                }
                if (memoryUsageElement) {
                    memoryUsageElement.textContent = data.memory_usage;
                }
                // 更新绘画状态
                if (statusIndicator && statusText && toggleBtn) {
                    if (data.is_painting_running) {
                        statusIndicator.classList.add('active');
                        statusText.textContent = '运行中';
                        toggleBtn.textContent = '停止绘画';
                    } else {
                        statusIndicator.classList.remove('active');
                        statusText.textContent = '已停止';
                        toggleBtn.textContent = '开始绘画';
                    }
                }
            })
            .catch(error => {
                console.error('获取系统信息失败:', error);
            });
    }
}

// 设置页面功能初始化
function initSettings() {
    const settingsForm = document.getElementById('settings-form');
    const resetBtn = document.getElementById('reset-btn');
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    const startWithSystemCheckbox = document.getElementById('start_with_system');
    
    // 范围滑块值实时显示
    rangeInputs.forEach(input => {
        const valueDisplay = input.parentElement.querySelector('.range-value');
        
        input.addEventListener('input', function() {
            valueDisplay.textContent = this.value;
        });
    });
    
    // 开机自启动复选框单独处理
    if (startWithSystemCheckbox) {
        // 获取当前自启动状态
        fetch('/api/system_info')
            .then(response => response.json())
            .then(data => {
                startWithSystemCheckbox.checked = data.autostart_enabled;
            })
            .catch(error => {
                console.error('获取自启动状态失败:', error);
            });
            
        // 监听复选框变更
        startWithSystemCheckbox.addEventListener('change', function() {
            const enabled = this.checked;
            
            fetch('/api/autostart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ enabled: enabled })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 更新复选框状态以匹配实际设置
                    this.checked = data.enabled;
                } else {
                    showToast('设置开机自启动失败: ' + data.message, 'error');
                    // 恢复复选框状态
                    this.checked = !enabled;
                }
            })
            .catch(error => {
                console.error('设置开机自启动失败:', error);
                showToast('设置开机自启动失败，请重试', 'error');
                // 恢复复选框状态
                this.checked = !enabled;
            });
        });
    }
    
    // 设置表单提交
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const settings = {};
            
            // 转换表单数据为JSON对象
            for (const [key, value] of formData.entries()) {
                if (key === 'enable_advanced_brush' || key === 'enable_auto_smoothing' || 
                    key === 'force_topmost' || key === 'enable_hardware_acceleration' || 
                    key === 'start_with_system') {
                    settings[key] = true; // 复选框被选中时才会出现在formData中
                } else if (key === 'base_width' || key === 'min_width' || key === 'max_width') {
                    settings[key] = parseInt(value);
                } else if (key === 'speed_factor') {
                    settings[key] = parseFloat(value);
                } else {
                    settings[key] = value;
                }
            }
            
            // 处理未选中的复选框
            const checkboxes = ['enable_advanced_brush', 'enable_auto_smoothing', 
                               'force_topmost', 'enable_hardware_acceleration', 'start_with_system'];
            
            checkboxes.forEach(key => {
                if (!settings.hasOwnProperty(key)) {
                    settings[key] = false;
                }
            });
            
            // 发送到后端
            fetch('/api/save_settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('设置已保存', 'success');
                } else {
                    showToast('保存失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                console.error('保存设置失败:', error);
                showToast('保存设置失败，请重试', 'error');
            });
        });
    }
    
    // 重置按钮
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            showConfirm('确定要恢复默认设置吗？', function() {
                fetch('/api/reset_settings', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showToast('已恢复默认设置，页面将刷新', 'success');
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        showToast('恢复默认设置失败: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('恢复默认设置失败:', error);
                    showToast('恢复默认设置失败，请重试', 'error');
                });
            });
        });
    }
} 