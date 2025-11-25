from app import app, db
from models import Policy
from datetime import datetime

def migrate_policies():
    with app.app_context():
        # Privacy Policy
        privacy_content = """
<div class="container my-5">
    <h1 class="mb-4">Privacy Policy</h1>
    <p class="text-muted">Last updated: November 25, 2025</p>

    <section class="my-4">
        <h2>1. Information We Collect</h2>
        <p>We collect information you provide directly to us when you create an account, enroll in courses, or contact us for support.</p>
    </section>

    <section class="my-4">
        <h2>2. How We Use Your Information</h2>
        <p>We use the information we collect to provide, maintain, and improve our services, process transactions, and communicate with you.</p>
    </section>

    <section class="my-4">
        <h2>3. Information Sharing</h2>
        <p>We do not sell your personal information. We may share your information with service providers who assist in our operations.</p>
    </section>

    <section class="my-4">
        <h2>4. Data Security</h2>
        <p>We implement appropriate security measures to protect your personal information from unauthorized access or disclosure.</p>
    </section>

    <section class="my-4">
        <h2>5. Contact Us</h2>
        <p>If you have questions about this Privacy Policy, please contact us at privacy@coursehub.com</p>
    </section>
</div>
"""

        privacy = Policy.query.filter_by(policy_type='privacy').first()
        if not privacy:
            privacy = Policy(policy_type='privacy', content=privacy_content)
            db.session.add(privacy)
            print("Privacy policy created")

        # Terms & Conditions
        terms_content = """
<div class="container my-5">
    <h1 class="mb-4">Terms & Conditions</h1>
    <p class="text-muted">Last updated: November 25, 2025</p>

    <section class="my-4">
        <h2>1. Acceptance of Terms</h2>
        <p>By accessing and using this platform, you accept and agree to be bound by these Terms and Conditions.</p>
    </section>

    <section class="my-4">
        <h2>2. User Accounts</h2>
        <p>You are responsible for maintaining the confidentiality of your account credentials.</p>
    </section>

    <section class="my-4">
        <h2>3. Course Access</h2>
        <p>Upon successful payment, you will receive lifetime access to the purchased course content.</p>
    </section>

    <section class="my-4">
        <h2>4. Intellectual Property</h2>
        <p>All course materials are protected by copyright and may not be reproduced without permission.</p>
    </section>

    <section class="my-4">
        <h2>5. Contact Information</h2>
        <p>For questions about these terms, contact us at support@coursehub.com</p>
    </section>
</div>
"""

        terms = Policy.query.filter_by(policy_type='terms').first()
        if not terms:
            terms = Policy(policy_type='terms', content=terms_content)
            db.session.add(terms)
            print("Terms & Conditions created")

        # Refund Policy
        refund_content = """
<div class="container my-5">
    <h1 class="mb-4">Refund Policy</h1>
    <p class="text-muted">Last updated: November 25, 2025</p>

    <section class="my-4">
        <h2>1. 7-Day Money-Back Guarantee</h2>
        <p>We offer a 7-day money-back guarantee on all course purchases.</p>
    </section>

    <section class="my-4">
        <h2>2. Refund Eligibility</h2>
        <p>To be eligible for a refund:</p>
        <ul>
            <li>Request must be made within 7 days of purchase</li>
            <li>You must not have completed more than 30% of the course</li>
            <li>No certificate has been downloaded</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>3. How to Request a Refund</h2>
        <p>Contact us at refunds@coursehub.com with your order details.</p>
    </section>

    <section class="my-4">
        <h2>4. Processing Time</h2>
        <p>Refunds are processed within 5-7 business days.</p>
    </section>
</div>
"""

        refund = Policy.query.filter_by(policy_type='refund').first()
        if not refund:
            refund = Policy(policy_type='refund', content=refund_content)
            db.session.add(refund)
            print("Refund policy created")

        db.session.commit()
        print("All policies migrated successfully!")

if __name__ == '__main__':
    migrate_policies()