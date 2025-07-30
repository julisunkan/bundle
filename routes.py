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

@app.route('/')
def index():
    return render_template('index.html')

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
                background_color=scraped_data.get('background_color', '#ffffff')
            )
            db.session.add(metadata)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error scraping metadata: {str(e)}")
            flash('Failed to scrape website metadata. Please check the URL and try again.', 'error')
            return redirect(url_for('index'))
    
    # Create build job
    build_job = BuildJob(
        url=url,
        app_name=metadata.title,
        package_type=package_type,
        status='pending'
    )
    db.session.add(build_job)
    db.session.commit()
    
    return redirect(url_for('build_progress', job_id=build_job.id))

@app.route('/build/<int:job_id>')
def build_progress(job_id):
    job = BuildJob.query.get_or_404(job_id)
    return render_template('build_progress.html', job=job)

@app.route('/api/build-status/<int:job_id>')
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
            else:
                # Mock other package types for now
                package_path = builder.build_mock_package(metadata, manifest_data, job.id, job.package_type)
            
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

@app.route('/download/<int:job_id>')
def download_package(job_id):
    job = BuildJob.query.get_or_404(job_id)
    
    if job.status != 'completed' or not job.download_path:
        flash('Package not ready for download', 'error')
        return redirect(url_for('index'))
    
    if not os.path.exists(job.download_path):
        flash('Package file not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('download.html', job=job)

@app.route('/download-file/<int:job_id>')
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

@app.route('/history')
def build_history():
    jobs = BuildJob.query.order_by(BuildJob.created_at.desc()).limit(50).all()
    return render_template('history.html', jobs=jobs)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
