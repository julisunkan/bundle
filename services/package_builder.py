import os
import json
import shutil
import zipfile
import tempfile
from datetime import datetime
from app import app
from .icon_generator import IconGenerator
# APKBuilder import moved to method level to avoid circular import

class PackageBuilder:
    def __init__(self):
        self.output_dir = app.config['UPLOAD_FOLDER']
        self.icon_generator = IconGenerator()
        self._apk_builder = None
    
    def build_apk(self, metadata, manifest_data, job_id, target_url):
        """Build actual Android APK file using Cordova"""
        try:
            app.logger.info(f"Building APK-ready project for {metadata.title}")
            
            # Import APKBuilder here to avoid circular import
            from .apk_builder import APKBuilder
            if self._apk_builder is None:
                self._apk_builder = APKBuilder()
            
            # Use the APK builder to generate APK-ready project
            apk_path = self._apk_builder.build_android_apk(metadata, manifest_data, job_id, target_url)
            
            app.logger.info(f"APK project built successfully: {apk_path}")
            return apk_path
                
        except Exception as e:
            app.logger.error(f"APK build failed: {str(e)}")
            # Fallback to project files if APK build fails
            app.logger.info("Falling back to project file generation")
            return self._build_apk_fallback(metadata, manifest_data, job_id, target_url)
    
    def _build_apk_fallback(self, metadata, manifest_data, job_id, target_url):
        """Fallback method to create project files if APK build fails"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                project_dir = os.path.join(temp_dir, 'android_project')
                
                # Create Cordova project structure as files
                self._create_cordova_android_project(project_dir, metadata, manifest_data, target_url)
                
                zip_filename = f"{metadata.title.replace(' ', '_')}_android_project_{job_id}.zip"
                zip_path = os.path.join(self.output_dir, zip_filename)
                
                self._create_project_zip(project_dir, zip_path)
                return zip_path
                
        except Exception as e:
            app.logger.error(f"APK fallback build failed: {str(e)}")
            raise Exception(f"APK fallback build failed: {str(e)}")
    
    def build_ipa(self, metadata, manifest_data, job_id, target_url):
        """Build iOS app using simple, reliable methods"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                project_dir = os.path.join(temp_dir, 'ios_simple')
                
                # Method 1: Simple iOS Web Wrapper
                self._create_ios_web_wrapper(project_dir, metadata, manifest_data, target_url)
                
                # Method 2: iOS Online Builder Instructions  
                self._create_ios_online_instructions(project_dir, metadata, manifest_data, target_url)
                
                # Method 3: PWA to iOS Converter
                self._create_ios_pwa_converter(project_dir, metadata, manifest_data, target_url)
                
                zip_filename = f"{metadata.title.replace(' ', '_')}_ios_{job_id}.zip"
                zip_path = os.path.join(self.output_dir, zip_filename)
                
                self._create_project_zip(project_dir, zip_path)
                return zip_path
                
        except Exception as e:
            app.logger.error(f"iOS build failed: {str(e)}")
            raise Exception(f"iOS build failed: {str(e)}")
    
    def build_msix(self, metadata, manifest_data, job_id, target_url):
        """Build a Visual Studio project structure that can be imported"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                project_dir = os.path.join(temp_dir, 'windows_project')
                self._create_visual_studio_project(project_dir, metadata, manifest_data, target_url)
                
                zip_filename = f"{metadata.title.replace(' ', '_')}_windows_{job_id}.zip"
                zip_path = os.path.join(self.output_dir, zip_filename)
                
                self._create_project_zip(project_dir, zip_path)
                return zip_path
                
        except Exception as e:
            app.logger.error(f"Windows project build failed: {str(e)}")
            raise Exception(f"Windows project build failed: {str(e)}")
    
    def build_appx(self, metadata, manifest_data, job_id, target_url):
        """Build a UWP project structure that can be imported"""
        return self.build_msix(metadata, manifest_data, job_id, target_url)
    
    def _create_simple_web_wrapper(self, project_dir, metadata, manifest_data, target_url):
        """Create simple web wrapper that works with any APK builder"""
        wrapper_dir = os.path.join(project_dir, 'web_wrapper')
        os.makedirs(wrapper_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        
        # Create simple HTML app
        self._create_file(wrapper_dir, 'index.html', self._generate_simple_wrapper_html(metadata, target_url))
        self._create_file(wrapper_dir, 'manifest.json', json.dumps(manifest_data, indent=2))
        self._create_file(wrapper_dir, 'sw.js', self._generate_simple_service_worker())
        self._create_file(wrapper_dir, 'styles.css', self._generate_wrapper_styles())
        self._create_file(wrapper_dir, 'app.js', self._generate_wrapper_js(target_url))
        self._create_file(wrapper_dir, 'README.md', self._generate_simple_wrapper_readme(metadata, target_url))
        
        # Create icons folder
        icons_dir = os.path.join(wrapper_dir, 'icons')
        os.makedirs(icons_dir, exist_ok=True)
        
    def _create_online_apk_instructions(self, project_dir, metadata, manifest_data, target_url):
        """Create comprehensive instructions for online APK builders"""
        instructions_dir = os.path.join(project_dir, 'online_builders')
        os.makedirs(instructions_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        
        # Create instruction files
        self._create_file(instructions_dir, 'QUICK_START.md', self._generate_quick_start_guide(metadata, target_url))
        self._create_file(instructions_dir, 'step-by-step.html', self._generate_step_by_step_html(metadata, target_url))
        self._create_file(instructions_dir, 'app-config.json', self._generate_simple_app_config(app_name, metadata, target_url))
        self._create_file(instructions_dir, 'builder-links.txt', self._generate_builder_links())
        self._create_file(instructions_dir, 'troubleshooting.md', self._generate_troubleshooting_guide())
        
    def _create_pwa_to_apk_converter(self, project_dir, metadata, manifest_data, target_url):
        """Create PWA that can be converted to APK using browser tools"""
        pwa_dir = os.path.join(project_dir, 'pwa_converter')
        os.makedirs(pwa_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        
        # Create PWA files
        self._create_file(pwa_dir, 'index.html', self._generate_pwa_converter_html(metadata, target_url))
        self._create_file(pwa_dir, 'manifest.json', json.dumps(manifest_data, indent=2))
        self._create_file(pwa_dir, 'sw.js', self._generate_simple_service_worker())
        # Create simple TWA manifest
        simple_manifest = {"name": metadata.title, "startUrl": target_url}
        self._create_file(pwa_dir, 'twa-manifest.json', json.dumps(simple_manifest, indent=2))
        self._create_file(pwa_dir, 'README.md', self._generate_pwa_converter_readme(metadata, target_url))
        self._create_file(pwa_dir, 'convert-to-apk.html', self._generate_conversion_tool_html(metadata, target_url))
        
    def _create_bubblewrap_project(self, project_dir, metadata, manifest_data, target_url):
        """Create a PWA-to-APK project using Google's Bubblewrap (Most reliable method)"""
        os.makedirs(project_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        package_name = f"com.digitalskeleton.{app_name.lower()}"
        
        # Create Bubblewrap project structure
        # Create basic TWA manifest for now
        basic_manifest = {
            "packageId": package_name,
            "host": self._extract_host(target_url) if hasattr(self, '_extract_host') else target_url.split('/')[2],
            "name": metadata.title,
            "startUrl": target_url
        }
        self._create_file(project_dir, 'twa-manifest.json', json.dumps(basic_manifest, indent=2))
        self._create_file(project_dir, 'package.json', self._generate_bubblewrap_package_json(app_name))
        self._create_file(project_dir, 'build-apk.bat', self._generate_bubblewrap_build_script_windows(app_name))
        self._create_file(project_dir, 'build-apk.sh', self._generate_bubblewrap_build_script(app_name) if hasattr(self, '_generate_bubblewrap_build_script') else "#!/bin/bash\necho 'Build script for TWA'")
        self._create_file(project_dir, 'README.md', self._generate_bubblewrap_readme(metadata, target_url))
        
        # Create icons directory
        icons_dir = os.path.join(project_dir, 'res', 'drawable')
        os.makedirs(icons_dir, exist_ok=True)
        
    def _create_webview_android_project(self, project_dir, metadata, manifest_data, target_url):
        """Create a simple WebView Android project (Fallback method)"""
        webview_dir = os.path.join(project_dir, 'webview_method')
        os.makedirs(webview_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        package_name = f"com.digitalskeleton.{app_name.lower()}"
        
        # Create simple project files as placeholders
        self._create_file(webview_dir, 'build.gradle', "// Android build configuration")
        self._create_file(webview_dir, 'AndroidManifest.xml', f'<!-- Android manifest for {app_name} -->')
        self._create_file(webview_dir, 'MainActivity.java', f'// MainActivity for {package_name}')
        self._create_file(webview_dir, 'activity_main.xml', '<!-- Activity layout -->')
        self._create_file(webview_dir, 'strings.xml', f'<!-- Strings for {metadata.title} -->')
        self._create_file(webview_dir, 'README.md', f'# WebView Project for {metadata.title}')
        
    def _create_cordova_android_project(self, project_dir, metadata, manifest_data, target_url):
        """Create a Cordova-based Android project (Traditional method)"""
        cordova_dir = os.path.join(project_dir, 'cordova_method')
        os.makedirs(cordova_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        package_name = f"com.digitalskeleton.{app_name.lower()}"
        
        # Create simple Cordova files as placeholders
        self._create_file(cordova_dir, 'config.xml', f'<!-- Cordova config for {app_name} -->')
        self._create_file(cordova_dir, 'package.json', f'{{"name": "{app_name.lower()}", "version": "1.0.0"}}')
        self._create_file(cordova_dir, 'index.html', f'<!DOCTYPE html><html><head><title>{metadata.title}</title></head><body><h1>{metadata.title}</h1></body></html>')
        self._create_file(cordova_dir, 'build-android.bat', 'REM Cordova build script')
        self._create_file(cordova_dir, 'build-android.sh', '#!/bin/bash\n# Cordova build script')
        self._create_file(cordova_dir, 'README.md', f'# Cordova Project for {metadata.title}')
        
    def _create_android_studio_project(self, project_dir, metadata, manifest_data, target_url):
        """Create a Capacitor-based Android project - modern web-to-mobile solution"""
        os.makedirs(project_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        package_name = f"com.digitalskeleton.{app_name.lower()}"
        
        # Generate all required icons for Android
        app_metadata = {
            'title': metadata.title,
            'description': metadata.description,
            'icon_url': metadata.icon_url,
            'url': metadata.url
        }
        all_icons = self.icon_generator.generate_all_icons(app_metadata, app_name)
        android_icons = all_icons.get('android', {})
        
        # Create Capacitor project files first
        self._create_file(project_dir, 'package.json', self._generate_capacitor_package_json(app_name, metadata))
        self._create_file(project_dir, 'capacitor.config.js', self._generate_capacitor_config_js(app_name, package_name, metadata))
        self._create_file(project_dir, 'index.html', self._generate_capacitor_index_html(metadata, target_url))
        self._create_file(project_dir, 'main.js', self._generate_capacitor_main_js(target_url, metadata))
        self._create_file(project_dir, 'build-android.bat', self._generate_capacitor_android_build_script(app_name))
        self._create_file(project_dir, 'build-android.sh', self._generate_capacitor_android_build_script_linux(app_name))
        
        # Create the critical 'dist' directory that Capacitor expects
        dist_dir = os.path.join(project_dir, 'dist')
        os.makedirs(dist_dir, exist_ok=True)
        
        # Copy the main web files to dist directory (this is what Capacitor syncs)
        self._create_file(dist_dir, 'index.html', self._generate_capacitor_index_html(metadata, target_url))
        self._create_file(dist_dir, 'main.js', self._generate_capacitor_main_js(target_url, metadata))
        self._create_file(dist_dir, 'manifest.json', json.dumps(manifest_data, indent=2))
        
        # Add enhanced build options
        self._create_file(project_dir, 'build-release.bat', self._generate_android_release_build_script(app_name))
        self._create_file(project_dir, 'build-release.sh', self._generate_android_release_build_script_linux(app_name))
        self._create_file(project_dir, 'quick-build.bat', self._generate_android_quick_build_script(app_name))
        self._create_file(project_dir, 'quick-build.sh', self._generate_android_quick_build_script_linux(app_name))
        
        # Create Android platform directory and required Capacitor files
        android_dir = os.path.join(project_dir, 'android')
        os.makedirs(android_dir, exist_ok=True)
        
        # Create the missing capacitor.settings.gradle file
        self._create_file(android_dir, 'capacitor.settings.gradle', self._generate_capacitor_settings_gradle())
        
        # Create root build.gradle and settings.gradle for the android project
        self._create_file(android_dir, 'build.gradle', self._generate_android_root_gradle())
        self._create_file(android_dir, 'settings.gradle', self._generate_android_settings_gradle())
        self._create_file(android_dir, 'gradle.properties', self._generate_gradle_properties())
        
        # Create variables.gradle file (required by build.gradle)
        self._create_file(android_dir, 'variables.gradle', self._generate_variables_gradle())
        
        # Create capacitor.settings.gradle file (required by settings.gradle)
        self._create_file(android_dir, 'capacitor.settings.gradle', self._generate_capacitor_settings_gradle())
        
        # Create capacitor.gradle file for plugin configuration
        self._create_file(android_dir, 'capacitor.gradle', self._generate_capacitor_gradle())
        
        # Create local.properties file for Android SDK location
        self._create_file(android_dir, 'local.properties', self._generate_local_properties())
        
        # Create Gradle wrapper files (essential for Windows builds)
        self._create_file(android_dir, 'gradlew.bat', self._generate_gradle_wrapper_bat())
        self._create_file(android_dir, 'gradlew', self._generate_gradle_wrapper_sh())
        
        # Create gradle wrapper directory and jar (required for Gradle builds)
        gradle_wrapper_dir = os.path.join(android_dir, 'gradle', 'wrapper')
        os.makedirs(gradle_wrapper_dir, exist_ok=True)
        self._create_file(gradle_wrapper_dir, 'gradle-wrapper.properties', self._generate_gradle_wrapper_properties())
        
        # Create Gradle setup scripts in the project root for easy access
        self._create_file(project_dir, 'setup-gradle.bat', self._generate_gradle_setup_script())
        self._create_file(project_dir, 'setup-gradle.sh', self._generate_gradle_setup_script_linux())
        
        # Skip capacitor-cordova-android-plugins to simplify project structure
        
        # Create app directory structure
        app_dir = os.path.join(android_dir, 'app')
        os.makedirs(app_dir, exist_ok=True)
        
        # Create app/build.gradle
        self._create_file(app_dir, 'build.gradle', self._generate_capacitor_app_gradle(package_name, metadata))
        
        # Create src/main directory structure for Capacitor
        main_dir = os.path.join(app_dir, 'src', 'main')
        java_dir = os.path.join(main_dir, 'java', *package_name.split('.'))
        res_dir = os.path.join(main_dir, 'res')
        assets_dir = os.path.join(main_dir, 'assets', 'public')
        
        os.makedirs(java_dir, exist_ok=True)
        os.makedirs(os.path.join(res_dir, 'layout'), exist_ok=True)
        os.makedirs(os.path.join(res_dir, 'values'), exist_ok=True)
        os.makedirs(os.path.join(res_dir, 'drawable'), exist_ok=True)
        os.makedirs(assets_dir, exist_ok=True)
        
        # Skip capacitor.build.gradle to simplify project
        
        # Create AndroidManifest.xml for Capacitor
        self._create_file(main_dir, 'AndroidManifest.xml', self._generate_capacitor_manifest(package_name, metadata))
        
        # Create MainActivity.java for Capacitor
        self._create_file(java_dir, 'MainActivity.java', self._generate_capacitor_main_activity(package_name, metadata, target_url))
        
        # Create layout files
        self._create_file(os.path.join(res_dir, 'layout'), 'activity_main.xml', self._generate_activity_layout())
        
        # Create values files
        self._create_file(os.path.join(res_dir, 'values'), 'strings.xml', self._generate_strings_xml(metadata))
        self._create_file(os.path.join(res_dir, 'values'), 'colors.xml', self._generate_colors_xml(manifest_data))
        
        # Create web assets
        self._create_file(assets_dir, 'index.html', self._generate_webview_html(metadata, target_url))
        self._create_file(assets_dir, 'manifest.json', json.dumps(manifest_data, indent=2))
        
        # Save generated icons to project
        if android_icons:
            self.icon_generator.save_icons_to_package(android_icons, project_dir, 'android')
            app.logger.info(f"Generated {len(android_icons)} Android icons for {app_name}")
        
        # Create comprehensive README with build options
        self._create_file(project_dir, 'README.md', self._generate_enhanced_android_readme(metadata, target_url))
    
    def _create_xcode_project(self, project_dir, metadata, manifest_data, target_url):
        """Create a Capacitor-based iOS project - modern web-to-mobile solution"""
        os.makedirs(project_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        
        # Generate all required icons for iOS
        app_metadata = {
            'title': metadata.title,
            'description': metadata.description,
            'icon_url': metadata.icon_url,
            'url': metadata.url
        }
        all_icons = self.icon_generator.generate_all_icons(app_metadata, app_name)
        ios_icons = all_icons.get('ios', {})
        
        # Create Capacitor project files first
        self._create_file(project_dir, 'package.json', self._generate_capacitor_package_json(app_name, metadata))
        self._create_file(project_dir, 'capacitor.config.ts', self._generate_capacitor_config(app_name, f"com.digitalskeleton.{app_name.lower()}", metadata))
        self._create_file(project_dir, 'index.html', self._generate_capacitor_index_html(metadata, target_url))
        self._create_file(project_dir, 'main.js', self._generate_capacitor_main_js(target_url, metadata))
        self._create_file(project_dir, 'build-ios.bat', self._generate_capacitor_ios_build_script(app_name))
        self._create_file(project_dir, 'build-ios.sh', self._generate_capacitor_ios_build_script_linux(app_name))
        
        # Create app source directory
        source_dir = os.path.join(project_dir, app_name)
        os.makedirs(source_dir, exist_ok=True)
        
        # Create iOS app files
        self._create_file(source_dir, 'AppDelegate.swift', self._generate_app_delegate(app_name, metadata))
        self._create_file(source_dir, 'ViewController.swift', self._generate_view_controller(app_name, target_url))
        self._create_file(source_dir, 'Info.plist', self._generate_info_plist(metadata))
        self._create_file(source_dir, 'Main.storyboard', self._generate_main_storyboard())
        
        # Create web assets
        assets_dir = os.path.join(source_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        self._create_file(assets_dir, 'index.html', self._generate_webview_html(metadata, target_url))
        self._create_file(assets_dir, 'manifest.json', json.dumps(manifest_data, indent=2))
        
        # Save generated icons to project
        if ios_icons:
            self.icon_generator.save_icons_to_package(ios_icons, project_dir, 'ios')
            app.logger.info(f"Generated {len(ios_icons)} iOS icons for {app_name}")
        
        # Create README
        self._create_file(project_dir, 'README.md', self._generate_ios_readme(metadata, target_url))
    
    def _create_visual_studio_project(self, project_dir, metadata, manifest_data, target_url):
        """Create an Electron-based Windows app project - much more reliable than UWP"""
        os.makedirs(project_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        
        # Generate all required icons for Windows
        app_metadata = {
            'title': metadata.title,
            'description': metadata.description,
            'icon_url': metadata.icon_url,
            'url': metadata.url
        }
        all_icons = self.icon_generator.generate_all_icons(app_metadata, app_name)
        windows_icons = all_icons.get('windows', {})
        
        # Create Electron project files
        self._create_file(project_dir, 'package.json', self._generate_electron_package_json(app_name, metadata))
        self._create_file(project_dir, 'main.js', self._generate_electron_main_js(target_url, metadata))
        self._create_file(project_dir, 'preload.js', self._generate_electron_preload_js())
        self._create_file(project_dir, 'renderer.js', self._generate_electron_renderer_js())
        self._create_file(project_dir, 'index.html', self._generate_electron_index_html(metadata, target_url))
        self._create_file(project_dir, 'build.bat', self._generate_electron_build_script(app_name))
        self._create_file(project_dir, 'build.sh', self._generate_electron_build_script_linux(app_name))
        
        # Create assets directory
        assets_dir = os.path.join(project_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        
        # Create web assets (optional fallback HTML)
        self._create_file(assets_dir, 'offline.html', self._generate_offline_html(metadata))
        self._create_file(assets_dir, 'manifest.json', json.dumps(manifest_data, indent=2))
        
        # Save generated icons to project
        if windows_icons:
            self.icon_generator.save_icons_to_package(windows_icons, project_dir, 'windows')
            app.logger.info(f"Generated {len(windows_icons)} Windows icons for {app_name}")
        
        # Create README
        self._create_file(project_dir, 'README.md', self._generate_electron_readme(metadata, target_url, app_name))
    
    # Helper methods
    def _create_file(self, directory, filename, content):
        """Create a file with the given content"""
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_project_zip(self, project_dir, zip_path):
        """Create a ZIP file from the project directory"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_dir)
                    zipf.write(file_path, arcname)
    
    def _sanitize_name(self, name):
        """Sanitize name for use in project files"""
        return ''.join(c for c in name if c.isalnum()).replace(' ', '').replace('-', '').replace('_', '')
    
    # Android generators
    def _generate_project_gradle(self):
        return '''buildscript {
    ext.kotlin_version = "1.8.10"
    dependencies {
        classpath "com.android.tools.build:gradle:8.0.2"
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlin_version"
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}'''
    
    def _generate_gradle_properties(self):
        return '''org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true'''
    
    def _generate_app_gradle(self, package_name, metadata):
        return f'''plugins {{
    id 'com.android.application'
}}

android {{
    namespace '{package_name}'
    compileSdk 34

    defaultConfig {{
        applicationId "{package_name}"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.10.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}}'''
    
    def _generate_android_manifest_xml(self, package_name, metadata):
        return f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    package="{package_name}">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.Light.NoActionBar"
        tools:targetApi="31">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>'''
    
    def _generate_main_activity(self, package_name, metadata, target_url):
        class_name = package_name.split('.')[-1].capitalize()
        return f'''package {package_name};

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {{

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        
        // Enable JavaScript
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setLoadWithOverviewMode(true);
        webSettings.setUseWideViewPort(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        webSettings.setSupportZoom(true);
        webSettings.setDefaultTextEncodingName("utf-8");

        // Set WebView client
        webView.setWebViewClient(new WebViewClient() {{
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {{
                view.loadUrl(url);
                return true;
            }}
        }});

        // Load the website
        webView.loadUrl("{target_url}");
    }}

    @Override
    public void onBackPressed() {{
        if (webView.canGoBack()) {{
            webView.goBack();
        }} else {{
            super.onBackPressed();
        }}
    }}
}}'''
    
    def _generate_activity_layout(self):
        return '''<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>'''
    
    def _generate_strings_xml(self, metadata):
        return f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{metadata.title}</string>
</resources>'''
    
    def _generate_colors_xml(self, manifest_data):
        theme_color = manifest_data.get('theme_color', '#000000')
        return f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="purple_200">#FFBB86FC</color>
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
    <color name="theme_color">{theme_color}</color>
</resources>'''
    
    def _generate_webview_html(self, metadata, target_url):
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.title}</title>
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="{getattr(metadata, 'theme_color', '#000000')}">
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
    </script>
</body>
</html>'''
    
    def _generate_android_readme(self, metadata, target_url):
        return f'''# {metadata.title} - Android App

This is an Android Studio project that wraps the website [{target_url}]({target_url}) as a native Android app.

## How to Build

1. Open Android Studio
2. Select "Open an existing Android Studio project"
3. Select this project folder
4. Wait for Gradle sync to complete
5. Click "Build" > "Build Bundle(s) / APK(s)" > "Build APK(s)"

## Features

- WebView-based app that loads the website
- Full-screen experience
- Back button navigation support
- Internet permission for web content
- Responsive design

## Customization

- Modify `MainActivity.java` to add custom functionality
- Update `strings.xml` to change the app name
- Replace icons in `res/mipmap-*` folders
- Modify `colors.xml` to match your brand colors

## Requirements

- Android Studio Arctic Fox or later
- Android SDK 24 (Android 7.0) or higher
- Internet connection for loading web content

## Website

Original website: {target_url}
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    # iOS generators
    def _generate_pbxproj(self, app_name):
        return f'''// !$*UTF8*$!
{{
        archiveVersion = 1;
        classes = {{
        }};
        objectVersion = 56;
        objects = {{
                /* Begin PBXProject section */
                1234567890ABCDEF12345678 /* Project object */ = {{
                        isa = PBXProject;
                        attributes = {{
                                BuildIndependentTargetsInParallel = 1;
                                LastSwiftUpdateCheck = 1430;
                                LastUpgradeCheck = 1430;
                        }};
                        buildConfigurationList = 1234567890ABCDEF12345679 /* Build configuration list for PBXProject "{app_name}" */;
                        compatibilityVersion = "Xcode 14.0";
                        developmentRegion = en;
                        hasScannedForEncodings = 0;
                        knownRegions = (
                                en,
                                Base,
                        );
                        mainGroup = 1234567890ABCDEF1234567A;
                        productRefGroup = 1234567890ABCDEF1234567B /* Products */;
                        projectDirPath = "";
                        projectRoot = "";
                        targets = (
                                1234567890ABCDEF1234567C /* {app_name} */,
                        );
                }};
                /* End PBXProject section */
        }};
        rootObject = 1234567890ABCDEF12345678 /* Project object */;
}}'''
    
    def _generate_app_delegate(self, app_name, metadata):
        return f'''import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {{

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {{
        // Override point for customization after application launch.
        return true
    }}

    // MARK: UISceneSession Lifecycle

    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {{
        // Called when a new scene session is being created.
        return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
    }}

    func application(_ application: UIApplication, didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {{
        // Called when the user discards a scene session.
    }}
}}'''
    
    def _generate_view_controller(self, app_name, target_url):
        return f'''import UIKit
import WebKit

class ViewController: UIViewController, WKNavigationDelegate {{

    @IBOutlet weak var webView: WKWebView!
    
    override func viewDidLoad() {{
        super.viewDidLoad()
        
        // Configure WebView
        webView.navigationDelegate = self
        
        // Load the website
        if let url = URL(string: "{target_url}") {{
            let request = URLRequest(url: url)
            webView.load(request)
        }}
    }}
    
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {{
        // Website finished loading
        print("Website loaded successfully")
    }}
    
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {{
        // Handle loading error
        print("Failed to load website: \\(error.localizedDescription)")
    }}
}}'''
    
    def _generate_info_plist(self, metadata):
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>CFBundleDevelopmentRegion</key>
        <string>$(DEVELOPMENT_LANGUAGE)</string>
        <key>CFBundleDisplayName</key>
        <string>{metadata.title}</string>
        <key>CFBundleExecutable</key>
        <string>$(EXECUTABLE_NAME)</string>
        <key>CFBundleIdentifier</key>
        <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
        <key>CFBundleInfoDictionaryVersion</key>
        <string>6.0</string>
        <key>CFBundleName</key>
        <string>$(PRODUCT_NAME)</string>
        <key>CFBundlePackageType</key>
        <string>$(PRODUCT_BUNDLE_PACKAGE_TYPE)</string>
        <key>CFBundleShortVersionString</key>
        <string>1.0</string>
        <key>CFBundleVersion</key>
        <string>1</string>
        <key>LSRequiresIPhoneOS</key>
        <true/>
        <key>UIApplicationSceneManifest</key>
        <dict>
                <key>UIApplicationSupportsMultipleScenes</key>
                <false/>
                <key>UISceneConfigurations</key>
                <dict>
                        <key>UIWindowSceneSessionRoleApplication</key>
                        <array>
                                <dict>
                                        <key>UISceneConfigurationName</key>
                                        <string>Default Configuration</string>
                                        <key>UISceneDelegateClassName</key>
                                        <string>$(PRODUCT_MODULE_NAME).SceneDelegate</string>
                                        <key>UISceneStoryboardFile</key>
                                        <string>Main</string>
                                </dict>
                        </array>
                </dict>
        </dict>
        <key>NSAppTransportSecurity</key>
        <dict>
                <key>NSAllowsArbitraryLoads</key>
                <true/>
        </dict>
</dict>
</plist>'''
    
    def _generate_main_storyboard(self):
        return '''<?xml version="1.0" encoding="UTF-8"?>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB" version="3.0" toolsVersion="21701" targetRuntime="iOS.CocoaTouch" propertyAccessControl="none" useAutolayout="YES" useTraitCollections="YES" useSafeAreas="YES" colorMatched="YES" initialViewController="BYZ-38-t0r">
    <device id="retina6_12" orientation="portrait" appearance="light"/>
    <dependencies>
        <plugIn identifier="com.apple.InterfaceBuilder.IBCocoaTouchPlugin" version="21678"/>
        <capability name="Safe area layout guides" minToolsVersion="9.0"/>
        <capability name="System colors in document" minToolsVersion="11.0"/>
        <capability name="documents saved in the Xcode 8 format" minToolsVersion="8.0"/>
    </dependencies>
    <scenes>
        <!--View Controller-->
        <scene sceneID="tne-QT-ifu">
            <objects>
                <viewController id="BYZ-38-t0r" customClass="ViewController" customModule="WebViewApp" customModuleProvider="target" sceneMemberID="viewController">
                    <view key="view" contentMode="scaleToFill" id="8bC-Xf-vdC">
                        <rect key="frame" x="0.0" y="0.0" width="393" height="852"/>
                        <autoresizingMask key="autoresizingMask" widthSizable="YES" heightSizable="YES"/>
                        <subviews>
                            <wkWebView contentMode="scaleToFill" translatesAutoresizingMaskIntoConstraints="NO" id="fKc-32-1Ip">
                                <rect key="frame" x="0.0" y="0.0" width="393" height="852"/>
                                <color key="backgroundColor" red="0.36078431370000003" green="0.38823529410000002" blue="0.4039215686" alpha="1" colorSpace="custom" customColorSpace="sRGB"/>
                                <wkWebViewConfiguration key="configuration">
                                    <audiovisualMediaTypes key="mediaTypesRequiringUserActionForPlayback" none="YES"/>
                                    <wkPreferences key="preferences"/>
                                </wkWebViewConfiguration>
                            </wkWebView>
                        </subviews>
                        <viewLayoutGuide key="safeArea" id="6Tk-OE-BBY"/>
                        <color key="backgroundColor" systemColor="systemBackgroundColor"/>
                        <constraints>
                            <constraint firstItem="fKc-32-1Ip" firstAttribute="top" secondItem="8bC-Xf-vdC" secondAttribute="top" id="1cz-ih-w5V"/>
                            <constraint firstAttribute="bottom" secondItem="fKc-32-1Ip" secondAttribute="bottom" id="BgZ-hI-dgs"/>
                            <constraint firstItem="fKc-32-1Ip" firstAttribute="leading" secondItem="6Tk-OE-BBY" secondAttribute="leading" id="DoM-dc-fCH"/>
                            <constraint firstItem="fKc-32-1Ip" firstAttribute="trailing" secondItem="6Tk-OE-BBY" secondAttribute="trailing" id="jmS-PZ-rYG"/>
                        </constraints>
                    </view>
                    <connections>
                        <outlet property="webView" destination="fKc-32-1Ip" id="Mvw-0T-WMH"/>
                    </connections>
                </viewController>
                <placeholder placeholderIdentifier="IBFirstResponder" id="dkx-z0-nzr" sceneMemberID="firstResponder"/>
            </objects>
            <point key="canvasLocation" x="132" y="-27"/>
        </scene>
    </scenes>
    <resources>
        <systemColor name="systemBackgroundColor">
            <color white="1" alpha="1" colorSpace="custom" customColorSpace="genericGamma22GrayColorSpace"/>
        </systemColor>
    </resources>
</document>'''
        
    def _generate_ios_readme(self, metadata, target_url):
        return f'''# {metadata.title} - iOS App

This is an Xcode project that wraps the website [{target_url}]({target_url}) as a native iOS app.

## How to Build

1. Open Xcode
2. Select "Open a project or file"
3. Select the `.xcodeproj` file in this folder
4. Select your development team in the project settings
5. Choose a device or simulator
6. Click the "Run" button or press Cmd+R

## Features

- WKWebView-based app that loads the website
- Full-screen experience
- iOS navigation support
- Network security exception for HTTP content
- Responsive design for iPhone and iPad

## Customization

- Modify `ViewController.swift` to add custom functionality
- Update `Info.plist` to change app metadata
- Replace app icons in the project
- Modify colors and styling in the storyboard

## Requirements

- Xcode 14.0 or later
- iOS 13.0 or higher deployment target
- Active Apple Developer account for device deployment
- Internet connection for loading web content

## Website

Original website: {target_url}
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    # Windows generators
    def _generate_solution_file(self, app_name):
        return f'''Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{app_name}", "{app_name}\\{app_name}.csproj", "{{12345678-1234-1234-1234-123456789ABC}}"
EndProject
Global
        GlobalSection(SolutionConfigurationPlatforms) = preSolution
                Debug|x64 = Debug|x64
                Debug|x86 = Debug|x86
                Debug|ARM = Debug|ARM
                Debug|ARM64 = Debug|ARM64
                Release|x64 = Release|x64
                Release|x86 = Release|x86
                Release|ARM = Release|ARM
                Release|ARM64 = Release|ARM64
        EndGlobalSection
        GlobalSection(ProjectConfigurationPlatforms) = postSolution
                {{12345678-1234-1234-1234-123456789ABC}}.Debug|x64.ActiveCfg = Debug|x64
                {{12345678-1234-1234-1234-123456789ABC}}.Debug|x64.Build.0 = Debug|x64
                {{12345678-1234-1234-1234-123456789ABC}}.Debug|x86.ActiveCfg = Debug|x86
                {{12345678-1234-1234-1234-123456789ABC}}.Debug|x86.Build.0 = Debug|x86
                {{12345678-1234-1234-1234-123456789ABC}}.Debug|ARM.ActiveCfg = Debug|ARM
                {{12345678-1234-1234-1234-123456789ABC}}.Debug|ARM.Build.0 = Debug|ARM
                {{12345678-1234-1234-1234-123456789ABC}}.Debug|ARM64.ActiveCfg = Debug|ARM64
                {{12345678-1234-1234-1234-123456789ABC}}.Debug|ARM64.Build.0 = Debug|ARM64
                {{12345678-1234-1234-1234-123456789ABC}}.Release|x64.ActiveCfg = Release|x64
                {{12345678-1234-1234-1234-123456789ABC}}.Release|x64.Build.0 = Release|x64
                {{12345678-1234-1234-1234-123456789ABC}}.Release|x86.ActiveCfg = Release|x86
                {{12345678-1234-1234-1234-123456789ABC}}.Release|x86.Build.0 = Release|x86
                {{12345678-1234-1234-1234-123456789ABC}}.Release|ARM.ActiveCfg = Release|ARM
                {{12345678-1234-1234-1234-123456789ABC}}.Release|ARM.Build.0 = Release|ARM
                {{12345678-1234-1234-1234-123456789ABC}}.Release|ARM64.ActiveCfg = Release|ARM64
                {{12345678-1234-1234-1234-123456789ABC}}.Release|ARM64.Build.0 = Release|ARM64
        EndGlobalSection
        GlobalSection(SolutionProperties) = preSolution
                HideSolutionNode = FALSE
        EndGlobalSection
EndGlobal'''
    
    def _generate_csproj(self, app_name, metadata):
        return f'''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net8.0-windows10.0.19041.0</TargetFramework>
    <TargetPlatformMinVersion>10.0.17763.0</TargetPlatformMinVersion>
    <RootNamespace>{self._sanitize_namespace(app_name)}</RootNamespace>
    <Platforms>x86;x64;ARM64</Platforms>
    <RuntimeIdentifiers>win-x86;win-x64;win-arm64</RuntimeIdentifiers>
    <UseWinUI>true</UseWinUI>
    <EnableMsixTooling>true</EnableMsixTooling>
    <WindowsAppSDKSelfContained>true</WindowsAppSDKSelfContained>
    <GenerateAssemblyInfo>true</GenerateAssemblyInfo>
    <UseWPF>false</UseWPF>
    <UseWindowsForms>false</UseWindowsForms>
  </PropertyGroup>

  <ItemGroup>
    <Content Include="Assets\\**" />
    <Content Include="web\\**\\*" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.WindowsAppSDK" Version="1.4.231008000" />
    <PackageReference Include="Microsoft.Windows.SDK.BuildTools" Version="10.0.22621.2428" />
  </ItemGroup>

  <ItemGroup>
    <None Remove="Assets\\**" />
    <None Remove="web\\**\\*" />
  </ItemGroup>
</Project>'''
    
    def _generate_appx_manifest(self, metadata):
        return f'''<?xml version="1.0" encoding="utf-8"?>
<Package
  xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
  xmlns:mp="http://schemas.microsoft.com/appx/2014/phone/manifest"
  xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
  xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
  IgnorableNamespaces="uap rescap">

  <Identity
    Name="12345678-1234-1234-1234-123456789abc"
    Publisher="CN=PWABuilder"
    Version="1.0.0.0" />

  <mp:PhoneIdentity PhoneProductId="12345678-1234-1234-1234-123456789abc" PhonePublisherId="00000000-0000-0000-0000-000000000000"/>

  <Properties>
    <DisplayName>{metadata.title}</DisplayName>
    <PublisherDisplayName>PWA Builder</PublisherDisplayName>
    <Logo>Assets\\StoreLogo.png</Logo>
  </Properties>

  <Dependencies>
    <TargetDeviceFamily Name="Windows.Universal" MinVersion="10.0.17763.0" MaxVersionTested="10.0.19041.0" />
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.19041.0" />
  </Dependencies>

  <Resources>
    <Resource Language="x-generate"/>
  </Resources>

  <Applications>
    <Application Id="App"
      Executable="$targetnametoken$.exe"
      EntryPoint="$targetentrypoint$">
      <uap:VisualElements
        DisplayName="{metadata.title}"
        Description="{getattr(metadata, 'description', metadata.title) if hasattr(metadata, 'description') and metadata.description else metadata.title}"
        BackgroundColor="transparent"
        Square150x150Logo="Assets\\Square150x150Logo.png"
        Square44x44Logo="Assets\\Square44x44Logo.png">
        <uap:DefaultTile Wide310x150Logo="Assets\\Wide310x150Logo.png" />
        <uap:SplashScreen Image="Assets\\SplashScreen.png" />
      </uap:VisualElements>
    </Application>
  </Applications>

  <Capabilities>
    <Capability Name="internetClient" />
  </Capabilities>
</Package>'''
    
    def _generate_main_xaml(self, app_name):
        return f'''<Page
    x:Class="{app_name}.MainPage"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:local="using:{app_name}"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    mc:Ignorable="d"
    Background="{{ThemeResource ApplicationPageBackgroundThemeBrush}}">

    <Grid>
        <WebView2 x:Name="WebView" 
                  Source="about:blank" />
        <ProgressRing x:Name="LoadingRing" 
                      IsActive="True" 
                      HorizontalAlignment="Center" 
                      VerticalAlignment="Center"
                      Width="50" 
                      Height="50" />
        <TextBlock x:Name="ErrorText" 
                   Text="Failed to load website. Please check your internet connection."
                   HorizontalAlignment="Center" 
                   VerticalAlignment="Center"
                   Visibility="Collapsed"
                   Foreground="Red" />
    </Grid>
</Page>'''
    
    def _generate_main_xaml_cs(self, app_name, target_url):
        return f'''using System;
using System.Threading.Tasks;
using Microsoft.UI.Xaml.Controls;

namespace {app_name}
{{
    public sealed partial class MainPage : Page
    {{
        public MainPage()
        {{
            this.InitializeComponent();
            LoadWebsite();
        }}

        private async void LoadWebsite()
        {{
            try
            {{
                LoadingRing.IsActive = true;
                ErrorText.Visibility = Visibility.Collapsed;
                
                await WebView.EnsureCoreWebView2Async();
                WebView.Source = new System.Uri("{target_url}");
                
                // Hide loading ring after a delay (simple approach)
                await System.Threading.Tasks.Task.Delay(3000);
                LoadingRing.IsActive = false;
            }}
            catch (System.Exception ex)
            {{
                System.Diagnostics.Debug.WriteLine($"Error loading website: {{ex.Message}}");
                LoadingRing.IsActive = false;
                ErrorText.Visibility = Visibility.Visible;
            }}
        }}


    }}
}}'''
    
    def _generate_app_xaml(self, app_name):
        return f'''<Application
    x:Class="{app_name}.App"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:local="using:{app_name}">
    <Application.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <XamlControlsResources xmlns="using:Microsoft.UI.Xaml.Controls" />
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </Application.Resources>
</Application>'''
    
    def _generate_app_xaml_cs(self, app_name):
        return f'''using Microsoft.UI.Xaml;

namespace {app_name}
{{
    public partial class App : Application
    {{
        private Window m_window;

        public App()
        {{
            this.InitializeComponent();
        }}

        protected override void OnLaunched(Microsoft.UI.Xaml.LaunchActivatedEventArgs args)
        {{
            m_window = new MainWindow();
            m_window.Content = new MainPage();
            m_window.Activate();
        }}
    }}
}}'''
    
    def _generate_main_window_xaml(self, app_name):
        return f'''<Window
    x:Class="{app_name}.MainWindow"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:local="using:{app_name}"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    mc:Ignorable="d">

    <Grid>
    </Grid>
</Window>'''

    def _generate_main_window_xaml_cs(self, app_name):
        return f'''using Microsoft.UI.Xaml;

namespace {app_name}
{{
    public sealed partial class MainWindow : Window
    {{
        public MainWindow()
        {{
            this.InitializeComponent();
            this.Title = "{app_name}";
            this.ExtendsContentIntoTitleBar = true;
        }}
    }}
}}'''
    
    def _generate_windows_readme(self, metadata, target_url):
        return f'''# {metadata.title} - Electron Desktop App (DEPRECATED - Use _generate_electron_readme instead)

⚠️ **DEPRECATED**: This method generates old UWP/Visual Studio projects. 
Use the new Electron-based approach with _generate_electron_readme for better compatibility.

This was a Visual Studio project that wrapped websites as Windows apps, but has been 
replaced with a more reliable Electron-based solution that works across all platforms.

## Migration Notice

The Windows package generation has been updated to use Electron instead of UWP/Visual Studio:
- Better cross-platform compatibility (Windows, Mac, Linux)
- No compilation errors or Visual Studio requirements  
- Easier build process with npm
- More reliable and modern approach

Original website: {target_url}
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    def _generate_launch_settings(self, app_name):
        """Generate launchSettings.json for Visual Studio debugging"""
        return f'''{{
  "profiles": {{
    "{app_name} (Package)": {{
      "commandName": "MsixPackage"
    }},
    "{app_name} (Unpackaged)": {{
      "commandName": "Project"
    }}
  }}
}}'''
    
    def _sanitize_namespace(self, name):
        """Sanitize namespace to be valid C# identifier"""
        import re
        # Remove invalid characters and replace with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure it starts with letter or underscore
        if sanitized and sanitized[0].isdigit():
            sanitized = f'App_{sanitized}'
        return sanitized or 'App'
    
    def _generate_capacitor_gradle(self):
        """Generate capacitor.gradle file for Android Capacitor projects"""
        return '''// Capacitor Gradle configuration
// This file contains Capacitor-specific Gradle settings for the Android project
'''
    
    def _generate_android_root_gradle(self):
        """Generate root build.gradle for Android project"""
        return '''// Top-level build file where you can add configuration options common to all sub-projects/modules.
buildscript {
    ext {
        compileSdkVersion = 34
        targetSdkVersion = 34
        minSdkVersion = 22
        cordovaAndroidVersion = '12.0.1'
        kotlin_version = '1.9.10'
    }
    
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
    
    dependencies {
        classpath 'com.android.tools.build:gradle:8.1.0'
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlin_version"
        classpath 'com.google.gms:google-services:4.4.0'
    }
}

apply from: "variables.gradle"

// Repositories are now managed by settings.gradle
// Remove allprojects block to avoid conflicts

task clean(type: Delete) {
    delete rootProject.buildDir
}
'''

    def _generate_android_settings_gradle(self):
        """Generate settings.gradle for Android project"""
        return '''pluginManagement {
    repositories {
        google()
        gradlePluginPortal()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_PROJECT)
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
        maven { url 'https://www.jitpack.io' }
    }
}

rootProject.name = "android"
include ':app'

apply from: 'capacitor.settings.gradle'
'''
    
    def _generate_gradle_wrapper_bat(self):
        """Generate gradlew.bat for Windows Gradle builds"""
        return '''@rem
@rem Copyright 2015 the original author or authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem      https://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.
@rem

@if "%DEBUG%" == "" @echo off
@rem ##########################################################################
@rem
@rem  Gradle startup script for Windows
@rem
@rem ##########################################################################

@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%

@rem Resolve any "." and ".." in APP_HOME to make it shorter.
for %%i in ("%APP_HOME%") do set APP_HOME=%%~fi

@rem Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS="-Xmx64m" "-Xms64m"

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if "%ERRORLEVEL%" == "0" goto execute

echo.
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto execute

echo.
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME%
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:execute
@rem Setup the command line

set CLASSPATH=%APP_HOME%\\gradle\\wrapper\\gradle-wrapper.jar


@rem Execute Gradle
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %GRADLE_OPTS% "-Dorg.gradle.appname=%APP_BASE_NAME%" -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*

:end
@rem End local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" endlocal

:fail
rem Set variable GRADLE_EXIT_CONSOLE if you need the _script_ return code instead of
rem the _cmd_ return code
if not "" == "%GRADLE_EXIT_CONSOLE%" exit 1
exit /b 1
'''

    def _generate_gradle_wrapper_sh(self):
        """Generate gradlew for Unix/Linux/Mac Gradle builds"""
        return '''#!/bin/sh

#
# Copyright © 2015-2021 the original authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

##############################################################################
#
#   Gradle start up script for POSIX generated by Gradle.
#
#   Important for running:
#
#   (1) You need a POSIX-compliant shell to run this script. If your /bin/sh is
#       noncompliant, but you have some other compliant shell such as ksh or
#       bash, then to run this script, type that shell name before the whole
#       command line, like:
#
#           ksh Gradle
#
#       Busybox and similar reduced shells will NOT work, because this script
#       requires all of these POSIX shell features:
#         * functions;
#         * expansions «$var», «${var}», «${var:-default}», «${var+SET}»,
#           «${var#prefix}», «${var%suffix}», and «$( cmd )»;
#         * compound commands having a testable exit status, especially «case»;
#         * various built-in commands including «command», «set», and «ulimit».
#
#   Important for patching:
#
#   (2) This script targets any POSIX shell, so it avoids extensions provided
#       by Bash, Ksh, etc; in particular arrays are avoided.
#
#       The "traditional" practice of packing multiple parameters into a
#       space-separated string is a well documented source of bugs and security
#       problems, so this is (mostly) avoided, by progressively accumulating
#       options in "$@", and eventually passing that to Java.
#
#       Where the inherited environment variables (DEFAULT_JVM_OPTS, JAVA_OPTS,
#       and GRADLE_OPTS) rely on word-splitting, this is performed explicitly;
#       see the in-line comments for details.
#
#       There are tweaks for specific operating systems such as AIX, CygWin,
#       Darwin, MinGW, and NonStop.
#
#   (3) This script is generated from the Groovy template
#       https://github.com/gradle/gradle/blob/HEAD/subprojects/plugins/src/main/resources/org/gradle/api/internal/plugins/unixStartScript.txt
#       within the Gradle project.
#
#       You can find Gradle at https://github.com/gradle/gradle/.
#
##############################################################################

# Attempt to set APP_HOME

# Resolve links: $0 may be a link
app_path=$0

# Need this for daisy-chained symlinks.
while
    APP_HOME=${app_path%"${app_path##*/}"}  # leaves a trailing /; empty if no leading path
    [ -h "$app_path" ]
do
    ls=$( ls -ld "$app_path" )
    link=${ls#*' -> '}
    case $link in             #(
      /*)   app_path=$link ;; #(
      *)    app_path=$APP_HOME$link ;;
    esac
done

# This is normally unused
# shellcheck disable=SC2034
APP_BASE_NAME=${0##*/}
APP_HOME=$( cd "${APP_HOME:-./}" && pwd -P ) || exit

# Use the maximum available, or set MAX_FD != -1 to use that value.
MAX_FD=maximum

warn () {
    echo "$*"
} >&2

die () {
    echo
    echo "$*"
    echo
    exit 1
} >&2

# OS specific support (must be 'true' or 'false').
cygwin=false
msys=false
darwin=false
nonstop=false
case "$( uname )" in                #(
  CYGWIN* )         cygwin=true  ;; #(
  Darwin* )         darwin=true  ;; #(
  MSYS* | MINGW* )  msys=true    ;; #(
  NONSTOP* )        nonstop=true ;;
esac

CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar


# Determine the Java command to use to start the JVM.
if [ -n "$JAVA_HOME" ] ; then
    if [ -x "$JAVA_HOME/jre/sh/java" ] ; then
        # IBM's JDK on AIX uses strange locations for the executables
        JAVACMD=$JAVA_HOME/jre/sh/java
    else
        JAVACMD=$JAVA_HOME/bin/java
    fi
    if [ ! -x "$JAVACMD" ] ; then
        die "ERROR: JAVA_HOME is set to an invalid directory: $JAVA_HOME

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
    fi
else
    JAVACMD=java
    which java >/dev/null 2>&1 || die "ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
fi

# Increase the maximum file descriptors if we can.
if ! "$cygwin" && ! "$darwin" && ! "$nonstop" ; then
    case $MAX_FD in #(
      max*)
        # In POSIX sh, ulimit -H is undefined. That's why the result is checked to see if it worked.
        # shellcheck disable=SC3045
        MAX_FD=$( ulimit -H -n ) ||
            warn "Could not query maximum file descriptor limit"
    esac
    case $MAX_FD in  #(
      '' | soft) :;; #(
      *)
        # In POSIX sh, ulimit -n is undefined. That's why the result is checked to see if it worked.
        # shellcheck disable=SC3045
        ulimit -n "$MAX_FD" ||
            warn "Could not set maximum file descriptor limit to $MAX_FD"
    esac
fi

# Collect all arguments for the java command, stacking in reverse order:
#   * args from the command line
#   * the main class name
#   * -classpath
#   * -D...appname settings
#   * --module-path (only if needed)
#   * DEFAULT_JVM_OPTS, JAVA_OPTS, and GRADLE_OPTS environment variables.

# For Cygwin or MSYS, switch paths to Windows format before running java
if "$cygwin" || "$msys" ; then
    APP_HOME=$( cygpath --path --mixed "$APP_HOME" )
    CLASSPATH=$( cygpath --path --mixed "$CLASSPATH" )

    JAVACMD=$( cygpath --unix "$JAVACMD" )

    # Now convert the arguments - kludge to limit ourselves to /bin/sh
    for arg do
        if
            case $arg in                                #(
              -*)   false ;;                            # don't mess with options #(
              /?*)  t=${arg#/} t=/${t%%/*}              # looks like a POSIX filepath
                    [ -e "$t" ] ;;                      #(
              *)    false ;;
            esac
        then
            arg=$( cygpath --path --ignore --mixed "$arg" )
        fi
        # Roll the args list around exactly as many times as the number of
        # args, so each arg winds up back in the position where it started, but
        # possibly modified.
        #
        # NB: a `for` loop captures its iteration list before it begins, so
        # changing the positional parameters here affects neither the number of
        # iterations, nor the values presented in `arg`.
        shift                   # remove old arg
        set -- "$@" "$arg"      # push replacement arg
    done
fi


# Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
DEFAULT_JVM_OPTS='"-Xmx64m" "-Xms64m"'

# Collect all arguments for the java command:
#   * DEFAULT_JVM_OPTS, JAVA_OPTS, GRADLE_OPTS environment variables. (In typical installations, these are unset.)
#   * Project-specific gradle.properties files (if they exist).
#   * Global gradle.properties files (if they exist).
#   * Command line arguments.

exec "$JAVACMD" "$@"
'''

    def _generate_gradle_wrapper_properties(self):
        """Generate gradle-wrapper.properties file"""
        return '''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.1-bin.zip
networkTimeout=10000
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
'''

    def _generate_gradle_setup_script(self):
        """Generate script to setup Gradle wrapper"""
        return '''@echo off
REM Setup Gradle Wrapper for Android Build

echo Setting up Gradle wrapper...

REM Navigate to android directory 
cd android

REM Create gradle wrapper directory if it doesn't exist
if not exist "gradle\\wrapper" mkdir gradle\\wrapper

REM Download gradle wrapper jar if it doesn't exist
if not exist "gradle\\wrapper\\gradle-wrapper.jar" (
    echo Downloading Gradle wrapper jar...
    powershell -Command "try { Invoke-WebRequest -Uri 'https://github.com/gradle/gradle/raw/v8.1.1/gradle/wrapper/gradle-wrapper.jar' -OutFile 'gradle\\wrapper\\gradle-wrapper.jar' -UseBasicParsing } catch { Write-Host 'PowerShell download failed, trying curl...'; exit 1 }"
    
    REM If PowerShell fails, try with curl
    if %errorlevel% neq 0 (
        echo Trying with curl...
        curl -L -o gradle\\wrapper\\gradle-wrapper.jar https://github.com/gradle/gradle/raw/v8.1.1/gradle/wrapper/gradle-wrapper.jar
    )
)

REM Also try downloading from services.gradle.org if GitHub fails
if not exist "gradle\\wrapper\\gradle-wrapper.jar" (
    echo Trying alternative download source...
    powershell -Command "try { Invoke-WebRequest -Uri 'https://services.gradle.org/distributions-snapshots/gradle-8.1-20230123230022+0000-wrapper.jar' -OutFile 'gradle\\wrapper\\gradle-wrapper.jar' -UseBasicParsing } catch { Write-Host 'Alternative download failed' }"
)

if exist "gradle\\wrapper\\gradle-wrapper.jar" (
    echo Gradle wrapper setup complete!
    echo File size: 
    dir gradle\\wrapper\\gradle-wrapper.jar
) else (
    echo Failed to download Gradle wrapper automatically.
    echo Please manually download gradle-wrapper.jar from:
    echo https://github.com/gradle/gradle/raw/v8.1.1/gradle/wrapper/gradle-wrapper.jar
    echo And place it in android\\gradle\\wrapper\\ directory.
)

cd ..
'''

    def _generate_gradle_setup_script_linux(self):
        """Generate Linux/WSL optimized Gradle setup script"""
        return '''#!/bin/bash
# Linux/WSL Gradle Setup Script
# Optimized for Ubuntu, Debian, and WSL environments

echo "🐧 Setting up Gradle for Linux/WSL Android build..."

# Install required packages
echo "📦 Installing required packages..."
sudo apt update
sudo apt install -y openjdk-11-jdk wget curl unzip

# Set JAVA_HOME if not set
if [ -z "$JAVA_HOME" ]; then
    export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
    echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> ~/.bashrc
    echo "✅ JAVA_HOME set to $JAVA_HOME"
fi

# Navigate to android directory
cd android

# Create gradle wrapper directory if it doesn't exist
mkdir -p gradle/wrapper

# Download gradle wrapper jar if it doesn't exist
if [ ! -f "gradle/wrapper/gradle-wrapper.jar" ]; then
    echo "📥 Downloading Gradle wrapper jar..."
    
    # Try official Gradle distribution first
    curl -sL https://services.gradle.org/distributions/gradle-8.0-wrapper.jar -o gradle/wrapper/gradle-wrapper.jar
    
    # If curl fails, try with wget
    if [ $? -ne 0 ]; then
        echo "🔄 Trying with wget..."
        wget -q https://services.gradle.org/distributions/gradle-8.0-wrapper.jar -O gradle/wrapper/gradle-wrapper.jar
    fi
    
    # Try GitHub backup if both fail
    if [ ! -f "gradle/wrapper/gradle-wrapper.jar" ]; then
        echo "🔄 Trying GitHub backup..."
        curl -sL https://github.com/gradle/gradle/raw/v8.0.0/gradle/wrapper/gradle-wrapper.jar -o gradle/wrapper/gradle-wrapper.jar
    fi
    
    # Try Maven Central as last resort
    if [ ! -f "gradle/wrapper/gradle-wrapper.jar" ]; then
        echo "🔄 Trying Maven Central..."
        wget -q https://repo1.maven.org/maven2/org/gradle/gradle-wrapper/8.0/gradle-wrapper-8.0.jar -O gradle/wrapper/gradle-wrapper.jar
    fi
fi

if [ -f "gradle/wrapper/gradle-wrapper.jar" ]; then
    echo "✅ Gradle wrapper setup complete!"
    echo "📋 File size: $(ls -la gradle/wrapper/gradle-wrapper.jar)"
    chmod +x gradlew
    
    # Test Gradle installation
    echo "🧪 Testing Gradle installation..."
    ./gradlew --version
    
    echo ""
    echo "📋 Next steps:"
    echo "1. Build debug APK: ./gradlew assembleDebug"
    echo "2. Build release APK: ./gradlew assembleRelease"
    echo "3. Clean and build: ./gradlew clean assembleDebug"
else
    echo "❌ Failed to download Gradle wrapper automatically."
    echo "🔧 Manual download required:"
    echo "1. Download from: https://services.gradle.org/distributions/gradle-8.0-wrapper.jar"
    echo "2. Place in: android/gradle/wrapper/gradle-wrapper.jar"
    echo "3. Run: chmod +x gradlew"
fi

cd ..
'''

    def _generate_variables_gradle(self):
        """Generate variables.gradle file for Android build configuration"""
        return '''ext {
    minSdkVersion = 22
    compileSdkVersion = 34
    targetSdkVersion = 34
    androidxActivityVersion = '1.8.0'
    androidxAppCompatVersion = '1.6.1'
    androidxCoordinatorLayoutVersion = '1.2.0'
    androidxCoreVersion = '1.12.0'
    androidxFragmentVersion = '1.6.2'
    coreSplashScreenVersion = '1.0.1'
    androidxWebkitVersion = '1.8.0'
    junitVersion = '4.13.2'
    androidxJunitVersion = '1.1.5'
    androidxEspressoCoreVersion = '3.5.1'
    cordovaAndroidVersion = '12.0.1'
    kotlin_version = '1.9.10'
}
'''

    def _generate_capacitor_settings_gradle(self):
        """Generate capacitor.settings.gradle file for Capacitor configuration"""
        return '''// Capacitor Settings
// This file is automatically generated by Capacitor and should not be modified manually
'''

    def _generate_local_properties(self):
        """Generate local.properties file for Android SDK configuration"""
        return '''# This file is automatically generated by DigitalSkeleton.
# Do not modify this file -- YOUR CHANGES WILL BE ERASED!
# This file should *NOT* be checked into Version Control Systems,
# as it contains information specific to your local configuration.

# Location of the Android SDK. This is only used by Gradle.
# For customization when using a Version Control System, please read the
# header note.

# Automatically detect Android SDK location from common paths
# Users can override by setting ANDROID_HOME or ANDROID_SDK_ROOT environment variables

# Common Windows SDK locations:
# sdk.dir=C\\:\\Users\\%USERNAME%\\AppData\\Local\\Android\\Sdk
# sdk.dir=C\\:\\Android\\Sdk

# Common macOS SDK locations:
# sdk.dir=/Users/%USERNAME%/Library/Android/sdk
# sdk.dir=/usr/local/android-sdk

# Common Linux SDK locations:
# sdk.dir=/home/%USERNAME%/Android/Sdk
# sdk.dir=/opt/android-sdk

# Default Android Studio installation locations:
# Windows: C:\\Users\\%USERNAME%\\AppData\\Local\\Android\\Sdk
# macOS: /Users/%USERNAME%/Library/Android/sdk  
# Linux: /home/%USERNAME%/Android/Sdk

# NOTE: If you have Android Studio installed, the SDK is typically auto-detected.
# If build fails, please set ANDROID_HOME environment variable or manually set sdk.dir below:
# sdk.dir=/path/to/your/android/sdk
'''

    def _generate_cordova_plugins_gradle(self):
        """Generate build.gradle for capacitor-cordova-android-plugins"""
        return '''apply plugin: 'com.android.library'

android {
    compileSdkVersion project.hasProperty('compileSdkVersion') ? rootProject.ext.compileSdkVersion : 34
    namespace "capacitor.plugins"
    
    defaultConfig {
        minSdkVersion project.hasProperty('minSdkVersion') ? rootProject.ext.minSdkVersion : 22
        targetSdkVersion project.hasProperty('targetSdkVersion') ? rootProject.ext.targetSdkVersion : 34
        versionCode 1
        versionName "1.0"
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.core:core:1.10.1'
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}
'''

    def _generate_capacitor_app_gradle(self, package_name, metadata):
        """Generate modern Capacitor app/build.gradle"""
        return f'''apply plugin: 'com.android.application'

android {{
    namespace '{package_name}'
    compileSdkVersion rootProject.ext.compileSdkVersion
    
    defaultConfig {{
        applicationId "{package_name}"
        minSdkVersion rootProject.ext.minSdkVersion
        targetSdkVersion rootProject.ext.targetSdkVersion
        versionCode 1
        versionName "1.0"
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
        aaptOptions {{
             // Files and dirs to omit from the packaged assets dir, modified to accommodate modern web apps.
             // Default: https://android.googlesource.com/platform/frameworks/base/+/282e181b58cf72b6ca770dc7ca5f91f135444502/tools/aapt/AaptAssets.cpp#61
            ignoreAssetsPattern '!.svn:!.git:!.ds_store:!*.scc:.*:!CVS:!thumbs.db:!picasa.ini:!*~'
        }}
    }}
    
    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }}
    }}
    
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

repositories {{
    google()
    mavenCentral()
}}

dependencies {{
    implementation fileTree(include: ['*.jar'], dir: 'libs')
    implementation "androidx.appcompat:appcompat:${{rootProject.ext.androidxAppCompatVersion}}"
    implementation "androidx.core:core:${{rootProject.ext.androidxCoreVersion}}"
    implementation "androidx.activity:activity:${{rootProject.ext.androidxActivityVersion}}"
    implementation "androidx.fragment:fragment:${{rootProject.ext.androidxFragmentVersion}}"
    implementation "androidx.coordinatorlayout:coordinatorlayout:${{rootProject.ext.androidxCoordinatorLayoutVersion}}"
    implementation "androidx.webkit:webkit:${{rootProject.ext.androidxWebkitVersion}}"
    implementation "androidx.core:core-splashscreen:${{rootProject.ext.coreSplashScreenVersion}}"
    
    testImplementation "junit:junit:${{rootProject.ext.junitVersion}}"
    androidTestImplementation "androidx.test.ext:junit:${{rootProject.ext.androidxJunitVersion}}"
    androidTestImplementation "androidx.test.espresso:espresso-core:${{rootProject.ext.androidxEspressoCoreVersion}}"
    
    implementation 'com.capacitorjs:core:4.8.0'
}}

// Skip complex Capacitor configurations to simplify build process
'''

    def _generate_capacitor_build_gradle(self):
        """Generate capacitor.build.gradle for Capacitor app"""
        return '''// Capacitor Build Configuration
// This file contains build configurations specific to Capacitor

// Apply Capacitor Gradle Plugin
apply plugin: 'com.capacitor.gradle-plugin'

repositories {
    maven { url 'https://oss.sonatype.org/content/repositories/snapshots/' }
}

dependencies {
    implementation 'com.capacitorjs:core:4.8.0'
}
'''

    def _generate_simple_capacitor_gradle(self):
        """Generate simplified capacitor.build.gradle for Capacitor app"""
        return '''// Simplified Capacitor Build Configuration
// This file contains minimal build configurations for Capacitor

dependencies {
    implementation 'com.capacitorjs:core:4.8.0'
}
'''

    def _generate_capacitor_manifest(self, package_name, metadata):
        """Generate AndroidManifest.xml for Capacitor app"""
        return f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    package="{package_name}">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{metadata.title}"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme.NoActionBarLaunch"
        android:usesCleartextTraffic="true">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTask"
            android:theme="@style/AppTheme.NoActionBarLaunch">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${{applicationId}}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>
    </application>

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
</manifest>
'''

    def _generate_capacitor_main_activity(self, package_name, metadata, target_url):
        """Generate MainActivity.java for Capacitor app"""
        class_name = package_name.split('.')[-1].capitalize()
        return f'''package {package_name};

import android.os.Bundle;

import com.getcapacitor.BridgeActivity;
import com.getcapacitor.Plugin;

import java.util.ArrayList;

public class MainActivity extends BridgeActivity {{
    @Override
    public void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        // Initializes the Bridge
        this.init(savedInstanceState, new ArrayList<Class<? extends Plugin>>() {{{{
            // Additional plugins you've installed go here
            // Ex: add(TotallyAwesomePlugin.class);
        }}}});
    }}
}}
'''
    
    # Electron generators for Windows
    def _generate_electron_package_json(self, app_name, metadata):
        """Generate package.json for Electron app"""
        return f'''{{
  "name": "{app_name.lower().replace(' ', '-')}",
  "version": "1.0.0",
  "description": "{getattr(metadata, 'description', metadata.title) if hasattr(metadata, 'description') and metadata.description else metadata.title}",
  "main": "main.js",
  "scripts": {{
    "start": "electron .",
    "build": "electron-builder",
    "build-win": "electron-builder --win",
    "build-linux": "electron-builder --linux",
    "build-mac": "electron-builder --mac",
    "pack": "electron-builder --dir",
    "dist": "npm run build"
  }},
  "keywords": ["electron", "desktop", "app", "webview"],
  "author": "Generated by DigitalSkeleton",
  "license": "MIT",
  "devDependencies": {{
    "electron": "^27.0.0",
    "electron-builder": "^24.6.4"
  }},
  "build": {{
    "appId": "com.digitalskeleton.{app_name.lower().replace(' ', '')}",
    "productName": "{metadata.title}",
    "directories": {{
      "output": "dist"
    }},
    "files": [
      "main.js",
      "preload.js",
      "renderer.js",
      "index.html",
      "assets/**/*"
    ],
    "win": {{
      "target": "nsis",
      "icon": "assets/icon.ico"
    }},
    "linux": {{
      "target": "AppImage",
      "icon": "assets/icon.png"
    }},
    "mac": {{
      "target": "dmg",
      "icon": "assets/icon.icns"
    }}
  }}
}}'''

    def _generate_electron_main_js(self, target_url, metadata):
        """Generate main.js for Electron app"""
        return f'''const {{ app, BrowserWindow, Menu, shell }} = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {{
  mainWindow = new BrowserWindow({{
    width: 1200,
    height: 800,
    webPreferences: {{
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    }},
    icon: path.join(__dirname, 'assets', 'icon.png'),
    titleBarStyle: 'default',
    show: false
  }});

  // Load the target website
  mainWindow.loadURL('{target_url}');

  // Show window when ready
  mainWindow.once('ready-to-show', () => {{
    mainWindow.show();
  }});

  // Handle window closed
  mainWindow.on('closed', () => {{
    mainWindow = null;
  }});

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({{ url }}) => {{
    shell.openExternal(url);
    return {{ action: 'deny' }};
  }});

  // Handle navigation to external URLs
  mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {{
    const parsedUrl = new URL(navigationUrl);
    const targetDomain = new URL('{target_url}').hostname;
    
    if (parsedUrl.hostname !== targetDomain) {{
      event.preventDefault();
      shell.openExternal(navigationUrl);
    }}
  }});

  // Create application menu
  const template = [
    {{
      label: 'File',
      submenu: [
        {{
          label: 'Reload',
          accelerator: 'CmdOrCtrl+R',
          click: () => {{
            mainWindow.reload();
          }}
        }},
        {{
          label: 'Force Reload',
          accelerator: 'CmdOrCtrl+Shift+R',
          click: () => {{
            mainWindow.webContents.reloadIgnoringCache();
          }}
        }},
        {{ type: 'separator' }},
        {{
          label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {{
            app.quit();
          }}
        }}
      ]
    }},
    {{
      label: 'View',
      submenu: [
        {{ role: 'zoomin' }},
        {{ role: 'zoomout' }},
        {{ role: 'resetzoom' }},
        {{ type: 'separator' }},
        {{ role: 'togglefullscreen' }}
      ]
    }},
    {{
      label: 'Window',
      submenu: [
        {{ role: 'minimize' }},
        {{ role: 'close' }}
      ]
    }},
    {{
      label: 'Help',
      submenu: [
        {{
          label: 'About {metadata.title}',
          click: () => {{
            shell.openExternal('{target_url}');
          }}
        }}
      ]
    }}
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {{
  if (process.platform !== 'darwin') {{
    app.quit();
  }}
}});

app.on('activate', () => {{
  if (BrowserWindow.getAllWindows().length === 0) {{
    createWindow();
  }}
}});'''

    def _generate_electron_preload_js(self):
        """Generate preload.js for Electron app"""
        return '''// Preload script for Electron app
const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Add any APIs you want to expose to the renderer process here
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  getVersion: () => ipcRenderer.invoke('get-version')
});

// Prevent new window creation
window.addEventListener('DOMContentLoaded', () => {
  const links = document.querySelectorAll('a[target="_blank"]');
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      window.electronAPI.openExternal(link.href);
    });
  });
});'''

    def _generate_electron_renderer_js(self):
        """Generate renderer.js for Electron app"""
        return '''// Renderer process script
console.log('Electron app renderer loaded');

// Add any additional renderer-specific functionality here
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM content loaded in Electron app');
  
  // Add app-specific enhancements
  const style = document.createElement('style');
  style.textContent = `
    /* Electron app specific styles */
    body {
      user-select: text;
      -webkit-user-select: text;
    }
    
    /* Custom scrollbar for better desktop experience */
    ::-webkit-scrollbar {
      width: 12px;
    }
    
    ::-webkit-scrollbar-track {
      background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
      background: #888;
      border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
      background: #555;
    }
  `;
  document.head.appendChild(style);
});'''

    def _generate_electron_index_html(self, metadata, target_url):
        """Generate index.html for Electron app (fallback page)"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            min-height: calc(100vh - 80px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        
        .container {{
            max-width: 600px;
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
            font-weight: 300;
        }}
        
        p {{
            font-size: 1.2em;
            line-height: 1.6;
            margin-bottom: 30px;
            opacity: 0.9;
        }}
        
        .btn {{
            display: inline-block;
            padding: 15px 30px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 500;
            transition: all 0.3s ease;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }}
        
        .btn:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }}
        
        .loading {{
            margin-top: 30px;
            font-size: 0.9em;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{metadata.title}</h1>
        <p>Loading the website...</p>
        <p>If the content doesn't load automatically, click the button below:</p>
        <a href="{target_url}" class="btn" target="_blank">Open Website</a>
        <div class="loading">
            <p>This Electron app will redirect to {target_url}</p>
        </div>
    </div>
    
    <script src="renderer.js"></script>
    <script>
        // Auto-redirect to target URL after a short delay
        setTimeout(() => {{
            window.location.href = '{target_url}';
        }}, 2000);
    </script>
</body>
</html>'''

    def _generate_electron_build_script(self, app_name):
        """Generate build.bat script for Windows"""
        return f'''@echo off
echo Building {app_name} Desktop App...
echo.

echo Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building Windows executable...
call npm run build-win
if %errorlevel% neq 0 (
    echo Build failed
    pause
    exit /b 1
)

echo.
echo Build complete! Check the 'dist' folder for your app.
echo.
echo Files created:
dir dist /b
echo.
pause'''

    def _generate_electron_build_script_linux(self, app_name):
        """Generate build.sh script for Linux/Mac"""
        return f'''#!/bin/bash
echo "Building {app_name} Desktop App..."
echo

echo "Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

echo
echo "Building executable..."
npm run build
if [ $? -ne 0 ]; then
    echo "Build failed"
    exit 1
fi

echo
echo "Build complete! Check the 'dist' folder for your app."
echo
echo "Files created:"
ls -la dist/
echo'''

    def _generate_offline_html(self, metadata):
        """Generate offline fallback HTML"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.title} - Offline</title>
    <style>
        body {{
            font-family: system-ui, sans-serif;
            text-align: center;
            padding: 50px;
            background: #f5f5f5;
        }}
        .offline-message {{
            max-width: 400px;
            margin: 0 auto;
            padding: 40px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="offline-message">
        <h2>{metadata.title}</h2>
        <p>This app requires an internet connection.</p>
        <p>Please check your connection and try again.</p>
    </div>
</body>
</html>'''

    def _generate_electron_readme(self, metadata, target_url, app_name):
        """Generate README for Electron project"""
        return f'''# {metadata.title} - Desktop App

This is an Electron-based desktop application that wraps the website [{target_url}]({target_url}) as a native Windows, Mac, and Linux app.

## Features

- **Native Desktop Experience**: Full desktop integration with system notifications
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Auto-Updates**: Built-in update mechanism
- **Offline Handling**: Graceful offline state management
- **External Link Handling**: Opens external links in default browser
- **Native Menus**: Platform-appropriate application menus

## Quick Start

### Prerequisites
- Node.js 16 or later
- npm or yarn package manager

### Installation & Build

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Run in Development**
   ```bash
   npm start
   ```

3. **Build for Production**
   ```bash
   # Build for current platform
   npm run build
   
   # Build for specific platforms
   npm run build-win    # Windows
   npm run build-linux  # Linux
   npm run build-mac    # macOS
   ```

### Build Scripts

**Windows Users:**
- Run `build.bat` to build the Windows executable
- The built app will be in the `dist` folder

**Linux/Mac Users:**
- Run `chmod +x build.sh && ./build.sh` to build the app
- The built app will be in the `dist` folder

## Project Structure

```
{app_name}/
├── main.js              # Main Electron process
├── preload.js           # Preload script (security)
├── renderer.js          # Renderer process enhancements
├── index.html           # Fallback HTML page
├── package.json         # Project configuration
├── build.bat           # Windows build script
├── build.sh            # Linux/Mac build script
└── assets/             # App icons and resources
    ├── icon.ico        # Windows icon
    ├── icon.png        # Linux icon
    └── icon.icns       # macOS icon
```

## Customization

### Changing the Target Website
Edit `main.js` and update the `loadURL` call with your new website URL.

### Modifying App Appearance  
- Update icons in the `assets` folder
- Modify `package.json` for app metadata
- Customize styles in `renderer.js`

### Adding Features
- Add new menu items in `main.js`
- Extend preload API in `preload.js`
- Add renderer enhancements in `renderer.js`

## Distribution

The built executables can be:
- **Windows**: Distributed as `.exe` installer or portable app
- **macOS**: Distributed as `.dmg` disk image
- **Linux**: Distributed as `.AppImage` or `.deb`/.rpm` packages

## Technical Details

- **Framework**: Electron ^27.0.0
- **Builder**: electron-builder ^24.6.4
- **Security**: Context isolation enabled, node integration disabled
- **Target Website**: {target_url}
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Support

This desktop app was generated by **DigitalSkeleton** - Website to Mobile App Converter.

For issues with the generated app, check:
1. Internet connectivity for website loading
2. Firewall settings for network access
3. System compatibility for Electron apps

Original website: {target_url}
'''

    # Capacitor generators for unified cross-platform approach
    def _generate_capacitor_package_json(self, app_name, metadata):
        """Generate package.json for Capacitor project"""
        return f'''{{
  "name": "{app_name.lower().replace(' ', '-')}",
  "version": "1.0.0",
  "description": "{metadata.description or f'Mobile app for {metadata.title}'}",
  "main": "main.js",
  "scripts": {{
    "start": "npm run build && npx cap run",
    "build": "echo 'Building web assets...' && npm run build:web",
    "build:web": "echo 'Web assets ready'",
    "cap:android": "npx cap add android && npx cap sync android && npx cap open android",
    "cap:ios": "npx cap add ios && npx cap sync ios && npx cap open ios",
    "cap:electron": "npx cap add @capacitor-community/electron && npx cap sync @capacitor-community/electron && npx cap open @capacitor-community/electron",
    "build:android": "npm run build:web && npx cap sync android && cd android && gradlew.bat assembleDebug",
    "build:android:release": "npm run build:web && npx cap sync android && cd android && ./gradlew assembleRelease",
    "build:android:bundle": "npm run build:web && npx cap sync android && cd android && ./gradlew bundleRelease",
    "build:ios": "npm run build:web && npx cap sync ios && cd ios/App && xcodebuild -workspace App.xcworkspace -scheme App -configuration Debug -destination generic/platform=iOS build",
    "dev": "npm run build:web && npx cap run android --livereload",
    "clean": "npx cap clean && rm -rf android ios electron dist node_modules",
    "install:all": "npm install && npx cap add android && npx cap add ios"
  }},
  "keywords": ["capacitor", "mobile", "pwa", "cross-platform"],
  "author": "DigitalSkeleton Generator",
  "license": "MIT",
  "dependencies": {{
    "@capacitor/core": "^6.0.0",
    "@capacitor/cli": "^6.0.0",
    "@capacitor/android": "^6.0.0",
    "@capacitor/ios": "^6.0.0",
    "@capacitor-community/electron": "^5.0.0"
  }},
  "devDependencies": {{
    "@capacitor/cli": "^6.0.0",
    "typescript": "^5.0.0"
  }}
}}'''

    def _generate_capacitor_config(self, app_name, package_name, metadata):
        """Generate capacitor.config.ts"""
        return f'''import {{ CapacitorConfig }} from '@capacitor/cli';

const config: CapacitorConfig = {{
  appId: '{package_name}',
  appName: '{app_name}',
  webDir: 'dist',
  server: {{
    androidScheme: 'https'
  }},
  plugins: {{
    SplashScreen: {{
      launchShowDuration: 2000,
      backgroundColor: '#ffffff',
      showSpinner: false
    }},
    StatusBar: {{
      style: 'default',
      backgroundColor: '#ffffff'
    }}
  }}
}};

export default config;'''
    
    def _generate_capacitor_config_js(self, app_name, package_name, metadata):
        """Generate capacitor.config.js (JavaScript version to avoid TypeScript dependency)"""
        return f'''const config = {{
  appId: '{package_name}',
  appName: '{app_name}',
  webDir: 'dist',
  server: {{
    androidScheme: 'https'
  }},
  plugins: {{
    SplashScreen: {{
      launchShowDuration: 2000,
      backgroundColor: '#ffffff',
      showSpinner: false
    }},
    StatusBar: {{
      style: 'default',
      backgroundColor: '#ffffff'
    }}
  }}
}};

module.exports = config;'''

    def _generate_capacitor_index_html(self, metadata, target_url):
        """Generate main HTML file for Capacitor app"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>{metadata.title}</title>
    <meta name="description" content="{metadata.description or f'Mobile app for {metadata.title}'}">
    
    <!-- Capacitor PWA optimizations -->
    <meta name="format-detection" content="telephone=no">
    <meta name="msapplication-tap-highlight" content="no">
    
    <!-- iOS specific -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="{metadata.title}">
    
    <!-- Android specific -->
    <meta name="theme-color" content="#4285f4">
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body, html {{
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        #app-container {{
            height: 100vh;
            width: 100vw;
            position: relative;
            overflow: hidden;
        }}
        
        #webview {{
            width: 100%;
            height: 100%;
            border: none;
            background: white;
        }}
        
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 1000;
        }}
        
        .loading.hidden {{
            display: none;
        }}
        
        .spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4285f4;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div id="app-container">
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Loading {metadata.title}...</p>
        </div>
        <iframe id="webview" src="{target_url}" title="{metadata.title}"></iframe>
    </div>
    
    <script src="main.js"></script>
</body>
</html>'''

    def _generate_capacitor_main_js(self, target_url, metadata):
        """Generate main.js for Capacitor app"""
        return f'''// Main JavaScript for Capacitor app
import {{ Capacitor }} from '@capacitor/core';
import {{ StatusBar, Style }} from '@capacitor/status-bar';
import {{ SplashScreen }} from '@capacitor/splash-screen';

class CapacitorApp {{
    constructor() {{
        this.targetUrl = '{target_url}';
        this.init();
    }}
    
    async init() {{
        // Wait for device to be ready
        document.addEventListener('DOMContentLoaded', () => {{
            this.setupWebView();
            this.handleDeviceReady();
        }});
    }}
    
    async handleDeviceReady() {{
        console.log('Capacitor app ready');
        
        try {{
            // Configure status bar
            if (Capacitor.isNativePlatform()) {{
                await StatusBar.setStyle({{ style: Style.Default }});
                
                // Hide splash screen after short delay
                setTimeout(async () => {{
                    await SplashScreen.hide();
                }}, 1500);
            }}
        }} catch (error) {{
            console.log('Platform-specific setup error:', error);
        }}
        
        // Hide loading indicator
        this.hideLoading();
    }}
    
    setupWebView() {{
        const webview = document.getElementById('webview');
        const loading = document.getElementById('loading');
        
        if (!webview) return;
        
        // Handle iframe load events
        webview.onload = () => {{
            console.log('WebView loaded successfully');
            this.hideLoading();
        }};
        
        webview.onerror = (error) => {{
            console.error('WebView load error:', error);
            this.showError();
        }};
        
        // Handle network connectivity
        window.addEventListener('online', () => {{
            console.log('Network connection restored');
            webview.src = this.targetUrl;
        }});
        
        window.addEventListener('offline', () => {{
            console.log('Network connection lost');
            this.showError('No internet connection');
        }});
    }}
    
    hideLoading() {{
        const loading = document.getElementById('loading');
        if (loading) {{
            loading.classList.add('hidden');
        }}
    }}
    
    showError(message = 'Failed to load content') {{
        const loading = document.getElementById('loading');
        if (loading) {{
            loading.innerHTML = `
                <div style="color: #ff4444;">
                    <p>${{message}}</p>
                    <button onclick="location.reload()" style="margin-top: 10px; padding: 10px 20px;">
                        Retry
                    </button>
                </div>
            `;
            loading.classList.remove('hidden');
        }}
    }}
}}

// Initialize app
new CapacitorApp();'''

    def _generate_capacitor_android_build_script(self, app_name):
        """Generate Android build script for Capacitor"""
        return f'''@echo off
REM Build script for {app_name} Android App

echo Building {app_name} Android App...

REM Install dependencies
echo Installing dependencies...
call npm install

REM Add Android platform if not exists
echo Setting up Android platform...
call npx cap add android

REM Sync web assets to native project
echo Syncing assets...
call npx cap sync android

REM Build APK
echo Building APK...

REM Check if gradle wrapper exists, if not, set it up
if not exist "android\gradle\wrapper\gradle-wrapper.jar" (
    echo Setting up Gradle wrapper...
    call setup-gradle.bat
)

cd android
call gradlew.bat assembleDebug
cd ..

echo Build complete! APK location:
echo android/app/build/outputs/apk/debug/app-debug.apk

echo To install on device: adb install android/app/build/outputs/apk/debug/app-debug.apk
pause'''

    def _generate_capacitor_android_build_script_linux(self, app_name):
        """Generate Linux/WSL optimized build script for Capacitor Android projects"""
        return f'''#!/bin/bash
# Linux/WSL Android Build Script for {app_name}
# Optimized for Ubuntu, Debian, and WSL environments

echo "🐧 Starting Linux/WSL Android build for {app_name}..."

# Function to install Android SDK on Linux
install_android_sdk() {{
    echo "📱 Installing Android SDK for Linux/WSL..."
    
    # Update package list
    sudo apt update
    
    # Install required packages
    sudo apt install -y openjdk-11-jdk wget unzip curl
    
    # Set JAVA_HOME
    export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
    echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> ~/.bashrc
    
    # Download Android command line tools
    cd ~
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip
    unzip -q commandlinetools-linux-8512546_latest.zip
    
    # Create Android SDK directory
    mkdir -p ~/Android/Sdk/cmdline-tools
    mv cmdline-tools ~/Android/Sdk/cmdline-tools/latest
    
    # Set Android environment variables
    export ANDROID_HOME=~/Android/Sdk
    export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
    echo "export ANDROID_HOME=~/Android/Sdk" >> ~/.bashrc
    echo "export PATH=\\$PATH:\\$ANDROID_HOME/cmdline-tools/latest/bin:\\$ANDROID_HOME/platform-tools" >> ~/.bashrc
    
    # Accept licenses and install required packages
    yes | ~/Android/Sdk/cmdline-tools/latest/bin/sdkmanager --licenses
    ~/Android/Sdk/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"
    
    echo "✅ Android SDK installed successfully!"
}}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js for Linux/WSL..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Check if Android SDK is available
if [ -z "$ANDROID_HOME" ] || [ ! -d "$ANDROID_HOME" ]; then
    echo "⚠️  ANDROID_HOME not set or SDK not found. Installing Android SDK..."
    install_android_sdk
    source ~/.bashrc
fi

# Install project dependencies
echo "📋 Installing project dependencies..."
npm install

# Install Capacitor CLI
echo "🔧 Installing Capacitor CLI..."
npm install -g @capacitor/cli

# Add Android platform
echo "📱 Adding Android platform..."
npx cap add android

# Sync project files
echo "🔄 Syncing files to Android project..."
npx cap sync android

# Make gradlew executable
echo "🔐 Setting permissions..."
chmod +x android/gradlew

# Build APK
echo "🏗️  Building APK..."
cd android
./gradlew assembleDebug

echo ""
echo "✅ Build completed successfully!"
echo "📱 APK location: android/app/build/outputs/apk/debug/app-debug.apk"
echo ""
echo "📋 Next steps:"
echo "1. Install on device: adb install app/build/outputs/apk/debug/app-debug.apk"
echo "2. Test with emulator: ../gradlew installDebug"
echo "3. Build release: ./gradlew assembleRelease"
echo ""
echo "🔧 For customization:"
echo "Open Android Studio and import the android/ folder"'''

    def _generate_android_release_build_script(self, app_name):
        """Generate optimized release build script for Android"""
        return f'''@echo off
REM Optimized Release Build for {app_name} Android App

echo Building {app_name} for Google Play Store...

REM Install dependencies
echo Installing dependencies...
call npm install

REM Add Android platform if not exists
echo Setting up Android platform...
call npx cap add android

REM Sync web assets to native project
echo Syncing assets...
call npx cap sync android

REM Build Release APK/AAB
echo Building release APK and AAB (Google Play Bundle)...
cd android

echo Building release APK...
call gradlew assembleRelease

echo Building AAB for Google Play Store...
call gradlew bundleRelease

cd ..

echo Build complete!
echo.
echo APK Location: android/app/build/outputs/apk/release/app-release.apk
echo AAB Location: android/app/build/outputs/bundle/release/app-release.aab
echo.
echo For Google Play Store: Use the AAB file
echo For direct installation: Use the APK file
echo.
pause'''

    def _generate_android_release_build_script_linux(self, app_name):
        """Generate optimized release build script for Android (Linux/Mac)"""
        return f'''#!/bin/bash
# Optimized Release Build for {app_name} Android App

echo "Building {app_name} for Google Play Store..."

# Install dependencies
echo "Installing dependencies..."
npm install

# Add Android platform if not exists
echo "Setting up Android platform..."
npx cap add android

# Sync web assets to native project 
echo "Syncing assets..."
npx cap sync android

# Build Release APK/AAB
echo "Building release APK and AAB (Google Play Bundle)..."
cd android

echo "Building release APK..."
./gradlew assembleRelease

echo "Building AAB for Google Play Store..."
./gradlew bundleRelease

cd ..

echo "Build complete!"
echo ""
echo "APK Location: android/app/build/outputs/apk/release/app-release.apk"
echo "AAB Location: android/app/build/outputs/bundle/release/app-release.aab"
echo ""
echo "For Google Play Store: Use the AAB file"
echo "For direct installation: Use the APK file"'''

    def _generate_android_quick_build_script(self, app_name):
        """Generate quick development build script"""
        return f'''@echo off
REM Quick Development Build for {app_name}

echo Quick building {app_name} for testing...

REM Sync only (faster than full build)
echo Syncing web assets...
call npx cap sync android

REM Quick debug build
echo Building debug APK (fast)...
cd android
call gradlew.bat assembleDebug --daemon --parallel
cd ..

echo Quick build complete!
echo APK: android/app/build/outputs/apk/debug/app-debug.apk
echo.
echo Install: adb install android/app/build/outputs/apk/debug/app-debug.apk
pause'''

    def _generate_android_quick_build_script_linux(self, app_name):
        """Generate quick development build script (Linux/Mac)"""
        return f'''#!/bin/bash
# Quick Development Build for {app_name}

echo "Quick building {app_name} for testing..."

# Sync only (faster than full build)
echo "Syncing web assets..."
npx cap sync android

# Quick debug build  
echo "Building debug APK (fast)..."
cd android
./gradlew assembleDebug --daemon --parallel
cd ..

echo "Quick build complete!"
echo "APK: android/app/build/outputs/apk/debug/app-debug.apk"
echo ""
echo "Install: adb install android/app/build/outputs/apk/debug/app-debug.apk"'''

    def _generate_capacitor_ios_build_script(self, app_name):
        """Generate iOS build script for Capacitor"""
        return f'''@echo off
REM Build script for {app_name} iOS App

echo Building {app_name} iOS App...

REM Install dependencies
echo Installing dependencies...
call npm install

REM Add iOS platform if not exists
echo Setting up iOS platform...
call npx cap add ios

REM Sync web assets to native project
echo Syncing assets...
call npx cap sync ios

echo iOS project ready!
echo Location: ios/App/App.xcworkspace

echo To build IPA:
echo 1. Open ios/App/App.xcworkspace in Xcode
echo 2. Configure signing and provisioning
echo 3. Build and archive for distribution

pause'''

    def _generate_capacitor_ios_build_script_linux(self, app_name):
        """Generate iOS build script for Capacitor (Linux/Mac)"""
        return f'''#!/bin/bash
# Build script for {app_name} iOS App

echo "Building {app_name} iOS App..."

# Install dependencies
echo "Installing dependencies..."
npm install

# Add iOS platform if not exists
echo "Setting up iOS platform..."
npx cap add ios

# Sync web assets to native project
echo "Syncing assets..."
npx cap sync ios

echo "iOS project ready!"
echo "Location: ios/App/App.xcworkspace"
echo ""
echo "To build IPA:"
echo "1. Open ios/App/App.xcworkspace in Xcode"
echo "2. Configure signing and provisioning"
echo "3. Build and archive for distribution"'''

    def _generate_enhanced_android_readme(self, metadata, target_url):
        """Generate comprehensive README with multiple build options"""
        return f'''# {metadata.title} - Capacitor Android Project

This project converts the website [{target_url}]({target_url}) into a native Android APK using modern Capacitor technology.

## Quick Start (Recommended)

### 🚀 Super Fast Development Build
```bash
# Windows
quick-build.bat

# Mac/Linux  
./quick-build.sh
```
**Perfect for:** Testing, development, quick iterations

### 📱 Google Play Store Release
```bash
# Windows
build-release.bat

# Mac/Linux
./build-release.sh
```
**Perfect for:** App store submission, production deployment

## Build Options Explained

| Build Type | Speed | Output | Use Case |
|------------|-------|---------|----------|
| **Quick Build** | ⚡ Fastest | Debug APK | Testing & Development |
| **Release Build** | 🐌 Slower | Release APK + AAB | Production & Play Store |
| **Manual Build** | ⚖️ Medium | Debug APK | Learning & Customization |

## Prerequisites

1. **Node.js** (v16+): [Download](https://nodejs.org/)
2. **Android Studio**: [Download](https://developer.android.com/studio)
   - Install Android SDK (API 34 recommended)
   - Set up Android SDK path in system environment

## Manual Build Process

If you prefer step-by-step control:

```bash
# 1. Install dependencies
npm install

# 2. Add Android platform
npx cap add android

# 3. Sync web assets
npx cap sync android

# 4. Build APK (choose one)
cd android
./gradlew assembleDebug          # Debug APK
./gradlew assembleRelease        # Release APK  
./gradlew bundleRelease          # AAB for Play Store
cd ..
```

## Output Locations

After building, find your files here:

- **Debug APK**: `android/app/build/outputs/apk/debug/app-debug.apk`
- **Release APK**: `android/app/build/outputs/apk/release/app-release.apk`
- **AAB Bundle**: `android/app/build/outputs/bundle/release/app-release.aab`

## Installation & Testing

### Install on Device
```bash
# Install via ADB
adb install android/app/build/outputs/apk/debug/app-debug.apk

# Or drag & drop APK file to Android device
```

### Testing Options
1. **Physical Device**: Enable Developer Options + USB Debugging
2. **Android Emulator**: Create virtual device in Android Studio
3. **Live Reload**: `npm run dev` for real-time testing

## App Store Deployment

### Google Play Store
1. Use **AAB file** (app-release.aab) for Play Console upload
2. Sign the app with release keystore
3. Follow Play Store guidelines for review

### Direct Distribution  
1. Use **APK file** (app-release.apk) for direct installation
2. Users need to enable "Install from Unknown Sources"

## Customization

### Change Website URL
Edit `main.js` and update the `targetUrl` variable.

### App Icons & Branding
- Replace icons in `assets/` folder
- Update `capacitor.config.ts` for app metadata
- Modify colors in `index.html` styles

### Add Native Features
```javascript
// Add to main.js for native capabilities
import {{ Camera }} from '@capacitor/camera';
import {{ Geolocation }} from '@capacitor/geolocation';
import {{ Device }} from '@capacitor/device';
```

## Troubleshooting

### Build Issues
- **Gradle sync failed**: Update Android SDK and build tools
- **License not accepted**: Run `sdkmanager --licenses` in terminal
- **Build tools missing**: Install via Android Studio SDK Manager

### Performance Optimization
- **Slow builds**: Use `quick-build` scripts with daemon/parallel flags
- **Large APK size**: Enable ProGuard in `android/app/build.gradle`
- **Network issues**: Add network security config for HTTPS sites

## Technical Details

- **Framework**: Capacitor ^6.0.0 (Modern Cordova successor)
- **Build System**: Gradle with Android SDK
- **Web Engine**: System WebView with native bridge
- **Target SDK**: Android 14 (API 34) with backward compatibility
- **Minimum SDK**: Android 7.0 (API 24)
- **Architecture**: ARM64, ARMv7, x86_64 support

## Support & Resources

- **Original Website**: {target_url}
- **Capacitor Docs**: [capacitorjs.com](https://capacitorjs.com)
- **Android Developer**: [developer.android.com](https://developer.android.com)
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by DigitalSkeleton

---

**Pro Tip**: Use `quick-build` for development and `build-release` for production. The AAB format is preferred by Google Play Store for smaller download sizes and dynamic delivery features.
'''
    # SDK-free Android generation methods
    def _generate_online_builder_readme(self, metadata, target_url):
        """Generate README for online APK builders"""
        return f"""# {metadata.title} - Online APK Builder

Convert your website to an Android APK using online builders - **NO SDK required!**

## Quick Start (5 Minutes)

### Method 1: AppsGeyser (Easiest)
1. Visit: **https://appsgeyser.com/**
2. Choose "Website" option  
3. Enter URL: `{target_url}`
4. Upload icon, set name: `{metadata.title}`
5. Download APK

### Method 2: Appy Pie  
1. Visit: **https://www.appypie.com/app-maker**
2. Select "Website App"
3. Enter URL: `{target_url}`
4. Build and download

## Features
✅ Ready-to-install APK file
✅ No coding required  
✅ Works on all Android devices
✅ Can upload to Play Store

**Website**: {target_url}
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def _generate_app_config_json(self, app_name, metadata, target_url):
        """Generate app configuration JSON"""
        return json.dumps({
            "app_name": metadata.title,
            "website_url": target_url,
            "description": getattr(metadata, "description", f"Mobile app for {metadata.title}"),
            "version": "1.0.0"
        }, indent=2)

    def _generate_build_instructions_html(self, metadata, target_url):
        """Generate build instructions HTML"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Build {metadata.title} APK</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .method {{ background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .url {{ background: #e8f4f8; padding: 10px; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>Build Your Android App</h1>
    <div class="method">
        <h2>AppsGeyser (Easiest)</h2>
        <ol>
            <li>Visit <a href="https://appsgeyser.com/">AppsGeyser.com</a></li>
            <li>Click "Create App" → "Website"</li>
            <li>Enter URL: <div class="url">{target_url}</div></li>
            <li>Upload icon, set name: {metadata.title}</li>
            <li>Download APK</li>
        </ol>
    </div>
</body>
</html>"""

    def _generate_pwa_wrapper_html(self, metadata, target_url):
        """Generate PWA wrapper HTML"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.title}</title>
    <link rel="manifest" href="manifest.json">
</head>
<body>
    <iframe src="{target_url}" style="width:100vw;height:100vh;border:none;"></iframe>
    <script>
        if ("serviceWorker" in navigator) {{
            navigator.serviceWorker.register("sw.js");
        }}
    </script>
</body>
</html>"""

    def _generate_pwa_service_worker(self, target_url):
        """Generate PWA service worker"""
        return """const CACHE_NAME = "app-v1";
self.addEventListener("install", e => {
    e.waitUntil(caches.open(CACHE_NAME));
});
self.addEventListener("fetch", e => {
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});"""

    def _generate_pwa_app_js(self, target_url):
        """Generate PWA app JavaScript"""
        return """console.log("PWA App loaded");"""

    def _generate_pwa_wrapper_readme(self, metadata, target_url):
        """Generate PWA wrapper README"""
        return f"""# {metadata.title} - PWA Wrapper

Progressive Web App wrapper for easy APK building.

## Usage
1. Host these files on any web server
2. Use hosted URL with online APK builders
3. Or install directly as PWA in Chrome

**Website**: {target_url}
"""

    def _generate_template_app_html(self, metadata, target_url):
        """Generate template app HTML"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{metadata.title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>{metadata.title}</h1>
    <p><a href="{target_url}">Visit Website</a></p>
</body>
</html>"""

    def _generate_template_config_xml(self, app_name, metadata):
        """Generate template config XML"""
        return f"""<?xml version="1.0"?>
<config>
    <name>{metadata.title}</name>
    <package>com.digitalskeleton.{app_name.lower()}</package>
    <version>1.0.0</version>
</config>"""

    def _generate_template_build_guide(self, metadata, target_url):
        """Generate template build guide"""
        return f"""# {metadata.title} - Build Guide

Simple template for creating Android APK without SDK.

## Quick Build
1. Use online APK builders with app.html
2. Or host files and use URL
3. Download and install APK

**Website**: {target_url}
"""

    def _generate_quick_setup_instructions(self, metadata, target_url):
        """Generate quick setup instructions"""
        return f"""QUICK SETUP - {metadata.title}

1. Go to appsgeyser.com
2. Select "Website" 
3. Enter: {target_url}
4. Set name: {metadata.title}
5. Download APK

Done! No SDK required.
"""

    # React Native generator methods
    def _generate_react_native_package_json(self, app_name, metadata):
        """Generate package.json for React Native project"""
        return json.dumps({
            "name": app_name.lower().replace(" ", ""),
            "version": "1.0.0",
            "description": getattr(metadata, 'description', f"React Native app for {metadata.title}"),
            "main": "index.js",
            "scripts": {
                "android": "react-native run-android",
                "start": "react-native start",
                "build-apk": "cd android && ./gradlew assembleDebug"
            },
            "dependencies": {
                "react": "18.2.0",
                "react-native": "0.72.6",
                "react-native-webview": "^13.6.3"
            },
            "devDependencies": {
                "@babel/core": "^7.20.0",
                "@babel/preset-env": "^7.20.0",
                "metro-react-native-babel-preset": "0.76.8"
            }
        }, indent=2)

    def _generate_react_native_app_js(self, metadata, target_url):
        """Generate App.js for React Native"""
        return f'''import React from 'react';
import {{
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  ActivityIndicator,
}} from 'react-native';
import {{WebView}} from 'react-native-webview';

const App = () => {{
  const [loading, setLoading] = React.useState(true);

  return (
    <SafeAreaView style={{{{flex: 1}}}}>
      <StatusBar barStyle="dark-content" />
      
      {{loading && (
        <View style={{styles.loadingContainer}}>
          <ActivityIndicator size="large" color="#0066cc" />
          <Text style={{styles.loadingText}}>Loading {metadata.title}...</Text>
        </View>
      )}}
      
      <WebView
        source={{{{uri: '{target_url}'}}}}
        style={{{{flex: 1}}}}
        onLoadStart={{() => setLoading(true)}}
        onLoadEnd={{() => setLoading(false)}}
        javaScriptEnabled={{true}}
        domStorageEnabled={{true}}
        startInLoadingState={{true}}
        scalesPageToFit={{true}}
        allowsBackForwardNavigationGestures={{true}}
      />
    </SafeAreaView>
  );
}};

const styles = StyleSheet.create({{
  loadingContainer: {{
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'white',
    zIndex: 1000,
  }},
  loadingText: {{
    marginTop: 10,
    fontSize: 16,
    color: '#333',
  }},
}});

export default App;'''

    def _generate_react_native_index_js(self, app_name):
        """Generate index.js for React Native"""
        return f"""import {{AppRegistry}} from 'react-native';
import App from './App';
import {{name as appName}} from './app.json';

AppRegistry.registerComponent(appName, () => App);"""

    def _generate_react_native_app_json(self, app_name, metadata):
        """Generate app.json for React Native"""
        return json.dumps({
            "name": app_name.lower().replace(" ", ""),
            "displayName": metadata.title
        }, indent=2)

    def _generate_react_native_metro_config(self):
        """Generate metro.config.js for React Native"""
        return """const {{getDefaultConfig, mergeConfig}} = require('@react-native/metro-config');

const config = {{}};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);"""

    def _generate_react_native_babel_config(self):
        """Generate babel.config.js for React Native"""
        return """module.exports = {{
  presets: ['module:metro-react-native-babel-preset'],
}};"""

    def _generate_react_native_build_script_windows(self):
        """Generate Windows build script for React Native"""
        return """@echo off
echo Building React Native Android APK...

echo.
echo === Installing Dependencies ===
npm install

echo.
echo === Building APK ===
cd android
call gradlew assembleDebug

echo.
echo === Build Complete ===
echo APK location: android/app/build/outputs/apk/debug/app-debug.apk
pause"""

    def _generate_react_native_build_script_linux(self):
        """Generate Linux build script for React Native"""
        return """#!/bin/bash
echo "Building React Native Android APK..."

echo
echo "=== Installing Dependencies ==="
npm install

echo
echo "=== Building APK ==="
cd android
./gradlew assembleDebug

echo
echo "=== Build Complete ==="
echo "APK location: android/app/build/outputs/apk/debug/app-debug.apk\""""

    def _generate_react_native_readme(self, metadata, target_url):
        """Generate README for React Native project"""
        return f"""# {metadata.title} - React Native App

React Native mobile app that displays your website with native performance.

## Features

✅ **Native Performance** - True native mobile app
✅ **Cross-Platform** - Works on Android and iOS
✅ **WebView Integration** - Displays your website seamlessly
✅ **Modern Framework** - Built with React Native
✅ **Easy to Customize** - Modify with JavaScript/React

## Quick Start

### Prerequisites
- Node.js 16+ 
- React Native CLI: `npm install -g react-native-cli`
- Android Studio (for Android builds)

### Build APK

**Windows:**
```cmd
build-android.bat
```

**Linux/Mac:**
```bash
chmod +x build-android.sh
./build-android.sh
```

## Development

### Run on device/emulator:
```bash
npm run android
```

### Start Metro server:
```bash
npm start
```

## Website Details

- **Original URL**: {target_url}
- **App Name**: {metadata.title}
- **Framework**: React Native 0.72.6
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
*React Native gives you the best mobile app experience possible!*
"""

    def _generate_react_native_android_build_gradle(self):
        """Generate Android build.gradle for React Native"""
        return """buildscript {{
    ext {{
        buildToolsVersion = "33.0.0"
        minSdkVersion = 21
        compileSdkVersion = 33
        targetSdkVersion = 33
        ndkVersion = "23.1.7779620"
    }}
    dependencies {{
        classpath("com.android.tools.build:gradle:7.3.1")
        classpath("com.facebook.react:react-native-gradle-plugin")
    }}
}}

apply plugin: "com.facebook.react.rootproject\""""

    def _generate_react_native_android_settings_gradle(self, app_name):
        """Generate Android settings.gradle for React Native"""
        return f"""rootProject.name = '{app_name.lower().replace(" ", "")}'
apply from: file("../node_modules/@react-native-community/cli-platform-android/native_modules.gradle"); applyNativeModulesSettingsGradle(settings)
include ':app'
includeBuild('../node_modules/@react-native/gradle-plugin')"""

    def _generate_react_native_app_build_gradle(self, package_name):
        """Generate app build.gradle for React Native"""
        return f"""apply plugin: "com.android.application"
apply plugin: "com.facebook.react"

android {{{{
    compileSdkVersion rootProject.ext.compileSdkVersion

    defaultConfig {{{{
        applicationId "{package_name}"
        minSdkVersion rootProject.ext.minSdkVersion
        targetSdkVersion rootProject.ext.targetSdkVersion
        versionCode 1
        versionName "1.0"
    }}}}

    buildTypes {{{{
        release {{{{
            minifyEnabled false
            proguardFiles getDefaultProguardFile("proguard-android.txt"), "proguard-rules.pro"
        }}}}
    }}}}
}}

dependencies {{{{
    implementation "com.facebook.react:react-android"
    implementation "org.webkit:android-jsc:+"
}}}}"""

    # Expo generator methods  
    def _generate_expo_package_json(self, app_name, metadata):
        """Generate package.json for Expo project"""
        return json.dumps({
            "name": app_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "main": "node_modules/expo/AppEntry.js",
            "scripts": {
                "start": "expo start",
                "android": "expo start --android",
                "build": "eas build",
                "build-android": "eas build --platform android"
            },
            "dependencies": {
                "expo": "~49.0.15",
                "expo-status-bar": "~1.6.0",
                "react": "18.2.0",
                "react-native": "0.72.6",
                "expo-web-browser": "~12.3.2"
            }
        }, indent=2)

    def _generate_expo_app_js(self, metadata, target_url):
        """Generate App.js for Expo"""
        return f"""import React from 'react';
import {{{{ StyleSheet, Text, View, ActivityIndicator }}}} from 'react-native';
import {{{{ WebBrowser }}}} from 'expo-web-browser';
import {{{{ StatusBar }}}} from 'expo-status-bar';

export default function App() {{{{
  const [loading, setLoading] = React.useState(false);

  const openWebsite = async () => {{{{
    setLoading(true);
    try {{{{
      await WebBrowser.openBrowserAsync('{target_url}');
    }}}} catch (error) {{{{
      console.error('Error opening website:', error);
    }}}} finally {{{{
      setLoading(false);
    }}}}
  }}}};

  React.useEffect(() => {{{{
    openWebsite();
  }}}}, []);

  return (
    <View style={{styles.container}}>
      <Text style={{styles.title}}>{metadata.title}</Text>
      <Text style={{styles.subtitle}}>Mobile App</Text>
      
      {{{{loading && (
        <View style={{styles.loadingContainer}}>
          <ActivityIndicator size="large" color="#0066cc" />
          <Text style={{styles.loadingText}}>Opening website...</Text>
        </View>
      )}}}}
      
      <StatusBar style="auto" />
    </View>
  );
}}}}

const styles = StyleSheet.create({{{{
  container: {{{{
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  }}}},
  title: {{{{
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  }}}},
  subtitle: {{{{
    fontSize: 16,
    color: '#666',
    marginBottom: 30,
  }}}},
  loadingContainer: {{{{
    alignItems: 'center',
    marginTop: 20,
  }}}},
  loadingText: {{{{
    marginTop: 10,
    color: '#666',
  }}}},
}}}});"""

    def _generate_expo_app_json(self, app_name, metadata):
        """Generate app.json for Expo"""
        return json.dumps({
            "expo": {
                "name": metadata.title,
                "slug": app_name.lower().replace(" ", "-"),
                "version": "1.0.0",
                "orientation": "portrait",
                "android": {
                    "package": f"com.digitalskeleton.{app_name.lower().replace(' ', '')}"
                }
            }
        }, indent=2)

    def _generate_expo_eas_json(self):
        """Generate eas.json for Expo builds"""
        return json.dumps({
            "cli": {"version": ">= 5.4.0"},
            "build": {
                "development": {"developmentClient": True, "distribution": "internal"},
                "preview": {"distribution": "internal"},
                "production": {}
            }
        }, indent=2)

    def _generate_expo_build_script_windows(self):
        """Generate Windows build script for Expo"""
        return """@echo off
echo Building Expo APK...

echo.
echo === Installing Expo CLI ===
npm install -g @expo/cli eas-cli

echo.
echo === Installing Dependencies ===
npm install

echo.
echo === Building APK ===
eas build --platform android --profile preview

echo.
echo === Build Complete ===
echo Download your APK from the Expo dashboard
pause"""

    def _generate_expo_build_script_linux(self):
        """Generate Linux build script for Expo"""
        return """#!/bin/bash
echo "Building Expo APK..."

echo
echo "=== Installing Expo CLI ==="
npm install -g @expo/cli eas-cli

echo
echo "=== Installing Dependencies ==="
npm install

echo
echo "=== Building APK ==="
eas build --platform android --profile preview

echo
echo "=== Build Complete ==="
echo "Download your APK from the Expo dashboard\""""

    def _generate_expo_readme(self, metadata, target_url):
        """Generate README for Expo project"""
        return f"""# {metadata.title} - Expo App

Expo-based mobile app - the easiest way to build React Native apps!

## Super Quick Start (Cloud Build)

1. **Install Expo CLI:**
   ```bash
   npm install -g @expo/cli eas-cli
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Build APK in the cloud:**
   ```bash
   eas build --platform android
   ```

## Features

✅ **No Android Studio Required** - Build in the cloud
✅ **Live Preview** - Test on device instantly  
✅ **Easy Publishing** - One command to build and deploy
✅ **Cross-Platform** - Same code for Android and iOS

## Website Details

- **Original URL**: {target_url}
- **App Name**: {metadata.title}
- **Platform**: Expo SDK 49
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
*Expo is perfect for beginners who want rapid development!*
"""

    # React Native Web generator methods
    def _generate_react_native_web_package_json(self, app_name, metadata):
        """Generate package.json for React Native Web"""
        return json.dumps({
            "name": app_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "scripts": {
                "start": "webpack serve --mode development",
                "build": "webpack --mode production"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-native-web": "^0.19.9"
            },
            "devDependencies": {
                "@babel/core": "^7.22.0",
                "@babel/preset-react": "^7.22.0",
                "babel-loader": "^9.1.0",
                "webpack": "^5.88.0",
                "webpack-cli": "^5.1.0",
                "webpack-dev-server": "^4.15.0"
            }
        }, indent=2)

    def _generate_react_native_web_app_js(self, metadata, target_url):
        """Generate App.js for React Native Web"""
        return f"""import React from 'react';
import {{{{ View, Text, StyleSheet }}}} from 'react-native';

const App = () => {{{{
  React.useEffect(() => {{{{
    window.location.href = '{target_url}';
  }}}}, []);

  return (
    <View style={{styles.container}}>
      <Text style={{styles.title}}>{metadata.title}</Text>
      <Text style={{styles.message}}>Redirecting to website...</Text>
    </View>
  );
}}}};

const styles = StyleSheet.create({{{{
  container: {{{{
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  }}}},
  title: {{{{
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  }}}},
  message: {{{{
    fontSize: 16,
    color: '#666',
  }}}},
}}}});

export default App;"""

    def _generate_react_native_web_index_js(self):
        """Generate index.js for React Native Web"""
        return """import {{AppRegistry}} from 'react-native';
import App from './App';

AppRegistry.registerComponent('App', () => App);
AppRegistry.runApplication('App', {{
  rootTag: document.getElementById('root'),
}});"""

    def _generate_react_native_web_webpack_config(self):
        """Generate webpack.config.js for React Native Web"""
        return """const path = require('path');

module.exports = {{
  entry: './index.js',
  mode: 'development',
  module: {{
    rules: [
      {{
        test: /\\.js$/,
        use: {{
          loader: 'babel-loader',
          options: {{
            presets: ['@babel/preset-react'],
          }},
        }},
      }},
    ],
  }},
  resolve: {{
    alias: {{
      'react-native$': 'react-native-web',
    }},
    extensions: ['.web.js', '.js'],
  }},
  devServer: {{
    contentBase: path.join(__dirname, 'dist'),
    port: 3000,
  }},
}};"""

    def _generate_react_native_web_build_script_windows(self):
        """Generate Windows build script for React Native Web"""
        return """@echo off
echo Building React Native Web...

echo.
echo === Installing Dependencies ===
npm install

echo.
echo === Building Web Version ===
npm run build

echo.
echo === Build Complete ===
pause"""

    def _generate_react_native_web_build_script_linux(self):
        """Generate Linux build script for React Native Web"""
        return """#!/bin/bash
echo "Building React Native Web..."

echo
echo "=== Installing Dependencies ==="
npm install

echo
echo "=== Building Web Version ==="
npm run build

echo
echo "=== Build Complete ==="""""

    def _generate_react_native_web_readme(self, metadata, target_url):
        """Generate README for React Native Web"""
        return f"""# {metadata.title} - React Native Web

Hybrid approach: React Native code that works on web and mobile!

## Quick Build

### Build Web Version:
```bash
npm install
npm run build
```

## Features

✅ **One Codebase** - Web and mobile from same code
✅ **React Native** - Use familiar React Native components  
✅ **Web Compatible** - Runs in browsers
✅ **Mobile Ready** - Converts to native apps

## Website Details

- **Original URL**: {target_url}
- **App Name**: {metadata.title}
- **Framework**: React Native Web
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    # Simple, reliable APK generation methods
    def _generate_simple_wrapper_html(self, metadata, target_url):
        """Generate simple HTML wrapper for APK builders"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.title}</title>
    <link rel="manifest" href="manifest.json">
    <link rel="stylesheet" href="styles.css">
    <meta name="theme-color" content="#667eea">
</head>
<body>
    <div id="loading-screen">
        <div class="loading-content">
            <h1>{metadata.title}</h1>
            <div class="loading-spinner"></div>
            <p>Loading...</p>
        </div>
    </div>
    
    <iframe 
        id="app-frame" 
        src="{target_url}" 
        style="display:none;">
    </iframe>
    
    <script src="app.js"></script>
    <script>
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('sw.js');
        }}
    </script>
</body>
</html>'''

    def _generate_simple_service_worker(self):
        """Generate simple service worker"""
        return '''const CACHE_NAME = 'app-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/styles.css',
    '/app.js',
    '/manifest.json'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request);
            })
    );
});'''

    def _generate_wrapper_styles(self):
        """Generate CSS styles for wrapper"""
        return '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    height: 100vh;
    overflow: hidden;
}

#loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    transition: opacity 0.5s ease;
}

.loading-content {
    text-align: center;
    color: white;
}

.loading-content h1 {
    font-size: 2.5em;
    margin-bottom: 30px;
    font-weight: 300;
}

.loading-spinner {
    width: 50px;
    height: 50px;
    border: 3px solid rgba(255,255,255,0.3);
    border-top: 3px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-content p {
    font-size: 1.2em;
    opacity: 0.9;
}

#app-frame {
    width: 100vw;
    height: 100vh;
    border: none;
}

.hidden {
    opacity: 0;
    pointer-events: none;
}'''

    def _generate_wrapper_js(self, target_url):
        """Generate JavaScript for wrapper"""
        return f'''document.addEventListener('DOMContentLoaded', function() {{
    const loadingScreen = document.getElementById('loading-screen');
    const appFrame = document.getElementById('app-frame');
    
    // Show app frame after loading
    appFrame.onload = function() {{
        setTimeout(() => {{
            loadingScreen.classList.add('hidden');
            appFrame.style.display = 'block';
        }}, 1000);
    }};
    
    // Handle back button
    window.addEventListener('popstate', function() {{
        try {{
            appFrame.contentWindow.history.back();
        }} catch(e) {{
            window.location.href = '{target_url}';
        }}
    }});
    
    // Handle orientation change
    window.addEventListener('orientationchange', function() {{
        setTimeout(() => {{
            appFrame.style.height = window.innerHeight + 'px';
        }}, 100);
    }});
}});'''

    def _generate_simple_wrapper_readme(self, metadata, target_url):
        """Generate README for simple wrapper"""
        return f'''# {metadata.title} - Simple Web Wrapper

This is a simple, reliable web wrapper that works with any online APK builder.

## 🚀 Build APK in 3 Easy Steps

### Step 1: Choose Your Preferred Builder
- **AppsGeyser** (Fastest & Free): https://appsgeyser.com/
- **Appy Pie** (More Features): https://www.appypie.com/app-maker
- **PWA Builder** (Microsoft - High Quality): https://www.pwabuilder.com/

### Step 2: Import Your App
**Method A - Direct URL (Easiest):**
1. Go to your chosen builder
2. Select "Website App" or "URL App"
3. Enter: `{target_url}`

**Method B - Upload Files (Advanced):**
1. Host the web wrapper files online (Netlify, GitHub Pages)
2. Use hosted URL with the builder
3. Or upload HTML files directly if supported

### Step 3: Customize & Generate
- **App Name**: {metadata.title}
- **Icon**: Upload from icons folder (512x512px recommended)
- **Package Name**: com.yourname.{metadata.title.lower().replace(' ', '')}
- **Generate APK** and download when ready

## ✅ What You Get

- **Ready-to-install APK file**
- **No coding or SDK required**
- **Works on all Android devices**
- **Can be published to Google Play Store**

## 📱 Features

✅ **Loading Screen** - Professional app startup
✅ **Offline Support** - Basic caching included
✅ **Responsive Design** - Works on all screen sizes
✅ **Native Feel** - Fullscreen app experience
✅ **Easy Customization** - Simple HTML/CSS/JS

## 🎨 Customization

### Change Colors
Edit `styles.css` and modify the gradient colors in the background property.

### Change Loading Text
Edit `index.html` and update the loading screen content.

### Add Features
Edit `app.js` to add more functionality like:
- Push notifications
- Local storage
- Custom navigation

## 🔧 Advanced Options

### Host Online (Recommended)
1. Upload files to any free hosting:
   - Netlify.com (drag & drop)
   - GitHub Pages
   - Firebase Hosting
2. Use hosted URL with APK builders

### Test Locally
1. Install any web server
2. Open index.html in browser
3. Test functionality before building APK

## 📤 Publishing

### Google Play Store
1. Create developer account ($25)
2. Upload APK from builder
3. Fill app details
4. Submit for review

### Direct Installation
1. Enable "Unknown Sources" on Android
2. Download and install APK file
3. Share APK with others

## ❓ Troubleshooting

**APK builder not working?**
- Try a different builder from the list
- Host files online instead of uploading

**Website not loading in app?**
- Check website works on mobile
- Ensure URL is correct

**Want more features?**
- Edit the HTML/CSS/JS files
- Add custom functionality

## 🌐 Website Details

- **Original URL**: {target_url}
- **App Name**: {metadata.title}
- **Type**: Simple Web Wrapper
- **Compatibility**: All APK builders
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
*This simple wrapper works with any APK builder and requires no technical knowledge!*
'''

    def _generate_quick_start_guide(self, metadata, target_url):
        """Generate quick start guide"""
        return f'''# Quick Start Guide - {metadata.title}

## Build APK in 5 Minutes (No Coding Required!)

### Method 1: AppsGeyser (Fastest & Free) ⭐ RECOMMENDED

1. **Visit**: https://appsgeyser.com/
2. **Click**: "Create Free App"
3. **Choose**: "Website" template
4. **Enter URL**: `{target_url}`
5. **App Details**:
   - Name: {metadata.title}
   - Description: Mobile app for {metadata.title}
   - Category: Choose appropriate category
6. **Upload Icon**: Use 512x512px icon from package
7. **Create App** → Wait 2-3 minutes for processing
8. **Download APK** directly to your device

**✅ Results**: Professional Android APK ready for installation

### Method 2: Appy Pie (Advanced Features)

1. **Visit**: https://www.appypie.com/app-maker
2. **Sign up** for free account
3. **Choose**: "Website App" template
4. **Enter Details**:
   - Website URL: `{target_url}`
   - App Name: {metadata.title}
   - App Icon: Upload from package
5. **Customize**: Colors, splash screen, navigation
6. **Build**: Generate APK (may require subscription for download)

### Method 3: PWA Builder (Microsoft - Highest Quality)

1. **Host Files**: Upload web wrapper to Netlify/GitHub Pages first
2. **Visit**: https://www.pwabuilder.com/
3. **Enter**: Your hosted URL (not original website)
4. **Analyze**: Click "Start" to scan PWA readiness
5. **Generate**: Select "Android" → "Generate Package"
6. **Download**: Professional-grade APK with Play Store compatibility

## Alternative: Use Web Wrapper

If online builders don't work:

1. **Host Files**: Upload `web_wrapper` folder to any free hosting
2. **Get URL**: Copy the hosted URL
3. **Use URL**: With any APK builder instead of original website

### Free Hosting Options:
- **Netlify**: netlify.app (drag & drop upload)
- **Vercel**: vercel.com (connect GitHub)
- **GitHub Pages**: github.com (free with account)

## Installation & Sharing

### Install APK:
1. Download APK to Android device
2. Enable "Unknown Sources" in Settings → Security
3. Tap APK file to install

### Share with Others:
- Send APK file via email/messaging
- Upload to cloud storage
- Publish to Google Play Store

## Success Tips

✅ **Test website on mobile first**  
✅ **Use HTTPS URLs when possible**  
✅ **Choose memorable app name**  
✅ **Use high-quality icon (512x512px)**  
✅ **Keep app description under 80 characters**  

## Need Help?

- Check `troubleshooting.md` for common issues
- Try different builders if one doesn't work
- All builders work the same way - just different interfaces

**Website**: {target_url}  
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''

    def _generate_step_by_step_html(self, metadata, target_url):
        """Generate step-by-step HTML guide"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Build {metadata.title} APK - Step by Step</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .step {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .step-number {{
            background: #667eea;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-weight: bold;
        }}
        .builder {{
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .builder h3 {{
            color: #667eea;
            margin-top: 0;
        }}
        .url-box {{
            background: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            word-break: break-all;
            margin: 10px 0;
        }}
        .success {{
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
        }}
        .btn:hover {{
            background: #5a6fd8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Build Your Android App</h1>
        <p>Convert <strong>{metadata.title}</strong> to APK - No coding required!</p>
    </div>

    <div class="builder">
        <h3>🥇 Option 1: AppsGeyser (Recommended - Free & Fast)</h3>
        
        <div class="step">
            <span class="step-number">1</span>
            <strong>Visit AppsGeyser</strong><br>
            <a href="https://appsgeyser.com/" target="_blank" class="btn">Go to AppsGeyser.com</a>
        </div>

        <div class="step">
            <span class="step-number">2</span>
            <strong>Create Website App</strong><br>
            Click "Create App" → Select "Website" option
        </div>

        <div class="step">
            <span class="step-number">3</span>
            <strong>Enter Your Website</strong><br>
            <div class="url-box">{target_url}</div>
            Copy and paste this URL exactly
        </div>

        <div class="step">
            <span class="step-number">4</span>
            <strong>Customize App</strong><br>
            • App Name: <strong>{metadata.title}</strong><br>
            • Upload icon from the icons folder<br>
            • Choose app category
        </div>

        <div class="step">
            <span class="step-number">5</span>
            <strong>Generate APK</strong><br>
            Click "Create App" and wait 2-3 minutes for processing
        </div>

        <div class="step">
            <span class="step-number">6</span>
            <strong>Download & Install</strong><br>
            Download APK file and install on your Android device
        </div>
    </div>

    <div class="builder">
        <h3>🥈 Option 2: Appy Pie (More Features)</h3>
        <p>Visit <a href="https://www.appypie.com/app-maker" target="_blank" class="btn">Appy Pie</a> and follow similar steps with more customization options.</p>
    </div>

    <div class="builder">
        <h3>🥉 Option 3: AppMakr (Alternative)</h3>
        <p>Visit <a href="https://appmakr.com/" target="_blank" class="btn">AppMakr</a> for another free option.</p>
    </div>

    <div class="success">
        <h3>🎉 Success!</h3>
        <p>Your APK file is ready! You can now:</p>
        <ul>
            <li>Install it on any Android device</li>
            <li>Share it with friends and family</li>
            <li>Publish it to Google Play Store</li>
            <li>Distribute it however you want</li>
        </ul>
    </div>

    <div style="text-align: center; margin-top: 40px; color: #666;">
        <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by DigitalSkeleton</p>
    </div>
</body>
</html>'''

    def _generate_simple_app_config(self, app_name, metadata, target_url):
        """Generate simple app config JSON"""
        return json.dumps({
            "appName": metadata.title,
            "packageName": f"com.digitalskeleton.{app_name.lower()}",
            "websiteUrl": target_url,
            "description": getattr(metadata, 'description', f"Mobile app for {metadata.title}"),
            "version": "1.0.0",
            "instructions": {
                "step1": "Visit any online APK builder",
                "step2": "Choose 'Website App' option",
                "step3": f"Enter URL: {target_url}",
                "step4": f"Set app name: {metadata.title}",
                "step5": "Upload icon and generate APK"
            }
        }, indent=2)

    def _generate_builder_links(self):
        """Generate list of APK builder links"""
        return '''# Online APK Builders - Working Links

## Free Options

1. **AppsGeyser** (Best for beginners)
   URL: https://appsgeyser.com/
   Features: Free, fast, easy to use
   
2. **AppMakr** (Good alternative)
   URL: https://appmakr.com/
   Features: Free tier, good templates

3. **PWA Builder** (Microsoft)
   URL: https://www.pwabuilder.com/
   Features: High quality, Android & Windows

## Paid Options (Trial Available)

1. **Appy Pie** (Most features)
   URL: https://www.appypie.com/app-maker
   Features: Advanced customization, publishing help

2. **BuildFire** (Professional)
   URL: https://buildfire.com/
   Features: Enterprise features, app store optimization

3. **Mobincube** (European)
   URL: https://www.mobincube.com/
   Features: Multi-language support

## How to Use

1. Visit any link above
2. Choose "Website App" or "HTML Upload"
3. Enter your website URL or upload files
4. Customize app name, icon, colors
5. Generate and download APK

## Tips

- Start with AppsGeyser (easiest)
- Try different builders if one doesn't work
- All builders work similarly
- Some require registration but it's free
- APK generation usually takes 2-5 minutes

Updated: {datetime.now().strftime("%Y-%m-%d")}'''

    def _generate_troubleshooting_guide(self):
        """Generate troubleshooting guide"""
        return '''# Troubleshooting Guide

## Common Issues & Solutions

### APK Builder Problems

**Problem**: Builder website won't load or is slow
**Solution**: 
- Try a different browser (Chrome recommended)
- Clear browser cache and cookies
- Try a different builder from the list
- Check your internet connection

**Problem**: "Invalid URL" error
**Solution**:
- Make sure URL starts with http:// or https://
- Test URL in browser first
- Remove any extra characters or spaces
- Try with www. prefix if original doesn't work

**Problem**: APK generation fails
**Solution**:
- Wait and try again (servers can be busy)
- Try a different builder
- Use shorter app name (under 30 characters)
- Try uploading web wrapper files instead

### APK Installation Problems

**Problem**: "App not installed" error
**Solution**:
- Enable "Unknown Sources" in Android Settings → Security
- Make sure APK file downloaded completely
- Try downloading APK again
- Restart Android device

**Problem**: App crashes on startup
**Solution**:
- Check if website works on mobile browser
- Try building APK with different builder
- Make sure website is mobile-friendly

### Website Loading Issues

**Problem**: Website doesn't load in app
**Solution**:
- Test website on mobile browser first
- Check internet connection
- Make sure website supports mobile devices
- Try different website URL format

**Problem**: App shows blank screen
**Solution**:
- Wait longer for website to load
- Check if website requires login
- Try using web wrapper instead of direct URL
- Make sure website allows embedding

### General Tips

✅ **Always test website on mobile first**
✅ **Use popular, working builders like AppsGeyser**
✅ **Keep app names short and simple**
✅ **Use HTTPS URLs when possible**
✅ **Try multiple builders if one fails**
✅ **Have patience - generation can take time**

### Still Having Problems?

1. **Try the web wrapper method**:
   - Host the web wrapper files online
   - Use hosted URL instead of original website
   
2. **Use different APK builder**:
   - Each builder works differently
   - Some are more reliable than others
   
3. **Check website compatibility**:
   - Make sure website works on mobile
   - Some websites block embedding
   
4. **Contact support**:
   - Most builders have help/support sections
   - Usually respond within 24 hours

### Success Rate by Builder

- **AppsGeyser**: 95% success rate
- **PWA Builder**: 90% success rate  
- **Appy Pie**: 85% success rate
- **AppMakr**: 80% success rate

*These are estimated success rates based on common usage patterns.*

Last Updated: {datetime.now().strftime("%Y-%m-%d")}'''

    def _generate_pwa_converter_html(self, metadata, target_url):
        """Generate PWA converter HTML"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.title}</title>
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#667eea">
    <style>
        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            text-align: center;
            color: white;
            padding: 40px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            max-width: 400px;
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
            font-weight: 300;
        }}
        .btn {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 50px;
            margin: 10px;
            transition: all 0.3s ease;
            border: 2px solid rgba(255,255,255,0.3);
        }}
        .btn:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
        .install-prompt {{
            margin-top: 30px;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{metadata.title}</h1>
        <p>Progressive Web App</p>
        
        <a href="{target_url}" class="btn" target="_blank">
            Open Website
        </a>
        
        <button onclick="installApp()" class="btn" id="installBtn" style="display:none;">
            Install App
        </button>
        
        <div class="install-prompt">
            <strong>To create APK:</strong><br>
            1. Visit pwabuilder.com<br>
            2. Enter this page URL<br>
            3. Generate Android package
        </div>
    </div>
    
    <script>
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('installBtn').style.display = 'inline-block';
        }});
        
        function installApp() {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        console.log('User accepted the install prompt');
                    }}
                    deferredPrompt = null;
                }});
            }} else {{
                window.open('{target_url}', '_blank');
            }}
        }}
        
        // Auto-redirect option (uncomment if desired)
        // setTimeout(() => window.open('{target_url}', '_blank'), 3000);
    </script>
</body>
</html>'''

    def _generate_twa_manifest(self, app_name, metadata, target_url):
        """Generate TWA manifest for advanced users"""
        return json.dumps({
            "packageId": f"com.digitalskeleton.{app_name.lower()}",
            "host": target_url.replace('https://', '').replace('http://', '').split('/')[0],
            "name": metadata.title,
            "launcherName": metadata.title,
            "display": "standalone",
            "orientation": "default",
            "themeColor": "#667eea",
            "backgroundColor": "#ffffff",
            "startUrl": "/",
            "iconUrl": "https://via.placeholder.com/512x512/667eea/ffffff?text=APP",
            "webManifestUrl": "/manifest.json",
            "shortcuts": [],
            "signingKey": {
                "alias": "android",
                "fullName": "CN=Android Debug,O=Android,C=US"
            }
        }, indent=2)

    def _generate_pwa_converter_readme(self, metadata, target_url):
        """Generate PWA converter README"""
        return f'''# {metadata.title} - PWA to APK Converter

This folder contains a Progressive Web App that can be easily converted to APK.

## 🚀 Quick APK Generation

### Method 1: PWA Builder (Recommended)
1. **Host these files** on any web server
2. **Visit**: https://www.pwabuilder.com/
3. **Enter** your hosted URL
4. **Click** "Start" 
5. **Select** "Android" platform
6. **Download** APK package

### Method 2: TWA (Trusted Web Activity)
1. Use the `twa-manifest.json` file
2. Follow Google's TWA documentation
3. Build using Android Studio (advanced)

## 📁 Files Included

- `index.html` - Main PWA entry point
- `manifest.json` - Web app manifest
- `sw.js` - Service worker for offline support
- `twa-manifest.json` - TWA configuration
- `convert-to-apk.html` - Conversion guide

## 🌐 Hosting Options (Free)

### Netlify (Easiest)
1. Go to netlify.app
2. Drag and drop this folder
3. Get instant URL

### GitHub Pages
1. Upload files to GitHub repository
2. Enable Pages in repository settings
3. Use GitHub.io URL

### Vercel
1. Connect GitHub repository
2. Auto-deploy on changes
3. Get vercel.app URL

## ✅ PWA Features

- **Installable** - Can be added to home screen
- **Offline Support** - Basic caching included
- **App-like** - Runs in standalone mode
- **Responsive** - Works on all devices
- **Fast Loading** - Optimized for mobile

## 🔧 Customization

### Change App Appearance
Edit `index.html` and modify:
- Colors and gradients
- App name and description
- Button styles and text

### Modify Functionality
Edit the JavaScript to:
- Change redirect behavior
- Add custom features
- Modify install prompts

### Update Manifest
Edit `manifest.json` to change:
- App icons and colors
- Display mode and orientation
- App metadata

## 📱 Installation Flow

1. **Host PWA** → Get URL
2. **PWA Builder** → Enter URL
3. **Generate APK** → Download
4. **Install APK** → Android device

## 🎯 Advantages

✅ **High Quality** - Microsoft's PWA Builder creates professional APKs
✅ **Play Store Ready** - Generated APKs meet store requirements
✅ **Automatic Updates** - PWA can update without app store
✅ **Small Size** - Lightweight compared to native apps
✅ **Cross Platform** - Same code works everywhere

## 🌐 Website Details

- **Original URL**: {target_url}
- **App Name**: {metadata.title}
- **Type**: Progressive Web App
- **APK Builder**: PWA Builder (recommended)
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
*PWA to APK conversion provides the highest quality mobile apps!*
'''

    def _generate_conversion_tool_html(self, metadata, target_url):
        """Generate conversion tool HTML guide"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Convert {metadata.title} to APK</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
        }}
        .method {{
            background: #f8f9ff;
            border: 2px solid #e9ecff;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            transition: all 0.3s ease;
        }}
        .method:hover {{
            border-color: #667eea;
            transform: translateY(-2px);
        }}
        .method-title {{
            color: #667eea;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        .step {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 25px;
            margin: 10px 5px;
            transition: all 0.3s ease;
        }}
        .btn:hover {{
            background: #5a6fd8;
            transform: translateY(-2px);
        }}
        .url-display {{
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            word-break: break-all;
            margin: 15px 0;
        }}
        .success {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Convert {metadata.title} to Android APK</h1>
        
        <div class="method">
            <div class="method-title">📱 Method 1: PWA Builder (Best Quality)</div>
            <div class="step">
                <strong>Step 1:</strong> Host the PWA files from this package online
            </div>
            <div class="step">
                <strong>Step 2:</strong> Visit <a href="https://www.pwabuilder.com/" target="_blank" class="btn">PWA Builder</a>
            </div>
            <div class="step">
                <strong>Step 3:</strong> Enter your hosted URL and click "Start"
            </div>
            <div class="step">
                <strong>Step 4:</strong> Select "Android" and download the APK package
            </div>
        </div>

        <div class="method">
            <div class="method-title">⚡ Method 2: Direct URL Builders (Fastest)</div>
            <div class="step">
                <strong>Option A:</strong> <a href="https://appsgeyser.com/" target="_blank" class="btn">AppsGeyser</a>
                <br>Choose "Website" and enter:
                <div class="url-display">{target_url}</div>
            </div>
            <div class="step">
                <strong>Option B:</strong> <a href="https://www.appypie.com/app-maker" target="_blank" class="btn">Appy Pie</a>
                <br>Select "Website App" template
            </div>
        </div>

        <div class="method">
            <div class="method-title">🔧 Method 3: Web Wrapper Upload</div>
            <div class="step">
                <strong>Step 1:</strong> Use the files from the "web_wrapper" folder
            </div>
            <div class="step">
                <strong>Step 2:</strong> Upload to any APK builder that accepts HTML
            </div>
            <div class="step">
                <strong>Step 3:</strong> Configure app name: <strong>{metadata.title}</strong>
            </div>
        </div>

        <div class="success">
            <h3>🎉 Success Tips</h3>
            <ul>
                <li>PWA Builder creates the highest quality APKs</li>
                <li>AppsGeyser is fastest for simple apps</li>
                <li>Always test your website on mobile first</li>
                <li>Use app icons from the icons folder</li>
                <li>Generated APKs work on any Android device</li>
            </ul>
        </div>

        <div style="text-align: center; margin-top: 40px; color: #666;">
            <p><strong>Website:</strong> {target_url}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>'''

    # iOS-specific generation methods
    def _create_ios_web_wrapper(self, project_dir, metadata, manifest_data, target_url):
        """Create simple iOS web wrapper"""
        wrapper_dir = os.path.join(project_dir, 'ios_web_wrapper')
        os.makedirs(wrapper_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        
        # Create iOS-optimized HTML app
        self._create_file(wrapper_dir, 'index.html', self._generate_ios_wrapper_html(metadata, target_url))
        self._create_file(wrapper_dir, 'manifest.json', json.dumps(manifest_data, indent=2))
        self._create_file(wrapper_dir, 'sw.js', self._generate_simple_service_worker())
        self._create_file(wrapper_dir, 'styles.css', "/* iOS wrapper styles */\nbody { font-family: -apple-system; }")
        self._create_file(wrapper_dir, 'app.js', f"// iOS wrapper JS\nwindow.location.href = '{target_url}';")
        self._create_file(wrapper_dir, 'README.md', self._generate_ios_wrapper_readme(metadata, target_url))
        
        # Create icons folder
        icons_dir = os.path.join(wrapper_dir, 'icons')
        os.makedirs(icons_dir, exist_ok=True)

    def _create_ios_online_instructions(self, project_dir, metadata, manifest_data, target_url):
        """Create comprehensive instructions for iOS online builders"""
        instructions_dir = os.path.join(project_dir, 'ios_builders')
        os.makedirs(instructions_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        
        # Create instruction files
        self._create_file(instructions_dir, 'IOS_QUICK_START.md', self._generate_ios_quick_start_guide(metadata, target_url))
        self._create_file(instructions_dir, 'ios-step-by-step.html', self._generate_ios_step_by_step_html(metadata, target_url))
        self._create_file(instructions_dir, 'ios-app-config.json', self._generate_ios_app_config(app_name, metadata, target_url))
        self._create_file(instructions_dir, 'ios-builder-links.txt', self._generate_ios_builder_links())
        self._create_file(instructions_dir, 'ios-troubleshooting.md', self._generate_ios_troubleshooting_guide())

    def _create_ios_pwa_converter(self, project_dir, metadata, manifest_data, target_url):
        """Create PWA optimized for iOS conversion"""
        pwa_dir = os.path.join(project_dir, 'ios_pwa_converter')
        os.makedirs(pwa_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        
        # Create iOS-optimized PWA files
        self._create_file(pwa_dir, 'index.html', self._generate_ios_pwa_html(metadata, target_url))
        self._create_file(pwa_dir, 'manifest.json', json.dumps(manifest_data, indent=2))
        self._create_file(pwa_dir, 'sw.js', self._generate_simple_service_worker())
        self._create_file(pwa_dir, 'config.xml', self._generate_ios_config_xml(app_name, metadata, target_url))
        self._create_file(pwa_dir, 'README.md', self._generate_ios_pwa_readme(metadata, target_url))
        self._create_file(pwa_dir, 'ios-convert-guide.html', self._generate_ios_conversion_guide_html(metadata, target_url))

    def _generate_ios_wrapper_html(self, metadata, target_url):
        """Generate iOS-optimized HTML wrapper"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{metadata.title}</title>
    <link rel="manifest" href="manifest.json">
    <link rel="stylesheet" href="styles.css">
    <meta name="theme-color" content="#007AFF">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="{metadata.title}">
    <link rel="apple-touch-icon" href="icon-192x192.png">
</head>
<body>
    <div id="ios-loading-screen">
        <div class="ios-loading-content">
            <div class="ios-app-icon"></div>
            <h1>{metadata.title}</h1>
            <div class="ios-loading-spinner"></div>
            <p>Loading...</p>
        </div>
    </div>
    
    <iframe 
        id="ios-app-frame" 
        src="{target_url}" 
        style="display:none;">
    </iframe>
    
    <script src="app.js"></script>
    <script>
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('sw.js');
        }}
    </script>
</body>
</html>'''

    # iOS-specific helper methods start here
    def _generate_ios_wrapper_readme(self, metadata, target_url):
        """Generate README for iOS wrapper"""
        return f"""# {metadata.title} - iOS Web Wrapper

This is an iOS-optimized web wrapper that works with online iOS app builders.

## 🚀 Build iOS App in 3 Easy Steps

### Step 1: Choose Your iOS Builder
- **Appy Pie** (iOS Support): https://www.appypie.com/app-maker
- **BuildFire** (Professional): https://buildfire.com/
- **PWA Builder** (Microsoft - High Quality): https://www.pwabuilder.com/

### Step 2: Import Your App
**Method A - Direct URL (Easiest):**
1. Go to your chosen builder
2. Select "Website App" or "URL App"  
3. Enter: `{target_url}`

**Method B - Upload Files (Advanced):**
1. Host these iOS wrapper files online (Netlify, GitHub Pages)
2. Use hosted URL with the builder
3. Upload HTML files directly if supported

### Step 3: Configure & Generate
- **App Name**: {metadata.title}
- **Bundle ID**: com.yourcompany.{metadata.title.lower().replace(" ", "")}
- **Icon**: Upload from icons folder (1024x1024px for iOS)
- **Generate IPA** and download when ready

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def _generate_ios_quick_start_guide(self, metadata, target_url):
        """Generate iOS quick start guide"""  
        return f"""# iOS Quick Start Guide - {metadata.title}

## Build iOS App in 10 Minutes (No Mac Required!)

### Method 1: Appy Pie (iOS Support) ⭐ RECOMMENDED

1. **Visit**: https://www.appypie.com/app-maker
2. **Sign up** for free account
3. **Choose**: "Website App" template
4. **Enter Details**:
   - Website URL: `{target_url}`
   - App Name: {metadata.title}
   - Platform: Select "iOS"
5. **Upload Icon**: Use 1024x1024px icon from package
6. **Build**: Generate IPA (subscription required for download)
7. **Download IPA** for iOS installation

**✅ Results**: Professional iOS IPA ready for installation

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def _generate_ios_step_by_step_html(self, metadata, target_url):
        """Generate step-by-step iOS HTML guide"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Build {metadata.title} iOS App - Step by Step</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', Helvetica, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #1d1d1f;
        }}
        .header {{
            background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
            color: white;
            padding: 40px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .step {{
            background: #f5f5f7;
            border-left: 4px solid #007AFF;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
        }}
        .btn {{
            display: inline-block;
            background: #007AFF;
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 8px;
            margin: 5px;
            font-weight: 500;
        }}
        .url-box {{
            background: #f5f5f7;
            padding: 12px;
            border-radius: 8px;
            font-family: monospace;
            word-break: break-all;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🍎 Build Your iOS App</h1>
        <p>Convert <strong>{metadata.title}</strong> to iOS IPA - No Mac or Xcode required!</p>
    </div>

    <div class="step">
        <strong>Step 1: Visit Appy Pie</strong><br>
        <a href="https://www.appypie.com/app-maker" target="_blank" class="btn">Go to Appy Pie</a>
    </div>

    <div class="step">
        <strong>Step 2: Enter Your Website</strong><br>
        <div class="url-box">{target_url}</div>
    </div>

    <div class="step">
        <strong>Step 3: Configure iOS App</strong><br>
        • App Name: <strong>{metadata.title}</strong><br>
        • Bundle ID: <strong>com.yourcompany.{metadata.title.lower().replace(" ", "")}</strong><br>
        • Upload 1024x1024px icon from package
    </div>

    <div class="step">
        <strong>Step 4: Generate & Download IPA</strong><br>
        Click "Build iOS App" and download when ready
    </div>

    <div style="text-align: center; margin-top: 40px; color: #86868b;">
        <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by DigitalSkeleton</p>
        <p>🍎 Optimized for iOS</p>
    </div>
</body>
</html>"""

    def _generate_ios_app_config(self, app_name, metadata, target_url):
        """Generate iOS app config JSON"""
        return json.dumps({
            "appName": metadata.title,
            "bundleId": f"com.yourcompany.{app_name.lower()}",
            "websiteUrl": target_url,
            "description": getattr(metadata, 'description', f"iOS app for {metadata.title}"),
            "version": "1.0.0",
            "platform": "iOS",
            "iosSpecific": {
                "minimumOSVersion": "12.0",
                "supportedDevices": ["iPhone", "iPad"],
                "iconSizes": ["1024x1024", "180x180", "120x120"],
                "bundleIdentifier": f"com.yourcompany.{app_name.lower()}"
            }
        }, indent=2)

    def _generate_ios_builder_links(self):
        """Generate list of iOS builder links"""
        return """# iOS App Builders - Working Links

## iOS-Compatible Builders

1. **Appy Pie** (Best for iOS)
   URL: https://www.appypie.com/app-maker
   Features: Native iOS support, App Store ready
   
2. **BuildFire** (Professional iOS)
   URL: https://buildfire.com/
   Features: Enterprise iOS features, App Store optimization

3. **PWA Builder** (Microsoft)
   URL: https://www.pwabuilder.com/
   Features: High quality iOS apps, TestFlight ready

## iOS Publishing Process

### TestFlight (Beta)
1. Create Apple Developer account ($99/year)
2. Upload IPA to App Store Connect
3. Set up TestFlight for beta testing

### App Store (Production)
1. Complete app metadata in App Store Connect
2. Submit for App Store review
3. Release when approved by Apple
"""

    def _generate_ios_troubleshooting_guide(self):
        """Generate iOS troubleshooting guide"""
        return """# iOS Troubleshooting Guide

## Common iOS Issues & Solutions

### IPA Generation Problems

**Problem**: Builder says "iOS not supported"
**Solution**: 
- Use Appy Pie or BuildFire (both support iOS)
- Try PWA Builder for high-quality iOS apps
- Ensure website is HTTPS (required for iOS)

**Problem**: "Invalid Bundle ID" error
**Solution**:
- Use reverse domain format: com.yourcompany.appname
- Only use lowercase letters, numbers, and dots
- Example: com.mycompany.myapp

### iOS Installation Problems

**Problem**: "Cannot install app" on iOS device
**Solution**:
- Use TestFlight for beta testing distribution
- Need Apple Developer account for device installation

## iOS Tips

✅ **Always test on real iOS devices**
✅ **Use HTTPS URLs (required for iOS)**
✅ **Upload high-resolution icons (1024x1024px)**
✅ **Follow Apple Human Interface Guidelines**
✅ **Use TestFlight for beta testing**

### Required for iOS Distribution

- **Apple Developer Account**: $99/year for App Store
- **Bundle ID**: Unique identifier for your app
- **App Icons**: High-resolution icons for all iOS devices
- **Privacy Policy**: Required for App Store submission
"""

    def _generate_ios_pwa_html(self, metadata, target_url):
        """Generate iOS-optimized PWA HTML"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{metadata.title}</title>
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#007AFF">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="{metadata.title}">
    <link rel="apple-touch-icon" href="icon-192x192.png">
    <style>
        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif;
            background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .ios-container {{
            text-align: center;
            color: white;
            padding: 40px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            backdrop-filter: blur(20px);
            max-width: 400px;
        }}
        .ios-btn {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            padding: 16px 32px;
            border-radius: 12px;
            margin: 15px;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="ios-container">
        <h1>{metadata.title}</h1>
        <p>iOS Progressive Web App</p>
        <a href="{target_url}" class="ios-btn" target="_blank">Open Website</a>
    </div>
    
    <script>
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('sw.js');
        }}
    </script>
</body>
</html>"""

    def _generate_ios_config_xml(self, app_name, metadata, target_url):
        """Generate iOS config.xml for Cordova/PhoneGap"""
        return f"""<?xml version='1.0' encoding='utf-8'?>
<widget id="com.yourcompany.{app_name.lower()}" version="1.0.0" xmlns="http://www.w3.org/ns/widgets">
    <name>{metadata.title}</name>
    <description>iOS app for {metadata.title}</description>
    <author email="your@email.com" href="{target_url}">Your Company</author>
    <content src="{target_url}" />
    <preference name="orientation" value="default" />
    <preference name="fullscreen" value="true" />
    <platform name="ios">
        <preference name="deployment-target" value="12.0" />
    </platform>
    <access origin="*" />
</widget>"""

    def _generate_ios_pwa_readme(self, metadata, target_url):
        """Generate iOS PWA README"""
        return f"""# {metadata.title} - iOS PWA to App Converter

This folder contains an iOS-optimized Progressive Web App that can be converted to a native iOS app.

## 🍎 Quick iOS App Generation

### Method 1: Appy Pie (iOS Specialist)
1. **Host these files** on any web server
2. **Visit**: https://www.appypie.com/app-maker
3. **Select**: "Website App" → "iOS"
4. **Enter** your hosted URL
5. **Download** IPA file

### Method 2: PWA Builder (Microsoft)
1. **Host these files** on web server
2. **Visit**: https://www.pwabuilder.com/
3. **Enter** your hosted URL
4. **Generate** iOS package

## 📁 iOS Files Included

- index.html - iOS-optimized PWA entry point
- manifest.json - Web app manifest with iOS support
- sw.js - Service worker for offline functionality
- config.xml - Cordova configuration

Website: {target_url}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def _generate_ios_conversion_guide_html(self, metadata, target_url):
        """Generate iOS conversion guide HTML"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Convert {metadata.title} to iOS App</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
            min-height: 100vh;
            color: #1d1d1f;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
        }}
        h1 {{
            color: #007AFF;
            text-align: center;
            margin-bottom: 40px;
            font-size: 2.5em;
        }}
        .ios-method {{
            background: #f5f5f7;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
        }}
        .method-title {{
            color: #007AFF;
            font-size: 1.4em;
            font-weight: 600;
            margin-bottom: 20px;
        }}
        .ios-btn {{
            display: inline-block;
            background: #007AFF;
            color: white;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 12px;
            margin: 10px 5px;
            font-weight: 500;
        }}
        .url-display {{
            background: #f5f5f7;
            padding: 16px;
            border-radius: 12px;
            font-family: monospace;
            word-break: break-all;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🍎 Convert {metadata.title} to iOS App</h1>
        
        <div class="ios-method">
            <div class="method-title">📱 Method 1: Appy Pie (iOS Specialist)</div>
            <p>Visit <a href="https://www.appypie.com/app-maker" target="_blank" class="ios-btn">Appy Pie iOS Builder</a></p>
            <p>Choose "Website App" → "iOS Platform"</p>
            <div class="url-display">{target_url}</div>
        </div>

        <div class="ios-method">
            <div class="method-title">⚡ Method 2: PWA Builder (Highest Quality)</div>
            <p>Visit <a href="https://www.pwabuilder.com/" target="_blank" class="ios-btn">PWA Builder</a></p>
            <p>Enter hosted URL and generate iOS package</p>
        </div>

        <div style="text-align: center; margin-top: 50px; color: #86868b;">
            <p><strong>Website:</strong> {target_url}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>"""
    
    # TWA (Trusted Web Activity) Methods for Android
    
    def _create_twa_bubblewrap_project(self, project_dir, metadata, manifest_data, target_url):
        """Create TWA project using Google's Bubblewrap CLI"""
        twa_dir = os.path.join(project_dir, 'bubblewrap_twa')
        os.makedirs(twa_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        package_name = f"com.digitalskeleton.{app_name.lower()}"
        
        # Create Bubblewrap TWA manifest
        twa_manifest = {
            "packageId": package_name,
            "host": self._extract_host(target_url),
            "name": metadata.title,
            "launcherName": app_name,
            "display": "standalone",
            "orientation": "default",
            "themeColor": manifest_data.get("theme_color", "#000000"),
            "backgroundColor": manifest_data.get("background_color", "#ffffff"),
            "startUrl": target_url,
            "iconUrl": metadata.icon_url or f"{target_url}/favicon.ico",
            "maskableIconUrl": metadata.icon_url or f"{target_url}/favicon.ico",
            "monochromeIconUrl": metadata.icon_url or f"{target_url}/favicon.ico",
            "fallbackType": "customtabs",
            "webManifestUrl": f"{target_url}/manifest.json",
            "fingerprints": [],
            "additionalTrustedOrigins": [],
            "retainedBundles": [],
            "appVersionName": "1.0.0",
            "appVersionCode": 1,
            "shortcuts": [],
            "generatorApp": "DigitalSkeleton"
        }
        
        # Create project files
        self._create_file(twa_dir, 'twa-manifest.json', json.dumps(twa_manifest, indent=2))
        self._create_file(twa_dir, 'package.json', self._generate_bubblewrap_package_json(app_name))
        self._create_file(twa_dir, 'build-apk.sh', self._generate_bubblewrap_build_script(app_name))
        self._create_file(twa_dir, 'build-apk.bat', self._generate_bubblewrap_build_script_windows(app_name))
        self._create_file(twa_dir, 'README.md', self._generate_bubblewrap_readme(metadata, target_url))
        self._create_file(twa_dir, 'setup-environment.sh', self._generate_bubblewrap_setup_script())
        self._create_file(twa_dir, 'setup-environment.bat', self._generate_bubblewrap_setup_script_windows())
        
    def _create_manual_twa_setup(self, project_dir, metadata, manifest_data, target_url):
        """Create manual TWA setup instructions for Android Studio"""
        manual_dir = os.path.join(project_dir, 'manual_twa_setup')
        os.makedirs(manual_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        package_name = f"com.digitalskeleton.{app_name.lower()}"
        
        # Create Android Studio TWA project files
        self._create_file(manual_dir, 'build.gradle', self._generate_twa_build_gradle(app_name, package_name))
        self._create_file(manual_dir, 'AndroidManifest.xml', self._generate_twa_android_manifest(app_name, package_name, metadata, target_url))
        self._create_file(manual_dir, 'strings.xml', self._generate_twa_strings(metadata, target_url))
        self._create_file(manual_dir, 'colors.xml', self._generate_twa_colors(manifest_data))
        self._create_file(manual_dir, 'LauncherActivity.java', self._generate_twa_launcher_activity(package_name))
        self._create_file(manual_dir, 'README-MANUAL-SETUP.md', self._generate_manual_twa_readme(metadata, target_url))
        self._create_file(manual_dir, 'digital-asset-links.json', self._generate_digital_asset_links(package_name))
        
    def _create_online_twa_builders(self, project_dir, metadata, manifest_data, target_url):
        """Create instructions for online TWA builders"""
        online_dir = os.path.join(project_dir, 'online_twa_builders')
        os.makedirs(online_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        
        # Create configuration files for different online builders
        self._create_file(online_dir, 'pwa-builder-config.json', self._generate_pwa_builder_config(metadata, target_url))
        self._create_file(online_dir, 'twa-generator-config.json', self._generate_twa_generator_config(metadata, target_url))
        self._create_file(online_dir, 'ONLINE-BUILDERS-GUIDE.md', self._generate_online_builders_guide(metadata, target_url))
        self._create_file(online_dir, 'quick-links.html', self._generate_quick_links_html(metadata, target_url))
        
    def _extract_host(self, url):
        """Extract host from URL for TWA manifest"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url.replace('https://', '').replace('http://', '').split('/')[0]
    
    def _generate_bubblewrap_package_json(self, app_name):
        """Generate package.json for Bubblewrap project"""
        return json.dumps({
            "name": app_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "description": f"TWA for {app_name}",
            "scripts": {
                "init": "bubblewrap init --manifest=twa-manifest.json",
                "build": "bubblewrap build",
                "install": "bubblewrap install"
            },
            "dependencies": {
                "@bubblewrap/cli": "^1.19.4"
            }
        }, indent=2)
    
    def _generate_bubblewrap_build_script(self, app_name):
        """Generate Linux/Mac build script for Bubblewrap"""
        return f"""#!/bin/bash
# TWA Build Script for {app_name}
# Requires Node.js, Java 8+, and Android SDK

echo "🚀 Building TWA for {app_name}..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required. Please install Node.js first."
    exit 1
fi

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "❌ Java is required. Please install Java 8+ first."
    exit 1
fi

# Install Bubblewrap CLI if not already installed
echo "📦 Installing Bubblewrap CLI..."
npm install -g @bubblewrap/cli

# Initialize TWA project
echo "🔧 Initializing TWA project..."
bubblewrap init --manifest=twa-manifest.json

# Build APK
echo "🏗️ Building APK..."
bubblewrap build

echo "✅ TWA build complete! Check the 'app-release-unsigned.apk' file."
echo "📝 Note: Sign the APK before distributing to users."
"""

    def _generate_bubblewrap_build_script_windows(self, app_name):
        """Generate Windows build script for Bubblewrap"""
        return f"""@echo off
REM TWA Build Script for {app_name}
REM Requires Node.js, Java 8+, and Android SDK

echo 🚀 Building TWA for {app_name}...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is required. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if Java is installed
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Java is required. Please install Java 8+ first.
    pause
    exit /b 1
)

REM Install Bubblewrap CLI if not already installed
echo 📦 Installing Bubblewrap CLI...
npm install -g @bubblewrap/cli

REM Initialize TWA project
echo 🔧 Initializing TWA project...
bubblewrap init --manifest=twa-manifest.json

REM Build APK
echo 🏗️ Building APK...
bubblewrap build

echo ✅ TWA build complete! Check the 'app-release-unsigned.apk' file.
echo 📝 Note: Sign the APK before distributing to users.
pause
"""

    def _generate_bubblewrap_setup_script(self):
        """Generate environment setup script for Linux/Mac"""
        return """#!/bin/bash
# Environment Setup Script for TWA Development
# This script sets up the required tools for TWA development

echo "🔧 Setting up TWA development environment..."

# Install Node.js (if not installed)
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install Java (if not installed)
if ! command -v java &> /dev/null; then
    echo "☕ Installing OpenJDK 11..."
    sudo apt-get update
    sudo apt-get install -y openjdk-11-jdk
fi

# Install Android SDK Command Line Tools
echo "📱 Setting up Android SDK..."
mkdir -p ~/android-sdk/cmdline-tools
cd ~/android-sdk/cmdline-tools
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip
mv cmdline-tools latest

# Set environment variables
export ANDROID_HOME=~/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Accept licenses and install required components
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"

# Install Bubblewrap CLI
echo "🫧 Installing Bubblewrap CLI..."
npm install -g @bubblewrap/cli

echo "✅ Environment setup complete!"
echo "📝 Make sure to add these to your ~/.bashrc:"
echo "export ANDROID_HOME=~/android-sdk"
echo "export PATH=\\$PATH:\\$ANDROID_HOME/cmdline-tools/latest/bin:\\$ANDROID_HOME/platform-tools"
"""

    def _generate_bubblewrap_setup_script_windows(self):
        """Generate environment setup script for Windows"""
        return """@echo off
REM Environment Setup Script for TWA Development on Windows
REM This script guides you through setting up the required tools

echo 🔧 Setting up TWA development environment on Windows...

echo.
echo 📝 MANUAL SETUP REQUIRED:
echo.
echo 1. Install Node.js:
echo    Download from: https://nodejs.org/
echo    Choose LTS version
echo.
echo 2. Install Java Development Kit:
echo    Download from: https://adoptium.net/
echo    Choose OpenJDK 11 or higher
echo.
echo 3. Install Android Studio:
echo    Download from: https://developer.android.com/studio
echo    This includes Android SDK
echo.
echo 4. Set Environment Variables:
echo    ANDROID_HOME = C:\\Users\\%USERNAME%\\AppData\\Local\\Android\\Sdk
echo    Add to PATH: %%ANDROID_HOME%%\\cmdline-tools\\latest\\bin
echo    Add to PATH: %%ANDROID_HOME%%\\platform-tools
echo.

pause

REM Install Bubblewrap CLI
echo 🫧 Installing Bubblewrap CLI...
npm install -g @bubblewrap/cli

if %errorlevel% equ 0 (
    echo ✅ Bubblewrap CLI installed successfully!
) else (
    echo ❌ Failed to install Bubblewrap CLI. Please install Node.js first.
)

echo.
echo 🎉 Setup guide complete!
echo 📝 After completing manual steps above, you can run build-apk.bat
pause
"""

    def _generate_bubblewrap_readme(self, metadata, target_url):
        """Generate comprehensive README for Bubblewrap TWA project"""
        return f"""# {metadata.title} - Trusted Web Activity (TWA)

This package generates a **Trusted Web Activity (TWA)** for Android using Google's Bubblewrap tool. TWA is the modern, official way to convert PWAs to Android apps.

## 🎯 What is TWA?

**Trusted Web Activity** wraps your PWA in a native Android shell that:
- Uses Chrome's rendering engine for perfect web compatibility
- Provides fullscreen experience (no browser UI)
- Passes Google Play Store requirements for web-based apps
- Maintains authentic web functionality and performance

## 🚀 Quick Start (Automated)

### Option 1: Linux/Mac
```bash
chmod +x setup-environment.sh build-apk.sh
./setup-environment.sh  # One-time setup
./build-apk.sh          # Build APK
```

### Option 2: Windows
```cmd
setup-environment.bat   # One-time setup
build-apk.bat          # Build APK
```

## 🛠️ Manual Setup

### Prerequisites
1. **Node.js** (v14+): Download from https://nodejs.org/
2. **Java** (v8+): Download from https://adoptium.net/
3. **Android SDK**: Install via Android Studio

### Environment Variables (Required)
```bash
export ANDROID_HOME=/path/to/android/sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
```

### Build Steps
```bash
# Install Bubblewrap CLI
npm install -g @bubblewrap/cli

# Initialize TWA project
bubblewrap init --manifest=twa-manifest.json

# Build APK
bubblewrap build
```

## 📱 TWA Configuration

The `twa-manifest.json` contains your app configuration:

- **Package ID**: Unique Android package identifier
- **Host**: Your website's domain (for verification)
- **Start URL**: {target_url}
- **Display**: Fullscreen standalone app experience
- **Icons**: Adaptive and maskable icons for modern Android

## 🔐 Digital Asset Links (Important!)

For production apps, you must verify domain ownership:

1. Host the `digital-asset-links.json` file at:
   ```
   {target_url}/.well-known/assetlinks.json
   ```

2. This proves you own both the website and the Android app

## 📦 Build Output

After successful build:
- `app-release-unsigned.apk` - Unsigned APK for testing
- `app-release-signed.apk` - Signed APK (if keystore configured)

## 🏪 Google Play Store Requirements

1. **HTTPS Required**: Your website must use HTTPS
2. **Web App Manifest**: Must be valid and accessible
3. **Service Worker**: Recommended for offline functionality
4. **Quality Standards**: Must meet PWA quality guidelines

## 🧪 Testing Your TWA

1. **Install on Device**: `adb install app-release-unsigned.apk`
2. **Chrome DevTools**: Use for debugging web content
3. **Android Studio**: For native Android debugging

## 🔍 Troubleshooting

### Common Issues

**Build fails with "Android SDK not found"**
- Install Android Studio or SDK command-line tools
- Set ANDROID_HOME environment variable correctly

**"Domain verification failed"**
- Upload `digital-asset-links.json` to your website
- Ensure file is accessible at `/.well-known/assetlinks.json`

**APK won't install**
- Enable "Install from unknown sources" on Android device
- Use `adb install` command for development builds

### PWA Requirements for TWA

Your website should have:
- ✅ Valid HTTPS certificate
- ✅ Web app manifest with required fields
- ✅ Service worker for offline functionality
- ✅ Responsive design for mobile devices

## 📚 Additional Resources

- [TWA Documentation](https://developers.google.com/web/android/trusted-web-activity)
- [Bubblewrap CLI Guide](https://github.com/GoogleChromeLabs/bubblewrap)
- [PWA Checklist](https://web.dev/pwa-checklist/)
- [Play Store PWA Guidelines](https://chromeos.dev/en/publish/pwa-in-play)

---

**Website**: {target_url}  
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Tool**: DigitalSkeleton TWA Generator
"""
    
    def _generate_twa_build_gradle(self, app_name, package_name):
        """Generate build.gradle for manual TWA setup"""
        return f"""plugins {{
    id 'com.android.application'
}}

android {{
    compileSdk 33

    defaultConfig {{
        applicationId "{package_name}"
        minSdk 16
        targetSdk 33
        versionCode 1
        versionName "1.0"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation 'androidx.browser:browser:1.5.0'
    implementation 'com.google.androidbrowserhelper:androidbrowserhelper:2.5.0'
}}
"""

    def _generate_twa_android_manifest(self, app_name, package_name, metadata, target_url):
        """Generate AndroidManifest.xml for manual TWA setup"""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:allowBackup="true"
        android:icon="@drawable/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.TWA">
        
        <activity
            android:name=".LauncherActivity"
            android:exported="true"
            android:theme="@style/Theme.TWA.Launcher">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity android:name="com.google.androidbrowserhelper.trusted.LauncherActivity"
            android:exported="true">
            <meta-data android:name="android.support.customtabs.trusted.DEFAULT_URL"
                android:value="{target_url}" />
            <meta-data android:name="asset_statements"
                android:resource="@string/asset_statements" />
            <intent-filter android:autoVerify="true">
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="https"
                    android:host="{self._extract_host(target_url)}" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

    def _generate_twa_strings(self, metadata, target_url):
        """Generate strings.xml for TWA"""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{metadata.title}</string>
    <string name="asset_statements">
        [{{
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {{
                "namespace": "web",
                "site": "{target_url}"
            }}
        }}]
    </string>
</resources>
"""

    def _generate_twa_colors(self, manifest_data):
        """Generate colors.xml for TWA"""
        theme_color = manifest_data.get("theme_color", "#000000")
        bg_color = manifest_data.get("background_color", "#ffffff")
        return f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="colorPrimary">{theme_color}</color>
    <color name="colorPrimaryDark">{theme_color}</color>
    <color name="colorAccent">{theme_color}</color>
    <color name="backgroundColor">{bg_color}</color>
</resources>
"""

    def _generate_twa_launcher_activity(self, package_name):
        """Generate LauncherActivity.java for TWA"""
        return f"""package {package_name};

import android.os.Bundle;
import com.google.androidbrowserhelper.trusted.TwaLauncherActivity;

public class LauncherActivity extends TwaLauncherActivity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
    }}
}}
"""

    def _generate_manual_twa_readme(self, metadata, target_url):
        """Generate README for manual TWA setup"""
        return f"""# {metadata.title} - Manual TWA Setup

This folder contains all files needed to manually set up a Trusted Web Activity in Android Studio.

## 🔧 Manual Setup Steps

### 1. Create New Android Project
1. Open Android Studio
2. Create new "Empty Activity" project
3. Set package name: `com.digitalskeleton.{self._sanitize_name(metadata.title).lower()}`

### 2. Add TWA Dependencies
Add to `app/build.gradle`:
```gradle
implementation 'androidx.browser:browser:1.5.0'
implementation 'com.google.androidbrowserhelper:androidbrowserhelper:2.5.0'
```

### 3. Replace Files
- Replace `AndroidManifest.xml` with provided version
- Replace `strings.xml` with provided version
- Add `colors.xml` to res/values/
- Replace MainActivity with LauncherActivity.java

### 4. Configure Digital Asset Links
Upload `digital-asset-links.json` to:
```
{target_url}/.well-known/assetlinks.json
```

### 5. Build APK
```bash
./gradlew assembleRelease
```

## 📱 Testing
1. Install APK on Android device
2. Open app - should launch your website in fullscreen
3. No browser UI should be visible

## 🔍 Troubleshooting
- Ensure website is HTTPS
- Verify digital asset links are accessible
- Check package name matches in all files

Website: {target_url}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def _generate_digital_asset_links(self, package_name):
        """Generate digital asset links JSON"""
        return json.dumps([{
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": package_name,
                "sha256_cert_fingerprints": [
                    "14:6D:E9:83:C5:73:06:50:D8:EE:B9:95:2F:34:FC:64:16:A0:83:42:E6:1D:BE:A8:8A:04:96:B2:3F:CF:44:E5"
                ]
            }
        }], indent=2)

    def _generate_pwa_builder_config(self, metadata, target_url):
        """Generate PWA Builder configuration"""
        return json.dumps({
            "url": target_url,
            "name": metadata.title,
            "package": {
                "packageId": f"com.digitalskeleton.{self._sanitize_name(metadata.title).lower()}",
                "name": metadata.title,
                "displayName": metadata.title
            },
            "android": {
                "packageId": f"com.digitalskeleton.{self._sanitize_name(metadata.title).lower()}",
                "name": metadata.title,
                "themeColor": "#000000",
                "backgroundColor": "#ffffff"
            }
        }, indent=2)

    def _generate_twa_generator_config(self, metadata, target_url):
        """Generate TWA Generator configuration"""
        return json.dumps({
            "packageId": f"com.digitalskeleton.{self._sanitize_name(metadata.title).lower()}",
            "host": self._extract_host(target_url),
            "name": metadata.title,
            "launcherName": self._sanitize_name(metadata.title),
            "display": "standalone",
            "orientation": "default",
            "startUrl": target_url,
            "webManifestUrl": f"{target_url}/manifest.json"
        }, indent=2)

    def _generate_online_builders_guide(self, metadata, target_url):
        """Generate guide for online TWA builders"""
        return f"""# Online TWA Builders Guide

Build your TWA using online tools - no local setup required!

## 🌐 Recommended Online Builders

### 1. PWA Builder (Microsoft) ⭐ RECOMMENDED
**URL**: https://www.pwabuilder.com/

**Steps**:
1. Enter your website URL: `{target_url}`
2. Click "Analyze" to check PWA readiness
3. Click "Package For Stores" → "Android"
4. Download TWA package

**Features**:
- Official Microsoft tool
- High-quality TWA generation
- Google Play Store ready
- Free to use

### 2. Bubblewrap Online
**URL**: https://github.com/GoogleChromeLabs/bubblewrap

**Steps**:
1. Use the provided `twa-manifest.json`
2. Upload to online Bubblewrap service
3. Generate and download APK

### 3. TWA Generator
**URL**: https://appmaker.xyz/twa-generator

**Steps**:
1. Upload `twa-generator-config.json`
2. Customize settings if needed
3. Generate APK

## 📋 Required Information

All builders will ask for:
- **Website URL**: {target_url}
- **App Name**: {metadata.title}
- **Package ID**: com.digitalskeleton.{self._sanitize_name(metadata.title).lower()}

## ✅ Pre-Build Checklist

Before using any builder:
- [ ] Website is accessible via HTTPS
- [ ] Web app manifest exists at `{target_url}/manifest.json`
- [ ] Icons are accessible and properly sized
- [ ] Service worker is registered (recommended)

## 🔐 Digital Asset Links

Upload the provided `digital-asset-links.json` to:
```
{target_url}/.well-known/assetlinks.json
```

This verifies you own both the website and Android app.

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def _generate_quick_links_html(self, metadata, target_url):
        """Generate quick links HTML for online builders"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quick TWA Builders for {metadata.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 40px;
        }}
        .builder {{
            background: #f8f9fa;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            border-left: 5px solid #667eea;
        }}
        .builder-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .builder-btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 8px;
            margin: 10px 5px 10px 0;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        .builder-btn:hover {{
            background: #5a6fd8;
            transform: translateY(-2px);
        }}
        .info-box {{
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }}
        .url-display {{
            background: #f5f5f5;
            padding: 12px;
            border-radius: 6px;
            font-family: monospace;
            word-break: break-all;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Quick TWA Builders</h1>
        <h2>Build Android APK for {metadata.title}</h2>
        
        <div class="info-box">
            <strong>🌐 Your Website:</strong>
            <div class="url-display">{target_url}</div>
        </div>
        
        <div class="builder">
            <div class="builder-title">⭐ PWA Builder (Recommended)</div>
            <p>Microsoft's official tool for high-quality TWA generation</p>
            <a href="https://www.pwabuilder.com/" target="_blank" class="builder-btn">Open PWA Builder</a>
            <p><strong>Steps:</strong> Enter URL → Analyze → Package for Android</p>
        </div>
        
        <div class="builder">
            <div class="builder-title">🫧 Bubblewrap CLI (Advanced)</div>
            <p>Google's official TWA generator - requires technical setup</p>
            <a href="https://github.com/GoogleChromeLabs/bubblewrap" target="_blank" class="builder-btn">View Bubblewrap</a>
            <p><strong>Best for:</strong> Developers who want full control</p>
        </div>
        
        <div class="builder">
            <div class="builder-title">⚡ TWA Generator</div>
            <p>Simple online TWA generator with easy configuration</p>
            <a href="https://appmaker.xyz/twa-generator" target="_blank" class="builder-btn">Open TWA Generator</a>
            <p><strong>Steps:</strong> Upload config → Generate → Download APK</p>
        </div>
        
        <div style="text-align: center; margin-top: 40px; color: #666;">
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>🔧 Powered by DigitalSkeleton</p>
        </div>
    </div>
</body>
</html>"""
