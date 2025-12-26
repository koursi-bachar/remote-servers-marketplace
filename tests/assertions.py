"""
Reusable assertion helpers to run consistent test validation.
"""

def _get_response_data(response):
    """Extract data from response object or return as-is if already a dict."""
    if hasattr(response, 'json'):
        return response.json()
    return response

def assert_status_code(response, expected_code=200, message=None):
    """
    Assert response status code with optional custom message.
    Usage:
        assert_status_code(resp, 201)
        assert_status_code(resp, 200, "Should return OK")
    """
    if hasattr(response, 'status_code'):
        actual_code = response.status_code
    else:
        raise ValueError("Response object required for status code assertion")
   
    if message:
        assert actual_code == expected_code, message
    else:
        assert actual_code == expected_code, \
            f"Expected status {expected_code}, got {actual_code}. Response: {getattr(response, 'text', 'N/A')}"

def assert_booking_status(response, expected_status):
    """
    Assert booking status in response.
    
    Usage:
        assert_booking_status(resp, "confirmed")
    """
    data = _get_response_data(response)
    actual_status = data["status"].lower()
    assert actual_status == expected_status.lower(), \
        f"Expected booking status '{expected_status}', got '{actual_status}'"

def assert_response_contains(response, field, expected_value=None):
    """
    Assert response contains field and optionally check its value.
    
    Usage:
        assert_response_contains(resp, "id")
        assert_response_contains(resp, "status", "confirmed")
    """
    data = _get_response_data(response)
    assert field in data, f"Field '{field}' not found in response: {data}"
    
    if expected_value is not None:
        assert data[field] == expected_value, \
            f"Field '{field}' expected '{expected_value}', got '{data[field]}'"

def assert_response_contains_fields(response, *fields):
    """
    Assert response contains multiple fields.
    Usage:
        assert_response_contains_fields(resp, "id", "status", "listing_id")
    """
    data = _get_response_data(response)
    for field in fields:
        assert field in data, f"Field '{field}' not found in response: {data}"

def assert_is_list(response, min_length=1):
    """
    Assert response is a list with minimum length.
    Usage:
        assert_is_list(resp)  #At least 1 item
        assert_is_list(resp, 3)  #At least 3 items
    """
    data = _get_response_data(response)
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) >= min_length, f"Expected at least {min_length} items, got {len(data)}"

def assert_any_item_contains(response, field, value):
    """
    Assert any item in a list response contains field with value.
    Usage:
        assert_any_item_contains(resp, "title", "Default Title")
    """
    data = _get_response_data(response)
    assert any(item.get(field) == value for item in data), \
        f"No item found with {field} = {value} in: {data}"

def assert_timestamp_field_exists(response, field):
    """
    Assert a timestamp field exists and is not None.
    Usage:
        assert_timestamp_field_exists(resp, "active_session_start")
    """
    data = _get_response_data(response)
    assert field in data, f"Timestamp field '{field}' not found"
    assert data[field] is not None, f"Timestamp field '{field}' is None"

#Specialized assertions for common patterns
def assert_booking_created_successfully(response):
    """Assert common booking creation success patterns."""
    assert_status_code(response, 201)
    assert_response_contains_fields(response, "id", "status", "listing_id")

def assert_booking_lifecycle_state(response, expected_status, has_active_session=False):
    """Assert booking state during lifecycle transitions."""
    assert_status_code(response, 200)
    assert_booking_status(response, expected_status)
    
    if has_active_session:
        assert_timestamp_field_exists(response, "active_session_start")

def assert_unauthorized(response):
    """Assert request was unauthorized (401)."""
    assert_status_code(response, 401)

def assert_forbidden(response):
    """Assert request was forbidden (403)."""
    assert_status_code(response, 403)