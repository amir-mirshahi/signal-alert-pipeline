import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # <-- New import

from app.main import app, get_db
from app.database import Base

# Use an in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# StaticPool forces SQLite to keep the SAME connection, 
# so the tables don't disappear!
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, # <-- New parameter
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def client():
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)
    
    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    
    # Drop the tables after the test is done
    Base.metadata.drop_all(bind=engine)