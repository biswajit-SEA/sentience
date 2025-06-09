"""
Azure App Service entry point for Flask application.
This is a simple module that serves as the entry point for Azure App Service.
"""

import os
import sys
import logging

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('azure_app')
logger.info("Starting Azure application...")

# Make sure the current directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    logger.info(f"Added {current_dir} to Python path")

# Create a simple Flask app in case imports fail
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# Try to import the main app from hackathon.py
try:
    logger.info("Attempting to import Flask app from hackathon.py")
    # Import the main application module
    import hackathon
    
    # Get the Flask app from hackathon.py
    main_app = hackathon.app
    logger.info("Successfully imported Flask app from hackathon.py")
    
    # Register all routes from the main app to our app
    for rule in main_app.url_map.iter_rules():
        # Skip the static route as it might already be defined
        if str(rule).startswith('/static/'):
            continue
        
        endpoint = rule.endpoint
        view_func = main_app.view_functions[endpoint]
        methods = rule.methods
        
        # Add the route to our app
        app.add_url_rule(str(rule), endpoint, view_func, methods=methods)
    
    # Copy over important configurations
    app.secret_key = main_app.secret_key
    app.config.update(main_app.config)
    
    # Register any error handlers
    for code, handler in main_app.error_handler_spec.get(None, {}).items():
        for exception, func in handler.items():
            app.register_error_handler(exception, func)
    
    # Print some debug info
    logger.info(f"Registered {len(list(app.url_map.iter_rules()))} routes")
    logger.info("Application successfully configured")
    
except Exception as e:
    logger.error(f"Failed to import hackathon app: {str(e)}")
    logger.error("The application will run with limited functionality")

# Always make sure we have an upload folder
os.makedirs('uploads', exist_ok=True)

# The Azure App Service will use this 'app' object
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
