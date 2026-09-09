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


def _stub_llm_analysis(monkeypatch):
    """Deterministic, offline stub for the requirement analyzer + task generator."""
    import json

    def fake_analyzer(system_prompt, user_prompt):
        response_json = json.dumps(
            {
                "project_type": "ecommerce",
                "users": ["customer", "admin"],
                "requirements": [
                    {
                        "category": "functional",
                        "text": "Customers can create accounts and log in.",
                        "confidence": 0.95,
                    }
                ],
                "features": [
                    {
                        "canonical_name": "AUTHENTICATION",
                        "description": "Account creation and login",
                        "priority": "high",
                        "complexity": "medium",
                        "confidence": 0.95,
                    }
                ],
            }
        )
        fake_metadata = {
            "provider": "groq",
            "model": "openai/gpt-oss-120b",
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "latency_ms": 5,
            "status": "success",
        }
        return response_json, fake_metadata

    def fake_task_generator(system_prompt, user_prompt):
        return json.dumps({"additional_tasks": []})

    import app.services.ai_analysis_service as analysis_mod
    from app.ai.groq_client import GroqProvider

    monkeypatch.setattr(analysis_mod, "call_llm_with_metadata", fake_analyzer)

    def fake_generate(self, system_prompt, user_prompt):
        return fake_task_generator(system_prompt, user_prompt)

    monkeypatch.setattr(GroqProvider, "generate", fake_generate)


class TestProjectsCRUD:
    def test_create_project(self, client):
        token = _register(client, "proj@test.com", "Proj Org")
        res = client.post(
            "/api/v1/projects/",
            json={
                "title": "My App",
                "description": "Build an app",
                "budget": "5000",
                "platform": "web",
            },
            headers=_auth(token),
        )
        assert res.status_code == 200
        body = res.json()
        assert body["title"] == "My App"
        assert body["status"] == "draft"

    def test_get_project(self, client):
        token = _register(client, "proj2@test.com", "Proj Org2")
        created = client.post(
            "/api/v1/projects/",
            json={"title": "App", "description": "desc"},
            headers=_auth(token),
        ).json()
        res = client.get(
            f"/api/v1/projects/{created['id']}", headers=_auth(token)
        )
        assert res.status_code == 200
        assert res.json()["id"] == created["id"]

    def test_get_missing_project_404(self, client):
        token = _register(client, "proj3@test.com", "Proj Org3")
        res = client.get(
            "/api/v1/projects/00000000-0000-0000-0000-000000000000",
            headers=_auth(token),
        )
        assert res.status_code == 404

    def test_update_project(self, client):
        token = _register(client, "proj4@test.com", "Proj Org4")
        created = client.post(
            "/api/v1/projects/",
            json={"title": "Old", "description": "old desc"},
            headers=_auth(token),
        ).json()
        res = client.patch(
            f"/api/v1/projects/{created['id']}",
            json={"title": "New Title", "budget": "9999"},
            headers=_auth(token),
        )
        assert res.status_code == 200
        body = res.json()
        assert body["title"] == "New Title"
        assert body["budget"] == "9999"
        assert body["description"] == "old desc"

    def test_delete_project(self, client):
        token = _register(client, "proj5@test.com", "Proj Org5")
        created = client.post(
            "/api/v1/projects/",
            json={"title": "Temp", "description": "to delete"},
            headers=_auth(token),
        ).json()
        res = client.delete(
            f"/api/v1/projects/{created['id']}", headers=_auth(token)
        )
        assert res.status_code == 200
        gone = client.get(
            f"/api/v1/projects/{created['id']}", headers=_auth(token)
        )
        assert gone.status_code == 404

    def test_recalculate_success_with_stubbed_llm(self, client, monkeypatch):
        _stub_llm_analysis(monkeypatch)
        token = _register(client, "proj6@test.com", "Proj Org6")
        created = client.post(
            "/api/v1/projects/",
            json={"title": "Recalc", "description": "An online store."},
            headers=_auth(token),
        ).json()

        res = client.post(
            f"/api/v1/projects/{created['id']}/recalculate",
            json={"description": "A revised online clothing store with payments."},
            headers=_auth(token),
        )
        assert res.status_code == 200
        body = res.json()
        assert "estimate" in body
        assert body["estimate"]["expected_hours"] > 0
        assert body["project"]["title"] == "Recalc"