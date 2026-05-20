from app.models.report_models import DecisionReport


def auth_headers(client, email="report-owner@example.com"):
    password = "StrongPass123!"
    register = client.post(
        "/api/v2/auth/register",
        json={"email": email, "password": password, "project_name": "Report Project"},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/v2/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def first_project_id(client, headers):
    response = client.get("/api/v2/projects", headers=headers)
    assert response.status_code == 200
    return response.json()[0]["id"]


def create_decision(client, headers, project_id):
    response = client.post(
        f"/api/v2/simulate?project_id={project_id}",
        headers=headers,
        json={"amount": 10, "locked_collateral": 10000, "minted_supply": 9000},
    )
    assert response.status_code == 200
    return response.json()


def test_decision_report_generates_pdf_and_metadata(client, db_session):
    headers = auth_headers(client)
    project_id = first_project_id(client, headers)
    decision = create_decision(client, headers, project_id)

    response = client.post(f"/api/v2/decisions/{decision['id']}/report", headers=headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert response.headers["x-signature-algorithm"] == "HMAC-SHA256"
    signature = response.headers["x-report-signature"]

    report = db_session.query(DecisionReport).filter_by(decision_id=decision["id"]).one()
    assert report.signature == signature
    assert report.report_sha256 == response.headers["x-report-sha256"]


def test_decision_report_signature_verification(client):
    headers = auth_headers(client, "verify-owner@example.com")
    project_id = first_project_id(client, headers)
    decision = create_decision(client, headers, project_id)
    report = client.post(f"/api/v2/decisions/{decision['id']}/report", headers=headers)
    assert report.status_code == 200

    valid = client.post(
        f"/api/v2/decisions/{decision['id']}/report/verify",
        headers=headers,
        json={"signature": report.headers["x-report-signature"]},
    )

    assert valid.status_code == 200
    assert valid.json()["valid"] is True

    invalid = client.post(
        f"/api/v2/decisions/{decision['id']}/report/verify",
        headers=headers,
        json={"signature": "00" + report.headers["x-report-signature"][2:]},
    )

    assert invalid.status_code == 200
    assert invalid.json()["valid"] is False


def test_decision_report_requires_owner(client):
    owner_headers = auth_headers(client, "report-owner-a@example.com")
    other_headers = auth_headers(client, "report-owner-b@example.com")
    project_id = first_project_id(client, owner_headers)
    decision = create_decision(client, owner_headers, project_id)

    response = client.post(f"/api/v2/decisions/{decision['id']}/report", headers=other_headers)

    assert response.status_code == 404
