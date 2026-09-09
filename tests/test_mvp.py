import uuid

from app.models.feature import Feature


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


def test_mvp_without_features_reports_not_possible(client):
    token = _register(client, "mvp1@test.com", "Mvp Org1")
    project = client.post(
        "/api/v1/projects/",
        json={"title": "MVP test", "description": "desc"},
        headers=_auth(token),
    ).json()
    res = client.get(
        f"/api/v1/projects/{project['id']}/mvp", headers=_auth(token)
    )
    assert res.status_code == 200
    body = res.json()
    assert body["recommendation_possible"] is False
    assert body["mvp_features"] == []


def test_mvp_prioritizes_high_features(client, db_session):
    token = _register(client, "mvp2@test.com", "Mvp Org2")
    project = client.post(
        "/api/v1/projects/",
        json={"title": "MVP test", "description": "desc"},
        headers=_auth(token),
    ).json()
    pid = uuid.UUID(project["id"])

    db_session.add_all(
        [
            Feature(
                project_id=pid,
                canonical_name="PAYMENT_PROCESSING",
                description="Pay",
                priority="high",
                complexity="high",
            ),
            Feature(
                project_id=pid,
                canonical_name="MESSAGING",
                description="Chat",
                priority="medium",
                complexity="medium",
            ),
            Feature(
                project_id=pid,
                canonical_name="EXPORT_EXCEL",
                description="Export",
                priority="low",
                complexity="low",
            ),
        ]
    )
    db_session.commit()

    body = client.get(
        f"/api/v1/projects/{project['id']}/mvp", headers=_auth(token)
    ).json()
    assert body["recommendation_possible"] is True
    mvp_names = {f["canonical_name"] for f in body["mvp_features"]}
    assert mvp_names == {"PAYMENT_PROCESSING"}
    phase2_names = {f["canonical_name"] for f in body["phase_2_features"]}
    assert phase2_names == {"MESSAGING"}
    later_names = {f["canonical_name"] for f in body["later_features"]}
    assert later_names == {"EXPORT_EXCEL"}
    assert "reasoning" in body
