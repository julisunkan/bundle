from flask import Blueprint, send_from_directory, jsonify

pwa_bp = Blueprint('pwa', __name__)

@pwa_bp.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@pwa_bp.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@pwa_bp.route('/offline.html')
def offline():
    return send_from_directory('templates', 'offline.html')
