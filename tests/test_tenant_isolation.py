def _register(client, email, org):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "full_name": email.split("@")[0],
            "organization_name": org,
        },
    )
    if res.status_code != 201:
        raise AssertionError(f"register failed: {res.status_code} {res.text}")
    return res.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create_project(client, token, title="Project X"):
    res = client.post(
        "/api/v1/projects/",
        json={"title": title, "description": "A description"},
        headers=_auth(token),
    )
    assert res.status_code == 200, res.text
    return res.json()


class TestTenantIsolation:
    def test_cross_org_project_access_denied(self, client):
        token_a = _register(client, "ownerA@test.com", "Org A")
        token_b = _register(client, "ownerB@test.com", "Org B")

        project = _create_project(client, token_a)

        # User B must NOT be able to read, update, delete, or recalc A's project
        assert (
            client.get(
                f"/api/v1/projects/{project['id']}", headers=_auth(token_b)
            ).status_code
            == 403
        )
        assert (
            client.patch(
                f"/api/v1/projects/{project['id']}",
                json={"title": "Hacked"},
                headers=_auth(token_b),
            ).status_code
            == 403
        )
        assert (
            client.delete(
                f"/api/v1/projects/{project['id']}", headers=_auth(token_b)
            ).status_code
            == 403
        )
        assert (
            client.post(
                f"/api/v1/projects/{project['id']}/recalculate",
                json={},
                headers=_auth(token_b),
            ).status_code
            == 403
        )
        assert (
            client.get(
                f"/api/v1/projects/{project['id']}/mvp", headers=_auth(token_b)
            ).status_code
            == 403
        )
        assert (
            client.get(
                f"/api/v1/projects/{project['id']}/report",
                headers=_auth(token_b),
            ).status_code
            == 403
        )

    def test_owner_can_access_own_project(self, client):
        token = _register(client, "owner2@test.com", "Org C")
        project = _create_project(client, token)

        res = client.get(
            f"/api/v1/projects/{project['id']}", headers=_auth(token)
        )
        assert res.status_code == 200
        assert res.json()["id"] == project["id"]

    def test_list_only_own_org_projects(self, client):
        token_a = _register(client, "listA@test.com", "Org ListA")
        token_b = _register(client, "listB@test.com", "Org ListB")

        _create_project(client, token_a, title="A's secret project")
        _create_project(client, token_b, title="B's project")

        mine = client.get("/api/v1/projects/", headers=_auth(token_a)).json()
        titles = [p["title"] for p in mine]
        assert "A's secret project" in titles
        assert "B's project" not in titles
