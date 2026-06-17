import os
from dotenv import load_dotenv
from src.logger import logger

load_dotenv()

class Settings:
    def __init__(self):
        self.ENV = os.getenv("ENV", "development")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
        self.R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
        self.R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
        self.R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
        self.ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        self.SMTP_HOST = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USER = os.getenv("SMTP_USER")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        self.SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@beepboops.app")

        if self.ACCESS_SECRET_KEY and len(self.ACCESS_SECRET_KEY) < 32:
            raise ValueError("ACCESS_SECRET_KEY must be at least 32 characters long")

        if self.ENV != "development" and self.BASE_URL.startswith("http://"):
            logger.warning("BASE_URL is using HTTP in %s mode: %s", self.ENV, self.BASE_URL)

settings = Settings()

REQUIRED_ENV_VARS = {
    "DATABASE_URL": settings.DATABASE_URL,
    "ACCESS_SECRET_KEY": settings.ACCESS_SECRET_KEY,
}

missing = [name for name, val in REQUIRED_ENV_VARS.items() if not val]
if missing:
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

if not all([settings.R2_ACCOUNT_ID, settings.R2_ACCESS_KEY_ID, settings.R2_SECRET_ACCESS_KEY, settings.R2_BUCKET_NAME]):
    logger.warning("R2 storage vars are missing — file uploads will fail")