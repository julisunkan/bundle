import os
import logging
import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set logging level based on environment
if os.environ.get('RENDER'):
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database - use SQLite only
database_url = "sqlite:///digitalskeleton.db"

# SQLite settings (no pooling needed)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# Configure upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'generated_packages')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Security settings for production
if os.environ.get('RENDER'):
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# initialize the app with the extension
db.init_app(app)

# Add custom Jinja2 filters
@app.template_filter('fromjson')
def fromjson_filter(value):
    """Convert JSON string to Python object"""
    try:
        return json.loads(value) if value else []
    except (json.JSONDecodeError, TypeError):
        return []

with app.app_context():
    # Import models and routes
    import models
    import routes

    try:
        # Only create tables if they don't exist, preserving existing data
        db.create_all()
        app.logger.info("Database tables initialized (existing data preserved)")
        
        # Initialize default settings only if they don't exist
        from models import AdminSettings, AdminUser, Tutorial
        
        # Check and create default admin settings if missing
        if not AdminSettings.query.first():
            default_settings = AdminSettings(
                google_adsense_code='',
                payment_account_name='Digital Skeleton',
                payment_bank_name='Default Bank',
                payment_account_number='1234567890',
                admin_email='admin@digitalskeleton.com',
                banner_price_per_day=10.0
            )
            db.session.add(default_settings)
            app.logger.info("Created default admin settings")
        
        # Check and create default admin user if missing
        if not AdminUser.query.first():
            default_admin = AdminUser(
                username='admin',
                email='admin@digitalskeleton.com'
            )
            default_admin.set_password('admin123')
            db.session.add(default_admin)
            app.logger.info("Created default admin user")
        
        # Check and create sample tutorials if none exist
        if Tutorial.query.count() == 0:
            tutorials = [
                Tutorial(
                    title="Welcome to DigitalSkeleton",
                    description="Learn the basics of converting websites to mobile apps",
                    content="""
                    <h3>Welcome to the DigitalSkeleton Tutorial Series!</h3>
                    <p>This tutorial will guide you through the process of converting websites into mobile applications using our platform.</p>
                    <h4>What You'll Learn:</h4>
                    <ul>
                        <li>How to analyze websites for PWA readiness</li>
                        <li>Understanding mobile app conversion process</li>
                        <li>Best practices for mobile app development</li>
                        <li>Tips for successful app deployment</li>
                    </ul>
                    <h4>Getting Started</h4>
                    <p>To convert a website to a mobile app:</p>
                    <ol>
                        <li>Enter the website URL in our converter</li>
                        <li>Choose your target platform (Android, iOS, Windows)</li>
                        <li>Click "Build Package" to generate your app files</li>
                        <li>Download and follow the setup instructions</li>
                    </ol>
                    <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                        <strong>Pro Tip:</strong> Make sure your website is mobile-friendly and has proper meta tags for the best conversion results.
                    </div>
                    <p>Ready to start building? Visit our <a href="/">home page</a> to begin converting your first website!</p>
                    """,
                    order_position=1,
                    is_active=True
                ),
                Tutorial(
                    title="Building Your First Android APK",
                    description="Step-by-step guide to creating Android apps from websites",
                    content="""
                    <h3>Building Your First Android APK</h3>
                    <p>Learn how to convert any website into a professional Android application package (APK).</p>
                    
                    <h4>Prerequisites</h4>
                    <ul>
                        <li>A responsive website URL</li>
                        <li>Basic understanding of mobile apps</li>
                        <li>Android Studio (for testing - optional)</li>
                    </ul>
                    
                    <h4>Step 1: Enter Your Website URL</h4>
                    <p>Navigate to the DigitalSkeleton homepage and enter your website URL in the conversion tool. Make sure the URL is complete with http:// or https://</p>
                    
                    <h4>Step 2: Configure APK Settings</h4>
                    <p>Our platform will automatically detect:</p>
                    <ul>
                        <li>App name and description</li>
                        <li>Icons and theme colors</li>
                        <li>PWA manifest data</li>
                    </ul>
                    
                    <h4>Step 3: Generate and Download</h4>
                    <p>Click "Build APK Package" and wait for the build process to complete. You'll receive a ZIP file containing:</p>
                    <ul>
                        <li>Configuration files (config.xml)</li>
                        <li>Build instructions</li>
                        <li>App resources and assets</li>
                    </ul>
                    
                    <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <strong>Important:</strong> You'll need Android Studio and Cordova CLI to compile the final APK from the generated files.
                    </div>
                    
                    <h4>Testing Your APK</h4>
                    <p>After building, test your APK on different Android devices to ensure compatibility and performance.</p>
                    """,
                    order_position=2,
                    is_active=True
                ),
                Tutorial(
                    title="Creating iOS Apps with DigitalSkeleton",
                    description="Convert websites to iOS applications",
                    content="""
                    <h3>Creating iOS Apps with DigitalSkeleton</h3>
                    <p>Transform your website into a native iOS application for iPhone and iPad.</p>
                    
                    <h4>What You Need</h4>
                    <ul>
                        <li>A Mac computer with Xcode installed</li>
                        <li>Apple Developer account (for App Store distribution)</li>
                        <li>Your website URL</li>
                    </ul>
                    
                    <h4>The Conversion Process</h4>
                    <p>DigitalSkeleton generates an iOS development package that includes:</p>
                    <ol>
                        <li><strong>App Configuration:</strong> Info.plist with all necessary metadata</li>
                        <li><strong>Assets:</strong> App icons in all required sizes</li>
                        <li><strong>Build Scripts:</strong> Ready-to-use build configuration</li>
                        <li><strong>WebView Setup:</strong> Optimized web view for your content</li>
                    </ol>
                    
                    <h4>Building in Xcode</h4>
                    <p>Follow these steps after downloading your package:</p>
                    <ol>
                        <li>Extract the downloaded ZIP file</li>
                        <li>Open the project in Xcode</li>
                        <li>Configure your bundle identifier</li>
                        <li>Add your provisioning profile</li>
                        <li>Build and test on iOS Simulator</li>
                    </ol>
                    
                    <div style="background: #d1ecf1; padding: 15px; border-left: 4px solid #0dcaf0; margin: 20px 0;">
                        <strong>Note:</strong> iOS app development requires a Mac computer and Apple Developer membership for distribution.
                    </div>
                    
                    <h4>App Store Submission</h4>
                    <p>Once tested, you can submit your app to the App Store following Apple's guidelines.</p>
                    """,
                    order_position=3,
                    is_active=True
                ),
                Tutorial(
                    title="Understanding PWA Analysis",
                    description="Learn how Progressive Web App detection works",
                    content="""
                    <h3>Understanding PWA Analysis</h3>
                    <p>Discover how DigitalSkeleton analyzes websites for Progressive Web App readiness.</p>
                    
                    <h4>What is PWA Analysis?</h4>
                    <p>PWA (Progressive Web App) analysis checks if your website has the necessary components to function as a native-like app:</p>
                    <ul>
                        <li>Web App Manifest</li>
                        <li>Service Worker</li>
                        <li>HTTPS security</li>
                        <li>Responsive design</li>
                    </ul>
                    
                    <h4>Key PWA Components</h4>
                    
                    <h5>1. Web App Manifest</h5>
                    <p>A JSON file that describes your app including name, icons, theme colors, and display mode.</p>
                    
                    <h5>2. Service Worker</h5>
                    <p>A script that enables offline functionality and push notifications.</p>
                    
                    <h5>3. Icons and Assets</h5>
                    <p>Multiple icon sizes for different devices and platforms.</p>
                    
                    <h4>How DigitalSkeleton Helps</h4>
                    <p>Our platform automatically:</p>
                    <ul>
                        <li>Detects existing PWA components</li>
                        <li>Extracts metadata from your website</li>
                        <li>Generates missing components</li>
                        <li>Optimizes for mobile platforms</li>
                    </ul>
                    
                    <div style="background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                        <strong>Best Practice:</strong> Websites that already have PWA features convert faster and produce better quality apps.
                    </div>
                    
                    <h4>Improving Your Website</h4>
                    <p>To get the best results, ensure your website has proper meta tags, icons, and mobile-responsive design before conversion.</p>
                    """,
                    order_position=4,
                    is_active=True
                ),
                Tutorial(
                    title="Windows App Development",
                    description="Create Windows applications from websites",
                    content="""
                    <h3>Windows App Development</h3>
                    <p>Learn to convert your website into a Windows application package.</p>
                    
                    <h4>Windows App Formats</h4>
                    <p>DigitalSkeleton supports multiple Windows app formats:</p>
                    <ul>
                        <li><strong>MSIX:</strong> Modern Windows 10/11 app format</li>
                        <li><strong>UWP:</strong> Universal Windows Platform apps</li>
                        <li><strong>Desktop Bridge:</strong> Traditional desktop apps</li>
                    </ul>
                    
                    <h4>System Requirements</h4>
                    <ul>
                        <li>Windows 10 or later</li>
                        <li>Visual Studio 2019 or later</li>
                        <li>Windows SDK</li>
                    </ul>
                    
                    <h4>Creating Your Windows Package</h4>
                    <ol>
                        <li>Enter your website URL</li>
                        <li>Select "Windows" as target platform</li>
                        <li>Choose your preferred format (MSIX recommended)</li>
                        <li>Download the generated package</li>
                    </ol>
                    
                    <h4>Package Contents</h4>
                    <p>Your download includes:</p>
                    <ul>
                        <li>App manifest files</li>
                        <li>Visual assets and logos</li>
                        <li>Build configuration</li>
                        <li>Detailed setup guide</li>
                    </ul>
                    
                    <h4>Building in Visual Studio</h4>
                    <p>Open the project in Visual Studio and follow the build instructions provided in the package.</p>
                    
                    <div style="background: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
                        <strong>Windows Store:</strong> Publishing to Microsoft Store requires a developer account and app certification.
                    </div>
                    
                    <h4>Testing Your App</h4>
                    <p>Test on different Windows versions to ensure compatibility across the ecosystem.</p>
                    """,
                    order_position=5,
                    is_active=True
                ),
                Tutorial(
                    title="Advanced App Customization",
                    description="Customize and optimize your mobile applications",
                    content="""
                    <h3>Advanced App Customization</h3>
                    <p>Take your mobile apps to the next level with advanced customization options.</p>
                    
                    <h4>Customizable Elements</h4>
                    
                    <h5>1. App Icons and Splash Screens</h5>
                    <p>Customize visual elements to match your brand:</p>
                    <ul>
                        <li>App launcher icons</li>
                        <li>Splash screen graphics</li>
                        <li>Theme colors</li>
                        <li>Status bar styling</li>
                    </ul>
                    
                    <h5>2. App Behavior</h5>
                    <p>Configure how your app behaves:</p>
                    <ul>
                        <li>Orientation (portrait/landscape)</li>
                        <li>Fullscreen vs standard mode</li>
                        <li>Navigation patterns</li>
                        <li>Offline functionality</li>
                    </ul>
                    
                    <h5>3. Performance Optimization</h5>
                    <p>Improve app performance:</p>
                    <ul>
                        <li>Enable caching strategies</li>
                        <li>Optimize image loading</li>
                        <li>Minimize network requests</li>
                        <li>Implement lazy loading</li>
                    </ul>
                    
                    <h4>Modifying Configuration Files</h4>
                    <p>After downloading your package, you can edit configuration files to customize:</p>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">
{
  "name": "Your App Name",
  "short_name": "App",
  "theme_color": "#0d6efd",
  "background_color": "#ffffff"
}
                    </pre>
                    
                    <div style="background: #e7f3ff; padding: 15px; border-left: 4px solid #2196f3; margin: 20px 0;">
                        <strong>Expert Tip:</strong> Keep your app size under 50MB for faster downloads and better user experience.
                    </div>
                    
                    <h4>Adding Native Features</h4>
                    <p>Consider adding native features like:</p>
                    <ul>
                        <li>Push notifications</li>
                        <li>Camera access</li>
                        <li>Geolocation</li>
                        <li>Biometric authentication</li>
                    </ul>
                    
                    <p>These features require additional coding in the native project files.</p>
                    """,
                    order_position=6,
                    is_active=True
                ),
                Tutorial(
                    title="Deployment and Distribution",
                    description="Learn how to deploy and distribute your apps",
                    content="""
                    <h3>Deployment and Distribution</h3>
                    <p>Successfully deploy your apps to app stores and users.</p>
                    
                    <h4>Distribution Channels</h4>
                    
                    <h5>Google Play Store (Android)</h5>
                    <ul>
                        <li>Create a Google Play Developer account ($25 one-time fee)</li>
                        <li>Prepare store listing with screenshots and description</li>
                        <li>Upload your signed APK or App Bundle</li>
                        <li>Complete content rating questionnaire</li>
                        <li>Submit for review</li>
                    </ul>
                    
                    <h5>Apple App Store (iOS)</h5>
                    <ul>
                        <li>Enroll in Apple Developer Program ($99/year)</li>
                        <li>Create app listing in App Store Connect</li>
                        <li>Upload build via Xcode or Transporter</li>
                        <li>Fill out app information and privacy details</li>
                        <li>Submit for review (typically 1-3 days)</li>
                    </ul>
                    
                    <h5>Microsoft Store (Windows)</h5>
                    <ul>
                        <li>Register as Microsoft Store developer</li>
                        <li>Create app submission</li>
                        <li>Upload MSIX package</li>
                        <li>Provide store assets</li>
                        <li>Submit for certification</li>
                    </ul>
                    
                    <h4>Alternative Distribution</h4>
                    <p>You can also distribute apps through:</p>
                    <ul>
                        <li><strong>Direct Download:</strong> Host APK files on your website</li>
                        <li><strong>Enterprise Distribution:</strong> Internal company apps</li>
                        <li><strong>Beta Testing:</strong> TestFlight (iOS) or Google Play Beta (Android)</li>
                    </ul>
                    
                    <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <strong>Important:</strong> Each app store has specific requirements for app quality, privacy policies, and content guidelines.
                    </div>
                    
                    <h4>Post-Launch Activities</h4>
                    <p>After launching your app:</p>
                    <ul>
                        <li>Monitor user reviews and ratings</li>
                        <li>Track download and usage analytics</li>
                        <li>Release updates regularly</li>
                        <li>Respond to user feedback</li>
                        <li>Promote through marketing channels</li>
                    </ul>
                    
                    <h4>Monetization Options</h4>
                    <p>Consider these monetization strategies:</p>
                    <ul>
                        <li>In-app advertising (Google AdMob, etc.)</li>
                        <li>Paid app downloads</li>
                        <li>In-app purchases</li>
                        <li>Subscription models</li>
                    </ul>
                    """,
                    order_position=7,
                    is_active=True
                ),
                Tutorial(
                    title="App Performance Optimization",
                    description="Optimize your mobile app for speed and efficiency",
                    content="""
                    <h3>App Performance Optimization</h3>
                    <p>Learn how to create fast, responsive mobile applications that users love.</p>
                    
                    <h4>Why Performance Matters</h4>
                    <p>App performance directly impacts:</p>
                    <ul>
                        <li>User retention and engagement</li>
                        <li>App store ratings and reviews</li>
                        <li>Conversion rates</li>
                        <li>Battery life and device resources</li>
                    </ul>
                    
                    <h4>Loading Time Optimization</h4>
                    <h5>1. Reduce Initial Load Time</h5>
                    <ul>
                        <li>Minimize JavaScript bundle size</li>
                        <li>Implement code splitting</li>
                        <li>Use lazy loading for images and components</li>
                        <li>Enable compression (gzip/brotli)</li>
                    </ul>
                    
                    <h5>2. Optimize Images and Media</h5>
                    <ul>
                        <li>Use appropriate image formats (WebP, AVIF)</li>
                        <li>Implement responsive images</li>
                        <li>Compress images without quality loss</li>
                        <li>Use CDN for static assets</li>
                    </ul>
                    
                    <h4>Runtime Performance</h4>
                    <h5>Rendering Optimization</h5>
                    <ul>
                        <li>Minimize DOM manipulation</li>
                        <li>Use virtual scrolling for long lists</li>
                        <li>Implement debouncing and throttling</li>
                        <li>Avoid memory leaks</li>
                    </ul>
                    
                    <div style="background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                        <strong>Performance Goal:</strong> Your app should load in under 3 seconds on 3G networks and respond to user input within 100ms.
                    </div>
                    
                    <h4>Caching Strategies</h4>
                    <ul>
                        <li><strong>Service Worker:</strong> Cache static assets and API responses</li>
                        <li><strong>LocalStorage:</strong> Store user preferences and small data</li>
                        <li><strong>IndexedDB:</strong> Cache larger datasets offline</li>
                        <li><strong>HTTP Caching:</strong> Proper cache headers</li>
                    </ul>
                    
                    <h4>Performance Monitoring</h4>
                    <p>Use these tools to measure performance:</p>
                    <ul>
                        <li>Chrome DevTools Performance tab</li>
                        <li>Lighthouse audits</li>
                        <li>WebPageTest</li>
                        <li>Real User Monitoring (RUM)</li>
                    </ul>
                    """,
                    order_position=8,
                    is_active=True
                ),
                Tutorial(
                    title="Security Best Practices",
                    description="Secure your mobile applications against threats",
                    content="""
                    <h3>Security Best Practices</h3>
                    <p>Protect your app and users with essential security measures.</p>
                    
                    <h4>HTTPS and SSL/TLS</h4>
                    <p>Always use HTTPS for all communications:</p>
                    <ul>
                        <li>Obtain valid SSL/TLS certificates</li>
                        <li>Enforce HTTPS redirects</li>
                        <li>Enable HTTP Strict Transport Security (HSTS)</li>
                        <li>Use certificate pinning for sensitive apps</li>
                    </ul>
                    
                    <h4>Data Protection</h4>
                    <h5>1. Sensitive Data Storage</h5>
                    <ul>
                        <li>Never store passwords in plain text</li>
                        <li>Use secure storage APIs (Keychain, KeyStore)</li>
                        <li>Encrypt sensitive data at rest</li>
                        <li>Clear sensitive data from memory after use</li>
                    </ul>
                    
                    <h5>2. API Security</h5>
                    <ul>
                        <li>Implement authentication (OAuth 2.0, JWT)</li>
                        <li>Use API rate limiting</li>
                        <li>Validate all user inputs</li>
                        <li>Implement proper authorization checks</li>
                    </ul>
                    
                    <div style="background: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
                        <strong>Warning:</strong> Never hardcode API keys, passwords, or secrets in your app code. Use environment variables or secure key management services.
                    </div>
                    
                    <h4>Common Vulnerabilities</h4>
                    <h5>Protect Against:</h5>
                    <ul>
                        <li><strong>XSS Attacks:</strong> Sanitize user inputs and outputs</li>
                        <li><strong>SQL Injection:</strong> Use parameterized queries</li>
                        <li><strong>CSRF:</strong> Implement anti-CSRF tokens</li>
                        <li><strong>Man-in-the-Middle:</strong> Certificate pinning</li>
                    </ul>
                    
                    <h4>User Authentication</h4>
                    <p>Implement strong authentication:</p>
                    <ul>
                        <li>Multi-factor authentication (MFA)</li>
                        <li>Biometric authentication (fingerprint, face ID)</li>
                        <li>Strong password requirements</li>
                        <li>Session timeout and management</li>
                    </ul>
                    
                    <h4>Privacy Compliance</h4>
                    <p>Ensure compliance with privacy regulations:</p>
                    <ul>
                        <li><strong>GDPR:</strong> European users' data protection</li>
                        <li><strong>CCPA:</strong> California consumer privacy</li>
                        <li><strong>COPPA:</strong> Children's privacy protection</li>
                        <li>Implement clear privacy policies</li>
                        <li>Provide data deletion options</li>
                    </ul>
                    
                    <h4>Security Checklist</h4>
                    <ol>
                        <li>Regular security audits and penetration testing</li>
                        <li>Keep all dependencies updated</li>
                        <li>Implement proper error handling (don't expose stack traces)</li>
                        <li>Use code obfuscation for production builds</li>
                        <li>Monitor for security vulnerabilities</li>
                    </ol>
                    """,
                    order_position=9,
                    is_active=True
                ),
                Tutorial(
                    title="Push Notifications and User Engagement",
                    description="Keep users engaged with effective notifications",
                    content="""
                    <h3>Push Notifications and User Engagement</h3>
                    <p>Master the art of user engagement through strategic push notifications.</p>
                    
                    <h4>Types of Push Notifications</h4>
                    <ul>
                        <li><strong>Transactional:</strong> Order updates, confirmations, receipts</li>
                        <li><strong>Marketing:</strong> Promotions, new features, special offers</li>
                        <li><strong>Re-engagement:</strong> Bring back inactive users</li>
                        <li><strong>Location-based:</strong> Geofencing and proximity alerts</li>
                    </ul>
                    
                    <h4>Setting Up Push Notifications</h4>
                    
                    <h5>Android (Firebase Cloud Messaging)</h5>
                    <ol>
                        <li>Create a Firebase project</li>
                        <li>Add your app to Firebase</li>
                        <li>Download google-services.json</li>
                        <li>Implement FCM SDK</li>
                        <li>Request notification permissions</li>
                    </ol>
                    
                    <h5>iOS (Apple Push Notification Service)</h5>
                    <ol>
                        <li>Enable push notifications in Xcode</li>
                        <li>Create APNs certificates</li>
                        <li>Implement UserNotifications framework</li>
                        <li>Request user permission</li>
                        <li>Handle device tokens</li>
                    </ol>
                    
                    <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <strong>Best Practice:</strong> Always request permission at the right moment, not immediately on app launch. Explain the value users will receive.
                    </div>
                    
                    <h4>Notification Best Practices</h4>
                    
                    <h5>Do's:</h5>
                    <ul>
                        <li>Personalize messages based on user behavior</li>
                        <li>Send notifications at optimal times</li>
                        <li>Use rich media (images, videos, emojis)</li>
                        <li>Include clear call-to-actions</li>
                        <li>A/B test your messaging</li>
                    </ul>
                    
                    <h5>Don'ts:</h5>
                    <ul>
                        <li>Send too many notifications (notification fatigue)</li>
                        <li>Use clickbait or misleading content</li>
                        <li>Send at inappropriate times (late night)</li>
                        <li>Ignore user preferences</li>
                        <li>Use generic, non-personalized messages</li>
                    </ul>
                    
                    <h4>Notification Channels (Android)</h4>
                    <p>Group notifications by type:</p>
                    <ul>
                        <li>Order Updates</li>
                        <li>Promotional Offers</li>
                        <li>Social Interactions</li>
                        <li>System Alerts</li>
                    </ul>
                    
                    <h4>Measuring Success</h4>
                    <p>Track these metrics:</p>
                    <ul>
                        <li><strong>Open Rate:</strong> Percentage of notifications opened</li>
                        <li><strong>Click-Through Rate:</strong> Actions taken after opening</li>
                        <li><strong>Opt-out Rate:</strong> Users disabling notifications</li>
                        <li><strong>Conversion Rate:</strong> Desired actions completed</li>
                    </ul>
                    
                    <h4>Advanced Features</h4>
                    <ul>
                        <li>Deep linking to specific app screens</li>
                        <li>Interactive notifications with action buttons</li>
                        <li>Silent notifications for background updates</li>
                        <li>Notification badges and counters</li>
                    </ul>
                    """,
                    order_position=10,
                    is_active=True
                ),
                Tutorial(
                    title="Offline Functionality and PWA Features",
                    description="Build apps that work seamlessly offline",
                    content="""
                    <h3>Offline Functionality and PWA Features</h3>
                    <p>Create reliable apps that work even without internet connectivity.</p>
                    
                    <h4>Why Offline Support Matters</h4>
                    <ul>
                        <li>Improved user experience in poor connectivity</li>
                        <li>Faster load times with cached resources</li>
                        <li>Increased user engagement and retention</li>
                        <li>Better app store ratings</li>
                    </ul>
                    
                    <h4>Service Workers</h4>
                    <p>The foundation of offline functionality:</p>
                    
                    <h5>Key Features:</h5>
                    <ul>
                        <li>Intercept and handle network requests</li>
                        <li>Cache assets and API responses</li>
                        <li>Enable background sync</li>
                        <li>Serve cached content when offline</li>
                    </ul>
                    
                    <h5>Basic Service Worker Structure:</h5>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">
// sw.js
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('v1').then(cache => {
      return cache.addAll([
        '/',
        '/styles.css',
        '/app.js',
        '/offline.html'
      ]);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
                    </pre>
                    
                    <h4>Caching Strategies</h4>
                    
                    <h5>1. Cache First</h5>
                    <p>Best for: Static assets, images, stylesheets</p>
                    <p>Serves cached content first, network as fallback</p>
                    
                    <h5>2. Network First</h5>
                    <p>Best for: Dynamic content, API calls</p>
                    <p>Tries network first, falls back to cache if offline</p>
                    
                    <h5>3. Stale While Revalidate</h5>
                    <p>Best for: Frequently updated content</p>
                    <p>Serves cached content while fetching updates in background</p>
                    
                    <div style="background: #d1ecf1; padding: 15px; border-left: 4px solid #0dcaf0; margin: 20px 0;">
                        <strong>Tip:</strong> Use different caching strategies for different types of resources to optimize performance and freshness.
                    </div>
                    
                    <h4>Offline Data Storage</h4>
                    
                    <h5>Storage Options:</h5>
                    <ul>
                        <li><strong>LocalStorage:</strong> Simple key-value storage (5MB limit)</li>
                        <li><strong>IndexedDB:</strong> Large structured data storage</li>
                        <li><strong>Cache API:</strong> HTTP request/response caching</li>
                        <li><strong>Web SQL:</strong> (Deprecated, use IndexedDB instead)</li>
                    </ul>
                    
                    <h4>Background Sync</h4>
                    <p>Queue actions when offline, sync when online:</p>
                    <ul>
                        <li>Form submissions</li>
                        <li>Data updates</li>
                        <li>File uploads</li>
                        <li>Analytics events</li>
                    </ul>
                    
                    <h4>Offline UI/UX</h4>
                    <p>Enhance offline experience:</p>
                    <ul>
                        <li>Show offline indicator banner</li>
                        <li>Display cached content with "offline" badge</li>
                        <li>Disable features that require connectivity</li>
                        <li>Queue user actions for later sync</li>
                        <li>Provide helpful error messages</li>
                    </ul>
                    
                    <h4>Testing Offline Features</h4>
                    <p>How to test:</p>
                    <ol>
                        <li>Use Chrome DevTools offline mode</li>
                        <li>Test on actual devices with airplane mode</li>
                        <li>Simulate slow/unstable connections</li>
                        <li>Test cache invalidation strategies</li>
                    </ol>
                    """,
                    order_position=11,
                    is_active=True
                ),
                Tutorial(
                    title="App Analytics and User Tracking",
                    description="Measure and improve app performance with analytics",
                    content="""
                    <h3>App Analytics and User Tracking</h3>
                    <p>Make data-driven decisions to improve your app's success.</p>
                    
                    <h4>Why Analytics Matter</h4>
                    <ul>
                        <li>Understand user behavior and preferences</li>
                        <li>Identify bottlenecks and pain points</li>
                        <li>Measure feature adoption and success</li>
                        <li>Optimize conversion funnels</li>
                        <li>Justify business decisions with data</li>
                    </ul>
                    
                    <h4>Popular Analytics Platforms</h4>
                    
                    <h5>1. Google Analytics for Mobile</h5>
                    <ul>
                        <li>Free and comprehensive</li>
                        <li>Screen tracking and user flows</li>
                        <li>Event tracking and custom dimensions</li>
                        <li>Real-time reporting</li>
                    </ul>
                    
                    <h5>2. Firebase Analytics</h5>
                    <ul>
                        <li>Unlimited event tracking</li>
                        <li>Audience segmentation</li>
                        <li>Integration with other Firebase services</li>
                        <li>Automatic event collection</li>
                    </ul>
                    
                    <h5>3. Mixpanel</h5>
                    <ul>
                        <li>Advanced funnel analysis</li>
                        <li>Cohort analysis</li>
                        <li>A/B testing capabilities</li>
                        <li>User retention tracking</li>
                    </ul>
                    
                    <h4>Key Metrics to Track</h4>
                    
                    <h5>Engagement Metrics:</h5>
                    <ul>
                        <li><strong>Daily Active Users (DAU):</strong> Users per day</li>
                        <li><strong>Monthly Active Users (MAU):</strong> Users per month</li>
                        <li><strong>Session Duration:</strong> Time spent per session</li>
                        <li><strong>Session Frequency:</strong> How often users return</li>
                    </ul>
                    
                    <h5>Retention Metrics:</h5>
                    <ul>
                        <li><strong>Day 1 Retention:</strong> Users returning after 24 hours</li>
                        <li><strong>Day 7 Retention:</strong> Users returning after 1 week</li>
                        <li><strong>Day 30 Retention:</strong> Users returning after 1 month</li>
                        <li><strong>Churn Rate:</strong> Users who stop using the app</li>
                    </ul>
                    
                    <div style="background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                        <strong>Industry Benchmark:</strong> Good mobile apps typically have 20-40% Day 1 retention, 10-20% Day 7, and 5-10% Day 30.
                    </div>
                    
                    <h4>Event Tracking</h4>
                    <p>Track important user actions:</p>
                    <ul>
                        <li>App launches and screen views</li>
                        <li>Button clicks and interactions</li>
                        <li>Form submissions</li>
                        <li>Purchase and checkout events</li>
                        <li>Feature usage</li>
                        <li>Errors and crashes</li>
                    </ul>
                    
                    <h4>User Segmentation</h4>
                    <p>Group users by characteristics:</p>
                    <ul>
                        <li>Demographics (age, gender, location)</li>
                        <li>Behavior patterns (power users, casual users)</li>
                        <li>Acquisition channel (organic, paid, referral)</li>
                        <li>Device type and OS version</li>
                        <li>Subscription status</li>
                    </ul>
                    
                    <h4>Funnel Analysis</h4>
                    <p>Track conversion steps:</p>
                    <ol>
                        <li>App install</li>
                        <li>Account creation</li>
                        <li>First interaction</li>
                        <li>Feature discovery</li>
                        <li>Purchase or conversion</li>
                    </ol>
                    
                    <h4>Privacy and Compliance</h4>
                    <ul>
                        <li>Obtain user consent for tracking</li>
                        <li>Provide opt-out options</li>
                        <li>Anonymize personal data</li>
                        <li>Comply with GDPR, CCPA regulations</li>
                        <li>Be transparent about data collection</li>
                    </ul>
                    
                    <h4>Actionable Insights</h4>
                    <p>Use analytics to:</p>
                    <ul>
                        <li>Identify and fix user pain points</li>
                        <li>Optimize onboarding flow</li>
                        <li>Prioritize feature development</li>
                        <li>Improve user retention strategies</li>
                        <li>Maximize monetization opportunities</li>
                    </ul>
                    """,
                    order_position=12,
                    is_active=True
                ),
                Tutorial(
                    title="App Store Optimization (ASO)",
                    description="Increase app downloads through ASO strategies",
                    content="""
                    <h3>App Store Optimization (ASO)</h3>
                    <p>Improve your app's visibility and downloads in app stores.</p>
                    
                    <h4>What is ASO?</h4>
                    <p>App Store Optimization is the process of improving your app's visibility in app stores to increase organic downloads. It's like SEO, but for mobile apps.</p>
                    
                    <h4>Key ASO Elements</h4>
                    
                    <h5>1. App Title</h5>
                    <ul>
                        <li>Include primary keyword (max 30 chars for App Store)</li>
                        <li>Make it memorable and unique</li>
                        <li>Convey app's main value proposition</li>
                        <li>Example: "Duolingo: Language Lessons"</li>
                    </ul>
                    
                    <h5>2. Subtitle/Short Description</h5>
                    <ul>
                        <li>iOS subtitle: 30 characters max</li>
                        <li>Android short description: 80 characters max</li>
                        <li>Include secondary keywords</li>
                        <li>Highlight unique selling points</li>
                    </ul>
                    
                    <h5>3. App Description</h5>
                    <p>Google Play (4000 chars) and App Store (4000 chars):</p>
                    <ul>
                        <li>First 2-3 lines are crucial (visible without expanding)</li>
                        <li>Use bullet points for features</li>
                        <li>Include relevant keywords naturally</li>
                        <li>Add social proof (awards, reviews)</li>
                        <li>Clear call-to-action</li>
                    </ul>
                    
                    <div style="background: #e7f3ff; padding: 15px; border-left: 4px solid #2196f3; margin: 20px 0;">
                        <strong>Pro Tip:</strong> The first 3 lines of your description are the most important. Make them count!
                    </div>
                    
                    <h4>Visual Assets</h4>
                    
                    <h5>App Icon</h5>
                    <ul>
                        <li>Simple, memorable design</li>
                        <li>Looks good at small sizes</li>
                        <li>Stands out from competitors</li>
                        <li>Consistent with brand identity</li>
                        <li>A/B test different variations</li>
                    </ul>
                    
                    <h5>Screenshots</h5>
                    <ul>
                        <li>Show key features (2-8 screenshots)</li>
                        <li>Use captions to highlight benefits</li>
                        <li>Show actual app UI</li>
                        <li>Portrait and landscape orientations</li>
                        <li>Update regularly with new features</li>
                    </ul>
                    
                    <h5>App Preview Video</h5>
                    <ul>
                        <li>15-30 seconds optimal length</li>
                        <li>Show core functionality</li>
                        <li>No sound required (auto-plays muted)</li>
                        <li>Hook viewers in first 3 seconds</li>
                    </ul>
                    
                    <h4>Keyword Research</h4>
                    <p>Finding the right keywords:</p>
                    <ol>
                        <li>Brainstorm relevant terms</li>
                        <li>Analyze competitor keywords</li>
                        <li>Use keyword research tools (App Annie, Sensor Tower)</li>
                        <li>Check search volume and difficulty</li>
                        <li>Target long-tail keywords for easier ranking</li>
                    </ol>
                    
                    <h4>Ratings and Reviews</h4>
                    <p>Crucial for conversions:</p>
                    <ul>
                        <li>Encourage satisfied users to rate</li>
                        <li>Respond to all reviews (positive and negative)</li>
                        <li>Fix issues mentioned in negative reviews</li>
                        <li>Use in-app prompts at optimal moments</li>
                        <li>Aim for 4+ star average rating</li>
                    </ul>
                    
                    <h4>Localization</h4>
                    <p>Expand to new markets:</p>
                    <ul>
                        <li>Translate metadata (title, description, keywords)</li>
                        <li>Localize screenshots and videos</li>
                        <li>Adapt to cultural preferences</li>
                        <li>Start with high-value markets</li>
                    </ul>
                    
                    <h4>ASO Metrics to Track</h4>
                    <ul>
                        <li><strong>Impressions:</strong> How often your app appears in search</li>
                        <li><strong>Conversion Rate:</strong> Visitors who download</li>
                        <li><strong>Keyword Rankings:</strong> Position for target keywords</li>
                        <li><strong>Category Rankings:</strong> Position in app categories</li>
                    </ul>
                    
                    <h4>Common ASO Mistakes</h4>
                    <ul>
                        <li>Keyword stuffing in title/description</li>
                        <li>Using misleading screenshots</li>
                        <li>Ignoring negative reviews</li>
                        <li>Not updating listing regularly</li>
                        <li>Poor quality app icon</li>
                    </ul>
                    """,
                    order_position=13,
                    is_active=True
                ),
                Tutorial(
                    title="Testing and Quality Assurance",
                    description="Ensure app quality through comprehensive testing",
                    content="""
                    <h3>Testing and Quality Assurance</h3>
                    <p>Build reliable, bug-free applications through thorough testing.</p>
                    
                    <h4>Types of Mobile App Testing</h4>
                    
                    <h5>1. Functional Testing</h5>
                    <p>Verify app features work as expected:</p>
                    <ul>
                        <li>User authentication and registration</li>
                        <li>Form validations</li>
                        <li>Navigation and user flows</li>
                        <li>Data input and output</li>
                        <li>Core functionality</li>
                    </ul>
                    
                    <h5>2. Usability Testing</h5>
                    <p>Evaluate user experience:</p>
                    <ul>
                        <li>Intuitive navigation</li>
                        <li>Clear labeling and instructions</li>
                        <li>Consistent design patterns</li>
                        <li>Accessibility for all users</li>
                        <li>Touch target sizes</li>
                    </ul>
                    
                    <h5>3. Performance Testing</h5>
                    <ul>
                        <li>Load time and responsiveness</li>
                        <li>Memory usage and leaks</li>
                        <li>CPU utilization</li>
                        <li>Battery consumption</li>
                        <li>Network performance (3G, 4G, WiFi)</li>
                    </ul>
                    
                    <h5>4. Security Testing</h5>
                    <ul>
                        <li>Data encryption verification</li>
                        <li>Authentication security</li>
                        <li>API security</li>
                        <li>Sensitive data handling</li>
                        <li>Vulnerability scanning</li>
                    </ul>
                    
                    <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <strong>Testing Rule:</strong> Test early, test often. The cost of fixing bugs increases exponentially the later they're discovered.
                    </div>
                    
                    <h4>Device and Platform Testing</h4>
                    
                    <h5>Test On:</h5>
                    <ul>
                        <li>Multiple OS versions (iOS 14+, Android 8+)</li>
                        <li>Different screen sizes and resolutions</li>
                        <li>Various device manufacturers</li>
                        <li>Tablets and phones</li>
                        <li>Low-end and high-end devices</li>
                    </ul>
                    
                    <h4>Testing Tools</h4>
                    
                    <h5>Automated Testing:</h5>
                    <ul>
                        <li><strong>Appium:</strong> Cross-platform mobile testing</li>
                        <li><strong>Espresso:</strong> Android UI testing</li>
                        <li><strong>XCTest:</strong> iOS testing framework</li>
                        <li><strong>Detox:</strong> React Native testing</li>
                    </ul>
                    
                    <h5>Manual Testing Tools:</h5>
                    <ul>
                        <li><strong>TestFlight:</strong> iOS beta testing</li>
                        <li><strong>Google Play Console:</strong> Android testing tracks</li>
                        <li><strong>BrowserStack:</strong> Real device testing</li>
                        <li><strong>Firebase Test Lab:</strong> Cloud-based testing</li>
                    </ul>
                    
                    <h4>Beta Testing Program</h4>
                    <p>Steps to successful beta testing:</p>
                    <ol>
                        <li>Define testing objectives</li>
                        <li>Recruit diverse beta testers</li>
                        <li>Provide clear testing guidelines</li>
                        <li>Set up feedback channels</li>
                        <li>Track and prioritize issues</li>
                        <li>Iterate based on feedback</li>
                    </ol>
                    
                    <h4>Common Testing Scenarios</h4>
                    <ul>
                        <li><strong>Interruptions:</strong> Incoming calls, notifications</li>
                        <li><strong>Network Changes:</strong> WiFi to cellular, offline mode</li>
                        <li><strong>Low Battery:</strong> App behavior at low power</li>
                        <li><strong>Permissions:</strong> Denied camera, location access</li>
                        <li><strong>Memory Pressure:</strong> Low storage, RAM limits</li>
                        <li><strong>Orientation Changes:</strong> Portrait to landscape</li>
                    </ul>
                    
                    <h4>Crash Reporting</h4>
                    <p>Implement crash tracking:</p>
                    <ul>
                        <li><strong>Crashlytics:</strong> Real-time crash reporting</li>
                        <li><strong>Sentry:</strong> Error tracking and monitoring</li>
                        <li><strong>Bugsnag:</strong> Stability monitoring</li>
                    </ul>
                    
                    <h4>QA Checklist</h4>
                    <p>Before release, verify:</p>
                    <ul>
                        <li>✓ All features work as specified</li>
                        <li>✓ No critical or major bugs</li>
                        <li>✓ Tested on target devices and OS versions</li>
                        <li>✓ Performance meets benchmarks</li>
                        <li>✓ Security vulnerabilities addressed</li>
                        <li>✓ App store guidelines compliance</li>
                        <li>✓ Privacy policy and terms updated</li>
                        <li>✓ Analytics and crash reporting configured</li>
                    </ul>
                    
                    <h4>Regression Testing</h4>
                    <p>Test after every update:</p>
                    <ul>
                        <li>Ensure new features don't break existing ones</li>
                        <li>Maintain automated regression test suite</li>
                        <li>Test critical user paths</li>
                        <li>Verify bug fixes didn't create new issues</li>
                    </ul>
                    """,
                    order_position=14,
                    is_active=True
                )
            ]
            
            for tutorial in tutorials:
                db.session.add(tutorial)
            
            app.logger.info(f"Created {len(tutorials)} tutorials")
        
        db.session.commit()
        
    except Exception as e:
        app.logger.error(f"Database initialization error: {str(e)}")
        db.session.rollback()