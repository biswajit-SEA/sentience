# Azure deployment integration module for hackathon.py

import os
import logging
from dotenv import load_dotenv
from flask import Flask

# Load environment variables from .env file if it exists
load_dotenv()

def create_azure_app():
    """
    Create and configure a Flask application with Azure integrations
    """
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configure basic settings
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Setup file logging (will be replaced by Azure Application Insights)
    if not app.config['DEBUG']:
        try:
            file_handler = logging.FileHandler('app.log')
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to set up file logging: {str(e)}")
    
    # Add Azure diagnostics logging
    try:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Azure Flask app initialized")
    except Exception as e:
        logger.error(f"Failed to set up Azure diagnostics logging: {str(e)}")
    
    # Log the environment variables (but not secret ones)
    app.logger.info(f"WEBSITE_SITE_NAME: {os.environ.get('WEBSITE_SITE_NAME', 'Not set')}")
    app.logger.info(f"Debug mode: {app.config['DEBUG']}")
    
    # Configure Azure services
    try:
        from azure_integration import init_azure_config, setup_azure_services
        
        # Initialize Azure configuration
        azure_config = init_azure_config()
        
        # Setup Azure services
        app = setup_azure_services(app, azure_config)
        
        logger.info("Azure services initialized successfully")
    except ImportError as e:
        logger.warning(f"Azure integration modules not available: {str(e)}")
        logger.warning("Azure services will not be enabled")
    except Exception as e:
        logger.error(f"Failed to initialize Azure services: {str(e)}")
    
    # Configure database
    try:
        from flask_sqlalchemy import SQLAlchemy
        
        # Check if Azure SQL connection string is available
        sql_connection_string = os.getenv('AZURE_SQL_CONNECTION_STRING')
        if sql_connection_string:
            app.config['SQLALCHEMY_DATABASE_URI'] = sql_connection_string
            logger.info("Using Azure SQL Database")
        else:
            # Fall back to SQLite
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/db.sqlite'
            logger.info("Using SQLite Database")
        
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize SQLAlchemy
        db = SQLAlchemy(app)
        app.config['DB'] = db
        
        logger.info("Database configuration completed")
    except ImportError:
        logger.error("SQLAlchemy not installed")
    except Exception as e:
        logger.error(f"Failed to configure database: {str(e)}")
    
    # Configure upload folder
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create a health check endpoint for Azure
    @app.route("/health")
    def health_check():
        from flask import jsonify
        return jsonify({"status": "healthy"}), 200
    
    return app

# This can be used as an entry point for Azure App Service
app = create_azure_app()

# Import the main application code
try:
    # Import the Flask application from hackathon.py
    from hackathon import app as hackathon_app
    
    # Merge routes and configurations from hackathon_app to our app
    for route in hackathon_app.url_map.iter_rules():
        # Skip the static route as it's already defined
        if str(route) == '/static/<path:filename>':
            continue
            
        view_func = hackathon_app.view_functions[route.endpoint]
        methods = route.methods
        app.add_url_rule(str(route), route.endpoint, view_func, methods=methods)
        
    # Copy over configurations from hackathon_app
    for key, value in hackathon_app.config.items():
        if key not in app.config:
            app.config[key] = value
            
    app.logger.info(f"Successfully imported routes from hackathon.py")
except ImportError as e:
    app.logger.error(f"Failed to import hackathon.py: {str(e)} - Application may not function correctly")
except Exception as e:
    app.logger.error(f"Error configuring application: {str(e)}")

# The Azure App Service will use this 'app' object
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
