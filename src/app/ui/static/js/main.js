// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
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
});

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
            if (confirm('确定要退出程序吗？')) {
                fetch('/api/exit', {
                    method: 'POST'
                });
            }
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
    
    if (runtimeElement || memoryUsageElement) {
        fetch('/api/system_info')
            .then(response => response.json())
            .then(data => {
                if (runtimeElement) {
                    runtimeElement.textContent = data.runtime;
                }
                if (memoryUsageElement) {
                    memoryUsageElement.textContent = data.memory_usage;
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
    
    // 范围滑块值实时显示
    rangeInputs.forEach(input => {
        const valueDisplay = input.parentElement.querySelector('.range-value');
        
        input.addEventListener('input', function() {
            valueDisplay.textContent = this.value;
        });
    });
    
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
                    alert('设置已保存');
                } else {
                    alert('保存失败: ' + data.message);
                }
            })
            .catch(error => {
                console.error('保存设置失败:', error);
                alert('保存设置失败，请重试');
            });
        });
    }
    
    // 重置按钮
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            if (confirm('确定要恢复默认设置吗？')) {
                fetch('/api/reset_settings', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('已恢复默认设置，页面将刷新');
                        window.location.reload();
                    } else {
                        alert('恢复默认设置失败: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('恢复默认设置失败:', error);
                    alert('恢复默认设置失败，请重试');
                });
            }
        });
    }
} 