# DigitalSkeleton - Website to Mobile App Converter

## Overview

DigitalSkeleton is a Flask-based web application that converts websites into mobile app packages. The application scrapes website metadata, generates web app manifests, and creates native app packages (APK, IPA, MSIX) that can be distributed through app stores or sideloaded onto devices.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### Migration from Replit Agent to Replit Environment (July 30, 2025)
- ✓ Successfully migrated DigitalSkeleton application to Replit environment
- ✓ Fixed database schema compatibility issues (recreated SQLite database)
- ✓ Verified all dependencies are properly installed and configured
- ✓ Confirmed Flask application runs correctly on port 5000 with gunicorn
- ✓ Database models properly initialized with all required columns
- ✓ Fixed routing parameter issues (UUID job IDs vs integer expectations)
- ✓ Fixed SQLAlchemy query syntax issues
- ✓ Enhanced web scraper with better headers to handle protected websites
- ✓ All routing errors resolved and application fully functional

### PWA Results Page Improvements (July 30, 2025)
- ✓ Fixed PWA generation redirect issues (session cookie overflow to database storage)
- ✓ Resolved text visibility issues with consistent dark theme styling
- ✓ Redesigned PWA file cards with proper dark backgrounds and visible text
- ✓ Removed non-functional "View Content" buttons for cleaner interface
- ✓ Enhanced download functionality with clear labeling and tooltips
- ✓ Streamlined user experience with working features only

### Package Builder Architecture Change (July 30, 2025)
- ✓ Changed from binary package generation to development project files
- ✓ Android APK → Android Studio project ZIP files
- ✓ iOS IPA → Xcode project ZIP files  
- ✓ Windows MSIX/APPX → Visual Studio project ZIP files
- ✓ Updated download filenames to use .zip extensions with descriptive names
- ✓ Replaced installation instructions with IDE import instructions
- ✓ Enhanced user experience for developers who want to customize and build apps

### PWA Implementation (July 30, 2025)
- ✓ Converted the DigitalSkeleton web app itself into a Progressive Web App
- ✓ Added web app manifest with proper metadata and icons
- ✓ Implemented service worker with caching, offline support, and background sync
- ✓ Created PWA installation functionality with install prompts
- ✓ Added offline detection and user feedback
- ✓ Implemented PWA-specific CSS for standalone app experience
- ✓ Added safe area support for mobile devices
- ✓ Created PWA routes for manifest and service worker serving
- ✓ Enhanced user experience with notification support and update detection

### Professional UI Enhancement (July 30, 2025)
- ✓ Redesigned with modern gradient backgrounds and glass morphism effects
- ✓ Implemented professional color palette with CSS custom properties
- ✓ Enhanced hero section with statistics and better visual hierarchy
- ✓ Redesigned platform selection cards with gradient backgrounds and animations
- ✓ Improved navigation with brand icon and professional styling
- ✓ Enhanced buttons with hover effects and shimmer animations
- ✓ Redesigned features section with modern card layouts and icons
- ✓ Added professional footer with comprehensive information architecture
- ✓ Created complete footer pages (Documentation, API Reference, Privacy, Terms, Support)
- ✓ Added proper routing and navigation for all footer pages
- ✓ Implemented comprehensive help and support system
- ✓ Implemented responsive design improvements for mobile devices
- ✓ Added professional loading states and micro-interactions

### Theme Switcher Implementation (July 30, 2025)
- ✓ Implemented dynamic theme switching between dark, light, and grey modes
- ✓ Added professional theme switcher component in navigation bar
- ✓ Created CSS custom properties system for theme variables
- ✓ Built JavaScript theme management with localStorage persistence
- ✓ Added smooth transitions between theme changes
- ✓ Implemented responsive theme-aware styling for all components

### Application Rebranding (July 30, 2025)
- ✓ Changed application name from "PWA Builder" to "DigitalSkeleton"
- ✓ Updated all templates, documentation, and legal pages with new branding
- ✓ Modified PWA manifest and configuration files
- ✓ Updated footer pages and support documentation
- ✓ Changed all email addresses and contact information to reflect new brand

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework) with SQLAlchemy ORM
- **Database**: SQLite for development (configurable to other databases via DATABASE_URL)
- **Web Server**: WSGI-compatible with ProxyFix middleware for deployment behind reverse proxies
- **File Storage**: Local filesystem for generated app packages

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5 with dark theme
- **JavaScript**: Vanilla JavaScript with Bootstrap components
- **Icons**: Font Awesome for UI icons and brand icons

### Service Layer
The application uses a service-oriented architecture with specialized services:
- `web_scraper.py`: Website metadata extraction with comprehensive content analysis
- `manifest_generator.py`: PWA manifest generation with platform-specific configurations
- `package_builder.py`: Real native app package creation for all supported platforms
- `pwa_detector.py`: PWA detection service to check if websites are already PWA-ready
- `pwa_generator.py`: PWA generator service that creates conversion instructions and generates PWA files

## Key Components

### Models (`models.py`)
- **BuildJob**: Tracks app package building requests with status, metadata, and file paths
- **AppMetadata**: Caches scraped website information to avoid repeated requests

### Routes (`routes.py`)
- **Index Route** (`/`): Main form for URL input and package type selection
- **Build Route** (`/build`): Handles package creation requests
- **Progress/Download Routes**: Track build status and serve completed packages

### Services
- **Web Scraper**: Uses BeautifulSoup and requests to extract website metadata (title, description, icons, theme colors)
- **Manifest Generator**: Creates PWA-compliant web app manifests from scraped data
- **Package Builder**: Generates real platform-specific app packages (APK, IPA, MSIX, APPX) with complete mobile app structures

### Configuration
- Environment-based configuration for database, secrets, and file storage
- Upload folder management with size limits (16MB)
- Development vs production settings

## Data Flow

### PWA Analysis Flow
1. **PWA Detection**: User requests PWA analysis of a website
2. **Comprehensive Analysis**: System analyzes PWA readiness (manifest, service worker, HTTPS, icons, etc.)
3. **PWA Score Calculation**: Generates readiness score and detailed recommendations
4. **PWA File Generation**: If not PWA-ready, generates all necessary PWA files with setup instructions

### App Package Building Flow
1. **User Input**: User submits website URL and selects package type
2. **URL Validation**: System validates URL format and accessibility
3. **Metadata Extraction**: Web scraper extracts website information (cached for efficiency)
4. **PWA Check**: System determines if website is PWA-ready or needs WebView approach
5. **Package Strategy**: Uses PWA approach for ready sites, WebView with offline support for others
6. **Package Building**: Service creates platform-specific app package
7. **Status Tracking**: Build job status is tracked in database
8. **Download Delivery**: Completed packages are served to users

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **BeautifulSoup4**: HTML parsing for metadata extraction
- **Requests**: HTTP client for website scraping
- **Trafilatura**: Advanced content extraction (imported but not fully implemented)

### Frontend Dependencies (CDN)
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library
- **Bootstrap JavaScript**: Interactive components

### Build Tools (Implied)
- Android SDK tools for APK generation (simplified implementation in current version)
- iOS development tools for IPA packages (planned)
- Windows SDK for MSIX packages (planned)

## Deployment Strategy

### Development Setup
- SQLite database for local development
- Flask development server with debug mode
- Local file storage for generated packages

### Production Considerations
- Environment variable configuration for sensitive data
- Database URL configuration for production databases (PostgreSQL recommended)
- ProxyFix middleware for deployment behind reverse proxies
- File upload size limits and storage management
- Session security with configurable secret keys

### Scaling Notes
- Package building is currently synchronous but designed for async conversion
- File storage could be moved to cloud storage (S3, GCS) for distributed deployments
- Database caching strategy implemented for metadata to reduce external requests
- Build job tracking enables queue-based processing for high-volume scenarios

The application is structured for easy extension to support additional package types and enhanced build pipelines while maintaining a simple, user-friendly interface for converting websites to mobile apps.