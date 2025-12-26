from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.auth.auth import get_current_user
from app.users.models import User
from typing import List

from .models import OrgRole
from .service import OrganizationsService, get_organization_service
from .schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationRead,
    MembershipCreate,
    MembershipRead,
    MembershipUpdateRole,
)


router = APIRouter()

#Organization CRUD
@router.post("/", response_model=OrganizationRead, status_code=201)
def create_organization(
    payload: OrganizationCreate,
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """
    Any authenticated user may create an organization.
    They automatically become the first admin.
    """
    return service.create_organization(user.id, payload)

@router.get("/mine", response_model=list[OrganizationRead])
def list_my_organizations(
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """List all organizations the authenticated user belongs to."""
    return service.list_user_organizations(user.id)

@router.patch("/{org_id:uuid}", response_model=OrganizationRead)
def update_organization(
    org_id: UUID,
    payload: OrganizationUpdate,
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """Only organization admins may update the org."""
    try:
        return service.update_organization(org_id, user.id, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

#Membership management
@router.get("/{org_id:uuid}/members", response_model=list[MembershipRead])
def list_members(
    org_id: UUID,
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """Only organization members may view membership lists."""
    try:
        return service.list_members(org_id, user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

@router.post("/{org_id:uuid}/members", response_model=MembershipRead, status_code=201)
def add_member(
    org_id: UUID,
    payload: MembershipCreate,
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """
    Only organization admins may add new members.
    """
    if not service.is_org_admin(user.id, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required",
        )

    try:
        return service.add_member(org_id, user.id, payload.user_id, payload.role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

@router.patch("/{org_id:uuid}/members/{user_id:uuid}")
def update_member_role(
    org_id: UUID,
    user_id: UUID,
    payload: MembershipUpdateRole,
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """
    Only admins may change roles.
    """
    try:
        return service.change_member_role(org_id, user.id, user_id, payload.role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

@router.delete("/{org_id:uuid}/members/{user_id:uuid}", status_code=204)
def remove_member(
    org_id: UUID,
    user_id: UUID,
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """Only admin can remove a member."""
    try:
        service.remove_member(org_id, user.id, user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return None

@router.get("/{org_id:uuid}/members/details", response_model=List[dict])
def get_organization_members_details(
    org_id: UUID,
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """
    Get organization members with detailed information including usage stats.
    Only organization members can view this.
    """
    try:
        return service.get_org_members_with_details(org_id, user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

@router.get("/{org_id:uuid}/members/{user_id:uuid}/usage")
def get_member_usage_stats(
    org_id: UUID,
    user_id: UUID,
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """
    Get usage statistics for a specific member.
    Only organization members can view this.
    """
    # Check if requesting user is member of organization
    if not service.is_org_member(user.id, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    # Check if requested user is member of organization
    if not service.is_org_member(user_id, org_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in organization",
        )
    
    return service.get_member_usage_stats(org_id, user_id)

# Admin-only bulk operations
@router.post("/{org_id:uuid}/members/bulk", status_code=201)
def admin_add_members_bulk(
    org_id: UUID,
    payload: dict,
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """
    Admin-only: Add multiple members to organization at once.
    User must be site admin or organization admin.
    """
    # Check permissions - user must be site admin OR org admin
    if not service.is_org_admin(user.id, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required",
        )
    
    user_ids = [UUID(uid) for uid in payload.get("user_ids", [])]
    role_str = payload.get("role", "member")
    
    try:
        role = OrgRole(role_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {role_str}. Must be 'admin' or 'member'",
        )
    
    try:
        results = service.admin_add_members_bulk(org_id, user_ids, role)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

@router.get("/{org_id:uuid}/stats")
def get_organization_stats(
    org_id: UUID,
    user: User = Depends(get_current_user),
    service: OrganizationsService = Depends(get_organization_service),
):
    """
    Get organization statistics including member counts and usage summary.
    Only organization members can view this.
    """
    if not service.is_org_member(user.id, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    members = service.repo.list_members(service.db, org_id)
    
    # Generate mock org stats
    import random
    random.seed(str(org_id))
    
    total_members = len(members)
    admin_count = sum(1 for m in members if m.org_role == OrgRole.ADMIN)
    
    # Mock usage stats
    total_hours = random.randint(0, 5000)
    total_spending = round(total_hours * random.uniform(0.5, 5.0), 2)
    active_users = random.randint(1, min(total_members, 10))
    
    # Top users (mock)
    top_users = []
    for member in random.sample(members, min(3, len(members))):
        user_hours = random.randint(0, total_hours // 2)
        top_users.append({
            'user_id': str(member.user_id),
            'hours': user_hours,
            'spending': round(user_hours * random.uniform(0.5, 5.0), 2)
        })
    
    return {
        'total_members': total_members,
        'admin_count': admin_count,
        'member_count': total_members - admin_count,
        'total_hours': total_hours,
        'total_spending': total_spending,
        'active_users': active_users,
        'avg_hours_per_user': round(total_hours / max(total_members, 1), 1),
        'top_users': top_users,
        'created_at': None,
    }