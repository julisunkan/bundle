import os
import json
import uuid
from datetime import datetime
from urllib.parse import urlparse

from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, session
from functools import wraps
from app import app, db
from models import BuildJob, AppMetadata, AdminUser, AdminSettings, Advertisement
from services.web_scraper import scrape_website_metadata
from services.package_builder import PackageBuilder
from services.manifest_generator import generate_manifest
from services.pwa_detector import analyze_website_pwa_status
from services.pwa_generator import PWAGenerator
from werkzeug.utils import secure_filename
from datetime import timedelta

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login to access admin panel', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Allowed file extensions for ad uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Context processor to inject settings and ads into all templates
@app.context_processor
def inject_global_data():
    settings = AdminSettings.query.first()
    active_ads = Advertisement.query.filter_by(status='active').filter(
        Advertisement.expires_at > datetime.utcnow()
    ).all() if Advertisement.query.first() else []
    
    return {
        'adsense_code': settings.google_adsense_code if settings else None,
        'active_ads': active_ads
    }

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@app.route('/')
def index():
    # Load SVG icons for display
    android_icon = '<i class="fab fa-android fa-2x"></i>'
    apple_icon = '<i class="fab fa-apple fa-2x"></i>'
    windows_icon = '<i class="fab fa-windows fa-2x"></i>'
    
    return render_template('index.html',
                         android_icon=android_icon,
                         apple_icon=apple_icon,
                         windows_icon=windows_icon)

@app.route('/analyze', methods=['POST'])
def analyze_pwa():
    """Analyze if a website is PWA-ready"""
    url = request.form.get('url', '').strip()
    
    # Validate URL
    if not url:
        return jsonify({'error': 'Please enter a valid URL'}), 400
    
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return jsonify({'error': 'Please enter a valid URL with http:// or https://'}), 400
    except Exception:
        return jsonify({'error': 'Invalid URL format'}), 400
    
    try:
        # Scrape website metadata
        metadata = scrape_website_metadata(url)
        
        # Analyze PWA readiness
        pwa_assessment = analyze_website_pwa_status(url)
        
        # Store metadata if not exists
        existing_metadata = AppMetadata.query.filter_by(url=url).first()
        if not existing_metadata:
            app_metadata = AppMetadata(
                url=url,
                title=metadata.get('title'),
                description=metadata.get('description'),
                icon_url=metadata.get('icon_url'),
                theme_color=metadata.get('theme_color'),
                metadata_json=json.dumps(metadata)
            )
            db.session.add(app_metadata)
            db.session.commit()
        
        return jsonify({
            'metadata': metadata,
            'pwa_assessment': pwa_assessment
        })
        
    except Exception as e:
        app.logger.error(f"PWA analysis failed for {url}: {str(e)}")
        import traceback
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to analyze website: {str(e)}'}), 500

@app.route('/generate-pwa', methods=['POST'])
def generate_pwa():
    """Generate PWA files for a website"""
    url = request.form.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Get existing metadata
        existing_metadata = AppMetadata.query.filter_by(url=url).first()
        if not existing_metadata:
            # Scrape metadata if not exists
            metadata = scrape_website_metadata(url)
            app_metadata = AppMetadata(
                url=url,
                title=metadata.get('title'),
                description=metadata.get('description'),
                icon_url=metadata.get('icon_url'),
                theme_color=metadata.get('theme_color'),
                metadata_json=json.dumps(metadata)
            )
            db.session.add(app_metadata)
            db.session.commit()
        else:
            # Reconstruct metadata from stored data
            metadata = json.loads(existing_metadata.metadata_json)
        
        # Analyze PWA status
        pwa_assessment = analyze_website_pwa_status(url)
        
        # Generate PWA files
        # Create a simple metadata object that PWAGenerator expects
        class MetadataObj:
            def __init__(self, url, metadata_dict):
                self.url = url
                self.title = metadata_dict.get('title', 'Unknown App')
                self.description = metadata_dict.get('description', '')
                self.theme_color = metadata_dict.get('theme_color', '#000000')
                self.background_color = metadata_dict.get('background_color', '#ffffff')
                self.icon_url = metadata_dict.get('icon_url', '')
        
        metadata_obj = MetadataObj(url, metadata)
        pwa_generator = PWAGenerator(metadata_obj, pwa_assessment)
        pwa_files = pwa_generator.generate_pwa_files()
        
        # Create a build job for PWA files
        job_id = str(uuid.uuid4())
        build_job = BuildJob(
            id=job_id,
            url=url,
            package_type='pwa',
            app_name=metadata.get('title', 'Unknown App'),
            status='completed',
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.session.add(build_job)
        db.session.commit()
        
        # Store PWA files in the build job for retrieval
        build_job.manifest_data = json.dumps({
            'pwa_files': pwa_files,
            'pwa_assessment': pwa_assessment,
            'app_name': metadata.get('title', 'Unknown App')
        })
        db.session.commit()
        
        return redirect(url_for('pwa_results', job_id=job_id))
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate PWA files: {str(e)}'}), 500

@app.route('/build', methods=['POST'])
def build_package():
    url = request.form.get('url', '').strip()
    package_type = request.form.get('package_type', 'apk')
    
    # Validate URL
    if not url:
        flash('Please enter a valid URL', 'error')
        return redirect(url_for('index'))
    
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            flash('Please enter a valid URL with http:// or https://', 'error')
            return redirect(url_for('index'))
    except Exception:
        flash('Invalid URL format', 'error')
        return redirect(url_for('index'))
    
    # Check if we already have metadata for this URL
    metadata = AppMetadata.query.filter_by(url=url).first()
    
    if not metadata:
        try:
            # Scrape website metadata
            scraped_data = scrape_website_metadata(url)
            
            metadata = AppMetadata(
                url=url,
                title=scraped_data.get('title', 'Web App'),
                description=scraped_data.get('description', 'Converted web application'),
                icon_url=scraped_data.get('icon_url'),
                theme_color=scraped_data.get('theme_color', '#000000'),
                background_color=scraped_data.get('background_color', '#ffffff'),
                metadata_json=json.dumps(scraped_data)
            )
            db.session.add(metadata)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error scraping metadata: {str(e)}")
            flash('Failed to scrape website metadata. Please check the URL and try again.', 'error')
            return redirect(url_for('index'))
    
    # Create build job and process immediately since builds are fast
    job_id = str(uuid.uuid4())
    build_job = BuildJob(
        id=job_id,
        url=url,
        app_name=metadata.title,
        package_type=package_type,
        status='building',
        created_at=datetime.utcnow()
    )
    db.session.add(build_job)
    db.session.commit()
    
    try:
        # Process build immediately
        manifest_data = generate_manifest(metadata, url)
        build_job.manifest_data = json.dumps(manifest_data)
        
        # Build package
        builder = PackageBuilder()
        if package_type == 'apk':
            package_path = builder.build_apk(metadata, manifest_data, job_id, url)
        elif package_type == 'ipa':
            package_path = builder.build_ipa(metadata, manifest_data, job_id, url)
        elif package_type == 'msix':
            package_path = builder.build_msix(metadata, manifest_data, job_id, url)
        elif package_type == 'appx':
            package_path = builder.build_appx(metadata, manifest_data, job_id, url)
        else:
            raise Exception(f"Unsupported package type: {package_type}")
        
        build_job.download_path = package_path
        build_job.status = 'completed'
        build_job.completed_at = datetime.utcnow()
        db.session.commit()
        
        # Redirect directly to download page since build completed
        return redirect(url_for('download_package', job_id=job_id))
        
    except Exception as e:
        build_job.status = 'failed'
        build_job.error_message = str(e)
        db.session.commit()
        app.logger.error(f"Build failed for job {job_id}: {str(e)}")
        return redirect(url_for('build_progress', job_id=job_id))

@app.route('/build/<job_id>')
def build_progress(job_id):
    job = BuildJob.query.get_or_404(job_id)
    return render_template('build_progress.html', job=job)

@app.route('/api/build-status/<job_id>')
def build_status(job_id):
    job = BuildJob.query.get_or_404(job_id)
    
    # Process the build if it's still pending
    if job.status == 'pending':
        try:
            job.status = 'building'
            db.session.commit()
            
            # Get metadata
            metadata = AppMetadata.query.filter_by(url=job.url).first()
            if not metadata:
                raise Exception("No metadata found for this URL")
            
            # Generate manifest
            manifest_data = generate_manifest(metadata, job.url)
            job.manifest_data = json.dumps(manifest_data)
            
            # Build package
            builder = PackageBuilder()
            if job.package_type == 'apk':
                package_path = builder.build_apk(metadata, manifest_data, job.id, job.url)
            elif job.package_type == 'ipa':
                package_path = builder.build_ipa(metadata, manifest_data, job.id, job.url)
            elif job.package_type == 'msix':
                package_path = builder.build_msix(metadata, manifest_data, job.id, job.url)
            elif job.package_type == 'appx':
                package_path = builder.build_appx(metadata, manifest_data, job.id, job.url)
            else:
                raise Exception(f"Unsupported package type: {job.package_type}")
            
            job.download_path = package_path
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            app.logger.error(f"Build failed for job {job_id}: {str(e)}")
        
        db.session.commit()
    
    return jsonify({
        'status': job.status,
        'error_message': job.error_message,
        'download_url': url_for('download_package', job_id=job.id) if job.status == 'completed' else None
    })

@app.route('/download/<job_id>')
def download_package(job_id):
    job = BuildJob.query.get_or_404(job_id)
    
    if job.status != 'completed' or not job.download_path:
        flash('Package not ready for download', 'error')
        return redirect(url_for('index'))
    
    if not os.path.exists(job.download_path):
        flash('Package file not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('download.html', job=job)

@app.route('/download-file/<job_id>')
def download_file(job_id):
    job = BuildJob.query.get_or_404(job_id)
    
    if job.status != 'completed' or not job.download_path:
        flash('Package not ready for download', 'error')
        return redirect(url_for('index'))
    
    if not os.path.exists(job.download_path):
        flash('Package file not found', 'error')
        return redirect(url_for('index'))
    
    # Generate appropriate filename based on project type
    if job.package_type == 'apk':
        filename = f"{job.app_name.replace(' ', '_')}_android_project.zip"
    elif job.package_type == 'ipa':
        filename = f"{job.app_name.replace(' ', '_')}_ios_project.zip"
    elif job.package_type in ['msix', 'appx']:
        filename = f"{job.app_name.replace(' ', '_')}_windows_project.zip"
    else:
        filename = f"{job.app_name.replace(' ', '_')}_project.zip"
    
    return send_file(job.download_path, as_attachment=True, download_name=filename)

@app.route('/pwa-results/<job_id>')
def pwa_results(job_id):
    """Display PWA generation results"""
    job = BuildJob.query.get_or_404(job_id)
    
    if not job.manifest_data:
        flash('No PWA files found. Please generate them first.', 'error')
        return redirect(url_for('index'))
    
    try:
        job_data = json.loads(job.manifest_data)
        pwa_files = job_data.get('pwa_files', {})
        pwa_assessment = job_data.get('pwa_assessment', {})
        app_name = job_data.get('app_name', 'Unknown App')
    except json.JSONDecodeError:
        flash('Invalid PWA data. Please regenerate files.', 'error')
        return redirect(url_for('index'))
    
    # Calculate PWA score
    pwa_score = pwa_assessment.get('score', 0)
    
    return render_template('pwa_results.html', 
                         pwa_files=pwa_files,
                         pwa_assessment=pwa_assessment,
                         pwa_score=pwa_score,
                         app_name=app_name,
                         job_id=job_id)

@app.route('/download-pwa-file/<job_id>/<filename>')
def download_pwa_file(job_id, filename):
    """Download individual PWA file"""
    job = BuildJob.query.get_or_404(job_id)
    
    if not job.manifest_data:
        flash('PWA files not found.', 'error')
        return redirect(url_for('index'))
    
    try:
        job_data = json.loads(job.manifest_data)
        pwa_files = job_data.get('pwa_files', {})
        
        if filename not in pwa_files:
            flash('File not found.', 'error')
            return redirect(url_for('pwa_results', job_id=job_id))
        
        file_content = pwa_files[filename]
        file_size = round(len(file_content) / 1024, 1)
        
        return render_template('pwa_download.html',
                             filename=filename,
                             file_content=file_content,
                             file_size=file_size,
                             job_id=job_id)
        
    except json.JSONDecodeError:
        flash('Invalid PWA data.', 'error')
        return redirect(url_for('index'))

@app.route('/history')
def build_history():
    jobs = BuildJob.query.order_by(db.desc(BuildJob.created_at)).limit(50).all()
    return render_template('history.html', jobs=jobs)

# Footer Pages
@app.route('/documentation')
def documentation():
    """Documentation page"""
    return render_template('documentation.html')

@app.route('/api-reference')
def api_reference():
    """API Reference page"""
    return render_template('api_reference.html')

@app.route('/privacy')
def privacy():
    """Privacy Policy page"""
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    """Terms of Service page"""
    return render_template('terms.html')

@app.route('/support')
def support():
    """Support page"""
    return render_template('support.html')

# PWA Routes
@app.route('/manifest.json')
def serve_manifest():
    """Serve PWA manifest file"""
    return send_file('static/manifest.json', mimetype='application/json')

@app.route('/sw.js')
def serve_service_worker():
    """Serve service worker file"""
    return send_file('static/sw.js', mimetype='application/javascript')

@app.route('/api/sync-jobs', methods=['POST'])
def sync_jobs():
    """Background sync endpoint for PWA"""
    try:
        # Check for any pending jobs and update their status
        pending_jobs = BuildJob.query.filter_by(status='pending').all()
        for job in pending_jobs:
            # Simulate checking job status (in real app, this would check actual build status)
            if job.created_at:
                # For demo purposes, mark as completed after creation
                job.status = 'completed'
        
        db.session.commit()
        return jsonify({'status': 'success', 'synced_jobs': len(pending_jobs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = AdminUser.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    settings = AdminSettings.query.first()
    pending_ads = Advertisement.query.filter_by(status='pending').count()
    active_ads = Advertisement.query.filter_by(status='active').count()
    total_ads = Advertisement.query.count()
    
    return render_template('admin/dashboard.html', 
                         settings=settings,
                         pending_ads=pending_ads,
                         active_ads=active_ads,
                         total_ads=total_ads)

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """Manage admin settings"""
    settings = AdminSettings.query.first()
    if not settings:
        settings = AdminSettings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        settings.google_adsense_code = request.form.get('google_adsense_code', '')
        settings.payment_account_name = request.form.get('payment_account_name', '')
        settings.payment_bank_name = request.form.get('payment_bank_name', '')
        settings.payment_account_number = request.form.get('payment_account_number', '')
        settings.admin_email = request.form.get('admin_email', '')
        settings.banner_price_per_day = float(request.form.get('banner_price_per_day', 10.0))
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    return render_template('admin/settings.html', settings=settings)

@app.route('/admin/ads')
@admin_required
def admin_ads():
    """Manage advertisements"""
    ads = Advertisement.query.order_by(Advertisement.created_at.desc()).all()
    return render_template('admin/ads.html', ads=ads)

@app.route('/admin/ads/<int:ad_id>/activate', methods=['POST'])
@admin_required
def activate_ad(ad_id):
    """Activate an advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    ad.status = 'active'
    ad.activated_at = datetime.utcnow()
    ad.expires_at = datetime.utcnow() + timedelta(days=ad.days_to_display)
    db.session.commit()
    flash(f'Advertisement "{ad.product_name}" activated successfully!', 'success')
    return redirect(url_for('admin_ads'))

@app.route('/admin/ads/<int:ad_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_ad(ad_id):
    """Deactivate an advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    ad.status = 'expired'
    db.session.commit()
    flash(f'Advertisement "{ad.product_name}" deactivated!', 'success')
    return redirect(url_for('admin_ads'))

@app.route('/admin/ads/<int:ad_id>/delete', methods=['POST'])
@admin_required
def delete_ad(ad_id):
    """Delete an advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    if ad.image_path and os.path.exists(ad.image_path):
        os.remove(ad.image_path)
    db.session.delete(ad)
    db.session.commit()
    flash('Advertisement deleted!', 'success')
    return redirect(url_for('admin_ads'))

# Guest Ad Placement Routes
@app.route('/place-advert', methods=['GET', 'POST'])
def place_advert():
    """Guest ad placement page"""
    settings = AdminSettings.query.first()
    if not settings:
        # Create default settings if none exist
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
    
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_url = request.form.get('product_url')
        description = request.form.get('description')
        contact_name = request.form.get('contact_name')
        contact_email = request.form.get('contact_email')
        days_to_display = int(request.form.get('days_to_display', 1))
        
        # Calculate amount
        amount_payable = settings.banner_price_per_day * days_to_display
        
        # Handle file upload
        image_path = None
        if 'ad_file' in request.files:
            file = request.files['ad_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{uuid.uuid4()}_{filename}"
                upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'ads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                image_path = file_path
        
        # Create advertisement
        ad = Advertisement(
            product_name=product_name,
            product_url=product_url,
            description=description,
            contact_name=contact_name,
            contact_email=contact_email,
            image_path=image_path,
            days_to_display=days_to_display,
            amount_payable=amount_payable,
            status='pending'
        )
        db.session.add(ad)
        db.session.commit()
        
        return redirect(url_for('ad_payment_details', ad_id=ad.id))
    
    return render_template('place_advert.html', settings=settings)

@app.route('/advert/payment/<int:ad_id>')
def ad_payment_details(ad_id):
    """Show payment details for advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    settings = AdminSettings.query.first()
    return render_template('ad_payment.html', ad=ad, settings=settings)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
