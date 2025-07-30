import json
import os
from urllib.parse import urlparse

class PWAGenerator:
    def __init__(self, metadata, pwa_assessment):
        self.metadata = metadata
        self.assessment = pwa_assessment
        self.base_url = f"{urlparse(metadata.url).scheme}://{urlparse(metadata.url).netloc}"
    
    def generate_pwa_files(self):
        """Generate all necessary PWA files"""
        files = {}
        
        # Always generate these core files
        files['manifest.json'] = self._generate_manifest()
        files['sw.js'] = self._generate_service_worker()
        files['index.html'] = self._generate_enhanced_html()
        files['offline.html'] = self._generate_offline_page()
        
        # Generate installation instructions
        files['PWA_SETUP_INSTRUCTIONS.md'] = self._generate_setup_instructions()
        
        return files
    
    def _generate_manifest(self):
        """Generate comprehensive web app manifest"""
        # Use existing manifest data if available, otherwise create new
        if self.assessment.get('checks', {}).get('manifest', {}).get('data'):
            manifest = self.assessment['checks']['manifest']['data'].copy()
            # Enhance existing manifest
            manifest.update(self._get_manifest_enhancements())
        else:
            # Create new manifest from scratch
            manifest = {
                "name": self.metadata.title,
                "short_name": self.metadata.title[:12] if len(self.metadata.title) > 12 else self.metadata.title,
                "description": self.metadata.description or f"Progressive Web App for {self.metadata.title}",
                "start_url": "/",
                "scope": "/",
                "display": "standalone",
                "orientation": "any",
                "theme_color": self.metadata.theme_color or "#000000",
                "background_color": self.metadata.background_color or "#ffffff",
                "lang": "en",
                "dir": "ltr",
                "categories": ["productivity", "utilities"],
                "prefer_related_applications": False,
                "icons": self._generate_icon_set(),
                "shortcuts": self._generate_shortcuts(),
                "screenshots": self._generate_screenshots()
            }
        
        return json.dumps(manifest, indent=2)
    
    def _generate_icon_set(self):
        """Generate comprehensive icon set"""
        icons = []
        
        # Standard PWA icon sizes
        sizes = [
            {"size": "72x72", "purpose": "any"},
            {"size": "96x96", "purpose": "any"},
            {"size": "128x128", "purpose": "any"},
            {"size": "144x144", "purpose": "any"},
            {"size": "152x152", "purpose": "any"},
            {"size": "192x192", "purpose": "any maskable"},
            {"size": "384x384", "purpose": "any"},
            {"size": "512x512", "purpose": "any maskable"}
        ]
        
        for size_info in sizes:
            if self.metadata.icon_url:
                icons.append({
                    "src": self.metadata.icon_url,
                    "sizes": size_info["size"],
                    "type": "image/png",
                    "purpose": size_info["purpose"]
                })
            else:
                # Generate placeholder icon reference
                icons.append({
                    "src": f"/icons/icon-{size_info['size']}.png",
                    "sizes": size_info["size"],
                    "type": "image/png",
                    "purpose": size_info["purpose"]
                })
        
        return icons
    
    def _generate_shortcuts(self):
        """Generate app shortcuts"""
        return [
            {
                "name": "Home",
                "short_name": "Home",
                "description": "Go to home page",
                "url": "/",
                "icons": [
                    {
                        "src": self.metadata.icon_url or "/icons/icon-192x192.png",
                        "sizes": "96x96"
                    }
                ]
            }
        ]
    
    def _generate_screenshots(self):
        """Generate screenshots metadata"""
        return [
            {
                "src": "/screenshots/screenshot-wide.png",
                "sizes": "1280x720",
                "type": "image/png",
                "platform": "wide",
                "label": "Wide screenshot of the application"
            },
            {
                "src": "/screenshots/screenshot-mobile.png",
                "sizes": "750x1334",
                "type": "image/png",
                "platform": "narrow",
                "label": "Mobile screenshot of the application"
            }
        ]
    
    def _get_manifest_enhancements(self):
        """Get enhancements for existing manifest"""
        return {
            "prefer_related_applications": False,
            "categories": ["productivity", "utilities"],
            "shortcuts": self._generate_shortcuts(),
            "screenshots": self._generate_screenshots()
        }
    
    def _generate_service_worker(self):
        """Generate comprehensive service worker"""
        return f'''// Service Worker for {self.metadata.title}
const CACHE_NAME = '{self.metadata.title.replace(" ", "-").lower()}-pwa-v1';
const STATIC_CACHE = CACHE_NAME + '-static';
const DYNAMIC_CACHE = CACHE_NAME + '-dynamic';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/index.html',
    '/manifest.json',
    '/offline.html',
    // Add your CSS, JS, and other static assets here
];

// Install event - cache static files
self.addEventListener('install', event => {{
    console.log('Service Worker: Installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {{
                console.log('Service Worker: Caching App Shell');
                return cache.addAll(STATIC_FILES);
            }})
            .then(() => {{
                console.log('Service Worker: Installed');
                return self.skipWaiting();
            }})
            .catch(error => {{
                console.error('Service Worker: Installation failed', error);
            }})
    );
}});

// Activate event - clean up old caches
self.addEventListener('activate', event => {{
    console.log('Service Worker: Activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {{
            return Promise.all(
                cacheNames.map(cacheName => {{
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {{
                        console.log('Service Worker: Deleting old cache', cacheName);
                        return caches.delete(cacheName);
                    }}
                }})
            );
        }})
        .then(() => {{
            console.log('Service Worker: Activated');
            return self.clients.claim();
        }})
    );
}});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {{
    const request = event.request;
    
    // Skip non-GET requests
    if (request.method !== 'GET') {{
        return;
    }}
    
    // Handle navigation requests
    if (request.mode === 'navigate') {{
        event.respondWith(
            fetch(request)
                .then(response => {{
                    // If online, cache the response and return it
                    const responseClone = response.clone();
                    caches.open(DYNAMIC_CACHE)
                        .then(cache => cache.put(request, responseClone));
                    return response;
                }})
                .catch(() => {{
                    // If offline, try cache first, then offline page
                    return caches.match(request)
                        .then(cachedResponse => {{
                            return cachedResponse || caches.match('/offline.html');
                        }});
                }})
        );
        return;
    }}
    
    // Handle other requests
    event.respondWith(
        caches.match(request)
            .then(cachedResponse => {{
                if (cachedResponse) {{
                    return cachedResponse;
                }}
                
                return fetch(request)
                    .then(response => {{
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {{
                            return response;
                        }}
                        
                        // Cache successful responses
                        const responseClone = response.clone();
                        caches.open(DYNAMIC_CACHE)
                            .then(cache => {{
                                cache.put(request, responseClone);
                            }});
                        
                        return response;
                    }})
                    .catch(() => {{
                        // Return offline page for failed requests
                        if (request.destination === 'document') {{
                            return caches.match('/offline.html');
                        }}
                    }});
            }})
    );
}});

// Background sync for when connection is restored
self.addEventListener('sync', event => {{
    console.log('Service Worker: Background sync', event.tag);
    // Handle background sync tasks here
}});

// Push notifications
self.addEventListener('push', event => {{
    console.log('Service Worker: Push received', event);
    // Handle push notifications here
}});

// Notification click
self.addEventListener('notificationclick', event => {{
    console.log('Service Worker: Notification clicked', event);
    event.notification.close();
    
    event.waitUntil(
        clients.openWindow('/')
    );
}});'''
    
    def _generate_enhanced_html(self):
        """Generate enhanced HTML with PWA features"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.metadata.title}</title>
    
    <!-- PWA Manifest -->
    <link rel="manifest" href="/manifest.json">
    
    <!-- Meta tags for PWA -->
    <meta name="theme-color" content="{self.metadata.theme_color}">
    <meta name="background-color" content="{self.metadata.background_color}">
    <meta name="description" content="{self.metadata.description}">
    
    <!-- iOS specific meta tags -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="{self.metadata.title}">
    
    <!-- Icon links -->
    <link rel="icon" href="{self.metadata.icon_url or '/icons/icon-192x192.png'}" type="image/png">
    <link rel="apple-touch-icon" href="{self.metadata.icon_url or '/icons/icon-192x192.png'}">
    
    <!-- Preload critical resources -->
    <link rel="preload" href="/manifest.json" as="fetch" crossorigin>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: {self.metadata.background_color};
            color: #333;
            line-height: 1.6;
        }}
        
        .app-container {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .app-header {{
            background: {self.metadata.theme_color};
            color: white;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .app-content {{
            flex: 1;
            position: relative;
            overflow: hidden;
        }}
        
        .website-frame {{
            width: 100%;
            height: 100%;
            border: none;
            display: block;
        }}
        
        .loading-screen {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: {self.metadata.background_color};
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }}
        
        .loading-spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid {self.metadata.theme_color};
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .install-prompt {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background: {self.metadata.theme_color};
            color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: none;
            z-index: 1001;
        }}
        
        .install-prompt button {{
            background: white;
            color: {self.metadata.theme_color};
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            margin: 0 0.5rem;
        }}
        
        .offline-indicator {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #ff6b6b;
            color: white;
            text-align: center;
            padding: 0.5rem;
            transform: translateY(-100%);
            transition: transform 0.3s ease;
            z-index: 1002;
        }}
        
        .offline-indicator.show {{
            transform: translateY(0);
        }}
        
        @media (max-width: 768px) {{
            .app-header {{
                padding: 0.8rem;
            }}
            
            .install-prompt {{
                bottom: 10px;
                left: 10px;
                right: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="app-container">
        <div class="offline-indicator" id="offlineIndicator">
            You're currently offline. Some features may not work.
        </div>
        
        <div class="app-header">
            <h1>{self.metadata.title}</h1>
        </div>
        
        <div class="app-content">
            <div class="loading-screen" id="loadingScreen">
                <div class="loading-spinner"></div>
                <p>Loading {self.metadata.title}...</p>
            </div>
            
            <iframe 
                src="{self.metadata.url}" 
                class="website-frame" 
                id="websiteFrame"
                title="{self.metadata.title}"
                sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-navigation"
                loading="lazy">
            </iframe>
        </div>
        
        <div class="install-prompt" id="installPrompt">
            <p><strong>Install {self.metadata.title}</strong></p>
            <p>Add this app to your home screen for a better experience!</p>
            <button id="installButton">Install</button>
            <button id="dismissButton">Maybe Later</button>
        </div>
    </div>

    <script>
        // PWA functionality
        let deferredPrompt;
        let isOnline = navigator.onLine;
        
        // Service Worker registration
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {{
                        console.log('SW registered: ', registration);
                    }})
                    .catch(registrationError => {{
                        console.log('SW registration failed: ', registrationError);
                    }});
            }});
        }}
        
        // Install prompt handling
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('installPrompt').style.display = 'block';
        }});
        
        document.getElementById('installButton').addEventListener('click', () => {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {{
                    console.log('User choice: ', choiceResult);
                    deferredPrompt = null;
                    document.getElementById('installPrompt').style.display = 'none';
                }});
            }}
        }});
        
        document.getElementById('dismissButton').addEventListener('click', () => {{
            document.getElementById('installPrompt').style.display = 'none';
        }});
        
        // Online/offline handling
        window.addEventListener('online', () => {{
            isOnline = true;
            document.getElementById('offlineIndicator').classList.remove('show');
            // Reload iframe when back online
            const frame = document.getElementById('websiteFrame');
            if (frame.src !== '{self.metadata.url}') {{
                frame.src = '{self.metadata.url}';
            }}
        }});
        
        window.addEventListener('offline', () => {{
            isOnline = false;
            document.getElementById('offlineIndicator').classList.add('show');
        }});
        
        // Loading screen handling
        document.getElementById('websiteFrame').addEventListener('load', () => {{
            document.getElementById('loadingScreen').style.display = 'none';
        }});
        
        // Error handling for iframe
        document.getElementById('websiteFrame').addEventListener('error', () => {{
            if (!isOnline) {{
                document.getElementById('loadingScreen').innerHTML = `
                    <div style="text-align: center; padding: 2rem;">
                        <h2>You're Offline</h2>
                        <p>Connect to the internet to use {self.metadata.title}</p>
                        <button onclick="location.reload()" style="
                            background: {self.metadata.theme_color}; 
                            color: white; 
                            border: none; 
                            padding: 0.8rem 1.5rem; 
                            border-radius: 4px; 
                            cursor: pointer;
                            margin-top: 1rem;
                        ">Try Again</button>
                    </div>
                `;
            }}
        }});
        
        // Initialize offline indicator
        if (!isOnline) {{
            document.getElementById('offlineIndicator').classList.add('show');
        }}
        
        // Handle app lifecycle
        document.addEventListener('visibilitychange', () => {{
            if (document.visibilityState === 'visible') {{
                // App became visible, check if we need to reload
                if (isOnline) {{
                    const frame = document.getElementById('websiteFrame');
                    // Optionally refresh the iframe
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    def _generate_offline_page(self):
        """Generate offline fallback page"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline - {self.metadata.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: {self.metadata.background_color};
            color: #333;
            margin: 0;
            padding: 2rem;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        
        .offline-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.6;
        }}
        
        h1 {{
            color: {self.metadata.theme_color};
            margin-bottom: 1rem;
        }}
        
        .retry-button {{
            background: {self.metadata.theme_color};
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
            margin-top: 1rem;
            transition: opacity 0.2s;
        }}
        
        .retry-button:hover {{
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="offline-icon">📡</div>
    <h1>You're Offline</h1>
    <p>It looks like you've lost your internet connection.</p>
    <p>Please check your connection and try again.</p>
    
    <button class="retry-button" onclick="location.reload()">
        Try Again
    </button>
    
    <script>
        // Auto-reload when connection is restored
        window.addEventListener('online', () => {{
            location.reload();
        }});
    </script>
</body>
</html>'''
    
    def _generate_setup_instructions(self):
        """Generate comprehensive setup instructions"""
        return f'''# 📱 PWA Setup Instructions for {self.metadata.title}

## 🎯 Overview
This package contains all the files needed to make **{self.metadata.title}** a Progressive Web App (PWA). 

## 📦 Files Included
- **`manifest.json`** - Web app manifest with app metadata
- **`sw.js`** - Service worker for offline functionality  
- **`index.html`** - Enhanced HTML with PWA features
- **`offline.html`** - Offline fallback page

## 🚀 Installation Steps

### Step 1: Upload Files
Upload all the generated files to your website's **root directory**:

```
your-website.com/
├── manifest.json          ← Place here
├── sw.js                  ← Place here  
├── index.html             ← Replace existing or use provided
└── offline.html           ← Place here
```

### Step 2: Create App Icons  
Create the following icon files and place them in an **`/icons/`** directory:

**Required Sizes:**
- `icon-72x72.png` (Android, Chrome)
- `icon-96x96.png` (Android, Chrome) 
- `icon-128x128.png` (Chrome, Windows)
- `icon-144x144.png` (Windows)
- `icon-152x152.png` (iOS)
- `icon-192x192.png` (Android, Chrome) ⭐ **Essential**
- `icon-384x384.png` (Android, Chrome)
- `icon-512x512.png` (Android, Chrome) ⭐ **Essential**

**Icon Requirements:**
- Format: PNG with transparent background
- Square aspect ratio (1:1)
- High quality, no compression artifacts

### Step 3: Create Screenshots (Optional but Recommended)
Create screenshot files in a **`/screenshots/`** directory:
- **`screenshot-wide.png`** (1280x720) - Desktop view
- **`screenshot-mobile.png`** (750x1334) - Mobile view

### Step 4: Update Existing HTML (If Not Using Provided index.html)
If you prefer to keep your existing HTML, add these elements to your **`<head>`** section:

```html
<!-- 📱 PWA Manifest -->
<link rel="manifest" href="/manifest.json">

<!-- 🎨 Meta tags for PWA -->
<meta name="theme-color" content="{self.metadata.theme_color}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="{self.metadata.title}">

<!-- 🎯 Icons -->
<link rel="icon" href="/icons/icon-192x192.png" type="image/png">
<link rel="apple-touch-icon" href="/icons/icon-192x192.png">
```

And add this JavaScript before the closing **`</body>`** tag:

```html
<script>
// Service Worker registration
if ('serviceWorker' in navigator) {{
    window.addEventListener('load', () => {{
        navigator.serviceWorker.register('/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    }});
}}
</script>
```

### 5. HTTPS Requirement
Ensure your website is served over HTTPS. PWAs require a secure connection.

### 6. Test Your PWA
1. Open your website in Chrome or Edge
2. Look for the install button in the address bar
3. Test offline functionality by disconnecting internet
4. Use Chrome DevTools > Application > Manifest to verify setup

## PWA Assessment Results

### Current PWA Score: {self.assessment.get('pwa_score', 0)}%

### Checks Performed:
'''

        # Add check results
        for check_name, check_result in self.assessment.get('checks', {}).items():
            status = "✅ PASS" if check_result.get('passed') else "❌ FAIL"
            instructions += f"- **{check_name.replace('_', ' ').title()}**: {status}\n"
            instructions += f"  - {check_result.get('details', 'No details')}\n\n"

        # Add recommendations
        if self.assessment.get('recommendations'):
            instructions += "### Recommendations:\n\n"
            for rec in self.assessment['recommendations']:
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(rec['priority'], "ℹ️")
                instructions += f"{priority_emoji} **{rec['title']}** ({rec['priority']} priority)\n"
                instructions += f"   - {rec['description']}\n"
                instructions += f"   - Action: {rec['action']}\n\n"

        instructions += f'''
## Support
- Test your PWA using Chrome DevTools > Lighthouse > Progressive Web App audit
- Verify manifest at: https://manifest-validator.appspot.com/
- Check service worker in DevTools > Application > Service Workers

## Additional Resources
- [PWA Checklist](https://web.dev/pwa-checklist/)
- [Service Worker Cookbook](https://serviceworke.rs/)
- [Web App Manifest Generator](https://app-manifest.firebaseapp.com/)
'''

        return instructions