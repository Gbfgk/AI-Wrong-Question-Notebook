// 主JavaScript文件 - AI错题本

// 初始化Materialize组件
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有下拉菜单
    var dropdowns = document.querySelectorAll('.dropdown-trigger');
    M.Dropdown.init(dropdowns);
    
    // 初始化所有模态框
    var modals = document.querySelectorAll('.modal');
    M.Modal.init(modals);
    
    // 初始化所有工具提示
    var tooltips = document.querySelectorAll('.tooltipped');
    M.Tooltip.init(tooltips);
    
    // 初始化所有toast通知
    // 自动隐藏flash消息（5秒后）
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });
    
    // 确认删除操作
    var deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('确定要执行此操作吗？')) {
                e.preventDefault();
            }
        });
    });
});

// 格式化时间显示
function formatTimeAgo(dateString) {
    var date = new Date(dateString);
    var now = new Date();
    var seconds = Math.floor((now - date) / 1000);
    
    var intervals = {
        'year': 31536000,
        'month': 2592000,
        'week': 604800,
        'day': 86400,
        'hour': 3600,
        'minute': 60
    };
    
    for (var key in intervals) {
        var interval = Math.floor(seconds / intervals[key]);
        if (interval >= 1) {
            return interval + ' ' + key + '前';
        }
    }
    
    return '刚刚';
}

// AJAX请求辅助函数
function ajaxRequest(url, method, data) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('网络响应失败');
        }
        return response.json();
    });
}

// 显示加载提示
function showLoading(message) {
    M.toast({html: message || '加载中...', classes: 'blue', displayLength: 3000});
}

// 显示成功提示
function showSuccess(message) {
    M.toast({html: message || '操作成功', classes: 'green', displayLength: 3000});
}

// 显示错误提示
function showError(message) {
    M.toast({html: message || '操作失败', classes: 'red', displayLength: 3000});
}

// 复制文本到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showSuccess('已复制到剪贴板');
        }, function() {
            showError('复制失败');
        });
    } else {
        // 降级方案
        var textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showSuccess('已复制到剪贴板');
        } catch (err) {
            showError('复制失败');
        }
        document.body.removeChild(textArea);
    }
}

// 表单验证辅助函数
function validateForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return false;
    
    var isValid = true;
    var requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('invalid');
            isValid = false;
        } else {
            field.classList.remove('invalid');
        }
    });
    
    return isValid;
}

// 防抖函数（用于搜索输入）
function debounce(func, wait) {
    var timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 本地存储辅助函数
const Storage = {
    get: function(key) {
        try {
            return JSON.parse(localStorage.getItem(key));
        } catch (e) {
            return null;
        }
    },
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            return false;
        }
    },
    remove: function(key) {
        localStorage.removeItem(key);
    },
    clear: function() {
        localStorage.clear();
    }
};

// 主题切换（可选功能）
function toggleTheme() {
    var body = document.body;
    body.classList.toggle('dark-theme');
    
    var isDark = body.classList.contains('dark-theme');
    Storage.set('theme', isDark ? 'dark' : 'light');
}

// 初始化主题
function initTheme() {
    var savedTheme = Storage.get('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// 页面加载时初始化
initTheme();

console.log('AI错题本 - 已加载');
