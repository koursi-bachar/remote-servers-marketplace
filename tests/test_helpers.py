from test_config import TestConfig
from factories.users import auth_headers_for, create_user


class ApiClient:
    """
    These wrappers are used around test client to provide
    consistent endpoint construction and common operations.
    """
    def __init__(self, client):
        self.client = client
    
    # URL construction
    def booking_url(self, booking_id=None, action=None):
        """Construct booking-related URLs."""
        base = f"{TestConfig.BASE_URL}/bookings"
        if booking_id and action:
            return f"{base}/{booking_id}/{action}"
        elif booking_id:
            return f"{base}/{booking_id}"
        else:
            return base
    
    def listing_url(self, listing_id=None):
        """Construct listing-related URLs."""
        base = f"{TestConfig.BASE_URL}/listings"
        return f"{base}/{listing_id}" if listing_id else base
    
    def machine_url(self, machine_id=None):
        """Construct machine-related URLs."""
        base = f"{TestConfig.BASE_URL}/machines"
        return f"{base}/{machine_id}" if machine_id else base
    
    # Common operations
    def put_booking_action(self, booking_id, action, role="admin"):
        """Perform booking actions (confirm, cancel, start, end)."""
        email = TestConfig.ADMIN_EMAIL if role == "admin" else getattr(TestConfig, f"{role.upper()}_EMAIL")
        return self.client.put(
            self.booking_url(booking_id, action),
            headers=auth_headers_for(email, role)
        )
    
    def get_bookings(self, role="buyer"):
        """Get bookings for a specific role."""
        email = getattr(TestConfig, f"{role.upper()}_EMAIL")
        return self.client.get(
            self.booking_url(),
            headers=auth_headers_for(email, role)
        )
    
    def create_booking_via_api(self, listing_id, role="buyer", **overrides):
        """Create a booking via API for a specific role."""
        from factories.bookings import booking_payload
        email = getattr(TestConfig, f"{role.upper()}_EMAIL")
        
        payload = booking_payload(listing_id=listing_id, **overrides)
        return self.client.post(
            f"{self.booking_url()}/request",
            json=payload,
            headers=auth_headers_for(email, role)
        )