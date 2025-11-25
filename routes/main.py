from flask import Blueprint, render_template, session
from models import db, Course, Payment, Policy

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    courses = Course.query.all()
    currency = session.get('currency', 'NGN')
    return render_template('index.html', courses=courses, currency=currency)

@main_bp.route('/toggle-currency')
def toggle_currency():
    current = session.get('currency', 'NGN')
    session['currency'] = 'USD' if current == 'NGN' else 'NGN'
    from flask import redirect, request
    return redirect(request.referrer or '/')

@main_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    currency = session.get('currency', 'NGN')
    return render_template('course_detail.html', course=course, currency=currency)

@main_bp.route('/privacy')
def privacy():
    policy = Policy.query.filter_by(name='Privacy Policy').first()
    return render_template('privacy.html', policy=policy)

@main_bp.route('/terms')
def terms():
    policy = Policy.query.filter_by(name='Terms & Conditions').first()
    return render_template('terms.html', policy=policy)

@main_bp.route('/refund')
def refund():
    policy = Policy.query.filter_by(name='Refund Policy').first()
    return render_template('refund.html', policy=policy)