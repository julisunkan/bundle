from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import db, Course, Module, Quiz, QuizQuestion, Assignment, Settings, User, Payment
from werkzeug.utils import secure_filename
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

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    if request.method == 'POST':
        keys = ['paystack_public_key', 'paystack_secret_key', 
                'flutterwave_public_key', 'flutterwave_secret_key', 'exchange_rate']
        
        for key in keys:
            value = request.form.get(key)
            setting = Settings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = Settings(key=key, value=value)
                db.session.add(setting)
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    settings_dict = {}
    for setting in Settings.query.all():
        settings_dict[setting.key] = setting.value
    
    return render_template('admin/settings.html', settings=settings_dict)

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    students = User.query.filter_by(is_admin=False).all()
    return render_template('admin/students.html', students=students)
