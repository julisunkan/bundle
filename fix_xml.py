import re

# Read the file
with open('services/apk_builder.py', 'r') as f:
    content = f.read()

# Define the corrected config XML generation function
corrected_function = '''    def _generate_cordova_config_xml(self, metadata, target_url):
        """Generate the config.xml file for Cordova"""
        app_name = self._sanitize_name(metadata.title)
        package_name = f"com.digitalskeleton.{app_name.lower()}"
        
        config_xml = """<?xml version='1.0' encoding='utf-8'?>
<widget id="%s" version="1.0.0" xmlns="http://www.w3.org/ns/widgets" xmlns:cdv="http://cordova.apache.org/ns/1.0">
    <name>%s</name>
    <description>
        %s
    </description>
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
        
        <!-- Target Android API level -->
        <preference name="android-targetSdkVersion" value="33" />
        <preference name="android-minSdkVersion" value="21" />
    </platform>
    
    <!-- Plugins compatible with Cordova Android 12.x -->
    <plugin name="cordova-plugin-inappbrowser" version="6.0.0" />
    <plugin name="cordova-plugin-network-information" version="3.0.0" />
    <plugin name="cordova-plugin-splashscreen" version="6.0.0" />
    
    <!-- Universal Links -->
    <plugin name="cordova-plugin-customurlscheme" version="5.0.0">
        <variable name="URL_SCHEME" value="%s" />
    </plugin>
</widget>""" % (
            package_name,
            metadata.title,
            metadata.description or f"Mobile app for {metadata.title}",
            app_name.lower()
        )
        
        return config_xml'''

# Find the function and replace it
pattern = r'    def _generate_cordova_config_xml\(self, metadata, target_url\):.*?(?=\n    def|\nclass|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    content = content.replace(match.group(0), corrected_function)
    print("Found and replaced the function")
else:
    print("Function not found with regex, trying manual approach")
    # Try to find the function manually
    lines = content.split('\n')
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if 'def _generate_cordova_config_xml' in line:
            start_idx = i
        elif start_idx is not None and (line.strip().startswith('def ') or line.strip().startswith('class ')):
            end_idx = i
            break
    
    if start_idx is not None:
        if end_idx is None:
            end_idx = len(lines)
        
        # Replace the function
        lines = lines[:start_idx] + corrected_function.split('\n') + lines[end_idx:]
        content = '\n'.join(lines)
        print(f"Manually replaced function from line {start_idx+1} to {end_idx}")

# Write the corrected content back
with open('services/apk_builder.py', 'w') as f:
    f.write(content)

print("XML generation function has been corrected")
