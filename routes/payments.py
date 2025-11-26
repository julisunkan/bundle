from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from models import db, Course, Payment, Settings
import requests
import uuid
import logging

payments_bp = Blueprint('payments', __name__)

def get_setting(key):
    setting = Settings.query.filter_by(key=key).first()
    return setting.value if setting else ''

@payments_bp.route('/initiate/<int:course_id>')
@login_required
def initiate_payment(course_id):
    course = Course.query.get_or_404(course_id)
    currency = session.get('currency', 'NGN')
    
    existing_purchase = Payment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id,
        status='success'
    ).first()
    
    if existing_purchase:
        flash('You have already purchased this course', 'info')
        return redirect(url_for('student.view_course', course_id=course_id))
    
    return render_template('payments/select_method.html', course=course, currency=currency)

@payments_bp.route('/flutterwave/<int:course_id>')
@login_required
def flutterwave_payment(course_id):
    course = Course.query.get_or_404(course_id)
    currency = session.get('currency', 'NGN')
    amount = course.price_ngn if currency == 'NGN' else course.price_usd
    
    public_key = get_setting('flutterwave_public_key')
    
    if not public_key:
        flash('Payment system not configured. Please contact admin.', 'danger')
        return redirect(url_for('main.course_detail', course_id=course_id))
    
    reference = f'FLW-{uuid.uuid4().hex[:16].upper()}'
    
    payment = Payment(
        user_id=current_user.id,
        course_id=course_id,
        amount=amount,
        currency=currency,
        payment_method='flutterwave',
        transaction_ref=reference,
        status='pending'
    )
    db.session.add(payment)
    db.session.commit()
    
    return render_template('payments/flutterwave.html',
                         public_key=public_key,
                         email=current_user.email,
                         amount=amount,
                         reference=reference,
                         currency=currency,
                         course=course,
                         customer_name=current_user.full_name)

@payments_bp.route('/flutterwave/callback')
@login_required
def flutterwave_callback():
    transaction_id = request.args.get('transaction_id')
    
    if not transaction_id:
        flash('Invalid transaction', 'danger')
        return redirect(url_for('main.index'))
    
    secret_key = get_setting('flutterwave_secret_key')
    
    if not secret_key:
        flash('Payment system not configured. Please contact admin.', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        headers = {
            'Authorization': f'Bearer {secret_key}'
        }
        response = requests.get(
            f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('status') == 'successful':
                tx_ref = data.get('data', {}).get('tx_ref')
                payment = Payment.query.filter_by(transaction_ref=tx_ref).first()
                
                if payment:
                    payment.status = 'success'
                    db.session.commit()
                    flash('Payment successful! You can now access the course.', 'success')
                    return redirect(url_for('student.view_course', course_id=payment.course_id))
        
        flash('Payment verification failed. Please contact support.', 'danger')
        return redirect(url_for('main.index'))
    except Exception as e:
        logging.error(f'Flutterwave verification error: {e}')
        flash('Payment verification error. Please contact support.', 'danger')
        return redirect(url_for('main.index'))

@payments_bp.route('/flutterwave/webhook', methods=['POST'])
def flutterwave_webhook():
    """
    Flutterwave V3 Live Webhook endpoint for handling payment notifications
    Live Webhook URL: https://your-domain.repl.co/payments/flutterwave/webhook
    """
    secret_hash = get_setting('flutterwave_webhook_secret_hash')
    
    if not secret_hash:
        logging.error('Flutterwave webhook secret hash not configured')
        return jsonify({'status': 'error', 'message': 'Configuration error'}), 500
    
    signature = request.headers.get('verif-hash')
    if not signature or signature != secret_hash:
        logging.error('Invalid webhook signature')
        return jsonify({'status': 'error', 'message': 'Invalid signature'}), 401
    
    try:
        event = request.json
        
        if not event:
            return jsonify({'status': 'error', 'message': 'No payload'}), 400
        
        event_type = event.get('event')
        data = event.get('data', {})
        
        logging.info(f'Flutterwave webhook received: {event_type}')
        
        if event_type == 'charge.completed':
            status = data.get('status')
            tx_ref = data.get('tx_ref')
            
            if status == 'successful' and tx_ref:
                payment = Payment.query.filter_by(transaction_ref=tx_ref).first()
                if payment and payment.status == 'pending':
                    payment.status = 'success'
                    db.session.commit()
                    logging.info(f'Payment {tx_ref} marked as successful via webhook')
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logging.error(f'Flutterwave webhook error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500
