import os
import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from app import app
from .icon_generator import IconGenerator

class EnhancedAPKBuilder:
    """Enhanced APK Builder with improved error handling and compatibility"""
    
    def __init__(self):
        self.output_dir = app.config['UPLOAD_FOLDER']
        self.icon_generator = IconGenerator()
    
    def build_android_apk(self, metadata, manifest_data, job_id, target_url):
        """Build Android APK-ready project with modern configuration"""
        try:
            app.logger.info(f"Building enhanced APK project for {metadata.title}")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                project_dir = os.path.join(temp_dir, 'android_apk_project')
                os.makedirs(project_dir, exist_ok=True)
                
                app_name = self._sanitize_name(metadata.title)
                
                # Create enhanced Cordova project structure
                self._create_enhanced_cordova_structure(project_dir, metadata, manifest_data, target_url)
                
                # Create modern build scripts
                self._create_modern_build_scripts(project_dir, app_name)
                
                # Create comprehensive documentation
                self._create_enhanced_documentation(project_dir, metadata, target_url)
                
                # Package as ZIP
                zip_filename = f"{app_name}_Enhanced_APK_Project_{job_id}.zip"
                zip_path = os.path.join(self.output_dir, zip_filename)
                
                self._create_project_zip(project_dir, zip_path)
                
                app.logger.info(f"Enhanced APK project created: {zip_filename}")
                return zip_path
                
        except Exception as e:
            app.logger.error(f"Enhanced APK build failed: {str(e)}")
            raise Exception(f"Enhanced APK build failed: {str(e)}")
    
    def _create_enhanced_cordova_structure(self, project_dir, metadata, manifest_data, target_url):
        """Create enhanced Cordova project structure with modern dependencies"""
        app_name = self._sanitize_name(metadata.title)
        package_name = f"com.digitalskeleton.{app_name.lower()}"
        
        # Create directory structure
        www_dir = os.path.join(project_dir, 'www')
        os.makedirs(www_dir, exist_ok=True)
        
        # Create modern package.json with updated dependencies
        package_json = {
            "name": app_name.lower(),
            "displayName": metadata.title,
            "version": "1.0.0",
            "description": f"Enhanced mobile app for {metadata.title}",
            "main": "index.js",
            "scripts": {
                "clean": "rm -rf platforms/android",
                "setup": "cordova platform add android",
                "build": "cordova build android --release",
                "build-debug": "cordova build android --debug",
                "run": "cordova run android",
                "prepare": "cordova prepare android",
                "serve": "cordova serve"
            },
            "dependencies": {
                "cordova": "^12.0.0",
                "cordova-android": "^12.0.0"
            },
            "devDependencies": {
                "cordova-plugin-inappbrowser": "^6.0.0",
                "cordova-plugin-network-information": "^3.0.0",
                "cordova-plugin-splashscreen": "^6.0.0"
            },
            "cordova": {
                "platforms": ["android"],
                "plugins": {
                    "cordova-plugin-inappbrowser": {},
                    "cordova-plugin-network-information": {},
                    "cordova-plugin-splashscreen": {}
                }
            }
        }
        
        with open(os.path.join(project_dir, 'package.json'), 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
        
        # Create enhanced config.xml with proper XML structure
        config_xml = self._generate_enhanced_config_xml(metadata, target_url, package_name, app_name)
        with open(os.path.join(project_dir, 'config.xml'), 'w', encoding='utf-8') as f:
            f.write(config_xml)
        
        # Create enhanced index.html
        index_html = self._generate_enhanced_index_html(metadata, target_url)
        with open(os.path.join(www_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        # Create offline page
        offline_html = self._generate_offline_page(metadata, target_url)
        with open(os.path.join(www_dir, 'offline.html'), 'w', encoding='utf-8') as f:
            f.write(offline_html)
        
        # Create service worker for offline support
        sw_js = self._generate_service_worker(target_url)
        with open(os.path.join(www_dir, 'sw.js'), 'w', encoding='utf-8') as f:
            f.write(sw_js)
        
        # Create enhanced manifest.json
        with open(os.path.join(www_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2)
        
        # Generate and save icons
        self._generate_project_icons(project_dir, metadata)
    
    def _generate_enhanced_config_xml(self, metadata, target_url, package_name, app_name):
        """Generate enhanced config.xml with proper XML structure and modern plugins"""
        
        # Escape XML special characters in text content
        def escape_xml(text):
            if not text:
                return ""
            return (text.replace("&", "&amp;")
                       .replace("<", "&lt;")
                       .replace(">", "&gt;")
                       .replace('"', "&quot;")
                       .replace("'", "&apos;"))
        
        title = escape_xml(metadata.title)
        description = escape_xml(metadata.description or f"Enhanced mobile app for {metadata.title}")
        
        return f"""<?xml version='1.0' encoding='utf-8'?>
<widget id="{package_name}" version="1.0.0" xmlns="http://www.w3.org/ns/widgets" xmlns:cdv="http://cordova.apache.org/ns/1.0">
    <name>{title}</name>
    <description>{description}</description>
    <author email="info@digitalskeleton.com" href="https://digitalskeleton.com">
        DigitalSkeleton Team
    </author>
    <content src="index.html" />
    
    <access origin="*" />
    <allow-intent href="http://*/*" />
    <allow-intent href="https://*/*" />
    <allow-intent href="tel:*" />
    <allow-intent href="sms:*" />
    <allow-intent href="mailto:*" />
    <allow-intent href="geo:*" />
    
    <platform name="android">
        <allow-intent href="market:*" />
        <preference name="AndroidLaunchMode" value="singleTop" />
        <preference name="AndroidPersistentFileLocation" value="Compatibility" />
        <preference name="SplashMaintainAspectRatio" value="true" />
        <preference name="SplashShowOnlyFirstTime" value="false" />
        <preference name="SplashScreen" value="screen" />
        <preference name="SplashScreenDelay" value="3000" />
        <preference name="AutoHideSplashScreen" value="true" />
        <preference name="ShowSplashScreenSpinner" value="false" />
        <preference name="loadUrlTimeoutValue" value="700000" />
        
        <preference name="android-targetSdkVersion" value="33" />
        <preference name="android-minSdkVersion" value="21" />
        <preference name="android-compileSdkVersion" value="33" />
    </platform>
    
    <plugin name="cordova-plugin-inappbrowser" spec="^6.0.0" />
    <plugin name="cordova-plugin-network-information" spec="^3.0.0" />
    <plugin name="cordova-plugin-splashscreen" spec="^6.0.0" />
</widget>"""
    
    def _generate_enhanced_index_html(self, metadata, target_url):
        """Generate enhanced index.html with offline page support"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>{metadata.title}</title>
    <link rel="manifest" href="manifest.json">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body, html {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
        }}
        
        #webview {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .loading {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .loading h2 {{
            font-size: 24px;
            color: #333;
            margin-bottom: 20px;
        }}
        
        .spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .offline-indicator {{
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: #e74c3c;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            z-index: 2000;
            display: none;
        }}
        
        .offline-indicator.online {{
            background: #27ae60;
        }}
    </style>
</head>
<body>
    <div id="offline-indicator" class="offline-indicator">No Internet Connection</div>
    
    <div id="loading" class="loading">
        <h2>Loading {metadata.title}...</h2>
        <div class="spinner"></div>
    </div>
    
    <iframe id="webview" style="display: none;"></iframe>
    
    <script>
        let isDeviceReady = false;
        let isWebsiteLoaded = false;
        let isOnline = navigator.onLine;
        let offlineIndicator = document.getElementById('offline-indicator');
        
        // Register service worker for offline support
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('sw.js')
                .then(function(registration) {{
                    console.log('Service Worker registered:', registration);
                }})
                .catch(function(error) {{
                    console.log('Service Worker registration failed:', error);
                }});
        }}
        
        // Handle online/offline status
        window.addEventListener('online', function() {{
            console.log('Device is online');
            isOnline = true;
            offlineIndicator.textContent = 'Connected';
            offlineIndicator.className = 'offline-indicator online';
            offlineIndicator.style.display = 'block';
            setTimeout(function() {{
                offlineIndicator.style.display = 'none';
            }}, 3000);
            
            // Reload content when back online
            if (isWebsiteLoaded) {{
                document.getElementById('webview').src = '{target_url}';
            }}
        }});
        
        window.addEventListener('offline', function() {{
            console.log('Device is offline');
            isOnline = false;
            offlineIndicator.textContent = 'No Internet Connection';
            offlineIndicator.className = 'offline-indicator';
            offlineIndicator.style.display = 'block';
            
            // Show offline page
            showOfflinePage();
        }});
        
        // Cordova device ready event
        document.addEventListener('deviceready', function() {{
            console.log('Cordova device ready');
            isDeviceReady = true;
            checkConnectionAndLoad();
        }}, false);
        
        // Fallback for web browser testing
        setTimeout(function() {{
            if (!isDeviceReady) {{
                console.log('Fallback: Loading in browser');
                checkConnectionAndLoad();
            }}
        }}, 1000);
        
        function checkConnectionAndLoad() {{
            if (isOnline) {{
                loadWebsite();
            }} else {{
                showOfflinePage();
            }}
        }}
        
        function loadWebsite() {{
            const loading = document.getElementById('loading');
            const webview = document.getElementById('webview');
            
            webview.onload = function() {{
                console.log('Website loaded successfully');
                loading.style.display = 'none';
                webview.style.display = 'block';
                isWebsiteLoaded = true;
            }};
            
            webview.onerror = function() {{
                console.error('Failed to load website');
                showOfflinePage();
            }};
            
            // Set timeout for loading
            setTimeout(function() {{
                if (!isWebsiteLoaded) {{
                    console.warn('Website loading timeout');
                    showOfflinePage();
                }}
            }}, 15000);
            
            webview.src = '{target_url}';
        }}
        
        function showOfflinePage() {{
            const loading = document.getElementById('loading');
            const webview = document.getElementById('webview');
            
            loading.style.display = 'none';
            webview.style.display = 'block';
            webview.src = 'offline.html';
            
            offlineIndicator.style.display = 'block';
        }}
        
        // Handle external links
        document.addEventListener('click', function(e) {{
            if (e.target.tagName === 'A' && e.target.href) {{
                e.preventDefault();
                if (typeof cordova !== 'undefined' && cordova.InAppBrowser) {{
                    cordova.InAppBrowser.open(e.target.href, '_system');
                }} else {{
                    window.open(e.target.href, '_blank');
                }}
            }}
        }});
        
        // Handle Cordova network information
        document.addEventListener('deviceready', function() {{
            if (typeof navigator.connection !== 'undefined') {{
                navigator.connection.addEventListener('change', function() {{
                    const networkState = navigator.connection.type;
                    console.log('Network status changed:', networkState);
                    
                    if (networkState === 'none') {{
                        isOnline = false;
                        showOfflinePage();
                    }} else {{
                        isOnline = true;
                        if (!isWebsiteLoaded) {{
                            loadWebsite();
                        }}
                    }}
                }});
            }}
        }});
    </script>
    
    <script src="cordova.js"></script>
</body>
</html>"""
    
    def _create_modern_build_scripts(self, project_dir, app_name):
        """Create modern build scripts with improved error handling"""
        
        # Enhanced Windows build script
        windows_script = f"""@echo off
echo ================================
echo Building {app_name} APK
echo ================================
echo.

echo [1/4] Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Adding Android platform...
call npx cordova platform add android
if %errorlevel% neq 0 (
    echo WARNING: Platform add failed, continuing...
)

echo.
echo [3/4] Preparing project...
call npx cordova prepare android
if %errorlevel% neq 0 (
    echo ERROR: Failed to prepare project
    pause
    exit /b 1
)

echo.
echo [4/4] Building APK...
call npx cordova build android --debug
if %errorlevel% neq 0 (
    echo ERROR: APK build failed
    echo.
    echo Troubleshooting tips:
    echo - Ensure Android SDK is installed
    echo - Check Java JDK version (recommended: JDK 11 or 17)
    echo - Verify ANDROID_HOME environment variable
    pause
    exit /b 1
)

echo.
echo ================================
echo APK BUILD SUCCESSFUL!
echo ================================
echo.
echo APK location: platforms\\android\\app\\build\\outputs\\apk\\debug\\
echo File: app-debug.apk
echo.
pause
"""
        
        # Enhanced Linux/Mac build script
        unix_script = f"""#!/bin/bash
echo "================================"
echo "Building {app_name} APK"
echo "================================"
echo

echo "[1/4] Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "[2/4] Adding Android platform..."
npx cordova platform add android
if [ $? -ne 0 ]; then
    echo "WARNING: Platform add failed, continuing..."
fi

echo
echo "[3/4] Preparing project..."
npx cordova prepare android
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to prepare project"
    exit 1
fi

echo
echo "[4/4] Building APK..."
npx cordova build android --debug
if [ $? -ne 0 ]; then
    echo "ERROR: APK build failed"
    echo
    echo "Troubleshooting tips:"
    echo "- Ensure Android SDK is installed"
    echo "- Check Java JDK version (recommended: JDK 11 or 17)"
    echo "- Verify ANDROID_HOME environment variable"
    exit 1
fi

echo
echo "================================"
echo "APK BUILD SUCCESSFUL!"
echo "================================"
echo
echo "APK location: platforms/android/app/build/outputs/apk/debug/"
echo "File: app-debug.apk"
echo
"""
        
        with open(os.path.join(project_dir, 'build_apk.bat'), 'w') as f:
            f.write(windows_script)
        
        with open(os.path.join(project_dir, 'build_apk.sh'), 'w') as f:
            f.write(unix_script)
        
        # Make shell script executable
        try:
            os.chmod(os.path.join(project_dir, 'build_apk.sh'), 0o755)
        except:
            pass
    
    def _generate_offline_page(self, metadata, target_url):
        """Generate offline.html page that displays when no connection is available"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{metadata.title} - Offline</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 20px;
        }}
        
        .offline-container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .offline-icon {{
            font-size: 60px;
            margin-bottom: 20px;
            opacity: 0.8;
        }}
        
        h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .app-name {{
            font-size: 20px;
            margin-bottom: 20px;
            opacity: 0.9;
            font-weight: 500;
        }}
        
        .message {{
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 30px;
            opacity: 0.8;
        }}
        
        .retry-button {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        
        .retry-button:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }}
        
        .features {{
            margin-top: 30px;
            text-align: left;
        }}
        
        .feature {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            font-size: 14px;
            opacity: 0.8;
        }}
        
        .feature-icon {{
            margin-right: 10px;
            font-size: 16px;
        }}
        
        .network-status {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(231, 76, 60, 0.9);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            backdrop-filter: blur(10px);
        }}
        
        .network-status.online {{
            background: rgba(39, 174, 96, 0.9);
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.6; }}
            100% {{ opacity: 1; }}
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
    </style>
</head>
<body>
    <div class="network-status" id="networkStatus">
        📡 Offline
    </div>
    
    <div class="offline-container">
        <div class="offline-icon">📱</div>
        <h1>You're Offline</h1>
        <div class="app-name">{metadata.title}</div>
        <div class="message">
            This app needs an internet connection to load content from the website. 
            Please check your network connection and try again.
        </div>
        
        <button class="retry-button" onclick="retryConnection()">
            <span id="retryText">Try Again</span>
        </button>
        
        <div class="features">
            <div class="feature">
                <span class="feature-icon">🌐</span>
                <span>Connects to: {target_url}</span>
            </div>
            <div class="feature">
                <span class="feature-icon">🔄</span>
                <span>Auto-retry when connection returns</span>
            </div>
            <div class="feature">
                <span class="feature-icon">📱</span>
                <span>Native mobile app experience</span>
            </div>
        </div>
    </div>
    
    <script>
        let retryAttempts = 0;
        const maxRetries = 3;
        
        // Monitor network status
        function updateNetworkStatus() {{
            const networkStatus = document.getElementById('networkStatus');
            if (navigator.onLine) {{
                networkStatus.textContent = '📡 Online';
                networkStatus.className = 'network-status online';
                // Auto-retry when connection is restored
                setTimeout(retryConnection, 1000);
            }} else {{
                networkStatus.textContent = '📡 Offline';
                networkStatus.className = 'network-status';
            }}
        }}
        
        function retryConnection() {{
            const retryButton = document.querySelector('.retry-button');
            const retryText = document.getElementById('retryText');
            
            if (!navigator.onLine) {{
                retryText.textContent = 'Still Offline';
                setTimeout(() => {{
                    retryText.textContent = 'Try Again';
                }}, 2000);
                return;
            }}
            
            retryAttempts++;
            retryText.textContent = 'Connecting...';
            retryButton.classList.add('pulse');
            
            // Test connection by trying to load the main page
            fetch('{target_url}', {{ 
                method: 'HEAD',
                cache: 'no-cache',
                mode: 'no-cors'
            }})
            .then(() => {{
                // Connection successful, redirect to main app
                window.location.href = 'index.html';
            }})
            .catch(() => {{
                // Connection failed
                retryButton.classList.remove('pulse');
                if (retryAttempts >= maxRetries) {{
                    retryText.textContent = 'Connection Failed';
                    setTimeout(() => {{
                        retryText.textContent = 'Try Again';
                        retryAttempts = 0;
                    }}, 3000);
                }} else {{
                    retryText.textContent = `Retry (${{retryAttempts}}/${{maxRetries}})`;
                    setTimeout(() => {{
                        retryText.textContent = 'Try Again';
                    }}, 2000);
                }}
            }});
        }}
        
        // Listen for network status changes
        window.addEventListener('online', updateNetworkStatus);
        window.addEventListener('offline', updateNetworkStatus);
        
        // Initial network status check
        updateNetworkStatus();
        
        // Auto-retry every 30 seconds when offline
        setInterval(() => {{
            if (!navigator.onLine) {{
                updateNetworkStatus();
            }}
        }}, 30000);
    </script>
</body>
</html>"""
    
    def _generate_service_worker(self, target_url):
        """Generate service worker for offline support"""
        return f"""// Service Worker for offline support
const CACHE_NAME = 'offline-cache-v1';
const OFFLINE_URL = 'offline.html';

// Install event - cache offline page
self.addEventListener('install', event => {{
    console.log('Service Worker installing');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {{
                console.log('Caching offline page');
                return cache.addAll([
                    OFFLINE_URL,
                    'index.html',
                    'manifest.json'
                ]);
            }})
            .then(() => self.skipWaiting())
    );
}});

// Activate event - clean up old caches
self.addEventListener('activate', event => {{
    console.log('Service Worker activating');
    event.waitUntil(
        caches.keys().then(cacheNames => {{
            return Promise.all(
                cacheNames.map(cacheName => {{
                    if (cacheName !== CACHE_NAME) {{
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }}
                }})
            );
        }}).then(() => self.clients.claim())
    );
}});

// Fetch event - serve offline page when network fails
self.addEventListener('fetch', event => {{
    // Only handle navigation requests (page loads)
    if (event.request.mode === 'navigate') {{
        event.respondWith(
            fetch(event.request)
                .catch(() => {{
                    console.log('Network failed, serving offline page');
                    return caches.match(OFFLINE_URL);
                }})
        );
    }}
}});

// Handle background sync (when connection is restored)
self.addEventListener('sync', event => {{
    console.log('Background sync event:', event.tag);
    if (event.tag === 'retry-connection') {{
        event.waitUntil(
            // Notify the main app that connection might be available
            self.clients.matchAll().then(clients => {{
                clients.forEach(client => {{
                    client.postMessage({{
                        type: 'CONNECTION_RETRY',
                        url: '{target_url}'
                    }});
                }});
            }})
        );
    }}
}});

// Handle messages from main app
self.addEventListener('message', event => {{
    if (event.data && event.data.type === 'CHECK_CONNECTION') {{
        // Test connection to the target URL
        fetch('{target_url}', {{ 
            method: 'HEAD',
            cache: 'no-cache',
            mode: 'no-cors'
        }})
        .then(() => {{
            event.source.postMessage({{ type: 'CONNECTION_OK' }});
        }})
        .catch(() => {{
            event.source.postMessage({{ type: 'CONNECTION_FAILED' }});
        }});
    }}
}});"""
    
    def _create_enhanced_documentation(self, project_dir, metadata, target_url):
        """Create comprehensive documentation for the enhanced APK project"""
        
        readme_content = f"""# {metadata.title} - Enhanced Android APK Project

This is an enhanced Cordova-based Android app project that wraps the website **{target_url}** into a native Android application with **full offline page support**.

## 🚀 Quick Start

### Prerequisites
- Node.js (version 14 or higher)
- Java JDK (version 11 or 17 recommended)
- Android SDK with Build Tools
- Android Studio (optional but recommended)

### Environment Setup

1. **Install Android SDK:**
   - Download Android Studio: https://developer.android.com/studio
   - Set ANDROID_HOME environment variable to SDK path
   - Add platform-tools to PATH

2. **Verify Java Installation:**
   ```bash
   java -version
   javac -version
   ```

### Building the APK

#### Windows:
```bash
# Run the automated build script
build_apk.bat
```

#### Linux/Mac:
```bash
# Make the script executable and run
chmod +x build_apk.sh
./build_apk.sh
```

#### Manual Build:
```bash
# Install dependencies
npm install

# Add Android platform
npx cordova platform add android

# Build APK
npx cordova build android --debug
```

## 📱 Features

- **Native Android App**: Full native app experience
- **Offline Page Support**: Shows beautiful offline page instead of URLs when no connection
- **Smart Network Detection**: Real-time network status monitoring with visual indicators
- **Auto-Retry Mechanism**: Automatically attempts to reconnect when internet returns
- **Service Worker**: Advanced offline caching and background sync
- **External Links**: Opens external links in system browser
- **Professional UI**: Loading states, animations, and modern design
- **Connection Resilience**: Handles network interruptions gracefully

## 📂 Project Structure

```
├── www/                 # Web app source files
│   ├── index.html      # Main app interface with network detection
│   ├── offline.html    # Beautiful offline page (shows when no connection)
│   ├── sw.js           # Service worker for offline caching
│   ├── manifest.json   # PWA manifest
│   └── icons/          # Generated app icons
├── config.xml          # Cordova configuration
├── package.json        # Node.js dependencies with modern plugins
├── build_apk.bat       # Windows build script
├── build_apk.sh        # Linux/Mac build script
└── platforms/          # Generated after building
    └── android/        # Android project files
```

## 🔧 Customization

### App Configuration
Edit `config.xml` to customize:
- App name and description
- Package ID
- Permissions
- Plugin settings
- Platform preferences

### App Content
Edit `www/index.html` to modify:
- Loading screen appearance
- Network detection behavior
- Online/offline transitions

Edit `www/offline.html` to customize:
- Offline page design
- Retry button behavior
- App information display

### Build Settings
Edit `package.json` to modify:
- Dependencies
- Build scripts
- App metadata

## 📋 Build Output

After successful build, find your APK at:
```
platforms/android/app/build/outputs/apk/debug/app-debug.apk
```

## 🔍 Troubleshooting

### Common Issues:

1. **"Android SDK not found"**
   - Set ANDROID_HOME environment variable
   - Add Android SDK platform-tools to PATH

2. **"Java version incompatible"**
   - Use Java JDK 11 or 17
   - Avoid Java 18+ (may cause issues)

3. **"Build failed with Gradle error"**
   - Clean project: `npx cordova clean android`
   - Remove platform: `npx cordova platform remove android`
   - Re-add platform: `npx cordova platform add android`

4. **"Plugin compatibility issues"**
   - This project uses modern, compatible plugin versions
   - If issues persist, try `npm update`

### Debug Commands:
```bash
# Check Cordova environment
npx cordova requirements android

# Clean and rebuild
npx cordova clean android
npx cordova build android --debug

# Run on connected device
npx cordova run android
```

## 📄 License

This project was generated by DigitalSkeleton (https://digitalskeleton.com).
The generated app is yours to use and modify as needed.

## 🆘 Support

For issues with:
- **This generated project**: Check troubleshooting section above
- **DigitalSkeleton service**: Visit https://digitalskeleton.com/support
- **Cordova framework**: Visit https://cordova.apache.org/docs/

---

**Target Website**: {target_url}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**DigitalSkeleton Version**: Enhanced APK Builder v2.0
"""
        
        with open(os.path.join(project_dir, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _generate_project_icons(self, project_dir, metadata):
        """Generate and save icons for the APK project"""
        try:
            app_metadata = {
                'icon_url': metadata.icon_url,
                'url': metadata.title
            }
            all_icons = self.icon_generator.generate_all_icons(app_metadata, metadata.title)
            android_icons = all_icons.get('android', {})
            
            if android_icons:
                # Save icons to www directory for the app
                icons_dir = os.path.join(project_dir, 'www', 'icons')
                os.makedirs(icons_dir, exist_ok=True)
                
                for filename, icon_data in android_icons.items():
                    icon_path = os.path.join(icons_dir, filename)
                    with open(icon_path, 'wb') as f:
                        f.write(icon_data)
                
                app.logger.info(f"Generated {len(android_icons)} Android icons")
            else:
                app.logger.warning("No icons generated, using default")
                
        except Exception as e:
            app.logger.warning(f"Icon generation failed: {str(e)}")
    
    def _create_project_zip(self, project_dir, zip_path):
        """Create a ZIP file from the project directory"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_dir)
                    zipf.write(file_path, arcname)
    
    def _sanitize_name(self, name):
        """Sanitize name for use in file paths and package names"""
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        sanitized = re.sub(r'_+', '_', sanitized)
        sanitized = sanitized.strip('_')
        if sanitized and sanitized[0].isdigit():
            sanitized = 'app_' + sanitized
        return sanitized or 'app'