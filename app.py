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
                )
            ]
            
            for tutorial in tutorials:
                db.session.add(tutorial)
            
            app.logger.info(f"Created {len(tutorials)} tutorials")
        
        db.session.commit()
        
    except Exception as e:
        app.logger.error(f"Database initialization error: {str(e)}")
        db.session.rollback()