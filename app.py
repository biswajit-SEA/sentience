"""
Self-contained Flask application for Azure App Service.
This file contains everything needed to run a basic version of the app.
"""

import os
import logging
from flask import Flask, jsonify, render_template_string, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'development-key-for-azure-deployment')

# Basic HTML template for the home page
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Azure App Service Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f0f2f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 800px;
            width: 100%;
            text-align: center;
        }
        h1 {
            color: #0078d4;
        }
        p {
            color: #333;
            line-height: 1.6;
        }
        .success {
            color: green;
            font-weight: bold;
        }
        .info {
            margin-top: 30px;
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 4px;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Flask Application on Azure App Service</h1>
        <p class="success">✅ Your application is running successfully!</p>
        
        <p>This is a self-contained Flask application deployed to Azure App Service.</p>
        
        <div class="info">
            <h3>Environment Information:</h3>
            <p>Python Version: {{ python_version }}</p>
            <p>Flask Version: {{ flask_version }}</p>
            <p>Request Method: {{ request_method }}</p>
            <p>Request Path: {{ request_path }}</p>
            <p>Azure Website Name: {{ website_name }}</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Render the home page with system information"""
    import sys
    import flask
    
    context = {
        'python_version': sys.version,
        'flask_version': flask.__version__,
        'request_method': request.method,
        'request_path': request.path,
        'website_name': os.environ.get('WEBSITE_SITE_NAME', 'Local Development')
    }
    
    return render_template_string(HOME_TEMPLATE, **context)

@app.route('/api/status')
def status():
    """Return the application status as JSON"""
    import sys
    import platform
    
    status_info = {
        'status': 'healthy',
        'python_version': sys.version,
        'platform': platform.platform(),
        'environment': os.environ.get('FLASK_ENV', 'production')
    }
    
    return jsonify(status_info)

@app.route('/api/echo', methods=['GET', 'POST'])
def echo():
    """Echo back the request data"""
    if request.method == 'POST':
        try:
            data = request.get_json(silent=True) or {}
        except Exception as e:
            data = {'error': str(e)}
    else:
        data = dict(request.args)
    
    return jsonify({
        'method': request.method,
        'data': data,
        'headers': dict(request.headers)
    })

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Page not found',
        'status_code': 404,
        'path': request.path
    }), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return jsonify({
        'error': 'Internal server error',
        'status_code': 500
    }), 500

# Create uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)

# Run the application if executed directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
