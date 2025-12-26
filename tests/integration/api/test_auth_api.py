import jwt
from factories.users import auth_headers_by_role
from factories.listings import valid_listing_payload
from test_config import TestConfig
from assertions import assert_status_code, assert_unauthorized, assert_forbidden


def test_auth_blocks_missing_token_on_protected_endpoint(client, db_session):
    payload = valid_listing_payload(client, db_session)
    resp = client.post("/api/v1/listings/", json=payload)
    assert_unauthorized(resp)

def test_auth_allows_provider_mock_token(client, db_session):
    """
    201 = valid payload
    400 = if provider lacks required fields as the schema grows
    """
    payload = valid_listing_payload(client, db_session)
    resp = client.post(
        "/api/v1/listings/",
        json=payload,
        headers=auth_headers_by_role("provider"),
    )
    assert resp.status_code in (201, 400)

def test_auth_forbids_buyer_on_provider_only_endpoint(client, db_session):
    payload = valid_listing_payload(client, db_session)

    resp = client.post(
        "/api/v1/listings/",
        json=payload,
        headers=auth_headers_by_role("buyer"),
    )
    assert_forbidden(resp)

def test_auth_cookie_token(client, monkeypatch):
    monkeypatch.setattr("app.auth.service.settings.SUPABASE_JWT_SECRET", "TESTSECRET")

    token = jwt.encode(
        {
            "sub": "999",
            "email": "cookie@example.com",
            "user_metadata": {"role": "buyer"},
        },
        "TESTSECRET",
        algorithm="HS256"
    )

    client.cookies.set("access_token", token)
    resp = client.get("/api/v1/bookings/")
    assert_status_code(resp, 200)  #or 404 if no bookings

def test_auth_invalid_jwt_shape(client):
    resp = client.get("/api/v1/bookings/", headers={"Authorization": "Bearer abc.def"})
    assert_unauthorized(resp)