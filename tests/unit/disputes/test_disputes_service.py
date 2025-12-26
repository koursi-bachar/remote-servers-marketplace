import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime, timezone

from app.disputes.service import DisputesService
from app.disputes.repository import DisputesRepository
from app.disputes.models import Dispute, DisputeStatus
from app.disputes.schemas import DisputeCreate, DisputeResolution
from app.bookings.public import BookingsPublic
from app.payments.public import PaymentsPublic
from app.notifications.public import NotificationsPublic


@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_repository():
    return Mock(spec=DisputesRepository)

@pytest.fixture
def mock_bookings_public():
    return Mock(spec=BookingsPublic)

@pytest.fixture
def mock_payments_public():
    return Mock(spec=PaymentsPublic)

@pytest.fixture
def mock_notifications_public():
    return Mock(spec=NotificationsPublic)

@pytest.fixture
def dispute_service(
    mock_db, mock_repository, mock_bookings_public, mock_payments_public, mock_notifications_public
):
    """Main service fixture that composes other fixtures"""
    return DisputesService(
        db=mock_db,
        repo=mock_repository,
        bookings_public=mock_bookings_public,
        payments_public=mock_payments_public,
        notifications_public=mock_notifications_public,
    )

@pytest.fixture
def sample_dispute_data():
    """Fixture for sample dispute creation data"""
    return DisputeCreate(
        booking_id=uuid4(),
        reason="Service not provided as described",
    )

@pytest.fixture
def sample_dispute():
    """Fixture for a sample dispute instance"""
    dispute = Mock(spec=Dispute)
    dispute.id = uuid4()
    dispute.booking_id = uuid4()
    dispute.user_id = uuid4()
    dispute.status = DisputeStatus.OPEN
    dispute.reason = "Test dispute"
    dispute.resolution_notes = None
    dispute.resolved_at = None
    dispute.user = Mock()
    return dispute

@pytest.fixture
def sample_booking():
    """Fixture for a sample booking instance"""
    booking = Mock()
    booking.id = uuid4()
    booking.buyer_user_id = uuid4()
    
    mock_machine = Mock()
    mock_machine.provider_id = uuid4()
    
    mock_listing = Mock()
    mock_listing.machine = mock_machine
    booking.listing = mock_listing
    
    return booking

class TestDisputesService:
    
    def test_get_dispute_or_raise_returns_dispute_when_exists(self, dispute_service, mock_db, mock_repository):
        """Test successful dispute retrieval"""
        mock_existing_dispute = Mock(spec=Dispute)
        dispute_id = uuid4()
        
        mock_repository.get_by_id.return_value = mock_existing_dispute
        
        result = dispute_service._get_dispute_or_raise(dispute_id)
        
        assert result == mock_existing_dispute
        mock_repository.get_by_id.assert_called_once_with(mock_db, dispute_id)

    def test_get_dispute_or_raise_raises_error_when_not_found(self, dispute_service, mock_db, mock_repository):
        """Test error when dispute doesn't exist"""
        dispute_id = uuid4()

        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Dispute not found"):
            dispute_service._get_dispute_or_raise(dispute_id)
        
        mock_repository.get_by_id.assert_called_once_with(mock_db, dispute_id)

    def test_get_booking_or_raise_returns_booking_when_exists(
        self, dispute_service, mock_bookings_public
    ):
        """Test successful booking retrieval"""
        mock_booking = Mock()
        booking_id = uuid4()
        
        mock_bookings_public.get_booking.return_value = mock_booking
        
        result = dispute_service._get_booking_or_raise(booking_id)
        
        assert result == mock_booking
        mock_bookings_public.get_booking.assert_called_once_with(booking_id)

    def test_get_booking_or_raise_raises_error_when_not_found(
        self, dispute_service, mock_bookings_public
    ):
        """Test error when booking doesn't exist"""
        booking_id = uuid4()

        mock_bookings_public.get_booking.return_value = None

        with pytest.raises(ValueError, match="Booking not found"):
            dispute_service._get_booking_or_raise(booking_id)
        
        mock_bookings_public.get_booking.assert_called_once_with(booking_id)

    def test_validate_booking_access_allows_buyer(self, dispute_service, sample_booking):
        """Test buyer can access their own booking"""
        user_id = sample_booking.buyer_user_id
        
        result = dispute_service._validate_booking_access(sample_booking, user_id)
        
        assert result is True

    def test_validate_booking_access_allows_provider(self, dispute_service, sample_booking):
        """Test provider can access booking for their machine"""
        user_id = sample_booking.listing.machine.provider_id
        
        result = dispute_service._validate_booking_access(sample_booking, user_id)
        
        assert result is True

    def test_validate_booking_access_raises_error_for_unauthorized_user(
        self, dispute_service, sample_booking
    ):
        """Test unauthorized user cannot access booking"""
        unauthorized_user_id = uuid4()
        
        with pytest.raises(ValueError, match="User not authorized to dispute this booking"):
            dispute_service._validate_booking_access(sample_booking, unauthorized_user_id)

    def test_validate_unique_open_dispute_allows_when_no_open_disputes(
        self, dispute_service, mock_db, mock_repository
    ):
        """Test allows dispute when no open disputes exist"""
        booking_id = uuid4()
        
        # Mock only closed disputes
        mock_closed_dispute = Mock()
        mock_closed_dispute.status = DisputeStatus.CLOSED
        mock_repository.list_for_booking.return_value = [mock_closed_dispute]
        
        dispute_service._validate_unique_open_dispute(booking_id)
        
        mock_repository.list_for_booking.assert_called_once_with(mock_db, booking_id)

    def test_validate_unique_open_dispute_raises_error_when_open_dispute_exists(
        self, dispute_service, mock_db, mock_repository
    ):
        """Test raises error when open dispute already exists"""
        booking_id = uuid4()
        
        # Mock an open dispute
        mock_open_dispute = Mock()
        mock_open_dispute.status = DisputeStatus.OPEN
        mock_repository.list_for_booking.return_value = [mock_open_dispute]
        
        with pytest.raises(ValueError, match="An open dispute already exists for this booking"):
            dispute_service._validate_unique_open_dispute(booking_id)

    def test_open_dispute_successfully_creates_dispute(
        self, dispute_service, mock_db, mock_repository, mock_bookings_public,
        mock_notifications_public, sample_dispute_data, sample_booking
    ):
        """Test successful dispute creation"""
        user_id = sample_booking.buyer_user_id
        sample_dispute_data.booking_id = sample_booking.id
        
        mock_new_dispute = Mock(spec=Dispute)
        
        mock_bookings_public.get_booking.return_value = sample_booking
        mock_repository.list_for_booking.return_value = []
        mock_repository.create_dispute.return_value = mock_new_dispute
        
        result = dispute_service.open_dispute(user_id, sample_dispute_data)
        
        assert result == mock_new_dispute
        mock_bookings_public.get_booking.assert_called_once_with(sample_booking.id)
        mock_repository.create_dispute.assert_called_once_with(
            mock_db,
            booking_id=sample_booking.id,
            user_id=user_id,
            reason=sample_dispute_data.reason,
        )
        mock_notifications_public.dispute_opened.assert_called_once_with(mock_new_dispute, user_id)

    def test_open_dispute_raises_error_when_booking_not_found(
        self, dispute_service, mock_bookings_public, sample_dispute_data
    ):
        """Test error when booking doesn't exist"""
        user_id = uuid4()
        
        mock_bookings_public.get_booking.return_value = None
        
        with pytest.raises(ValueError, match="Booking not found"):
            dispute_service.open_dispute(user_id, sample_dispute_data)

    def test_open_dispute_raises_error_when_user_not_authorized(
        self, dispute_service, mock_bookings_public, sample_dispute_data, sample_booking
    ):
        """Test error when user is not authorized"""
        unauthorized_user_id = uuid4()
        sample_dispute_data.booking_id = sample_booking.id
        
        mock_bookings_public.get_booking.return_value = sample_booking
        
        with pytest.raises(ValueError, match="User not authorized to dispute this booking"):
            dispute_service.open_dispute(unauthorized_user_id, sample_dispute_data)

    def test_list_disputes_for_user_delegates_to_repository(
        self, dispute_service, mock_db, mock_repository
    ):
        """Test listing disputes delegates to repository"""
        user_id = uuid4()
        mock_disputes = [Mock(spec=Dispute), Mock(spec=Dispute)]
        
        mock_repository.list_for_user.return_value = mock_disputes
        
        result = dispute_service.list_disputes_for_user(user_id)
        
        assert result == mock_disputes
        mock_repository.list_for_user.assert_called_once_with(mock_db, user_id)

    def test_list_disputes_for_booking_delegates_to_repository(
        self, dispute_service, mock_db, mock_repository
    ):
        """Test listing disputes for booking delegates to repository"""
        booking_id = uuid4()
        mock_disputes = [Mock(spec=Dispute), Mock(spec=Dispute)]
        
        mock_repository.list_for_booking.return_value = mock_disputes
        
        result = dispute_service.list_disputes_for_booking(booking_id)
        
        assert result == mock_disputes
        mock_repository.list_for_booking.assert_called_once_with(mock_db, booking_id)

    def test_list_open_for_admin_delegates_to_repository(
        self, dispute_service, mock_db, mock_repository
    ):
        """Test listing open disputes for admin delegates to repository"""
        mock_disputes = [Mock(spec=Dispute), Mock(spec=Dispute)]
        
        mock_repository.list_open_for_admin.return_value = mock_disputes
        
        result = dispute_service.list_open_for_admin()
        
        assert result == mock_disputes
        mock_repository.list_open_for_admin.assert_called_once_with(mock_db)

    def test_set_status_successful_transition_open_to_in_review(
        self, dispute_service, mock_db, mock_repository, sample_dispute
    ):
        """Test successful status transition from OPEN to IN_REVIEW"""
        sample_dispute.status = DisputeStatus.OPEN
        new_status = DisputeStatus.IN_REVIEW
        
        mock_updated_dispute = Mock(spec=Dispute)
        
        mock_repository.get_by_id.return_value = sample_dispute
        mock_repository.update_status.return_value = mock_updated_dispute
        
        result = dispute_service.set_status(
            sample_dispute.id,
            new_status=new_status,
            resolution_notes="Review started"
        )
        
        assert result == mock_updated_dispute
        mock_repository.update_status.assert_called_once_with(
            mock_db,
            sample_dispute.id,
            new_status,
            resolution_notes="Review started",
            resolved_at=None,
        )

    def test_set_status_successful_transition_in_review_to_needs_info(
        self, dispute_service, mock_db, mock_repository, sample_dispute
    ):
        """Test successful status transition from IN_REVIEW to NEEDS_INFO"""
        sample_dispute.status = DisputeStatus.IN_REVIEW
        new_status = DisputeStatus.NEEDS_INFO
        
        mock_updated_dispute = Mock(spec=Dispute)
        
        mock_repository.get_by_id.return_value = sample_dispute
        mock_repository.update_status.return_value = mock_updated_dispute
        
        result = dispute_service.set_status(sample_dispute.id, new_status=new_status)
        
        assert result == mock_updated_dispute

    def test_set_status_successful_transition_needs_info_to_in_review(
        self, dispute_service, mock_db, mock_repository, sample_dispute
    ):
        """Test successful status transition from NEEDS_INFO to IN_REVIEW"""
        sample_dispute.status = DisputeStatus.NEEDS_INFO
        new_status = DisputeStatus.IN_REVIEW
        
        mock_updated_dispute = Mock(spec=Dispute)
        
        mock_repository.get_by_id.return_value = sample_dispute
        mock_repository.update_status.return_value = mock_updated_dispute
        
        result = dispute_service.set_status(sample_dispute.id, new_status=new_status)
        
        assert result == mock_updated_dispute

    def test_set_status_raises_error_for_invalid_transition(
        self, dispute_service, mock_db, mock_repository, sample_dispute
    ):
        """Test error for invalid status transition"""
        sample_dispute.status = DisputeStatus.OPEN
        new_status = DisputeStatus.NEEDS_INFO  # Invalid direct transition
        
        mock_repository.get_by_id.return_value = sample_dispute
        
        with pytest.raises(ValueError, match="Invalid dispute status transition"):
            dispute_service.set_status(sample_dispute.id, new_status=new_status)
        
        mock_repository.update_status.assert_not_called()

    def test_set_status_raises_error_when_dispute_not_found(
        self, dispute_service, mock_db, mock_repository
    ):
        """Test error when dispute doesn't exist"""
        dispute_id = uuid4()
        
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Dispute not found"):
            dispute_service.set_status(dispute_id, new_status=DisputeStatus.IN_REVIEW)

    def test_resolve_dispute_refund_success(
        self, dispute_service, mock_db, mock_repository, mock_bookings_public,
        mock_payments_public, mock_notifications_public, sample_dispute
    ):
        """Test successful dispute resolution with refund"""
        sample_dispute.status = DisputeStatus.IN_REVIEW
        sample_booking = Mock()
        sample_booking.id = sample_dispute.booking_id
        
        payload = DisputeResolution(
            decision="refund",
            refund_amount=100.00,
            resolution_notes="Full refund granted"
        )
        
        mock_updated_dispute = Mock(spec=Dispute)
        
        mock_repository.get_by_id.return_value = sample_dispute
        mock_bookings_public.get_booking.return_value = sample_booking
        mock_repository.update_status.return_value = mock_updated_dispute
        
        result = dispute_service.resolve_dispute(sample_dispute.id, payload)
        
        assert result == mock_updated_dispute
        mock_payments_public.refund_for_booking.assert_called_once_with(
            booking_id=sample_booking.id,
            reason="dispute_resolution",
        )
        mock_repository.update_status.assert_called_once()
        call_args = mock_repository.update_status.call_args
        assert call_args[0][2] == DisputeStatus.RESOLVED_REFUNDED
        mock_notifications_public.dispute_resolved.assert_called_once()

    def test_resolve_dispute_refund_raises_error_for_invalid_amount(
        self, dispute_service, mock_repository, mock_bookings_public, sample_dispute
    ):
        """Test error when refund amount is invalid"""
        sample_dispute.status = DisputeStatus.IN_REVIEW
        sample_booking = Mock()
        sample_booking.id = sample_dispute.booking_id
        
        payload = DisputeResolution(
            decision="refund",
            refund_amount=0,  # Invalid amount
            resolution_notes="No refund"
        )
        
        mock_repository.get_by_id.return_value = sample_dispute
        mock_bookings_public.get_booking.return_value = sample_booking
        
        with pytest.raises(ValueError, match="refund_amount must be > 0 for refund decisions"):
            dispute_service.resolve_dispute(sample_dispute.id, payload)

    def test_resolve_dispute_deny_success(
        self, dispute_service, mock_db, mock_repository, mock_bookings_public,
        mock_payments_public, mock_notifications_public, sample_dispute
    ):
        """Test successful dispute resolution with deny"""
        sample_dispute.status = DisputeStatus.IN_REVIEW
        sample_booking = Mock()
        sample_booking.id = sample_dispute.booking_id
        
        payload = DisputeResolution(
            decision="deny",
            refund_amount=None,
            resolution_notes="Dispute denied"
        )
        
        mock_updated_dispute = Mock(spec=Dispute)
        
        mock_repository.get_by_id.return_value = sample_dispute
        mock_bookings_public.get_booking.return_value = sample_booking
        mock_repository.update_status.return_value = mock_updated_dispute
        
        result = dispute_service.resolve_dispute(sample_dispute.id, payload)
        
        assert result == mock_updated_dispute
        mock_payments_public.refund_for_booking.assert_not_called()
        mock_repository.update_status.assert_called_once()
        call_args = mock_repository.update_status.call_args
        assert call_args[0][2] == DisputeStatus.RESOLVED_DENIED
        mock_notifications_public.dispute_resolved.assert_called_once()

    def test_resolve_dispute_raises_error_for_invalid_status(
        self, dispute_service, mock_repository, mock_bookings_public, mock_payments_public, sample_dispute
    ):
        """Test error when dispute is not in valid status for resolution"""
        sample_dispute.status = DisputeStatus.CLOSED  # Invalid status for resolution
        
        payload = DisputeResolution(
            decision="refund",
            refund_amount=100.00,
            resolution_notes="Test"
        )
        
        mock_repository.get_by_id.return_value = sample_dispute
        sample_booking = Mock()
        sample_booking.id = sample_dispute.booking_id
        mock_bookings_public.get_booking.return_value = sample_booking
        
        with pytest.raises(ValueError, match="Dispute must be in-review or needs-info to be resolved"):
            dispute_service.resolve_dispute(sample_dispute.id, payload)
        mock_payments_public.refund_for_booking.assert_not_called()

    def test_resolve_dispute_raises_error_for_unsupported_decision(
        self, dispute_service, mock_repository, mock_bookings_public, mock_payments_public, sample_dispute
    ):
        """Test error for unsupported decision type"""
        sample_dispute.status = DisputeStatus.IN_REVIEW
        
        # Use model_construct() to bypass Pydantic validation (for testing only)
        payload = DisputeResolution.model_construct(
            decision="invalid_decision",  # Unsupported decision
            refund_amount=None,
            resolution_notes="Test"
        )
        
        mock_repository.get_by_id.return_value = sample_dispute
        sample_booking = Mock()
        sample_booking.id = sample_dispute.booking_id
        mock_bookings_public.get_booking.return_value = sample_booking
        
        with pytest.raises(ValueError, match="Unsupported decision type"):
            dispute_service.resolve_dispute(sample_dispute.id, payload)
        mock_payments_public.refund_for_booking.assert_not_called()

    def test_close_dispute_success_for_refunded(
        self, dispute_service, mock_db, mock_repository, sample_dispute
    ):
        """Test successful closing of refunded dispute"""
        sample_dispute.status = DisputeStatus.RESOLVED_REFUNDED
        
        mock_updated_dispute = Mock(spec=Dispute)
        
        mock_repository.get_by_id.return_value = sample_dispute
        mock_repository.update_status.return_value = mock_updated_dispute
        
        result = dispute_service.close_dispute(sample_dispute.id)
        
        assert result == mock_updated_dispute
        mock_repository.update_status.assert_called_once_with(
            mock_db,
            sample_dispute.id,
            DisputeStatus.CLOSED,
            resolution_notes=sample_dispute.resolution_notes,
            resolved_at=sample_dispute.resolved_at,
        )

    def test_close_dispute_success_for_denied(
        self, dispute_service, mock_db, mock_repository, sample_dispute
    ):
        """Test successful closing of denied dispute"""
        sample_dispute.status = DisputeStatus.RESOLVED_DENIED
        
        mock_updated_dispute = Mock(spec=Dispute)
        
        mock_repository.get_by_id.return_value = sample_dispute
        mock_repository.update_status.return_value = mock_updated_dispute
        
        result = dispute_service.close_dispute(sample_dispute.id)
        
        assert result == mock_updated_dispute

    def test_close_dispute_raises_error_for_non_resolved_status(
        self, dispute_service, mock_db, mock_repository, sample_dispute
    ):
        """Test error when trying to close non-resolved dispute"""
        sample_dispute.status = DisputeStatus.IN_REVIEW
        
        mock_repository.get_by_id.return_value = sample_dispute
        
        with pytest.raises(ValueError, match="Only resolved disputes can be closed"):
            dispute_service.close_dispute(sample_dispute.id)
        
        mock_repository.update_status.assert_not_called()

    def test_list_all_for_admin_delegates_to_repository(
        self, dispute_service, mock_db, mock_repository
    ):
        """Test listing all disputes for admin delegates to repository"""
        mock_disputes = [Mock(spec=Dispute), Mock(spec=Dispute), Mock(spec=Dispute)]
        
        mock_repository.list_all_for_admin.return_value = mock_disputes
        
        result = dispute_service.list_all_for_admin()
        
        assert result == mock_disputes
        mock_repository.list_all_for_admin.assert_called_once_with(mock_db)

    def test_list_all_for_admin_returns_empty_list_when_none_exist(
        self, dispute_service, mock_db, mock_repository
    ):
        """Test listing all disputes for admin returns empty list when none exist"""
        mock_repository.list_all_for_admin.return_value = []
        
        result = dispute_service.list_all_for_admin()
        
        assert result == []
        mock_repository.list_all_for_admin.assert_called_once_with(mock_db)