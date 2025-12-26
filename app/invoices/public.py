from typing import List, Protocol
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.invoices.models import Invoice
from app.invoices.repository import InvoicesRepository
from app.invoices.service import InvoicesService, get_invoice_service


class InvoicesPublic(Protocol):
    """Protocol defining the public interface for invoices queries."""
    def get_invoice(self, invoice_id: UUID) -> Invoice | None:
        ...

    def get_invoices_for_org(self, org_id: UUID, limit: int = 100) -> List[Invoice]:
        ...

class InvoicesPublicImpl(InvoicesPublic):
    """Concrete implementation of InvoicesPublic using the InvoicesService."""
    def __init__(
        self,
        db: Session,
        repo: InvoicesRepository,
        service: InvoicesService,
    ) -> None:
        self.db = db
        self.repo = repo
        self.service = service

    def get_invoice(self, invoice_id: UUID) -> Invoice | None:
        return self.repo.get(invoice_id)

    def get_invoices_for_org(self, org_id: UUID, limit: int = 100) -> List[Invoice]:
        return self.repo.list_for_org(organization_id=org_id, limit=limit)

def get_invoices_public(
    db: Session = Depends(get_db),
    service: InvoicesService = Depends(get_invoice_service),
) -> InvoicesPublic:
    """Dependency injection provider for InvoicesService interface."""
    repo = InvoicesRepository()
    return InvoicesPublicImpl(db=db, repo=repo, service=service)