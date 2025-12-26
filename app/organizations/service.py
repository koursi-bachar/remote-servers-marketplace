import random
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import List, Dict
from sqlalchemy.orm import Session

from app.database import get_db

from .repository import OrganizationsRepository
from .models import OrgRole
from .schemas import OrganizationCreate, OrganizationUpdate, MembershipCreate, MembershipUpdateRole
from .permissions import OrgPermission

from app.users.public import UsersPublic, get_users_public


class OrganizationsService:
    def __init__(
        self,
        db: Session,
        repo: OrganizationsRepository,
        users_public: UsersPublic,
    ):
        self.db = db
        self.repo = repo
        self.users_public = users_public

    def create_organization(self, creator_user_id: UUID, payload: OrganizationCreate):
        """Creator becomes the first admin automatically."""
        org = self.repo.create(self.db, payload.model_dump())

        #creator is automatically an admin
        self.repo.add_member(self.db, org.id, creator_user_id, OrgRole.ADMIN)

        return org

    def update_organization(self, org_id: UUID, actor_user_id: UUID, payload: OrganizationUpdate):
        """Only organization admins may update org metadata."""
        membership = self.repo.get_membership(self.db, org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        org = self.repo.get(self.db, org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        return self.repo.update(self.db, org, payload.model_dump(exclude_unset=True))

    #Org membership
    def add_member(self, org_id: UUID, actor_user_id: UUID, user_id: UUID, role: OrgRole):
        """
        Admin adds another member.
        """
        membership = self.repo.get_membership(self.db, org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        return self.repo.add_member(self.db, org_id, user_id, role)

    def remove_member(self, org_id: UUID, actor_user_id: UUID, user_id: UUID):
        """
        Admin removes a member.
        """
        membership = self.repo.get_membership(self.db, org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        return self.repo.remove_member(self.db, org_id, user_id)

    def list_user_organizations(self, user_id: UUID):
        """
        List all orgs a user is a member of.
        """
        return self.repo.list_for_user(self.db, user_id)

    def list_members(self, org_id: UUID, requesting_user_id: UUID):
        """
        Only members of an organization can view membership lists.
        """
        membership = self.repo.get_membership(self.db, org_id, requesting_user_id)
        OrgPermission.require_member(membership)

        return self.repo.list_members(self.db, org_id)

    #helpers exposed in public interface
    def is_org_admin(self, user_id: UUID, org_id: UUID) -> bool:
        """
        Public helper used by other domains (Bookings, Providers, Invoices).
        """
        membership = self.repo.get_membership(self.db, org_id, user_id)
        return membership is not None and membership.org_role == OrgRole.ADMIN

    def is_org_member(self, user_id: UUID, org_id: UUID) -> bool:
        membership = self.repo.get_membership(self.db, org_id, user_id)
        return membership is not None
    
    def change_member_role(self, org_id: UUID, actor_user_id: UUID, user_id: UUID, role: OrgRole):
        """
        Admin changes another user's role.
        """
        membership = self.repo.get_membership(self.db, org_id, actor_user_id)
        OrgPermission.require_admin(membership)
        
        # Check if trying to change own role
        if actor_user_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role",
            )
        
        # Check if at least one admin remains
        if role != OrgRole.ADMIN:
            admin_count = len([
                m for m in self.repo.list_members(self.db, org_id)
                if m.org_role == OrgRole.ADMIN
            ])
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization must have at least one admin",
                )
        
        updated = self.repo.change_role(self.db, org_id, user_id, role)
        return updated

    def get_member_usage_stats(self, org_id: UUID, user_id: UUID) -> Dict:
        """
        Generate mock usage statistics for a member.
        In a real system, this would query bookings, compute hours, spending, etc.
        """
        #Generate deterministic but varied mock data based on user_id
        random.seed(str(user_id) + str(org_id))
        
        #Mock data generation
        total_hours = random.randint(0, 500)
        total_spending = round(total_hours * random.uniform(0.5, 5.0), 2)
        active_bookings = random.randint(0, 3)
        completed_bookings = random.randint(0, 20)
        avg_session_hours = round(random.uniform(1.0, 24.0), 1)
        
        #Generate time-based data
        now = datetime.now(timezone.utc)
        last_30_days = []
        for i in range(30):
            date = (now - timedelta(days=29-i)).strftime('%Y-%m-%d')
            usage = random.randint(0, 12) if random.random() > 0.7 else 0
            last_30_days.append({
                'date': date,
                'hours': usage,
                'spending': round(usage * random.uniform(0.5, 5.0), 2)
            })
        
        return {
            'user_id': str(user_id),
            'org_id': str(org_id),
            'total_hours': total_hours,
            'total_spending': total_spending,
            'active_bookings': active_bookings,
            'completed_bookings': completed_bookings,
            'avg_session_hours': avg_session_hours,
            'last_30_days': last_30_days,
            'preferred_resources': random.sample([
                'GPU Servers', 'CPU Clusters', 'Storage', 'Memory-Optimized',
                'High-Performance Computing', 'Development Environments'
            ], random.randint(1, 3)),
            'usage_tier': random.choice(['Low', 'Medium', 'High', 'Very High']),
            'last_active': (now - timedelta(days=random.randint(0, 7))).isoformat(),
        }

    def get_org_members_with_details(self, org_id: UUID, requesting_user_id: UUID) -> List[Dict]:
        """
        Get organization members with enriched details including email and usage stats.
        Only members can view this list.
        """
        membership = self.repo.get_membership(self.db, org_id, requesting_user_id)
        OrgPermission.require_member(membership)
        
        members = self.repo.list_members(self.db, org_id)
        result = []
        
        for member in members:
            member_dict = {
                'id': str(member.id),
                'user_id': str(member.user_id),
                'org_role': member.org_role.value,
                'created_at': member.created_at,
                'user_email': None,
            }
            
            #Add usage stats
            if self.users_public:
                try:
                    user = self.users_public.get_user(member.user_id)
                    if user:
                        member_dict['user_email'] = user.email
                except:
                    pass  #Silently fail if can't get user info
            
            #Add usage statistics
            member_dict['usage_stats'] = self.get_member_usage_stats(org_id, member.user_id)
            
            result.append(member_dict)
        
        return result

    def admin_add_members_bulk(self, org_id: UUID, user_ids: List[UUID], role: OrgRole = OrgRole.MEMBER):
        """
        Admin-only: Add multiple members to organization at once.
        Useful for initial setup or bulk operations.
        """
        # Note: This doesn't check actor permissions - should be called from a route that does
        results = []
        for user_id in user_ids:
            try:
                #Check if user is already a member
                existing = self.repo.get_membership(self.db, org_id, user_id)
                if existing:
                    results.append({
                        'user_id': str(user_id),
                        'status': 'already_member',
                        'role': existing.org_role.value
                    })
                    continue
                
                #Add member
                record = self.repo.add_member(self.db, org_id, user_id, role)
                results.append({
                    'user_id': str(user_id),
                    'status': 'added',
                    'role': role.value,
                    'membership_id': str(record.id)
                })
            except Exception as e:
                results.append({
                    'user_id': str(user_id),
                    'status': 'error',
                    'error': str(e)
                })
        
        return results

def get_organization_service(
    db: Session = Depends(get_db),
    users_public: UsersPublic = Depends(get_users_public)
) -> OrganizationsService:
    repo = OrganizationsRepository()
    return OrganizationsService(
        db=db,
        repo=repo,
        users_public=users_public,
    )