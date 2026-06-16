import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from moto import mock_aws
import boto3

from src.database import Base

TEST_DB_URL = os.getenv("TEST_DB_URL", "sqlite:///:memory:")

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def mock_s3_client():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        yield client