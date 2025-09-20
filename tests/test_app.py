import json
from app import app

def test_get_token_missing_keys():
    client = app.test_client()
    response = client.post("/get-token", json={})
    data = response.get_json()

    assert response.status_code == 400 or "error" in data

def test_get_token_with_dummy_keys():
    client = app.test_client()
    response = client.post("/get-token", json={
        "aws_access_key": "fake",
        "aws_secret_key": "fake",
        "region": "us-east-1"
    })
    data = response.get_json()

    # Should fail gracefully with error message
    assert "error" in data

