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
        """Generate enhanced index.html with better error handling and loading states"""
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
        
        .error {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            max-width: 300px;
            z-index: 1000;
        }}
        
        .error h3 {{
            color: #e74c3c;
            margin-bottom: 15px;
        }}
        
        .error p {{
            color: #666;
            margin-bottom: 20px;
            line-height: 1.4;
        }}
        
        .retry-btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }}
        
        .retry-btn:hover {{
            background: #2980b9;
        }}
    </style>
</head>
<body>
    <div id="loading" class="loading">
        <h2>Loading {metadata.title}...</h2>
        <div class="spinner"></div>
    </div>
    
    <div id="error" class="error" style="display: none;">
        <h3>Connection Error</h3>
        <p>Unable to load the website. Please check your internet connection and try again.</p>
        <button class="retry-btn" onclick="location.reload()">Retry</button>
    </div>
    
    <iframe id="webview" style="display: none;"></iframe>
    
    <script>
        let isDeviceReady = false;
        let isWebsiteLoaded = false;
        
        // Cordova device ready event
        document.addEventListener('deviceready', function() {{
            console.log('Cordova device ready');
            isDeviceReady = true;
            if (!isWebsiteLoaded) {{
                loadWebsite();
            }}
        }}, false);
        
        // Fallback for web browser testing
        setTimeout(function() {{
            if (!isDeviceReady) {{
                console.log('Fallback: Loading website in browser');
                loadWebsite();
            }}
        }}, 1000);
        
        function loadWebsite() {{
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const webview = document.getElementById('webview');
            
            webview.onload = function() {{
                console.log('Website loaded successfully');
                loading.style.display = 'none';
                webview.style.display = 'block';
                isWebsiteLoaded = true;
            }};
            
            webview.onerror = function() {{
                console.error('Failed to load website');
                loading.style.display = 'none';
                error.style.display = 'block';
            }};
            
            // Set timeout for loading
            setTimeout(function() {{
                if (!isWebsiteLoaded) {{
                    console.warn('Website loading timeout');
                    loading.style.display = 'none';
                    error.style.display = 'block';
                }}
            }}, 15000);
            
            webview.src = '{target_url}';
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
        
        // Handle network status
        if (typeof navigator !== 'undefined' && navigator.connection) {{
            navigator.connection.addEventListener('change', function() {{
                console.log('Network status changed:', navigator.connection.type);
            }});
        }}
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
    
    def _create_enhanced_documentation(self, project_dir, metadata, target_url):
        """Create comprehensive documentation for the enhanced APK project"""
        
        readme_content = f"""# {metadata.title} - Enhanced Android APK Project

This is an enhanced Cordova-based Android app project that wraps the website **{target_url}** into a native Android application.

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
- **Offline Capability**: Basic offline support
- **Network Detection**: Automatic network status monitoring
- **External Links**: Opens external links in system browser
- **Splash Screen**: Professional loading experience
- **Error Handling**: Comprehensive error messages and retry functionality

## 📂 Project Structure

```
├── www/                 # Web app source files
│   ├── index.html      # Main app interface
│   └── manifest.json   # PWA manifest
├── config.xml          # Cordova configuration
├── package.json        # Node.js dependencies
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
- Error messages
- App behavior

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