// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 禁用右键菜单
    disableRightClick();
    
    // 初始化导航菜单
    initNavigation();
    
    // 初始化侧边栏折叠功能
    initSidebarCollapse();
    
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
    
    // 添加页面过渡动画
    addPageTransitionEffects();
    
    // 添加按钮点击波纹效果
    addButtonRippleEffect();
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

// 添加页面过渡动画
function addPageTransitionEffects() {
    // 为内容容器添加初始动画
    const contentContainer = document.getElementById('content-container');
    if (contentContainer) {
        contentContainer.style.opacity = '0';
        contentContainer.style.transform = 'translateY(20px)';
        contentContainer.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        // 延迟显示内容，创建淡入效果
        setTimeout(() => {
            contentContainer.style.opacity = '1';
            contentContainer.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // 为导航链接添加页面过渡效果
    const navLinks = document.querySelectorAll('.nav-item');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // 只处理同域名下的链接
            if (this.hostname === window.location.hostname) {
                e.preventDefault();
                
                // 淡出当前页面
                if (contentContainer) {
                    contentContainer.style.opacity = '0';
                    contentContainer.style.transform = 'translateY(20px)';
                    
                    // 延迟导航，等待动画完成
                    setTimeout(() => {
                        window.location.href = this.href;
                    }, 300);
                } else {
                    window.location.href = this.href;
                }
            }
        });
    });
}

// 添加按钮点击波纹效果
function addButtonRippleEffect() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // 创建波纹元素
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            
            // 设置波纹位置
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            // 设置波纹样式
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            // 添加波纹到按钮
            this.appendChild(ripple);
            
            // 移除波纹
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // 添加波纹样式
    const style = document.createElement('style');
    style.textContent = `
        .btn {
            position: relative;
            overflow: hidden;
        }
        .ripple-effect {
            position: absolute;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.4);
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }
        @keyframes ripple {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
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

// 显示提示框样式的确认对话框
function showToastConfirm(message, onConfirm, onCancel) {
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

// 初始化侧边栏折叠功能
function initSidebarCollapse() {
    const sidebar = document.getElementById('sidebar');
    const toggleButton = document.getElementById('sidebar-toggle');
    
    if (!sidebar || !toggleButton) return;
    
    // 从本地存储中读取侧边栏状态
    const sidebarCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
    
    // 设置初始状态
    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
    }
    
    // 添加切换按钮点击事件
    toggleButton.addEventListener('click', function() {
        // 切换侧边栏折叠状态
        sidebar.classList.toggle('collapsed');
        
        // 记录状态到本地存储
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebar_collapsed', isCollapsed);
        
        // 记录侧边栏状态变化
        const logMessage = isCollapsed ? '侧边栏已折叠' : '侧边栏已展开';
        
        // 发送日志到服务器
        fetch('/api/log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: logMessage,
                level: 'info',
                module: 'ui'
            })
        }).catch(error => {
            console.error('日志记录失败:', error);
        });
    });
    
    // 为导航项添加提示工具（当侧边栏折叠时）
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        const text = item.querySelector('.text').textContent;
        item.setAttribute('title', text);
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
            // 使用utils.js中的showConfirm函数，它会创建一个模态对话框而非toast
            // 这个模态对话框不会自动消失，必须用户手动点击按钮关闭
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
                // 恢复复选框状态
                this.checked = !enabled;
                showToast('设置开机自启动失败', 'error');
            });
        });
    }
    
    // 设置表单提交
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 收集表单数据
            const formData = new FormData(this);
            const settings = {};
            
            // 转换为JSON对象
            for (const [key, value] of formData.entries()) {
                if (key === 'enable_advanced_brush' || key === 'enable_auto_smoothing' || 
                    key === 'force_topmost' || key === 'enable_hardware_acceleration') {
                    settings[key] = value === 'on';
                } else if (key === 'speed_factor' || key === 'base_width' || 
                           key === 'min_width' || key === 'max_width') {
                    settings[key] = parseFloat(value);
                } else {
                    settings[key] = value;
                }
            }
            
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
                    showToast('保存设置失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                console.error('保存设置失败:', error);
                showToast('保存设置失败', 'error');
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
                    showToast('恢复默认设置失败', 'error');
                });
            });
        });
    }
} 