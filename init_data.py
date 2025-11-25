from app import create_app
from models import db, Course, Module, Quiz, QuizQuestion, Assignment

def populate_courses():
    from flask import current_app
    
    if current_app:
        ctx = None
    else:
        app = create_app()
        ctx = app.app_context()
        ctx.push()
    
    try:
        if Course.query.count() > 0:
            print("Courses already exist. Skipping population.")
            return
        
        courses_data = [
            {
                'title': 'Cyber Security Fundamentals',
                'description': 'Learn the fundamentals of cybersecurity, network protection, and ethical hacking basics.',
                'price_ngn': 45000,
                'price_usd': 30,
                'image_url': 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400',
                'modules': [
                    {
                        'title': 'Intro to Cyber Security',
                        'content': 'Understanding the basics of cybersecurity, threats, and defense mechanisms.',
                        'video_url': 'https://www.youtube.com/embed/inWWhr5tnEA',
                        'quiz': {
                            'title': 'Cyber Security Basics Quiz',
                            'questions': [
                                {
                                    'question': 'What is the primary goal of cybersecurity?',
                                    'option_a': 'To protect information and systems',
                                    'option_b': 'To hack systems',
                                    'option_c': 'To slow down computers',
                                    'option_d': 'To install viruses',
                                    'correct_answer': 'A'
                                },
                                {
                                    'question': 'Which of the following is a common cyber threat?',
                                    'option_a': 'Antivirus software',
                                    'option_b': 'Phishing',
                                    'option_c': 'Firewall',
                                    'option_d': 'Encryption',
                                    'correct_answer': 'B'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Network Security',
                        'content': 'Learn about network protocols, firewalls, and secure network design.',
                        'video_url': 'https://www.youtube.com/embed/qiQR5rTSshw',
                        'assignment': {
                            'title': 'Network Security Assessment',
                            'description': 'Analyze a network diagram and identify potential security vulnerabilities.'
                        }
                    },
                    {
                        'title': 'Ethical Hacking Basics',
                        'content': 'Introduction to ethical hacking, penetration testing, and security auditing.',
                        'video_url': 'https://www.youtube.com/embed/3Kq1MIfTWCE'
                    }
                ]
            },
            {
                'title': 'Graphics Design Masterclass',
                'description': 'Master graphic design from theory to practical application using industry-standard tools.',
                'price_ngn': 35000,
                'price_usd': 25,
                'image_url': 'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=400',
                'modules': [
                    {
                        'title': 'Design Theory',
                        'content': 'Understanding color theory, typography, composition, and design principles.',
                        'video_url': 'https://www.youtube.com/embed/YqQx75OPRa0',
                        'quiz': {
                            'title': 'Design Theory Quiz',
                            'questions': [
                                {
                                    'question': 'What are the primary colors?',
                                    'option_a': 'Red, Yellow, Blue',
                                    'option_b': 'Red, Green, Blue',
                                    'option_c': 'Orange, Purple, Green',
                                    'option_d': 'Black, White, Gray',
                                    'correct_answer': 'A'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Photoshop Essentials',
                        'content': 'Learn the essential tools and techniques in Adobe Photoshop.',
                        'video_url': 'https://www.youtube.com/embed/IyR_uYsRdPs'
                    },
                    {
                        'title': 'Illustrator Techniques',
                        'content': 'Master vector graphics creation with Adobe Illustrator.',
                        'video_url': 'https://www.youtube.com/embed/Ib8UBwu3yGA',
                        'assignment': {
                            'title': 'Logo Design Project',
                            'description': 'Create a professional logo design for a fictional company.'
                        }
                    }
                ]
            },
            {
                'title': 'Robotics for Beginners',
                'description': 'Get started with robotics, learn about motors, sensors, and basic programming.',
                'price_ngn': 50000,
                'price_usd': 35,
                'image_url': 'https://images.unsplash.com/photo-1561557944-6e7860d1a7eb?w=400',
                'modules': [
                    {
                        'title': 'Introduction to Robotics',
                        'content': 'Understanding robotics fundamentals, components, and applications.',
                        'video_url': 'https://www.youtube.com/embed/bLKJ16wpRGE'
                    },
                    {
                        'title': 'Motor Control',
                        'content': 'Learn how to control DC motors, servo motors, and stepper motors.',
                        'video_url': 'https://www.youtube.com/embed/0qwrnUeSpYQ',
                        'quiz': {
                            'title': 'Motor Control Quiz',
                            'questions': [
                                {
                                    'question': 'What type of motor provides precise angular control?',
                                    'option_a': 'DC Motor',
                                    'option_b': 'Servo Motor',
                                    'option_c': 'AC Motor',
                                    'option_d': 'Linear Motor',
                                    'correct_answer': 'B'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Basic Sensors',
                        'content': 'Understanding ultrasonic, infrared, and other common sensors.',
                        'video_url': 'https://www.youtube.com/embed/y_mJ6dPQbj4'
                    }
                ]
            },
            {
                'title': 'Electronic Engineering Foundation',
                'description': 'Build a solid foundation in electronics from circuit theory to PCB design.',
                'price_ngn': 40000,
                'price_usd': 28,
                'image_url': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400',
                'modules': [
                    {
                        'title': 'Circuit Theory',
                        'content': "Learn Ohm's law, Kirchhoff's laws, and basic circuit analysis.",
                        'video_url': 'https://www.youtube.com/embed/m4jzgqZu-4s',
                        'quiz': {
                            'title': 'Circuit Theory Quiz',
                            'questions': [
                                {
                                    'question': "What does Ohm's law state?",
                                    'option_a': 'V = I × R',
                                    'option_b': 'V = I + R',
                                    'option_c': 'V = I - R',
                                    'option_d': 'V = I / R',
                                    'correct_answer': 'A'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Microcontrollers',
                        'content': 'Introduction to Arduino, ESP32, and microcontroller programming.',
                        'video_url': 'https://www.youtube.com/embed/nL34zDTPkcs'
                    },
                    {
                        'title': 'Soldering & PCB Basics',
                        'content': 'Learn proper soldering techniques and PCB design fundamentals.',
                        'video_url': 'https://www.youtube.com/embed/VxMV6wGS3NY',
                        'assignment': {
                            'title': 'PCB Design Project',
                            'description': 'Design a simple PCB layout for an LED circuit.'
                        }
                    }
                ]
            },
            {
                'title': 'Data Science & Machine Learning',
                'description': 'Learn data science fundamentals, visualization, and machine learning algorithms.',
                'price_ngn': 55000,
                'price_usd': 40,
                'image_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400',
                'modules': [
                    {
                        'title': 'Python for Data Science',
                        'content': 'Learn Python programming, NumPy, and Pandas for data analysis.',
                        'video_url': 'https://www.youtube.com/embed/LHBE6Q9XlzI',
                        'quiz': {
                            'title': 'Python Basics Quiz',
                            'questions': [
                                {
                                    'question': 'Which library is commonly used for data manipulation in Python?',
                                    'option_a': 'Pandas',
                                    'option_b': 'Flask',
                                    'option_c': 'Django',
                                    'option_d': 'Requests',
                                    'correct_answer': 'A'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Data Visualization',
                        'content': 'Create compelling visualizations using Matplotlib and Seaborn.',
                        'video_url': 'https://www.youtube.com/embed/DAQNHzOcO5A'
                    },
                    {
                        'title': 'ML Algorithms Overview',
                        'content': 'Introduction to supervised and unsupervised learning algorithms.',
                        'video_url': 'https://www.youtube.com/embed/ukzFI9rgwfU',
                        'assignment': {
                            'title': 'ML Model Project',
                            'description': 'Build and train a simple machine learning model on a dataset.'
                        }
                    }
                ]
            }
        ]
        
        for course_data in courses_data:
            course = Course(
                title=course_data['title'],
                description=course_data['description'],
                price_ngn=course_data['price_ngn'],
                price_usd=course_data['price_usd'],
                image_url=course_data['image_url']
            )
            db.session.add(course)
            db.session.flush()
            
            for idx, module_data in enumerate(course_data['modules']):
                module = Module(
                    course_id=course.id,
                    title=module_data['title'],
                    content=module_data['content'],
                    video_url=module_data.get('video_url', ''),
                    order=idx
                )
                db.session.add(module)
                db.session.flush()
                
                if 'quiz' in module_data:
                    quiz = Quiz(
                        module_id=module.id,
                        title=module_data['quiz']['title']
                    )
                    db.session.add(quiz)
                    db.session.flush()
                    
                    for question_data in module_data['quiz']['questions']:
                        question = QuizQuestion(
                            quiz_id=quiz.id,
                            question=question_data['question'],
                            option_a=question_data['option_a'],
                            option_b=question_data['option_b'],
                            option_c=question_data['option_c'],
                            option_d=question_data['option_d'],
                            correct_answer=question_data['correct_answer']
                        )
                        db.session.add(question)
                
                if 'assignment' in module_data:
                    assignment = Assignment(
                        module_id=module.id,
                        title=module_data['assignment']['title'],
                        description=module_data['assignment']['description']
                    )
                    db.session.add(assignment)
        
        db.session.commit()
        print("Database populated with 5 courses successfully!")
    finally:
        if ctx:
            ctx.pop()

if __name__ == '__main__':
    populate_courses()
