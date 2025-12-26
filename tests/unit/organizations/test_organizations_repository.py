import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timezone

from app.organizations.repository import OrganizationsRepository
from app.organizations.models import Organization, OrganizationMembership, OrganizationStatus, OrgRole


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def organizations_repository():
    """OrganizationsRepository instance fixture"""
    return OrganizationsRepository()

@pytest.fixture
def sample_organization():
    """Fixture for a mock organization object"""
    organization = Mock(spec=Organization)
    organization.id = uuid4()
    organization.name = "Test Organization"
    organization.billing_email = "billing@test.org"
    organization.status = OrganizationStatus.ACTIVE
    organization.created_at = datetime.now(timezone.utc)
    organization.updated_at = datetime.now(timezone.utc)
    return organization

@pytest.fixture
def sample_membership():
    """Fixture for a mock membership object"""
    membership = Mock(spec=OrganizationMembership)
    membership.id = uuid4()
    membership.organization_id = uuid4()
    membership.user_id = uuid4()
    membership.org_role = OrgRole.MEMBER
    membership.created_at = datetime.now(timezone.utc)
    return membership

class TestOrganizationsRepository:
    
    def test_create_performs_database_operations(self, mock_db, organizations_repository):
        """Test that organization creation performs database operations"""
        data = {
            "name": "Test Organization",
            "billing_email": "billing@test.org",
            "status": OrganizationStatus.ACTIVE
        }
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        organizations_repository.create(mock_db, data)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_update_performs_database_operations(self, mock_db, organizations_repository, sample_organization):
        """Test that organization update performs database operations"""
        data = {"name": "Updated Organization", "status": OrganizationStatus.SUSPENDED}
        
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        result = organizations_repository.update(mock_db, sample_organization, data)
        
        assert result == sample_organization
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_organization)

    def test_get_returns_organization_when_exists(self, mock_db, organizations_repository, sample_organization):
        """Test getting organization by ID returns organization"""
        org_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter_by.return_value
        mock_filtered_query.first.return_value = sample_organization
        
        result = organizations_repository.get(mock_db, org_id)
        
        assert result == sample_organization
        mock_db.query.assert_called_once_with(Organization)
        mock_query.filter_by.assert_called_once_with(id=org_id)

    def test_get_returns_none_when_not_found(self, mock_db, organizations_repository):
        """Test getting organization by ID returns None when not found"""
        org_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter_by.return_value
        mock_filtered_query.first.return_value = None
        
        result = organizations_repository.get(mock_db, org_id)
        
        assert result is None
        mock_db.query.assert_called_once_with(Organization)

    def test_list_for_user_returns_user_organizations(self, mock_db, organizations_repository):
        """Test getting organizations for a user returns list"""
        user_id = uuid4()
        mock_organizations = [Mock(spec=Organization), Mock(spec=Organization)]
        
        mock_query = mock_db.query.return_value
        mock_joined_query = mock_query.join.return_value
        mock_filtered_query = mock_joined_query.filter.return_value
        mock_filtered_query.all.return_value = mock_organizations
        
        result = organizations_repository.list_for_user(mock_db, user_id)
        
        assert result == mock_organizations
        mock_db.query.assert_called_once_with(Organization)
        mock_query.join.assert_called_once_with(OrganizationMembership)
        mock_joined_query.filter.assert_called_once()

    def test_list_for_user_returns_empty_list_when_none_exist(self, mock_db, organizations_repository):
        """Test getting organizations for user returns empty list when none exist"""
        user_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_joined_query = mock_query.join.return_value
        mock_filtered_query = mock_joined_query.filter.return_value
        mock_filtered_query.all.return_value = []
        
        result = organizations_repository.list_for_user(mock_db, user_id)
        
        assert result == []
        mock_db.query.assert_called_once_with(Organization)

    def test_add_member_performs_database_operations(self, mock_db, organizations_repository, sample_membership):
        """Test that adding a member performs database operations"""
        org_id = uuid4()
        user_id = uuid4()
        role = OrgRole.ADMIN
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        result = organizations_repository.add_member(mock_db, org_id, user_id, role)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_remove_member_performs_database_operations(self, mock_db, organizations_repository):
        """Test that removing a member performs database operations"""
        org_id = uuid4()
        user_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter_by.return_value
        mock_filtered_query.delete.return_value = None
        
        organizations_repository.remove_member(mock_db, org_id, user_id)
        
        mock_db.query.assert_called_once_with(OrganizationMembership)
        mock_query.filter_by.assert_called_once_with(organization_id=org_id, user_id=user_id)
        mock_db.commit.assert_called_once()

    def test_change_role_updates_existing_membership(self, mock_db, organizations_repository, sample_membership):
        """Test changing role for existing membership"""
        org_id = uuid4()
        user_id = uuid4()
        new_role = OrgRole.ADMIN
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter_by.return_value
        mock_filtered_query.first.return_value = sample_membership
        
        result = organizations_repository.change_role(mock_db, org_id, user_id, new_role)
        
        assert result == sample_membership
        assert sample_membership.org_role == new_role
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_membership)

    def test_list_members_returns_organization_members(self, mock_db, organizations_repository, sample_membership):
        """Test getting members for an organization returns list"""
        org_id = uuid4()
        mock_memberships = [sample_membership, Mock(spec=OrganizationMembership)]
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter_by.return_value
        mock_filtered_query.all.return_value = mock_memberships
        
        result = organizations_repository.list_members(mock_db, org_id)
        
        assert result == mock_memberships
        mock_db.query.assert_called_once_with(OrganizationMembership)
        mock_query.filter_by.assert_called_once_with(organization_id=org_id)

    def test_list_members_returns_empty_list_when_no_members(self, mock_db, organizations_repository):
        """Test getting members for organization returns empty list when none exist"""
        org_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter_by.return_value
        mock_filtered_query.all.return_value = []
        
        result = organizations_repository.list_members(mock_db, org_id)
        
        assert result == []
        mock_db.query.assert_called_once_with(OrganizationMembership)

    def test_get_membership_returns_membership_when_exists(self, mock_db, organizations_repository, sample_membership):
        """Test getting membership returns membership when exists"""
        org_id = uuid4()
        user_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter_by.return_value
        mock_filtered_query.first.return_value = sample_membership
        
        result = organizations_repository.get_membership(mock_db, org_id, user_id)
        
        assert result == sample_membership
        mock_db.query.assert_called_once_with(OrganizationMembership)
        mock_query.filter_by.assert_called_once_with(organization_id=org_id, user_id=user_id)

    def test_get_membership_returns_none_when_not_found(self, mock_db, organizations_repository):
        """Test getting membership returns None when not found"""
        org_id = uuid4()
        user_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter_by.return_value
        mock_filtered_query.first.return_value = None
        
        result = organizations_repository.get_membership(mock_db, org_id, user_id)
        
        assert result is None
        mock_db.query.assert_called_once_with(OrganizationMembership)