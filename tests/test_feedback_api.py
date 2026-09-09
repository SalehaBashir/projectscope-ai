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
    return res.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


class TestFeedbackAPI:
    def test_submit_and_list_project_feedback(self, client):
        token = _register(client, "fb@test.com", "Fb Org")
        project = client.post(
            "/api/v1/projects/",
            json={"title": "FB", "description": "desc"},
            headers=_auth(token),
        ).json()

        res = client.post(
            f"/api/v1/projects/{project['id']}/feedback",
            json={"actual_hours": 120, "estimated_hours": 100, "notes": "Done"},
            headers=_auth(token),
        )
        assert res.status_code == 200
        fb = res.json()
        assert fb["actual_hours"] == 120
        assert fb["project_id"] == project["id"]

        listed = client.get(
            f"/api/v1/projects/{project['id']}/feedback", headers=_auth(token)
        ).json()
        assert len(listed) == 1

        summary = client.get(
            f"/api/v1/projects/{project['id']}/feedback/summary",
            headers=_auth(token),
        ).json()
        assert summary["total_feedback_count"] == 1
        assert summary["total_actual_hours"] == 120

    def test_feedback_cannot_be_added_by_other_org(self, client):
        token_a = _register(client, "fbA@test.com", "Fb Org A")
        token_b = _register(client, "fbB@test.com", "Fb Org B")
        project = client.post(
            "/api/v1/projects/",
            json={"title": "FB", "description": "desc"},
            headers=_auth(token_a),
        ).json()

        res = client.post(
            f"/api/v1/projects/{project['id']}/feedback",
            json={"actual_hours": 10},
            headers=_auth(token_b),
        )
        assert res.status_code == 403

    def test_feedback_rejects_negative_hours(self, client):
        token = _register(client, "fbC@test.com", "Fb Org C")
        project = client.post(
            "/api/v1/projects/",
            json={"title": "FB", "description": "desc"},
            headers=_auth(token),
        ).json()
        res = client.post(
            f"/api/v1/projects/{project['id']}/feedback",
            json={"actual_hours": -5},
            headers=_auth(token),
        )
        assert res.status_code == 422
