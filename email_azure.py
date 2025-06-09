# Updated email functions for Azure integration

def send_email_azure_adapted(app, subject, recipient, html_content, max_retries=2):
    """
    Unified email sending function that works with both Azure and original implementation
    
    Args:
        app: Flask application instance
        subject: Email subject
        recipient: Recipient email address
        html_content: HTML content of the email
        max_retries: Number of retry attempts for failed sends
        
    Returns:
        True if successful, False otherwise
    """
    # Check if Azure Communication Services is configured
    if app.config.get('EMAIL_PROVIDER') == 'azure_communication':
        from azure_integration import azure_send_email
        return azure_send_email(app, subject, recipient, html_content, max_retries)
    
    # Fall back to original implementation
    try:
        from flask_mail import Message
        from threading import Thread
        
        # Create message
        msg = Message(subject, recipients=[recipient])
        msg.html = html_content
        
        # Get the mail extension
        mail = app.extensions.get('mail')
        if not mail:
            app.logger.error("Flask-Mail not initialized")
            return False
        
        # Function to send email with retries
        def send_with_retries(message, retry_count=0):
            try:
                mail.send(message)
                app.logger.info(f"Email sent successfully to {recipient}")
                return True
            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    app.logger.error(f"Failed to send email after {max_retries} attempts: {str(e)}")
                    return False
                app.logger.warning(f"Email send attempt {retry_count} failed. Retrying...")
                return send_with_retries(message, retry_count)
        
        # Start a background thread to send email
        thread = Thread(target=send_with_retries, args=(msg,))
        thread.start()
        
        return True
    except Exception as e:
        app.logger.error(f"Error setting up email: {str(e)}")
        return False

# Wrapper function to maintain compatibility with existing code
def send_email(subject, recipient, html_content, max_retries=2):
    """
    Wrapper for send_email_azure_adapted that maintains compatibility with existing code
    """
    from flask import current_app
    return send_email_azure_adapted(current_app, subject, recipient, html_content, max_retries)
