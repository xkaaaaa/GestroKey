// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 禁用右键菜单
    disableRightClick();
    
    // 初始化导航菜单
    initNavigation();
    
    // 初始化侧边栏折叠功能
    initSidebarCollapse();
    
    // 初始化图标交互效果
    initIconInteractions();
    
    // 初始化控制台页面功能
    if (document.querySelector('.console-page')) {
        initConsole();
    }
    
    // 初始化设置页面功能
    if (document.querySelector('.settings-page')) {
        initSettings();
    }
    
    // 创建全局提示框容器
    createGlobalToastContainer();
    
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
            // 如果点击的是当前激活的选项卡，则不执行任何操作
            if (this.classList.contains('active')) {
                e.preventDefault();
                return false;
            }
            
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
        // 添加鼠标悬停事件监听
        if (button.classList.contains('primary-btn')) {
            button.addEventListener('mouseenter', function() {
                // 记录主按钮悬停事件
                logToServer('用户界面', '主按钮悬停交互', 'info');
            });
        }
        
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

// 创建全局提示框容器
function createGlobalToastContainer() {
    // 检查是否已存在
    if (document.getElementById('global-toast-container')) return;
    
    // 创建容器
    const container = document.createElement('div');
    container.id = 'global-toast-container';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 10px;
        pointer-events: none;
    `;
    document.body.appendChild(container);
    
    // 创建样式
    const style = document.createElement('style');
    style.textContent = `
        #global-toast-container .toast {
            background-color: white;
            color: #333333;
            border-radius: 4px;
            padding: 12px 20px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
            opacity: 0;
            transform: translateX(30px);
            transition: opacity 0.3s, transform 0.3s;
            border-left: 4px solid #4A90E2;
            max-width: 300px;
            pointer-events: auto;
        }
        
        #global-toast-container .toast.show {
            opacity: 1;
            transform: translateX(0);
        }
        
        #global-toast-container .toast.success {
            border-left-color: #28a745;
        }
        
        #global-toast-container .toast.error {
            border-left-color: #dc3545;
        }
        
        #global-toast-container .toast.warning {
            border-left-color: #ffc107;
        }
        
        #global-toast-container .toast.info {
            border-left-color: #4A90E2;
        }
        
        #global-toast-container .toast.confirm {
            background-color: #f8f9fa;
            border-left-color: #6c757d;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
    `;
    document.head.appendChild(style);
}

// 显示全局提示框
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('global-toast-container');
    if (!container) return;
    
    // 创建提示框
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toast.style.color = '#333333';
    container.appendChild(toast);
    
    // 显示提示框（使用requestAnimationFrame确保DOM更新后再添加动画类）
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });
    });
    
    // 设置自动消失
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            container.removeChild(toast);
        }, 300); // 等待淡出动画完成
    }, duration);
    
    return toast;
}

// 显示全局确认对话框
function showConfirm(message, onConfirm, onCancel) {
    const container = document.getElementById('global-toast-container');
    if (!container) return;
    
    // 创建确认框
    const confirm = document.createElement('div');
    confirm.className = 'toast confirm';
    confirm.style.width = '280px';
    confirm.style.padding = '15px';
    confirm.style.backgroundColor = '#f8f9fa';
    confirm.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.3)';
    
    // 创建消息文本
    const messageEl = document.createElement('div');
    messageEl.style.marginBottom = '15px';
    messageEl.style.color = '#333333';
    messageEl.style.fontWeight = '500';
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
        font-weight: 500;
    `;
    
    // 创建确认按钮
    const confirmBtn = document.createElement('button');
    confirmBtn.textContent = '确定';
    confirmBtn.style.cssText = `
        padding: 5px 12px;
        border: none;
        border-radius: 4px;
        background-color: #4A90E2;
        color: white;
        cursor: pointer;
        font-weight: 500;
    `;
    
    // 添加按钮到容器
    buttonContainer.appendChild(cancelBtn);
    buttonContainer.appendChild(confirmBtn);
    confirm.appendChild(buttonContainer);
    
    // 添加确认框到容器
    container.appendChild(confirm);
    
    // 显示确认框
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            confirm.classList.add('show');
        });
    });
    
    // 绑定按钮事件
    cancelBtn.addEventListener('click', () => {
        confirm.classList.remove('show');
        setTimeout(() => {
            container.removeChild(confirm);
            if (typeof onCancel === 'function') {
                onCancel();
            }
        }, 300);
    });
    
    confirmBtn.addEventListener('click', () => {
        confirm.classList.remove('show');
        setTimeout(() => {
            container.removeChild(confirm);
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
    
    // 最小化按钮
    if (minimizeBtn) {
        // 设置按钮文本为"最小化到托盘"
        minimizeBtn.textContent = '最小化到托盘';
        
        minimizeBtn.addEventListener('click', function() {
            console.log('隐藏窗口到托盘');
            fetch('/api/minimize', {
                method: 'POST'
            })
            .then(response => {
                if (!response.ok) {
                    console.error('隐藏窗口到托盘失败');
                    showToast('隐藏窗口到托盘失败', 'error');
                }
            })
            .catch(error => {
                console.error('隐藏窗口到托盘请求错误:', error);
                showToast('隐藏窗口到托盘失败: ' + error.message, 'error');
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
        const min = parseFloat(input.min) || 0;
        const max = parseFloat(input.max) || 100;
        
        // 初始化滑动条填充进度
        updateSliderProgress(input);
        
        // 监听滑块值变化
        input.addEventListener('input', function() {
            // 更新显示值
            valueDisplay.textContent = this.value;
            
            // 更新滑动条填充进度
            updateSliderProgress(this);
            
            // 添加值更新动画效果
            valueDisplay.classList.add('updating');
            setTimeout(() => {
                valueDisplay.classList.remove('updating');
            }, 400);
        });
        
        // 滑块值确认变化时记录日志
        input.addEventListener('change', function() {
            // 记录滑动条值变化
            logToServer('用户界面', `${this.id}设置值改为${this.value}`, 'info');
        });
    });
    
    // 更新滑动条填充进度
    function updateSliderProgress(slider) {
        const min = parseFloat(slider.min) || 0;
        const max = parseFloat(slider.max) || 100;
        const val = parseFloat(slider.value);
        const percentage = ((val - min) * 100) / (max - min);
        
        // 使用CSS变量设置填充进度
        slider.style.setProperty('--percent', `${percentage}%`);
    }
    
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
            
            // 显示保存中提示
            showToast('正在保存设置...', 'info');
            
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
                    // 禁用表单按钮短暂时间，避免重复提交
                    const submitBtn = settingsForm.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.disabled = true;
                        setTimeout(() => {
                            submitBtn.disabled = false;
                        }, 1000);
                    }
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
                // 显示重置中提示
                showToast('正在恢复默认设置...', 'info');
                
                fetch('/api/reset_settings', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showToast('已恢复默认设置', 'success');
                        
                        // 获取最新设置并更新表单
                        fetch('/api/system_info')
                            .then(response => response.json())
                            .then(infoData => {
                                // 更新表单字段值
                                updateSettingsFormValues(infoData);
                            })
                            .catch(error => {
                                console.error('获取设置数据失败:', error);
                                // 如果无法获取最新设置，才刷新页面
                                setTimeout(() => {
                                    window.location.reload();
                                }, 1500);
                            });
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
    
    // 更新设置表单值的函数
    function updateSettingsFormValues(data) {
        const settings = data.settings || {};
        
        // 遍历表单元素并更新值
        for (const [key, value] of Object.entries(settings)) {
            const input = document.getElementById(key);
            if (!input) continue;
            
            // 根据输入类型设置值
            if (input.type === 'checkbox') {
                input.checked = value;
            } else if (input.type === 'range') {
                input.value = value;
                // 更新显示的值和进度条
                const valueDisplay = input.parentElement.querySelector('.range-value');
                if (valueDisplay) valueDisplay.textContent = value;
                updateSliderProgress(input);
            } else {
                input.value = value;
            }
        }
    }
}

// 初始化图标交互效果
function initIconInteractions() {
    // 设置选项卡点击旋转效果
    const settingsNavItem = document.querySelector('.nav-item[data-page="settings"]');
    const settingsIcon = settingsNavItem ? settingsNavItem.querySelector('.icon i') : null;
    
    if (settingsNavItem && settingsIcon) {
        // 跟踪鼠标是否悬停在选项卡上
        let isHovering = false;
        
        // 监听鼠标进入
        settingsNavItem.addEventListener('mouseenter', function() {
            isHovering = true;
        });
        
        // 监听鼠标离开
        settingsNavItem.addEventListener('mouseleave', function() {
            isHovering = false;
        });
        
        // 为整个设置选项卡添加点击事件
        settingsNavItem.addEventListener('click', function(e) {
            // 如果已经在设置页面（有active类），则不执行旋转动画
            if (this.classList.contains('active')) {
                return;
            }
            
            // 记录日志
            logToServer('用户界面', '设置选项卡点击', 'info');
            
            // 防止快速连续点击
            if (settingsIcon.classList.contains('icon-spin')) {
                return;
            }
            
            // 添加旋转动画类
            settingsIcon.classList.add('icon-spin');
            
            // 动画完成后移除类
            setTimeout(() => {
                settingsIcon.classList.remove('icon-spin');
                
                // 如果此时鼠标仍然悬停在选项卡上，确保应用悬停样式
                if (isHovering && !settingsNavItem.classList.contains('active')) {
                    // 触发一次鼠标进入事件以重新应用悬停样式
                    settingsNavItem.dispatchEvent(new MouseEvent('mouseenter'));
                }
            }, parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--spin-duration')) * 1000);
        });
    }
}

// 向服务器发送日志
function logToServer(module, message, level = 'info') {
    fetch('/api/log', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            module: module,
            message: message,
            level: level
        })
    }).catch(err => console.error('发送日志失败:', err));
} 