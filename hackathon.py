from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)
from models.text_analysis_model import predict_chat
from models.churn_prediction_model import ChurnPredictionModel
from flask_mail import Mail, Message
from models.models import db, User, Role, OTPVerification, RateLimit
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_migrate import Migrate
import threading
import os
import functools
import requests
import json
import secrets
import random
from datetime import datetime, timedelta
from flask_wtf.csrf import CSRFProtect, CSRFError
from itsdangerous import URLSafeTimedSerializer
import re
import logging
from sqlalchemy.exc import SQLAlchemyError
import sys
import traceback
import pandas as pd


# Custom thread exception handler
def thread_exception_handler():
    """
    Global exception handler for threads to ensure they log errors properly
    """

    def excepthook(args):
        # Handle _thread._ExceptHookArgs object from Python 3.8+
        if (
            hasattr(args, "exc_type")
            and hasattr(args, "exc_value")
            and hasattr(args, "exc_traceback")
        ):
            exc_type = args.exc_type
            exc_value = args.exc_value
            exc_traceback = args.exc_traceback

            # Skip KeyboardInterrupt to allow proper Ctrl+C handling
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # Log the exception
            logger.error(
                f"Uncaught exception in thread {getattr(args, 'thread', '(unknown)')}:",
                exc_info=(exc_type, exc_value, exc_traceback),
            )
        # Handle tuple of (exc_type, exc_value, exc_traceback)
        elif isinstance(args, tuple) and len(args) == 3:
            exc_type, exc_value, exc_traceback = args

            # Skip KeyboardInterrupt to allow proper Ctrl+C handling
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # Log the exception
            logger.error(
                "Uncaught exception in thread:",
                exc_info=(exc_type, exc_value, exc_traceback),
            )
        else:
            # In case args is in an unexpected format
            logger.error(
                f"Uncaught exception in thread with unexpected arguments format: {args}"
            )

    # Set the exception hook
    threading.excepthook = excepthook


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="app.log",
)
logger = logging.getLogger(__name__)

# Initialize thread exception handler
thread_exception_handler()

# Ensure the instance directory exists
os.makedirs("instance", exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-goes-here-make-it-strong"

# CSRF Protection
csrf = CSRFProtect(app)

# Session configuration - set timeout to 15 minutes (900 seconds)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)

# reCAPTCHA Configuration
app.config["RECAPTCHA_SECRET_KEY"] = (
    "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"  # Test secret key
)

# Database setup
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Email configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "biswajitpanda754@gmail.com"
app.config["MAIL_PASSWORD"] = "aljriijmtoinnwbx"
app.config["MAIL_DEFAULT_SENDER"] = "biswajitpanda754@gmail.com"
# Fallback if email sending fails
app.config["MAIL_SUPPRESS_SEND"] = False

mail = Mail(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the token serializer for password reset
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# OTP and rate limiting configuration
OTP_EXPIRY_MINUTES = 3
MAX_OTP_ATTEMPTS = 5
RATE_LIMIT_WINDOW_MINUTES = 15
MAX_OTP_REQUESTS_PER_EMAIL = 5  # Max OTP requests per email in window
MAX_OTP_REQUESTS_PER_IP = 10  # Max OTP requests per IP in window
MAX_FAILED_VERIFICATIONS = 10  # Max failed verifications per IP in window


# Rate limiting decorator
def rate_limit(action, limit, get_key=None):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Default key is the client's IP address
            key = get_key(*args, **kwargs) if get_key else request.remote_addr

            if not key:
                logger.warning(f"Rate limiting key couldn't be determined for {action}")
                return f(*args, **kwargs)

            # Check if rate limit exists for this key and action
            rate_limit = RateLimit.get_or_create(key, action, RATE_LIMIT_WINDOW_MINUTES)

            # Check if the reset time has passed
            if rate_limit.is_reset_time:
                rate_limit.reset(RATE_LIMIT_WINDOW_MINUTES)
                db.session.commit()

            # Check if limit exceeded
            if rate_limit.attempts >= limit:
                logger.warning(f"Rate limit exceeded for {key} on {action}")
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Too many requests. Please try again later.",
                        }
                    ),
                    429,
                )

            # Increment the counter
            rate_limit.increment()
            db.session.commit()

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Function to verify reCAPTCHA response
def verify_recaptcha(recaptcha_response):
    payload = {
        "secret": app.config["RECAPTCHA_SECRET_KEY"],
        "response": recaptcha_response,
    }

    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify", data=payload
        )
        result = response.json()
        return result.get("success", False)
    except Exception as e:
        logger.error(f"Error verifying reCAPTCHA: {str(e)}")
        return False


# Role-based access control decorator
def role_required(role_name):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("login"))

            if current_user.role.name != role_name:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("index"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Create tables and default roles/users - Using with_app_context for Flask 2.0+ compatibility
def create_tables_and_roles():
    with app.app_context():
        try:

            # Create roles if they don't exist
            if not Role.query.filter_by(name="admin").first():
                admin_role = Role(name="admin")
                db.session.add(admin_role)
                logger.info("Created admin role")

            if not Role.query.filter_by(name="user").first():
                user_role = Role(name="user")
                db.session.add(user_role)
                logger.info("Created user role")

            db.session.commit()

            # Get admin role
            admin_role = Role.query.filter_by(name="admin").first()

            # Check if any admin user exists
            admin_exists = (
                User.query.filter_by(role_id=admin_role.id).first() is not None
            )

            # Only create default admin if no admin users exist
            if not admin_exists:
                admin_user = User(
                    name="Admin", email="admin@example.com", role_id=admin_role.id
                )
                admin_user.set_password("Admin123!")
                db.session.add(admin_user)
                db.session.commit()
                logger.info("Created default admin user")

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating initial database: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error initializing app: {str(e)}")


# Generate a random 6-digit OTP
def generate_otp():
    return "".join(random.choices("0123456789", k=6))


# Handle email sending with better error handling and retry mechanism
def send_email(subject, recipient, html_content, max_retries=2):
    retries = 0
    while retries <= max_retries:
        try:
            msg = Message(subject=subject, recipients=[recipient], html=html_content)
            mail.send(msg)
            logger.info(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            retries += 1
            logger.error(f"Error sending email (attempt {retries}): {str(e)}")
            if retries > max_retries:
                return False


# Function to check if there are any admins other than the specified user
def has_other_admins(user_id):
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return False

    # Count admins other than the specified user
    other_admins_count = User.query.filter(
        User.role_id == admin_role.id, User.id != user_id
    ).count()

    return other_admins_count > 0


# Send OTP via email
def send_otp_email(user_email, user_name, otp):
    html_content = f"""
    <html>
    <head>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #f9f9f9;
          padding: 20px;
        }}
        .container {{
          background-color: #ffffff;
          padding: 20px;
          border-radius: 10px;
          box-shadow: 0 0 10px rgba(0,0,0,0.1);
          max-width: 600px;
          margin: 0 auto;
        }}
        h2 {{
          color: #333;
        }}
        .otp-container {{
          background-color: #f5f5f5;
          padding: 15px;
          border-radius: 5px;
          font-size: 24px;
          letter-spacing: 5px;
          text-align: center;
          margin: 20px 0;
          font-weight: bold;
          color: #333;
        }}
        .note {{
          font-size: 12px;
          color: #666;
          margin-top: 20px;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h2>Email Verification</h2>
        <p>Hello {user_name},</p>
        <p>Thank you for signing up for Churn Prediction System. Please use the following verification code to complete your registration:</p>
        
        <div class="otp-container">{otp}</div>
        
        <p>This verification code will expire in {OTP_EXPIRY_MINUTES} minutes.</p>
        
        <p>If you did not sign up for an account, please ignore this email.</p>
        
        <p>Thanks,<br><strong>Churn Prediction System Team</strong></p>
        
        <p class="note">This is an automated message, please do not reply to this email.</p>
      </div>
    </body>
    </html>
    """

    return send_email(
        subject="Verification Code - Churn Prediction System",
        recipient=user_email,
        html_content=html_content,
    )


# Send account creation confirmation email
def send_account_created_email(user_email, user_name):
    html_content = f"""
    <html>
    <head>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #f9f9f9;
          padding: 20px;
        }}
        .container {{
          background-color: #ffffff;
          padding: 20px;
          border-radius: 10px;
          box-shadow: 0 0 10px rgba(0,0,0,0.1);
          max-width: 600px;
          margin: 0 auto;
        }}
        h2 {{
          color: #333;
        }}
        .button {{
          display: inline-block;
          background-color: #4285f4;
          color: white;
          text-decoration: none;
          padding: 10px 20px;
          margin: 20px 0;
          border-radius: 5px;
          font-weight: bold;
        }}
        .note {{
          font-size: 12px;
          color: #666;
          margin-top: 20px;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h2>Welcome to Churn Prediction System!</h2>
        <p>Hello {user_name},</p>
        <p>Your account has been successfully created. Thank you for joining us!</p>
        
        <a href="{url_for('login', _external=True)}" class="button">Login to Your Account</a>
        
        <p>If you have any questions or need assistance, please contact our support team.</p>
        
        <p>Thanks,<br><strong>Churn Prediction System Team</strong></p>
        
        <p class="note">This is an automated message, please do not reply to this email.</p>
      </div>
    </body>
    </html>
    """

    # Try sending email with more retries for welcome email
    result = send_email(
        subject="Welcome to Churn Prediction System",
        recipient=user_email,
        html_content=html_content,
        max_retries=3,
    )

    if result:
        logger.info(f"Welcome email sent successfully to {user_email}")
    else:
        logger.error(f"Failed to send welcome email to {user_email}")

    return result


# Authentication routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = "remember" in request.form

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return render_template("login.html", error="Invalid email or password")

        # Check if password is expired (30 days)
        if user.is_password_expired():
            return redirect(url_for("change_password", expired=True))

        # Check if password is about to expire (within 7 days)
        days_left = user.days_until_password_expires()
        if 0 < days_left <= 7:
            flash(
                f"Your password will expire in {days_left} days. Please consider changing it.",
                "warning",
            )

        # Make session permanent to apply the timeout setting
        session.permanent = True
        login_user(user, remember=remember)

        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        return redirect(url_for("index"))

    # Handle success message from query parameter
    success = request.args.get("success")
    return render_template("login.html", success=success)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    # This route now only handles the GET request to display the signup form
    # The actual signup process is managed via AJAX with the OTP verification flow
    return render_template("signup.html")


# Request OTP API endpoint with rate limiting
@app.route("/request_otp", methods=["POST"])
@rate_limit("request_otp_ip", MAX_OTP_REQUESTS_PER_IP)
def request_otp():
    try:
        data = request.json
        email = data.get("email")
        name = data.get("name")
        is_resend = data.get("resend", False)

        # Validate email
        if not email or not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            return jsonify({"success": False, "message": "Invalid email address"})

        # Apply rate limiting per email
        email_key = f"email:{email}"
        try:
            rate_limit = RateLimit.get_or_create(
                email_key, "request_otp_email", RATE_LIMIT_WINDOW_MINUTES
            )

            # Check if the reset time has passed
            if rate_limit.is_reset_time:
                rate_limit.reset(RATE_LIMIT_WINDOW_MINUTES)
            # Defensive check to ensure attempts is not None
            elif (
                rate_limit.attempts is not None
                and rate_limit.attempts >= MAX_OTP_REQUESTS_PER_EMAIL
            ):
                logger.warning(f"Rate limit exceeded for email {email} on OTP request")
                return jsonify(
                    {
                        "success": False,
                        "message": "Too many verification requests. Please try again later.",
                    }
                )

            # Check if email is already registered
            if User.query.filter_by(email=email).first():
                return jsonify(
                    {"success": False, "message": "Email already registered"}
                )

        except Exception as e:
            logger.error(f"Error during rate limiting: {str(e)}")
            # Continue with the request even if rate limiting fails

        # Check reCAPTCHA for initial request (not for resend)
        if not is_resend:
            recaptcha_response = data.get("recaptcha")
            if not recaptcha_response or not verify_recaptcha(recaptcha_response):
                return jsonify(
                    {"success": False, "message": "reCAPTCHA verification failed"}
                )

        # Generate a new OTP
        otp = generate_otp()

        # Delete any existing OTP records for this email
        try:
            existing_otps = OTPVerification.query.filter_by(email=email).all()
            for old_otp in existing_otps:
                db.session.delete(old_otp)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error cleaning up old OTPs: {str(e)}")

        # Create new OTP record
        try:
            otp_record = OTPVerification.create(
                email=email, name=name, otp_code=otp, expiry_minutes=OTP_EXPIRY_MINUTES
            )
            db.session.add(otp_record)
            db.session.commit()

            # Increment the email rate limit counter if rate limiting is working
            try:
                if rate_limit:
                    rate_limit.increment()
                    db.session.commit()
            except Exception as e:
                logger.error(f"Error incrementing rate limit: {str(e)}")
                # Continue even if incrementing fails

            # Send OTP email
            email_sent = send_otp_email(email, name, otp)
            if not email_sent:
                # If email fails, we still keep the OTP record but inform the user
                logger.error(f"Failed to send OTP email to {email}")
                return jsonify(
                    {
                        "success": False,
                        "message": "Failed to send verification email. Please try again or contact support.",
                    }
                )

            logger.info(f"OTP generated and sent to {email}")
            return jsonify(
                {"success": True, "message": "Verification code sent to your email"}
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error creating OTP: {str(e)}")
            return jsonify(
                {"success": False, "message": "Server error. Please try again later."}
            )
        except Exception as e:
            logger.error(f"Unexpected error in request_otp: {str(e)}")
            return jsonify(
                {
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )
    except Exception as e:
        logger.error(f"Global error in request_otp: {str(e)}")
        return jsonify(
            {"success": False, "message": "Server error. Please try again later."}
        )


# Verify OTP and create account API endpoint
@app.route("/verify_otp", methods=["POST"])
@rate_limit("verify_otp", MAX_FAILED_VERIFICATIONS)
def verify_otp():
    try:
        data = request.json
        email = data.get("email")
        submitted_otp = data.get("otp")
        user_data = data.get("userData", {})

        # Validate inputs
        if not email or not submitted_otp:
            return jsonify({"success": False, "message": "Missing required fields"})

        # Find OTP record
        otp_record = OTPVerification.query.filter_by(email=email).first()
        if not otp_record:
            logger.warning(f"No OTP record found for {email}")
            return jsonify(
                {
                    "success": False,
                    "message": "No verification code found for this email",
                }
            )

        # Check if OTP is expired
        if otp_record.is_expired:
            # Clean up expired OTP
            try:
                db.session.delete(otp_record)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Error cleaning up expired OTP: {str(e)}")

            return jsonify(
                {"success": False, "message": "Verification code has expired"}
            )

        # Check if max attempts exceeded
        if otp_record.has_max_attempts:
            # Clean up OTP after too many attempts
            try:
                db.session.delete(otp_record)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Error cleaning up OTP after max attempts: {str(e)}")

            return jsonify(
                {
                    "success": False,
                    "message": "Too many failed attempts. Please request a new code.",
                }
            )

        # Increment attempt counter
        try:
            otp_record.increment_attempts()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error incrementing attempt counter: {str(e)}")

        # Verify OTP
        if submitted_otp != otp_record.otp_code:
            return jsonify({"success": False, "message": "Invalid verification code"})

        # OTP is valid - create the user account
        try:
            # Begin transaction
            name = user_data.get("name") or otp_record.name
            password = user_data.get("password")

            if not password:
                return jsonify({"success": False, "message": "Password is required"})

            # Create user
            user_role = Role.query.filter_by(name="user").first()
            if not user_role:
                return jsonify({"success": False, "message": "User role not found"})

            new_user = User(name=name, email=email, role_id=user_role.id)
            new_user.set_password(password)

            # Mark OTP as verified
            otp_record.verified = True

            # Save changes
            db.session.add(new_user)
            db.session.commit()

            # Now that the user is created, we can safely clean up the OTP
            try:
                db.session.delete(otp_record)
                db.session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Error cleaning up OTP after user creation: {str(e)}")
                # Continue anyway since the user was created successfully

            # Send welcome email (wrapped in try-except for better error handling)
            try:
                # First attempt to send email directly (more reliable than threading)
                welcome_email_sent = send_account_created_email(email, name)

                if not welcome_email_sent:
                    # If direct sending fails, try with threading
                    logger.warning(
                        f"Direct welcome email failed for {email}, attempting via thread"
                    )
                    thread = threading.Thread(
                        target=send_account_created_email, args=(email, name)
                    )
                    thread.daemon = True
                    thread.start()
            except Exception as e:
                logger.error(f"Failed to send welcome email to {email}: {str(e)}")
                # Continue anyway since the user was created successfully

            logger.info(f"User account created successfully for {email}")
            return jsonify(
                {
                    "success": True,
                    "message": "Account created successfully!",
                    "redirectUrl": url_for(
                        "login", success="Account created successfully! Please login."
                    ),
                }
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            error_message = str(e)
            logger.error(f"Database error creating user account: {error_message}")

            if "UNIQUE constraint failed" in error_message and "email" in error_message:
                return jsonify(
                    {"success": False, "message": "This email is already registered"}
                )

            return jsonify(
                {
                    "success": False,
                    "message": "Error creating account. Please try again.",
                }
            )

        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error creating user account: {str(e)}")
            return jsonify(
                {
                    "success": False,
                    "message": "Error creating account. Please try again.",
                }
            )

    except Exception as e:
        logger.error(f"Global error in verify_otp: {str(e)}")
        return jsonify(
            {"success": False, "message": "Server error. Please try again later."}
        )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Forgot password route
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email")
        recaptcha_response = request.form.get("g-recaptcha-response")

        # Validate email
        if not email or not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            return render_template(
                "forgot_password.html", error="Invalid email address"
            )

        # Verify reCAPTCHA
        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            return render_template(
                "forgot_password.html", error="Please verify you are not a robot"
            )

        user = User.query.filter_by(email=email).first()

        # Always show success even if email not found (security best practice)
        if not user:
            logger.info(f"Password reset requested for non-existent email: {email}")
            return render_template(
                "forgot_password.html",
                success="If your email is registered, you will receive a password reset link shortly.",
            )

        try:
            # Generate a secure token
            token = ts.dumps(user.email, salt="password-reset-salt")

            # Build reset URL
            reset_url = url_for("reset_password", token=token, _external=True)

            # Send password reset email
            email_sent = send_password_reset_email(user, reset_url)

            if not email_sent:
                logger.error(f"Failed to send password reset email to {email}")
                # Still show success to prevent email enumeration
            else:
                logger.info(f"Password reset email sent to {email}")

            return render_template(
                "forgot_password.html",
                success="A password reset link has been sent to your email.",
            )
        except Exception as e:
            logger.error(f"Error in forgot_password for {email}: {str(e)}")
            # Still show success to prevent email enumeration
            return render_template(
                "forgot_password.html",
                success="If your email is registered, you will receive a password reset link shortly.",
            )

    return render_template("forgot_password.html")


# Reset password with token route
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    try:
        # Verify token (valid for 1 hour)
        email = ts.loads(token, salt="password-reset-salt", max_age=3600)
    except Exception as e:
        logger.warning(f"Invalid or expired reset token: {str(e)}")
        return render_template(
            "reset_password.html",
            error="Invalid or expired reset link. Please try again.",
        )

    user = User.query.filter_by(email=email).first()
    if not user:
        logger.warning(f"Reset password token for non-existent user: {email}")
        return render_template("reset_password.html", error="Invalid reset link.")

    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Check if passwords match
        if password != confirm_password:
            return render_template(
                "reset_password.html", token=token, error="Passwords do not match"
            )

        # Check if new password meets requirements
        password_pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s])[A-Za-z\d\W]{8,}$"
        )
        if not re.match(password_pattern, password):
            return render_template(
                "reset_password.html",
                token=token,
                error="New password must meet all requirements",
            )

        # Check if the new password is the same as the old password
        if user.check_password(password):
            return render_template(
                "reset_password.html",
                token=token,
                error="New password cannot be the same as your old password",
            )

        try:
            # Update user's password
            user.set_password(password)
            db.session.commit()

            # Send notification email
            try:
                send_password_changed_notification(user)
            except Exception as e:
                logger.error(f"Failed to send password changed notification: {str(e)}")

            logger.info(f"Password reset successful for {email}")
            return redirect(
                url_for(
                    "login",
                    success="Your password has been updated successfully. Please login with your new password.",
                )
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error resetting password: {str(e)}")
            return render_template(
                "reset_password.html",
                token=token,
                error="Error resetting password. Please try again.",
            )
        except Exception as e:
            logger.error(f"Unexpected error in reset_password: {str(e)}")
            return render_template(
                "reset_password.html",
                token=token,
                error="An error occurred. Please try again.",
            )

    return render_template("reset_password.html", token=token)


# Change password route
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    # Check if password expiry forced this redirect
    password_expired = request.args.get("expired", False)

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Validate form inputs
        if not current_password or not new_password or not confirm_password:
            return render_template(
                "change_password.html",
                error="All fields are required",
                expired=password_expired,
            )

        # Check if current password is correct
        if not current_user.check_password(current_password):
            return render_template(
                "change_password.html",
                error="Current password is incorrect",
                expired=password_expired,
            )

        # Check if new password is the same as current password
        if current_password == new_password:
            return render_template(
                "change_password.html",
                error="New password cannot be the same as your current password",
                expired=password_expired,
            )

        # Check if new password meets requirements
        password_pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s])[A-Za-z\d\W]{8,}$"
        )
        if not re.match(password_pattern, new_password):
            return render_template(
                "change_password.html",
                error="New password must meet all requirements",
                expired=password_expired,
            )

        # Check if new passwords match
        if new_password != confirm_password:
            return render_template(
                "change_password.html",
                error="New passwords do not match",
                expired=password_expired,
            )

        try:
            # Change the password
            current_user.set_password(new_password)
            db.session.commit()

            # Send notification email
            try:
                send_password_changed_notification(current_user)
            except Exception as e:
                logger.error(f"Failed to send password changed notification: {str(e)}")

            logger.info(f"Password changed successfully for {current_user.email}")

            if password_expired:
                # If password was expired, log the user out to make them log in again
                logout_user()
                return redirect(
                    url_for(
                        "login",
                        success="Your password has been changed successfully. Please login with your new password.",
                    )
                )
            else:
                return render_template(
                    "change_password.html",
                    success="Your password has been changed successfully.",
                )

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error changing password: {str(e)}")
            return render_template(
                "change_password.html",
                error="Error changing password. Please try again.",
                expired=password_expired,
            )
        except Exception as e:
            logger.error(f"Unexpected error in change_password: {str(e)}")
            return render_template(
                "change_password.html",
                error="An error occurred. Please try again.",
                expired=password_expired,
            )

    return render_template("change_password.html", expired=password_expired)


# Send password reset email function
def send_password_reset_email(user, reset_url):
    html_content = f"""
    <html>
    <head>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #f9f9f9;
          padding: 20px;
        }}
        .container {{
          background-color: #ffffff;
          padding: 20px;
          border-radius: 10px;
          box-shadow: 0 0 10px rgba(0,0,0,0.1);
          max-width: 600px;
          margin: 0 auto;
        }}
        h2 {{
          color: #333;
        }}
        .button {{
          display: inline-block;
          background-color: #4285f4;
          color: white;
          text-decoration: none;
          padding: 10px 20px;
          margin: 20px 0;
          border-radius: 5px;
          font-weight: bold;
        }}
        .note {{
          font-size: 12px;
          color: #666;
          margin-top: 20px;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h2>Password Reset Request</h2>
        <p>Hello {user.name},</p>
        <p>We received a request to reset your password for your Churn Prediction System account. Click the button below to set a new password:</p>
        
        <a href="{reset_url}" class="button">Reset Your Password</a>
        
        <p>If you did not request a password reset, please ignore this email or contact us if you have concerns.</p>
        
        <p>This password reset link will expire in 1 hour.</p>
        
        <p>Thanks,<br><strong>Churn Prediction System Team</strong></p>
        
        <p class="note">If the button above doesn't work, copy and paste this URL into your browser: {reset_url}</p>
      </div>
    </body>
    </html>
    """

    return send_email(
        subject="Password Reset - Churn Prediction System",
        recipient=user.email,
        html_content=html_content,
    )


# Serve the frontend (now protected by login)
@app.route("/")
@login_required
def index():
    return render_template("index.html")


# Handle File Upload (protected)
@app.route("/upload", methods=["POST"])
@login_required
def upload_files():
    try:
        audio_files = []
        data_files = []
        chat_files = []

        if (
            "audioFiles" not in request.files
            and "dataFiles" not in request.files
            and "chatFiles" not in request.files
        ):
            return jsonify({"error": "No files uploaded"}), 400

        # Save files
        for key in request.files:
            files = request.files.getlist(key)
            for file in files:
                if file.filename == "":
                    continue

                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)

                if key == "audioFiles":
                    audio_files.append(file_path)
                elif key == "dataFiles":
                    data_files.append(file_path)
                elif key == "chatFiles":
                    chat_files.append(file_path)

        # Call your ML models here
        audio_result = process_audio_files(audio_files)
        data_result = process_data_files(data_files)
        chat_result = predict_chat(chat_files)

        final_result = further_processing(audio_result, data_result, chat_result)

        # Log that results are about to be displayed to the user
        logger.info(
            f"Results successfully prepared and about to be displayed to user: {current_user.name if current_user else 'Unknown'}"
        )

        # Send email
        thread = threading.Thread(target=send_email_async, args=(final_result,))
        thread.daemon = True
        thread.start()

        return jsonify({"result": final_result})
    except Exception as e:
        logger.error(f"Error in upload_files: {str(e)}")
        return jsonify({"error": "An error occurred while processing your files"}), 500


# Admin dashboard route
@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    users = User.query.all()
    return render_template("admin.html", users=users)


# API endpoint to delete a user
@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_user(user_id):
    # Prevent admin from deleting themselves
    if current_user.id == user_id:
        return (
            jsonify(
                {"success": False, "message": "You cannot delete your own account"}
            ),
            400,
        )

    try:
        # First check if the user exists
        user = db.session.get(User, user_id)
        if not user:
            logger.warning(f"Attempted to delete non-existent user ID: {user_id}")
            return (
                jsonify(
                    {"success": False, "message": f"User with ID {user_id} not found"}
                ),
                404,
            )

        # Check if trying to delete the last admin user
        admin_role = Role.query.filter_by(name="admin").first()
        if user.role_id == admin_role.id and not has_other_admins(user.id):
            logger.warning(f"Attempted to delete the last admin user: {user.email}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Cannot delete the last admin user. Create another admin user first.",
                    }
                ),
                400,
            )

        # Log the delete attempt
        logger.info(f"Attempting to delete user: {user.name} (ID: {user.id})")

        # Try to delete the user
        db.session.delete(user)
        db.session.commit()

        logger.info(f"User {user.name} (ID: {user.id}) deleted successfully")
        return jsonify(
            {"success": True, "message": f"User {user.name} deleted successfully"}
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        error_message = str(e)
        logger.error(f"Database error deleting user {user_id}: {error_message}")

        # Check for database constraint errors (more specific error handling)
        if "foreign key constraint" in error_message.lower():
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Cannot delete this user because they have related records in the system",
                    }
                ),
                400,
            )

        return (
            jsonify(
                {"success": False, "message": f"Error deleting user: {error_message}"}
            ),
            500,
        )
    except Exception as e:
        db.session.rollback()
        error_message = str(e)
        logger.error(f"Unexpected error deleting user {user_id}: {error_message}")
        return (
            jsonify(
                {"success": False, "message": f"Error deleting user: {error_message}"}
            ),
            500,
        )


# API endpoint to update a user
@app.route("/admin/update_user", methods=["POST"])
@login_required
@role_required("admin")
def update_user():
    try:
        data = request.json

        user_id = data.get("userId")
        name = data.get("name")
        email = data.get("email")
        role_name = data.get("role")

        if not all([user_id, name, email, role_name]):
            return (
                jsonify({"success": False, "message": "Missing required fields"}),
                400,
            )

        # Get the user by ID and handle the case when user is not found
        user = db.session.get(User, user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found during update")
            return (
                jsonify(
                    {"success": False, "message": f"User with ID {user_id} not found"}
                ),
                404,
            )

        # Make role lookup case-insensitive by using a case-insensitive comparison
        role = Role.query.filter(Role.name.ilike(role_name)).first()

        if not role:
            logger.warning(f"Role {role_name} not found during user update")
            return (
                jsonify({"success": False, "message": f"Role {role_name} not found"}),
                404,
            )

        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != int(user_id):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Email is already in use by another user",
                    }
                ),
                400,
            )

        # Check if trying to change the last admin to a regular user
        admin_role = Role.query.filter_by(name="admin").first()
        if user.role_id == admin_role.id and role.name.lower() != "admin":
            # If this is an admin user being demoted, check if there are other admins
            if not has_other_admins(user.id):
                logger.warning(f"Attempted to remove the last admin user: {user.email}")
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Cannot change role of the last admin user. Assign another user as admin first.",
                        }
                    ),
                    400,
                )

        try:
            user.name = name
            user.email = email
            user.role_id = role.id

            db.session.commit()
            logger.info(
                f"User {user.name} (ID: {user.id}) updated successfully with role {role.name}"
            )

            return jsonify(
                {
                    "success": True,
                    "message": f"User {name} updated successfully",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "role": role.name,
                    },
                }
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            error_message = str(e)
            logger.error(f"Database error updating user {user_id}: {error_message}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error updating user: {error_message}",
                    }
                ),
                500,
            )
    except Exception as e:
        error_message = str(e)
        logger.error(f"Unexpected error in update_user: {error_message}")
        return (
            jsonify(
                {"success": False, "message": f"Error updating user: {error_message}"}
            ),
            500,
        )


# Admin reset password route
@app.route("/admin/reset_password", methods=["POST"])
@login_required
@role_required("admin")
def admin_reset_password():
    try:
        data = request.json
        user_id = data.get("userId")

        if not user_id:
            logger.warning("Missing user ID in reset password request")
            return jsonify({"success": False, "message": "Missing user ID"}), 400

        # Prevent admin from resetting their own password through this route
        if int(user_id) == current_user.id:
            logger.warning(
                f"Admin attempted to reset their own password through admin interface"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Please use the regular password reset flow for your own account",
                    }
                ),
                400,
            )

        try:
            # First check if the user exists
            user = db.session.get(User, user_id)
            if not user:
                logger.warning(
                    f"Attempted to reset password for non-existent user ID: {user_id}"
                )
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"User with ID {user_id} not found",
                        }
                    ),
                    404,
                )

            logger.info(
                f"Attempting to reset password for user: {user.name} (ID: {user.id})"
            )

            # Generate a random password
            temp_password = secrets.token_urlsafe(8)
            user.set_password(temp_password)
            db.session.commit()

            logger.info(
                f"Password reset successful for user: {user.name} (ID: {user.id})"
            )

            # Send notification email
            try:
                send_password_changed_notification(user, True)
                logger.info(f"Password reset notification email sent to {user.email}")
            except Exception as email_err:
                logger.error(
                    f"Warning: Could not send password reset email: {str(email_err)}"
                )
                # Continue even if email fails, since the password was reset successfully

            return jsonify(
                {
                    "success": True,
                    "message": f"Password for {user.name} has been reset",
                    "temp_password": temp_password,
                }
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            error_message = str(e)
            logger.error(
                f"Database error resetting password for user {user_id}: {error_message}"
            )

            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error resetting password: {error_message}",
                    }
                ),
                500,
            )
    except Exception as e:
        error_message = str(e)
        logger.error(f"Unexpected error in admin_reset_password: {error_message}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Error resetting password: {error_message}",
                }
            ),
            500,
        )


# Send password changed notification
def send_password_changed_notification(user, admin_reset=False):
    subject = "Password Changed - Churn Prediction System"
    if admin_reset:
        subject = "Your Password Has Been Reset - Churn Prediction System"

    action = "changed" if not admin_reset else "reset by an administrator"

    html_content = f"""
    <html>
    <head>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #f9f9f9;
          padding: 20px;
        }}
        .container {{
          background-color: #ffffff;
          padding: 20px;
          border-radius: 10px;
          box-shadow: 0 0 10px rgba(0,0,0,0.1);
          max-width: 600px;
          margin: 0 auto;
        }}
        h2 {{
          color: #333;
        }}
        .warning {{
          color: #d9534f;
          font-weight: bold;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h2>Password {action.capitalize()}</h2>
        <p>Hello {user.name},</p>
        
        {'<p>An administrator has reset your password for your Churn Prediction System account.</p>' if admin_reset else '<p>Your password for the Churn Prediction System has been changed successfully.</p>'}
        
        {'<p class="warning">If you did not request this change, please contact your administrator immediately.</p>' if admin_reset else '<p>If you did not make this change, please contact us immediately as your account may have been compromised.</p>'}
        
        <p>Thanks,<br><strong>Churn Prediction System Team</strong></p>
      </div>
    </body>
    </html>
    """

    return send_email(subject=subject, recipient=user.email, html_content=html_content)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    logger.warning(f"CSRF Error: {str(e)}")
    # For AJAX requests, return JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return (
            jsonify(
                {"error": "CSRF token expired or invalid. Please refresh the page."}
            ),
            400,
        )

    # For regular requests, redirect to login with a message
    flash("Your session has expired. Please log in again.", "error")
    return redirect(url_for("login"))


def send_email_async(final_result):
    try:
        with app.app_context():
            send_result_email(final_result)
    except Exception as e:
        logger.error(f"Failed to send email asynchronously: {str(e)}")


def send_result_email(final_result):
    """
    Sends a well-formatted HTML email with the analysis results to admin users.
    The email template is designed to be visually appealing and clearly structured.
    """
    try:
        # Get all admin users
        admin_role = Role.query.filter_by(name="admin").first()
        if not admin_role:
            logger.error("Admin role not found when sending result email")
            return False

        admin_users = User.query.filter_by(role_id=admin_role.id).all()
        if not admin_users:
            logger.warning("No admin users found when sending result email")
            # Fallback to current user if no admins exist
            recipients = [current_user.email] if current_user else []
        else:
            recipients = [admin.email for admin in admin_users]

        if not recipients:
            logger.error("No recipients found for result email")
            return False

        # Format the data model results for better readability
        data_output = final_result.get("data_output", "N/A")
        data_output_html = format_data_output_for_email(data_output)
        # Get other result data
        audio_output = final_result.get("audio_output", "N/A")
        chat_output = final_result.get("chat_output", "N/A")
        final_decision = final_result.get(
            "final_decision", "No final decision available"
        )
        timestamp = final_result.get("timestamp", datetime.now().isoformat())
        customer_id = final_result.get("customer_id", "Unknown")
        try:
            # Format timestamp for better readability
            timestamp_obj = datetime.fromisoformat(timestamp)
            formatted_timestamp = timestamp_obj.strftime("%B %d, %Y; %H:%M:%S")
        except:
            formatted_timestamp = timestamp

        # Get triggering user info
        triggered_by = final_result.get("triggered_by", "Unknown")

        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Churn Analysis Report</title>
            <style>
                body {{
                    font-family: Arial, Helvetica, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .email-container {{
                    max-width: 650px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}                .header {{
                    background-color: #3f51b5;
                    color: #ffffff;
                    padding: 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                }}
                .customer-id {{
                    background-color: #673ab7;
                    color: #ffffff;
                    padding: 10px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 16px;
                    margin-top: -1px;
                }}
                .content {{
                    padding: 20px;
                }}
                .section {{
                    margin-bottom: 25px;
                    background-color: #f9f9f9;
                    border-radius: 6px;
                    padding: 15px;
                    border-left: 4px solid #3f51b5;
                }}
                .section.audio {{
                    border-left-color: #2196F3;
                    background-color: #e3f2fd;
                }}
                .section.data {{
                    border-left-color: #673ab7;
                    background-color: #ede7f6;
                }}
                .section.chat {{
                    border-left-color: #ff9800;
                    background-color: #fff8e1;
                }}
                .section.final {{
                    border-left-color: #4caf50;
                    background-color: #e8f5e9;
                }}
                .section h2 {{
                    margin-top: 0;
                    font-size: 18px;
                    color: #444;
                    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                    padding-bottom: 8px;
                }}
                .data-card {{
                    background-color: white;
                    border-radius: 4px;
                    padding: 12px;
                    margin-bottom: 10px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
                }}
                .data-card-header {{
                    font-weight: bold;
                    margin-bottom: 8px;
                    color: #555;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 5px;
                }}
                .data-item {{
                    margin-bottom: 5px;
                }}
                .status-stay {{
                    color: #2e7d32;
                    font-weight: bold;
                    background-color: rgba(46, 125, 50, 0.1);
                    padding: 2px 6px;
                    border-radius: 4px;
                    display: inline-block;
                }}
                .status-churn {{
                    color: #c62828;
                    font-weight: bold;
                    background-color: rgba(198, 40, 40, 0.1);
                    padding: 2px 6px;
                    border-radius: 4px;
                    display: inline-block;
                }}
                .status-positive {{
                    color: #2e7d32;
                    font-weight: bold;
                }}
                .status-negative {{
                    color: #c62828;
                    font-weight: bold;
                }}
                .footer {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-top: 1px solid #ddd;
                }}
                .timestamp {{
                    text-align: right;
                    font-size: 12px;
                    color: #757575;
                    margin-top: 20px;
                    font-style: italic;
                }}
                .user-info {{
                    text-align: right;
                    font-size: 12px;
                    color: #757575;
                    margin-top: 5px;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">                <div class="header">
                    <h1>📊 Churn Analysis Report</h1>
                </div>
                
                <div class="customer-id">
                    Customer ID: {customer_id}
                </div>
                
                <div class="content">
                    <div class="section audio">
                        <h2>Audio Analysis</h2>
                        <div>{audio_output}</div>
                    </div>
                    
                    <div class="section data">
                        <h2>Data Analysis</h2>
                        <div>{data_output_html}</div>
                    </div>
                    
                    <div class="section chat">
                        <h2>Chat Analysis</h2>
                        <div class="{get_chat_status_class(chat_output)}">{chat_output}</div>
                    </div>
                    
                    <div class="section final">
                        <h2>Final Decision</h2>
                        <div><strong>{final_decision}</strong></div>
                    </div>
                    
                    <div class="timestamp">Processed at: {formatted_timestamp}</div>
                    <div class="user-info">Analysis triggered by: {triggered_by}</div>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from the Churn Prediction System.</p>
                    <p>© {datetime.now().year} Team Sentience</p>
                </div>
            </div>
        </body>
        </html>
        """  # Send to each admin user
        for recipient in recipients:
            success = send_email(
                subject=f"📊 Churn Analysis Report - Customer ID: {customer_id}",
                recipient=recipient,
                html_content=html_content,
            )
            if not success:
                logger.warning(f"Failed to send result email to admin: {recipient}")

        return True
    except Exception as e:
        logger.error(f"Error in send_result_email: {str(e)}")
        return False


def format_data_output_for_email(data_output):
    """Helper function to format data output for the email template"""
    if not data_output:
        return "<p>No data analysis results available</p>"

    if isinstance(data_output, str):
        return f"<p>{data_output}</p>"

    # Handle array of prediction results
    if isinstance(data_output, list):
        html_output = ""
        for item in data_output:
            file_name = item.get("file", "Unknown file")
            prediction = item.get("prediction", {})
            customer_id = item.get("customer_id", "Unknown")

            if isinstance(prediction, dict):
                stay_prob = prediction.get("stay_probability", 0) * 100
                churn_prob = prediction.get("churn_probability", 0) * 100
                pred_result = (
                    "STAY" if prediction.get("prediction", 1) == 0 else "CHURN"
                )
                status_class = (
                    "status-stay" if pred_result == "STAY" else "status-churn"
                )

                html_output += f"""
                <div class="data-card">
                    <div class="data-card-header">File: {file_name}</div>
                    <div class="data-item"><strong>Stay Probability:</strong> {stay_prob:.2f}%</div>
                    <div class="data-item"><strong>Churn Probability:</strong> {churn_prob:.2f}%</div>
                    <div class="data-item"><strong>Prediction:</strong> <span class="{status_class}">{pred_result}</span></div>
                </div>
                """
            else:
                html_output += f"""
                <div class="data-card">
                    <div class="data-card-header">File: {file_name}</div>
                    <div>{prediction}</div>
                </div>
                """
        return html_output

    # If it's some other format, convert to string
    return f"<p>{str(data_output)}</p>"


def get_chat_status_class(chat_output):
    """Helper function to determine the CSS class for chat analysis status"""
    if not chat_output:
        return ""

    if chat_output.upper() == "POSITIVE":
        return "status-positive"
    elif chat_output.upper() == "NEGATIVE":
        return "status-negative"

    return ""


def process_audio_files(audio_paths):
    # Load and run audio model here
    try:
        logger.info(f"Processing {len(audio_paths)} audio file(s)")
        # Placeholder implementation
        return "audio model result"
    except Exception as e:
        logger.error(f"Error processing audio files: {str(e)}")
        return "Error processing audio"


def process_data_files(data_paths):
    # Load and run data model here
    try:
        logger.info(f"Processing {len(data_paths)} data file(s)")

        # Create an instance of the ChurnPredictionModel
        churn_model = ChurnPredictionModel()

        # Load the pre-trained model, scaler, and feature columns
        model_path = "models/output/Random_Forest_model.pkl"
        scaler_path = "models/output/scaler.pkl"
        feature_path = "models/output/feature_columns.pkl"

        # Check if model files exist before loading
        if (
            os.path.exists(model_path)
            and os.path.exists(scaler_path)
            and os.path.exists(feature_path)
        ):
            logger.info(f"Loading pre-trained model from {model_path}")
            trained_model = churn_model.load_model(
                model_path, scaler_path, feature_path
            )
            churn_model.best_model = (
                trained_model  # Set as the best model to use for prediction
            )
        else:
            logger.error(
                f"Model files not found. Please ensure the model is trained first."
            )
            return "Error: Model files not found"

        if data_paths:
            # If there are data files, use them
            sample_results = []
            customer_id = None  # Variable to store the customer ID

            for file_path in data_paths:
                logger.info(f"Processing file: {file_path}")

                # Read the data file
                if file_path.endswith(".csv"):
                    df = pd.read_csv(file_path)
                elif file_path.endswith(".xlsx"):
                    df = pd.read_excel(file_path)
                else:
                    logger.warning(f"Unsupported file format: {file_path}")
                    continue

                # Just use the first row as an example
                if not df.empty:
                    # Try to extract customer ID from the data (look for columns like CustomerID, Customer_ID, etc.)
                    possible_id_columns = [
                        "CustomerID",
                        "Customer_ID",
                        "customer_id",
                        "CustomerId",
                        "ID",
                        "Id",
                        "id",
                    ]
                    for col in possible_id_columns:
                        if col in df.columns:
                            customer_id = str(df.iloc[0][col])
                            logger.info(f"Found customer ID: {customer_id}")
                            break

                    customer_data = df.iloc[0].to_dict()
                    prediction = churn_model.predict_new_customer(customer_data)
                    sample_results.append(
                        {
                            "file": os.path.basename(file_path),
                            "prediction": prediction,
                            "customer_id": customer_id,
                        }
                    )

            return sample_results
        else:
            # If no data files provided, just return a message
            return "No data files to process"

    except Exception as e:
        logger.error(f"Error processing data files: {str(e)}")
        return f"Error processing data: {str(e)}"


def further_processing(audio_output, data_output, chat_output):
    # Combine results or do extra steps
    try:
        logger.info("Performing further processing on model outputs")

        # Create final decision based on the model outputs
        final_decision = "Customer is likely to stay with the service"

        # Structure data output properly for display
        data_output_formatted = data_output
        chat_output_temp = ""
        if chat_output == "positive":
            chat_output_temp = "POSITIVE"
        elif chat_output == "negative":
            chat_output_temp = "NEGATIVE"
        chat_output_formatted = chat_output

        # Extract customer ID from data_output if it exists
        customer_id = None
        if isinstance(data_output, list) and len(data_output) > 0:
            # Try to find customer ID in the first data output item
            for item in data_output:
                if "customer_id" in item and item["customer_id"]:
                    customer_id = item["customer_id"]
                    break

        # Return structured data that will be used for both API response and email
        result = {
            "audio_output": audio_output,
            "data_output": data_output_formatted,
            "chat_output": chat_output_formatted,
            "final_decision": final_decision,
            "timestamp": datetime.now().isoformat(),
            "triggered_by": current_user.name if current_user is not None else "System",
            "customer_id": customer_id,
        }

        return result

        return result
    except Exception as e:
        logger.error(f"Error in further processing: {str(e)}")
        return {"error": "Error in processing", "timestamp": datetime.now().isoformat()}


# Add a new admin user route - This should only be used to recover from admin loss
@app.route("/create-admin-recovery", methods=["GET"])
def create_admin_recovery():
    # Check if admin role exists
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        # Create admin role if it doesn't exist
        admin_role = Role(name="admin")
        db.session.add(admin_role)
        db.session.commit()

    # Create a recovery admin user with predefined credentials
    recovery_email = "admin@recovery.com"
    recovery_password = "Admin123!"  # You'll want to change this immediately

    # Check if recovery admin already exists
    existing_admin = User.query.filter_by(email=recovery_email).first()
    if existing_admin:
        # Check if existing user is already an admin
        if existing_admin.role_id == admin_role.id:
            return jsonify(
                {
                    "success": True,
                    "message": "Admin recovery account already exists. Please login with the recovery credentials.",
                }
            )
        else:
            # Update existing user to admin role
            existing_admin.role_id = admin_role.id
            db.session.commit()
            return jsonify(
                {
                    "success": True,
                    "message": "Existing account updated to admin role. Please login with the recovery credentials.",
                }
            )

    # Create new admin user
    admin_user = User(
        name="Admin Recovery", email=recovery_email, role_id=admin_role.id
    )
    admin_user.set_password(recovery_password)

    try:
        db.session.add(admin_user)
        db.session.commit()
        logger.info(f"Admin recovery account created successfully")

        return jsonify(
            {
                "success": True,
                "message": "Admin recovery account created successfully.",
                "email": recovery_email,
                "password": recovery_password,
                "note": "Please login and change this password immediately!",
            }
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating admin recovery account: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Error creating admin recovery account: {str(e)}",
                }
            ),
            500,
        )


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    # Return JSON response for API requests
    if (
        request.path.startswith("/api/")
        or request.headers.get("Content-Type") == "application/json"
    ):
        return jsonify({"error": "An unexpected error occurred"}), 500
    # Return error page for regular requests
    return render_template("error.html", error="An unexpected error occurred"), 500


if __name__ == "__main__":
    # Configure file handler for logging
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # Call the create tables function before starting the app
    create_tables_and_roles()

    app.run(host="0.0.0.0", port=8000, debug=True)
