# File operations adapted for Azure Blob Storage

import os
from flask import current_app
from werkzeug.utils import secure_filename

def save_file_azure_adapted(file, category_folder=None):
    """
    Save a file to either Azure Blob Storage or local filesystem
    
    Args:
        file: The file object to save
        category_folder: Optional subfolder (audio, data, chat)
        
    Returns:
        The path to the saved file
    """
    filename = secure_filename(file.filename)
    
    # Add category prefix to filename if provided
    if category_folder:
        filename = f"{category_folder}/{filename}"
    
    # Check if Azure Blob Storage is configured
    if current_app.config.get('UPLOAD_PROVIDER') == 'azure_blob':
        try:
            from azure_integration import azure_save_file
            
            # Get content type
            content_type = file.content_type if hasattr(file, 'content_type') else None
            
            # Save to Azure Blob Storage
            blob_url = azure_save_file(current_app, file, filename, content_type)
            
            if blob_url:
                current_app.logger.info(f"File {filename} saved to Azure Blob Storage")
                return blob_url
            else:
                # Fall back to local storage if Azure fails
                current_app.logger.warning(f"Failed to save {filename} to Azure. Falling back to local storage.")
        except Exception as e:
            current_app.logger.error(f"Error saving to Azure Blob Storage: {str(e)}")
            current_app.logger.warning(f"Falling back to local storage for {filename}")
    
    # Fall back to local storage
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    # Create directory if it doesn't exist
    if category_folder:
        folder_path = os.path.join(upload_folder, category_folder)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, os.path.basename(filename))
    else:
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
    
    # Save the file
    file.save(file_path)
    current_app.logger.info(f"File {filename} saved to local storage")
    
    return file_path

def get_file_azure_adapted(filename):
    """
    Get a file from either Azure Blob Storage or local filesystem
    
    Args:
        filename: The name of the file
        
    Returns:
        The file data
    """
    # Check if Azure Blob Storage is configured
    if current_app.config.get('UPLOAD_PROVIDER') == 'azure_blob':
        try:
            from azure.storage.blob import BlobClient
            
            blob_service_client = current_app.config.get('AZURE_BLOB_SERVICE_CLIENT')
            if blob_service_client:
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
            current_app.logger.error(f"Error downloading from Azure Blob Storage: {str(e)}")
            current_app.logger.warning(f"Falling back to local storage for {filename}")
    
    # Fall back to local storage
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    file_path = os.path.join(upload_folder, filename)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            file_data = f.read()
        current_app.logger.info(f"File {filename} read from local storage")
        return file_data
    
    current_app.logger.error(f"File {filename} not found in local storage")
    return None
