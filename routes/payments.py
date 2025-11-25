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

@payments_bp.route('/paystack/<int:course_id>')
@login_required
def paystack_payment(course_id):
    course = Course.query.get_or_404(course_id)
    currency = session.get('currency', 'NGN')
    amount = course.price_ngn if currency == 'NGN' else course.price_usd
    
    public_key = get_setting('paystack_public_key')
    
    if not public_key:
        flash('Payment system not configured. Please contact admin.', 'danger')
        return redirect(url_for('main.course_detail', course_id=course_id))
    
    reference = f'PAY-{uuid.uuid4().hex[:16].upper()}'
    
    payment = Payment(
        user_id=current_user.id,
        course_id=course_id,
        amount=amount,
        currency=currency,
        payment_method='paystack',
        transaction_ref=reference,
        status='pending'
    )
    db.session.add(payment)
    db.session.commit()
    
    amount_kobo = int(amount * 100)
    
    return render_template('payments/paystack.html',
                         public_key=public_key,
                         email=current_user.email,
                         amount=amount_kobo,
                         reference=reference,
                         course=course)

@payments_bp.route('/paystack/callback')
@login_required
def paystack_callback():
    reference = request.args.get('reference')
    
    if not reference:
        flash('Invalid payment reference', 'danger')
        return redirect(url_for('main.index'))
    
    payment = Payment.query.filter_by(transaction_ref=reference).first()
    
    if not payment:
        flash('Payment record not found', 'danger')
        return redirect(url_for('main.index'))
    
    secret_key = get_setting('paystack_secret_key')
    
    if not secret_key:
        flash('Payment system not configured. Please contact admin.', 'danger')
        payment.status = 'failed'
        db.session.commit()
        return redirect(url_for('main.index'))
    
    try:
        headers = {
            'Authorization': f'Bearer {secret_key}'
        }
        response = requests.get(
            f'https://api.paystack.co/transaction/verify/{reference}',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('status') == 'successful':
                payment.status = 'success'
                db.session.commit()
                flash('Payment successful! You can now access the course.', 'success')
                return redirect(url_for('student.view_course', course_id=payment.course_id))
        
        payment.status = 'failed'
        db.session.commit()
        flash('Payment verification failed. Please contact support.', 'danger')
        return redirect(url_for('main.index'))
    except Exception as e:
        logging.error(f'Paystack verification error: {e}')
        payment.status = 'failed'
        db.session.commit()
        flash('Payment verification error. Please contact support.', 'danger')
        return redirect(url_for('main.index'))

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

@payments_bp.route('/paypal/<int:course_id>')
@login_required
def paypal_payment(course_id):
    course = Course.query.get_or_404(course_id)
    currency = session.get('currency', 'NGN')
    amount = course.price_ngn if currency == 'NGN' else course.price_usd
    
    client_id = get_setting('paypal_client_id')
    paypal_mode = get_setting('paypal_mode') or 'sandbox'
    
    if not client_id:
        flash('PayPal payment system not configured. Please contact admin.', 'danger')
        return redirect(url_for('main.course_detail', course_id=course_id))
    
    reference = f'PAYPAL-{uuid.uuid4().hex[:16].upper()}'
    
    payment = Payment(
        user_id=current_user.id,
        course_id=course_id,
        amount=amount,
        currency=currency,
        payment_method='paypal',
        transaction_ref=reference,
        status='pending'
    )
    db.session.add(payment)
    db.session.commit()
    
    # Convert NGN to USD for PayPal (PayPal doesn't support NGN directly)
    if currency == 'NGN':
        exchange_rate = float(get_setting('exchange_rate') or 1500)
        paypal_amount = round(amount / exchange_rate, 2)
        paypal_currency = 'USD'
    else:
        paypal_amount = amount
        paypal_currency = currency
    
    return render_template('payments/paypal.html',
                         client_id=client_id,
                         amount=paypal_amount,
                         currency=paypal_currency,
                         reference=reference,
                         course=course,
                         paypal_mode=paypal_mode,
                         payment_id=payment.id)

@payments_bp.route('/paypal/callback', methods=['POST'])
@login_required
def paypal_callback():
    data = request.json
    order_id = data.get('orderID')
    payment_id = data.get('paymentID')
    
    if not payment_id:
        return jsonify({'success': False, 'message': 'Invalid payment ID'}), 400
    
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return jsonify({'success': False, 'message': 'Payment record not found'}), 404
    
    client_id = get_setting('paypal_client_id')
    client_secret = get_setting('paypal_client_secret')
    paypal_mode = get_setting('paypal_mode') or 'sandbox'
    
    if not client_id or not client_secret:
        payment.status = 'failed'
        db.session.commit()
        return jsonify({'success': False, 'message': 'Payment system not configured'}), 500
    
    try:
        # Get PayPal API base URL
        api_base = 'https://api-m.sandbox.paypal.com' if paypal_mode == 'sandbox' else 'https://api-m.paypal.com'
        
        # Get access token
        auth_response = requests.post(
            f'{api_base}/v1/oauth2/token',
            headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
            auth=(client_id, client_secret),
            data={'grant_type': 'client_credentials'}
        )
        
        if auth_response.status_code != 200:
            payment.status = 'failed'
            db.session.commit()
            return jsonify({'success': False, 'message': 'PayPal authentication failed'}), 500
        
        access_token = auth_response.json().get('access_token')
        
        # Verify the order
        verify_response = requests.get(
            f'{api_base}/v2/checkout/orders/{order_id}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
        )
        
        if verify_response.status_code == 200:
            order_data = verify_response.json()
            if order_data.get('status') == 'COMPLETED':
                payment.status = 'success'
                db.session.commit()
                return jsonify({
                    'success': True, 
                    'message': 'Payment successful',
                    'redirect_url': url_for('student.view_course', course_id=payment.course_id)
                })
        
        payment.status = 'failed'
        db.session.commit()
        return jsonify({'success': False, 'message': 'Payment verification failed'}), 400
        
    except Exception as e:
        logging.error(f'PayPal verification error: {e}')
        payment.status = 'failed'
        db.session.commit()
        return jsonify({'success': False, 'message': 'Payment verification error'}), 500
