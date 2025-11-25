# CourseHub - Online Course Selling Platform

## Overview
CourseHub is a comprehensive Flask-based web application for selling and managing online courses. Students can browse courses, purchase them using Paystack or Flutterwave, take quizzes, submit assignments, and receive PDF certificates upon completion. Admins have full control over course content, student management, and payment configurations.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
- **Bootstrap 5**: Clean, modern, and responsive interface
- **Dark Mode**: Toggle between light and dark themes
- **Mobile-First Design**: Optimized for all screen sizes
- **Gradient Hero Section**: Eye-catching landing page with gradient background
- **Card-Based Layout**: Course cards with hover effects
- **Flash Messages**: User-friendly notifications for all actions

### Technical Stack
- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: SQLite for local development (can be configured for PostgreSQL in production)
- **Authentication**: Flask-Login with password hashing (Werkzeug)
- **Payment Gateways**: Paystack & Flutterwave integration
- **PDF Generation**: ReportLab for certificates
- **Frontend**: Jinja2 templates, Bootstrap 5, Vanilla JavaScript
- **PWA Support**: Service Worker, manifest.json, offline fallback page

### Core Features

#### 1. User Management
- **Student Registration & Login**: Secure authentication with password hashing
- **Admin Dashboard**: Full access to course and student management
- **Role-Based Access Control**: Separate interfaces for students and admins

#### 2. Course Management (Admin)
- Create, edit, and delete courses
- Set pricing in both NGN and USD
- Upload course images (external URLs)
- Add multiple modules per course
- Create quizzes with multiple-choice questions
- Assign assignments to modules

#### 3. Student Experience
- Browse all available courses
- View detailed course information
- Purchase courses using Paystack or Flutterwave
- Access purchased course modules
- Watch embedded video content (YouTube)
- Take quizzes and receive instant scoring
- Submit assignments (file upload)
- Download personalized PDF certificates

#### 4. Payment System
- **Currency Switching**: Toggle between NGN and USD
- **Paystack Integration**: Secure card payments (Nigerian market)
- **Flutterwave Integration**: Multiple payment options
- **Payment Verification**: Server-side transaction verification
- **Payment History**: Track all transactions in admin dashboard

#### 5. Progressive Web App
- **Offline Support**: Service worker caches essential resources
- **Installable**: Can be installed on mobile devices
- **Manifest**: App-like experience on mobile
- **Responsive Icons**: Multiple icon sizes for different devices

#### 6. Policy Management (Admin)
- **Privacy Policy Template**: Editable template for privacy policy
- **Terms & Conditions Template**: Editable template for terms and conditions
- **Refund Policy Template**: Editable template for refund policy
- **HTML Support**: Templates support HTML formatting for rich content
- **Integrated Settings**: All policy templates are managed in the admin settings page

### Database Models
- **User**: Students and admins with authentication
- **Course**: Course information and pricing
- **Module**: Individual lessons within courses
- **Quiz**: Module quizzes with questions
- **QuizQuestion**: Multiple-choice questions
- **QuizAnswer**: Student quiz submissions
- **Assignment**: Module assignments
- **Submission**: Student assignment submissions
- **Payment**: Transaction records
- **Certificate**: Issued certificates
- **Settings**: Payment API keys and configurations
- **Policy**: Policy templates (privacy, terms, refund)

### Security Features
- **Password Hashing**: Werkzeug security for password storage
- **Payment Verification**: Strict verification before granting access
- **Login Required**: Protected routes for authenticated users
- **Admin Protection**: Decorator-based admin access control
- **CSRF Protection**: Built into Flask forms

## Setup & Configuration

### Environment Variables
The application requires the following environment variable:
- `SESSION_SECRET`: Secret key for Flask sessions (automatically provided by Replit)

Payment API keys are stored in the database and can be configured through the admin settings page.

### Default Admin Account
- **Email**: admin@example.com
- **Password**: admin123
- **Note**: Change this password after first login for security

### Pre-Populated Courses
The database is automatically populated with 5 starter courses on first run:
1. **Cyber Security Fundamentals** (₦45,000 / $30)
2. **Graphics Design Masterclass** (₦35,000 / $25)
3. **Robotics for Beginners** (₦50,000 / $35)
4. **Electronic Engineering Foundation** (₦40,000 / $28)
5. **Data Science & Machine Learning** (₦55,000 / $40)

Each course includes multiple modules with video content, quizzes, and assignments.

### Admin Settings Configuration
To configure payment gateways and policy templates:
1. Login as admin (admin@example.com / admin123)
2. Navigate to Admin Dashboard → Settings
3. Configure payment gateways by entering your Paystack and/or Flutterwave API keys:
   - Paystack Public Key
   - Paystack Secret Key
   - Flutterwave Public Key
   - Flutterwave Secret Key
4. Set the NGN to USD exchange rate (default: 1500)

### Python Dependencies
- Flask==3.1.1
- Flask-SQLAlchemy==3.1.1
- Flask-Login==0.6.3
- Werkzeug==3.1.3
- reportlab==4.2.5
- requests==2.32.4
- python-dotenv==1.0.1
- gunicorn==23.0.0

### Frontend Dependencies (CDN)
- **Bootstrap 5.3.2**: Responsive UI framework
- **Bootstrap Icons 1.11.3**: Icon library
- **Feather Icons**: Additional icon set

## Project Structure
```
├── app.py                      # Main Flask application factory
├── main.py                     # Application entry point
├── models.py                   # Database models
├── init_data.py               # Database seeding script
├── requirements.txt           # Python dependencies
├── routes/                    # Route blueprints
│   ├── auth.py               # Authentication routes
│   ├── admin.py              # Admin dashboard routes
│   ├── student.py            # Student dashboard routes
│   ├── payments.py           # Payment processing routes
│   ├── pwa.py                # PWA routes
│   └── main.py               # Main routes (home, courses)
├── templates/                 # Jinja2 templates
│   ├── base.html            # Base template
│   ├── index.html           # Homepage
│   ├── course_detail.html   # Course details page
│   ├── offline.html         # PWA offline page
│   ├── auth/                # Authentication templates
│   ├── admin/               # Admin dashboard templates
│   ├── student/             # Student dashboard templates
│   └── payments/            # Payment templates
├── static/                   # Static assets
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   ├── icons/               # PWA icons
│   ├── uploads/             # User-uploaded files
│   ├── certificates/        # Generated certificates
│   ├── manifest.json        # PWA manifest
│   └── sw.js                # Service worker
├── utils/                    # Utility modules
│   └── certificate_generator.py  # PDF certificate generation
└── database.db              # SQLite database (auto-created)
```

## Usage Guide

### For Students
1. **Register**: Create an account using the Register page
2. **Browse Courses**: View available courses on the homepage
3. **Purchase**: Select a course and choose a payment method (Paystack/Flutterwave)
4. **Learn**: Access course modules, watch videos, take quizzes
5. **Submit**: Complete assignments by uploading files
6. **Certificate**: Download your certificate after completing the course

### For Admins
1. **Login**: Use admin credentials (admin@example.com / admin123)
2. **Manage Courses**: Create, edit, or delete courses
3. **Add Content**: Create modules with videos, quizzes, and assignments
4. **Configure Payments**: Set up Paystack/Flutterwave API keys
5. **Edit Policies**: Customize Privacy Policy, Terms & Conditions, and Refund Policy templates
6. **View Analytics**: Track students, revenue, and course enrollments

## Recent Changes
- **2025-11-25**: Added policy template editing to admin settings
  - Admins can now edit Privacy Policy, Terms & Conditions, and Refund Policy templates
  - Policy templates support HTML formatting for rich content
  - Templates are pre-populated with default content and current date
  - All policy editing is integrated into the admin settings page
  
- **2025-11-25**: Initial release of CourseHub platform
  - Complete course selling and management system
  - Paystack and Flutterwave payment integrations
  - Quiz and assignment features
  - PDF certificate generation
  - Progressive Web App implementation
  - Pre-populated with 5 comprehensive courses

## Notes
- The application uses SQLite by default for simplicity
- File uploads are stored in `static/uploads/`
- Certificates are generated on-demand and stored in `static/certificates/`
- The service worker caches static assets for offline access
- Payment verification is done server-side for security