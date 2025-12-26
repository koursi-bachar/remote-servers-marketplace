from fastapi import HTTPException, status
from uuid import UUID
from .models import OrgRole

class OrgPermission:
    @staticmethod
    def require_admin(membership):
        if membership is None or membership.org_role != OrgRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization admin permission required",
            )
        
    @staticmethod
    def require_member(membership):
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization membership required",
            )