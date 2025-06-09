"""
Azure App Service entry point for Flask application.
This module serves as the entry point for Azure App Service.
"""

import os
import logging
import sys

# Ensure the current directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging first thing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('azure_app')
logger.info("Starting Azure application...")

try:
    # Import the main application
    from hackathon import app
    logger.info("Successfully imported Flask app from hackathon.py")
except ImportError as e:
    logger.error(f"Failed to import app from hackathon.py: {e}")
    # Fallback to creating a simple app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Application startup error. Check logs for details."
    
    @app.route('/health')
    def health():
        return jsonify({"status": "error", "message": "Main app failed to load"}), 500
except Exception as e:
    logger.error(f"Unexpected error during import: {e}")
    raise

# Add a health check endpoint
@app.route('/health-check')
def health_check():
    from flask import jsonify
    return jsonify({"status": "healthy"}), 200

# Azure expects app to be global
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
