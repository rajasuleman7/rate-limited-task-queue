
def test_register_success(client):
    r = client.post("/auth/register",
                    json={"username":"raja","password":"pass123","role":"user"})
    assert r.status_code == 201
    assert "access_token" in r.json()

def test_register_duplicate(client):
    client.post("/auth/register", json={"username":"u","password":"pass123"})
    r = client.post("/auth/register", json={"username":"u","password":"pass123"})
    assert r.status_code == 409

def test_login_success(client):
    client.post("/auth/register", json={"username":"u2","password":"pass123"})
    r = client.post("/auth/login", json={"username":"u2","password":"pass123"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_login_wrong_password(client):
    client.post("/auth/register", json={"username":"u3","password":"pass123"})
    r = client.post("/auth/login", json={"username":"u3","password":"wrong"})
    assert r.status_code == 401

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
