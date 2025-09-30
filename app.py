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
        
        # Check and create sample tutorial if none exist
        if Tutorial.query.count() == 0:
            sample_tutorial = Tutorial(
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
            )
            db.session.add(sample_tutorial)
            app.logger.info("Created sample tutorial")
        
        db.session.commit()
        
    except Exception as e:
        app.logger.error(f"Database initialization error: {str(e)}")
        db.session.rollback()