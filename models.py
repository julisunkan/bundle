from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from werkzeug.security import generate_password_hash, check_password_hash

class BuildJob(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    app_name = db.Column(db.String(100), nullable=False)
    package_type = db.Column(db.String(20), nullable=False)  # apk, ipa, msix, etc.
    status = db.Column(db.String(20), default='pending')  # pending, building, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    download_path = db.Column(db.String(500))
    manifest_data = db.Column(db.Text)  # JSON string of the app manifest
    
    def __init__(self, id, url, package_type, app_name, status='pending', created_at=None, completed_at=None, error_message=None, download_path=None, manifest_data=None):
        self.id = id
        self.url = url
        self.package_type = package_type
        self.app_name = app_name
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.completed_at = completed_at
        self.error_message = error_message
        self.download_path = download_path
        self.manifest_data = manifest_data
    
    def __repr__(self):
        return f'<BuildJob {self.id}: {self.app_name} ({self.package_type})>'

class AppMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False, unique=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    icon_url = db.Column(db.String(500))
    theme_color = db.Column(db.String(7))  # Hex color
    background_color = db.Column(db.String(7))  # Hex color
    last_scraped = db.Column(db.DateTime, default=datetime.utcnow)
    metadata_json = db.Column(db.Text)  # JSON string of all metadata
    
    def __init__(self, url, title=None, description=None, icon_url=None, theme_color=None, background_color=None, metadata_json=None, last_scraped=None):
        self.url = url
        self.title = title
        self.description = description
        self.icon_url = icon_url
        self.theme_color = theme_color
        self.background_color = background_color
        self.metadata_json = metadata_json
        self.last_scraped = last_scraped or datetime.utcnow()
    
    def __repr__(self):
        return f'<AppMetadata {self.id}: {self.title}>'

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'

class AdminSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_adsense_code = db.Column(db.Text)
    payment_account_name = db.Column(db.String(200))
    payment_bank_name = db.Column(db.String(200))
    payment_account_number = db.Column(db.String(100))
    admin_email = db.Column(db.String(120))
    banner_price_per_day = db.Column(db.Float, default=10.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminSettings {self.id}>'

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    contact_name = db.Column(db.String(200))
    contact_email = db.Column(db.String(120))
    image_path = db.Column(db.String(500))
    days_to_display = db.Column(db.Integer, nullable=False)
    amount_payable = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, active, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    def __init__(self, product_name, product_url, description=None, contact_name=None, 
                 contact_email=None, image_path=None, days_to_display=1, amount_payable=0.0, 
                 status='pending', created_at=None, activated_at=None, expires_at=None):
        self.product_name = product_name
        self.product_url = product_url
        self.description = description
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.image_path = image_path
        self.days_to_display = days_to_display
        self.amount_payable = amount_payable
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.activated_at = activated_at
        self.expires_at = expires_at
    
    def __repr__(self):
        return f'<Advertisement {self.id}: {self.product_name}>'

class Tutorial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)  # HTML content
    order_position = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, title, content, description=None, order_position=0, is_active=True, 
                 created_at=None, updated_at=None):
        self.title = title
        self.content = content
        self.description = description
        self.order_position = order_position
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def __repr__(self):
        return f'<Tutorial {self.id}: {self.title}>'

class TutorialCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    learner_name = db.Column(db.String(200), nullable=False)
    tutorial_ids = db.Column(db.Text)  # JSON string of completed tutorial IDs
    completion_date = db.Column(db.DateTime, default=datetime.utcnow)
    certificate_id = db.Column(db.String(36), unique=True)  # UUID for certificate
    
    def __init__(self, learner_name, tutorial_ids, certificate_id, completion_date=None):
        self.learner_name = learner_name
        self.tutorial_ids = tutorial_ids
        self.certificate_id = certificate_id
        self.completion_date = completion_date or datetime.utcnow()
    
    def __repr__(self):
        return f'<TutorialCompletion {self.id}: {self.learner_name}>'
