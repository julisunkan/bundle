// PWA Builder App JavaScript

// Global app object
const PWABuilder = {
    // Initialize the application
    init() {
        this.setupEventListeners();
        this.setupTooltips();
        this.setupFormValidation();
    },

    // Setup event listeners
    setupEventListeners() {
        // Copy to clipboard functionality
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-copy]')) {
                this.copyToClipboard(e.target.dataset.copy);
            }
        });

        // Form submission handling
        const forms = document.querySelectorAll('form[data-ajax]');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleAjaxForm(e);
            });
        });

        // Package type selection handling
        const packageInputs = document.querySelectorAll('input[name="package_type"]');
        packageInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.updatePackageTypeInfo(e.target.value);
            });
        });
    },

    // Setup Bootstrap tooltips
    setupTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Setup form validation
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    },

    // Copy text to clipboard
    copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Copied to clipboard!', 'success');
            }).catch(err => {
                console.error('Failed to copy: ', err);
                this.showToast('Failed to copy to clipboard', 'error');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                this.showToast('Copied to clipboard!', 'success');
            } catch (err) {
                console.error('Fallback: Failed to copy', err);
                this.showToast('Failed to copy to clipboard', 'error');
            } finally {
                textArea.remove();
            }
        }
    },

    // Show toast notification
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1055';
            document.body.appendChild(toastContainer);
        }

        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 4000
        });
        bsToast.show();

        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    // Update package type information
    updatePackageTypeInfo(packageType) {
        const infoMap = {
            'apk': {
                title: 'Android APK',
                description: 'Full implementation with WebView container for Android devices.',
                icon: 'fab fa-android',
                color: 'success'
            },
            'ipa': {
                title: 'iOS IPA',
                description: 'Demo package for iOS devices. Requires proper signing for installation.',
                icon: 'fab fa-apple',
                color: 'info'
            },
            'msix': {
                title: 'Windows MSIX',
                description: 'Demo package for modern Windows 10/11 applications.',
                icon: 'fab fa-windows',
                color: 'warning'
            },
            'appx': {
                title: 'Windows APPX',
                description: 'Demo package for Windows 8.1/10 applications.',
                icon: 'fab fa-windows',
                color: 'secondary'
            }
        };

        const info = infoMap[packageType];
        if (info) {
            // Update any package info display elements
            const infoElement = document.getElementById('package-info');
            if (infoElement) {
                infoElement.innerHTML = `
                    <div class="alert alert-${info.color} border-0">
                        <i class="${info.icon} me-2"></i>
                        <strong>${info.title}:</strong> ${info.description}
                    </div>
                `;
            }
        }
    },

    // Handle AJAX form submissions
    handleAjaxForm(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;

        // Show loading state
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        submitBtn.disabled = true;

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok');
        })
        .then(data => {
            if (data.success) {
                this.showToast('Request processed successfully!', 'success');
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            } else {
                this.showToast(data.message || 'An error occurred', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showToast('An error occurred while processing your request', 'error');
        })
        .finally(() => {
            // Restore button state
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
        });
    },

    // Validate URL input
    validateUrl(url) {
        try {
            const parsedUrl = new URL(url);
            return parsedUrl.protocol === 'http:' || parsedUrl.protocol === 'https:';
        } catch (e) {
            return false;
        }
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Format date
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Debounce function for input validation
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    PWABuilder.init();
});

// Export for use in other scripts
window.PWABuilder = PWABuilder;
