import json
import logging

from flask import Blueprint, render_template, request, jsonify, redirect, url_for

logger = logging.getLogger(__name__)

setup_bp = Blueprint('setup', __name__)


@setup_bp.route('/setup', methods=['GET'])
def setup_page():
    from utils.credentials_store import is_firebase_configured
    from utils.firestore_manager import _firebase_failed
    configured = is_firebase_configured()
    return render_template('setup.html', already_configured=configured, firebase_failed=_firebase_failed)


@setup_bp.route('/setup', methods=['POST'])
def setup_submit():
    data = request.get_json(silent=True) or {}
    creds_raw = data.get('credentials', '')

    if isinstance(creds_raw, str):
        try:
            creds = json.loads(creds_raw)
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid JSON — please paste the full Firebase service account JSON.'}), 400
    elif isinstance(creds_raw, dict):
        creds = creds_raw
    else:
        return jsonify({'success': False, 'error': 'credentials field is required.'}), 400

    required = ('type', 'project_id', 'private_key', 'client_email')
    missing = [k for k in required if not creds.get(k)]
    if missing:
        return jsonify({'success': False, 'error': f'Missing required fields: {", ".join(missing)}'}), 400

    if creds.get('type') != 'service_account':
        return jsonify({'success': False, 'error': 'This does not look like a Firebase service account JSON (type must be "service_account").'}), 400

    from utils.credentials_store import save_firebase_credentials
    from utils.firestore_manager import reset_firebase_app, startup_check

    if not save_firebase_credentials(creds):
        return jsonify({'success': False, 'error': 'Could not save credentials to the database. Check server logs.'}), 500

    reset_firebase_app()
    startup_check()

    return jsonify({
        'success': True,
        'message': f'Firebase connected for project "{creds.get("project_id")}". Redirecting…',
        'redirect': '/',
    })
