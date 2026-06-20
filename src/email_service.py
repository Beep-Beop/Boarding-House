import requests

from src.config import settings
from src.logger import logger

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _send_email(to_email: str, subject: str, text: str, html: str) -> bool:
    if settings.BREVO_API_KEY:
        return _send_via_brevo_api(to_email, subject, text, html)
    return _send_via_smtp(to_email, subject, text, html)


def _send_via_brevo_api(to_email: str, subject: str, text: str, html: str) -> bool:
    try:
        payload = {
            "sender": {"email": settings.SMTP_FROM_EMAIL, "name": "Boarding House Finder"},
            "to": [{"email": to_email}],
            "subject": subject,
            "textContent": text,
            "htmlContent": html,
        }
        resp = requests.post(
            BREVO_API_URL,
            json=payload,
            headers={"api-key": settings.BREVO_API_KEY},
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
    subject = "Password Reset Code - Boarding House Finder"
    text = f"Your password reset code is: {code}\n\nThis code expires in 15 minutes."

    html = f"""\
<html>
<body style="font-family: Arial, sans-serif; background-color: #f6f1e8; padding: 20px;">
  <table align="center" width="100%" cellpadding="0" cellspacing="0"
         style="max-width: 480px; background-color: #ffffff; border-radius: 8px; overflow: hidden;">
    <tr>
      <td style="padding: 30px 30px 10px 30px; text-align: center;">
        <h1 style="color: #AC7F5E; font-size: 22px; margin: 0;">Boarding House Finder</h1>
      </td>
    </tr>
    <tr>
      <td style="padding: 10px 30px 20px 30px; text-align: center;">
        <p style="color: #3E362A; font-size: 16px; margin: 0 0 20px 0;">Your password reset code</p>
        <div style="background-color: #f6f1e8; border-radius: 8px; padding: 20px; display: inline-block;">
          <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #3E362A;">{code}</span>
        </div>
        <p style="color: #666; font-size: 13px; margin: 20px 0 0 0;">
          This code expires in <strong>15 minutes</strong>.<br>
          If you did not request this, please ignore this email.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    return _send_email(to_email, subject, text, html)


def send_verification_email(to_email: str, token: str) -> bool:
    verify_url = f"{settings.BASE_URL}/auth/verify-email/{token}"
    subject = "Verify Your Email - Boarding House Finder"
    text = f"Click this link to verify your email: {verify_url}\n\nThis link expires in 24 hours."

    html = f"""\
<html>
<body style="font-family: Arial, sans-serif; background-color: #f6f1e8; padding: 20px;">
  <table align="center" width="100%" cellpadding="0" cellspacing="0"
         style="max-width: 480px; background-color: #ffffff; border-radius: 8px; overflow: hidden;">
    <tr>
      <td style="padding: 30px 30px 10px 30px; text-align: center;">
        <h1 style="color: #AC7F5E; font-size: 22px; margin: 0;">Boarding House Finder</h1>
      </td>
    </tr>
    <tr>
      <td style="padding: 10px 30px 20px 30px; text-align: center;">
        <p style="color: #3E362A; font-size: 16px; margin: 0 0 20px 0;">Verify your email address</p>
        <p style="color: #666; font-size: 14px; margin: 0 0 25px 0;">
          Click the button below to verify your account.
        </p>
        <a href="{verify_url}" style="display: inline-block; background-color: #AC7F5E; color: #ffffff;
           text-decoration: none; padding: 14px 40px; border-radius: 6px; font-size: 16px; font-weight: bold;">
          VERIFY EMAIL
        </a>
        <p style="color: #666; font-size: 13px; margin: 25px 0 0 0;">
          This link expires in <strong>24 hours</strong>.<br>
          If you did not create an account, please ignore this email.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    return _send_email(to_email, subject, text, html)
