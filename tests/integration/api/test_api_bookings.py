from factories.bookings import create_booking, booking_payload
from factories.users import create_user_by_role, auth_headers_by_role
from factories.listings import create_listing
from test_helpers import ApiClient
from assertions import assert_status_code, assert_any_item_contains


def test_admin_create_booking_endpoint(client, db_session):
    """
    An admin member can manually create a booking with buyer_user_id.
    """
    api = ApiClient(client)
    
    #Create users using config-based helpers
    admin = create_user_by_role(db_session, "admin")
    buyer = create_user_by_role(db_session, "buyer")
    
    listing = create_listing(client, db_session)

    payload = booking_payload(listing_id=listing["id"], buyer_user_id=str(buyer.id))

    resp = client.post(
        "/api/v1/bookings/",
        json=payload,
        headers=auth_headers_by_role("admin"),
    )
    assert_status_code(resp, 201)

def test_request_booking_and_list_for_buyer_and_provider(client, db_session):
    """
    A buyer sees the bookings they made.
    A provider sees bookings for their machines.
    """
    api = ApiClient(client)
    booking = create_booking(client, db_session)

    #Buyer sees their booking
    response = api.get_bookings("buyer")
    assert_status_code(response, 200)
    assert_any_item_contains(response, "id", booking["id"])

    #Provider sees booking for their machine
    response = api.get_bookings("provider")
    assert_status_code(response, 200)
    assert_any_item_contains(response, "id", booking["id"])