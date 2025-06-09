# Customer Churn Prediction System Documentation

## Overview
This documentation provides a comprehensive overview of the Customer Churn Prediction System, a web application that predicts customer churn probability using multiple machine learning models. The system analyzes data files, chat transcripts, and audio recordings to deliver a holistic view of churn risk.

## System Architecture

The application follows a multi-tier architecture:
- **Frontend**: HTML templates with CSS styling and JavaScript for interactivity
- **Backend**: Flask web server with Python-based route handlers
- **Data Processing**: Machine learning models for data analysis, chat sentiment, and audio processing
- **Database**: SQLite database for user management and authentication
- **Security**: CSRF protection, rate limiting, and OTP verification

## Backend Documentation

### Core Application
- [Main Application (hackathon.py)](python_docs/hackathon.py.md) - Flask application with routes and core functionality
- [Database Models (models.py)](python_docs/models.py.md) - SQLAlchemy ORM models for data persistence

### Machine Learning Models
- [Text Analysis Model (text_analysis_model.py)](python_docs/text_analysis_model.py.md) - Sentiment analysis using DistilBERT
- [Churn Prediction Model (churn_prediction_model.py)](python_docs/churn_prediction_model.py.md) - Random Forest model for churn prediction

## Frontend Documentation

### HTML Templates
- [Frontend Templates](frontend_docs/templates.md) - Documentation for all HTML templates

### JavaScript Components
- [File Upload Interface (script.js)](frontend_docs/js/script.js.md) - Main dashboard functionality
- [User Registration (signup.js)](frontend_docs/js/signup.js.md) - User registration with OTP verification
- [Admin Dashboard (admin.js)](frontend_docs/js/admin.js.md) - User management for administrators

## Key Features

### Authentication System
- Secure login with password expiry
- Two-step registration with email verification
- Password reset via secure token
- Role-based access control

### Churn Prediction
- Multi-model prediction approach
- Customer data analysis with Random Forest
- Chat sentiment analysis with DistilBERT
- Combined analysis for final prediction

### Security Features
- CSRF protection for all forms
- Rate limiting for sensitive operations
- Email verification with OTPs
- Password complexity requirements
- Session timeout management

## Database Schema

### User Management
- `User` - Stores user accounts with roles and authentication data
- `Role` - Defines user roles (admin, user)
- `OTPVerification` - Manages one-time passwords for email verification
- `RateLimit` - Tracks request rates for security-sensitive operations

## Installation and Setup

### Requirements
- Python 3.8+
- Flask and related extensions
- PyTorch for the DistilBERT model
- Scikit-learn for the Random Forest model
- SQLite for the database

### Configuration
Key configuration settings in `hackathon.py`:
- SECRET_KEY for session security
- Mail server settings for email functionality
- Database URI for SQLAlchemy
- Rate limiting parameters

## API Endpoints

### Authentication
- `/login` - User login
- `/signup` - User registration
- `/request_otp` - Request verification code
- `/verify_otp` - Verify code and create account
- `/logout` - User logout
- `/forgot_password` - Password recovery
- `/reset_password/<token>` - Set new password
- `/change_password` - Update existing password

### File Processing
- `/upload` - Process uploaded files for churn prediction

### User Management
- `/admin` - Admin dashboard
- `/admin/delete_user/<int:user_id>` - Delete user
- `/admin/update_user` - Update user details
- `/admin/reset_password` - Reset user password