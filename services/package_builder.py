import os
import json
import shutil
import zipfile
import tempfile
from datetime import datetime
from app import app

class PackageBuilder:
    def __init__(self):
        self.output_dir = app.config['UPLOAD_FOLDER']
    
    def build_apk(self, metadata, manifest_data, job_id):
        """
        Build an APK package for Android
        This is a simplified implementation - in production you would use proper Android build tools
        """
        try:
            # Create a temporary directory for building
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create APK structure
                apk_dir = os.path.join(temp_dir, 'apk_build')
                os.makedirs(apk_dir, exist_ok=True)
                
                # Create basic APK structure
                self._create_android_structure(apk_dir, metadata, manifest_data)
                
                # Create the APK file (simplified - just a zip with APK extension)
                apk_filename = f"app_{job_id}.apk"
                apk_path = os.path.join(self.output_dir, apk_filename)
                
                # Create a zip file with APK structure
                with zipfile.ZipFile(apk_path, 'w', zipfile.ZIP_DEFLATED) as apk_zip:
                    for root, dirs, files in os.walk(apk_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, apk_dir)
                            apk_zip.write(file_path, arc_name)
                
                return apk_path
                
        except Exception as e:
            app.logger.error(f"APK build failed: {str(e)}")
            raise Exception(f"APK build failed: {str(e)}")
    
    def _create_android_structure(self, apk_dir, metadata, manifest_data):
        """Create basic Android APK structure"""
        
        # Create AndroidManifest.xml
        manifest_xml = self._generate_android_manifest(metadata, manifest_data)
        with open(os.path.join(apk_dir, 'AndroidManifest.xml'), 'w') as f:
            f.write(manifest_xml)
        
        # Create assets directory with web app files
        assets_dir = os.path.join(apk_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        
        # Create a basic HTML file that loads the web app
        html_content = self._generate_webview_html(metadata)
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
    
    def _generate_webview_html(self, metadata):
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
    <iframe id="webview" src="{metadata.url}" style="display: none;" onload="showWebView()"></iframe>
    
    <script>
        function showWebView() {{
            document.getElementById('loading').style.display = 'none';
            document.getElementById('webview').style.display = 'block';
        }}
        
        // Handle offline scenarios
        window.addEventListener('online', function() {{
            document.getElementById('webview').src = "{metadata.url}";
        }});
    </script>
</body>
</html>"""
    
    def build_mock_package(self, metadata, manifest_data, job_id, package_type):
        """
        Build mock packages for other formats (IPA, MSIX, etc.)
        These are placeholder implementations for demonstration
        """
        try:
            # Create a mock package file
            package_filename = f"app_{job_id}.{package_type}"
            package_path = os.path.join(self.output_dir, package_filename)
            
            # Create a zip file with mock content
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as package_zip:
                # Add manifest
                package_zip.writestr('manifest.json', json.dumps(manifest_data, indent=2))
                
                # Add mock app content based on package type
                if package_type in ['ipa']:
                    self._add_ios_mock_content(package_zip, metadata, manifest_data)
                elif package_type in ['msix', 'msixbundle', 'appx', 'appxbundle']:
                    self._add_windows_mock_content(package_zip, metadata, manifest_data)
                else:
                    # Generic mock content
                    package_zip.writestr('README.txt', f"Mock {package_type.upper()} package for {metadata.title}")
                
                # Add common web app files
                html_content = self._generate_webview_html(metadata)
                package_zip.writestr('index.html', html_content)
            
            return package_path
            
        except Exception as e:
            app.logger.error(f"Mock package build failed: {str(e)}")
            raise Exception(f"Mock package build failed: {str(e)}")
    
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
    
    def _add_windows_mock_content(self, zip_file, metadata, manifest_data):
        """Add mock Windows-specific content"""
        appx_manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10">
    <Identity Name="PWABuilder.{metadata.title.replace(' ', '')}" 
              Publisher="CN=PWABuilder" 
              Version="1.0.0.0" />
    <Properties>
        <DisplayName>{metadata.title}</DisplayName>
        <PublisherDisplayName>PWA Builder</PublisherDisplayName>
        <Description>{metadata.description}</Description>
    </Properties>
    <Applications>
        <Application Id="App" Executable="app.exe" EntryPoint="Windows.FullTrustApplication">
            <uap:VisualElements DisplayName="{metadata.title}" 
                               BackgroundColor="{metadata.background_color}"
                               Square150x150Logo="logo.png" 
                               Square44x44Logo="logo.png" />
        </Application>
    </Applications>
</Package>"""
        zip_file.writestr('AppxManifest.xml', appx_manifest)
        zip_file.writestr('README.txt', 'Mock Windows package - This would contain compiled Windows app binary in production')
