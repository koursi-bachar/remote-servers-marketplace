from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_

from .models import Invoice, InvoiceStatus


class InvoicesRepository:
    def create(
        self,
        db: Session,
        *,
        organization_id: UUID,
        period_start: datetime,
        period_end: datetime,
        total_amount,
        currency: str,
        status: InvoiceStatus = InvoiceStatus.PENDING,
    ) -> Invoice:
        invoice = Invoice(
            organization_id=organization_id,
            period_start=period_start,
            period_end=period_end,
            total_amount=total_amount,
            currency=currency,
            status=status,
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice

    def get(self, db: Session, invoice_id: UUID) -> Optional[Invoice]:
        return db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def get_for_period(
        self,
        db: Session,
        *,
        organization_id: UUID,
        period_start: datetime,
        period_end: datetime,
    ) -> Optional[Invoice]:
        """
        Simple 'exact match' check. Can be extended to check 
        any overlap with [period_start, period_end].
        """
        return (
            db.query(Invoice)
            .filter(
                Invoice.organization_id == organization_id,
                Invoice.period_start == period_start,
                Invoice.period_end == period_end,
            )
            .first()
        )

    def list_for_org(
        self,
        db: Session,
        organization_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Invoice]:
        return (
            db.query(Invoice)
            .filter(Invoice.organization_id == organization_id)
            .order_by(Invoice.period_start.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Invoice]:
        return (
            db.query(Invoice)
            .order_by(Invoice.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        db: Session,
        invoice: Invoice,
        new_status: InvoiceStatus,
    ) -> Invoice:
        invoice.status = new_status
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice