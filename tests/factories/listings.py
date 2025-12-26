from factories.machines import create_machine
from factories.users import auth_headers_by_role
from test_config import TestConfig

def listing_payload(machine_id, **overrides):
    base = {
        "title": TestConfig.DEFAULT_LISTING_TITLE,
        "description": "Default Description", 
        "hourly_price": TestConfig.DEFAULT_LISTING_PRICE,
        "machine_id": machine_id,
    }
    base.update(overrides)
    return base

def create_listing(client, db_session, provider_role="provider", **overrides):
    """Create machine using config-based provider"""
    machine = create_machine(client, db_session, provider_role=provider_role)
    payload = listing_payload(machine_id=machine["id"], **overrides)

    resp = client.post(
        "/api/v1/listings/",
        json=payload,
        headers=auth_headers_by_role(provider_role),
    )
    assert resp.status_code == 201
    return resp.json()

def valid_listing_payload(client, db_session, provider_role="provider", **overrides):
    """Create a machine and return listing payload (without creating listing)."""
    machine = create_machine(client, db_session, provider_role=provider_role)
    return listing_payload(machine_id=machine["id"], **overrides)

def create_listing_with_machine(client, db_session, machine_payload_overrides=None, listing_payload_overrides=None):
    """Create a listing with custom machine and listing parameters."""
    machine_overrides = machine_payload_overrides or {}
    listing_overrides = listing_payload_overrides or {}
    
    return create_listing(
        client, 
        db_session, 
        **listing_overrides
    )