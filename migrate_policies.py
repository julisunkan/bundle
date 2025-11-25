
from app import app
from models import db, Policy
from datetime import datetime

def migrate_policies():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Privacy Policy
        privacy_content = """
<div class="container my-5">
    <h1 class="mb-4">Privacy Policy</h1>
    <p class="text-muted">Last updated: November 25, 2025</p>

    <section class="my-4">
        <h2>1. Information We Collect</h2>
        <p>We collect information that you provide directly to us, including:</p>
        <ul>
            <li>Name and email address when you register</li>
            <li>Payment information processed through our payment gateways (Paystack and Flutterwave)</li>
            <li>Course progress, quiz results, and assignment submissions</li>
            <li>Device and usage information when you access our platform</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>2. How We Use Your Information</h2>
        <p>We use the information we collect to:</p>
        <ul>
            <li>Provide, maintain, and improve our courses and services</li>
            <li>Process your payments and send receipts</li>
            <li>Send you course updates and important notifications</li>
            <li>Generate certificates upon course completion</li>
            <li>Respond to your comments and questions</li>
            <li>Protect against fraudulent or illegal activity</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>3. Information Sharing</h2>
        <p>We do not sell or share your personal information with third parties except:</p>
        <ul>
            <li>With payment processors (Paystack and Flutterwave) to complete transactions</li>
            <li>When required by law or to protect our rights</li>
            <li>With your consent or at your direction</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>4. Data Security</h2>
        <p>We implement appropriate security measures to protect your personal information. However, no method of transmission over the Internet is 100% secure, and we cannot guarantee absolute security.</p>
    </section>

    <section class="my-4">
        <h2>5. Your Rights</h2>
        <p>You have the right to:</p>
        <ul>
            <li>Access and update your personal information</li>
            <li>Request deletion of your account and data</li>
            <li>Opt-out of marketing communications</li>
            <li>Request a copy of your data</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>6. Cookies</h2>
        <p>We use cookies and similar technologies to maintain your session, remember your preferences (like currency selection and dark mode), and analyze site usage.</p>
    </section>

    <section class="my-4">
        <h2>7. Changes to Privacy Policy</h2>
        <p>We may update this privacy policy from time to time. We will notify you of any changes by posting the new policy on this page.</p>
    </section>

    <section class="my-4">
        <h2>8. Contact Us</h2>
        <p>If you have questions about this privacy policy, please contact us at:</p>
        <p><strong>Email:</strong> privacy@coursehub.com</p>
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
        <p>By accessing and using CourseHub, you accept and agree to be bound by these Terms and Conditions. If you do not agree to these terms, please do not use our platform.</p>
    </section>

    <section class="my-4">
        <h2>2. User Accounts</h2>
        <ul>
            <li>You must provide accurate and complete information when registering</li>
            <li>You are responsible for maintaining the confidentiality of your account credentials</li>
            <li>You must be at least 18 years old to create an account</li>
            <li>One account per user; multiple accounts are not permitted</li>
            <li>You are responsible for all activities under your account</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>3. Course Access and Content</h2>
        <ul>
            <li>Course access is granted upon successful payment</li>
            <li>All course content is for personal, non-commercial use only</li>
            <li>You may not share, redistribute, or resell course materials</li>
            <li>We reserve the right to update or modify course content</li>
            <li>Course access is lifetime unless otherwise stated</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>4. Payments and Pricing</h2>
        <ul>
            <li>All prices are listed in Nigerian Naira (NGN) and US Dollars (USD)</li>
            <li>Payments are processed through Paystack or Flutterwave</li>
            <li>All sales are final unless stated in our Refund Policy</li>
            <li>We reserve the right to change prices at any time</li>
            <li>Promotional prices are subject to availability and may expire</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>5. Intellectual Property</h2>
        <p>All content, including videos, quizzes, assignments, and course materials, are the intellectual property of CourseHub or its content creators. Unauthorized use, reproduction, or distribution is strictly prohibited.</p>
    </section>

    <section class="my-4">
        <h2>6. User Conduct</h2>
        <p>You agree not to:</p>
        <ul>
            <li>Use the platform for any illegal or unauthorized purpose</li>
            <li>Attempt to gain unauthorized access to any part of the platform</li>
            <li>Upload malicious code or files</li>
            <li>Harass, abuse, or harm other users</li>
            <li>Impersonate another person or entity</li>
            <li>Share assignment answers or quiz solutions with others</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>7. Certificates</h2>
        <ul>
            <li>Certificates are issued upon successful course completion</li>
            <li>You must complete all modules, quizzes, and assignments</li>
            <li>Certificates are for personal use and verification purposes</li>
            <li>We reserve the right to revoke certificates if terms are violated</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>8. Limitation of Liability</h2>
        <p>CourseHub is provided "as is" without warranties of any kind. We are not liable for any damages arising from your use of the platform, including but not limited to loss of data, profits, or business opportunities.</p>
    </section>

    <section class="my-4">
        <h2>9. Account Termination</h2>
        <p>We reserve the right to suspend or terminate your account at any time for violation of these terms, fraudulent activity, or any other reason at our discretion.</p>
    </section>

    <section class="my-4">
        <h2>10. Changes to Terms</h2>
        <p>We may modify these terms at any time. Continued use of the platform after changes constitutes acceptance of the modified terms.</p>
    </section>

    <section class="my-4">
        <h2>11. Governing Law</h2>
        <p>These terms are governed by the laws of Nigeria. Any disputes will be resolved in the courts of Nigeria.</p>
    </section>

    <section class="my-4">
        <h2>12. Contact Information</h2>
        <p>For questions about these terms, contact us at:</p>
        <p><strong>Email:</strong> support@coursehub.com</p>
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
        <p>We offer a 7-day money-back guarantee on all course purchases. If you are not satisfied with your course for any reason, you may request a full refund within 7 days of purchase.</p>
    </section>

    <section class="my-4">
        <h2>2. Refund Eligibility</h2>
        <p>To be eligible for a refund, you must meet the following conditions:</p>
        <ul>
            <li>Request must be made within 7 days of the original purchase date</li>
            <li>You must not have completed more than 30% of the course content</li>
            <li>You must not have downloaded the certificate</li>
            <li>You must provide a valid reason for the refund request</li>
            <li>No previous refunds have been requested for the same course</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>3. Non-Refundable Situations</h2>
        <p>Refunds will not be granted in the following cases:</p>
        <ul>
            <li>Request made after 7 days from purchase</li>
            <li>More than 30% of course content has been accessed</li>
            <li>Certificate has been downloaded</li>
            <li>Course access was obtained through a promotional code or discount</li>
            <li>Violation of our Terms & Conditions</li>
            <li>Multiple refund requests from the same user</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>4. How to Request a Refund</h2>
        <p>To request a refund, please follow these steps:</p>
        <ol>
            <li>Send an email to <strong>refunds@coursehub.com</strong></li>
            <li>Include your order/transaction reference number</li>
            <li>Provide the course name and purchase date</li>
            <li>Explain the reason for your refund request</li>
        </ol>
        <p>Our team will review your request and respond within 3-5 business days.</p>
    </section>

    <section class="my-4">
        <h2>5. Refund Processing Time</h2>
        <p>Once your refund is approved:</p>
        <ul>
            <li>Paystack refunds: 5-10 business days to your original payment method</li>
            <li>Flutterwave refunds: 7-14 business days to your original payment method</li>
            <li>You will receive an email confirmation when the refund is processed</li>
            <li>Your course access will be immediately revoked</li>
        </ul>
    </section>

    <section class="my-4">
        <h2>6. Partial Refunds</h2>
        <p>Partial refunds may be offered in exceptional circumstances, such as:</p>
        <ul>
            <li>Technical issues preventing course access (if not resolved within 48 hours)</li>
            <li>Significant content quality issues</li>
            <li>Course content does not match description</li>
        </ul>
        <p>Partial refund amounts are determined on a case-by-case basis.</p>
    </section>

    <section class="my-4">
        <h2>7. Currency Exchange</h2>
        <p>Refunds will be issued in the same currency used for the original purchase. Exchange rate fluctuations between purchase and refund are not our responsibility.</p>
    </section>

    <section class="my-4">
        <h2>8. Disputed Charges</h2>
        <p>If you dispute a charge with your bank or payment provider without contacting us first, we reserve the right to permanently ban your account and deny future purchases.</p>
    </section>

    <section class="my-4">
        <h2>9. Policy Changes</h2>
        <p>We reserve the right to modify this refund policy at any time. Changes will be effective immediately upon posting on this page.</p>
    </section>

    <section class="my-4">
        <h2>10. Contact Us</h2>
        <p>For refund inquiries or questions about this policy, please contact:</p>
        <p><strong>Email:</strong> refunds@coursehub.com<br>
        <strong>Response Time:</strong> Within 24-48 hours</p>
    </section>

    <div class="alert alert-info mt-5">
        <i class="bi bi-info-circle"></i> <strong>Note:</strong> This refund policy applies only to course purchases. Other services or products may have different terms.
    </div>
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
