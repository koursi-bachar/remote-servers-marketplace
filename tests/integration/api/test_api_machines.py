from factories.users import auth_headers_by_role
from factories.machines import create_machine
from assertions import assert_status_code, assert_forbidden


def test_get_nonexistent_machine_returns_404(client, db_session):
    """
    Getting a non-existent machine returns a 404 error.
    """
    resp = client.get(
        "/api/v1/machines/999999/",  #This machine ID doesn't exist
        headers=auth_headers_by_role("provider")
    )
    assert_status_code(resp, 404)

def test_provider_cannot_access_other_providers_machine(client, db_session):
    """
    Provider cannot access machines belonging to other providers.
    """
    #Create machine with one provider
    machine = create_machine(client, db_session, provider_role="provider")
    
    #Try to access with a different provider
    from factories.users import create_user, auth_headers_for
    other_provider = create_user(db_session, "other@example.com", "provider")
    
    resp = client.get(
        f"/api/v1/machines/{machine['id']}/",
        headers=auth_headers_for("other@example.com", "provider")
    )
    assert_forbidden(resp)