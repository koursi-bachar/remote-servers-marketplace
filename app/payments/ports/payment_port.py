from abc import abstractmethod
from decimal import Decimal
from typing import Protocol, Optional, Dict, Any


class PaymentPort(Protocol):
    """
    Complete payment processor interface.
    The PaymentService depends on this abstraction
    """
    
    @abstractmethod
    def create_hold(
        self,
        amount: Decimal,
        currency: str,
        reference: str,
    ) -> str:
        """
        Create an authorization/hold on the user's payment method.
        Returns a processor reference ID (e.g., Stripe PaymentIntent ID).
        """
        ...

    @abstractmethod
    def capture(
        self,
        processor_ref: str,
    ) -> None:
        """
        Capture a previously authorized payment.
        """
        ...

    @abstractmethod
    def cancel_payment_intent(
        self,
        processor_ref: str,
    ) -> None:
        """
        Cancel a PaymentIntent that won't be used.
        """
        ...

    @abstractmethod
    def refund(
        self,
        processor_ref: str,
        amount: Decimal,
    ) -> str:
        """
        Refund a previously captured or authorized payment.
        """
        ...

    @abstractmethod
    def create_checkout_session(
        self,
        booking_id: str,
        user_id: str,
        amount: Decimal,
        currency: str,
        success_url: str,
        cancel_url: str,
        customer_email: str = None,
    ) -> dict:
        """Create Stripe Checkout Session with manual capture"""
        ...

    @abstractmethod
    def retrieve_checkout_session(
        self,
        session_id: str
    ) -> dict:
        """Retrieve Checkout Session details"""
        ...

    @abstractmethod
    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        reference: str,
        capture_method: str = "manual",
    ) -> Dict[str, Any]:
        """
        Create a PaymentIntent for frontend Stripe Elements.
        Returns dict with client_secret and payment_intent_id.
        """
        raise NotImplementedError

    @abstractmethod
    def confirm_payment_intent(
        self,
        payment_intent_id: str,
    ) -> Dict[str, Any]:
        """
        Confirm a PaymentIntent after frontend collection.
        """
        raise NotImplementedError

    @abstractmethod
    def get_payment_intent(
        self,
        payment_intent_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a PaymentIntent status from processor.
        """
        raise NotImplementedError