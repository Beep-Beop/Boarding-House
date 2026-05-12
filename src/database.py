from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from src.config import settings

Base = declarative_base()

def get_engine():
    db_url = settings.DATABASE_URL
    connect_args = {}
    
    if db_url and "ssl_ca" in db_url:
        connect_args = {"ssl": {"ca": os.getenv("SSL_CA_PATH", "./ca.pem")}}

    engine = create_engine(
        db_url, 
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=3600
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