from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.service import AuthService, get_auth_service

security = HTTPBearer(auto_error=False)


def require_roles(*roles):
    """Enforces that the authenticated user must have one of the specified roles."""
    def dependency(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user

    return dependency


def extract_token(credentials: HTTPAuthorizationCredentials, request: Request) -> str | None:
    """
    Extracts a token from Authorization header or from cookies.
    Header takes priority.
    """
    #Authorization header
    if credentials and credentials.credentials:
        return credentials.credentials

    #cookie-based auth as a second option
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    return None


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Gets the user from auth token and raises exception if not found."""
    token = extract_token(credentials, request)

    try:
        user = auth_service.get_current_user(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token")

    return user


def optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Returns the authenticated user if a valid token is provided, otherwise returns None."""
    token = extract_token(credentials, request)

    try:
        return auth_service.get_current_user(token)
    except Exception:
        return None