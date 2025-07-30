import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

class PWADetector:
    def __init__(self, url):
        self.url = url
        self.base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
    def analyze_pwa_readiness(self):
        """Analyze if a website is PWA-ready and return detailed assessment"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            assessment = {
                'is_pwa_ready': False,
                'pwa_score': 0,
                'checks': {
                    'manifest': self._check_manifest(soup),
                    'service_worker': self._check_service_worker(soup),
                    'https': self._check_https(),
                    'responsive': self._check_responsive_design(soup),
                    'app_icons': self._check_app_icons(soup),
                    'theme_color': self._check_theme_color(soup),
                    'display_mode': self._check_display_mode(soup),
                    'start_url': self._check_start_url(soup)
                },
                'missing_files': [],
                'recommendations': []
            }
            
            # Calculate PWA score
            total_checks = len(assessment['checks'])
            passed_checks = sum(1 for check in assessment['checks'].values() if check['passed'])
            assessment['pwa_score'] = int((passed_checks / total_checks) * 100)
            assessment['is_pwa_ready'] = assessment['pwa_score'] >= 80
            
            # Generate recommendations
            assessment['recommendations'] = self._generate_recommendations(assessment['checks'])
            assessment['missing_files'] = self._generate_missing_files(assessment['checks'])
            
            return assessment
            
        except Exception as e:
            return {
                'is_pwa_ready': False,
                'pwa_score': 0,
                'error': str(e),
                'checks': {},
                'missing_files': [],
                'recommendations': []
            }
    
    def _check_manifest(self, soup):
        """Check for web app manifest"""
        manifest_link = soup.find('link', rel='manifest')
        if manifest_link and manifest_link.get('href'):
            manifest_url = urljoin(self.url, manifest_link['href'])
            try:
                manifest_response = requests.get(manifest_url, timeout=5)
                if manifest_response.status_code == 200:
                    manifest_data = manifest_response.json()
                    required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
                    has_required = all(field in manifest_data for field in required_fields)
                    
                    return {
                        'passed': has_required,
                        'details': f"Manifest found at {manifest_url}",
                        'data': manifest_data if has_required else None
                    }
            except:
                pass
        
        return {
            'passed': False,
            'details': "No valid web app manifest found",
            'data': None
        }
    
    def _check_service_worker(self, soup):
        """Check for service worker registration"""
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'serviceWorker' in script.string:
                return {
                    'passed': True,
                    'details': "Service worker registration found in page scripts"
                }
        
        # Check for common service worker files
        common_sw_paths = ['/sw.js', '/service-worker.js', '/serviceworker.js']
        for path in common_sw_paths:
            try:
                sw_url = urljoin(self.base_url, path)
                sw_response = requests.head(sw_url, timeout=3)
                if sw_response.status_code == 200:
                    return {
                        'passed': True,
                        'details': f"Service worker found at {sw_url}"
                    }
            except:
                continue
        
        return {
            'passed': False,
            'details': "No service worker registration or file found"
        }
    
    def _check_https(self):
        """Check if site uses HTTPS"""
        is_https = self.url.startswith('https://')
        return {
            'passed': is_https,
            'details': "HTTPS required for PWA" if not is_https else "Site uses HTTPS"
        }
    
    def _check_responsive_design(self, soup):
        """Check for responsive design indicators"""
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        if viewport_meta and viewport_meta.get('content'):
            content = viewport_meta['content'].lower()
            if 'width=device-width' in content:
                return {
                    'passed': True,
                    'details': "Responsive viewport meta tag found"
                }
        
        return {
            'passed': False,
            'details': "No responsive viewport meta tag found"
        }
    
    def _check_app_icons(self, soup):
        """Check for app icons"""
        icon_links = soup.find_all('link', rel=['icon', 'apple-touch-icon', 'apple-touch-icon-precomposed'])
        if icon_links:
            icons = []
            for link in icon_links:
                if link.get('href'):
                    icons.append({
                        'href': urljoin(self.url, link['href']),
                        'sizes': link.get('sizes', 'unknown'),
                        'type': link.get('type', 'unknown')
                    })
            
            return {
                'passed': len(icons) > 0,
                'details': f"Found {len(icons)} app icon(s)",
                'icons': icons
            }
        
        return {
            'passed': False,
            'details': "No app icons found"
        }
    
    def _check_theme_color(self, soup):
        """Check for theme color"""
        theme_meta = soup.find('meta', attrs={'name': 'theme-color'})
        if theme_meta and theme_meta.get('content'):
            return {
                'passed': True,
                'details': f"Theme color found: {theme_meta['content']}"
            }
        
        return {
            'passed': False,
            'details': "No theme color meta tag found"
        }
    
    def _check_display_mode(self, soup):
        """Check for display mode indicators"""
        # This is typically defined in manifest, but check for meta tags too
        display_meta = soup.find('meta', attrs={'name': 'mobile-web-app-capable'})
        if display_meta:
            return {
                'passed': True,
                'details': "Mobile web app capable meta tag found"
            }
        
        return {
            'passed': False,
            'details': "No display mode indicators found (should be in manifest)"
        }
    
    def _check_start_url(self, soup):
        """Check for start URL (usually in manifest)"""
        # This is a placeholder - start_url is typically in manifest
        return {
            'passed': True,
            'details': "Start URL should be defined in manifest"
        }
    
    def _generate_recommendations(self, checks):
        """Generate recommendations based on failed checks"""
        recommendations = []
        
        if not checks['manifest']['passed']:
            recommendations.append({
                'priority': 'high',
                'title': 'Add Web App Manifest',
                'description': 'Create a manifest.json file with app metadata',
                'action': 'Create manifest.json with name, icons, start_url, and display mode'
            })
        
        if not checks['service_worker']['passed']:
            recommendations.append({
                'priority': 'high',
                'title': 'Implement Service Worker',
                'description': 'Add service worker for offline functionality',
                'action': 'Create service worker to cache resources and enable offline access'
            })
        
        if not checks['https']['passed']:
            recommendations.append({
                'priority': 'critical',
                'title': 'Enable HTTPS',
                'description': 'PWAs require secure HTTPS connection',
                'action': 'Configure SSL certificate and redirect HTTP to HTTPS'
            })
        
        if not checks['responsive']['passed']:
            recommendations.append({
                'priority': 'medium',
                'title': 'Add Responsive Design',
                'description': 'Ensure site works on mobile devices',
                'action': 'Add viewport meta tag and responsive CSS'
            })
        
        if not checks['app_icons']['passed']:
            recommendations.append({
                'priority': 'medium',
                'title': 'Add App Icons',
                'description': 'Create icons for different screen sizes',
                'action': 'Add multiple icon sizes (192x192, 512x512) and link in HTML'
            })
        
        if not checks['theme_color']['passed']:
            recommendations.append({
                'priority': 'low',
                'title': 'Add Theme Color',
                'description': 'Define app theme color for better integration',
                'action': 'Add theme-color meta tag and include in manifest'
            })
        
        return recommendations
    
    def _generate_missing_files(self, checks):
        """Generate list of files needed to make site PWA-ready"""
        missing_files = []
        
        if not checks['manifest']['passed']:
            missing_files.append({
                'filename': 'manifest.json',
                'description': 'Web app manifest file',
                'required': True
            })
        
        if not checks['service_worker']['passed']:
            missing_files.append({
                'filename': 'sw.js',
                'description': 'Service worker file',
                'required': True
            })
        
        if not checks['app_icons']['passed']:
            missing_files.extend([
                {
                    'filename': 'icon-192x192.png',
                    'description': 'App icon 192x192 pixels',
                    'required': True
                },
                {
                    'filename': 'icon-512x512.png',
                    'description': 'App icon 512x512 pixels',
                    'required': True
                }
            ])
        
        return missing_files

def analyze_website_pwa_status(url):
    """Analyze a website's PWA readiness"""
    detector = PWADetector(url)
    return detector.analyze_pwa_readiness()