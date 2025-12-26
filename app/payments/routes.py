from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from .schemas import PaymentRead, CheckoutRequest
from .public import PaymentsPublic, get_payments_public
from app.database import get_db
from app.auth.auth import get_current_user

from .service import PaymentsService, get_payments_service
from decimal import Decimal


router = APIRouter()

#Initialize templates
templates = Jinja2Templates(directory="frontend/templates")

@router.get(
    "/bookings/{booking_id}",
    response_model=list[PaymentRead],
)
def list_payments_for_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    payments_public: PaymentsPublic = Depends(get_payments_public),
    user=Depends(get_current_user),
):
    """
    Get all payments associated with a booking.
    Caller must be either the buyer or the provider (via booking access logic).
    """
    return payments_public.list_for_booking(booking_id)

#Update the create_checkout function
@router.post("/checkout")
def create_checkout(
    checkout_data: CheckoutRequest,
    payments_service: PaymentsService = Depends(get_payments_service),
    user=Depends(get_current_user),
    request: Request = None,
):
    """
    Create Stripe Checkout Session for a booking.
    """
    try:
        base_url = str(request.base_url) if request else "http://localhost:8000"

        success_url = (
            f"{base_url}api/v1/payments/success"
            f"?session_id={{CHECKOUT_SESSION_ID}}"
            f"&booking_id={checkout_data.booking_id}"
            f"&amount={checkout_data.amount}"
            f"&currency={checkout_data.currency}"
        )

        cancel_url = f"{base_url}api/v1/payments/cancel?booking_id={checkout_data.booking_id}"
        
        result = payments_service.create_checkout_session(
            booking_id=str(checkout_data.booking_id),
            user_id=str(user.id),
            amount=Decimal(str(checkout_data.amount)),
            currency=checkout_data.currency,
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user.email if hasattr(user, 'email') else None,
        )
        
        return {"checkout_url": result['url'], "session_id": result['session_id']}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/verify/{session_id}")
def verify_payment(
    session_id: str,
    payments_service: PaymentsService = Depends(get_payments_service),
):
    """Verify a Stripe Checkout Session payment."""
    try:
        session = payments_service.verify_checkout_session(session_id)
        return {
            "paid": session.get('payment_status') == 'paid',
            "session": session
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/success")
async def payment_success_page(
    request: Request,
    session_id: str = None,
    booking_id: str = None,
    amount: float = None,
    currency: str = "USD",
):
    """Payment success page"""
    return templates.TemplateResponse(
        "payment_success.html",
        {
            "request": request,
            "session_id": session_id,
            "booking_id": booking_id,
            "amount": amount,
            "currency": currency,
        }
    )

@router.get("/cancel")
async def payment_cancel_page(
    request: Request,
    booking_id: str = None,
):
    """Payment cancellation page"""
    return templates.TemplateResponse(
        "payment_cancel.html",
        {
            "request": request,
            "booking_id": booking_id,
        }
    )

@router.post("/intent")
def create_payment_intent(
    booking_id: UUID,
    amount: float,
    currency: str = "USD",
    payments_service: PaymentsService = Depends(get_payments_service),
    db: Session = Depends(get_db),
):
    """
    Create a Stripe PaymentIntent for frontend payment collection.
    """
    try:
        result = payments_service.create_payment_intent(
            booking_id=booking_id,
            amount=Decimal(str(amount)),
            currency=currency,
        )
        return result
    except Exception as e:
        raise ValueError(f"Failed to create payment intent: {str(e)}")

@router.get("/{payment_intent_id}/status")
def get_payment_status(
    payment_intent_id: str,
    payments_public: PaymentsPublic = Depends(get_payments_public),
    db: Session = Depends(get_db),
):
    """
    Get payment status for a PaymentIntent.
    """
    payments = payments_public.list_for_booking(payment_intent_id)
    if payments:
        return {"status": payments[0].status}
    return {"status": "unknown"}