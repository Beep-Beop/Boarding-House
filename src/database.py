import base64
import os
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.config import settings

Base = declarative_base()

def _write_ssl_ca():
    raw = os.getenv("SSL_CA_CERT")
    if not raw:
        return None
    try:
        decoded = base64.b64decode(raw)
        tmp = tempfile.NamedTemporaryFile(prefix="aiven-ca-", suffix=".pem", delete=False)
        tmp.write(decoded)
        tmp.close()
        return tmp.name
    except Exception:
        return None

_SSL_CA_PATH = _write_ssl_ca()

def get_engine():
    db_url = settings.DATABASE_URL
    connect_args = {}

    if db_url and "ssl_ca" in db_url:
        ca_path = _SSL_CA_PATH or os.getenv("SSL_CA_PATH", "./ca.pem")
        connect_args = {"ssl": {"ca": ca_path}}

    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    return engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()