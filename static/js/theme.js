// static/js/theme.js
document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('theme-toggle');
    const html = document.documentElement;
    // Persist theme in localStorage
    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        btn.innerHTML = theme === 'dark'
            ? '<i class="ph ph-sun"></i>'
            : '<i class="ph ph-moon"></i>';
    }
    // On load
    const saved = localStorage.getItem('theme');
    setTheme(saved === 'light' ? 'light' : 'dark');
    btn.addEventListener('click', function () {
        setTheme(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });
});
