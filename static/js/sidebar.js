// static/js/sidebar.js
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const openBtn = document.getElementById('sidebar-toggle');
    const closeBtn = document.getElementById('sidebar-close');

    function openSidebar() {
        sidebar.classList.add('mobile-active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    function closeSidebar() {
        sidebar.classList.remove('mobile-active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (openBtn) openBtn.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    if (overlay) overlay.addEventListener('click', closeSidebar);
});

// User teaser dropdown for logout
document.addEventListener('DOMContentLoaded', function () {
    const userTeaser = document.getElementById('user-teaser');
    const logoutMenu = document.getElementById('logout-menu');
    if (userTeaser && logoutMenu) {
        userTeaser.addEventListener('click', function (e) {
            logoutMenu.classList.toggle('show');
            userTeaser.classList.toggle('user-teaser-hidden');
            e.stopPropagation();
        });
        // Hide menu when clicking outside
        document.addEventListener('click', function (e) {
            if (logoutMenu.classList.contains('show') && !logoutMenu.contains(e.target)) {
                logoutMenu.classList.remove('show');
                userTeaser.classList.remove('user-teaser-hidden');
            }
        });
    }
});
