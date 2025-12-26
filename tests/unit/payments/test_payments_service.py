import pytest
from unittest.mock import Mock, MagicMock 
from uuid import uuid4
from decimal import Decimal

from app.payments.service import PaymentsService
from app.payments.repository import PaymentsRepository
from app.payments.ports.payment_port import PaymentPort
from app.payments.models import Payment, PaymentType, PaymentStatus
from app.providers.public import ProvidersPublic
from app.notifications.public import NotificationsPublic


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def mock_repository():
    """Mock PaymentsRepository fixture"""
    return Mock(spec=PaymentsRepository)

@pytest.fixture
def mock_port():
    """Mock PaymentPort fixture"""
    return Mock(spec=PaymentPort)

@pytest.fixture
def mock_providers_public():
    """Mock ProvidersPublic fixture"""
    return Mock(spec=ProvidersPublic)

@pytest.fixture
def mock_notifications_public():
    """Mock NotificationsPublic fixture"""
    return Mock(spec=NotificationsPublic)

@pytest.fixture
def payments_service(mock_db, mock_repository, mock_port, mock_providers_public, mock_notifications_public):
    """PaymentsService fixture with all dependencies"""
    return PaymentsService(
        db=mock_db,
        repo=mock_repository,
        port=mock_port,
        providers_public=mock_providers_public,
        notifications_public=mock_notifications_public
    )

@pytest.fixture
def sample_booking():
    """Fixture for a mock booking object"""
    booking = Mock()
    booking.id = uuid4()
    booking.buyer = Mock()
    return booking

@pytest.fixture
def sample_escrow_payment():
    """Fixture for a mock escrow payment object"""
    payment = Mock(spec=Payment)
    payment.id = uuid4()
    payment.booking_id = uuid4()
    payment.type = PaymentType.ESCROW
    payment.processor_ref = "pi_123456789"
    payment.amount = Decimal("100.00")
    payment.currency = "USD"
    payment.status = PaymentStatus.AUTHORIZED
    return payment

@pytest.fixture
def sample_refund_payment():
    """Fixture for a mock refund payment object"""
    payment = Mock(spec=Payment)
    payment.id = uuid4()
    payment.booking_id = uuid4()
    payment.type = PaymentType.REFUND
    payment.processor_ref = "re_123456789"
    payment.amount = Decimal("100.00")
    payment.currency = "USD"
    payment.status = PaymentStatus.REFUNDED
    return payment

@pytest.fixture
def sample_payment_intent_response():
    """Fixture for Stripe PaymentIntent response"""
    return {
        "client_secret": "pi_123_secret_abc",
        "payment_intent_id": "pi_123456789",
        "amount": Decimal("100.00"),
        "currency": "USD"
    }

class TestPaymentsService:
    
    def test_create_escrow_successfully_creates_authorization_hold(
        self, payments_service, mock_db, mock_port, mock_repository, sample_booking, sample_escrow_payment
    ):
        """Test successful escrow creation with external payment processor"""
        processor_ref = "re_123456789"
        mock_payment = sample_escrow_payment
        amount = Decimal("100.00")
        currency = "USD"

        mock_port.create_hold.return_value = processor_ref
        mock_repository.create_payment.return_value = mock_payment

        result = payments_service.create_escrow(sample_booking, amount, currency)

        mock_port.create_hold.assert_called_once_with(amount=amount, currency=currency, reference=str(sample_booking.id))
        assert result.type == PaymentType.ESCROW
        assert result.status == PaymentStatus.AUTHORIZED
        mock_repository.create_payment.assert_called_once()
        assert result == mock_payment

    def test_create_escrow_handles_external_api_failure_gracefully(
        self, payments_service, mock_repository, mock_port, sample_booking
    ):
        """Test escrow creation fails when payment processor API fails"""
        amount = Decimal("100.00")
        currency = "USD"

        mock_port.create_hold.side_effect = ValueError("Could not create a payment hold.")

        with pytest.raises(ValueError, match="Could not create a payment hold."):
            payments_service.create_escrow(sample_booking, amount, currency)

        mock_repository.create_payment.assert_not_called()

    def test_capture_successfully_captures_authorized_escrow(
        self, payments_service, mock_db, mock_repository, mock_port, mock_notifications_public, sample_booking, sample_escrow_payment
    ):
        """Test successful capture of authorized escrow payment"""
        mock_escrow = sample_escrow_payment
        mock_escrow.status = PaymentStatus.AUTHORIZED
        mock_updated_payment = Mock(spec=Payment)
        mock_updated_payment.status = PaymentStatus.CAPTURED
        
        mock_repository.get_latest_escrow.return_value = mock_escrow
        mock_repository.update_payment.return_value = mock_updated_payment
        
        result = payments_service.capture(sample_booking)
        
        mock_repository.get_latest_escrow.assert_called_once_with(mock_db, sample_booking.id)
        mock_port.capture.assert_called_once_with(processor_ref=mock_escrow.processor_ref)
        mock_repository.update_payment.assert_called_once_with(mock_db, mock_escrow)
        mock_notifications_public.payment_captured.assert_called_once_with(sample_booking.buyer, mock_updated_payment)
        assert result == mock_updated_payment

    def test_capture_raises_error_when_no_escrow_found(
        self, payments_service, mock_port, mock_repository, sample_booking
    ):
        """Test capture fails when no escrow exists for booking"""
        mock_repository.get_latest_escrow.return_value = None

        with pytest.raises(ValueError, match="No escrow found to capture."):
            payments_service.capture(sample_booking)

        mock_port.capture.assert_not_called()

    def test_capture_raises_error_when_escrow_not_authorized(
        self, payments_service, mock_port, mock_repository, sample_booking, sample_escrow_payment
    ):
        """Test capture fails when escrow is not in AUTHORIZED state"""
        mock_escrow = sample_escrow_payment
        mock_escrow.status = PaymentStatus.REFUNDED

        mock_repository.get_latest_escrow.return_value = mock_escrow

        with pytest.raises(ValueError, match="Escrow already captured or refunded."):
            payments_service.capture(sample_booking)

        mock_port.capture.assert_not_called()

    def test_capture_handles_external_capture_failure(
        self, payments_service, mock_db, mock_repository, mock_port, sample_booking, sample_escrow_payment
    ):
        """Test capture fails when payment processor capture fails"""
        mock_repository.get_latest_escrow.return_value = sample_escrow_payment
        mock_port.capture.side_effect = ValueError("Could not capture payment.")

        with pytest.raises(ValueError, match="Could not capture payment."):
            payments_service.capture(sample_booking)

        mock_repository.update_payment.assert_not_called()

    def test_void_escrow_successfully_cancels_authorized_payment(
        self, payments_service, mock_db, mock_repository, mock_port, sample_booking, sample_escrow_payment
    ):
        """Test successful void of authorized escrow payment"""
        mock_repository.get_latest_escrow.return_value = sample_escrow_payment
        mock_port.cancel_payment_intent.return_value = None

        mock_repository.update_payment.return_value = sample_escrow_payment
        result = payments_service.void_escrow(sample_booking)

        mock_repository.get_latest_escrow.assert_called_once_with(mock_db, sample_booking.id)
        mock_port.cancel_payment_intent.assert_called_once_with(processor_ref=sample_escrow_payment.processor_ref)
        assert result.status == PaymentStatus.CANCELLED
        mock_repository.update_payment.assert_called_once_with(mock_db, sample_escrow_payment)
        assert result == sample_escrow_payment

    def test_void_escrow_raises_error_when_no_escrow_found(
        self, payments_service, mock_port, mock_repository, sample_booking
    ):
        """Test void fails when no escrow exists for booking"""
        mock_repository.get_latest_escrow.return_value = None

        with pytest.raises(ValueError, match="No escrow found to void."):
            payments_service.void_escrow(sample_booking)  

        mock_port.cancel_payment_intent.assert_not_called()      

    def test_void_escrow_raises_error_when_escrow_not_authorized(
        self, payments_service, mock_repository, sample_booking, sample_escrow_payment, mock_port
    ):
        """Test void fails when escrow is not in AUTHORIZED state"""
        sample_escrow_payment.status = PaymentStatus.CAPTURED

        mock_repository.get_latest_escrow.return_value = sample_escrow_payment

        with pytest.raises(ValueError, match=f"Cannot void escrow in status: {sample_escrow_payment.status}. Only AUTHORIZED payments can be voided."):
            payments_service.void_escrow(sample_booking)  

        mock_port.cancel_payment_intent.assert_not_called()    

    def test_refund_raises_error_when_no_captured_payment(
        self, payments_service, mock_port, mock_repository, sample_booking
    ):
        """Test refund fails when no captured payment exists"""
        mock_repository.get_captured_escrow_payment.return_value = None

        with pytest.raises(ValueError, match="No captured payment found to refund."):
            payments_service.refund(sample_booking.id)

        mock_port.refund.assert_not_called()

    def test_refund_handles_external_refund_failure(
        self, payments_service, mock_repository, mock_port, sample_booking, sample_escrow_payment
    ):
        """Test refund fails when payment processor refund fails"""
        sample_escrow_payment.status = PaymentStatus.CAPTURED
        mock_repository.get_captured_escrow_payment.return_value = sample_escrow_payment
        mock_port.refund.side_effect = ValueError("Unable to process refund with Stripe.")

        with pytest.raises(ValueError, match="Unable to process refund with Stripe."):
            payments_service.refund(sample_booking.id)
        
        mock_repository.create_payment.assert_not_called()

    def test_list_for_booking_delegates_to_repository(
        self, payments_service, mock_db, mock_repository, sample_booking
    ):
        """Test payment listing for booking delegates to repository"""
        booking_id = sample_booking.id
        mock_payments = [Mock(spec=Payment), Mock(spec=Payment)]

        mock_repository.list_payments_for_booking.return_value = mock_payments

        result = payments_service.list_for_booking(booking_id)
        mock_repository.list_payments_for_booking.assert_called_once_with(mock_db, booking_id)
        assert result == mock_payments

    def test_list_for_booking_returns_empty_list_when_no_payments(
        self, payments_service, mock_repository, sample_booking
    ):
        """Test payment listing returns empty list when no payments exist"""
        mock_repository.list_payments_for_booking.return_value = []
        result = payments_service.list_for_booking(sample_booking.id)

        assert result == []

    def test_get_payments_for_bookings_delegates_to_repository(
        self, payments_service, mock_db, mock_repository
    ):
        """Test getting payments for multiple bookings delegates to repository"""
        booking_ids = [uuid4(), uuid4()]
        mock_payments = [Mock(spec=Payment), Mock(spec=Payment)]

        mock_repository.list_payments_for_bookings.return_value = mock_payments
        result = payments_service.get_payments_for_bookings(booking_ids)    
        mock_repository.list_payments_for_bookings.assert_called_once_with(mock_db, booking_ids)
        assert result == mock_payments

    def test_get_payments_for_bookings_handles_empty_booking_ids(
        self, payments_service, mock_db, mock_repository
    ):
        """Test getting payments for empty booking_ids list"""
        empty_list = []
        mock_repository.list_payments_for_bookings.return_value = []
        result = payments_service.get_payments_for_bookings(empty_list)

        mock_repository.list_payments_for_bookings.assert_called_once_with(mock_db, empty_list)
        assert result == []

    def test_create_payment_intent_successfully_creates_stripe_intent(
        self, payments_service, mock_repository, mock_port, sample_payment_intent_response
    ):
        """Test successful Stripe PaymentIntent creation for frontend"""
        booking_id = uuid4()
        amount = Decimal("100.00")
        currency = "USD"
        
        mock_port.create_payment_intent.return_value = sample_payment_intent_response
        
        mock_payment = Mock(spec=Payment)
        mock_payment.type = PaymentType.ESCROW
        mock_payment.status = PaymentStatus.AUTHORIZED
        mock_repository.create_payment.return_value = mock_payment
        
        result = payments_service.create_payment_intent(booking_id, amount, currency)
        
        mock_port.create_payment_intent.assert_called_once_with(
            amount=amount,
            currency=currency,
            reference=str(booking_id),
            capture_method="manual",
        )
        
        mock_repository.create_payment.assert_called_once()
        call_args = mock_repository.create_payment.call_args
        created_payment = call_args[0][1]
        assert created_payment.type == PaymentType.ESCROW
        assert created_payment.status == PaymentStatus.AUTHORIZED
        
        assert result["client_secret"] == sample_payment_intent_response["client_secret"]
        assert result["payment_intent_id"] == sample_payment_intent_response["payment_intent_id"]
        assert result["amount"] == amount
        assert result["currency"] == currency

    def test_create_payment_intent_handles_stripe_api_failure(
        self, payments_service, sample_booking, mock_port, mock_repository
    ):
        """Test PaymentIntent creation fails when Stripe API fails"""
        amount = Decimal("100.00")
        currency = "USD"
        
        mock_port.create_payment_intent.side_effect = ValueError("Stripe error: couldn't create payment intent")

        with pytest.raises(ValueError, match="Stripe error: couldn't create payment intent"):
            payments_service.create_payment_intent(sample_booking.id, amount, currency)
        
        mock_repository.create_payment.assert_not_called()

    def test_create_payment_intent_uses_correct_amount_conversion(
        self, payments_service, mock_repository, mock_port
    ):
        """Test PaymentIntent amount is correctly handled by port"""
        booking_id = uuid4()
        amount = Decimal("150.75")
        currency = "USD"
        
        captured_kwargs = {}
        def mock_port_create_payment_intent(**kwargs):
            captured_kwargs.update(kwargs)
            return {
                "client_secret": "secret",
                "payment_intent_id": "pi_123",
            }
        
        mock_port.create_payment_intent.side_effect = mock_port_create_payment_intent
        
        mock_payment = Mock(spec=Payment)
        mock_repository.create_payment.return_value = mock_payment
        
        result = payments_service.create_payment_intent(booking_id, amount, currency)
        
        # The port should receive the amount as Decimal, not converted to cents
        assert captured_kwargs["amount"] == amount
        
        call_args = mock_repository.create_payment.call_args
        created_payment = call_args[0][1]
        assert created_payment.amount == amount