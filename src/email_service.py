import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.config import settings
from src.logger import logger


def _send_email(to_email: str, subject: str, text: str, html: str) -> bool:
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

        logger.info("Email sent to %s", to_email)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to_email, e)
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


def send_verification_email(to_email: str, token: str, code: str = None) -> bool:
    verify_url = f"{settings.BASE_URL}/auth/verify-email/{token}"
    subject = "Verify Your Email - Boarding House Finder"
    text = f"Click this link to verify your email: {verify_url}\n\nThis link expires in 24 hours."
    if code:
        text += f"\n\nOr use this verification code: {code}"

    code_html = ""
    if code:
        code_html = f"""
        <p style="color: #3E362A; font-size: 16px; margin: 20px 0 10px 0;">Or enter this code in the app:</p>
        <div style="background-color: #f6f1e8; border-radius: 8px; padding: 20px; display: inline-block;">
          <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #3E362A;">{code}</span>
        </div>"""

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
        {code_html}
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
