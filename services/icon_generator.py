import os
import io
import base64
import requests
from PIL import Image, ImageDraw, ImageFont
# import cairosvg  # Will handle SVG without cairo for now
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class IconGenerator:
    """
    Comprehensive icon generator for mobile app packages.
    Generates all required icon sizes for Android, iOS, and Windows platforms.
    """
    
    # Icon size requirements for different platforms
    ANDROID_ICON_SIZES = [
        # Android Launcher Icons
        36, 48, 72, 96, 144, 192,
        # Additional Android sizes
        512, 1024
    ]
    
    IOS_ICON_SIZES = [
        # iPhone and iPad icons
        20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180,
        # App Store icon
        1024
    ]
    
    WINDOWS_ICON_SIZES = [
        # Windows tile sizes
        44, 55, 71, 89, 107, 142, 150, 284, 310,
        # Store logo
        50, 620
    ]
    
    def __init__(self):
        self.temp_dir = 'temp_icons'
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def download_icon(self, icon_url, base_url=None):
        """
        Download icon from URL with proper error handling.
        """
        try:
            if not icon_url:
                return None
                
            # Handle relative URLs
            if base_url and not icon_url.startswith(('http://', 'https://')):
                icon_url = urljoin(base_url, icon_url)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(icon_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            logger.warning(f"Failed to download icon from {icon_url}: {e}")
            return None
    
    def create_fallback_icon(self, app_name, size=512):
        """
        Create a fallback icon when no source icon is available.
        """
        try:
            # Create a colorful gradient background
            img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Create gradient background
            for i in range(size):
                ratio = i / size
                r = int(102 + (118 - 102) * ratio)  # 667eea to 764ba2
                g = int(126 + (75 - 126) * ratio)
                b = int(234 + (162 - 234) * ratio)
                draw.line([(0, i), (size, i)], fill=(r, g, b, 255))
            
            # Draw rounded corners
            mask = Image.new('L', (size, size), 0)
            mask_draw = ImageDraw.Draw(mask)
            corner_radius = size // 8
            mask_draw.rounded_rectangle(
                [(0, 0), (size, size)], 
                radius=corner_radius, 
                fill=255
            )
            
            # Apply mask
            result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            result.paste(img, mask=mask)
            
            # Add app initial or icon
            try:
                # Try to use a system font
                font_size = size // 4
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Get first letter of app name
                initial = app_name[0].upper() if app_name else 'A'
                
                # Calculate text position
                bbox = draw.textbbox((0, 0), initial, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (size - text_width) // 2
                y = (size - text_height) // 2
                
                # Draw text with shadow
                shadow_color = (0, 0, 0, 128)
                text_color = (255, 255, 255, 255)
                
                draw = ImageDraw.Draw(result)
                draw.text((x + 2, y + 2), initial, font=font, fill=shadow_color)
                draw.text((x, y), initial, font=font, fill=text_color)
                
            except Exception as e:
                logger.warning(f"Failed to add text to fallback icon: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create fallback icon: {e}")
            return None
    
    def process_source_icon(self, icon_data, target_size=512):
        """
        Process source icon data and return PIL Image.
        """
        try:
            if not icon_data:
                return None
            
            # Handle SVG icons - create fallback for now, can enhance later
            if icon_data.startswith(b'<svg') or b'<svg' in icon_data[:100]:
                logger.info("SVG icon detected, using fallback icon generation")
                return None  # Will use fallback icon
            else:
                # Handle regular image formats
                img = Image.open(io.BytesIO(icon_data))
            
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Resize to target size while maintaining aspect ratio
            img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
            
            # Create centered image on transparent background
            final_img = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
            
            # Center the image
            x = (target_size - img.width) // 2
            y = (target_size - img.height) // 2
            final_img.paste(img, (x, y), img)
            
            return final_img
            
        except Exception as e:
            logger.error(f"Failed to process source icon: {e}")
            return None
    
    def generate_icon_set(self, source_icon, sizes, app_name, platform):
        """
        Generate a complete icon set for a specific platform.
        """
        icon_files = {}
        
        for size in sizes:
            try:
                if source_icon:
                    # Resize source icon
                    icon = source_icon.copy()
                    icon = icon.resize((size, size), Image.Resampling.LANCZOS)
                else:
                    # Create fallback icon
                    icon = self.create_fallback_icon(app_name, size)
                
                if icon:
                    # Save icon to bytes
                    img_byte_arr = io.BytesIO()
                    icon.save(img_byte_arr, format='PNG', optimize=True)
                    img_byte_arr.seek(0)
                    
                    # Generate filename
                    if platform == 'android':
                        filename = f'icon-{size}x{size}.png'
                    elif platform == 'ios':
                        filename = f'Icon-{size}.png'
                    elif platform == 'windows':
                        filename = f'Square{size}x{size}Logo.png'
                    else:
                        filename = f'icon_{size}.png'
                    
                    icon_files[filename] = img_byte_arr.getvalue()
                    
            except Exception as e:
                logger.error(f"Failed to generate {size}x{size} icon for {platform}: {e}")
        
        return icon_files
    
    def generate_all_icons(self, app_metadata, app_name):
        """
        Generate all required icons for all platforms.
        """
        try:
            # Download source icon
            source_icon_data = None
            if app_metadata.get('icon_url'):
                source_icon_data = self.download_icon(
                    app_metadata['icon_url'], 
                    app_metadata.get('url')
                )
            
            # Process source icon
            source_icon = None
            if source_icon_data:
                source_icon = self.process_source_icon(source_icon_data, 512)
            
            # If no source icon, create fallback
            if not source_icon:
                source_icon = self.create_fallback_icon(app_name, 512)
            
            # Generate icon sets for all platforms
            all_icons = {}
            
            # Android icons
            android_icons = self.generate_icon_set(
                source_icon, self.ANDROID_ICON_SIZES, app_name, 'android'
            )
            all_icons['android'] = android_icons
            
            # iOS icons
            ios_icons = self.generate_icon_set(
                source_icon, self.IOS_ICON_SIZES, app_name, 'ios'
            )
            all_icons['ios'] = ios_icons
            
            # Windows icons
            windows_icons = self.generate_icon_set(
                source_icon, self.WINDOWS_ICON_SIZES, app_name, 'windows'
            )
            all_icons['windows'] = windows_icons
            
            # Generate universal icons (various common sizes)
            universal_sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
            universal_icons = self.generate_icon_set(
                source_icon, universal_sizes, app_name, 'universal'
            )
            all_icons['universal'] = universal_icons
            
            logger.info(f"Generated {sum(len(icons) for icons in all_icons.values())} icons for {app_name}")
            return all_icons
            
        except Exception as e:
            logger.error(f"Failed to generate icons for {app_name}: {e}")
            return {}
    
    def save_icons_to_package(self, icon_data, package_path, platform):
        """
        Save generated icons to the appropriate package directory structure.
        """
        try:
            if platform == 'android':
                # Android resource directory structure
                icon_dirs = {
                    'icon-36x36.png': 'res/drawable-ldpi',
                    'icon-48x48.png': 'res/drawable-mdpi',
                    'icon-72x72.png': 'res/drawable-hdpi',
                    'icon-96x96.png': 'res/drawable-xhdpi',
                    'icon-144x144.png': 'res/drawable-xxhdpi',
                    'icon-192x192.png': 'res/drawable-xxxhdpi',
                }
                
                for filename, icon_bytes in icon_data.items():
                    if filename in icon_dirs:
                        icon_dir = os.path.join(package_path, icon_dirs[filename])
                        os.makedirs(icon_dir, exist_ok=True)
                        icon_path = os.path.join(icon_dir, 'ic_launcher.png')
                    else:
                        # Store additional sizes in assets
                        icon_dir = os.path.join(package_path, 'assets/icons')
                        os.makedirs(icon_dir, exist_ok=True)
                        icon_path = os.path.join(icon_dir, filename)
                    
                    with open(icon_path, 'wb') as f:
                        f.write(icon_bytes)
            
            elif platform == 'ios':
                # iOS bundle structure
                icon_dir = os.path.join(package_path, 'Assets.xcassets/AppIcon.appiconset')
                os.makedirs(icon_dir, exist_ok=True)
                
                for filename, icon_bytes in icon_data.items():
                    icon_path = os.path.join(icon_dir, filename)
                    with open(icon_path, 'wb') as f:
                        f.write(icon_bytes)
            
            elif platform == 'windows':
                # Windows package structure
                icon_dir = os.path.join(package_path, 'Assets')
                os.makedirs(icon_dir, exist_ok=True)
                
                for filename, icon_bytes in icon_data.items():
                    icon_path = os.path.join(icon_dir, filename)
                    with open(icon_path, 'wb') as f:
                        f.write(icon_bytes)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save icons to {platform} package: {e}")
            return False
    
    def cleanup(self):
        """
        Clean up temporary files.
        """
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary files: {e}")