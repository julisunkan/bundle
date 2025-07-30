from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean

class BuildJob(db.Model):
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)
    app_name = Column(String(100), nullable=False)
    package_type = Column(String(20), nullable=False)  # apk, ipa, msix, etc.
    status = Column(String(20), default='pending')  # pending, building, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    download_path = Column(String(500))
    manifest_data = Column(Text)  # JSON string of the app manifest
    
    def __repr__(self):
        return f'<BuildJob {self.id}: {self.app_name} ({self.package_type})>'

class AppMetadata(db.Model):
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False, unique=True)
    title = Column(String(200))
    description = Column(Text)
    icon_url = Column(String(500))
    theme_color = Column(String(7))  # Hex color
    background_color = Column(String(7))  # Hex color
    last_scraped = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AppMetadata {self.id}: {self.title}>'
