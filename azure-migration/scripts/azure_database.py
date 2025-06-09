# Azure database configuration for Churn Prediction System

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def configure_azure_sql_database(app):
    """
    Configure Flask application to use Azure SQL Database
    
    Args:
        app: Flask application instance
        
    Returns:
        SQLAlchemy database instance
    """
    # Get connection string from environment variables
    connection_string = os.getenv('AZURE_SQL_CONNECTION_STRING')
    
    if not connection_string:
        app.logger.warning("Azure SQL connection string not found. Using SQLite database.")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/db.sqlite'
    else:
        # Configure SQLAlchemy with the Azure SQL connection string
        app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    
    # Other SQLAlchemy settings
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)
    
    return db

def create_tables(app, db):
    """
    Create database tables based on SQLAlchemy models
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    with app.app_context():
        # Create all tables
        db.create_all()
        
        app.logger.info("Database tables created successfully.")

# Sample code to set up and migrate database
def setup_and_migrate_database():
    """
    Set up and migrate database to Azure SQL
    """
    # Create a temporary Flask app
    app = Flask(__name__)
    
    # Configure the app to use Azure SQL
    db = configure_azure_sql_database(app)
    
    # Import models (must be done after db is defined)
    from models import User, Role, OTPVerification, RateLimit
    
    # Create tables
    create_tables(app, db)
    
    # You would typically use Flask-Migrate for more complex migrations
    # This is just a simple example for creating the initial schema
