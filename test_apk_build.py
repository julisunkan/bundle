#!/usr/bin/env python3
"""
Test script to verify APK building functionality
"""

import sys
import os
sys.path.append('.')

from services.apk_builder import APKBuilder
from services.web_scraper import scrape_website_metadata
from services.manifest_generator import generate_manifest

class MockMetadata:
    def __init__(self, title, icon_url=None):
        self.title = title
        self.icon_url = icon_url

def test_apk_build():
    """Test APK building with a simple example"""
    print("Testing APK build functionality...")
    
    try:
        # Create test metadata
        metadata = MockMetadata("Test App", "https://example.com/icon.png")
        manifest_data = {
            "name": "Test App",
            "short_name": "TestApp",
            "start_url": "/",
            "display": "standalone",
            "theme_color": "#000000",
            "background_color": "#ffffff"
        }
        
        # Initialize APK builder
        builder = APKBuilder()
        
        # Test APK building
        result = builder.build_android_apk(
            metadata=metadata,
            manifest_data=manifest_data,
            job_id="test123",
            target_url="https://example.com"
        )
        
        print(f"✓ APK build test completed successfully: {result}")
        return True
        
    except Exception as e:
        print(f"✗ APK build test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_apk_build()
    sys.exit(0 if success else 1)