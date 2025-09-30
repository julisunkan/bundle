
from app import app, db
from models import AdminSettings, AdminUser

def init_default_settings():
    """Initialize default admin settings if they don't exist"""
    with app.app_context():
        # Create default admin settings
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
            print("Created default admin settings")
        
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
        
        db.session.commit()
        print("Default settings initialization complete")

if __name__ == '__main__':
    init_default_settings()
