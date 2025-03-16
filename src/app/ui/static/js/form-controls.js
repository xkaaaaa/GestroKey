/**
 * 表单控件增强脚本
 * 为复选框和单选框添加丝滑动画和交互效果
 */

// 自执行函数，避免变量污染全局作用域
(function() {
    // 记录日志
    function logDebug(message) {
        if (window.consoleLogger && typeof window.consoleLogger.log === 'function') {
            window.consoleLogger.log('表单控件', message);
        } else if (console && typeof console.log === 'function') {
            console.log('[表单控件]', message);
        }
    }

    /**
     * 初始化复选框组件
     */
    function initCheckboxes() {
        logDebug('初始化复选框组件');
        const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]');
        
        checkboxes.forEach(checkbox => {
            // 添加事件监听器
            checkbox.addEventListener('change', function(e) {
                // 创建涟漪动画效果
                createRippleEffect(this, '.checkbox-ripple');
                
                // 如果有回调函数，调用回调
                const dataCallback = this.getAttribute('data-callback');
                if (dataCallback && window[dataCallback] && typeof window[dataCallback] === 'function') {
                    window[dataCallback](this.checked, this.id);
                }
            });
            
            // 添加键盘支持
            checkbox.addEventListener('keydown', function(e) {
                if (e.key === ' ' || e.key === 'Enter') {
                    e.preventDefault();
                    this.checked = !this.checked;
                    
                    // 触发change事件
                    const event = new Event('change');
                    this.dispatchEvent(event);
                }
            });
        });
    }
    
    /**
     * 初始化单选框组件
     */
    function initRadioButtons() {
        logDebug('初始化单选框组件');
        const radios = document.querySelectorAll('.radio-group input[type="radio"]');
        
        radios.forEach(radio => {
            // 添加事件监听器
            radio.addEventListener('change', function(e) {
                // 创建涟漪动画效果
                createRippleEffect(this, '.radio-ripple');
                
                // 如果有回调函数，调用回调
                const dataCallback = this.getAttribute('data-callback');
                if (dataCallback && window[dataCallback] && typeof window[dataCallback] === 'function') {
                    window[dataCallback](this.value, this.name);
                }
            });
            
            // 添加键盘支持
            radio.addEventListener('keydown', function(e) {
                if (e.key === ' ' || e.key === 'Enter') {
                    e.preventDefault();
                    this.checked = true;
                    
                    // 触发change事件
                    const event = new Event('change');
                    this.dispatchEvent(event);
                }
            });
        });
    }
    
    /**
     * 创建涟漪动画效果
     * @param {HTMLElement} element - 触发元素
     * @param {string} rippleSelector - 涟漪元素的CSS选择器
     */
    function createRippleEffect(element, rippleSelector) {
        const ripple = element.parentNode.querySelector(rippleSelector);
        if (!ripple) return;
        
        // 先重置动画
        ripple.style.animation = 'none';
        
        // 强制回流后再添加动画
        void ripple.offsetWidth;
        
        // 添加动画
        ripple.style.animation = 'rippleEffect 0.6s ease forwards';
    }
    
    /**
     * 初始化所有自定义表单控件
     */
    function initFormControls() {
        try {
            logDebug('开始初始化表单控件');
            initCheckboxes();
            initRadioButtons();
            logDebug('表单控件初始化完成 - 优化间距布局');
        } catch (error) {
            logDebug(`表单控件初始化失败: ${error.message}`);
            console.error('表单控件初始化失败:', error);
        }
    }
    
    // 页面加载完成后或DOM内容加载后初始化
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(initFormControls, 1);
    } else {
        document.addEventListener('DOMContentLoaded', initFormControls);
    }
    
    // 将初始化函数暴露给全局作用域，以便可以在动态添加表单元素后重新初始化
    window.initFormControls = initFormControls;
})(); 