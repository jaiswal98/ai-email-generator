from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_login_and_generate_email_without_api_key():
    email = f"test-{uuid4().hex[:8]}@example.com"
    password = "StrongPass123"

    register_response = client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": email, "password": password},
    )
    assert register_response.status_code == 201
    token = register_response.json()["access_token"]

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    generate_response = client.post(
        "/api/emails/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "purpose": "Follow up after interview",
            "recipient_type": "HR Manager",
            "tone": "Professional",
            "key_points": "Thank them for their time and ask about next steps.",
            "language": "English",
            "length": "Medium",
            "include_subject": True,
            "include_call_to_action": True,
        },
    )
    assert generate_response.status_code == 201
    assert "subject" in generate_response.json()
