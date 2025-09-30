#!/usr/bin/env python3
"""Initialize admin user and settings for the ad management system"""

from app import app, db
from models import AdminUser, AdminSettings

def init_admin():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if admin user exists
        existing_admin = AdminUser.query.filter_by(username='admin').first()
        if not existing_admin:
            # Create admin user
            admin = AdminUser()
            admin.username = 'admin'
            admin.email = 'support@digitalskeleton.com.ng'
            admin.set_password('admin123')  # Change this password immediately after first login
            db.session.add(admin)
            print("✓ Admin user created (username: admin, password: admin123)")
        else:
            print("✓ Admin user already exists")
        
        # Check if settings exist
        existing_settings = AdminSettings.query.first()
        if not existing_settings:
            # Create default settings
            settings = AdminSettings()
            settings.admin_email = 'support@digitalskeleton.com.ng'
            settings.banner_price_per_day = 10.0
            db.session.add(settings)
            print("✓ Admin settings created")
        else:
            print("✓ Admin settings already exist")
        
        db.session.commit()
        print("\n✅ Admin initialization complete!")
        print("\nLogin credentials:")
        print("  URL: /admin/login")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n⚠️  IMPORTANT: Change the default password after first login!")

if __name__ == '__main__':
    init_admin()
