// Theme Switcher Functionality
class ThemeSwitcher {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.init();
    }

    init() {
        // Set initial theme
        this.setTheme(this.currentTheme);
        
        // Add event listeners to theme buttons
        document.querySelectorAll('.theme-option').forEach(button => {
            button.addEventListener('click', (e) => {
                const theme = e.target.closest('.theme-option').dataset.theme;
                this.setTheme(theme);
            });
        });

        // Update active button
        this.updateActiveButton();
    }

    setTheme(theme) {
        // Update body data attribute
        document.body.setAttribute('data-theme', theme);
        
        // Update navigation background based on theme
        const nav = document.querySelector('.navbar');
        if (nav) {
            switch(theme) {
                case 'light':
                    nav.style.background = 'rgba(255, 255, 255, 0.95)';
                    nav.style.borderBottom = '1px solid rgba(0, 0, 0, 0.1)';
                    nav.classList.remove('navbar-dark');
                    nav.classList.add('navbar-light');
                    break;
                case 'grey':
                    nav.style.background = 'rgba(134, 142, 150, 0.95)';
                    nav.style.borderBottom = '1px solid rgba(255, 255, 255, 0.15)';
                    nav.classList.remove('navbar-light');
                    nav.classList.add('navbar-dark');
                    break;
                default: // dark
                    nav.style.background = 'rgba(0, 0, 0, 0.9)';
                    nav.style.borderBottom = '1px solid rgba(255, 255, 255, 0.1)';
                    nav.classList.remove('navbar-light');
                    nav.classList.add('navbar-dark');
                    break;
            }
        }

        // Update install button style for light theme
        const installBtn = document.getElementById('install-pwa-btn');
        if (installBtn) {
            if (theme === 'light') {
                installBtn.className = 'btn btn-outline-dark btn-sm px-3 py-2';
            } else {
                installBtn.className = 'btn btn-outline-light btn-sm px-3 py-2';
            }
            installBtn.style.borderRadius = '25px';
            installBtn.style.fontWeight = '500';
        }

        // Update footer text colors for light theme
        const footer = document.querySelector('.professional-footer');
        if (footer && theme === 'light') {
            footer.querySelectorAll('.text-white, .text-on-dark').forEach(el => {
                el.style.color = '#333 !important';
            });
            footer.querySelectorAll('[style*="color: rgba(255, 255, 255"]').forEach(el => {
                el.style.color = 'rgba(51, 51, 51, 0.8)';
            });
        }

        // Store theme preference
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);
        
        // Update active button
        this.updateActiveButton();

        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    }

    updateActiveButton() {
        document.querySelectorAll('.theme-option').forEach(button => {
            button.classList.remove('active');
            if (button.dataset.theme === this.currentTheme) {
                button.classList.add('active');
            }
        });
    }

    getTheme() {
        return this.currentTheme;
    }
}

// Initialize theme switcher when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeSwitcher = new ThemeSwitcher();
    
    // Add smooth transitions after initial load
    setTimeout(() => {
        document.body.style.transition = 'all 0.3s ease';
    }, 100);
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeSwitcher;
}