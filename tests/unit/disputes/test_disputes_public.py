import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.disputes.public import DisputesPublicImpl
from app.disputes.models import DisputeStatus
from app.disputes.schemas import DisputeCreate, DisputeResolution


def test_disputes_public_implements_protocol():
    """Test that DisputesPublicImpl properly implements the DisputesPublic protocol"""
    mock_service = Mock()
    public_impl = DisputesPublicImpl(mock_service)
    
    assert hasattr(public_impl, 'open_dispute')
    assert hasattr(public_impl, 'list_disputes_for_user')
    assert hasattr(public_impl, 'list_disputes_for_booking')
    assert hasattr(public_impl, 'list_open_for_admin')
    assert hasattr(public_impl, 'set_status')
    assert hasattr(public_impl, 'resolve_dispute')
    assert hasattr(public_impl, 'close_dispute')
    assert hasattr(public_impl, 'list_all_for_admin')
    
    assert callable(public_impl.open_dispute)
    assert callable(public_impl.list_disputes_for_user)
    assert callable(public_impl.list_disputes_for_booking)
    assert callable(public_impl.list_open_for_admin)
    assert callable(public_impl.set_status)
    assert callable(public_impl.resolve_dispute)
    assert callable(public_impl.close_dispute)
    assert callable(public_impl.list_all_for_admin)

def test_disputes_public_delegates_to_service():
    """Test that all public methods correctly delegate to the service layer"""
    mock_service = Mock()
    public_impl = DisputesPublicImpl(mock_service)
    
    user_id = uuid4()
    booking_id = uuid4()
    dispute_id = uuid4()
    mock_dispute = Mock()
    mock_disputes_list = [Mock(), Mock()]
    mock_dispute_create = Mock(spec=DisputeCreate)
    mock_dispute_resolution = Mock(spec=DisputeResolution)
    
    mock_service.open_dispute.return_value = mock_dispute
    result = public_impl.open_dispute(user_id, mock_dispute_create)
    assert result == mock_dispute
    mock_service.open_dispute.assert_called_once_with(user_id, mock_dispute_create)
    
    mock_service.reset_mock()
    
    mock_service.list_disputes_for_user.return_value = mock_disputes_list
    result = public_impl.list_disputes_for_user(user_id)
    assert result == mock_disputes_list
    mock_service.list_disputes_for_user.assert_called_once_with(user_id)
    
    mock_service.reset_mock()
    
    mock_service.list_disputes_for_booking.return_value = mock_disputes_list
    result = public_impl.list_disputes_for_booking(booking_id)
    assert result == mock_disputes_list
    mock_service.list_disputes_for_booking.assert_called_once_with(booking_id)
    
    mock_service.reset_mock()
    
    mock_service.list_open_for_admin.return_value = mock_disputes_list
    result = public_impl.list_open_for_admin()
    assert result == mock_disputes_list
    mock_service.list_open_for_admin.assert_called_once()
    
    mock_service.reset_mock()
    
    mock_service.set_status.return_value = mock_dispute
    new_status = DisputeStatus.RESOLVED_REFUNDED
    resolution_notes = "Issue resolved"
    result = public_impl.set_status(dispute_id, new_status=new_status, resolution_notes=resolution_notes)
    assert result == mock_dispute
    mock_service.set_status.assert_called_once_with(
        dispute_id,
        new_status=new_status,
        resolution_notes=resolution_notes
    )
    
    mock_service.reset_mock()
    
    mock_service.resolve_dispute.return_value = mock_dispute
    result = public_impl.resolve_dispute(dispute_id, mock_dispute_resolution)
    assert result == mock_dispute
    mock_service.resolve_dispute.assert_called_once_with(dispute_id, mock_dispute_resolution)
    
    mock_service.reset_mock()
    
    mock_service.close_dispute.return_value = mock_dispute
    result = public_impl.close_dispute(dispute_id)
    assert result == mock_dispute
    mock_service.close_dispute.assert_called_once_with(dispute_id)

    mock_service.reset_mock()

    mock_service.list_all_for_admin.return_value = mock_disputes_list
    result = public_impl.list_all_for_admin()
    assert result == mock_disputes_list
    mock_service.list_all_for_admin.assert_called_once_with()