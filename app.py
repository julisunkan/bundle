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
        ('privacy', f'''<div class="container my-5">
    <h1 class="mb-4">Privacy Policy</h1>
    <p class="text-muted">Last updated: {current_date}</p>

    <section class="my-4">
        <h2>1. Introduction</h2>
        <p>DigitalSkeleton ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our online learning platform.</p>
    </section>

    <section class="my-4">
        <h2>2. Information We Collect</h2>
        <h4>Personal Information</h4>
        <p>We collect information you provide directly to us, including:</p>
        <ul>
            <li>Name and email address</li>
            <li>Account credentials</li>
            <li>Payment information (processed securely through third-party payment processors)</li>
            <li>Course enrollment and progress data</li>
            <li>Assignment submissions and quiz responses</li>
        </ul>
        
        <h4>Automatically Collected Information</h4>
        <p>When you access our platform, we may automatically collect:</p>
        <ul>
            <li>Device and browser information</li>
            <li>IP address and location data</li>
            <li>Usage data and learning analytics</li>
            <li>Cookies and similar tracking technologies</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>3. How We Use Your Information</h2>
        <p>We use the collected information for:</p>
        <ul>
            <li>Providing and maintaining our educational services</li>
            <li>Processing course enrollments and payments</li>
            <li>Tracking your learning progress and issuing certificates</li>
            <li>Communicating with you about courses, updates, and support</li>
            <li>Improving our platform and developing new features</li>
            <li>Preventing fraud and ensuring platform security</li>
            <li>Complying with legal obligations</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>4. Information Sharing and Disclosure</h2>
        <p>We do not sell your personal information. We may share your information with:</p>
        <ul>
            <li><strong>Service Providers:</strong> Third-party vendors who assist in payment processing, hosting, and analytics</li>
            <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
            <li><strong>Business Transfers:</strong> In connection with any merger, sale, or acquisition</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>5. Data Security</h2>
        <p>We implement industry-standard security measures to protect your personal information from unauthorized access, disclosure, alteration, or destruction. However, no internet transmission is completely secure, and we cannot guarantee absolute security.</p>
    </section>

    <section class="my-4">
        <h2>6. Your Rights</h2>
        <p>You have the right to:</p>
        <ul>
            <li>Access and update your personal information</li>
            <li>Request deletion of your account and data</li>
            <li>Opt-out of marketing communications</li>
            <li>Object to certain data processing activities</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>7. Cookies</h2>
        <p>We use cookies and similar technologies to enhance your experience, analyze usage patterns, and remember your preferences. You can control cookie settings through your browser.</p>
    </section>

    <section class="my-4">
        <h2>8. Children's Privacy</h2>
        <p>Our platform is not intended for users under 13 years of age. We do not knowingly collect personal information from children under 13.</p>
    </section>

    <section class="my-4">
        <h2>9. Changes to This Policy</h2>
        <p>We may update this Privacy Policy from time to time. We will notify you of significant changes by posting the new policy on our platform.</p>
    </section>

    <section class="my-4">
        <h2>10. Contact Us</h2>
        <p>If you have questions about this Privacy Policy, please contact us at:</p>
        <p><strong>Email:</strong> ceo@digitalskeleton.com.ng</p>
    </section>
</div>'''),
        ('terms', f'''<div class="container my-5">
    <h1 class="mb-4">Terms & Conditions</h1>
    <p class="text-muted">Last updated: {current_date}</p>

    <section class="my-4">
        <h2>1. Acceptance of Terms</h2>
        <p>By accessing and using DigitalSkeleton's online learning platform, you accept and agree to be bound by these Terms and Conditions. If you do not agree to these terms, please do not use our platform.</p>
    </section>

    <section class="my-4">
        <h2>2. User Accounts</h2>
        <h4>Account Creation</h4>
        <p>To access courses, you must create an account by providing accurate and complete information. You are responsible for:</p>
        <ul>
            <li>Maintaining the confidentiality of your account credentials</li>
            <li>All activities that occur under your account</li>
            <li>Notifying us immediately of any unauthorized access</li>
        </ul>
        
        <h4>Account Termination</h4>
        <p>We reserve the right to suspend or terminate your account for violations of these terms, fraudulent activity, or any other reason at our discretion.</p>
    </section>

    <section class="my-4">
        <h2>3. Course Enrollment and Access</h2>
        <p>Upon successful payment, you will receive lifetime access to the purchased course content, subject to these terms:</p>
        <ul>
            <li>Course access is personal and non-transferable</li>
            <li>You may not share your account credentials with others</li>
            <li>We reserve the right to modify or discontinue courses with notice</li>
            <li>Course content may be updated or improved over time</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>4. Payment and Pricing</h2>
        <ul>
            <li>All prices are listed in Nigerian Naira (NGN) and US Dollars (USD)</li>
            <li>Payments are processed securely through third-party payment processors (Paystack/Flutterwave)</li>
            <li>We reserve the right to change course prices at any time</li>
            <li>All sales are final - see our Refund Policy for details</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>5. Intellectual Property Rights</h2>
        <p>All course materials, including but not limited to videos, text, images, quizzes, and assignments, are protected by copyright and other intellectual property laws. You agree that:</p>
        <ul>
            <li>All content is owned by DigitalSkeleton or its licensors</li>
            <li>You may not reproduce, distribute, or create derivative works without permission</li>
            <li>You may not record, screenshot, or share course content publicly</li>
            <li>Violations may result in account termination and legal action</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>6. User Conduct</h2>
        <p>You agree not to:</p>
        <ul>
            <li>Use the platform for any illegal or unauthorized purpose</li>
            <li>Attempt to gain unauthorized access to our systems</li>
            <li>Upload malicious code or harmful content</li>
            <li>Harass, abuse, or harm other users</li>
            <li>Impersonate others or provide false information</li>
            <li>Violate any applicable laws or regulations</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>7. Certificates</h2>
        <p>Upon successful completion of a course, you may receive a certificate of completion. Certificates:</p>
        <ul>
            <li>Are issued at our discretion based on completion criteria</li>
            <li>Do not represent accredited qualifications unless explicitly stated</li>
            <li>May be revoked if terms violations are discovered</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>8. Disclaimer of Warranties</h2>
        <p>Our platform and courses are provided "as is" without warranties of any kind, either express or implied. We do not guarantee:</p>
        <ul>
            <li>Uninterrupted or error-free service</li>
            <li>Specific learning outcomes or career advancement</li>
            <li>Accuracy or completeness of course content</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>9. Limitation of Liability</h2>
        <p>To the maximum extent permitted by law, DigitalSkeleton shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of our platform.</p>
    </section>

    <section class="my-4">
        <h2>10. Modifications to Terms</h2>
        <p>We reserve the right to modify these Terms and Conditions at any time. Continued use of the platform after changes constitutes acceptance of the modified terms.</p>
    </section>

    <section class="my-4">
        <h2>11. Governing Law</h2>
        <p>These Terms shall be governed by and construed in accordance with the laws of Nigeria, without regard to its conflict of law provisions.</p>
    </section>

    <section class="my-4">
        <h2>12. Contact Information</h2>
        <p>For questions about these Terms and Conditions, contact us at:</p>
        <p><strong>Email:</strong> ceo@digitalskeleton.com.ng</p>
    </section>
</div>'''),
        ('refund', f'''<div class="container my-5">
    <h1 class="mb-4">Refund Policy</h1>
    <p class="text-muted">Last updated: {current_date}</p>

    <section class="my-4">
        <h2>No Refund Policy</h2>
        <p class="lead"><strong>All course purchases are final and non-refundable.</strong></p>
    </section>

    <section class="my-4">
        <h2>1. Policy Overview</h2>
        <p>DigitalSkeleton operates a strict no-refund policy for all course purchases. Once you have completed payment and gained access to a course, you will not be eligible for a refund under any circumstances.</p>
        
        <p>This policy applies to:</p>
        <ul>
            <li>All individual course purchases</li>
            <li>All payment methods (Paystack, Flutterwave, etc.)</li>
            <li>All currencies (NGN, USD, etc.)</li>
            <li>Partial or full course access</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>2. Why We Have This Policy</h2>
        <p>Our no-refund policy exists because:</p>
        <ul>
            <li>Digital course content is delivered immediately upon purchase</li>
            <li>Course materials can be accessed, downloaded, or viewed instantly</li>
            <li>The nature of digital products makes them non-returnable</li>
            <li>We invest significant resources in creating high-quality educational content</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>3. Before You Purchase</h2>
        <p>We strongly encourage you to:</p>
        <ul>
            <li>Carefully review the course description and curriculum</li>
            <li>Check course requirements and prerequisites</li>
            <li>Review any available preview materials or sample lessons</li>
            <li>Ensure the course matches your learning objectives</li>
            <li>Verify that your payment information is correct</li>
        </ul>
        
        <p class="alert alert-warning">
            <i class="bi bi-exclamation-triangle"></i> <strong>Important:</strong> By completing your purchase, you acknowledge that you have read and agree to this no-refund policy.
        </p>
    </section>

    <section class="my-4">
        <h2>4. Exceptions</h2>
        <p>Refunds will only be considered in the following exceptional circumstances:</p>
        <ul>
            <li><strong>Duplicate Payments:</strong> If you accidentally paid for the same course multiple times</li>
            <li><strong>Technical Errors:</strong> If payment was processed but course access was never granted due to a technical error on our end</li>
            <li><strong>Unauthorized Transactions:</strong> If your payment was made fraudulently without your authorization (subject to verification)</li>
        </ul>
        
        <p>To request consideration for these exceptional circumstances, you must contact us within 48 hours of the transaction with supporting evidence.</p>
    </section>

    <section class="my-4">
        <h2>5. Course Access Issues</h2>
        <p>If you experience technical difficulties accessing your purchased course:</p>
        <ul>
            <li>Contact our support team immediately</li>
            <li>We will work to resolve the issue promptly</li>
            <li>Technical issues do not qualify for refunds; we will provide solutions instead</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>6. Chargebacks</h2>
        <p>Initiating a chargeback or payment dispute for a valid course purchase may result in:</p>
        <ul>
            <li>Immediate suspension of your account</li>
            <li>Revocation of course access</li>
            <li>Permanent ban from the platform</li>
            <li>Legal action to recover costs</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>7. Course Updates and Changes</h2>
        <p>We reserve the right to update, modify, or discontinue courses. If a course is discontinued:</p>
        <ul>
            <li>Existing students will retain access to current course materials</li>
            <li>No refunds will be issued</li>
            <li>We may offer access to replacement or updated courses at our discretion</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>8. Contact Us</h2>
        <p>If you have questions about this refund policy or need assistance with a purchase, please contact us at:</p>
        <p><strong>Email:</strong> ceo@digitalskeleton.com.ng</p>
        
        <p class="text-muted">Please note that contacting us does not guarantee a refund, as our policy remains that all sales are final.</p>
    </section>

    <section class="my-4">
        <div class="alert alert-info">
            <h4 class="alert-heading">Summary</h4>
            <p class="mb-0"><strong>All course purchases are final and non-refundable. Please review courses carefully before purchasing.</strong></p>
        </div>
    </section>
</div>''')
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
