import json
import logging
import os
import datetime
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, Response, abort

from models.settings import Setting

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)

ADMIN_PASSWORD_KEY = 'admin_password'
DEFAULT_PASSWORD = 'admin123'


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            if request.path.startswith('/julisunkan/api/') or request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Unauthorized', 'redirect': url_for('admin.login_page')}), 401
            return redirect(url_for('admin.login_page'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('')
@admin_bp.route('/')
def login_page():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/login.html')


@admin_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(silent=True) or {}
        password = data.get('password', '')
        stored = Setting.get(ADMIN_PASSWORD_KEY, DEFAULT_PASSWORD)
        if password == stored:
            session['admin_logged_in'] = True
            session.permanent = True
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Incorrect password'}), 401
    except Exception as e:
        logger.error('Admin login error: %s', e)
        return jsonify({'success': False, 'error': 'Server error'}), 500


@admin_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('admin_logged_in', None)
    return jsonify({'success': True})


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')


# ── SETTINGS API ─────────────────────────────────────────────────────────────

@admin_bp.route('/api/settings', methods=['GET'])
@admin_required
def get_settings():
    sensitive = {'groq_api_key', ADMIN_PASSWORD_KEY, 'bitly_access_token', 'tly_api_key', 'kutt_api_key', 'urlzli_api_key', 'picsee_api_key'}
    rows = Setting.query.all()
    result = {}
    for r in rows:
        if r.key in sensitive:
            result[r.key] = '••••••••' if r.value else ''
        else:
            result[r.key] = r.value or ''
    defaults = {
        'groq_api_key': '',
        'ai_model': 'llama-3.3-70b-versatile',
        'ai_max_tokens': '4096',
        'app_name': 'AI Resume & Cover Letter Creator',
        'app_tagline': 'Your intelligent job application assistant — from resume to offer letter.',
        'site_url': '',
        'contact_email': '',
        'meta_description': 'AI-powered resume builder, cover letter generator, and career assistant.',
        'meta_keywords': 'resume builder, cover letter, AI, job application, career',
        'twitter_url': '',
        'linkedin_url': '',
        'facebook_url': '',
        'instagram_url': '',
        'youtube_url': '',
        'google_search_console': '',
        'max_upload_mb': '10',
        'use_fake_stats': '0',
        ADMIN_PASSWORD_KEY: '',
        'analytics_id': '',
        'adsense_publisher_id': '',
        'adsense_auto_ads': '0',
        'ad_top_banner_enabled': '0',
        'ad_top_banner_slot': '',
        'ad_results_enabled': '0',
        'ad_results_slot': '',
        'ad_sidebar_enabled': '0',
        'ad_sidebar_slot': '',
        'adzuna_app_id': '',
        'adzuna_app_key': '',
        'hide_footer': '0',
        'url_shortener': 'bitly',
        'bitly_access_token': '',
        'tly_api_key': '',
        'kutt_api_key': '',
        'urlzli_api_key': '',
        'picsee_api_key': '',
        'share_twitter': '1',
        'share_facebook': '1',
        'share_linkedin': '1',
        'share_whatsapp': '1',
        'share_telegram': '0',
        'share_reddit': '0',
        'share_email': '1',
        'share_copy_link': '1',
    }
    for k, v in defaults.items():
        if k not in result:
            result[k] = v
    return jsonify(result)


@admin_bp.route('/api/settings', methods=['POST'])
@admin_required
def save_settings():
    data = request.get_json(silent=True) or {}
    skip_mask = {'••••••••'}
    for key, value in data.items():
        if value in skip_mask:
            continue
        if value is not None:
            Setting.set(key, str(value))
    Setting.invalidate_cache()
    return jsonify({'success': True})


@admin_bp.route('/api/settings/test-groq', methods=['POST'])
@admin_required
def test_groq():
    api_key = Setting.get('groq_api_key', '')
    if not api_key:
        return jsonify({'success': False, 'error': 'No API key saved'})
    try:
        from groq import Groq
        from utils.ai_engine import _get_model
        client = Groq(api_key=api_key)
        model = _get_model()
        resp = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': 'Say "OK" in one word.'}],
            max_tokens=5,
        )
        return jsonify({'success': True, 'response': resp.choices[0].message.content.strip(), 'model': model})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ── RESUMES API ───────────────────────────────────────────────────────────────

@admin_bp.route('/api/resumes', methods=['GET'])
@admin_required
def list_resumes():
    from utils.data_layer import resume_list
    return jsonify(resume_list())


@admin_bp.route('/api/resumes/<rid>', methods=['GET'])
@admin_required
def get_resume(rid):
    from utils.data_layer import resume_get
    r = resume_get(rid)
    if r is None:
        abort(404)
    return jsonify(r)


@admin_bp.route('/api/resumes/<rid>', methods=['PUT'])
@admin_required
def update_resume(rid):
    from utils.data_layer import resume_update
    data = request.get_json(silent=True) or {}
    r = resume_update(rid, data)
    if r is None:
        abort(404)
    return jsonify(r)


@admin_bp.route('/api/resumes/<rid>', methods=['DELETE'])
@admin_required
def delete_resume(rid):
    from utils.data_layer import resume_delete
    if not resume_delete(rid):
        abort(404)
    return jsonify({'success': True})


@admin_bp.route('/api/resumes/bulk-delete', methods=['POST'])
@admin_required
def bulk_delete_resumes():
    from utils.data_layer import resume_bulk_delete
    data = request.get_json(silent=True) or {}
    ids = data.get('ids', [])
    deleted = resume_bulk_delete(ids)
    return jsonify({'success': True, 'deleted': deleted})


# ── JOBS API ──────────────────────────────────────────────────────────────────

@admin_bp.route('/api/jobs', methods=['GET'])
@admin_required
def list_jobs():
    from utils.data_layer import job_list
    return jsonify(job_list())


@admin_bp.route('/api/jobs/<jid>', methods=['PUT'])
@admin_required
def update_job(jid):
    from utils.data_layer import job_update
    data = request.get_json(silent=True) or {}
    j = job_update(jid, data)
    if j is None:
        abort(404)
    return jsonify(j)


@admin_bp.route('/api/jobs/<jid>', methods=['DELETE'])
@admin_required
def delete_job(jid):
    from utils.data_layer import job_delete
    if not job_delete(jid):
        abort(404)
    return jsonify({'success': True})


@admin_bp.route('/api/jobs/bulk-delete', methods=['POST'])
@admin_required
def bulk_delete_jobs():
    from utils.data_layer import job_bulk_delete
    data = request.get_json(silent=True) or {}
    ids = data.get('ids', [])
    deleted = job_bulk_delete(ids)
    return jsonify({'success': True, 'deleted': deleted})


# ── ADS.TXT ───────────────────────────────────────────────────────────────────

@admin_bp.route('/api/ads-txt', methods=['GET'])
@admin_required
def get_ads_txt():
    content = Setting.get('ads_txt_content', '')
    return jsonify({'content': content})


@admin_bp.route('/api/ads-txt', methods=['POST'])
@admin_required
def save_ads_txt():
    if request.content_type and 'multipart/form-data' in request.content_type:
        f = request.files.get('file')
        if not f or not f.filename:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        content = f.read().decode('utf-8', errors='replace')
    else:
        data = request.get_json(silent=True) or {}
        content = data.get('content', '')
    Setting.set('ads_txt_content', content)
    return jsonify({'success': True})


# ── STATS ─────────────────────────────────────────────────────────────────────

@admin_bp.route('/api/stats', methods=['GET'])
@admin_required
def get_stats():
    from utils.data_layer import (
        resume_count, job_count, job_count_by_status,
        message_count, message_count_unread, report_count,
    )

    def _safe(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            return 0

    by_status = _safe(job_count_by_status) or {}
    return jsonify({
        'resumes': _safe(resume_count),
        'jobs': _safe(job_count),
        'interviews': by_status.get('Interview', 0),
        'offers': by_status.get('Offer', 0),
        'messages': _safe(message_count),
        'unread_messages': _safe(message_count_unread),
        'reports': _safe(report_count),
        'pending_reports': _safe(report_count, status='pending'),
    })


# ── CONTACT MESSAGES API ──────────────────────────────────────────────────────

@admin_bp.route('/api/messages', methods=['GET'])
@admin_required
def list_messages():
    from utils.data_layer import message_list
    return jsonify(message_list())


@admin_bp.route('/api/messages/<mid>', methods=['GET'])
@admin_required
def get_message(mid):
    from utils.data_layer import message_get, message_set_read
    m = message_get(mid)
    if m is None:
        abort(404)
    if not m.get('is_read'):
        message_set_read(mid, True)
        m['is_read'] = True
    return jsonify(m)


@admin_bp.route('/api/messages/<mid>/read', methods=['POST'])
@admin_required
def mark_read(mid):
    from utils.data_layer import message_set_read
    if not message_set_read(mid, True):
        abort(404)
    return jsonify({'success': True})


@admin_bp.route('/api/messages/<mid>/unread', methods=['POST'])
@admin_required
def mark_unread(mid):
    from utils.data_layer import message_set_read
    if not message_set_read(mid, False):
        abort(404)
    return jsonify({'success': True})


@admin_bp.route('/api/messages/<mid>', methods=['DELETE'])
@admin_required
def delete_message(mid):
    from utils.data_layer import message_delete
    if not message_delete(mid):
        abort(404)
    return jsonify({'success': True})


@admin_bp.route('/api/messages/bulk-delete', methods=['POST'])
@admin_required
def bulk_delete_messages():
    from utils.data_layer import message_bulk_delete
    data = request.get_json(silent=True) or {}
    ids = data.get('ids', [])
    deleted = message_bulk_delete(ids)
    return jsonify({'success': True, 'deleted': deleted})


# ── DATABASE CONFIG (Firebase only) ──────────────────────────────────────────

@admin_bp.route('/api/database/config', methods=['GET'])
@admin_required
def get_db_config():
    return jsonify({'db_type': 'firebase', 'active_db': 'firebase'})


@admin_bp.route('/api/database/config', methods=['POST'])
@admin_required
def save_db_config():
    return jsonify({'success': True, 'message': 'Firebase is the only database. No configuration needed.'})


@admin_bp.route('/api/database/restart', methods=['POST'])
@admin_required
def restart_app():
    import threading
    def _restart():
        import time
        import signal
        time.sleep(0.8)
        os.kill(os.getpid(), signal.SIGTERM)
    threading.Thread(target=_restart, daemon=True).start()
    return jsonify({'success': True})


@admin_bp.route('/api/database/export/sqlite', methods=['GET'])
@admin_bp.route('/api/database/export/mysql', methods=['GET'])
@admin_required
def export_db_sql():
    """SQLite/MySQL export is not applicable — app uses Firebase only. Returns a JSON data dump instead."""
    import json as _json
    from utils.data_layer import resume_list, job_list, message_list
    from models.settings import Setting
    sensitive = {'admin_password', 'groq_api_key', 'bitly_access_token',
                 'tly_api_key', 'kutt_api_key', 'urlzli_api_key', 'picsee_api_key'}
    rows = Setting.query.all()
    settings_data = {r.key: r.value or '' for r in rows if r.key not in sensitive}
    try:
        data = {
            'note': 'This app uses Firebase/Firestore exclusively. SQL export is not available. '
                    'This JSON file contains all your Firestore data.',
            'exported_at': datetime.datetime.utcnow().isoformat() + 'Z',
            'resumes': resume_list(),
            'jobs': job_list(),
            'contact_messages': message_list(),
            'settings': settings_data,
        }
    except Exception as e:
        return jsonify({'error': f'Export failed: {e}'}), 500
    ts = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    return Response(
        _json.dumps(data, indent=2, default=str),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=firebase_export_{ts}.json'}
    )


@admin_bp.route('/api/database/import-sql', methods=['POST'])
@admin_required
def import_sql_dump():
    """SQL import is not applicable — this app uses Firebase only."""
    return jsonify({
        'success': False,
        'error': 'SQL import is not supported. This app uses Firebase/Firestore exclusively. '
                 'Use the Firebase panel to manage your data directly.',
    }), 400


# ── SETTINGS JSON EXPORT / IMPORT ─────────────────────────────────────────────

@admin_bp.route('/api/settings/export-json', methods=['GET'])
@admin_required
def export_settings_json():
    import json as _json
    sensitive = {'admin_password', 'groq_api_key'}
    rows = Setting.query.all()
    data = {}
    for r in rows:
        data[r.key] = '[REDACTED]' if r.key in sensitive else (r.value or '')
    ts = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    return Response(
        _json.dumps(data, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=settings_{ts}.json'}
    )


@admin_bp.route('/api/settings/import-json', methods=['POST'])
@admin_required
def import_settings_json():
    import json as _json
    sensitive = {'admin_password', 'groq_api_key'}
    f = request.files.get('file')
    if not f:
        raw = request.get_json(silent=True) or {}
        data = raw
    else:
        try:
            data = _json.loads(f.read().decode('utf-8'))
        except Exception as e:
            return jsonify({'success': False, 'error': f'Invalid JSON: {e}'}), 400
    count = 0
    skipped = []
    for key, value in data.items():
        if value == '[REDACTED]':
            skipped.append(key)
            continue
        if key in sensitive:
            skipped.append(key)
            continue
        Setting.set(str(key), str(value))
        count += 1
    Setting.invalidate_cache()
    msg = f'Imported {count} settings.'
    if skipped:
        msg += f' Skipped {len(skipped)} sensitive/redacted keys: {", ".join(skipped)}'
    return jsonify({'success': True, 'message': msg, 'imported': count, 'skipped': skipped})


# ── FIREBASE / FIRESTORE ───────────────────────────────────────────────────────

@admin_bp.route('/api/firebase/status', methods=['GET'])
@admin_required
def firebase_status():
    from utils.credentials_store import get_firebase_credentials, is_firebase_configured
    creds = get_firebase_credentials() or {}
    return jsonify({
        'configured': is_firebase_configured(),
        'project_id': creds.get('project_id', ''),
        'client_email': creds.get('client_email', ''),
    })


@admin_bp.route('/api/firebase/save-credentials', methods=['POST'])
@admin_required
def firebase_save_credentials():
    data = request.get_json(silent=True) or {}
    creds_raw = data.get('credentials', '')
    if isinstance(creds_raw, str):
        try:
            creds = json.loads(creds_raw)
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid JSON — please paste the full service account JSON.'}), 400
    elif isinstance(creds_raw, dict):
        creds = creds_raw
    else:
        return jsonify({'success': False, 'error': 'credentials field is required.'}), 400

    required = ('type', 'project_id', 'private_key', 'client_email')
    missing = [k for k in required if not creds.get(k)]
    if missing:
        return jsonify({'success': False, 'error': f'Missing required fields: {", ".join(missing)}'}), 400

    from utils.credentials_store import save_firebase_credentials
    from utils.firestore_manager import reset_firebase_app, startup_check
    if not save_firebase_credentials(creds):
        return jsonify({'success': False, 'error': 'Failed to save credentials to database.'}), 500

    reset_firebase_app()
    startup_check()
    return jsonify({'success': True, 'message': f'Firebase credentials saved for project "{creds.get("project_id")}".'})


@admin_bp.route('/api/firebase/clear-credentials', methods=['POST'])
@admin_required
def firebase_clear_credentials():
    from utils.credentials_store import clear_firebase_credentials
    from utils.firestore_manager import reset_firebase_app
    clear_firebase_credentials()
    reset_firebase_app()
    return jsonify({'success': True, 'message': 'Firebase credentials cleared. The app will run without a database until new credentials are added.'})


@admin_bp.route('/api/firebase/test', methods=['POST'])
@admin_required
def firebase_test():
    try:
        from utils.firestore_manager import test_connection
        ok, msg = test_connection()
        return jsonify({'success': ok, 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@admin_bp.route('/api/firebase/export', methods=['POST'])
@admin_required
def firebase_export():
    """Download all selected Firestore collections as a JSON file."""
    import json as _json
    from utils.data_layer import (
        resume_list, job_list, message_list, jobpost_list,
    )
    data = request.get_json(silent=True) or {}
    collections = data.get('collections', ['resumes', 'jobs'])
    try:
        results = {}
        counts = {}
        if 'resumes' in collections:
            rows = resume_list()
            results['resumes'] = rows
            counts['resumes'] = len(rows)
        if 'jobs' in collections:
            rows = job_list()
            results['jobs'] = rows
            counts['jobs'] = len(rows)
        if 'messages' in collections:
            rows = message_list()
            results['contact_messages'] = rows
            counts['contact_messages'] = len(rows)
        if 'job_posts' in collections:
            rows = jobpost_list()
            results['job_posts'] = rows
            counts['job_posts'] = len(rows)
        if 'settings' in collections:
            sensitive = {'admin_password', 'groq_api_key'}
            rows = Setting.query.all()
            results['settings'] = {r.key: r.value or '' for r in rows if r.key not in sensitive}
            counts['settings'] = len(results['settings'])
        export_data = {
            'exported_at': datetime.datetime.utcnow().isoformat() + 'Z',
            **results,
        }
        ts = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return Response(
            _json.dumps(export_data, indent=2, default=str),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=firestore_export_{ts}.json'},
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/firebase/import', methods=['POST'])
@admin_required
def firebase_import():
    return jsonify({
        'success': True,
        'message': 'Firebase is the only database. All data is already in Firestore.',
        'results': {},
    })


# ── CONTENT REPORTS API ───────────────────────────────────────────────────────

@admin_bp.route('/api/reports', methods=['GET'])
@admin_required
def list_reports():
    from utils.data_layer import report_list
    status = request.args.get('status')
    return jsonify(report_list(status=status or None))


@admin_bp.route('/api/reports/<rid>', methods=['GET'])
@admin_required
def get_report(rid):
    from utils.data_layer import report_get
    r = report_get(rid)
    if r is None:
        abort(404)
    return jsonify(r)


@admin_bp.route('/api/reports/<rid>/status', methods=['POST'])
@admin_required
def update_report_status(rid):
    from utils.data_layer import report_update_status
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    if status not in ('pending', 'reviewed', 'dismissed'):
        return jsonify({'error': 'Invalid status'}), 400
    r = report_update_status(rid, status)
    if r is None:
        abort(404)
    return jsonify(r)


@admin_bp.route('/api/reports/<rid>', methods=['DELETE'])
@admin_required
def delete_report(rid):
    from utils.data_layer import report_delete
    if not report_delete(rid):
        abort(404)
    return jsonify({'success': True})


# ── SYNC API (Firebase is now primary — no sync needed) ───────────────────────

@admin_bp.route('/api/sync/status', methods=['GET'])
@admin_required
def sync_status():
    return jsonify({'available': True, 'message': 'Firebase is the only database. All data is live in Firestore.'})


@admin_bp.route('/api/sync/push', methods=['POST'])
@admin_required
def sync_push():
    return jsonify({'success': True, 'message': 'Firebase is the only database. All data is already in Firestore.'})


@admin_bp.route('/api/sync/restore', methods=['POST'])
@admin_required
def sync_restore():
    return jsonify({'success': True, 'message': 'Firebase is the only database. All data is already in Firestore.'})
