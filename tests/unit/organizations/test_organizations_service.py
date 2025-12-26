import pytest
from unittest.mock import Mock
from uuid import uuid4
from fastapi import HTTPException, status

from app.organizations.service import OrganizationsService
from app.organizations.repository import OrganizationsRepository
from app.organizations.models import Organization, OrganizationMembership, OrganizationStatus, OrgRole
from app.organizations.schemas import OrganizationCreate, OrganizationUpdate, MembershipCreate, MembershipUpdateRole
from app.organizations.permissions import OrgPermission

from app.users.public import UsersPublic


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def mock_repository():
    """Mock OrganizationsRepository fixture"""
    return Mock(spec=OrganizationsRepository)

@pytest.fixture
def mock_users_public():
    return Mock(spec=UsersPublic)

@pytest.fixture
def organization_service(mock_db, mock_repository, mock_users_public):
    """OrganizationsService fixture with all dependencies"""
    return OrganizationsService(
        db=mock_db,
        repo=mock_repository,
        users_public=mock_users_public,
    )

@pytest.fixture
def sample_organization():
    """Fixture for a mock organization object"""
    organization = Mock(spec=Organization)
    organization.id = uuid4()
    organization.name = "Test Organization"
    organization.billing_email = "billing@test.org"
    organization.status = OrganizationStatus.ACTIVE
    organization.created_at = Mock()
    organization.updated_at = Mock()
    return organization

@pytest.fixture
def sample_membership():
    """Fixture for a mock membership object"""
    membership = Mock(spec=OrganizationMembership)
    membership.id = uuid4()
    membership.organization_id = uuid4()
    membership.user_id = uuid4()
    membership.org_role = OrgRole.ADMIN
    membership.created_at = Mock()
    return membership

@pytest.fixture
def sample_member_membership():
    """Fixture for a mock member (non-admin) membership object"""
    membership = Mock(spec=OrganizationMembership)
    membership.id = uuid4()
    membership.organization_id = uuid4()
    membership.user_id = uuid4()
    membership.org_role = OrgRole.MEMBER
    membership.created_at = Mock()
    return membership

@pytest.fixture
def sample_organization_create_data():
    """Fixture for sample organization creation data"""
    return OrganizationCreate(
        name="Test Organization",
        billing_email="billing@test.org"
    )

@pytest.fixture
def sample_organization_update_data():
    """Fixture for sample organization update data"""
    return OrganizationUpdate(
        name="Updated Organization",
        billing_email="updated@test.org",
        status=OrganizationStatus.SUSPENDED
    )

@pytest.fixture
def sample_membership_create_data():
    """Fixture for sample membership creation data"""
    return MembershipCreate(
        user_id=uuid4(),
        role=OrgRole.MEMBER
    )

@pytest.fixture
def sample_membership_update_data():
    """Fixture for sample membership update data"""
    return MembershipUpdateRole(
        role=OrgRole.ADMIN
    )

class TestOrganizationsService:
    
    def test_create_organization_successfully_creates_and_adds_creator_as_admin(self, organization_service, mock_db, mock_repository, sample_organization_create_data, sample_organization, sample_member_membership):
        """Test successful organization creation with creator as admin"""
        creator_user_id = uuid4()
        mock_repository.create.return_value = sample_organization
        mock_repository.add_member.return_value = sample_member_membership

        result = organization_service.create_organization(creator_user_id, sample_organization_create_data)

        mock_repository.create.assert_called_once_with(mock_db, sample_organization_create_data.model_dump())
        mock_repository.add_member.assert_called_once_with(mock_db, sample_organization.id, creator_user_id, OrgRole.ADMIN)
        assert result == sample_organization

    def test_update_organization_successfully_updates_with_admin_permission(self, organization_service, mock_db, mock_repository, sample_organization, sample_membership, sample_organization_update_data):
        """Test successful organization update by admin"""
        org_id = uuid4()
        actor_user_id = uuid4()
        mock_repository.get_membership.return_value = sample_membership
        mock_repository.get.return_value = sample_organization
        mock_repository.update.return_value = sample_organization

        result = organization_service.update_organization(org_id, actor_user_id, sample_organization_update_data)

        mock_repository.get_membership.assert_called_once_with(mock_db, org_id, actor_user_id)
        mock_repository.get.assert_called_once_with(mock_db, org_id)
        mock_repository.update.assert_called_once_with(mock_db, sample_organization, sample_organization_update_data.model_dump(exclude_unset=True))
        assert result == sample_organization

    def test_update_organization_raises_error_when_not_admin(self, organization_service, mock_repository, sample_organization_update_data, sample_member_membership):
        """Test organization update fails when user is not admin"""
        org_id = uuid4()
        actor_user_id = uuid4()
        mock_repository.get_membership.return_value = sample_member_membership

        with pytest.raises(HTTPException, match="Organization admin permission required") as exception_info:
            organization_service.update_organization(org_id, actor_user_id, sample_organization_update_data)

        mock_repository.get.assert_not_called()
        mock_repository.update.assert_not_called()
        assert exception_info.value.status_code == 403

    def test_update_organization_raises_error_when_organization_not_found(self, organization_service, mock_repository, sample_membership, sample_organization_update_data):
        """Test organization update fails when organization doesn't exist"""
        org_id = uuid4()
        actor_user_id = uuid4()
        mock_repository.get_membership.return_value = sample_membership
        mock_repository.get.return_value = None

        with pytest.raises(HTTPException, match="Organization not found") as exception_info:
            organization_service.update_organization(org_id, actor_user_id, sample_organization_update_data)

        mock_repository.update.assert_not_called()
        assert exception_info.value.status_code == 404

    def test_add_member_successfully_adds_member_with_admin_permission(self, organization_service, mock_db, mock_repository, sample_membership):
        """Test successful member addition by admin"""
        org_id = uuid4()
        actor_user_id = uuid4()
        user_id = uuid4()
        mock_repository.get_membership.return_value = sample_membership
        mock_repository.add_member.return_value = sample_membership

        result = organization_service.add_member(org_id, actor_user_id, user_id, OrgRole.MEMBER)

        mock_repository.get_membership.assert_called_once_with(mock_db, org_id, actor_user_id)
        mock_repository.add_member.assert_called_once_with(mock_db, org_id, user_id, OrgRole.MEMBER)
        assert result == sample_membership

    def test_add_member_raises_error_when_not_admin(self, organization_service, mock_repository, sample_member_membership):
        """Test member addition fails when user is not admin"""
        org_id = uuid4()
        actor_user_id = uuid4()
        user_id = uuid4()
        mock_repository.get_membership.return_value = sample_member_membership
        
        with pytest.raises(HTTPException, match="Organization admin permission required") as exception_info:
            organization_service.add_member(org_id, actor_user_id, user_id, OrgRole.MEMBER)
        
        mock_repository.add_member.assert_not_called()
        assert exception_info.value.status_code == 403

    def test_remove_member_successfully_removes_member_with_admin_permission(self, organization_service, mock_db, mock_repository, sample_membership):
        """Test successful member removal by admin"""
        org_id = uuid4()
        actor_user_id = uuid4()
        user_id = uuid4()
        mock_repository.get_membership.return_value = sample_membership
        mock_repository.remove_member.return_value = None

        result = organization_service.remove_member(org_id, actor_user_id, user_id)
        
        mock_repository.get_membership.assert_called_once_with(mock_db, org_id, actor_user_id)
        mock_repository.remove_member.assert_called_once_with(mock_db, org_id, user_id)
        assert result is None

    def test_remove_member_raises_error_when_not_admin(self, organization_service, mock_repository):
        """Test member removal fails when user is not admin"""
        org_id = uuid4()
        actor_user_id = uuid4()
        user_id = uuid4()
        mock_repository.get_membership.return_value = None

        with pytest.raises(HTTPException, match="Organization admin permission required") as exception_info:
            organization_service.remove_member(org_id, actor_user_id, user_id)

        assert exception_info.value.status_code == 403
        mock_repository.remove_member.assert_not_called()

    def test_change_member_role_successfully_updates_role_with_admin_permission(self, organization_service, mock_db, mock_repository, sample_membership):
        """Test successful member role change by admin"""
        org_id = uuid4()
        actor_user_id = uuid4()
        user_id = uuid4()
        mock_repository.get_membership.return_value = sample_membership
        mock_repository.change_role.return_value = sample_membership

        result = organization_service.change_member_role(org_id, actor_user_id, user_id, OrgRole.ADMIN)
        
        mock_repository.get_membership.assert_called_once_with(mock_db, org_id, actor_user_id)
        mock_repository.change_role.assert_called_once_with(mock_db, org_id, user_id, OrgRole.ADMIN)
        assert result == sample_membership

    def test_change_member_role_raises_error_when_not_admin(self, organization_service, mock_repository):
        """Test member role change fails when user is not admin"""
        org_id = uuid4()
        actor_user_id = uuid4()
        user_id = uuid4()
        mock_repository.get_membership.return_value = None

        with pytest.raises(HTTPException, match="Organization admin permission required") as exception_info:
            organization_service.change_member_role(org_id, actor_user_id, user_id, OrgRole.MEMBER)

        assert exception_info.value.status_code == 403
        mock_repository.change_role.assert_not_called()

    def test_list_user_organizations_delegates_to_repository(self, organization_service, mock_db, mock_repository):
        """Test listing user organizations delegates to repository"""
        user_id = uuid4()
        sample_organizations = [Mock(spec=Organization), Mock(spec=Organization)]
        mock_repository.list_for_user.return_value = sample_organizations
        
        result = organization_service.list_user_organizations(user_id)
        mock_repository.list_for_user.assert_called_once_with(mock_db, user_id)

        assert result == sample_organizations

    def test_list_user_organizations_returns_empty_list_when_none_exist(self, organization_service, mock_db, mock_repository):
        """Test listing user organizations returns empty list when none exist"""
        user_id = uuid4()
        mock_repository.list_for_user.return_value = []

        result = organization_service.list_user_organizations(user_id)
        assert result == []
        mock_repository.list_for_user.assert_called_once_with(mock_db, user_id)

    def test_list_members_successfully_returns_members_with_member_permission(self, organization_service, mock_db, mock_repository, sample_member_membership):
        """Test successful member listing with member permission"""
        org_id = uuid4()
        requesting_user_id = uuid4()
        sample_members = [Mock(spec=OrganizationMembership), Mock(spec=OrganizationMembership)]

        mock_repository.get_membership.return_value = sample_member_membership
        mock_repository.list_members.return_value = sample_members

        result = organization_service.list_members(org_id, requesting_user_id)
        
        mock_repository.get_membership.assert_called_once_with(mock_db, org_id, requesting_user_id)
        mock_repository.list_members.assert_called_once_with(mock_db, org_id)
        assert result == sample_members

    def test_list_members_raises_error_when_not_member(self, organization_service, mock_repository):
        """Test member listing fails when user is not a member"""
        org_id = uuid4()
        requesting_user_id = uuid4()
        mock_repository.get_membership.return_value = None

        with pytest.raises(HTTPException, match="Organization membership required") as exception_info:
            organization_service.list_members(org_id, requesting_user_id)

        assert exception_info.value.status_code == 403
        mock_repository.list_members.assert_not_called()

    def test_is_org_admin_returns_true_for_admin_member(self, organization_service, mock_repository, sample_membership):
        """Test is_org_admin returns true for admin member"""
        org_id = uuid4()
        user_id = uuid4()
        sample_membership.org_role = OrgRole.ADMIN
        mock_repository.get_membership.return_value = sample_membership

        result = organization_service.is_org_admin(user_id, org_id)

        mock_repository.get_membership.assert_called_once()
        assert result == True

    def test_is_org_admin_returns_false_for_non_admin_member(self, organization_service, mock_repository, sample_member_membership):
        """Test is_org_admin returns false for non-admin member"""
        org_id = uuid4()
        user_id = uuid4()
        sample_member_membership.org_role = OrgRole.MEMBER
        mock_repository.get_membership.return_value = sample_member_membership

        result = organization_service.is_org_admin(user_id, org_id)

        mock_repository.get_membership.assert_called_once()
        assert result == False

    def test_is_org_admin_returns_false_for_non_member(self, organization_service, mock_repository):
        """Test is_org_admin returns false for non-member"""
        org_id = uuid4()
        user_id = uuid4()
        mock_repository.get_membership.return_value = None

        result = organization_service.is_org_admin(user_id, org_id)

        mock_repository.get_membership.assert_called_once()
        assert result == False

    def test_is_org_member_returns_true_for_member(self, organization_service, mock_repository, sample_member_membership):
        """Test is_org_member returns true for member"""
        org_id = uuid4()
        user_id = uuid4()
        mock_repository.get_membership.return_value = sample_member_membership

        result = organization_service.is_org_member(user_id, org_id)

        mock_repository.get_membership.assert_called_once()
        assert result == True

    def test_is_org_member_returns_false_for_non_member(self, organization_service, mock_repository):
        """Test is_org_member returns false for non-member"""
        org_id = uuid4()
        user_id = uuid4()
        mock_repository.get_membership.return_value = None

        result = organization_service.is_org_member(user_id, org_id)

        mock_repository.get_membership.assert_called_once()
        assert result == False