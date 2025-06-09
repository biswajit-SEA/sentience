# Azure-adapted upload files function

from flask import request, jsonify, current_app
from flask_login import current_user, login_required
import threading
import logging
import os
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

@login_required
def upload_files_azure():
    """
    Azure-adapted version of the upload_files function
    """
    try:
        audio_files = []
        data_files = []
        chat_files = []

        if (
            "audioFiles" not in request.files
            and "dataFiles" not in request.files
            and "chatFiles" not in request.files
        ):
            return jsonify({"error": "No files provided"}), 400

        # Import the Azure-adapted file saving function
        from file_operations_azure import save_file_azure_adapted

        # Process and save files by category
        for key in request.files:
            files = request.files.getlist(key)
            for file in files:
                if file.filename == "":
                    continue
                
                # Determine the category folder
                category = None
                if key == "audioFiles":
                    category = "audio"
                elif key == "dataFiles":
                    category = "data"
                elif key == "chatFiles":
                    category = "chat"
                
                # Save the file using the Azure-adapted function
                file_path = save_file_azure_adapted(file, category)
                
                # Add to the appropriate list
                if key == "audioFiles":
                    audio_files.append(file_path)
                elif key == "dataFiles":
                    data_files.append(file_path)
                elif key == "chatFiles":
                    chat_files.append(file_path)

        # Call ML models with the file paths
        audio_result = process_audio_files(audio_files)
        data_result = process_data_files(data_files)
        chat_result = predict_chat(chat_files)

        final_result = further_processing(audio_result, data_result, chat_result)

        # Log that results are about to be displayed to the user
        logger.info(
            f"Results successfully prepared and about to be displayed to user: {current_user.name if current_user else 'Unknown'}"
        )

        # Send email asynchronously
        thread = threading.Thread(target=send_email_async, args=(final_result,))
        thread.daemon = True
        thread.start()

        return jsonify({"result": final_result})
    except Exception as e:
        logger.error(f"Error in upload_files: {str(e)}")
        return jsonify({"error": "An error occurred while processing your files"}), 500

# These functions should be imported from your original module
# They are listed here as placeholders
def process_audio_files(audio_paths):
    # Import from your original module
    from hackathon import process_audio_files as original_process
    return original_process(audio_paths)

def process_data_files(data_paths):
    # Import from your original module
    from hackathon import process_data_files as original_process
    return original_process(data_paths)

def predict_chat(chat_files):
    # Import from your original module
    from hackathon import predict_chat as original_predict
    return original_predict(chat_files)

def further_processing(audio_output, data_output, chat_output):
    # Import from your original module
    from hackathon import further_processing as original_processing
    return original_processing(audio_output, data_output, chat_output)

def send_email_async(final_result):
    # Import from your original module
    from hackathon import send_email_async as original_send
    return original_send(final_result)
