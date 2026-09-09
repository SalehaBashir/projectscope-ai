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


def _make_project(client, token, title="Report Project"):
    return client.post(
        "/api/v1/projects/",
        json={"title": title, "description": "A full plan report project."},
        headers=_auth(token),
    ).json()


class TestReportGeneration:
    def test_pdf_report_download(self, client):
        token = _register(client, "report@test.com", "Report Org")
        project = _make_project(client, token)
        res = client.get(
            f"/api/v1/projects/{project['id']}/report?format=pdf",
            headers=_auth(token),
        )
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("application/pdf")
        assert "attachment" in res.headers.get("content-disposition", "")
        assert res.content[:4] == b"%PDF"

    def test_docx_report_download(self, client):
        token = _register(client, "report2@test.com", "Report Org2")
        project = _make_project(client, token)
        res = client.get(
            f"/api/v1/projects/{project['id']}/report?format=docx",
            headers=_auth(token),
        )
        assert res.status_code == 200
        assert "officedocument.wordprocessingml" in res.headers["content-type"]
        # DOCX files are ZIP archives -> PK magic bytes
        assert res.content[:2] == b"PK"

    def test_report_defaults_to_pdf(self, client):
        token = _register(client, "report3@test.com", "Report Org3")
        project = _make_project(client, token)
        res = client.get(
            f"/api/v1/projects/{project['id']}/report", headers=_auth(token)
        )
        assert res.status_code == 200
        assert res.content[:4] == b"%PDF"

    def test_report_for_missing_project_404(self, client):
        token = _register(client, "report6@test.com", "Report Org6")
        res = client.get(
            "/api/v1/projects/00000000-0000-0000-0000-000000000000/report",
            headers=_auth(token),
        )
        assert res.status_code == 404
