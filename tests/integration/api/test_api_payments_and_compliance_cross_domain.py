import pytest
from datetime import datetime, timezone, timedelta

from test_config import TestConfig
from test_helpers import ApiClient
from assertions import (
    assert_status_code,
)

from factories.bookings import create_booking
from factories.machines import create_machine
from factories.listings import listing_payload
from factories.bookings import create_booking_for_listing
from factories.users import auth_headers_by_role


def create_booking_with_machine_and_listing(client, db_session, buyer_role="buyer", provider_role="provider"):
    """
    Creates:
    1) Verified provider
    2) Machine belonging to provider
    3) Listing on that machine
    4) Booking for that listing
    """
    # machine (includes provider verification)
    machine = create_machine(client, db_session, provider_role=provider_role)

    # listing
    listing_body = listing_payload(machine["id"])
    listing_resp = client.post(
        f"{TestConfig.BASE_URL}/listings",
        json=listing_body,
        headers=auth_headers_by_role(provider_role),
    )
    assert_status_code(listing_resp, 201)
    listing = listing_resp.json()

    # booking
    booking = create_booking_for_listing(
        client,
        db_session,
        listing["id"],
        buyer_role=buyer_role,
    )

    return booking, listing, machine

PAYMENTS_BASE_URL = f"{TestConfig.BASE_URL}/payments"
COMPLIANCE_BASE_URL = f"{TestConfig.BASE_URL}/compliance"

# ---------------------------------------------------------------------------
# PAYMENTS ↔ BOOKINGS CROSS-DOMAIN TESTS
# ---------------------------------------------------------------------------
def _list_payments_for_booking(client, booking_id, role="buyer"):
    """
    Helper to call the payments API for a given booking.
    """
    headers = auth_headers_by_role(role)
    resp = client.get(
        f"{PAYMENTS_BASE_URL}/bookings/{booking_id}",
        headers=headers,
    )
    assert_status_code(resp, 200)
    return resp.json()

def test_escrow_created_on_booking_request(client, db_session):
    booking = create_booking(client, db_session)
    payments = _list_payments_for_booking(client, booking["id"], role="buyer")

    assert len(payments) == 1

    p = payments[0]
    assert p["type"] == "escrow"
    assert p["status"] == "authorized"
    assert str(p["booking_id"]) == booking["id"]

def test_escrow_voided_on_cancellation_without_refund_row(client, db_session):
    now = datetime.now(timezone.utc)
    start = now + timedelta(hours=2)
    end = start + timedelta(hours=1)

    booking = create_booking(
        client,
        db_session,
        start_time=start.isoformat(),
        end_time=end.isoformat(),
    )

    api = ApiClient(client)

    cancel_resp = api.put_booking_action(booking["id"], "cancel", role="buyer")
    assert_status_code(cancel_resp, 200)

    payments = _list_payments_for_booking(client, booking["id"], role="buyer")

    assert len(payments) == 1

    escrow = payments[0]
    assert escrow["type"] == "escrow"
    assert escrow["status"] == "cancelled"

def test_capture_on_booking_completion_updates_escrow_status(client, db_session):
    booking = create_booking(client, db_session)
    api = ApiClient(client)

    assert_status_code(api.put_booking_action(booking["id"], "confirm", role="admin"), 200)
    assert_status_code(api.put_booking_action(booking["id"], "start", role="admin"), 200)
    assert_status_code(api.put_booking_action(booking["id"], "end", role="admin"), 200)

    payments = _list_payments_for_booking(client, booking["id"], role="buyer")
    assert len(payments) == 1

    escrow = payments[0]
    assert escrow["type"] == "escrow"
    assert escrow["status"] == "captured"

# ---------------------------------------------------------------------------
# COMPLIANCE ↔ BOOKINGS / PROVIDERS / MACHINES CROSS-DOMAIN TESTS
# ---------------------------------------------------------------------------
def _create_wipe_attestation_payload(booking_id, machine_id):
    return {
        "booking_id": booking_id,
        "machine_id": machine_id,
        "method": "secure-erase",
        "evidence_uri": f"mock://wipe/{booking_id}.log",
        "notes": "Test wipe attestation",
    }

def test_provider_can_submit_wipe_attestation_for_own_machine(client, db_session):
    booking, listing, machine = create_booking_with_machine_and_listing(client, db_session)

    machine_id = machine["id"]
    provider_headers = auth_headers_by_role("provider")
    payload = _create_wipe_attestation_payload(booking["id"], machine_id)

    # submit attestation
    resp = client.post(
        f"{COMPLIANCE_BASE_URL}/attestations",
        json=payload,
        headers=provider_headers,
    )
    assert_status_code(resp, 200)
    att = resp.json()

    assert att["booking_id"] == booking["id"]
    assert att["machine_id"] == machine_id
    assert att["method"] == payload["method"]

    # verify listing
    resp_list = client.get(
        f"{COMPLIANCE_BASE_URL}/machines/{machine_id}/attestations",
        headers=provider_headers,
    )
    assert_status_code(resp_list, 200)
    assert any(a["id"] == att["id"] for a in resp_list.json())

def create_start_end_times():
    now = datetime.now(timezone.utc)
    start = now + timedelta(hours=1)
    end = start + timedelta(hours=1)
    return start, end

def test_booking_completion_auto_generates_wipe_attestation(client, db_session):
    """Now uses helper to ensure machine + listing + provider verification"""
    booking, listing, machine = create_booking_with_machine_and_listing(client, db_session)

    machine_id = machine["id"]
    api = ApiClient(client)

    # lifecycle
    api.put_booking_action(booking["id"], "confirm", role="admin")
    api.put_booking_action(booking["id"], "start", role="admin")

    # complete → triggers auto-wipe
    end_resp = api.put_booking_action(booking["id"], "end", role="admin")
    assert_status_code(end_resp, 200)

    # check wipe
    provider_headers = auth_headers_by_role("provider")
    atts_resp = client.get(
        f"{COMPLIANCE_BASE_URL}/machines/{machine_id}/attestations",
        headers=provider_headers,
    )
    assert_status_code(atts_resp, 200)

    items = atts_resp.json()
    assert len(items) >= 1
    assert items[0]["booking_id"] == booking["id"]

def test_booking_can_complete_after_wipe_attestation_exists(client, db_session):
    """Uses helper to guarantee valid machine/listing + verified provider"""
    booking, listing, machine = create_booking_with_machine_and_listing(client, db_session)

    machine_id = machine["id"]
    api = ApiClient(client)

    api.put_booking_action(booking["id"], "confirm", role="admin")
    api.put_booking_action(booking["id"], "start", role="admin")

    provider_headers = auth_headers_by_role("provider")

    payload = {
        "booking_id": booking["id"],
        "machine_id": machine_id,
        "method": "secure-erase",
        "evidence_uri": "mock://manual/att.log",
        "notes": "Provider submitted manually",
    }
    att_resp = client.post(
        f"{COMPLIANCE_BASE_URL}/attestations",
        json=payload,
        headers=provider_headers,
    )
    assert_status_code(att_resp, 200)

    end_resp = api.put_booking_action(booking["id"], "end", role="admin")
    assert_status_code(end_resp, 200)

    final = end_resp.json()
    assert final["status"].lower() in ("completed", "complete")