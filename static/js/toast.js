// static/js/toast.js

// Map Flask flash categories to icons and classes
const toastIcons = {
    success: '<i class="ph ph-check-circle"></i>',
    info:    '<i class="ph ph-info"></i>',
    warning: '<i class="ph ph-warning"></i>',
    danger:  '<i class="ph ph-x-circle"></i>',
    error:   '<i class="ph ph-x-circle"></i>',
    default: '<i class="ph ph-bell"></i>'
};

function showToast(message, category = "info", timeout = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${category}`;
    toast.innerHTML = `
        <span class="toast-icon">${toastIcons[category] || toastIcons.default}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" aria-label="Close">&times;</button>
    `;

    // Close button
    toast.querySelector('.toast-close').onclick = () => {
        toast.remove();
    };

    container.appendChild(toast);

    // Auto-dismiss
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, timeout);
}

// On page load, convert Flask flashed messages to toasts
document.addEventListener('DOMContentLoaded', function () {
    // Flask injects messages into a JS variable if we add them to the template
    if (window.FLASK_FLASHES) {
        window.FLASK_FLASHES.forEach(([category, message]) => {
            showToast(message, category);
        });
    }
});
