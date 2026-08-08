
import pytest
from fastapi.testclient import TestClient
import app.auth as auth_module
import app.routes.tasks as tasks_module

@pytest.fixture(autouse=True)
def reset_state():
    """Clear in-memory state between tests."""
    auth_module._users.clear()
    tasks_module._jobs.clear()
    yield

@pytest.fixture
def client():
    from app import create_app
    return TestClient(create_app())

@pytest.fixture
def auth_headers(client):
    client.post("/auth/register",
                json={"username":"testuser","password":"pass123","role":"user"})
    r = client.post("/auth/login",
                    json={"username":"testuser","password":"pass123"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client):
    client.post("/auth/register",
                json={"username":"adminuser","password":"pass123","role":"admin"})
    r = client.post("/auth/login",
                    json={"username":"adminuser","password":"pass123"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
