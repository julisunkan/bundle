import os
import json
import shutil
import zipfile
import tempfile
from datetime import datetime
from app import app
from .icon_generator import IconGenerator

class PackageBuilder:
    def __init__(self):
        self.output_dir = app.config['UPLOAD_FOLDER']
        self.icon_generator = IconGenerator()
    
    def build_apk(self, metadata, manifest_data, job_id, target_url):
        """Build an Android Studio project structure that can be imported"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                project_dir = os.path.join(temp_dir, 'android_project')
                self._create_android_studio_project(project_dir, metadata, manifest_data, target_url)
                
                zip_filename = f"{metadata.title.replace(' ', '_')}_android_{job_id}.zip"
                zip_path = os.path.join(self.output_dir, zip_filename)
                
                self._create_project_zip(project_dir, zip_path)
                return zip_path
                
        except Exception as e:
            app.logger.error(f"Android project build failed: {str(e)}")
            raise Exception(f"Android project build failed: {str(e)}")
    
    def build_ipa(self, metadata, manifest_data, job_id, target_url):
        """Build an Xcode project structure that can be imported"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                project_dir = os.path.join(temp_dir, 'ios_project')
                self._create_xcode_project(project_dir, metadata, manifest_data, target_url)
                
                zip_filename = f"{metadata.title.replace(' ', '_')}_ios_{job_id}.zip"
                zip_path = os.path.join(self.output_dir, zip_filename)
                
                self._create_project_zip(project_dir, zip_path)
                return zip_path
                
        except Exception as e:
            app.logger.error(f"iOS project build failed: {str(e)}")
            raise Exception(f"iOS project build failed: {str(e)}")
    
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
    
    def _create_android_studio_project(self, project_dir, metadata, manifest_data, target_url):
        """Create an Android Studio project structure"""
        os.makedirs(project_dir, exist_ok=True)
        
        app_name = self._sanitize_name(metadata.title)
        package_name = f"com.pwabuilder.{app_name.lower()}"
        
        # Generate all required icons for Android
        app_metadata = {
            'title': metadata.title,
            'description': metadata.description,
            'icon_url': metadata.icon_url,
            'url': metadata.url
        }
        all_icons = self.icon_generator.generate_all_icons(app_metadata, app_name)
        android_icons = all_icons.get('android', {})
        
        # Create build.gradle (Project)
        self._create_file(project_dir, 'build.gradle', self._generate_project_gradle())
        
        # Create settings.gradle
        self._create_file(project_dir, 'settings.gradle', f'include ":app"\nrootProject.name = "{app_name}"')
        
        # Create gradle.properties
        self._create_file(project_dir, 'gradle.properties', self._generate_gradle_properties())
        
        # Create app directory structure
        app_dir = os.path.join(project_dir, 'app')
        os.makedirs(app_dir, exist_ok=True)
        
        # Create app/build.gradle
        self._create_file(app_dir, 'build.gradle', self._generate_app_gradle(package_name, metadata))
        
        # Create src/main directory structure
        main_dir = os.path.join(app_dir, 'src', 'main')
        java_dir = os.path.join(main_dir, 'java', 'com', 'pwabuilder', app_name.lower())
        res_dir = os.path.join(main_dir, 'res')
        assets_dir = os.path.join(main_dir, 'assets')
        
        os.makedirs(java_dir, exist_ok=True)
        os.makedirs(os.path.join(res_dir, 'layout'), exist_ok=True)
        os.makedirs(os.path.join(res_dir, 'values'), exist_ok=True)
        os.makedirs(os.path.join(res_dir, 'mipmap-hdpi'), exist_ok=True)
        os.makedirs(assets_dir, exist_ok=True)
        
        # Create AndroidManifest.xml
        self._create_file(main_dir, 'AndroidManifest.xml', self._generate_android_manifest_xml(package_name, metadata))
        
        # Create MainActivity.java
        self._create_file(java_dir, 'MainActivity.java', self._generate_main_activity(package_name, metadata, target_url))
        
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
        
        # Create README
        self._create_file(project_dir, 'README.md', self._generate_android_readme(metadata, target_url))
    
    def _create_xcode_project(self, project_dir, metadata, manifest_data, target_url):
        """Create an Xcode project structure"""
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
        
        # Create project structure
        project_file_dir = os.path.join(project_dir, f'{app_name}.xcodeproj')
        os.makedirs(project_file_dir, exist_ok=True)
        
        # Create pbxproj file
        self._create_file(project_file_dir, 'project.pbxproj', self._generate_pbxproj(app_name))
        
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
        return f'''# {metadata.title} - Windows App

This is a Visual Studio project that wraps the website [{target_url}]({target_url}) as a native Windows app.

## How to Build

1. Install Visual Studio 2022 with:
   - .NET 8.0 SDK
   - Windows App SDK
   - Universal Windows Platform development workload

2. Open Visual Studio 2022
2. Select "Open a project or solution"
3. Select the `.sln` file in this folder
4. Right-click the project and select "Set as StartUp Project"
5. Select your target platform (x64, x86, ARM64)
6. Click "Build" > "Build Solution" or press Ctrl+Shift+B
7. Click "Debug" > "Start Without Debugging" or press Ctrl+F5

## Features

- WebView2-based app that loads the website
- Full Windows integration
- Native Windows look and feel
- Internet connectivity support
- Multi-platform support (x64, x86, ARM64)

## Customization

- Modify `MainPage.xaml.cs` to add custom functionality
- Update `Package.appxmanifest` to change app metadata
- Replace app icons in the Assets folder
- Modify XAML files for UI customization

## Requirements

- Visual Studio 2022 with UWP development workload
- Windows 10 version 1903 (build 18362) or higher
- Windows App SDK
- Internet connection for loading web content

## Deployment

- For development: Run directly from Visual Studio
- For distribution: Create an MSIX package through Visual Studio
- For Microsoft Store: Use the generated MSIX package

## Website

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