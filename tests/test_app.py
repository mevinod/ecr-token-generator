import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

def test_get_token_missing_keys():
    client = app.test_client()
    response = client.post("/get-token", json={})
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Missing AWS credentials"

def test_get_token_with_dummy_keys():
    client = app.test_client()
    response = client.post("/get-token", json={
        "aws_access_key": "fake",
        "aws_secret_key": "fake",
        "region": "us-east-1"
    })
    data = response.get_json()

    assert response.status_code in [400, 500]
    assert "error" in data
