import os
from flask import Flask
from flask_login import LoginManager
from models import db, User

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static/certificates', exist_ok=True)
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.student import student_bp
    from routes.payments import payments_bp
    from routes.pwa import pwa_bp
    from routes.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(pwa_bp)
    
    @app.template_filter('format_currency')
    def format_currency(value):
        if value is None:
            return '0.00'
        return '{:,.2f}'.format(float(value))
    
    with app.app_context():
        db.create_all()
        init_database()
    
    return app

def init_database():
    from models import User, Settings, Course, Policy
    from init_data import populate_courses
    
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            email='admin@example.com',
            full_name='Admin User',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    default_settings = [
        ('paystack_public_key', ''),
        ('paystack_secret_key', ''),
        ('flutterwave_public_key', ''),
        ('flutterwave_secret_key', ''),
        ('exchange_rate', '1500'),
    ]
    
    for key, value in default_settings:
        if not Settings.query.filter_by(key=key).first():
            setting = Settings(key=key, value=value)
            db.session.add(setting)
    
    from datetime import datetime
    current_date = datetime.utcnow().strftime('%B %d, %Y')
    
    default_policies = [
        ('privacy', f'''<h2>Privacy Policy</h2>
<p>Your privacy is important to us. This privacy policy explains how we collect, use, and protect your personal information.</p>

<h3>Information We Collect</h3>
<p>We collect information you provide directly to us, such as when you create an account, enroll in a course, or contact us for support.</p>

<h3>How We Use Your Information</h3>
<p>We use the information we collect to provide, maintain, and improve our services, process transactions, and communicate with you.</p>

<h3>Data Security</h3>
<p>We implement appropriate technical and organizational measures to protect your personal information.</p>

<p><em>Last updated: {current_date}</em></p>'''),
        ('terms', f'''<h2>Terms and Conditions</h2>
<p>Welcome to DigitalSkeleton. By accessing our platform, you agree to be bound by these terms and conditions.</p>

<h3>Use of Service</h3>
<p>You may use our service only as permitted by law and these terms. You are responsible for maintaining the security of your account.</p>

<h3>Course Access</h3>
<p>Upon successful payment, you will receive access to the purchased course materials. Course access is personal and non-transferable.</p>

<h3>Intellectual Property</h3>
<p>All course content, including videos, text, and materials, are protected by copyright and are the property of DigitalSkeleton.</p>

<p><em>Last updated: {current_date}</em></p>'''),
        ('refund', f'''<h2>Refund Policy</h2>
<p>We want you to be satisfied with your purchase. Please read our refund policy carefully.</p>

<h3>Refund Eligibility</h3>
<p>You may request a refund within 7 days of purchase if you have not completed more than 10% of the course content.</p>

<h3>How to Request a Refund</h3>
<p>To request a refund, please contact our support team with your order details and reason for the refund request.</p>

<h3>Processing Time</h3>
<p>Approved refunds will be processed within 5-10 business days to your original payment method.</p>

<p><em>Last updated: {current_date}</em></p>''')
    ]
    
    for policy_type, content in default_policies:
        if not Policy.query.filter_by(policy_type=policy_type).first():
            policy = Policy(policy_type=policy_type, content=content)
            db.session.add(policy)
    
    db.session.commit()
    
    if Course.query.count() == 0:
        populate_courses()

# Create app instance at module level for gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
