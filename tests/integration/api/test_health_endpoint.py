from assertions import assert_status_code


def test_health_endpoint(client):
    """
    This test ensures that the API health endpoint
    responds with an okay status.
    """
    resp = client.get("/api/v1/health/")
    assert_status_code(resp, 200)
    body = resp.json()
    assert body.get("status") == "ok"