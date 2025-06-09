# Azure-adapted file operations for Churn Prediction System

from flask import current_app
import os
from azure.storage.blob import BlobClient, ContentSettings

def save_file_to_azure_blob(file_obj, filename, content_type=None):
    """
    Save a file to Azure Blob Storage
    
    Args:
        file_obj: The file object to save
        filename: The name to give the file in blob storage
        content_type: The MIME type of the file
        
    Returns:
        The URL of the saved blob
    """
    if 'AZURE_BLOB_SERVICE_CLIENT' not in current_app.config:
        current_app.logger.error("Azure Blob Storage not configured")
        return None
    
    try:
        blob_service_client = current_app.config['AZURE_BLOB_SERVICE_CLIENT']
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
        
        current_app.logger.info(f"File {filename} uploaded to Azure Blob Storage")
        return blob_url
    
    except Exception as e:
        current_app.logger.error(f"Error uploading file to Azure Blob Storage: {str(e)}")
        return None

def get_file_from_azure_blob(filename):
    """
    Get a file from Azure Blob Storage
    
    Args:
        filename: The name of the file in blob storage
        
    Returns:
        The file data as bytes
    """
    if 'AZURE_BLOB_SERVICE_CLIENT' not in current_app.config:
        current_app.logger.error("Azure Blob Storage not configured")
        return None
    
    try:
        blob_service_client = current_app.config['AZURE_BLOB_SERVICE_CLIENT']
        container_name = "uploads"
        
        # Create a blob client
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=filename
        )
        
        # Download the blob
        blob_data = blob_client.download_blob()
        file_data = blob_data.readall()
        
        current_app.logger.info(f"File {filename} downloaded from Azure Blob Storage")
        return file_data
    
    except Exception as e:
        current_app.logger.error(f"Error downloading file from Azure Blob Storage: {str(e)}")
        return None

def delete_file_from_azure_blob(filename):
    """
    Delete a file from Azure Blob Storage
    
    Args:
        filename: The name of the file in blob storage
        
    Returns:
        True if successful, False otherwise
    """
    if 'AZURE_BLOB_SERVICE_CLIENT' not in current_app.config:
        current_app.logger.error("Azure Blob Storage not configured")
        return False
    
    try:
        blob_service_client = current_app.config['AZURE_BLOB_SERVICE_CLIENT']
        container_name = "uploads"
        
        # Create a blob client
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=filename
        )
        
        # Delete the blob
        blob_client.delete_blob()
        
        current_app.logger.info(f"File {filename} deleted from Azure Blob Storage")
        return True
    
    except Exception as e:
        current_app.logger.error(f"Error deleting file from Azure Blob Storage: {str(e)}")
        return False
