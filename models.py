from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean

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
