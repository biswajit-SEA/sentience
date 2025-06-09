# Azure Adaptations for Churn Prediction System

import os
import logging
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.communication.email import EmailClient
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.samplers import ProbabilitySampler
import redis

# Load environment variables
load_dotenv()

def setup_azure_blob_storage(app):
    """Configure Azure Blob Storage for file uploads"""
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        app.logger.warning("Azure Storage connection string not found. File uploads will not work.")
        return None
    
    try:
        # Create the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Create a container if it doesn't exist
        container_name = "uploads"
        try:
            container_client = blob_service_client.get_container_client(container_name)
            # Check if container exists
            container_client.get_container_properties()
        except Exception:
            # Create the container
            container_client = blob_service_client.create_container(container_name)
        
        app.config['AZURE_BLOB_SERVICE_CLIENT'] = blob_service_client
        app.config['AZURE_BLOB_CONTAINER_CLIENT'] = container_client
        app.config['UPLOAD_PROVIDER'] = 'azure_blob'
        
        app.logger.info("Azure Blob Storage configured successfully.")
        return blob_service_client
    except Exception as e:
        app.logger.error(f"Failed to configure Azure Blob Storage: {str(e)}")
        return None

def setup_azure_email_service(app):
    """Configure Azure Communication Services for email"""
    connection_string = os.getenv('AZURE_COMMUNICATION_CONNECTION_STRING')
    if not connection_string:
        app.logger.warning("Azure Communication Services connection string not found. Email sending will not work.")
        return None
    
    try:
        email_client = EmailClient.from_connection_string(connection_string)
        app.config['AZURE_EMAIL_CLIENT'] = email_client
        app.config['EMAIL_PROVIDER'] = 'azure_communication'
        
        app.logger.info("Azure Communication Services configured successfully.")
        return email_client
    except Exception as e:
        app.logger.error(f"Failed to configure Azure Communication Services: {str(e)}")
        return None

def setup_azure_logging(app):
    """Configure Azure Application Insights for logging"""
    instrumentation_key = os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY')
    if not instrumentation_key:
        app.logger.warning("Application Insights instrumentation key not found. Advanced logging will not be available.")
        return
    
    try:
        # Set up Azure logging
        azure_handler = AzureLogHandler(connection_string=f'InstrumentationKey={instrumentation_key}')
        azure_handler.setLevel(logging.INFO)
        app.logger.addHandler(azure_handler)
        
        # Set up request tracking
        middleware = FlaskMiddleware(
            app,
            exporter=None,
            sampler=ProbabilitySampler(rate=1.0),
        )
        
        app.logger.info("Azure Application Insights configured successfully.")
    except Exception as e:
        app.logger.error(f"Failed to configure Azure Application Insights: {str(e)}")

def setup_azure_redis(app):
    """Configure Azure Redis Cache for session storage"""
    redis_connection_string = os.getenv('AZURE_REDIS_CONNECTION_STRING')
    if not redis_connection_string:
        app.logger.warning("Azure Redis connection string not found. Session storage will use default.")
        return None
    
    try:
        # Parse connection string
        # Format: rediss://username:password@host:port
        redis_client = redis.from_url(redis_connection_string)
        
        # Test connection
        redis_client.ping()
        
        # Configure Flask session to use Redis
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = redis_client
        app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
        
        app.logger.info("Azure Redis Cache configured successfully.")
        return redis_client
    except Exception as e:
        app.logger.error(f"Failed to configure Azure Redis Cache: {str(e)}")
        return None
