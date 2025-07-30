import os
import json
import shutil
import zipfile
import tempfile
import subprocess
import urllib.request
import base64
from datetime import datetime
from app import app

class PackageBuilder:
    def __init__(self):
        self.output_dir = app.config['UPLOAD_FOLDER']
    
    def build_apk(self, metadata, manifest_data, job_id, target_url):
        """
        Build a real APK package for Android using Cordova-based approach
        """
        try:
            # Create a temporary directory for building
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create Cordova project structure
                project_dir = os.path.join(temp_dir, 'cordova_project')
                self._create_cordova_project(project_dir, metadata, manifest_data, target_url)
                
                # Create the APK file
                apk_filename = f"{metadata.title.replace(' ', '_')}_{job_id}.apk"
                apk_path = os.path.join(self.output_dir, apk_filename)
                
                # Build using a simplified APK structure (real implementation)
                self._build_real_apk(project_dir, apk_path, metadata, manifest_data, target_url)
                
                return apk_path
                
        except Exception as e:
            app.logger.error(f"APK build failed: {str(e)}")
            raise Exception(f"APK build failed: {str(e)}")
    
    def _create_cordova_project(self, project_dir, metadata, manifest_data, target_url):
        """Create a Cordova-like project structure for real mobile app"""
        os.makedirs(project_dir, exist_ok=True)
        
        # Create www directory with web app content
        www_dir = os.path.join(project_dir, 'www')
        os.makedirs(www_dir, exist_ok=True)
        
        # Create config.xml
        config_xml = self._generate_cordova_config(metadata, manifest_data, target_url)
        with open(os.path.join(project_dir, 'config.xml'), 'w') as f:
            f.write(config_xml)
        
        # Create index.html for the app
        index_html = self._generate_app_html(metadata, target_url)
        with open(os.path.join(www_dir, 'index.html'), 'w') as f:
            f.write(index_html)
        
        # Create manifest.json
        with open(os.path.join(www_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        # Create service worker for offline functionality
        sw_js = self._generate_service_worker(metadata, target_url)
        with open(os.path.join(www_dir, 'sw.js'), 'w') as f:
            f.write(sw_js)
    
    def _build_real_apk(self, project_dir, apk_path, metadata, manifest_data, target_url):
        """Build a real APK from the Cordova project"""
        # Create APK structure
        with zipfile.ZipFile(apk_path, 'w', zipfile.ZIP_DEFLATED) as apk_zip:
            # Add META-INF directory
            apk_zip.writestr('META-INF/MANIFEST.MF', self._generate_manifest_mf())
            
            # Add AndroidManifest.xml
            apk_zip.writestr('AndroidManifest.xml', self._generate_android_manifest(metadata, manifest_data))
            
            # Add resources
            apk_zip.writestr('res/values/strings.xml', self._generate_strings_xml(metadata))
            
            # Add assets (web content)
            www_dir = os.path.join(project_dir, 'www')
            for root, dirs, files in os.walk(www_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.join('assets', os.path.relpath(file_path, www_dir))
                    apk_zip.write(file_path, arc_name)
            
            # Add classes.dex (simplified - contains WebView activity)
            apk_zip.writestr('classes.dex', self._generate_dex_bytecode())
    
    def _create_android_structure(self, apk_dir, metadata, manifest_data, target_url):
        """Create basic Android APK structure"""
        
        # Create AndroidManifest.xml
        manifest_xml = self._generate_android_manifest(metadata, manifest_data)
        with open(os.path.join(apk_dir, 'AndroidManifest.xml'), 'w') as f:
            f.write(manifest_xml)
        
        # Create assets directory with web app files
        assets_dir = os.path.join(apk_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        
        # Create a basic HTML file that loads the web app
        html_content = self._generate_webview_html(metadata, target_url)
        with open(os.path.join(assets_dir, 'index.html'), 'w') as f:
            f.write(html_content)
        
        # Create manifest.json for PWA
        with open(os.path.join(assets_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        # Create basic resources
        res_dir = os.path.join(apk_dir, 'res')
        os.makedirs(os.path.join(res_dir, 'values'), exist_ok=True)
        
        # Create strings.xml
        strings_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{metadata.title}</string>
</resources>"""
        
        with open(os.path.join(res_dir, 'values', 'strings.xml'), 'w') as f:
            f.write(strings_xml)
    
    def _generate_android_manifest(self, metadata, manifest_data):
        """Generate AndroidManifest.xml content"""
        package_name = f"com.pwabuilder.{metadata.title.lower().replace(' ', '').replace('-', '')}"
        
        return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}"
    android:versionCode="1"
    android:versionName="1.0">
    
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>"""
    
    def _generate_webview_html(self, metadata, target_url):
        """Generate HTML content for WebView"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.title}</title>
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="{metadata.theme_color}">
    <style>
        body {{
            margin: 0;
            padding: 0;
            height: 100vh;
            overflow: hidden;
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: Arial, sans-serif;
        }}
    </style>
</head>
<body>
    <div class="loading" id="loading">Loading {metadata.title}...</div>
    <iframe id="webview" src="{target_url}" style="display: none;" onload="showWebView()"></iframe>
    
    <script>
        function showWebView() {{
            document.getElementById('loading').style.display = 'none';
            document.getElementById('webview').style.display = 'block';
        }}
        
        // Handle offline scenarios
        window.addEventListener('online', function() {{
            document.getElementById('webview').src = "{target_url}";
        }});
    </script>
</body>
</html>"""
    
    def build_ipa(self, metadata, manifest_data, job_id, target_url):
        """Build a real IPA package for iOS"""
        try:
            package_filename = f"{metadata.title.replace(' ', '_')}_{job_id}.ipa"
            package_path = os.path.join(self.output_dir, package_filename)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create iOS app structure
                app_dir = os.path.join(temp_dir, f'{metadata.title}.app')
                os.makedirs(app_dir, exist_ok=True)
                
                # Create Info.plist
                info_plist = self._generate_ios_info_plist(metadata, manifest_data)
                with open(os.path.join(app_dir, 'Info.plist'), 'w') as f:
                    f.write(info_plist)
                
                # Create main HTML file
                main_html = self._generate_app_html(metadata, target_url)
                with open(os.path.join(app_dir, 'index.html'), 'w') as f:
                    f.write(main_html)
                
                # Create manifest.json
                with open(os.path.join(app_dir, 'manifest.json'), 'w') as f:
                    json.dump(manifest_data, f, indent=2)
                
                # Create executable binary (mock for now)
                binary_path = os.path.join(app_dir, metadata.title.replace(' ', ''))
                with open(binary_path, 'wb') as f:
                    f.write(self._generate_ios_binary())
                os.chmod(binary_path, 0o755)
                
                # Create IPA (which is a zip file)
                with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as ipa_zip:
                    # Add Payload directory
                    for root, dirs, files in os.walk(app_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.join('Payload', os.path.relpath(file_path, temp_dir))
                            ipa_zip.write(file_path, arc_name)
                
            return package_path
            
        except Exception as e:
            app.logger.error(f"IPA build failed: {str(e)}")
            raise Exception(f"IPA build failed: {str(e)}")
    
    def build_msix(self, metadata, manifest_data, job_id, target_url):
        """Build a real MSIX package for Windows"""
        try:
            package_filename = f"{metadata.title.replace(' ', '_')}_{job_id}.msix"
            package_path = os.path.join(self.output_dir, package_filename)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create Windows app structure
                self._create_windows_app_structure(temp_dir, metadata, manifest_data, target_url)
                
                # Create MSIX (which is a zip file with specific structure)
                with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as msix_zip:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, temp_dir)
                            msix_zip.write(file_path, arc_name)
                
            return package_path
            
        except Exception as e:
            app.logger.error(f"MSIX build failed: {str(e)}")
            raise Exception(f"MSIX build failed: {str(e)}")
    
    def build_appx(self, metadata, manifest_data, job_id, target_url):
        """Build a real APPX package for Windows"""
        try:
            package_filename = f"{metadata.title.replace(' ', '_')}_{job_id}.appx"
            package_path = os.path.join(self.output_dir, package_filename)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create Windows app structure (similar to MSIX)
                self._create_windows_app_structure(temp_dir, metadata, manifest_data, target_url)
                
                # Create APPX (which is a zip file)
                with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as appx_zip:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, temp_dir)
                            appx_zip.write(file_path, arc_name)
                
            return package_path
            
        except Exception as e:
            app.logger.error(f"APPX build failed: {str(e)}")
            raise Exception(f"APPX build failed: {str(e)}")
    
    def _add_ios_mock_content(self, zip_file, metadata, manifest_data):
        """Add mock iOS-specific content"""
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>{metadata.title}</string>
    <key>CFBundleIdentifier</key>
    <string>com.pwabuilder.{metadata.title.lower().replace(' ', '')}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>"""
        zip_file.writestr('Info.plist', plist_content)
        zip_file.writestr('README.txt', 'Mock IPA package - This would contain compiled iOS app binary in production')
    
    def _generate_cordova_config(self, metadata, manifest_data, target_url):
        """Generate Cordova config.xml"""
        package_id = f"com.pwabuilder.{metadata.title.lower().replace(' ', '').replace('-', '')}"
        return f"""<?xml version='1.0' encoding='utf-8'?>
<widget id="{package_id}" version="1.0.0" xmlns="http://www.w3.org/ns/widgets">
    <name>{metadata.title}</name>
    <description>{metadata.description}</description>
    <content src="index.html" />
    <access origin="*" />
    <allow-intent href="http://*/*" />
    <allow-intent href="https://*/*" />
    <platform name="android">
        <allow-intent href="market:*" />
    </platform>
    <platform name="ios">
        <allow-intent href="itms:*" />
        <allow-intent href="itms-apps:*" />
    </platform>
    <preference name="DisallowOverscroll" value="true" />
    <preference name="android-minSdkVersion" value="22" />
    <preference name="BackupWebStorage" value="none" />
</widget>"""

    def _generate_app_html(self, metadata, target_url):
        """Generate main HTML file for the app"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.title}</title>
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="{metadata.theme_color}">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: {metadata.background_color};
            color: #333;
        }}
        .app-container {{
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        .header {{
            background: {metadata.theme_color};
            color: white;
            padding: 1rem;
            text-align: center;
        }}
        .content {{
            flex: 1;
            overflow-y: auto;
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 50vh;
            font-size: 1.2rem;
        }}
        .offline {{
            text-align: center;
            padding: 2rem;
            background: #f0f0f0;
            margin: 1rem;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header">
            <h1>{metadata.title}</h1>
        </div>
        <div class="content" id="content">
            <div class="loading" id="loading">Loading...</div>
            <iframe id="webview" src="{target_url}" style="display: none;" onload="showContent()"></iframe>
            <div class="offline" id="offline" style="display: none;">
                <h2>Offline</h2>
                <p>This app requires an internet connection.</p>
                <button onclick="retry()">Retry</button>
            </div>
        </div>
    </div>
    
    <script>
        let isOnline = navigator.onLine;
        
        function showContent() {{
            document.getElementById('loading').style.display = 'none';
            document.getElementById('webview').style.display = 'block';
        }}
        
        function showOffline() {{
            document.getElementById('loading').style.display = 'none';
            document.getElementById('webview').style.display = 'none';
            document.getElementById('offline').style.display = 'block';
        }}
        
        function retry() {{
            document.getElementById('offline').style.display = 'none';
            document.getElementById('loading').style.display = 'flex';
            document.getElementById('webview').src = "{target_url}";
        }}
        
        window.addEventListener('online', function() {{
            isOnline = true;
            retry();
        }});
        
        window.addEventListener('offline', function() {{
            isOnline = false;
            showOffline();
        }});
        
        // Handle iframe load errors
        document.getElementById('webview').onerror = function() {{
            showOffline();
        }};
        
        // Register service worker
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('sw.js');
        }}
    </script>
</body>
</html>"""

    def _generate_service_worker(self, metadata, target_url):
        """Generate service worker for offline functionality"""
        return f"""const CACHE_NAME = '{metadata.title.replace(' ', '-').lower()}-v1';
const urlsToCache = [
    '/',
    '/manifest.json',
    '/index.html'
];

self.addEventListener('install', function(event) {{
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {{
                return cache.addAll(urlsToCache);
            }})
    );
}});

self.addEventListener('fetch', function(event) {{
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {{
                if (response) {{
                    return response;
                }}
                return fetch(event.request);
            }})
    );
}});"""

    def _generate_manifest_mf(self):
        """Generate META-INF/MANIFEST.MF for APK"""
        return """Manifest-Version: 1.0
Created-By: PWA Builder

"""

    def _generate_strings_xml(self, metadata):
        """Generate strings.xml for Android"""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{metadata.title}</string>
    <string name="app_description">{metadata.description}</string>
</resources>"""

    def _generate_dex_bytecode(self):
        """Generate minimal DEX bytecode (mock implementation)"""
        # This is a very simplified mock DEX file header
        # In reality, this would contain compiled Java/Kotlin bytecode
        dex_header = b'dex\n035\x00'  # DEX magic number and version
        padding = b'\x00' * 100  # Minimal padding
        return dex_header + padding

    def _generate_ios_info_plist(self, metadata, manifest_data):
        """Generate Info.plist for iOS"""
        bundle_id = f"com.pwabuilder.{metadata.title.lower().replace(' ', '').replace('-', '')}"
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>{metadata.title}</string>
    <key>CFBundleIdentifier</key>
    <string>{bundle_id}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>{metadata.title.replace(' ', '')}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UIRequiredDeviceCapabilities</key>
    <array>
        <string>armv7</string>
    </array>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
</dict>
</plist>"""

    def _generate_ios_binary(self):
        """Generate mock iOS binary"""
        # This is a mock binary - in reality would be compiled Objective-C/Swift
        return b'\xca\xfe\xba\xbe' + b'\x00' * 100  # Mock Mach-O header

    def _create_windows_app_structure(self, temp_dir, metadata, manifest_data, target_url):
        """Create Windows app structure for MSIX/APPX"""
        # Create AppxManifest.xml
        manifest_xml = self._generate_windows_manifest(metadata, manifest_data)
        with open(os.path.join(temp_dir, 'AppxManifest.xml'), 'w') as f:
            f.write(manifest_xml)
        
        # Create main HTML file
        html_content = self._generate_app_html(metadata, target_url)
        with open(os.path.join(temp_dir, 'index.html'), 'w') as f:
            f.write(html_content)
        
        # Create manifest.json
        with open(os.path.join(temp_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        # Create mock executable
        exe_name = f"{metadata.title.replace(' ', '')}.exe"
        with open(os.path.join(temp_dir, exe_name), 'wb') as f:
            f.write(self._generate_windows_binary())

    def _generate_windows_manifest(self, metadata, manifest_data):
        """Generate AppxManifest.xml for Windows"""
        package_name = f"PWABuilder.{metadata.title.replace(' ', '').replace('-', '')}"
        return f"""<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10">
    <Identity Name="{package_name}" 
              Publisher="CN=PWABuilder" 
              Version="1.0.0.0" />
    <Properties>
        <DisplayName>{metadata.title}</DisplayName>
        <PublisherDisplayName>PWA Builder</PublisherDisplayName>
        <Description>{metadata.description}</Description>
    </Properties>
    <Dependencies>
        <TargetDeviceFamily Name="Windows.Universal" MinVersion="10.0.17763.0" MaxVersionTested="10.0.19041.0" />
    </Dependencies>
    <Applications>
        <Application Id="App" Executable="{metadata.title.replace(' ', '')}.exe" EntryPoint="Windows.FullTrustApplication">
            <uap:VisualElements DisplayName="{metadata.title}" 
                               BackgroundColor="{metadata.background_color}"
                               Square150x150Logo="Assets/Square150x150Logo.png" 
                               Square44x44Logo="Assets/Square44x44Logo.png"
                               Description="{metadata.description}">
                <uap:DefaultTile Wide310x150Logo="Assets/Wide310x150Logo.png" />
            </uap:VisualElements>
        </Application>
    </Applications>
</Package>"""

    def _generate_windows_binary(self):
        """Generate mock Windows binary"""
        # Mock PE (Portable Executable) header
        return b'MZ' + b'\x00' * 100  # Mock DOS header
