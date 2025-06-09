# Frontend Templates Documentation

## Overview
This document provides information about the frontend templates used in the Customer Churn Prediction System. The application uses HTML templates with Flask's Jinja2 templating engine, CSS for styling, and JavaScript for interactive functionality.

## Template Structure

The frontend is organized into several HTML templates:
- `login.html` - User authentication
- `signup.html` - New user registration
- `forgot_password.html` - Password recovery
- `reset_password.html` - Setting a new password
- `change_password.html` - Changing existing password
- `index.html` - Main application dashboard
- `admin.html` - Administrator dashboard

## Common Elements

### Header
All pages share a common header with:
- Team logo on the left
- Application title in the center
- Tech Mahindra logo on the right

```html
<header class="header-container">
  <div class="logo-left">
    <img src="{{ url_for('static', filename='images/team-logo-bg.png') }}" alt="team logo" />
  </div>
  <h1>Churn Prediction System</h1>
  <div class="logo-right">
    <img src="{{ url_for('static', filename='images/techm-logo.png') }}" alt="techm logo" />
  </div>
</header>
```

### Form Elements
- Input fields with labels
- Error message containers
- CSRF protection tokens
- Password visibility toggles

### Notifications
- Success and error message containers
- Flash message handling

## Login Template (`login.html`)

The login page serves as the entry point for authenticated users.

### Features
- Email and password form
- "Remember me" functionality
- Password visibility toggle
- reCAPTCHA integration for bot protection
- Links to signup and password reset pages

### Security Features
- CSRF token protection
- Client-side input validation
- Server-side authentication
- Session timeout monitoring

### User Experience
- Clear error messaging
- Success notifications
- Password visibility toggle

### JavaScript Integration
```javascript
// Toggle password visibility
document.getElementById('togglePassword').addEventListener('click', function() {
    const passwordInput = document.getElementById('password');
    const icon = this.querySelector('i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
});
```

## Signup Template (`signup.html`)

The signup page allows new users to register for the system.

### Features
- Two-step registration with OTP verification
- Name, email, and password fields
- Password strength requirements display
- reCAPTCHA protection
- Email verification via OTP

### Security Features
- Password complexity requirements
- Email verification
- Client-side validation
- AJAX form submission with CSRF protection

### Form Validation
- Real-time password strength checking
- Email format validation
- Matching password confirmation

## Main Dashboard (`index.html`)

The main application dashboard for file upload and analysis.

### Features
- Multi-file upload interface
- Drag-and-drop functionality
- File type validation
- Progress indicators
- Results display section

### File Upload Sections
- Customer data files (.csv, .xlsx)
- Chat history files (.txt)
- Audio recording files (.mp3, .wav)

### Results Display
- Visualizations of prediction results
- Tabular data presentation
- Combined analysis from multiple models

## Admin Dashboard (`admin.html`)

Administrator interface for user management.

### Features
- User listing with pagination
- User details editing
- Password reset functionality
- User deletion with confirmation
- Role management

### User Management
- Add new users
- Modify existing user details
- Change user roles
- Reset user passwords
- Delete users

### Security Features
- Role-based access control
- Action confirmation dialogs
- Audit logging

## Password Management Templates

### Forgot Password (`forgot_password.html`)
- Email input for password reset
- reCAPTCHA verification
- Email delivery of reset link

### Reset Password (`reset_password.html`)
- Token-based authentication
- New password and confirmation inputs
- Password strength requirements
- Token validity checking

### Change Password (`change_password.html`)
- Current password verification
- New password input with strength requirements
- Password history checking

## Stylesheets and JavaScript

The templates are supported by:

### CSS Files
- `index.css` - Common styles across all pages
- `login.css` - Styles specific to authentication pages
- `admin.css` - Styles for admin dashboard

### JavaScript Files
- `login.js` - Login form validation and submission
- `signup.js` - Signup process and OTP verification
- `session-timeout.js` - Manages user session timeouts
- `script.js` - Main application functionality
- `admin.js` - Admin dashboard functionality

## Responsive Design

All templates implement responsive design using:
- Flexible layouts
- Media queries for different screen sizes
- Mobile-friendly input elements
- Touch-friendly interface elements