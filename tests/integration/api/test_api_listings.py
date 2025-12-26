from factories.listings import create_listing
from test_config import TestConfig
from test_helpers import ApiClient
from assertions import assert_status_code, assert_is_list, assert_any_item_contains


def test_create_listing_as_provider(client, db_session):
    """
    A provider can create a listing.
    """
    listing = create_listing(client, db_session, provider_role="provider")
    
    assert listing["title"] == TestConfig.DEFAULT_LISTING_TITLE
    assert listing["hourly_price"] == TestConfig.DEFAULT_LISTING_PRICE

def test_list_listings_public(client, db_session):
    """
    The public show listings endpoint works.
    """
    api = ApiClient(client)
    create_listing(client, db_session)

    resp = client.get("/api/v1/listings/")
    assert_status_code(resp, 200)
    assert_is_list(resp)
    
    # Fix: Check the nested structure
    data = resp.json()
    assert any(item.get('listing', {}).get('title') == TestConfig.DEFAULT_LISTING_TITLE 
               for item in data), \
        f"No listing found with title = {TestConfig.DEFAULT_LISTING_TITLE}"