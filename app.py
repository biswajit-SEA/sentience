"""
Minimal Flask application for Azure App Service.
This file serves as a simple entry point for Azure App Service.
"""

from flask import Flask, jsonify

# Create a simple Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Azure App Service is running. This is a minimal Flask application."

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

# The Azure App Service will use this 'app' object
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
