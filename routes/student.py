from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, session
from flask_login import login_required, current_user
from models import db, Course, Module, Payment, Quiz, QuizQuestion, QuizAnswer, Assignment, Submission, Certificate
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

student_bp = Blueprint('student', __name__)

def check_course_purchased(course_id):
    return Payment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id,
        status='success'
    ).first() is not None

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    purchased_courses = []
    payments = Payment.query.filter_by(user_id=current_user.id, status='success').all()
    
    for payment in payments:
        if payment.course:
            purchased_courses.append(payment.course)
    
    return render_template('student/dashboard.html', courses=purchased_courses)

@student_bp.route('/course/<int:course_id>')
@login_required
def view_course(course_id):
    if not check_course_purchased(course_id):
        flash('You need to purchase this course first', 'warning')
        return redirect(url_for('main.course_detail', course_id=course_id))
    
    course = Course.query.get_or_404(course_id)
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.order).all()
    
    return render_template('student/course.html', course=course, modules=modules)

@student_bp.route('/module/<int:module_id>')
@login_required
def view_module(module_id):
    module = Module.query.get_or_404(module_id)
    
    if not check_course_purchased(module.course_id):
        flash('You need to purchase this course first', 'warning')
        return redirect(url_for('main.index'))
    
    return render_template('student/module.html', module=module)

@student_bp.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if not check_course_purchased(quiz.module.course_id):
        flash('You need to purchase this course first', 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        score = 0
        total = len(quiz.questions)
        
        for question in quiz.questions:
            answer = request.form.get(f'question_{question.id}')
            is_correct = answer == question.correct_answer
            
            if is_correct:
                score += 1
            
            quiz_answer = QuizAnswer(
                user_id=current_user.id,
                question_id=question.id,
                selected_answer=answer,
                is_correct=is_correct
            )
            db.session.add(quiz_answer)
        
        db.session.commit()
        
        percentage = (score / total * 100) if total > 0 else 0
        flash(f'Quiz completed! Score: {score}/{total} ({percentage:.1f}%)', 'success')
        
        return redirect(url_for('student.view_module', module_id=quiz.module_id))
    
    return render_template('student/quiz.html', quiz=quiz)

@student_bp.route('/assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    if not check_course_purchased(assignment.module.course_id):
        flash('You need to purchase this course first', 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        file = request.files.get('file')
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join('static/uploads', f'{current_user.id}_{datetime.now().timestamp()}_{filename}')
            file.save(filepath)
            
            submission = Submission(
                assignment_id=assignment_id,
                user_id=current_user.id,
                file_path=filepath
            )
            db.session.add(submission)
            db.session.commit()
            
            flash('Assignment submitted successfully!', 'success')
            return redirect(url_for('student.view_module', module_id=assignment.module_id))
    
    return render_template('student/assignment.html', assignment=assignment)

@student_bp.route('/certificate/<int:course_id>')
@login_required
def generate_certificate(course_id):
    if not check_course_purchased(course_id):
        flash('You need to purchase this course first', 'warning')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    
    certificate = Certificate.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not certificate:
        cert_id = f'CERT-{uuid.uuid4().hex[:8].upper()}'
        certificate = Certificate(
            user_id=current_user.id,
            course_id=course_id,
            certificate_id=cert_id
        )
        db.session.add(certificate)
        db.session.commit()
    
    from utils.certificate_generator import generate_certificate_pdf
    pdf_path = generate_certificate_pdf(current_user, course, certificate)
    
    return send_file(pdf_path, as_attachment=True)
