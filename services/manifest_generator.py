import json
from urllib.parse import urlparse

def generate_manifest(metadata, start_url):
    """
    Generate a web app manifest based on scraped metadata
    """
    parsed_url = urlparse(start_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # Generate app name and short name
    app_name = metadata.title
    short_name = app_name[:12] if len(app_name) > 12 else app_name
    
    manifest = {
        "name": app_name,
        "short_name": short_name,
        "description": metadata.description or f"Mobile app for {app_name}",
        "start_url": start_url,
        "scope": base_url,
        "display": "standalone",
        "orientation": "any",
        "theme_color": metadata.theme_color or "#000000",
        "background_color": metadata.background_color or "#ffffff",
        "lang": "en",
        "dir": "ltr",
        "icons": []
    }
    
    # Add icons if available
    if metadata.icon_url:
        # Generate multiple icon sizes for better compatibility
        icon_sizes = [
            {"size": "72x72", "type": "image/png"},
            {"size": "96x96", "type": "image/png"},
            {"size": "128x128", "type": "image/png"},
            {"size": "144x144", "type": "image/png"},
            {"size": "152x152", "type": "image/png"},
            {"size": "192x192", "type": "image/png"},
            {"size": "384x384", "type": "image/png"},
            {"size": "512x512", "type": "image/png"}
        ]
        
        for icon_size in icon_sizes:
            manifest["icons"].append({
                "src": metadata.icon_url,
                "sizes": icon_size["size"],
                "type": icon_size["type"],
                "purpose": "any maskable"
            })
    
    # Add categories
    manifest["categories"] = ["productivity", "utilities"]
    
    # Add related applications (optional)
    manifest["prefer_related_applications"] = False
    
    # Add screenshots (placeholder)
    manifest["screenshots"] = [
        {
            "src": f"{base_url}/screenshot1.png",
            "sizes": "1280x720",
            "type": "image/png",
            "platform": "wide"
        },
        {
            "src": f"{base_url}/screenshot2.png", 
            "sizes": "750x1334",
            "type": "image/png",
            "platform": "narrow"
        }
    ]
    
    # Add shortcuts (example)
    manifest["shortcuts"] = [
        {
            "name": "Home",
            "short_name": "Home",
            "description": "Go to home page",
            "url": start_url,
            "icons": [
                {
                    "src": metadata.icon_url or "/icon-192.png",
                    "sizes": "96x96"
                }
            ]
        }
    ]
    
    return manifest

def generate_ios_config(metadata, start_url):
    """
    Generate iOS-specific configuration
    """
    return {
        "bundleIdentifier": f"com.pwabuilder.{metadata.title.lower().replace(' ', '').replace('-', '')}",
        "bundleVersion": "1.0",
        "displayName": metadata.title,
        "launchUrl": start_url,
        "statusBarStyle": "default",
        "orientation": "any",
        "fullScreen": False
    }

def generate_android_config(metadata, start_url):
    """
    Generate Android-specific configuration
    """
    return {
        "packageName": f"com.pwabuilder.{metadata.title.lower().replace(' ', '').replace('-', '')}",
        "versionCode": 1,
        "versionName": "1.0",
        "displayName": metadata.title,
        "launchUrl": start_url,
        "orientation": "any",
        "fullScreen": False,
        "permissions": [
            "android.permission.INTERNET",
            "android.permission.ACCESS_NETWORK_STATE"
        ]
    }

def generate_windows_config(metadata, start_url):
    """
    Generate Windows-specific configuration
    """
    return {
        "packageIdentity": f"PWABuilder.{metadata.title.replace(' ', '')}",
        "publisherName": "PWA Builder",
        "version": "1.0.0.0",
        "displayName": metadata.title,
        "description": metadata.description,
        "startUrl": start_url,
        "windowsFeatures": [
            "webApplicationManifest"
        ]
    }
