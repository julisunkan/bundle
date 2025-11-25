from flask import Blueprint, render_template, session, redirect, request
from models import db, Course, Payment, Policy

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 4
    pagination = Course.query.paginate(page=page, per_page=per_page, error_out=False)
    courses = pagination.items
    currency = session.get('currency', 'NGN')
    return render_template('index.html', courses=courses, currency=currency, pagination=pagination)

@main_bp.route('/toggle-currency')
def toggle_currency():
    current = session.get('currency', 'NGN')
    new_currency = 'USD' if current == 'NGN' else 'NGN'
    session['currency'] = new_currency
    session.modified = True
    return redirect(request.referrer or '/')

@main_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    currency = session.get('currency', 'NGN')
    return render_template('course_detail.html', course=course, currency=currency)

@main_bp.route('/privacy')
def privacy():
    policy = Policy.query.filter_by(policy_type='privacy').first()
    return render_template('privacy.html', policy=policy)

@main_bp.route('/terms')
def terms():
    policy = Policy.query.filter_by(policy_type='terms').first()
    return render_template('terms.html', policy=policy)

@main_bp.route('/refund')
def refund():
    policy = Policy.query.filter_by(policy_type='refund').first()
    return render_template('refund.html', policy=policy)