from eoms import app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(from_email, to_email, subject, body):
    """
    Sends an email using the SMTP settings defined in the application's config.py file.
    """
    # Get email configuration directly from the app config
    # This ensures we use the credentials you set up.
    EMAIL_HOST = app.config.get('MAIL_SERVER')
    EMAIL_PORT = app.config.get('MAIL_PORT')
    EMAIL_HOST_USER = app.config.get('MAIL_USERNAME')
    EMAIL_HOST_PASSWORD = app.config.get('MAIL_PASSWORD')
    
    # Compose the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Connect to the SMTP server (e.g., Gmail)
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        # Login using the App Password
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        text = msg.as_string()
        # Send the email
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Successfully sent password reset email to {to_email}")
        return {'success': True}
    except Exception as e:
        # This will print any login or sending errors to your console for debugging
        print(f"ERROR sending email: {e}")
        return {'success': False, 'message': f'{e}'}
