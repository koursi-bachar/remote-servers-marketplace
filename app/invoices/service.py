from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable, List
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.invoices.models import Invoice, InvoiceStatus
from app.invoices.repository import InvoicesRepository
from app.invoices.schemas import InvoiceCreate
from app.bookings.public import BookingsPublic, get_bookings_public
from app.payments.public import PaymentsPublic, get_payments_public
from app.organizations.public import OrganizationsPublic, get_organizations_public

from app.notifications.public import NotificationsPublic, get_notifications_public


@dataclass
class BookingSummary:
    id: UUID
    organization_id: UUID
    start_time: datetime
    end_time: datetime
    currency: str

@dataclass
class PaymentSummary:
    id: UUID
    booking_id: UUID
    amount: Decimal
    currency: str
    status: str

class InvoicesService:
    """
    Orchestrates invoice generation and lifecycle.
    Permissions:
    - Admin-only for generate/finalize/void/list_alls.
    - Org admins (and optionally members) can read their org's invoices.
    """
    def __init__(
        self,
        db: Session,
        repo: InvoicesRepository,
        bookings_public: BookingsPublic,
        payments_public: PaymentsPublic,
        organizations_public: OrganizationsPublic,
        notifications_public: NotificationsPublic,
    ) -> None:
        self.db = db
        self.repo = repo
        self.bookings_public = bookings_public
        self.payments_public = payments_public
        self.organizations_public = organizations_public
        self.notifications = notifications_public

    #Public API: generation/lifecycle
    def generate_invoice(
        self,
        invoice_in: InvoiceCreate,
        *,
        is_site_admin: bool,
    ) -> Invoice:
        """
        Generate an invoice for an organization.
        Aggregates the total order amount from bookings and calculates total.
        """
        if not is_site_admin:
            raise PermissionError("Only site admins may generate invoices.")

        org = self.organizations_public.get_organization(invoice_in.organization_id)
        if org is None:
            raise ValueError("Organization not found.")

        existing = self.repo.get_for_period(
            self.db,
            organization_id=invoice_in.organization_id,
            period_start=invoice_in.period_start,
            period_end=invoice_in.period_end,
        )
        if existing:
            raise ValueError("Invoice already exists for this period.")

        bookings = self.bookings_public.get_org_bookings_in_period(
            org_id=invoice_in.organization_id,
            period_start=invoice_in.period_start,
            period_end=invoice_in.period_end,
        )

        total_amount = self._aggregate_total_amount(bookings)

        invoice = self.repo.create(
            self.db,
            organization_id=invoice_in.organization_id,
            period_start=invoice_in.period_start,
            period_end=invoice_in.period_end,
            total_amount=total_amount,
            currency=invoice_in.currency,
            status=InvoiceStatus.PENDING,
        )

        self.notifications.invoice_generated(org, invoice)

        return invoice

    def list_org_invoices(
        self,
        org_id: UUID,
        *,
        is_site_admin: bool,
        is_org_admin: bool,
        is_org_member: bool,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Invoice]:
        """"Lists invoices for a given organization"""
        if not (is_site_admin or is_org_admin or is_org_member):
            raise PermissionError("Not allowed to view these invoices.")

        self._ensure_org_exists(org_id)

        invoices = self.repo.list_for_org(
            self.db,
            organization_id=org_id,
            skip=skip,
            limit=limit,
        )

        return invoices

    def list_all_invoices(
        self,
        *,
        is_site_admin: bool,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Invoice]:
        if not is_site_admin:
            raise PermissionError("Only site admins may list all invoices.")
        return self.repo.list_all(self.db, skip=skip, limit=limit)

    def get_invoice(
        self,
        invoice_id: UUID,
        *,
        is_site_admin: bool,
        user_org_ids: Iterable[UUID],
    ) -> Invoice:
        invoice = self.repo.get(self.db, invoice_id)
        if not invoice:
            raise ValueError("Invoice not found.")

        if not is_site_admin and invoice.organization_id not in set(user_org_ids):
            raise PermissionError("Not allowed to view this invoice.")

        return invoice

    def finalize_invoice(
        self,
        invoice_id: UUID,
        *,
        is_site_admin: bool,
    ) -> Invoice:
        """Admin function to finalize an invoice and change the invoice status."""
        if not is_site_admin:
            raise PermissionError("Only site admins may finalize invoices.")

        invoice = self.repo.get(self.db, invoice_id)
        if not invoice:
            raise ValueError("Invoice not found.")

        if invoice.status != InvoiceStatus.PENDING:
            raise ValueError("Only pending invoices can be finalized.")

        invoice = self.repo.update_status(self.db, invoice, InvoiceStatus.FINALIZED)

        self.notifications.invoice_finalized(invoice.organization, invoice)

        return invoice

    def void_invoice(
        self,
        invoice_id: UUID,
        *,
        is_site_admin: bool,
    ) -> Invoice:
        """Admin function to void an invoice in case of errors."""
        if not is_site_admin:
            raise PermissionError("Only site admins may void invoices.")

        invoice = self.repo.get(self.db, invoice_id)
        if not invoice:
            raise ValueError("Invoice not found.")

        if invoice.status == InvoiceStatus.PAID:
            raise ValueError("Cannot void a paid invoice.")

        invoice = self.repo.update_status(self.db, invoice, InvoiceStatus.VOID)
        return invoice

    def mark_invoice_paid(
        self,
        invoice_id: UUID,
        *,
        is_site_admin: bool,
    ) -> Invoice:
        """
        Optional helper when integrating with external AR/payment-by-invoice.
        """
        if not is_site_admin:
            raise PermissionError("Only site admins may mark invoices as paid.")

        invoice = self.repo.get(self.db, invoice_id)
        if not invoice:
            raise ValueError("Invoice not found.")

        if invoice.status != InvoiceStatus.FINALIZED:
            raise ValueError("Only finalized invoices can be marked as paid.")

        invoice = self.repo.update_status(self.db, invoice, InvoiceStatus.PAID)
        return invoice

    #Helpers
    def _ensure_org_exists(self, org_id: UUID) -> None:
        org = self.organizations_public.get_organization(org_id)
        if not org:
            raise ValueError("Organization not found.")

    def _aggregate_total_amount(
        self,
        bookings: List[BookingSummary],
    ) -> Decimal:
        """
        Aggregate total invoice amount = sum(captured) - sum(refunded)
        for all payments belonging to bookings in the period.
        Assumes one currency per organization.
        """
        if not bookings:
            return Decimal("0.00")

        booking_ids = [b.id for b in bookings]

        payments: List[PaymentSummary] = self.payments_public.get_payments_for_bookings(
            booking_ids=booking_ids
        )

        captured = Decimal("0.00")
        refunded = Decimal("0.00")

        for p in payments:
            if p.status == "captured":
                captured += p.amount
            elif p.status == "refunded":
                refunded += p.amount

        return captured - refunded

def get_invoice_service(
    db: Session = Depends(get_db),
    bookings_public: BookingsPublic = Depends(get_bookings_public),
    payments_public: PaymentsPublic = Depends(get_payments_public),
    organizations_public: OrganizationsPublic = Depends(get_organizations_public),
    notifications_public: NotificationsPublic = Depends(get_notifications_public),
) -> InvoicesService:
    repo = InvoicesRepository()
    return InvoicesService(
        db=db,
        repo=repo,
        bookings_public=bookings_public,
        payments_public=payments_public,
        organizations_public=organizations_public,
        notifications_public=notifications_public,
    )