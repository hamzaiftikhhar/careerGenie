from pathlib import Path
from typing import Any, Dict

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Template

from app.core.config import settings

# Configure FastMail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.EMAILS_FROM_NAME,
    MAIL_STARTTLS=settings.SMTP_TLS,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# Path to templates directory
templates_dir = Path(__file__).parent.parent / "templates"

def send_verification_email(email_to: str, token: str, username: str) -> None:
    """
    Send email verification email.
    """
    # Load email template
    with open(templates_dir / "email_verification.html") as f:
        template = Template(f.read())
    
    # Generate verification link
    verification_link = f"{settings.FRONTEND_URL}/verify-email/{token}"
    
    # Generate HTML content
    html_content = template.render(
        username=username,
        verification_link=verification_link
    )
    
    # Create message
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email_to],
        body=html_content,
        subtype="html"
    )
    
    # Send email
    fm = FastMail(conf)
    fm.send_message(message)
    
    return None


def send_password_reset_email(email_to: str, token: str, username: str) -> None:
    """
    Send password reset email.
    """
    # Load email template
    with open(templates_dir / "password_reset.html") as f:
        template = Template(f.read())
    
    # Generate password reset link
    reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
    
    # Generate HTML content
    html_content = template.render(
        username=username,
        reset_link=reset_link
    )
    
    # Create message
    message = MessageSchema(
        subject="Reset your password",
        recipients=[email_to],
        body=html_content,
        subtype="html"
    )
    
    # Send email
    fm = FastMail(conf)
    fm.send_message(message)
    
    return None