# `models.py` Documentation

## Overview
This file defines the database models for the Customer Churn Prediction System using SQLAlchemy ORM. It establishes the data structure for user authentication, role-based access control, OTP verification, and rate limiting functionality.

## Database Models

### `Role` Model
Defines user roles in the system for role-based access control.

```python
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    users = db.relationship("User", backref="role", lazy=True)
```

#### Fields:
- `id`: Primary key for role identification
- `name`: Role name (e.g., "admin", "user")
- `users`: Relationship to User model (one-to-many)

#### Usage:
- Used to assign different access levels to users
- Currently supports "admin" and "user" roles
- Admin users have access to user management functionality

### `User` Model
Represents user accounts in the system, incorporating Flask-Login's UserMixin for authentication.

```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_password_change = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Fields:
- `id`: Primary key for user identification
- `name`: User's display name
- `email`: Unique email address (used for login)
- `password_hash`: Securely stored password hash
- `role_id`: Foreign key to Role model
- `created_at`: Timestamp of account creation
- `last_password_change`: Timestamp of last password update

#### Methods:
- `set_password(password)`: Securely hashes and stores the password
- `check_password(password)`: Validates provided password against stored hash
- `is_password_expired(expiry_days=30)`: Checks if password has expired
- `days_until_password_expires(expiry_days=30)`: Calculates days until password expiry

#### Security Features:
- Passwords are never stored in plain text, only as secure hashes
- Tracks password age for enforcing periodic changes
- Default password expiry is 30 days

### `OTPVerification` Model
Manages one-time passwords for email verification during signup.

```python
class OTPVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
```

#### Fields:
- `id`: Primary key
- `email`: Email address to verify
- `name`: User's name (stored during registration process)
- `otp_code`: Generated 6-digit verification code
- `created_at`: Timestamp of OTP creation
- `expires_at`: Timestamp when the OTP expires
- `verified`: Whether the OTP has been verified
- `attempts`: Number of verification attempts made

#### Methods:
- `is_expired`: Property that checks if the OTP has expired
- `has_max_attempts`: Property that checks if max verification attempts reached
- `increment_attempts()`: Tracks failed verification attempts
- `create(email, name, otp_code, expiry_minutes=3)`: Class method for creating new OTP records

#### Security Features:
- OTPs expire after a short time (default 3 minutes)
- Limited verification attempts (max 5)
- Indexed email field for efficient lookups

### `RateLimit` Model
Implements rate limiting for security-sensitive operations.

```python
class RateLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    reset_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Fields:
- `id`: Primary key
- `key`: Identifier for the rate limit (typically IP address or email)
- `action`: The action being rate-limited (e.g., "request_otp", "verify_otp")
- `attempts`: Number of attempts made
- `reset_at`: When the rate limit counter resets
- `created_at`: When the rate limit record was created

#### Methods:
- `is_reset_time`: Property that checks if the rate limit period has expired
- `increment()`: Increases the attempt counter
- `reset(reset_minutes=15)`: Resets the counter and sets a new expiry time
- `get_or_create(key, action, reset_minutes=15)`: Class method for fetching or creating rate limit records

#### Security Features:
- Tracks attempts by IP address or email
- Configurable reset window (default 15 minutes)
- Different rate limits can be set for different actions
- Protects against brute force attacks

## Database Initialization
The database instance is initialized with:

```python
db = SQLAlchemy()
```

This instance needs to be initialized with the Flask app using `db.init_app(app)` in the main application file.

## Usage in the Application
- Role-based access control (`@role_required('admin')` decorator)
- User authentication (`current_user` from Flask-Login)
- OTP verification during the registration process
- Rate limiting for sensitive operations