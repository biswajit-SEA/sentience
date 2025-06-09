from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

db = SQLAlchemy()


# Defining User Roles
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    users = db.relationship("User", backref="role", lazy=True)

    def __repr__(self):
        return f"<Role {self.name}>"


# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(
        db.Integer, db.ForeignKey("role.id"), default=2
    )  # Default to regular user role
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_password_change = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.last_password_change = datetime.utcnow()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_password_expired(self, expiry_days=30):
        if not self.last_password_change:
            return False
        expiry_date = self.last_password_change + timedelta(days=expiry_days)
        return datetime.utcnow() > expiry_date
        
    def days_until_password_expires(self, expiry_days=30):
        if not self.last_password_change:
            return 0
        expiry_date = self.last_password_change + timedelta(days=expiry_days)
        days_left = (expiry_date - datetime.utcnow()).days
        return max(0, days_left)

    def __repr__(self):
        return f"<User {self.email}>"


# OTP Verification Model
class OTPVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
        
    @property
    def has_max_attempts(self):
        return self.attempts >= 5
        
    def increment_attempts(self):
        self.attempts += 1
        return self.attempts
    
    @classmethod
    def create(cls, email, name, otp_code, expiry_minutes=3):
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        return cls(
            email=email,
            name=name,
            otp_code=otp_code,
            expires_at=expires_at
        )
        
    def __repr__(self):
        return f"<OTPVerification {self.email}>"


# Rate Limiting Model
class RateLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False, index=True)  # IP address or email
    action = db.Column(db.String(50), nullable=False)  # e.g., 'request_otp', 'verify_otp'
    attempts = db.Column(db.Integer, default=0, nullable=False)
    reset_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_reset_time(self):
        return datetime.utcnow() > self.reset_at
        
    def increment(self):
        if self.attempts is None:
            self.attempts = 0
        self.attempts += 1
        return self.attempts
        
    def reset(self, reset_minutes=15):
        self.attempts = 0
        self.reset_at = datetime.utcnow() + timedelta(minutes=reset_minutes)
        
    @classmethod
    def get_or_create(cls, key, action, reset_minutes=15):
        rate_limit = cls.query.filter_by(key=key, action=action).first()
        if not rate_limit:
            reset_at = datetime.utcnow() + timedelta(minutes=reset_minutes)
            rate_limit = cls(key=key, action=action, attempts=0, reset_at=reset_at)
            db.session.add(rate_limit)
        elif rate_limit.attempts is None:
            rate_limit.attempts = 0
        return rate_limit
        
    def __repr__(self):
        return f"<RateLimit {self.key}:{self.action}>"
