from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import db, Course, Module, Quiz, QuizQuestion, Assignment, Settings, User, Payment, Policy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_courses = Course.query.count()
    total_students = User.query.filter_by(is_admin=False).count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='success').scalar() or 0
    
    recent_payments = Payment.query.filter_by(status='success').order_by(Payment.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_courses=total_courses,
                         total_students=total_students,
                         total_revenue=total_revenue,
                         recent_payments=recent_payments)

@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/course/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price_ngn = float(request.form.get('price_ngn', 0))
        price_usd = float(request.form.get('price_usd', 0))
        image_url = request.form.get('image_url', '')
        
        course = Course(
            title=title,
            description=description,
            price_ngn=price_ngn,
            price_usd=price_usd,
            image_url=image_url
        )
        db.session.add(course)
        db.session.commit()
        
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/add_course.html')

@admin_bp.route('/course/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form.get('title')
        course.description = request.form.get('description')
        course.price_ngn = float(request.form.get('price_ngn', 0))
        course.price_usd = float(request.form.get('price_usd', 0))
        course.image_url = request.form.get('image_url', '')
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/edit_course.html', course=course)

@admin_bp.route('/course/delete/<int:course_id>')
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin.courses'))

@admin_bp.route('/course/<int:course_id>/modules')
@login_required
@admin_required
def course_modules(course_id):
    course = Course.query.get_or_404(course_id)
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.order).all()
    return render_template('admin/modules.html', course=course, modules=modules)

@admin_bp.route('/course/<int:course_id>/module/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_module(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        video_url = request.form.get('video_url', '')
        order = int(request.form.get('order', 0))
        
        module = Module(
            course_id=course_id,
            title=title,
            content=content,
            video_url=video_url,
            order=order
        )
        db.session.add(module)
        db.session.commit()
        
        flash('Module added successfully!', 'success')
        return redirect(url_for('admin.course_modules', course_id=course_id))
    
    return render_template('admin/add_module.html', course=course)

@admin_bp.route('/module/<int:module_id>/quiz/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_quiz(module_id):
    module = Module.query.get_or_404(module_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        
        quiz = Quiz(module_id=module_id, title=title)
        db.session.add(quiz)
        db.session.flush()
        
        question_count = int(request.form.get('question_count', 1))
        for i in range(question_count):
            question_text = request.form.get(f'question_{i}')
            if question_text:
                question = QuizQuestion(
                    quiz_id=quiz.id,
                    question=question_text,
                    option_a=request.form.get(f'option_a_{i}', ''),
                    option_b=request.form.get(f'option_b_{i}', ''),
                    option_c=request.form.get(f'option_c_{i}', ''),
                    option_d=request.form.get(f'option_d_{i}', ''),
                    correct_answer=request.form.get(f'correct_{i}', 'A')
                )
                db.session.add(question)
        
        db.session.commit()
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('admin.course_modules', course_id=module.course_id))
    
    return render_template('admin/add_quiz.html', module=module)

@admin_bp.route('/module/<int:module_id>/assignment/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_assignment(module_id):
    module = Module.query.get_or_404(module_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        assignment = Assignment(
            module_id=module_id,
            title=title,
            description=description
        )
        db.session.add(assignment)
        db.session.commit()
        
        flash('Assignment added successfully!', 'success')
        return redirect(url_for('admin.course_modules', course_id=module.course_id))
    
    return render_template('admin/add_assignment.html', module=module)

@admin_bp.route('/module/edit/<int:module_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_module(module_id):
    module = Module.query.get_or_404(module_id)
    
    if request.method == 'POST':
        module.title = request.form.get('title')
        module.content = request.form.get('content')
        module.video_url = request.form.get('video_url', '')
        module.order = int(request.form.get('order', 0))
        
        db.session.commit()
        flash('Module updated successfully!', 'success')
        return redirect(url_for('admin.course_modules', course_id=module.course_id))
    
    return render_template('admin/edit_module.html', module=module)

@admin_bp.route('/module/delete/<int:module_id>')
@login_required
@admin_required
def delete_module(module_id):
    module = Module.query.get_or_404(module_id)
    course_id = module.course_id
    db.session.delete(module)
    db.session.commit()
    flash('Module deleted successfully!', 'success')
    return redirect(url_for('admin.course_modules', course_id=course_id))

@admin_bp.route('/quiz/edit/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        quiz.title = request.form.get('title')
        
        # Delete existing questions
        QuizQuestion.query.filter_by(quiz_id=quiz_id).delete()
        
        # Add new questions
        question_count = int(request.form.get('question_count', 1))
        for i in range(question_count):
            question_text = request.form.get(f'question_{i}')
            if question_text:
                question = QuizQuestion(
                    quiz_id=quiz.id,
                    question=question_text,
                    option_a=request.form.get(f'option_a_{i}', ''),
                    option_b=request.form.get(f'option_b_{i}', ''),
                    option_c=request.form.get(f'option_c_{i}', ''),
                    option_d=request.form.get(f'option_d_{i}', ''),
                    correct_answer=request.form.get(f'correct_{i}', 'A')
                )
                db.session.add(question)
        
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.course_modules', course_id=quiz.module.course_id))
    
    return render_template('admin/edit_quiz.html', quiz=quiz)

@admin_bp.route('/quiz/delete/<int:quiz_id>')
@login_required
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course_id = quiz.module.course_id
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin.course_modules', course_id=course_id))

@admin_bp.route('/assignment/edit/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    if request.method == 'POST':
        assignment.title = request.form.get('title')
        assignment.description = request.form.get('description')
        
        db.session.commit()
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('admin.course_modules', course_id=assignment.module.course_id))
    
    return render_template('admin/edit_assignment.html', assignment=assignment)

@admin_bp.route('/assignment/delete/<int:assignment_id>')
@login_required
@admin_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    course_id = assignment.module.course_id
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment deleted successfully!', 'success')
    return redirect(url_for('admin.course_modules', course_id=course_id))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    if request.method == 'POST':
        keys = ['flutterwave_public_key', 'flutterwave_secret_key', 'flutterwave_encryption_key', 'flutterwave_webhook_secret_hash', 'exchange_rate']
        
        for key in keys:
            value = request.form.get(key)
            setting = Settings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = Settings(key=key, value=value)
                db.session.add(setting)
        
        policy_types = ['privacy', 'terms', 'refund']
        for policy_type in policy_types:
            content = request.form.get(f'{policy_type}_policy')
            if content:
                policy = Policy.query.filter_by(policy_type=policy_type).first()
                if policy:
                    policy.content = content
                    policy.last_updated = datetime.utcnow()
                else:
                    policy = Policy(policy_type=policy_type, content=content)
                    db.session.add(policy)
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    settings_dict = {}
    for setting in Settings.query.all():
        settings_dict[setting.key] = setting.value
    
    policies = {}
    for policy_type in ['privacy', 'terms', 'refund']:
        policy = Policy.query.filter_by(policy_type=policy_type).first()
        policies[policy_type] = policy.content if policy else ''
    
    return render_template('admin/settings.html', settings=settings_dict, policies=policies)

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    students = User.query.all()
    return render_template('admin/students.html', students=students)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # Check if email is taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email already in use by another user', 'danger')
            return redirect(url_for('admin.profile'))
        
        # Verify current password if changing password
        if new_password:
            if not current_password or not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('admin.profile'))
            current_user.set_password(new_password)
        
        current_user.full_name = full_name
        current_user.email = email
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('admin.profile'))
    
    return render_template('admin/profile.html')

@admin_bp.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        
        # Check if email is taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user.id:
            flash('Email already in use by another user', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        user.full_name = full_name
        user.email = email
        
        # Update password if provided
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.students'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/user/ban/<int:user_id>')
@login_required
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from banning themselves
    if user.id == current_user.id:
        flash('You cannot ban yourself', 'danger')
        return redirect(url_for('admin.students'))
    
    # Toggle banned status
    if hasattr(user, 'is_banned'):
        user.is_banned = not user.is_banned
        status = 'banned' if user.is_banned else 'unbanned'
    else:
        # If is_banned column doesn't exist yet, we'll add it via model
        flash('Ban feature requires database update', 'warning')
        return redirect(url_for('admin.students'))
    
    db.session.commit()
    flash(f'User {status} successfully!', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/user/send-certificate/<int:user_id>/<int:course_id>')
@login_required
@admin_required
def send_certificate(user_id, course_id):
    from models import Certificate, Course
    from utils.certificate_generator import generate_certificate_pdf
    import uuid
    
    user = User.query.get_or_404(user_id)
    course = Course.query.get_or_404(course_id)
    
    # Check if user has purchased the course
    payment = Payment.query.filter_by(
        user_id=user_id,
        course_id=course_id,
        status='success'
    ).first()
    
    if not payment:
        flash('User has not purchased this course', 'warning')
        return redirect(url_for('admin.students'))
    
    # Check if certificate already exists
    certificate = Certificate.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()
    
    if not certificate:
        cert_id = f'CERT-{uuid.uuid4().hex[:8].upper()}'
        certificate = Certificate(
            user_id=user_id,
            course_id=course_id,
            certificate_id=cert_id
        )
        db.session.add(certificate)
        db.session.commit()
    
    # Generate certificate PDF
    try:
        generate_certificate_pdf(user, course, certificate)
        flash(f'Certificate generated for {user.full_name} - {course.title}', 'success')
    except Exception as e:
        flash(f'Error generating certificate: {str(e)}', 'danger')
    
    return redirect(url_for('admin.students'))

@admin_bp.route('/policies')
@login_required
@admin_required
def policies():
    privacy = Policy.query.filter_by(policy_type='privacy').first()
    terms = Policy.query.filter_by(policy_type='terms').first()
    refund = Policy.query.filter_by(policy_type='refund').first()
    return render_template('admin/policies.html', privacy=privacy, terms=terms, refund=refund)

@admin_bp.route('/policy/edit/<policy_type>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_policy(policy_type):
    if policy_type not in ['privacy', 'terms', 'refund']:
        flash('Invalid policy type', 'danger')
        return redirect(url_for('admin.policies'))
    
    policy = Policy.query.filter_by(policy_type=policy_type).first()
    
    if request.method == 'POST':
        content = request.form.get('content')
        
        if policy:
            policy.content = content
            policy.last_updated = datetime.utcnow()
        else:
            policy = Policy(policy_type=policy_type, content=content)
            db.session.add(policy)
        
        db.session.commit()
        flash(f'{policy_type.capitalize()} policy updated successfully!', 'success')
        return redirect(url_for('admin.policies'))
    
    policy_titles = {
        'privacy': 'Privacy Policy',
        'terms': 'Terms & Conditions',
        'refund': 'Refund Policy'
    }
    
    return render_template('admin/edit_policy.html', 
                         policy=policy, 
                         policy_type=policy_type,
                         policy_title=policy_titles[policy_type])
