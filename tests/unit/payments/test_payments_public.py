import pytest
from unittest.mock import Mock
from uuid import uuid4
from decimal import Decimal

from app.payments.public import PaymentsPublicImpl
from app.payments.models import Payment


def test_payments_public_implements_protocol():
    """Test that PaymentsPublicImpl properly implements the PaymentsPublic protocol"""
    mock_service = Mock()
    public_impl = PaymentsPublicImpl(mock_service)
    
    assert hasattr(public_impl, 'escrow_for_booking')
    assert hasattr(public_impl, 'capture_for_booking')
    assert hasattr(public_impl, 'refund_for_booking')
    assert hasattr(public_impl, 'list_for_booking')
    assert hasattr(public_impl, 'void_escrow_for_booking')
    assert hasattr(public_impl, 'get_payments_for_bookings')
    
    assert callable(public_impl.escrow_for_booking)
    assert callable(public_impl.capture_for_booking)
    assert callable(public_impl.refund_for_booking)
    assert callable(public_impl.list_for_booking)
    assert callable(public_impl.void_escrow_for_booking)
    assert callable(public_impl.get_payments_for_bookings)

def test_payments_public_delegates_to_service():
    """Test that all public methods correctly delegate to the service layer"""
    mock_service = Mock()
    public_impl = PaymentsPublicImpl(mock_service)
    
    mock_booking = Mock()
    mock_booking.id = uuid4()
    amount = Decimal("100.00")
    currency = "USD"
    mock_payment = Mock(spec=Payment)
    
    mock_service.create_escrow.return_value = mock_payment
    result = public_impl.escrow_for_booking(mock_booking, amount, currency)
    assert result == mock_payment
    mock_service.create_escrow.assert_called_once_with(
        booking=mock_booking,
        amount=amount,
        currency=currency
    )
    
    mock_service.reset_mock()
    
    mock_service.capture.return_value = mock_payment
    result = public_impl.capture_for_booking(mock_booking)
    assert result == mock_payment
    mock_service.capture.assert_called_once_with(booking=mock_booking)
    
    mock_service.reset_mock()

    reason = "Customer requested refund"
    mock_service.refund.return_value = mock_payment
    result = public_impl.refund_for_booking(mock_booking.id, reason)
    assert result == mock_payment
    mock_service.refund.assert_called_once_with(booking_id=mock_booking.id, reason=reason)
    
    mock_service.reset_mock()
    mock_booking.id = uuid4()
    
    mock_service.refund.return_value = mock_payment
    result = public_impl.refund_for_booking(mock_booking.id)
    assert result == mock_payment
    mock_service.refund.assert_called_once_with(booking_id=mock_booking.id, reason=None)
    
    mock_service.reset_mock()
    booking_id = uuid4()
    mock_payments = [Mock(spec=Payment), Mock(spec=Payment)]
    
    mock_service.list_for_booking.return_value = mock_payments
    result = public_impl.list_for_booking(booking_id)
    assert result == mock_payments
    mock_service.list_for_booking.assert_called_once_with(booking_id)
    
    mock_service.reset_mock()
    
    mock_service.void_escrow.return_value = mock_payment
    result = public_impl.void_escrow_for_booking(mock_booking)
    assert result == mock_payment
    mock_service.void_escrow.assert_called_once_with(booking=mock_booking)
    
    mock_service.reset_mock()
    
    booking_ids = [uuid4(), uuid4()]
    mock_payments_list = [Mock(spec=Payment), Mock(spec=Payment), Mock(spec=Payment)]
    
    mock_service.get_payments_for_bookings.return_value = mock_payments_list
    result = public_impl.get_payments_for_bookings(booking_ids)
    assert result == mock_payments_list
    mock_service.get_payments_for_bookings.assert_called_once_with(booking_ids)