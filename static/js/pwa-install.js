// PWA Installation and Management
class PWAInstaller {
  constructor() {
    this.deferredPrompt = null;
    this.init();
  }

  init() {
    // Register service worker
    this.registerServiceWorker();
    
    // Handle install prompt
    this.setupInstallPrompt();
    
    // Setup install button
    this.setupInstallButtons();
    
    // Check if already installed
    this.checkInstallationStatus();
  }

  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/static/sw.js');
        console.log('Service Worker registered successfully:', registration);
        
        // Update found
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.showUpdateAvailable();
            }
          });
        });
      } catch (error) {
        console.log('Service Worker registration failed:', error);
      }
    }
  }

  setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e) => {
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault();
      
      // Save the event so it can be triggered later
      this.deferredPrompt = e;
      
      // Show install button
      this.showInstallButton();
    });

    window.addEventListener('appinstalled', () => {
      console.log('PWA was installed');
      this.hideInstallButton();
      this.deferredPrompt = null;
    });
  }

  setupInstallButtons() {
    const installButton = document.getElementById('install-pwa-btn');
    if (installButton) {
      installButton.addEventListener('click', () => {
        this.promptInstall();
      });
    }
  }

  showInstallButton() {
    const installButton = document.getElementById('install-pwa-btn');
    if (installButton) {
      installButton.style.display = 'inline-block';
    }
  }

  hideInstallButton() {
    const installButton = document.getElementById('install-pwa-btn');
    if (installButton) {
      installButton.style.display = 'none';
    }
  }

  async promptInstall() {
    if (!this.deferredPrompt) {
      console.log('Install prompt not available');
      return;
    }

    // Show the install prompt
    this.deferredPrompt.prompt();

    // Wait for the user to respond to the prompt
    const { outcome } = await this.deferredPrompt.userChoice;
    console.log(`User response to the install prompt: ${outcome}`);

    // Clear the deferredPrompt
    this.deferredPrompt = null;
    
    if (outcome === 'accepted') {
      this.hideInstallButton();
    }
  }

  checkInstallationStatus() {
    // Check if app is running in standalone mode
    if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone) {
      console.log('App is running in standalone mode');
      this.hideInstallButton();
      this.addStandaloneStyles();
    }
  }

  addStandaloneStyles() {
    document.body.classList.add('standalone-app');
  }

  showUpdateAvailable() {
    const updateBanner = document.createElement('div');
    updateBanner.className = 'alert alert-info alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    updateBanner.style.zIndex = '9999';
    updateBanner.innerHTML = `
      <i class="fas fa-sync-alt me-2"></i>
      New version available! 
      <button type="button" class="btn btn-sm btn-outline-info ms-2" onclick="location.reload()">
        Update Now
      </button>
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(updateBanner);
  }
}

// Notification support
class PWANotifications {
  constructor() {
    this.init();
  }

  init() {
    this.setupNotificationPermission();
  }

  async setupNotificationPermission() {
    if ('Notification' in window && 'serviceWorker' in navigator) {
      // Request permission on user interaction
      document.addEventListener('click', this.requestPermission.bind(this), { once: true });
    }
  }

  async requestPermission() {
    if (Notification.permission === 'default') {
      const permission = await Notification.requestPermission();
      console.log('Notification permission:', permission);
    }
  }

  showNotification(title, options = {}) {
    if (Notification.permission === 'granted' && 'serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then(registration => {
        registration.showNotification(title, {
          icon: '/static/icons/icon-192x192.png',
          badge: '/static/icons/icon-72x72.png',
          ...options
        });
      });
    }
  }
}

// Offline/Online detection
class PWAConnectionManager {
  constructor() {
    this.init();
  }

  init() {
    this.setupConnectionListeners();
    this.checkInitialConnection();
  }

  setupConnectionListeners() {
    window.addEventListener('online', () => {
      this.hideOfflineIndicator();
    });

    window.addEventListener('offline', () => {
      this.showOfflineIndicator();
    });
  }

  checkInitialConnection() {
    if (!navigator.onLine) {
      this.showOfflineIndicator();
    }
  }

  showOfflineIndicator() {
    const indicator = document.getElementById('offline-indicator');
    if (indicator) {
      indicator.classList.add('show');
    }
  }

  hideOfflineIndicator() {
    const indicator = document.getElementById('offline-indicator');
    if (indicator) {
      indicator.classList.remove('show');
    }
  }
}

// Initialize PWA features
document.addEventListener('DOMContentLoaded', () => {
  new PWAInstaller();
  new PWANotifications();
  new PWAConnectionManager();
});

// Export for use in other scripts
window.PWAInstaller = PWAInstaller;
window.PWANotifications = PWANotifications;
window.PWAConnectionManager = PWAConnectionManager;