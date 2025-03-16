/**
 * 高级代码编辑器组件
 * 基于 CodeMirror 实现，支持语法高亮、行号、自动缩进等功能
 */

// 编辑器实例集合
const editors = new Map();

// 初始化代码编辑器
function initCodeEditor() {
    // 加载 CodeMirror 样式
    loadStylesheet('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/codemirror.min.css');
    loadStylesheet('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/theme/dracula.min.css');
    loadStylesheet('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/addon/hint/show-hint.min.css');
    
    // 加载 CodeMirror 脚本
    loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/codemirror.min.js', () => {
        // 加载扩展和模式
        const scripts = [
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/mode/javascript/javascript.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/mode/python/python.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/addon/edit/matchbrackets.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/addon/edit/closebrackets.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/addon/comment/comment.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/addon/hint/show-hint.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/addon/hint/javascript-hint.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.3/addon/selection/active-line.min.js'
        ];
        
        loadScriptsSequentially(scripts, initializeEditors);
    });
    
    // 注册事件 - 点击扩展/折叠按钮
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('code-editor-expand-btn')) {
            toggleEditorExpansion(e.target);
        }
    });
}

// 按顺序加载脚本
function loadScriptsSequentially(scripts, callback, index = 0) {
    if (index >= scripts.length) {
        if (callback) callback();
        return;
    }
    
    loadScript(scripts[index], () => {
        loadScriptsSequentially(scripts, callback, index + 1);
    });
}

// 加载样式表
function loadStylesheet(url) {
    if (document.querySelector(`link[href="${url}"]`)) return;
    
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = url;
    document.head.appendChild(link);
}

// 加载脚本
function loadScript(url, callback) {
    if (document.querySelector(`script[src="${url}"]`)) {
        if (callback) callback();
        return;
    }
    
    const script = document.createElement('script');
    script.src = url;
    script.onload = callback;
    document.head.appendChild(script);
}

// 初始化所有编辑器
function initializeEditors() {
    document.querySelectorAll('.code-editor').forEach(element => {
        createEditor(element);
    });
}

// 创建编辑器
function createEditor(element, options = {}) {
    if (!window.CodeMirror) {
        console.error('CodeMirror 未加载');
        return null;
    }
    
    // 已存在的编辑器
    if (editors.has(element.id)) {
        return editors.get(element.id);
    }
    
    // 默认配置
    const defaultOptions = {
        mode: element.dataset.language || 'javascript',
        theme: 'dracula',
        lineNumbers: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        styleActiveLine: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        lineWrapping: true,
        extraKeys: {
            'Ctrl-Space': 'autocomplete',
            'Tab': function(cm) {
                if (cm.somethingSelected()) {
                    cm.indentSelection('add');
                } else {
                    cm.replaceSelection('    ', 'end');
                }
            },
            'Ctrl-/': 'toggleComment'
        }
    };
    
    // 合并选项
    const editorOptions = { ...defaultOptions, ...options };
    
    // 创建编辑器
    const editor = CodeMirror.fromTextArea(element, editorOptions);
    
    // 创建工具栏
    createEditorToolbar(element, editor);
    
    // 保存实例引用
    if (element.id) {
        editors.set(element.id, editor);
    }
    
    // 编辑器初始化事件
    const event = new CustomEvent('editor:ready', { detail: { editor, element } });
    element.dispatchEvent(event);
    
    return editor;
}

// 创建编辑器工具栏
function createEditorToolbar(element, editor) {
    const editorWrapper = editor.getWrapperElement();
    const container = editorWrapper.parentElement;
    
    // 创建工具栏
    const toolbar = document.createElement('div');
    toolbar.className = 'code-editor-toolbar';
    toolbar.innerHTML = `
        <div class="editor-toolbar-left">
            <span class="editor-language">${editor.getOption('mode')}</span>
            <button class="editor-btn format-btn" title="格式化代码">
                <i class="fas fa-indent"></i>
            </button>
            <button class="editor-btn copy-btn" title="复制代码">
                <i class="fas fa-copy"></i>
            </button>
        </div>
        <div class="editor-toolbar-right">
            <button class="editor-btn code-editor-expand-btn" title="全屏编辑">
                <i class="fas fa-expand"></i>
            </button>
        </div>
    `;
    
    // 在编辑器之前插入工具栏
    container.insertBefore(toolbar, editorWrapper);
    
    // 格式化按钮
    const formatBtn = toolbar.querySelector('.format-btn');
    formatBtn.addEventListener('click', () => {
        formatCode(editor);
    });
    
    // 复制按钮
    const copyBtn = toolbar.querySelector('.copy-btn');
    copyBtn.addEventListener('click', () => {
        copyToClipboard(editor.getValue());
    });
}

// 格式化代码
function formatCode(editor) {
    const mode = editor.getOption('mode');
    const code = editor.getValue();
    
    try {
        let formattedCode = code;
        
        if (mode === 'javascript' || mode === 'application/json') {
            // JavaScript 格式化
            formattedCode = formatJavaScript(code);
        } else if (mode === 'python') {
            // Python 格式化 (简单实现)
            formattedCode = formatPython(code);
        }
        
        // 更新编辑器内容
        editor.setValue(formattedCode);
        
        // 显示成功消息
        showToast('代码格式化成功', 'success');
    } catch (error) {
        console.error('格式化失败:', error);
        showToast('代码格式化失败: ' + error.message, 'error');
    }
}

// 格式化 JavaScript 代码
function formatJavaScript(code) {
    // 这里使用简单的方法，实际中可以使用 prettier 等库
    try {
        // 尝试解析并重新字符串化 JSON
        const parsed = JSON.parse(code);
        return JSON.stringify(parsed, null, 4);
    } catch (e) {
        // 不是有效的 JSON，尝试使用 Function 构造函数格式化 JS
        try {
            // 注意：这不是一个完美的格式化方案，仅用于简单场景
            const result = Function(`
                "use strict";
                let formatted = '';
                ${code}
                return formatted;
            `)();
            return result || code;
        } catch (e2) {
            return code; // 返回原始代码
        }
    }
}

// 格式化 Python 代码 (简单实现)
function formatPython(code) {
    // 实际应用中应该使用专门的 Python 格式化工具
    // 这里仅做简单处理
    return code;
}

// 复制到剪贴板
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            showToast('代码已复制到剪贴板', 'success');
        })
        .catch(err => {
            console.error('复制失败:', err);
            showToast('复制失败', 'error');
        });
}

// 切换编辑器全屏显示
function toggleEditorExpansion(button) {
    const wrapper = button.closest('.code-editor-container');
    wrapper.classList.toggle('expanded');
    
    // 更新图标
    const icon = button.querySelector('i');
    if (wrapper.classList.contains('expanded')) {
        icon.classList.remove('fa-expand');
        icon.classList.add('fa-compress');
        button.setAttribute('title', '退出全屏');
    } else {
        icon.classList.remove('fa-compress');
        icon.classList.add('fa-expand');
        button.setAttribute('title', '全屏编辑');
    }
    
    // 找到对应的编辑器实例并刷新
    const textareaId = wrapper.querySelector('textarea').id;
    const editor = editors.get(textareaId);
    if (editor) {
        editor.refresh();
    }
}

// 手动创建编辑器
function createCodeEditor(elementOrId, options = {}) {
    const element = typeof elementOrId === 'string' 
        ? document.getElementById(elementOrId) 
        : elementOrId;
        
    if (!element) {
        console.error('找不到元素:', elementOrId);
        return null;
    }
    
    return createEditor(element, options);
}

// 获取编辑器实例
function getEditor(id) {
    return editors.get(id);
}

// 销毁编辑器
function destroyEditor(id) {
    const editor = editors.get(id);
    if (editor) {
        editor.toTextArea();
        editors.delete(id);
    }
}

// 文档加载完成后初始化
document.addEventListener('DOMContentLoaded', initCodeEditor);

// 导出函数
window.CodeEditorManager = {
    create: createCodeEditor,
    get: getEditor,
    destroy: destroyEditor
}; 