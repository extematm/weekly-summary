import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, to_email, from_email, password):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Office 365/Outlook SMTP settings
    smtp_server = "smtp.office365.com"
    smtp_port = 587

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)

# Example usage:
# send_email("Weekly Summary", "Here is the summary...", "recipient@company.com", "your@company.com", "your_password")