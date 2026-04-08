import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)
report_bp = Blueprint('report', __name__)

VALID_CONTENT_TYPES = {'resume', 'cover_letter', 'chat', 'interview', 'linkedin', 'job_post', 'other'}
VALID_REASONS = {'harmful', 'inaccurate', 'offensive', 'misleading', 'other'}


@report_bp.route('/api/report/content', methods=['POST'])
def submit_report():
    try:
        from utils.data_layer import report_create
    except Exception:
        return jsonify({'success': False, 'error': 'Reporting is temporarily unavailable.'}), 503

    data = request.get_json(silent=True) or {}

    content_type = data.get('content_type', 'other')
    if content_type not in VALID_CONTENT_TYPES:
        content_type = 'other'

    reason = data.get('reason', 'other')
    if reason not in VALID_REASONS:
        reason = 'other'

    details = (data.get('details') or '').strip()
    content_snippet = (data.get('content_snippet') or '').strip()
    content_id = str(data.get('content_id') or '')

    try:
        report = report_create({
            'content_type': content_type,
            'content_id': content_id,
            'content_snippet': content_snippet,
            'reason': reason,
            'details': details,
        })
        logger.info('Content report submitted: id=%s type=%s reason=%s', report['id'], content_type, reason)
        return jsonify({'success': True, 'report_id': report['id']})
    except Exception as e:
        logger.error('Failed to save content report: %s', e)
        return jsonify({'success': False, 'error': 'Could not save report. Please try again.'}), 500
