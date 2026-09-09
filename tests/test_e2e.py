import json


def _register(client, email, org):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "full_name": email.split("@")[0],
            "organization_name": org,
        },
    )

    assert response.status_code == 201

    return response.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_full_projectscope_e2e_flow(client, monkeypatch):
    """
    End-to-end flow:

    Register
        -> Create Project
        -> AI Analysis
        -> Generate Report
    """

    # ---------------------------------------------------------
    # 1. REGISTER
    # ---------------------------------------------------------
    token = _register(
        client,
        "e2e@test.com",
        "E2E Organization",
    )

    headers = _auth(token)

    # ---------------------------------------------------------
    # 2. CREATE PROJECT
    # ---------------------------------------------------------
    project_response = client.post(
        "/api/v1/projects/",
        json={
            "title": "E2E E-Commerce Project",
            "description": (
                "An e-commerce platform where customers can "
                "browse products, add products to cart, and "
                "complete checkout."
            ),
            "budget": "10000",
            "platform": "web",
        },
        headers=headers,
    )

    assert project_response.status_code == 200

    project = project_response.json()

    assert "id" in project
    assert project["title"] == "E2E E-Commerce Project"

    project_id = project["id"]

    # ---------------------------------------------------------
    # 3. MOCK AI RESPONSE
    # ---------------------------------------------------------
    import app.services.ai_analysis_service as analysis_mod

    def fake_call_llm_with_metadata(system_prompt, user_prompt):
        return (
            json.dumps(
                {
                    "project_type": "ecommerce",
                    "users": [
                        "customer",
                        "admin",
                    ],
                    "requirements": [
                        {
                            "category": "functional",
                            "text": "Customers can browse products.",
                            "confidence": 0.95,
                        },
                        {
                            "category": "functional",
                            "text": "Customers can add products to cart.",
                            "confidence": 0.95,
                        },
                        {
                            "category": "functional",
                            "text": "Customers can complete checkout.",
                            "confidence": 0.90,
                        },
                    ],
                    "features": [
                        {
                            "canonical_name": "PRODUCT_CATALOG",
                            "description": "Browse products.",
                            "priority": "high",
                            "complexity": "medium",
                            "confidence": 0.95,
                        },
                        {
                            "canonical_name": "SHOPPING_CART",
                            "description": "Add and manage cart items.",
                            "priority": "high",
                            "complexity": "medium",
                            "confidence": 0.95,
                        },
                        {
                            "canonical_name": "CHECKOUT",
                            "description": "Complete checkout.",
                            "priority": "high",
                            "complexity": "high",
                            "confidence": 0.90,
                        },
                    ],
                    "assumptions": [
                        "The project is initially web-based.",
                    ],
                    "missing_information": [],
                }
            ),
            {
                "provider": "groq",
                "model": "openai/gpt-oss-120b",
                "version": "groq-client-v1.1",
                "prompt_tokens": 100,
                "completion_tokens": 100,
                "total_tokens": 200,
                "latency_ms": 10,
                "status": "success",
                "fallback_used": False,
            },
        )

    monkeypatch.setattr(
        analysis_mod,
        "call_llm_with_metadata",
        fake_call_llm_with_metadata,
    )

    # ---------------------------------------------------------
    # 4. AI ANALYSIS
    # ---------------------------------------------------------
    analysis_response = client.post(
        f"/api/v1/projects/{project_id}/analyze",
        json={
            "description": (
                "An e-commerce platform where customers can "
                "browse products, add products to cart, and "
                "complete checkout."
            ),
            "budget": "10000",
            "platform": "web",
        },
        headers=headers,
    )

    assert analysis_response.status_code == 200

    analysis = analysis_response.json()

    assert analysis["project_type"] == "ecommerce"
    assert len(analysis["requirements"]) > 0
    assert len(analysis["features"]) > 0
    assert "assumptions" in analysis
    assert "missing_information" in analysis

    # ---------------------------------------------------------
    # 5. GENERATE PDF REPORT
    # ---------------------------------------------------------
    report_response = client.get(
        f"/api/v1/projects/{project_id}/report?format=pdf",
        headers=headers,
    )

    assert report_response.status_code == 200
    assert report_response.headers["content-type"].startswith(
        "application/pdf"
    )
    assert report_response.content[:4] == b"%PDF"