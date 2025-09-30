from app import app, db
from models import AdminSettings, AdminUser

def init_default_settings():
    """Initialize default admin settings if they don't exist"""
    with app.app_context():
        # Create default settings if missing
        settings = AdminSettings.query.first()
        if not settings:
            settings = AdminSettings(
                google_adsense_code='',
                payment_account_name='Digital Skeleton',
                payment_bank_name='Default Bank',
                payment_account_number='1234567890',
                admin_email='admin@digitalskeleton.com',
                banner_price_per_day=10.0
            )
            db.session.add(settings)
            db.session.commit()
            print("Default settings created")
        else:
            print("Settings already exist")

        # Create default admin user if none exists
        admin = AdminUser.query.first()
        if not admin:
            admin = AdminUser(
                username='admin',
                email='admin@digitalskeleton.com'
            )
            admin.set_password('admin123')  # Change this password!
            db.session.add(admin)
            print("Created default admin user (username: admin, password: admin123)")

        # Create sample tutorial if none exist
        from models import Tutorial
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
            db.session.commit()
            print("Sample tutorial created")

        db.session.commit()
        print("Default settings initialization complete")

if __name__ == '__main__':
    init_default_settings()