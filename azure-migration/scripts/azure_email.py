# Azure-adapted email functionality for Churn Prediction System

from flask import current_app
from azure.communication.email import EmailClient, EmailContent, EmailAddress, EmailMessage, EmailRecipients
import logging

def send_email_via_azure(subject, recipient, html_content, max_retries=2):
    """
    Send an email using Azure Communication Services
    
    Args:
        subject: Email subject
        recipient: Recipient email address
        html_content: HTML content of the email
        max_retries: Number of retry attempts for failed sends
        
    Returns:
        True if successful, False otherwise
    """
    if 'AZURE_EMAIL_CLIENT' not in current_app.config:
        current_app.logger.error("Azure Communication Services not configured")
        return False
    
    try:
        email_client = current_app.config['AZURE_EMAIL_CLIENT']
        sender = current_app.config.get('DEFAULT_FROM_EMAIL', 'no-reply@churnpredictionsystem.com')
        
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
                current_app.logger.info(f"Email sent successfully to {recipient}, message ID: {response.message_id}")
                return True
            
            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    current_app.logger.error(f"Failed to send email after {max_retries} attempts: {str(e)}")
                    return False
                current_app.logger.warning(f"Email send attempt {retry_count} failed: {str(e)}. Retrying...")
    
    except Exception as e:
        current_app.logger.error(f"Error setting up email: {str(e)}")
        return False
