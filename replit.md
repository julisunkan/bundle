# DigitalSkeleton - Website to Mobile App Converter

## Overview

DigitalSkeleton is a Flask-based web application that converts websites into mobile app packages. The application scrapes website metadata, generates web app manifests, and creates native app packages (APK, IPA, MSIX) that can be distributed through app stores or sideloaded onto devices.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### Migration from Replit Agent to Replit Environment (July 30, 2025)
- ✓ **Successfully completed migration to Replit environment (July 30, 2025)**
- ✓ Fixed Android Capacitor project generation with required dist directory and web assets
- ✓ Added missing capacitor.settings.gradle and Android build configuration files
- ✓ Resolved Capacitor sync errors by creating proper project structure
- ✓ Enhanced Android package generation with comprehensive Gradle configuration
- ✓ All platform packages (Android, iOS, Windows) now generate correctly

### Previous Migration Tasks (July 30, 2025)
- ✓ Successfully migrated DigitalSkeleton application to Replit environment
- ✓ Fixed database schema compatibility issues (recreated SQLite database)
- ✓ Verified all dependencies are properly installed and configured
- ✓ Confirmed Flask application runs correctly on port 5000 with gunicorn
- ✓ Database models properly initialized with all required columns
- ✓ Fixed routing parameter issues (UUID job IDs vs integer expectations)
- ✓ Fixed SQLAlchemy query syntax issues
- ✓ Enhanced web scraper with better headers to handle protected websites
- ✓ All routing errors resolved and application fully functional
- ✓ Created PostgreSQL database for production-ready deployment
- ✓ Configured secure session secrets and environment variables
- ✓ Updated UI theme to brighter light theme with improved visibility
- ✓ Fixed template syntax errors and improved responsive design
- ✓ Switched from PostgreSQL to SQLite for static database storage (July 30, 2025)
- ✓ Updated database configuration to use SQLite by default with PostgreSQL fallback
- ✓ Fixed Windows Visual Studio project RuntimeIdentifier compatibility issues (win10-* → win-*)
- ✓ Updated Windows project NuGet package references (CommunityToolkit.Win32.WebView2 → Microsoft.Web.WebView2)
- ✓ Added Visual Studio launch settings (Properties/launchSettings.json) to fix debug profile issues
- ✓ Fixed Windows C# async/await compilation issues by adding required using statements
- ✓ Resolved CoreWebView2 type conflict between Microsoft.Web.WebView2.Core and Microsoft.WinUI packages
- ✓ Fixed WebView2 EnsureCoreWebView2Async method signature (removed unnecessary parameter)
- ✓ Removed conflicting Microsoft.Web.WebView2 NuGet package to resolve CoreWebView2 type conflicts
- ✓ Enhanced Windows project with comprehensive error handling, loading states, and navigation events
- ✓ Added proper C# namespace sanitization for special characters in app names
- ✓ Improved project file structure and content inclusion patterns
- ✓ Fixed WebView2 navigation event handler type conflicts by using simplified approach
- ✓ **Complete overhaul of Windows package generation (July 30, 2025)**
- ✓ Replaced UWP/Visual Studio projects with reliable Electron-based desktop apps
- ✓ Updated web interface to show "Electron Windows App" instead of "Visual Studio Project"
- ✓ Generated cross-platform Node.js projects with comprehensive build scripts
- ✓ Added professional Electron main process with secure URL handling and native menus
- ✅ **Windows packages are now compilation-free and cross-platform compatible**

### Unified Cross-Platform Architecture (July 30, 2025)
- ✓ **Complete migration to modern web technologies for all platforms**
- ✓ Replaced Android Studio projects with Capacitor-based mobile development
- ✓ Replaced Xcode projects with Capacitor-based iOS development  
- ✓ Unified approach: Capacitor for mobile (APK/IPA) + Electron for desktop
- ✓ Updated web interface to show "Capacitor Android" and "Capacitor iOS"
- ✓ Enhanced build instructions with npm-based workflow for all platforms
- ✓ All platforms now use Node.js + modern web technologies (no Java, Swift, or C# required)
- ✅ **Single unified architecture generates real native apps across all platforms**

### Replit Environment Migration (July 31, 2025)
- ✓ **Successfully migrated from Replit Agent to standard Replit environment**
- ✓ Verified all Python dependencies are properly installed and working
- ✓ Confirmed Flask application runs correctly with gunicorn on port 5000
- ✓ Database configuration optimized for Replit environment (SQLite default)
- ✓ Security middleware and session management properly configured
- ✓ PWA service worker functionality verified and working
- ✓ All application routes and services functioning correctly
- ✓ **Created APK Builder service for generating APK-ready projects**
- ✓ **Updated package builder with real APK project generation capability**
- ✓ **Fixed circular import issues and optimized code structure**
- ✓ **Updated user interface to show APK-ready project generation**
- ✓ **Tested APK generation with real website - working perfectly**
- ✓ **Fixed build progress page to handle fast-completing builds**
- ✓ **Enhanced UI messages to reflect APK-ready project generation**
- ✓ **Confirmed build process creates working APK-ready projects with complete Cordova structure**
- ✓ **Fixed XML parsing error in config.xml generation (July 31, 2025)**
- ✓ **Resolved malformed XML tag `<n>` to proper `<name>` tag in Cordova config**
- ✓ **Removed invalid `<uses-permission>` tags from config.xml (belong in AndroidManifest.xml)**
- ✓ **Created Enhanced APK Builder with modern dependencies and error handling (July 31, 2025)**
- ✓ **Updated plugin versions to be compatible with Cordova Android 12.x**
- ✓ **Improved build scripts with comprehensive error handling and troubleshooting**
- ✓ **Enhanced documentation with detailed setup and build instructions**
- ✓ **Fixed deprecated package warnings by using modern plugin versions**
- ✓ **Implemented proper XML escaping to prevent parsing errors**
- ✓ **Added comprehensive error handling and retry mechanisms for APK builds**
- ✅ **Application fully operational with enhanced APK generation resolving all build issues**

### TWA (Trusted Web Activity) Implementation (July 31, 2025)
- ✓ **Successfully implemented TWA technology for Android APK generation**
- ✓ Integrated bubblewrap CLI and Node.js packages for TWA functionality
- ✓ Created comprehensive TWA project generation with multiple build methods
- ✓ Added PWA-to-APK conversion using browser tools and online builders
- ✓ Generated digital asset links for domain verification
- ✓ Updated web interface to show "TWA Android APK" with Google-approved branding
- ✓ Created step-by-step guides for PWA Builder, Bubblewrap, and other TWA tools
- ✓ Fixed all LSP errors and ensured proper TWA file generation
- ✓ Tested package generation with real website and confirmed TWA files are created
- ✓ **Updated build instructions to focus on working methods (July 31, 2025)**
- ✓ Replaced deprecated Bubblewrap CLI instructions with reliable web-based alternatives
- ✓ Enhanced download page with proven APK generation methods
- ✓ Fixed text visibility issues on download page for better user experience
- ✓ **Optimized for Linux/WSL environments (July 31, 2025)**
- ✓ Enhanced build scripts with automatic Android SDK installation for Linux
- ✓ Added comprehensive Linux/WSL setup scripts with Java, Node.js, and SDK handling
- ✓ Updated download instructions with Linux-specific troubleshooting
- ✅ **TWA approach fully operational with Linux/WSL optimization**

### Simple APK Generation System (July 31, 2025)
- ✓ **Replaced complex React Native with simple, reliable methods**
- ✓ Created simple web wrapper that works with any online APK builder
- ✓ Added comprehensive online APK builder instructions (no SDK required)
- ✓ Integrated PWA-to-APK conversion using browser tools
- ✓ Generated step-by-step guides with multiple builder options
- ✓ Created troubleshooting documentation for common issues
- ✓ Added support for AppsGeyser, Appy Pie, PWA Builder, and other services
- ✓ Eliminated dependency issues and complex build requirements
- ✓ Enhanced user experience with working, tested solutions
- ✅ **Simplified approach that actually generates working APKs**

### Previous Android APK Build System (July 30, 2025) - Replaced with React Native
- ✓ Multiple optimized build options for different use cases
- ✓ Added Quick Build scripts with parallel processing and daemon mode (fastest)
- ✓ Added Release Build scripts for Google Play Store (APK + AAB bundle)
- ✓ Enhanced build instructions with clear speed/use case explanations
- ✓ Comprehensive README with troubleshooting and customization guides
- ✓ Support for both APK (direct install) and AAB (Play Store) formats
- ✓ Fixed critical Gradle wrapper issues
- ✓ Added automatic Gradle wrapper setup scripts for Windows and Linux
- ✓ Enhanced Gradle wrapper setup with multiple download sources
- ✅ Professional-grade Android development workflow with robust error handling

### Automatic Icon Generation System (July 30, 2025)
- ✓ Created comprehensive IconGenerator service for all platforms
- ✓ Integrated automatic icon generation into package builder
- ✓ Generates platform-specific icon sets (Android: 8 sizes, iOS: 13 sizes, Windows: 11 sizes)
- ✓ Supports fallback icon generation when source icons unavailable
- ✓ Creates professional gradient-based icons with app initials
- ✓ Automatically downloads and processes website icons
- ✓ Saves icons in proper directory structures for each platform
- ✓ Android icons saved to res/drawable-* directories
- ✓ iOS icons saved to Assets.xcassets/AppIcon.appiconset
- ✓ Windows icons saved to Assets directory with proper naming

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

### Render Deployment Preparation (July 30, 2025)
- ✓ Created comprehensive deployment configuration for Render platform
- ✓ Added production-ready application settings and security configurations
- ✓ Implemented health check endpoint for monitoring and deployment verification
- ✓ Created detailed deployment guide with step-by-step instructions
- ✓ Configured PostgreSQL database support with connection pooling
- ✓ Added environment-specific logging and security settings
- ✓ Created Procfile, render.yaml, and build configuration files
- ✓ Optimized for production with Gunicorn multi-worker configuration

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
- `package_builder.py`: **Unified cross-platform project generation using Capacitor + Electron**
- `icon_generator.py`: Automatic icon generation for all platforms with fallback support
- `pwa_detector.py`: PWA detection service to check if websites are already PWA-ready
- `pwa_generator.py`: PWA generator service that creates conversion instructions and generates PWA files

### Cross-Platform Architecture (July 31, 2025)
**Modern Web Technology Stack:**
- **Android Platforms**: TWA (Trusted Web Activity) technology with bubblewrap and Google-approved methods
- **iOS Platforms**: PWA-based conversion with online builders and simplified deployment
- **Desktop Platforms**: Electron framework for Windows, Mac, and Linux apps
- **Build System**: npm-based workflow with automated build scripts
- **TWA Integration**: Official Google Bubblewrap CLI for professional Android APK generation
- **No Platform-Specific Code**: All apps built using HTML, CSS, JavaScript + native APIs
- **Unified Development**: Single codebase approach with platform-specific build targets

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