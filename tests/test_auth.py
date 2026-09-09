def test_root_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_register_returns_token(client):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@test.com",
            "password": "supersecret123",
            "full_name": "Alice",
            "organization_name": "Alice Corp",
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_register_duplicate_email_fails(client):
    payload = {
        "email": "bob@test.com",
        "password": "supersecret123",
        "organization_name": "Bob Corp",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 400


def test_login_success_and_uses_org(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "carol@test.com",
            "password": "supersecret123",
            "organization_name": "Carol Org",
        },
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "carol@test.com", "password": "supersecret123"},
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password_fails(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "dan@test.com", "password": "supersecret123"},
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "dan@test.com", "password": "wrongpassword"},
    )
    assert res.status_code == 401


def test_protected_endpoint_requires_auth(client):
    res = client.get("/api/v1/projects/")
    assert res.status_code == 403 or res.status_code == 401
