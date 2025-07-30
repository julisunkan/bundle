import os
import json
import uuid
from datetime import datetime
from urllib.parse import urlparse

from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app import app, db
from models import BuildJob, AppMetadata
from services.web_scraper import scrape_website_metadata
from services.package_builder import PackageBuilder
from services.manifest_generator import generate_manifest
from services.pwa_detector import analyze_website_pwa_status
from services.pwa_generator import PWAGenerator

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
        # Create a metadata object that PWAGenerator expects
        metadata_obj = type('Metadata', (), metadata)()
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
        job.manifest_data = json.dumps({
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
    
    # Create build job
    job_id = str(uuid.uuid4())
    build_job = BuildJob(
        id=job_id,
        url=url,
        app_name=metadata.title,
        package_type=package_type,
        status='pending'
    )
    db.session.add(build_job)
    db.session.commit()
    
    return redirect(url_for('build_progress', job_id=build_job.id))

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
            
            # Generate manifest
            manifest_data = generate_manifest(metadata, job.url)
            job.manifest_data = json.dumps(manifest_data)
            
            # Build package
            builder = PackageBuilder()
            if job.package_type == 'apk':
                package_path = builder.build_apk(metadata, manifest_data, job.id)
            elif job.package_type == 'ipa':
                package_path = builder.build_ipa(metadata, manifest_data, job.id)
            elif job.package_type == 'msix':
                package_path = builder.build_msix(metadata, manifest_data, job.id)
            elif job.package_type == 'appx':
                package_path = builder.build_appx(metadata, manifest_data, job.id)
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
    
    filename = f"{job.app_name.replace(' ', '_')}.{job.package_type}"
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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
