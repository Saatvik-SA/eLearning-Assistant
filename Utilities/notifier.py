# --- Utilities/notifier.py ---
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import mimetypes

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email_with_attachment(subject, body, to_email, attachment_path=None):
    """Send an email with optional attachment(s) using credentials from environment variables."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(body)
    # Support both single file and list of files
    if attachment_path:
        if isinstance(attachment_path, str):
            attachment_path = [attachment_path]
        for file in attachment_path:
            if not os.path.exists(file):
                continue
            ctype, encoding = mimetypes.guess_type(file)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            with open(file, "rb") as f:
                msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(file))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
