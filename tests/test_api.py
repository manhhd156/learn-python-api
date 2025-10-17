import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, engine
import models

client = TestClient(app)

# Setup DB test
@pytest.fixture(scope="module")
def db_session():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

def test_register_and_login():
    # Register
    response = client.post("/register", json={"username": "testuser", "email": "test@example.com", "password": "testpass"})
    assert response.status_code == 200

    # Login
    response = client.post("/login", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Protected route
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/todos", json={"task": "Test todo"}, headers=headers)
    assert response.status_code == 200

def test_unauthorized():
    response = client.post("/todos", json={"task": "No auth"})
    assert response.status_code == 401