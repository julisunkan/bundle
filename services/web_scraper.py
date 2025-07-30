import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import trafilatura

def scrape_website_metadata(url):
    """
    Scrape website metadata for app generation
    """
    try:
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = None
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Try Open Graph title
        if not title:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title = str(og_title.get('content', '')).strip()
        
        # Fallback to domain name
        if not title:
            parsed_url = urlparse(url)
            title = parsed_url.netloc.replace('www.', '').title()
        
        # Extract description
        description = None
        
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = str(meta_desc.get('content', '')).strip()
        
        # Try Open Graph description
        if not description:
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                description = str(og_desc.get('content', '')).strip()
        
        # Extract using trafilatura as fallback
        if not description:
            try:
                downloaded = trafilatura.fetch_url(url)
                text_content = trafilatura.extract(downloaded)
                if text_content:
                    # Take first 200 characters as description
                    description = text_content[:200].strip() + '...' if len(text_content) > 200 else text_content.strip()
            except:
                pass
        
        # Extract icon
        icon_url = None
        
        # Try to find favicon or apple-touch-icon
        icon_selectors = [
            'link[rel="apple-touch-icon"]',
            'link[rel="icon"]',
            'link[rel="shortcut icon"]',
            'link[rel="apple-touch-icon-precomposed"]'
        ]
        
        for selector in icon_selectors:
            icon_link = soup.select_one(selector)
            if icon_link and icon_link.get('href'):
                icon_url = urljoin(url, str(icon_link['href']))
                break
        
        # Fallback to /favicon.ico
        if not icon_url:
            parsed_url = urlparse(url)
            icon_url = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
        
        # Extract theme colors
        theme_color = '#000000'
        background_color = '#ffffff'
        
        # Try to get theme color from meta tags
        theme_meta = soup.find('meta', attrs={'name': 'theme-color'})
        if theme_meta and theme_meta.get('content'):
            theme_color = str(theme_meta.get('content', '#000000'))
        
        # Try to get background color from CSS or other sources
        # This is a simplified approach - in a real implementation, 
        # you might want to analyze the CSS more thoroughly
        
        return {
            'title': title or 'Web App',
            'description': description or 'Converted web application',
            'icon_url': icon_url,
            'theme_color': theme_color,
            'background_color': background_color,
            'url': url
        }
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch website: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to parse website metadata: {str(e)}")

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        return text if text else ""
    except Exception as e:
        raise Exception(f"Failed to extract text content: {str(e)}")
