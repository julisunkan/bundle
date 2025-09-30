# DigitalSkeleton - Website to Mobile App Converter

## Overview
DigitalSkeleton is a Flask-based web application that converts websites into mobile app packages. It scrapes website metadata, generates web app manifests, and creates native app packages (APK, IPA, MSIX) for distribution through app stores or sideloading. The project aims to unify mobile and desktop app generation using modern web technologies, offering a streamlined process for converting any website into a functional application.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
The application features a professional UI with modern gradient backgrounds, glass morphism effects, and a responsive design. It includes a dynamic theme switcher (dark, light, grey modes) and professional loading states. The overall design prioritizes a clean, user-friendly interface.

### Technical Implementations
- **Backend**: Flask (Python) with SQLAlchemy ORM. Uses PostgreSQL database (configured via DATABASE_URL environment variable) with SQLite fallback for development.
- **Frontend**: Jinja2 templating, Bootstrap 5 (dark theme), Vanilla JavaScript, and Font Awesome.
- **Cross-Platform Architecture**:
    - **Mobile (Android/iOS)**: Utilizes Capacitor-based development and TWA (Trusted Web Activity) technology for Android. iOS conversion is PWA-based with online builders.
    - **Desktop (Windows/Mac/Linux)**: Electron framework for cross-platform desktop applications.
    - **Unified Approach**: All platforms leverage Node.js and modern web technologies (HTML, CSS, JavaScript) for a single codebase approach.
- **Core Services**:
    - `web_scraper.py`: Extracts website metadata.
    - `manifest_generator.py`: Generates PWA manifests.
    - `package_builder.py`: Generates unified cross-platform projects (Capacitor for mobile, Electron for desktop).
    - `icon_generator.py`: Automatic icon generation for all platforms.
    - `pwa_detector.py`: Checks PWA readiness of websites.
    - `pwa_generator.py`: Creates PWA files and conversion instructions.
- **PWA Implementation**: DigitalSkeleton itself is a Progressive Web App, featuring a web app manifest, service worker for caching and offline support, and PWA installation prompts.

### Feature Specifications
- **App Package Generation**: Converts websites into development project files (ZIP) for Android (Capacitor/TWA), iOS (Capacitor/PWA), and Windows (Electron).
- **Automatic Icon Generation**: Generates platform-specific icon sets and professional gradient-based icons.
- **PWA Analysis**: Analyzes website PWA readiness, provides scores, recommendations, and can generate necessary PWA files.
- **Offline Support**: Implements offline pages and service workers for generated applications to ensure functionality without an internet connection.
- **Simplified APK Generation**: Provides methods for generating working APKs using online builders and TWA technology, reducing dependency complexities.

### System Design Choices
- **Service-Oriented Architecture**: Modular design with specialized Python services.
- **Data Flow**: Clearly defined processes for PWA analysis and app package building, from URL validation to package delivery.
- **Configuration**: Environment-based configuration for database, secrets, and file storage.
- **Scalability**: Designed for asynchronous processing and cloud storage integration for generated packages.

## External Dependencies

### Python Packages
- **Flask**: Web framework.
- **SQLAlchemy**: Database ORM.
- **BeautifulSoup4**: HTML parsing.
- **Requests**: HTTP client.
- **Trafilatura**: Advanced content extraction (partially implemented).

### Frontend Dependencies (CDN)
- **Bootstrap 5**: UI framework.
- **Font Awesome**: Icon library.
- **Bootstrap JavaScript**: Interactive components.

### Build Tools (Integrated/Implied)
- **Capacitor**: For Android and iOS mobile app generation.
- **Electron**: For Windows, Mac, and Linux desktop app generation.
- **Node.js/npm**: Core for cross-platform build workflows.
- **Bubblewrap CLI**: For TWA (Trusted Web Activity) Android APK generation.