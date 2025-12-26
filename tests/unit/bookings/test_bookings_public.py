import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from app.bookings.public import BookingsPublicImpl


def test_bookings_public_implements_protocol():
    """Test that BookingsPublicImpl properly implements the BookingsPublic protocol"""
    mock_service = Mock()
    public_impl = BookingsPublicImpl(mock_service)
    
    assert hasattr(public_impl, 'get_booking')
    assert hasattr(public_impl, 'is_active')
    assert hasattr(public_impl, 'is_confirmed')
    assert hasattr(public_impl, 'is_requested')
    assert hasattr(public_impl, 'is_cancelled')
    assert hasattr(public_impl, 'is_completed')
    assert hasattr(public_impl, 'is_cancellable')
    assert hasattr(public_impl, 'get_org_bookings_in_period')
    
    assert callable(public_impl.get_booking)
    assert callable(public_impl.is_active)
    assert callable(public_impl.is_confirmed)
    assert callable(public_impl.is_requested)
    assert callable(public_impl.is_cancelled)
    assert callable(public_impl.is_completed)
    assert callable(public_impl.is_cancellable)
    assert callable(public_impl.get_org_bookings_in_period)

def test_bookings_public_delegates_to_service():
    """Test that all public methods correctly delegate to the service layer"""
    mock_service = Mock()
    public_impl = BookingsPublicImpl(mock_service)
    
    booking_id = uuid4()
    mock_booking = Mock()
    mock_booking_result = Mock()
    mock_org_bookings_result = [Mock(), Mock()]
    
    #Test get_booking delegation
    mock_service.get_booking_readonly.return_value = mock_booking_result
    result = public_impl.get_booking(booking_id)
    assert result == mock_booking_result
    mock_service.get_booking_readonly.assert_called_once_with(booking_id)
    
    mock_service.reset_mock()
    
    #Test is_active delegation
    mock_service.BookingStatus.ACTIVE = "active"
    mock_booking.status = "active"
    result = public_impl.is_active(mock_booking)
    assert result == True
    
    mock_booking.status = "confirmed"
    result = public_impl.is_active(mock_booking)
    assert result == False
    
    mock_service.reset_mock()
    
    #Test is_confirmed delegation
    mock_service.BookingStatus.CONFIRMED = "confirmed"
    mock_booking.status = "confirmed"
    result = public_impl.is_confirmed(mock_booking)
    assert result == True
    
    mock_booking.status = "requested"
    result = public_impl.is_confirmed(mock_booking)
    assert result == False
    
    mock_service.reset_mock()
    
    #Test is_requested delegation
    mock_service.BookingStatus.REQUESTED = "requested"
    mock_booking.status = "requested"
    result = public_impl.is_requested(mock_booking)
    assert result == True
    
    mock_booking.status = "confirmed"
    result = public_impl.is_requested(mock_booking)
    assert result == False
    
    mock_service.reset_mock()
    
    #Test is_cancelled delegation
    mock_service.BookingStatus.CANCELLED = "cancelled"
    mock_booking.status = "cancelled"
    result = public_impl.is_cancelled(mock_booking)
    assert result == True
    
    mock_booking.status = "active"
    result = public_impl.is_cancelled(mock_booking)
    assert result == False
    
    mock_service.reset_mock()
    
    #Test is_completed delegation
    mock_service.BookingStatus.COMPLETED = "completed"
    mock_booking.status = "completed"
    result = public_impl.is_completed(mock_booking)
    assert result == True
    
    mock_booking.status = "active"
    result = public_impl.is_completed(mock_booking)
    assert result == False
    
    mock_service.reset_mock()
    
    #Test is_cancellable delegation
    mock_service.BookingStatus.REQUESTED = "requested"
    mock_service.BookingStatus.CONFIRMED = "confirmed"
    mock_service.BookingStatus.ACTIVE = "active"
    
    mock_booking.status = "requested"
    result = public_impl.is_cancellable(mock_booking)
    assert result == True
    
    mock_booking.status = "confirmed"
    result = public_impl.is_cancellable(mock_booking)
    assert result == True
    
    mock_booking.status = "active"
    result = public_impl.is_cancellable(mock_booking)
    assert result == False
    
    mock_service.reset_mock()
    
    #Test get_org_bookings_in_period delegation
    org_id = uuid4()
    period_start = datetime.now(timezone.utc) - timedelta(days=30)
    period_end = datetime.now(timezone.utc)
    
    mock_service.get_org_bookings_in_period.return_value = mock_org_bookings_result
    result = public_impl.get_org_bookings_in_period(org_id, period_start, period_end)
    assert result == mock_org_bookings_result
    mock_service.get_org_bookings_in_period.assert_called_once_with(org_id, period_start, period_end)