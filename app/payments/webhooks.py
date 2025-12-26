import json
import os
import stripe
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from .repository import PaymentsRepository
from .models import Payment, PaymentType, PaymentStatus
from .public import get_payments_public, PaymentsPublic
from app.database import get_db


router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    payments_public: PaymentsPublic = Depends(get_payments_public),
):
    """
    Stripe webhook endpoint
    Processes out-of-band events from the payment processor
    """
    try:
        # Get raw payload
        payload_bytes = await request.body()
        payload = payload_bytes.decode('utf-8')
        sig_header = request.headers.get('stripe-signature')
        
        # For testing without signature verification
        if not sig_header or os.getenv("STRIPE_WEBHOOK_SECRET", "") == "":
            event = json.loads(payload)
        else:
            # Verify webhook signature for production
            try:
                event = stripe.Webhook.construct_event(
                    payload_bytes,
                    sig_header,
                    os.getenv("STRIPE_WEBHOOK_SECRET")
                )
            except stripe.error.SignatureVerificationError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid signature: {str(e)}"
                )
        
        event_type = event.get('type')
        data = event.get('data', {}).get('object', {})
        
        # Handle checkout.session.completed
        if event_type == 'checkout.session.completed':
            session_id = data.get('id')
            booking_id = data.get('metadata', {}).get('booking_id')
            user_id = data.get('metadata', {}).get('user_id')
            payment_intent_id = data.get('payment_intent')
            amount_total = Decimal(data.get('amount_total', 0)) / 100
            currency = data.get('currency', 'usd')
            
            print(f"[Webhook] Payment completed for booking {booking_id}, user {user_id}")
            print(f"[Webhook] Session: {session_id}, PaymentIntent: {payment_intent_id}")
            
            if booking_id and payment_intent_id:
                try:
                    # convert booking_id to UUID
                    booking_uuid = UUID(booking_id)
                    
                    # Create payment record with actual booking_id
                    payment = Payment(
                        booking_id=booking_uuid,
                        type=PaymentType.ESCROW,
                        amount=amount_total,
                        currency=currency,
                        processor_ref=payment_intent_id,
                        status=PaymentStatus.AUTHORIZED,
                    )
                    
                    repo = PaymentsRepository()
                    saved_payment = repo.create_payment(db, payment)
                    
                    print(f"[Webhook] Payment recorded for booking {booking_id}: {saved_payment.id}")
                    
                    # Return success. Bookings domain can check payment status later
                    return {
                        "status": "payment_recorded", 
                        "event": event_type,
                        "payment_id": str(saved_payment.id),
                        "booking_id": booking_id,
                        "user_id": user_id,
                        "amount": float(amount_total),
                        "currency": currency
                    }
                    
                except Exception as e:
                    print(f"[Webhook] Failed to record payment: {str(e)}")
                    # Still return 200 to Stripe (no retries for errors)
                    return {"status": "error", "detail": str(e), "event": event_type}
            
            return {"status": "ignored", "reason": "missing metadata", "event": event_type}
        
        # Handle payment_intent events (existing logic)
        processor_ref = data.get('id')
        if not processor_ref:
            return {"status": "ignored", "reason": "no processor ref"}
        
        repo = PaymentsRepository()
        payment = repo.get_by_processor_ref(db, processor_ref)
        if not payment:
            return {"status": "ignored", "reason": "payment not found"}

        # Update payment_intent.succeeded handling
        if event_type == "payment_intent.succeeded":
            # Check if payment is captured in Stripe
            payment_intent_obj = data
            
            if payment_intent_obj.get('captured', False):
                payment.status = PaymentStatus.CAPTURED
            else:
                payment.status = PaymentStatus.AUTHORIZED
            
            repo.update_payment(db, payment)
            return {"status": "ok", "updated": payment.status}

        if event_type == "payment_intent.canceled":
            payment.status = PaymentStatus.CANCELLED
            repo.update_payment(db, payment)
            return {"status": "ok", "updated": "cancelled"}

        if event_type == "payment_intent.payment_failed":
            payment.status = PaymentStatus.FAILED
            repo.update_payment(db, payment)
            return {"status": "ok", "updated": "failed"}

        if event_type == "payment_intent.amount_capturable_updated":
            print(f"[Webhook] Payment {processor_ref} ready for capture")
            return {"status": "ok", "event": event_type}

        # Add charge.captured event
        if event_type == "charge.captured":
            charge = data
            payment_intent_id = charge.get('payment_intent')
            
            if payment_intent_id:
                captured_payment = repo.get_by_processor_ref(db, payment_intent_id)  # Use different name
                if captured_payment and captured_payment.status == PaymentStatus.AUTHORIZED:
                    captured_payment.status = PaymentStatus.CAPTURED
                    repo.update_payment(db, captured_payment)
                    
        return {"status": "ignored", "event": event_type}
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}",
        )