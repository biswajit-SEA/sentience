# Azure Integration Module for Churn Prediction System

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize configurations
def init_azure_config():
    """
    Initialize Azure configuration dictionary
    """
    config = {
        'AZURE_STORAGE_CONNECTION_STRING': os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
        'AZURE_SQL_CONNECTION_STRING': os.getenv('AZURE_SQL_CONNECTION_STRING'),
        'AZURE_COMMUNICATION_CONNECTION_STRING': os.getenv('AZURE_COMMUNICATION_CONNECTION_STRING'),
        'APPINSIGHTS_INSTRUMENTATIONKEY': os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY'),
        'DEFAULT_FROM_EMAIL': os.getenv('DEFAULT_FROM_EMAIL', 'noreply@churnpredictionsystem.com')
    }
    
    # Check if required configurations are present
    missing_configs = [key for key, value in config.items() if not value and key != 'DEFAULT_FROM_EMAIL']
    if missing_configs:
        print(f"Warning: Missing Azure configurations: {', '.join(missing_configs)}")
        print("Some Azure services may not function correctly.")
    
    return config

# Setup Azure services
def setup_azure_services(app, config):
    """
    Set up all Azure services for the application
    """
    # Import Azure service modules only if configurations are available
    if config.get('APPINSIGHTS_INSTRUMENTATIONKEY'):
        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            from opencensus.ext.flask.flask_middleware import FlaskMiddleware
            from opencensus.trace.samplers import ProbabilitySampler
            
            # Set up Azure Application Insights
            azure_handler = AzureLogHandler(connection_string=f"InstrumentationKey={config['APPINSIGHTS_INSTRUMENTATIONKEY']}")
            app.logger.addHandler(azure_handler)
            
            # Set up request tracking
            middleware = FlaskMiddleware(
                app,
                exporter=None,
                sampler=ProbabilitySampler(rate=1.0),
            )
            
            app.logger.info("Azure Application Insights configured successfully")
        except ImportError:
            app.logger.warning("Azure Application Insights packages not installed. Skipping configuration.")
        except Exception as e:
            app.logger.error(f"Failed to configure Azure Application Insights: {str(e)}")
    
    # Set up Azure Blob Storage
    if config.get('AZURE_STORAGE_CONNECTION_STRING'):
        try:
            from azure.storage.blob import BlobServiceClient
            
            # Create the BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(config['AZURE_STORAGE_CONNECTION_STRING'])
            
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
            
            app.logger.info("Azure Blob Storage configured successfully")
        except ImportError:
            app.logger.warning("Azure Blob Storage packages not installed. Skipping configuration.")
        except Exception as e:
            app.logger.error(f"Failed to configure Azure Blob Storage: {str(e)}")
    
    # Set up Azure Communication Services for email
    if config.get('AZURE_COMMUNICATION_CONNECTION_STRING'):
        try:
            from azure.communication.email import EmailClient
            
            email_client = EmailClient.from_connection_string(config['AZURE_COMMUNICATION_CONNECTION_STRING'])
            app.config['AZURE_EMAIL_CLIENT'] = email_client
            app.config['EMAIL_PROVIDER'] = 'azure_communication'
            app.config['DEFAULT_FROM_EMAIL'] = config['DEFAULT_FROM_EMAIL']
            
            app.logger.info("Azure Communication Services configured successfully")
        except ImportError:
            app.logger.warning("Azure Communication Services packages not installed. Skipping configuration.")
        except Exception as e:
            app.logger.error(f"Failed to configure Azure Communication Services: {str(e)}")
    
    return app

# Helper functions for Azure file operations
def azure_save_file(app, file_obj, filename, content_type=None):
    """
    Save a file to Azure Blob Storage
    
    Args:
        app: Flask application instance
        file_obj: The file object to save
        filename: The name to give the file in blob storage
        content_type: The MIME type of the file
        
    Returns:
        The URL of the saved blob, or None if failed
    """
    if 'AZURE_BLOB_SERVICE_CLIENT' not in app.config:
        app.logger.warning("Azure Blob Storage not configured. Falling back to local storage.")
        return None
    
    try:
        from azure.storage.blob import ContentSettings
        
        blob_service_client = app.config['AZURE_BLOB_SERVICE_CLIENT']
        container_name = "uploads"
        
        # Create a blob client
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=filename
        )
        
        # Set content settings if provided
        content_settings = None
        if content_type:
            content_settings = ContentSettings(content_type=content_type)
        
        # Upload the file
        file_obj.seek(0)  # Go to the beginning of the file
        blob_client.upload_blob(file_obj, overwrite=True, content_settings=content_settings)
        
        # Get the URL
        blob_url = blob_client.url
        
        app.logger.info(f"File {filename} uploaded to Azure Blob Storage")
        return blob_url
    
    except Exception as e:
        app.logger.error(f"Error uploading file to Azure Blob Storage: {str(e)}")
        return None

# Azure email function
def azure_send_email(app, subject, recipient, html_content, max_retries=2):
    """
    Send an email using Azure Communication Services
    
    Args:
        app: Flask application instance
        subject: Email subject
        recipient: Recipient email address
        html_content: HTML content of the email
        max_retries: Number of retry attempts for failed sends
        
    Returns:
        True if successful, False otherwise
    """
    if 'AZURE_EMAIL_CLIENT' not in app.config:
        app.logger.warning("Azure Communication Services not configured. Email will not be sent.")
        return False
    
    try:
        from azure.communication.email import EmailContent, EmailAddress, EmailMessage, EmailRecipients
        
        email_client = app.config['AZURE_EMAIL_CLIENT']
        sender = app.config.get('DEFAULT_FROM_EMAIL', 'no-reply@churnpredictionsystem.com')
        
        # Create the email message
        message = EmailMessage(
            sender=sender,
            content=EmailContent(
                subject=subject,
                html=html_content
            ),
            recipients=EmailRecipients(
                to=[EmailAddress(email=recipient)]
            )
        )
        
        # Send the email
        retry_count = 0
        while retry_count <= max_retries:
            try:
                poller = email_client.begin_send(message)
                response = poller.result()
                
                # Log success
                app.logger.info(f"Email sent successfully to {recipient}, message ID: {response.message_id}")
                return True
            
            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    app.logger.error(f"Failed to send email after {max_retries} attempts: {str(e)}")
                    return False
                app.logger.warning(f"Email send attempt {retry_count} failed: {str(e)}. Retrying...")
    
    except Exception as e:
        app.logger.error(f"Error setting up email: {str(e)}")
        return False
