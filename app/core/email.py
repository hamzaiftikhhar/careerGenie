import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import emails
from emails.template import JinjaTemplate
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings

def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    """Send an email using the SMTP settings from the config."""
    assert settings.EMAILS_FROM_EMAIL
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")


def send_verification_email(email_to: str, token: str) -> None:
    """Send the verification email to a user."""
    project_name = "Career Counseling & Scholarship Platform"
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    templates_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("email_verification.html")
    
    html_content = template.render(
        project_name=project_name,
        verification_url=verification_url,
        username=email_to.split("@")[0],
    )
    
    subject = f"{project_name} - Email Verification"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=html_content,
    )


def send_reset_password_email(email_to: str, token: str) -> None:
    """Send the password reset email to a user."""
    project_name = "Career Counseling & Scholarship Platform"
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    templates_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("password_reset.html")
    
    html_content = template.render(
        project_name=project_name,
        reset_url=reset_url,
        username=email_to.split("@")[0],
    )
    
    subject = f"{project_name} - Password Reset"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=html_content,
    )