"""
Alternative entry point for Azure App Service.
"""

import os
import sys
import logging

# Basic configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('azure')

# Make sure we can import from the current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # First try to import from hackathon.py directly
    logger.info("Trying to import app from hackathon.py")
    from hackathon import app
    logger.info("Successfully imported app from hackathon.py")
except Exception as e:
    logger.warning(f"Could not import from hackathon.py: {e}")
    
    # Fall back to our application.py
    try:
        logger.info("Trying to import app from application.py")
        from application import app
        logger.info("Successfully imported app from application.py")
    except Exception as e:
        logger.error(f"Could not import from application.py: {e}")
        
        # Create a minimal Flask app as a last resort
        from flask import Flask, jsonify
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return "Application Error: Could not load the main application. Check logs for details."
        
        @app.route('/health')
        def health():
            return jsonify({"status": "error", "message": "Main app failed to load"}), 500

# The Azure App Service will use this 'app' object
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
