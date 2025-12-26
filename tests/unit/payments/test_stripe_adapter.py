import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
import os

from app.payments.ports.stripe_adapter import RealStripeAdapter, MockStripeAdapter, get_payment_adapter
import stripe


@pytest.fixture
def real_stripe_adapter():
    """RealStripeAdapter fixture with patched environment variable"""
    with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_123"}):
        return RealStripeAdapter()

@pytest.fixture
def mock_stripe_adapter():
    """MockStripeAdapter fixture"""
    return MockStripeAdapter()

class TestRealStripeAdapter:
    
    def test_init_raises_error_when_stripe_key_missing(self):
        """Test adapter initialization fails without Stripe secret key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="STRIPE_SECRET_KEY environment variable is required"):
                RealStripeAdapter()

    def test_create_hold_delegates_to_create_payment_intent(self, real_stripe_adapter):
        """Test create_hold calls create_payment_intent with correct parameters"""
        with patch.object(real_stripe_adapter, 'create_payment_intent') as mock_create_intent:
            mock_create_intent.return_value = {"payment_intent_id": "pi_123"}
            
            result = real_stripe_adapter.create_hold(
                amount=Decimal("100.00"),
                currency="USD",
                reference="booking_123"
            )
            
            mock_create_intent.assert_called_once_with(
                amount=Decimal("100.00"),
                currency="USD",
                reference="booking_123",
                capture_method="manual"
            )
            assert result == "pi_123"

    def test_create_payment_intent_successfully_creates_stripe_intent(self, real_stripe_adapter):
        """Test successful PaymentIntent creation through Stripe API"""
        mock_intent = Mock()
        mock_intent.id = "pi_123456789"
        mock_intent.client_secret = "cs_secret_123"
        mock_intent.status = "requires_payment_method"
        
        with patch.object(stripe.PaymentIntent, 'create', return_value=mock_intent):
            result = real_stripe_adapter.create_payment_intent(
                amount=Decimal("100.50"),
                currency="USD",
                reference="booking_123",
                capture_method="manual"
            )
            
            stripe.PaymentIntent.create.assert_called_once_with(
                amount=10050,
                currency="usd",
                capture_method="manual",
                metadata={"booking_id": "booking_123"},
                payment_method_types=["card"]
            )
            assert result["payment_intent_id"] == "pi_123456789"
            assert result["client_secret"] == "cs_secret_123"
            assert result["amount"] == Decimal("100.50")

    def test_create_payment_intent_handles_stripe_error(self, real_stripe_adapter):
        """Test PaymentIntent creation raises error when Stripe API fails"""
        stripe_error = stripe.error.StripeError("API error")
        
        with patch.object(stripe.PaymentIntent, 'create', side_effect=stripe_error):
            with pytest.raises(ValueError, match="Stripe error: API error"):
                real_stripe_adapter.create_payment_intent(
                    amount=Decimal("100.00"),
                    currency="USD",
                    reference="booking_123"
                )

    def test_confirm_payment_intent_retrieves_intent_status(self, real_stripe_adapter):
        """Test payment intent confirmation retrieves intent from Stripe"""
        mock_intent = Mock()
        mock_intent.status = "succeeded"
        mock_intent.id = "pi_123"
        
        with patch.object(stripe.PaymentIntent, 'retrieve', return_value=mock_intent):
            result = real_stripe_adapter.confirm_payment_intent(
                payment_intent_id="pi_123"
            )
            
            stripe.PaymentIntent.retrieve.assert_called_once_with("pi_123")
            assert result["status"] == "succeeded"
            assert result["payment_intent_id"] == "pi_123"

    def test_confirm_payment_intent_handles_stripe_error(self, real_stripe_adapter):
        """Test confirmation raises error when Stripe API fails"""
        stripe_error = stripe.error.StripeError("Retrieval error")
        
        with patch.object(stripe.PaymentIntent, 'retrieve', side_effect=stripe_error):
            with pytest.raises(ValueError, match="Stripe confirmation error: Retrieval error"):
                real_stripe_adapter.confirm_payment_intent(
                    payment_intent_id="pi_123"
                )

    def test_get_payment_intent_returns_intent_when_exists(self, real_stripe_adapter):
        """Test successful retrieval of existing payment intent"""
        mock_intent = Mock()
        mock_intent.id = "pi_123"
        mock_intent.status = "succeeded"
        mock_intent.amount = 10000
        mock_intent.currency = "usd"
        mock_intent.client_secret = "cs_secret_123"
        mock_intent.capture_method = "manual"
        
        with patch.object(stripe.PaymentIntent, 'retrieve', return_value=mock_intent):
            result = real_stripe_adapter.get_payment_intent(
                payment_intent_id="pi_123"
            )
            
            assert result["id"] == "pi_123"
            assert result["status"] == "succeeded"
            assert result["amount"] == Decimal("100.00")
            assert result["currency"] == "usd"

    def test_get_payment_intent_returns_none_when_not_found(self, real_stripe_adapter):
        """Test retrieval returns None when payment intent doesn't exist"""
        stripe_error = stripe.error.StripeError("Not found")
        
        with patch.object(stripe.PaymentIntent, 'retrieve', side_effect=stripe_error):
            result = real_stripe_adapter.get_payment_intent(
                payment_intent_id="pi_nonexistent"
            )
            
            assert result is None

    def test_capture_successfully_captures_payment(self, real_stripe_adapter):
        """Test successful payment capture through Stripe API"""
        with patch.object(stripe.PaymentIntent, 'capture') as mock_capture:
            real_stripe_adapter.capture(processor_ref="pi_123")
            
            mock_capture.assert_called_once_with("pi_123")

    def test_capture_handles_stripe_error(self, real_stripe_adapter):
        """Test capture raises error when Stripe API fails"""
        stripe_error = stripe.error.StripeError("Capture failed")
        
        with patch.object(stripe.PaymentIntent, 'capture', side_effect=stripe_error):
            with pytest.raises(ValueError, match="Stripe capture error: Capture failed"):
                real_stripe_adapter.capture(processor_ref="pi_123")

    def test_cancel_payment_intent_successfully_cancels_payment(self, real_stripe_adapter):
        """Test successful payment intent cancellation"""
        with patch.object(stripe.PaymentIntent, 'cancel') as mock_cancel:
            real_stripe_adapter.cancel_payment_intent(processor_ref="pi_123")
            
            mock_cancel.assert_called_once_with("pi_123")

    def test_cancel_payment_intent_handles_stripe_error(self, real_stripe_adapter):
        """Test cancellation raises error when Stripe API fails"""
        stripe_error = stripe.error.StripeError("Cancel failed")
        
        with patch.object(stripe.PaymentIntent, 'cancel', side_effect=stripe_error):
            with pytest.raises(ValueError, match="Stripe cancel error: Cancel failed"):
                real_stripe_adapter.cancel_payment_intent(processor_ref="pi_123")

    def test_refund_successfully_creates_refund(self, real_stripe_adapter):
        """Test successful refund creation through Stripe API"""
        with patch.object(stripe.Refund, 'create') as mock_refund_create:
            real_stripe_adapter.refund(
                processor_ref="pi_123",
                amount=Decimal("75.50")
            )
            
            mock_refund_create.assert_called_once_with(
                payment_intent="pi_123",
                amount=7550
            )

    def test_refund_handles_stripe_error(self, real_stripe_adapter):
        """Test refund raises error when Stripe API fails"""
        stripe_error = stripe.error.StripeError("Refund failed")
        
        with patch.object(stripe.Refund, 'create', side_effect=stripe_error):
            with pytest.raises(ValueError, match="Stripe refund error: Refund failed"):
                real_stripe_adapter.refund(
                    processor_ref="pi_123",
                    amount=Decimal("75.50")
                )

class TestMockStripeAdapter:
    
    def test_create_hold_returns_mock_payment_intent_id(self, mock_stripe_adapter):
        """Test mock create_hold returns valid payment intent ID"""
        result = mock_stripe_adapter.create_hold(
            amount=Decimal("100.00"),
            currency="USD",
            reference="booking_123"
        )
        
        assert result.startswith("pi_mock_")
        assert len(result) == len("pi_mock_") + 32

    def test_create_payment_intent_returns_complete_response(self, mock_stripe_adapter):
        """Test mock create_payment_intent returns all required fields"""
        result = mock_stripe_adapter.create_payment_intent(
            amount=Decimal("100.00"),
            currency="USD",
            reference="booking_123"
        )
        
        assert "payment_intent_id" in result
        assert result["payment_intent_id"].startswith("pi_mock_")
        assert "client_secret" in result
        assert result["client_secret"].startswith("cs_mock_")
        assert result["status"] == "requires_payment_method"
        assert result["amount"] == Decimal("100.00")
        assert result["currency"] == "USD"

    def test_confirm_payment_intent_returns_success_status(self, mock_stripe_adapter):
        """Test mock confirmation returns succeeded status"""
        payment_intent_id = "pi_123"
        result = mock_stripe_adapter.confirm_payment_intent(
            payment_intent_id=payment_intent_id
        )
        
        assert result["status"] == "succeeded"
        assert result["payment_intent_id"] == payment_intent_id

    def test_get_payment_intent_returns_mock_data(self, mock_stripe_adapter):
        """Test mock retrieval returns payment intent data"""
        payment_intent_id = "pi_123"
        result = mock_stripe_adapter.get_payment_intent(
            payment_intent_id=payment_intent_id
        )
        
        assert result["id"] == payment_intent_id
        assert result["status"] == "succeeded"
        assert result["amount"] == Decimal("100.00")
        assert result["currency"] == "usd"
        assert "client_secret" in result

    def test_capture_does_not_raise_error(self, mock_stripe_adapter):
        """Test mock capture completes without error"""
        mock_stripe_adapter.capture(processor_ref="pi_123")

    def test_refund_does_not_raise_error(self, mock_stripe_adapter):
        """Test mock refund completes without error"""
        mock_stripe_adapter.refund(
            processor_ref="pi_123",
            amount=Decimal("50.00")
        )

    def test_cancel_payment_intent_does_not_raise_error(self, mock_stripe_adapter):
        """Test mock cancellation completes without error"""
        mock_stripe_adapter.cancel_payment_intent(processor_ref="pi_123")

class TestGetPaymentAdapter:
    
    def test_get_payment_adapter_returns_mock_by_default(self):
        """Test factory returns MockStripeAdapter when USE_REAL_STRIPE not set"""
        with patch.dict(os.environ, {}, clear=True):
            adapter = get_payment_adapter()
            assert isinstance(adapter, MockStripeAdapter)

    def test_get_payment_adapter_returns_mock_when_false(self):
        """Test factory returns MockStripeAdapter when USE_REAL_STRIPE is false"""
        with patch.dict(os.environ, {"USE_REAL_STRIPE": "false"}):
            adapter = get_payment_adapter()
            assert isinstance(adapter, MockStripeAdapter)

    def test_get_payment_adapter_returns_real_when_true(self):
        """Test factory returns RealStripeAdapter when USE_REAL_STRIPE is true"""
        with patch.dict(os.environ, {"USE_REAL_STRIPE": "true", "STRIPE_SECRET_KEY": "sk_test_123"}):
            adapter = get_payment_adapter()
            assert isinstance(adapter, RealStripeAdapter)

    def test_get_payment_adapter_case_insensitive_true_check(self):
        """Test factory handles case-insensitive true value"""
        with patch.dict(os.environ, {"USE_REAL_STRIPE": "True", "STRIPE_SECRET_KEY": "sk_test_123"}):
            adapter = get_payment_adapter()
            assert isinstance(adapter, RealStripeAdapter)