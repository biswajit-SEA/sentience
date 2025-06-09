# `hackathon.py` Documentation

## Overview
This file serves as the main application entry point for the Customer Churn Prediction System. It's a Flask-based web application that integrates user authentication, file uploading, machine learning models for predicting customer churn, and an admin dashboard for user management.

## Dependencies
- **Flask**: Web framework for the application
- **Flask-Login**: Handles user authentication and session management
- **Flask-Mail**: For sending emails (OTP verification, password reset, results)
- **Flask-Migrate**: Database migration management
- **SQLAlchemy**: ORM for database operations
- **Pandas**: For data manipulation and analysis
- **Threading**: For asynchronous processing (like sending emails)

## Global Configuration

### Application Setup
```python
app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-goes-here-make-it-strong"
```

### Security Features
- CSRF Protection for form submissions
- Session timeout (15 minutes)
- reCAPTCHA integration for bot protection
- Password complexity requirements
- Rate limiting for sensitive operations

### Email Configuration
```python
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "example@gmail.com"
```

### Database Configuration
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
```

## Error Handling
- Thread exception handler to catch and log errors in background threads
- Global exception handler for all uncaught exceptions
- Detailed logging with timestamps to `app.log`

## Key Functions

### Authentication System

#### `login()`
- Handles user login with credential verification
- Password expiry checking (30 days)
- Warning for passwords about to expire (7 days)
- Session management with remember-me functionality

#### `signup()` and OTP Verification Flow
- Two-step registration process with email verification
- OTP generation and email delivery
- Rate limiting to prevent abuse
- Secure account creation with validated input

#### `logout()`
- Terminates user session and redirects to login page

#### `forgot_password()` and `reset_password()`
- Password recovery through email verification
- Secure token generation with time expiry (1 hour)
- Password strength validation during reset

#### `change_password()`
- Allows users to change their password
- Enforces password history check (prevents reuse)
- Password complexity validation

### Email Functionality

#### `send_email()`
- Retry mechanism for reliable email delivery
- HTML-formatted emails with styling
- Error handling and logging

#### Email Templates
- OTP verification emails
- Account creation confirmation
- Password reset instructions
- Analysis result notifications

### Admin Dashboard

#### `admin_dashboard()`
- Protected by role-based access control
- Lists all users in the system

#### User Management APIs
- `delete_user()`: Remove users with safeguards for last admin
- `update_user()`: Modify user details and roles
- `admin_reset_password()`: Force password reset for users
- `create_admin_recovery()`: Emergency admin account creation

### File Upload and Analysis

#### `upload_files()`
- Handles multi-file uploads (audio, data, chat files)
- Processes files through different ML models
- Combines results into a comprehensive analysis
- Sends email notifications with the results

#### File Processing Functions
- `process_audio_files()`: Analyzes audio recordings
- `process_data_files()`: Processes structured data using Random Forest
- `predict_chat()`: Sentiment analysis on text files
- `further_processing()`: Combines model outputs into final prediction

## Security Features

### Rate Limiting
- Customizable rate limiting for sensitive operations
- Per-IP and per-email tracking
- Window-based limiting (e.g., 15-minute windows)

### CSRF Protection
- Cross-Site Request Forgery protection for all forms
- Custom error handler for expired tokens

### Password Management
- Secure password hashing
- Complexity requirements (uppercase, lowercase, numbers, special chars)
- Password expiration policy
- History checking to prevent reuse

## Application Initialization

### `create_tables_and_roles()`
- Creates database tables if they don't exist
- Sets up default roles (admin, user)
- Creates a default admin account if none exists

### Main Entry Point
```python
if __name__ == "__main__":
    # Call the create tables function before starting the app
    create_tables_and_roles()
    
    app.run(host="0.0.0.0", port=5000, debug=True)
```