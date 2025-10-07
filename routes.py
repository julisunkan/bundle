import os
import json
import uuid
import shutil
from datetime import datetime
from urllib.parse import urlparse

from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, session
from functools import wraps
from sqlalchemy import desc
from app import app, db
from models import BuildJob, AppMetadata, AdminUser, AdminSettings, Advertisement, Tutorial, TutorialCompletion
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
        try:
            if 'admin_id' not in session:
                flash('Please login to access admin panel', 'error')
                return redirect(url_for('admin_login'))

            # Verify admin user still exists
            admin = AdminUser.query.get(session['admin_id'])
            if not admin:
                session.pop('admin_id', None)
                session.pop('admin_username', None)
                flash('Admin session expired. Please login again.', 'error')
                return redirect(url_for('admin_login'))

            return f(*args, **kwargs)
        except Exception as e:
            app.logger.error(f"Admin authentication error: {str(e)}")
            flash('Authentication error. Please login again.', 'error')
            return redirect(url_for('admin_login'))
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

@app.route('/ads.txt')
def serve_ads_txt():
    """Serve Google AdSense ads.txt file"""
    settings = AdminSettings.query.first()
    if settings and settings.ads_txt_content:
        from flask import Response
        return Response(settings.ads_txt_content, mimetype='text/plain')
    return Response('', mimetype='text/plain', status=404)

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

# Tutorial Routes (Guest Access)
@app.route('/tutorials')
def tutorials_list():
    """List all active tutorials for guests"""
    tutorials = Tutorial.query.filter_by(is_active=True).order_by(Tutorial.order_position, Tutorial.created_at).all()
    return render_template('tutorials/list.html', tutorials=tutorials)

@app.route('/tutorial/<int:tutorial_id>')
def view_tutorial(tutorial_id):
    """View individual tutorial"""
    tutorial = Tutorial.query.filter_by(id=tutorial_id, is_active=True).first_or_404()
    all_tutorials = Tutorial.query.filter_by(is_active=True).order_by(Tutorial.order_position, Tutorial.created_at).all()

    # Find current position
    current_index = 0
    for i, t in enumerate(all_tutorials):
        if t.id == tutorial_id:
            current_index = i
            break

    next_tutorial = all_tutorials[current_index + 1] if current_index < len(all_tutorials) - 1 else None
    prev_tutorial = all_tutorials[current_index - 1] if current_index > 0 else None

    return render_template('tutorials/view.html', 
                         tutorial=tutorial, 
                         next_tutorial=next_tutorial,
                         prev_tutorial=prev_tutorial,
                         current_index=current_index + 1,
                         total_tutorials=len(all_tutorials))

@app.route('/tutorial-complete', methods=['GET', 'POST'])
def complete_tutorials():
    """Complete tutorials and generate certificate"""
    if request.method == 'POST':
        learner_name = request.form.get('learner_name', '').strip()
        if not learner_name:
            flash('Please enter your name to generate the certificate.', 'error')
            return redirect(url_for('complete_tutorials'))

        # Get all active tutorials
        tutorials = Tutorial.query.filter_by(is_active=True).all()
        tutorial_ids = [str(t.id) for t in tutorials]

        # Generate certificate ID
        certificate_id = str(uuid.uuid4())

        # Save completion record
        completion = TutorialCompletion(
            learner_name=learner_name,
            tutorial_ids=json.dumps(tutorial_ids),
            certificate_id=certificate_id
        )
        db.session.add(completion)
        db.session.commit()

        return redirect(url_for('view_certificate', certificate_id=certificate_id))

    tutorials = Tutorial.query.filter_by(is_active=True).order_by(Tutorial.order_position, Tutorial.created_at).all()
    return render_template('tutorials/complete.html', tutorials=tutorials)

@app.route('/certificate/<certificate_id>')
def view_certificate(certificate_id):
    """View generated certificate"""
    completion = TutorialCompletion.query.filter_by(certificate_id=certificate_id).first_or_404()
    tutorial_ids = json.loads(completion.tutorial_ids)
    tutorials = Tutorial.query.filter(Tutorial.id.in_(tutorial_ids)).all()

    return render_template('tutorials/certificate.html', 
                         completion=completion, 
                         tutorials=tutorials)

# Admin Routes
@app.route('/babaj/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page - auto login without credentials"""
    # Get the first admin user (admin should already exist from app initialization)
    admin = AdminUser.query.first()
    if not admin:
        # This should not happen if app.py initialization worked correctly
        app.logger.warning("No admin user found during login - this should not happen")
        flash('Admin user not found. Please contact support.', 'error')
        return redirect(url_for('index'))

    # Automatically log in the user
    session['admin_id'] = admin.id
    session['admin_username'] = admin.username
    flash('Automatically logged in as admin!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/babaj/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/babaj/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    try:
        settings = AdminSettings.query.first()
        pending_ads = Advertisement.query.filter_by(status='pending').count()
        active_ads = Advertisement.query.filter_by(status='active').count()
        total_ads = Advertisement.query.count()
        total_tutorials = Tutorial.query.count()
        active_tutorials = Tutorial.query.filter_by(is_active=True).count()
        total_completions = TutorialCompletion.query.count()

        return render_template('admin/dashboard.html', 
                             settings=settings,
                             pending_ads=pending_ads,
                             active_ads=active_ads,
                             total_ads=total_ads,
                             total_tutorials=total_tutorials,
                             active_tutorials=active_tutorials,
                             total_completions=total_completions)
    except Exception as e:
        app.logger.error(f"Admin dashboard error: {str(e)}")
        flash('Error loading dashboard. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/babaj/settings', methods=['GET', 'POST'])
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
        settings.ads_txt_content = request.form.get('ads_txt_content', '')
        settings.payment_account_name = request.form.get('payment_account_name', '')
        settings.payment_bank_name = request.form.get('payment_bank_name', '')
        settings.payment_account_number = request.form.get('payment_account_number', '')
        settings.admin_email = request.form.get('admin_email', '')
        settings.banner_price_per_day = float(request.form.get('banner_price_per_day', 10.0))

        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))

    return render_template('admin/settings.html', settings=settings)

@app.route('/babaj/ads')
@admin_required
def admin_ads():
    """Manage advertisements"""
    ads = Advertisement.query.order_by(desc(Advertisement.created_at)).all()
    return render_template('admin/ads.html', ads=ads)

@app.route('/babaj/ads/<int:ad_id>/activate', methods=['POST'])
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

@app.route('/babaj/ads/<int:ad_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_ad(ad_id):
    """Deactivate an advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    ad.status = 'expired'
    db.session.commit()
    flash(f'Advertisement "{ad.product_name}" deactivated!', 'success')
    return redirect(url_for('admin_ads'))

@app.route('/babaj/ads/<int:ad_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_ad(ad_id):
    """Edit an advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)

    if request.method == 'POST':
        ad.product_name = request.form.get('product_name')
        ad.product_url = request.form.get('product_url')
        ad.description = request.form.get('description')
        ad.contact_name = request.form.get('contact_name')
        ad.contact_email = request.form.get('contact_email')
        ad.image_path = request.form.get('ad_image_url')
        ad.days_to_display = int(request.form.get('days_to_display', 1))

        # Recalculate amount if days changed
        settings = AdminSettings.query.first()
        if settings:
            ad.amount_payable = settings.banner_price_per_day * ad.days_to_display

        db.session.commit()
        flash(f'Advertisement "{ad.product_name}" updated successfully!', 'success')
        return redirect(url_for('admin_ads'))

    return render_template('admin/edit_ad.html', ad=ad)

@app.route('/babaj/ads/<int:ad_id>/delete', methods=['POST'])
@admin_required
def delete_ad(ad_id):
    """Delete an advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    flash('Advertisement deleted!', 'success')
    return redirect(url_for('admin_ads'))

# Admin Tutorial Management Routes
@app.route('/babaj/tutorials')
@admin_required
def admin_tutorials():
    """Manage tutorials"""
    tutorials = Tutorial.query.order_by(Tutorial.order_position, Tutorial.created_at).all()
    return render_template('admin/tutorials.html', tutorials=tutorials)

@app.route('/babaj/tutorials/add', methods=['GET', 'POST'])
@admin_required
def add_tutorial():
    """Add new tutorial"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        content = request.form.get('content')
        order_position = int(request.form.get('order_position', 0))
        is_active = request.form.get('is_active') == 'on'

        tutorial = Tutorial(
            title=title,
            description=description,
            content=content,
            order_position=order_position,
            is_active=is_active
        )
        db.session.add(tutorial)
        db.session.commit()
        flash(f'Tutorial "{title}" added successfully!', 'success')
        return redirect(url_for('admin_tutorials'))

    return render_template('admin/add_tutorial.html')

@app.route('/babaj/tutorials/<int:tutorial_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_tutorial(tutorial_id):
    """Edit tutorial"""
    tutorial = Tutorial.query.get_or_404(tutorial_id)

    if request.method == 'POST':
        tutorial.title = request.form.get('title')
        tutorial.description = request.form.get('description')
        tutorial.content = request.form.get('content')
        tutorial.order_position = int(request.form.get('order_position', 0))
        tutorial.is_active = request.form.get('is_active') == 'on'
        tutorial.updated_at = datetime.utcnow()

        db.session.commit()
        flash(f'Tutorial "{tutorial.title}" updated successfully!', 'success')
        return redirect(url_for('admin_tutorials'))

    return render_template('admin/edit_tutorial.html', tutorial=tutorial)

@app.route('/babaj/tutorials/<int:tutorial_id>/delete', methods=['POST'])
@admin_required
def delete_tutorial(tutorial_id):
    """Delete tutorial"""
    tutorial = Tutorial.query.get_or_404(tutorial_id)
    db.session.delete(tutorial)
    db.session.commit()
    flash('Tutorial deleted!', 'success')
    return redirect(url_for('admin_tutorials'))

@app.route('/babaj/tutorial-completions')
@admin_required
def admin_tutorial_completions():
    """View tutorial completions"""
    completions = TutorialCompletion.query.order_by(desc(TutorialCompletion.completion_date)).all()
    return render_template('admin/tutorial_completions.html', completions=completions)

@app.route('/babaj/backup-restore')
@admin_required
def admin_backup_restore():
    """Admin backup and restore page"""
    return render_template('admin/backup_restore.html')

@app.route('/babaj/create-backup', methods=['POST'])
@admin_required
def create_backup():
    """Create a full system backup"""
    try:
        import zipfile
        import shutil
        from datetime import datetime

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'digitalskeleton_backup_{timestamp}.zip'
        backup_path = os.path.join(app.config['UPLOAD_FOLDER'], backup_filename)

        # Create backup data directory
        backup_data = {
            'admin_users': [],
            'admin_settings': [],
            'advertisements': [],
            'tutorials': [],
            'tutorial_completions': [],
            'app_metadata': [],
            'build_jobs': []
        }

        # Export database records
        admin_users = AdminUser.query.all()
        for user in admin_users:
            backup_data['admin_users'].append({
                'id': user.id,
                'username': user.username,
                'password_hash': user.password_hash,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })

        settings = AdminSettings.query.all()
        for setting in settings:
            backup_data['admin_settings'].append({
                'id': setting.id,
                'google_adsense_code': setting.google_adsense_code,
                'payment_account_name': setting.payment_account_name,
                'payment_bank_name': setting.payment_bank_name,
                'payment_account_number': setting.payment_account_number,
                'admin_email': setting.admin_email,
                'banner_price_per_day': setting.banner_price_per_day,
                'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
            })

        ads = Advertisement.query.all()
        for ad in ads:
            backup_data['advertisements'].append({
                'id': ad.id,
                'product_name': ad.product_name,
                'product_url': ad.product_url,
                'description': ad.description,
                'contact_name': ad.contact_name,
                'contact_email': ad.contact_email,
                'image_path': ad.image_path,
                'days_to_display': ad.days_to_display,
                'amount_payable': ad.amount_payable,
                'status': ad.status,
                'created_at': ad.created_at.isoformat() if ad.created_at else None,
                'activated_at': ad.activated_at.isoformat() if ad.activated_at else None,
                'expires_at': ad.expires_at.isoformat() if ad.expires_at else None
            })

        tutorials = Tutorial.query.all()
        for tutorial in tutorials:
            backup_data['tutorials'].append({
                'id': tutorial.id,
                'title': tutorial.title,
                'description': tutorial.description,
                'content': tutorial.content,
                'order_position': tutorial.order_position,
                'is_active': tutorial.is_active,
                'created_at': tutorial.created_at.isoformat() if tutorial.created_at else None,
                'updated_at': tutorial.updated_at.isoformat() if tutorial.updated_at else None
            })

        completions = TutorialCompletion.query.all()
        for completion in completions:
            backup_data['tutorial_completions'].append({
                'id': completion.id,
                'learner_name': completion.learner_name,
                'tutorial_ids': completion.tutorial_ids,
                'completion_date': completion.completion_date.isoformat() if completion.completion_date else None,
                'certificate_id': completion.certificate_id
            })

        metadata_records = AppMetadata.query.all()
        for metadata in metadata_records:
            backup_data['app_metadata'].append({
                'id': metadata.id,
                'url': metadata.url,
                'title': metadata.title,
                'description': metadata.description,
                'icon_url': metadata.icon_url,
                'theme_color': metadata.theme_color,
                'background_color': metadata.background_color,
                'last_scraped': metadata.last_scraped.isoformat() if metadata.last_scraped else None,
                'metadata_json': metadata.metadata_json
            })

        jobs = BuildJob.query.all()
        for job in jobs:
            backup_data['build_jobs'].append({
                'id': job.id,
                'url': job.url,
                'app_name': job.app_name,
                'package_type': job.package_type,
                'status': job.status,
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'error_message': job.error_message,
                'download_path': job.download_path,
                'manifest_data': job.manifest_data
            })

        # Create zip file with backup
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add database backup as JSON
            backup_json = json.dumps(backup_data, indent=2)
            zipf.writestr('database_backup.json', backup_json)

            # Add generated packages directory if it exists
            if os.path.exists(app.config['UPLOAD_FOLDER']):
                for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
                    for file in files:
                        if file != backup_filename:  # Don't include the backup file itself
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, app.config['UPLOAD_FOLDER'])
                            zipf.write(file_path, f'generated_packages/{arcname}')

            # Add static files directory
            static_dir = os.path.join(os.getcwd(), 'static')
            if os.path.exists(static_dir):
                for root, dirs, files in os.walk(static_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, static_dir)
                        zipf.write(file_path, f'static/{arcname}')

            # Add templates directory
            templates_dir = os.path.join(os.getcwd(), 'templates')
            if os.path.exists(templates_dir):
                for root, dirs, files in os.walk(templates_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, templates_dir)
                        zipf.write(file_path, f'templates/{arcname}')

        flash(f'Backup created successfully: {backup_filename}', 'success')
        return redirect(url_for('download_backup', filename=backup_filename))

    except Exception as e:
        app.logger.error(f"Backup creation failed: {str(e)}")
        flash(f'Backup creation failed: {str(e)}', 'error')
        return redirect(url_for('admin_backup_restore'))

@app.route('/babaj/download-backup/<filename>')
@admin_required
def download_backup(filename):
    """Download backup file"""
    backup_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(backup_path):
        flash('Backup file not found', 'error')
        return redirect(url_for('admin_backup_restore'))

    return send_file(backup_path, as_attachment=True, download_name=filename)

@app.route('/babaj/file-manager')
@admin_required
def admin_file_manager():
    """Admin file management page"""
    try:
        files_info = []
        total_size = 0

        # Scan generated_packages directory
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        relative_path = os.path.relpath(file_path, app.config['UPLOAD_FOLDER'])
                        file_size = stat.st_size
                        total_size += file_size

                        # Determine file type
                        file_type = 'other'
                        if file.endswith('.zip'):
                            file_type = 'package'
                        elif file.endswith(('.json', '.html', '.js', '.css')):
                            file_type = 'pwa'
                        elif file.endswith(('.txt', '.md')):
                            file_type = 'documentation'

                        files_info.append({
                            'name': file,
                            'relative_path': relative_path,
                            'full_path': file_path,
                            'size': file_size,
                            'size_mb': round(file_size / (1024 * 1024), 2),
                            'modified': datetime.fromtimestamp(stat.st_mtime),
                            'type': file_type
                        })
                    except (OSError, IOError):
                        continue

        # Sort files by modification date (newest first)
        files_info.sort(key=lambda x: x['modified'], reverse=True)

        # Get database statistics
        total_jobs = BuildJob.query.count()
        completed_jobs = BuildJob.query.filter_by(status='completed').count()
        total_metadata = AppMetadata.query.count()
        total_certificates = TutorialCompletion.query.count()

        return render_template('admin/file_manager.html', 
                             files=files_info,
                             total_files=len(files_info),
                             total_size_mb=round(total_size / (1024 * 1024), 2),
                             total_jobs=total_jobs,
                             completed_jobs=completed_jobs,
                             total_metadata=total_metadata,
                             total_certificates=total_certificates)

    except Exception as e:
        app.logger.error(f"File manager error: {str(e)}")
        flash('Error loading file manager. Please try again.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/babaj/delete-file', methods=['POST'])
@admin_required
def admin_delete_file():
    """Delete a specific file"""
    try:
        relative_path = request.form.get('file_path')
        if not relative_path:
            flash('No file specified for deletion.', 'error')
            return redirect(url_for('admin_file_manager'))

        # Security check - ensure file is within upload folder
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], relative_path)
        if not full_path.startswith(app.config['UPLOAD_FOLDER']):
            flash('Invalid file path.', 'error')
            return redirect(url_for('admin_file_manager'))

        if os.path.exists(full_path):
            os.remove(full_path)
            flash(f'File "{os.path.basename(relative_path)}" deleted successfully.', 'success')
        else:
            flash('File not found.', 'error')

    except Exception as e:
        app.logger.error(f"File deletion error: {str(e)}")
        flash(f'Error deleting file: {str(e)}', 'error')

    return redirect(url_for('admin_file_manager'))

@app.route('/babaj/delete-multiple-files', methods=['POST'])
@admin_required
def admin_delete_multiple_files():
    """Delete multiple selected files"""
    try:
        file_paths = request.form.getlist('selected_files')
        if not file_paths:
            flash('No files selected for deletion.', 'error')
            return redirect(url_for('admin_file_manager'))

        deleted_count = 0
        errors = []

        for relative_path in file_paths:
            try:
                # Security check - ensure file is within upload folder
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], relative_path)
                if not full_path.startswith(app.config['UPLOAD_FOLDER']):
                    errors.append(f'Invalid path: {relative_path}')
                    continue

                if os.path.exists(full_path):
                    os.remove(full_path)
                    deleted_count += 1
                else:
                    errors.append(f'File not found: {os.path.basename(relative_path)}')
            except Exception as e:
                errors.append(f'Error deleting {os.path.basename(relative_path)}: {str(e)}')

        if deleted_count > 0:
            flash(f'Successfully deleted {deleted_count} file(s).', 'success')

        if errors:
            for error in errors[:5]:  # Show max 5 errors
                flash(error, 'error')
            if len(errors) > 5:
                flash(f'...and {len(errors) - 5} more errors.', 'error')

    except Exception as e:
        app.logger.error(f"Multiple file deletion error: {str(e)}")
        flash(f'Error deleting files: {str(e)}', 'error')

    return redirect(url_for('admin_file_manager'))

@app.route('/babaj/cleanup-orphaned-files', methods=['POST'])
@admin_required
def admin_cleanup_orphaned_files():
    """Clean up files that don't have corresponding database records"""
    try:
        cleaned_count = 0
        errors = []

        if os.path.exists(app.config['UPLOAD_FOLDER']):
            # Get all build job download paths from database
            valid_paths = set()
            build_jobs = BuildJob.query.filter(BuildJob.download_path.isnot(None)).all()
            for job in build_jobs:
                if job.download_path and os.path.exists(job.download_path):
                    valid_paths.add(os.path.abspath(job.download_path))

            # Scan all files and check if they're referenced
            for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
                for file in files:
                    file_path = os.path.join(root, file)
                    abs_path = os.path.abspath(file_path)

                    # Skip if file is referenced by a build job
                    if abs_path in valid_paths:
                        continue

                    # Skip template directories and important files
                    relative_path = os.path.relpath(file_path, app.config['UPLOAD_FOLDER'])
                    if any(part in relative_path for part in ['template', 'README', 'manifest.json']):
                        continue

                    try:
                        # Check if file is older than 7 days
                        stat = os.stat(file_path)
                        file_age = datetime.now() - datetime.fromtimestamp(stat.st_mtime)

                        if file_age.days >= 7:  # Only delete files older than 7 days
                            os.remove(file_path)
                            cleaned_count += 1
                    except Exception as e:
                        errors.append(f'Error cleaning {file}: {str(e)}')

        if cleaned_count > 0:
            flash(f'Cleaned up {cleaned_count} orphaned file(s).', 'success')
        else:
            flash('No orphaned files found to clean up.', 'info')

        if errors:
            for error in errors[:3]:  # Show max 3 errors
                flash(error, 'error')

    except Exception as e:
        app.logger.error(f"Cleanup error: {str(e)}")
        flash(f'Error during cleanup: {str(e)}', 'error')

    return redirect(url_for('admin_file_manager'))

@app.route('/babaj/restore-backup', methods=['POST'])
@admin_required
def restore_backup():
    """Restore system from backup"""
    temp_dir = None # Initialize temp_dir to None
    try:
        if 'backup_file' not in request.files:
            flash('No backup file selected', 'error')
            return redirect(url_for('admin_backup_restore'))

        backup_file = request.files['backup_file']
        if backup_file.filename == '':
            flash('No backup file selected', 'error')
            return redirect(url_for('admin_backup_restore'))

        if not backup_file.filename.endswith('.zip'):
            flash('Invalid backup file format. Please upload a .zip file', 'error')
            return redirect(url_for('admin_backup_restore'))

        import zipfile
        import tempfile
        from datetime import datetime

        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        backup_path = os.path.join(temp_dir, backup_file.filename)
        backup_file.save(backup_path)

        # Extract and process backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            # Extract all files to temp directory
            extract_dir = os.path.join(temp_dir, 'extracted')
            zipf.extractall(extract_dir)

            # Read database backup
            db_backup_path = os.path.join(extract_dir, 'database_backup.json')
            if not os.path.exists(db_backup_path):
                flash('Invalid backup file: database backup not found', 'error')
                return redirect(url_for('admin_backup_restore'))

            with open(db_backup_path, 'r') as f:
                backup_data = json.load(f)

            # Clear existing data (WARNING: This removes all current data!)
            db.session.execute(db.text('DELETE FROM tutorial_completion'))
            db.session.execute(db.text('DELETE FROM build_job'))
            db.session.execute(db.text('DELETE FROM app_metadata'))
            db.session.execute(db.text('DELETE FROM tutorial'))
            db.session.execute(db.text('DELETE FROM advertisement'))
            db.session.execute(db.text('DELETE FROM admin_settings'))
            db.session.execute(db.text('DELETE FROM admin_user'))
            db.session.commit()

            # Restore admin users
            for user_data in backup_data.get('admin_users', []):
                user = AdminUser()
                user.username = user_data['username']
                user.password_hash = user_data['password_hash']
                user.email = user_data['email']
                if user_data.get('created_at'):
                    user.created_at = datetime.fromisoformat(user_data['created_at'])
                db.session.add(user)

            # Restore admin settings
            for settings_data in backup_data.get('admin_settings', []):
                settings = AdminSettings()
                settings.google_adsense_code = settings_data.get('google_adsense_code')
                settings.payment_account_name = settings_data.get('payment_account_name')
                settings.payment_bank_name = settings_data.get('payment_bank_name')
                settings.payment_account_number = settings_data.get('payment_account_number')
                settings.admin_email = settings_data.get('admin_email')
                settings.banner_price_per_day = settings_data.get('banner_price_per_day', 10.0)
                if settings_data.get('updated_at'):
                    settings.updated_at = datetime.fromisoformat(settings_data['updated_at'])
                db.session.add(settings)

            # Restore advertisements
            for ad_data in backup_data.get('advertisements', []):
                ad = Advertisement(
                    product_name=ad_data['product_name'],
                    product_url=ad_data['product_url'],
                    description=ad_data.get('description'),
                    contact_name=ad_data.get('contact_name'),
                    contact_email=ad_data.get('contact_email'),
                    image_path=ad_data.get('image_path'),
                    days_to_display=ad_data.get('days_to_display', 1),
                    amount_payable=ad_data.get('amount_payable', 0.0),
                    status=ad_data.get('status', 'pending')
                )
                if ad_data.get('created_at'):
                    ad.created_at = datetime.fromisoformat(ad_data['created_at'])
                if ad_data.get('activated_at'):
                    ad.activated_at = datetime.fromisoformat(ad_data['activated_at'])
                if ad_data.get('expires_at'):
                    ad.expires_at = datetime.fromisoformat(ad_data['expires_at'])
                db.session.add(ad)

            # Restore tutorials
            for tutorial_data in backup_data.get('tutorials', []):
                tutorial = Tutorial(
                    title=tutorial_data['title'],
                    content=tutorial_data['content'],
                    description=tutorial_data.get('description'),
                    order_position=tutorial_data.get('order_position', 0),
                    is_active=tutorial_data.get('is_active', True)
                )
                if tutorial_data.get('created_at'):
                    tutorial.created_at = datetime.fromisoformat(tutorial_data['created_at'])
                if tutorial_data.get('updated_at'):
                    tutorial.updated_at = datetime.fromisoformat(tutorial_data['updated_at'])
                db.session.add(tutorial)

            # Restore tutorial completions
            for completion_data in backup_data.get('tutorial_completions', []):
                completion = TutorialCompletion(
                    learner_name=completion_data['learner_name'],
                    tutorial_ids=completion_data['tutorial_ids'],
                    certificate_id=completion_data['certificate_id']
                )
                if completion_data.get('completion_date'):
                    completion.completion_date = datetime.fromisoformat(completion_data['completion_date'])
                db.session.add(completion)

            # Restore app metadata
            for metadata_data in backup_data.get('app_metadata', []):
                metadata = AppMetadata(
                    url=metadata_data['url'],
                    title=metadata_data.get('title'),
                    description=metadata_data.get('description'),
                    icon_url=metadata_data.get('icon_url'),
                    theme_color=metadata_data.get('theme_color'),
                    background_color=metadata_data.get('background_color'),
                    metadata_json=metadata_data.get('metadata_json')
                )
                if metadata_data.get('last_scraped'):
                    metadata.last_scraped = datetime.fromisoformat(metadata_data['last_scraped'])
                db.session.add(metadata)

            # Restore build jobs
            for job_data in backup_data.get('build_jobs', []):
                job = BuildJob(
                    id=job_data['id'],
                    url=job_data['url'],
                    package_type=job_data['package_type'],
                    app_name=job_data['app_name'],
                    status=job_data.get('status', 'pending'),
                    error_message=job_data.get('error_message'),
                    download_path=job_data.get('download_path'),
                    manifest_data=job_data.get('manifest_data')
                )
                if job_data.get('created_at'):
                    job.created_at = datetime.fromisoformat(job_data['created_at'])
                if job_data.get('completed_at'):
                    job.completed_at = datetime.fromisoformat(job_data['completed_at'])
                db.session.add(job)

            db.session.commit()

            # Restore files
            files_restored = 0

            # Restore generated packages
            generated_packages_src = os.path.join(extract_dir, 'generated_packages')
            if os.path.exists(generated_packages_src):
                for root, dirs, files in os.walk(generated_packages_src):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, generated_packages_src)
                        dst_path = os.path.join(app.config['UPLOAD_FOLDER'], rel_path)

                        # Create directory if it doesn't exist
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        files_restored += 1

            # Restore static files
            static_src = os.path.join(extract_dir, 'static')
            static_dst = os.path.join(os.getcwd(), 'static')
            if os.path.exists(static_src):
                for root, dirs, files in os.walk(static_src):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, static_src)
                        dst_path = os.path.join(static_dst, rel_path)

                        # Create directory if it doesn't exist
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        files_restored += 1

            # Restore templates
            templates_src = os.path.join(extract_dir, 'templates')
            templates_dst = os.path.join(os.getcwd(), 'templates')
            if os.path.exists(templates_src):
                for root, dirs, files in os.walk(templates_src):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, templates_src)
                        dst_path = os.path.join(templates_dst, rel_path)

                        # Create directory if it doesn't exist
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        files_restored += 1

        flash(f'Backup restored successfully! Restored {files_restored} files. Please restart the application.', 'success')
        return redirect(url_for('admin_backup_restore'))

    except Exception as e:
        # Clean up temp files in case of error
        try:
            if temp_dir: # Check if temp_dir was assigned
                shutil.rmtree(temp_dir)
        except Exception as cleanup_error:
            app.logger.warning(f"Could not clean up temp directory after error: {str(cleanup_error)}")

        app.logger.error(f"Backup restoration failed: {str(e)}")
        flash(f'Backup restoration failed: {str(e)}', 'error')
        return redirect(url_for('admin_backup_restore'))

# Guest Ad Placement Routes
@app.route('/place-advert', methods=['GET', 'POST'])
def place_advert():
    """Guest ad placement page"""
    settings = AdminSettings.query.first()
    if not settings:
        # This should not happen if app.py initialization worked correctly
        app.logger.warning("No admin settings found - this should not happen")
        flash('System settings not found. Please contact support.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_url = request.form.get('product_url')
        description = request.form.get('description')
        contact_name = request.form.get('contact_name')
        contact_email = request.form.get('contact_email')
        days_to_display = int(request.form.get('days_to_display', 1))

        # Get ad image URL
        ad_image_url = request.form.get('ad_image_url')

        # Calculate amount
        amount_payable = settings.banner_price_per_day * days_to_display

        # Create advertisement
        ad = Advertisement(
            product_name=product_name,
            product_url=product_url,
            description=description,
            contact_name=contact_name,
            contact_email=contact_email,
            image_path=ad_image_url,  # Store the external URL in image_path field
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