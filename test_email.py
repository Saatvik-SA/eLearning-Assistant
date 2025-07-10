import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("PARENT_EMAIL")

msg = EmailMessage()
msg["Subject"] = "Test Email from eLearning Assistant"
msg["From"] = EMAIL_USER
msg["To"] = TO_EMAIL
msg.set_content("This is a test email to confirm SMTP setup.")

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
        print("Email sent successfully!")
except Exception as e:
    print("Email failed:", e)
