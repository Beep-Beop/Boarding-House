import requests

from src.config import settings
from src.logger import logger

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _send_email(to_email: str, subject: str, text: str, html: str) -> bool:
    if settings.BREVO_API_KEY:
        return _send_via_brevo_api(to_email, subject, text, html)
    return _send_via_smtp(to_email, subject, text, html)


def _send_via_brevo_api(to_email: str, subject: str, text: str, html: str) -> bool:
    logger.info("BREVO_API_KEY loaded: %s", "yes" if settings.BREVO_API_KEY else "no")
    try:
        payload = {
            "sender": {"email": settings.SMTP_FROM_EMAIL, "name": "Boarding House Finder"},
            "to": [{"email": to_email}],
            "subject": subject,
            "textContent": text,
            "htmlContent": html,
        }
        api_key = settings.BREVO_API_KEY.strip()
        resp = requests.post(
            BREVO_API_URL,
            json=payload,
            headers={"api-key": api_key},
            timeout=15,
        )
        if resp.ok:
            logger.info("Email sent to %s via Brevo API", to_email)
            return True
        logger.error("Brevo API error [%s]: %s", resp.status_code, resp.text)
        return False
    except Exception as e:
        logger.error("Failed to send email to %s via API: %s", to_email, e)
        return False


def _send_via_smtp(to_email: str, subject: str, text: str, html: str) -> bool:
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email

        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        ctx = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls(context=ctx)
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())

        logger.info("Email sent to %s via SMTP", to_email)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s via SMTP: %s", to_email, e)
        return False


def send_reset_code(to_email: str, code: str) -> bool:
    print(f"\n{'='*60}")
    print(f"  [DEV] Password Reset Code for {to_email}")
    print(f"  Code: {code}")
    print(f"  Expires in: 15 minutes")
    print(f"{'='*60}\n")
    return True


def send_verification_email(to_email: str, token: str) -> bool:
    verify_url = f"{settings.BASE_URL}/auth/verify-email/{token}"
    print(f"\n{'='*60}")
    print(f"  [DEV] Email Verification for {to_email}")
    print(f"  URL: {verify_url}")
    print(f"  Expires in: 24 hours")
    print(f"{'='*60}\n")
    return True
