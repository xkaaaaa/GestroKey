// 工具函数库

/**
 * 显示通知提示框
 * @param {string} message - 通知信息
 * @param {string} type - 通知类型: 'success', 'error', 'warning', 'info'
 * @param {number} duration - 显示持续时间（毫秒）
 */
function showToast(message, type = 'info', duration = 3000) {
    // 检查是否存在toast容器，如果不存在则创建
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // 根据类型添加图标
    let icon = '';
    switch (type) {
        case 'success':
            icon = '<i class="fas fa-check-circle"></i>';
            break;
        case 'error':
            icon = '<i class="fas fa-times-circle"></i>';
            break;
        case 'warning':
            icon = '<i class="fas fa-exclamation-triangle"></i>';
            break;
        case 'info':
        default:
            icon = '<i class="fas fa-info-circle"></i>';
            break;
    }
    
    // 设置toast内容
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
    `;
    
    // 添加到容器中
    toastContainer.appendChild(toast);
    
    // 重新调整所有toast的位置
    const allToasts = toastContainer.querySelectorAll('.toast');
    let topOffset = 20;
    
    allToasts.forEach((t) => {
        if (t !== toast) {
            const height = t.offsetHeight;
            topOffset += height + 10; // 10px的间距
        }
    });
    
    // 设置新toast的初始位置
    toast.style.transform = `translateY(${topOffset}px) translateX(120%)`;
    
    // 显示toast，添加动画
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // 设置自动移除
    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('fade-out');
        
        // 动画结束后移除元素并重新排列其他toast
        setTimeout(() => {
            const height = toast.offsetHeight + 10; // 高度 + 间距
            const nextToasts = Array.from(toastContainer.querySelectorAll('.toast')).filter(t => {
                const tTop = parseInt(t.style.transform.match(/translateY\((\d+)px\)/)[1], 10);
                return tTop > parseInt(toast.style.transform.match(/translateY\((\d+)px\)/)[1], 10);
            });
            
            nextToasts.forEach(t => {
                const currentTransform = t.style.transform;
                const currentTop = parseInt(currentTransform.match(/translateY\((\d+)px\)/)[1], 10);
                const newTop = currentTop - height;
                const newTransform = currentTransform.replace(/translateY\(\d+px\)/, `translateY(${newTop}px)`);
                t.style.transform = newTransform;
            });
            
            toastContainer.removeChild(toast);
            
            // 如果容器为空，也移除容器
            if (toastContainer.children.length === 0) {
                document.body.removeChild(toastContainer);
            }
        }, 300);
    }, duration);
}

/**
 * 显示确认对话框
 * @param {string} message - 确认信息
 * @param {Function} onConfirm - 确认回调函数
 * @param {Function} onCancel - 取消回调函数
 */
function showConfirm(message, onConfirm, onCancel = null) {
    // 检查是否已存在对话框
    let modal = document.getElementById('confirm-modal');
    let overlay = document.getElementById('confirm-overlay');

    if (modal) {
        document.body.removeChild(modal);
    }

    if (overlay) {
        document.body.removeChild(overlay);
    }

    // 创建遮罩层
    overlay = document.createElement('div');
    overlay.id = 'confirm-overlay';
    overlay.className = 'overlay';

    // 创建对话框
    modal = document.createElement('div');
    modal.id = 'confirm-modal';
    modal.className = 'modal';

    // 设置对话框内容
    modal.innerHTML = `
        <div class="modal-header">
            <h3>确认操作</h3>
            <button id="modal-close-btn" class="modal-close-btn">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="modal-body">
            <p>${message}</p>
        </div>
        <div class="modal-footer">
            <button id="modal-cancel-btn" class="secondary-btn">取消</button>
            <button id="modal-confirm-btn" class="primary-btn">确认</button>
        </div>
    `;

    // 添加到文档中
    document.body.appendChild(overlay);
    document.body.appendChild(modal);

    // 显示对话框
    setTimeout(() => {
        overlay.classList.add('active');
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // 防止背景滚动
    }, 10);

    // 处理ESC键关闭对话框
    function handleEscKey(e) {
        if (e.key === 'Escape') {
            closeModal();
            if (typeof onCancel === 'function') {
                onCancel();
            }
        }
    }

    // 关闭对话框的函数
    function closeModal() {
        modal.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = ''; // 恢复背景滚动
        
        document.removeEventListener('keydown', handleEscKey);

        // 动画结束后移除元素
        setTimeout(() => {
            if (document.body.contains(modal)) {
                document.body.removeChild(modal);
            }
            if (document.body.contains(overlay)) {
                document.body.removeChild(overlay);
            }
        }, 300);
    }

    // 绑定事件
    const confirmBtn = document.getElementById('modal-confirm-btn');
    const cancelBtn = document.getElementById('modal-cancel-btn');
    const closeBtn = document.getElementById('modal-close-btn');

    // 确认按钮事件
    confirmBtn.addEventListener('click', function() {
        closeModal();
        if (typeof onConfirm === 'function') {
            onConfirm();
        }
    });

    // 取消按钮事件
    cancelBtn.addEventListener('click', function() {
        closeModal();
        if (typeof onCancel === 'function') {
            onCancel();
        }
    });
    
    // 关闭按钮事件
    closeBtn.addEventListener('click', function() {
        closeModal();
        if (typeof onCancel === 'function') {
            onCancel();
        }
    });

    // 点击遮罩层关闭
    overlay.addEventListener('click', function(e) {
        if (e.target === overlay) {
            closeModal();
            if (typeof onCancel === 'function') {
                onCancel();
            }
        }
    });

    // 添加ESC键监听
    document.addEventListener('keydown', handleEscKey);
} 