from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.public import ensure_admin
from app.organizations.public import OrganizationsPublic, get_organizations_public
from app.auth.auth import get_current_user
from app.invoices.schemas import InvoiceCreate, InvoiceListItem, InvoiceRead
from app.invoices.service import InvoicesService, get_invoice_service

from app.users.models import User, UserRole

router = APIRouter()


def _user_org_ids(current_user) -> list[UUID]:
    """
    Adjust to user/org membership representation.
    For now we assume current_user has .organization_ids or similar.
    """
    return getattr(current_user, "organization_ids", []) or []

#Admin endpoints
@router.post(
    "/admin/generate",
    response_model=InvoiceRead,
    status_code=status.HTTP_201_CREATED,
)
def generate_invoice_admin(
    invoice_in: InvoiceCreate,
    service: InvoicesService = Depends(get_invoice_service),
    admin_user=Depends(ensure_admin),
):
    try:
        invoice = service.generate_invoice(
            invoice_in,
            is_site_admin=True,
        )
    except (PermissionError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    return invoice

@router.get(
    "/admin",
    response_model=List[InvoiceListItem],
)
def list_all_invoices_admin(
    service: InvoicesService = Depends(get_invoice_service),
    admin_user=Depends(ensure_admin),
    skip: int = 0,
    limit: int = 100,
):
    invoices = service.list_all_invoices(
        is_site_admin=True,
        skip=skip,
        limit=limit,
    )
    return invoices

@router.post(
    "/admin/{invoice_id}/finalize",
    response_model=InvoiceRead,
)
def finalize_invoice_admin(
    invoice_id: UUID,
    service: InvoicesService = Depends(get_invoice_service),
    admin_user=Depends(ensure_admin),
):
    try:
        invoice = service.finalize_invoice(
            invoice_id,
            is_site_admin=True,
        )
    except (PermissionError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    return invoice

@router.post(
    "/admin/{invoice_id}/void",
    response_model=InvoiceRead,
)
def void_invoice_admin(
    invoice_id: UUID,
    service: InvoicesService = Depends(get_invoice_service),
    admin_user=Depends(ensure_admin),
):
    try:
        invoice = service.void_invoice(
            invoice_id,
            is_site_admin=True,
        )
    except (PermissionError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    return invoice

#Organization endpoints
@router.get(
    "/organizations/{org_id}",
    response_model=List[InvoiceListItem],
)
def list_org_invoices(
    org_id: UUID,
    service: InvoicesService = Depends(get_invoice_service),
    organization_public: OrganizationsPublic = Depends(get_organizations_public),
    current_user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    user_org_ids = _user_org_ids(current_user)
    is_site_admin = getattr(current_user, "is_site_admin", False)
    is_org_admin = getattr(current_user, "is_org_admin_for", lambda _id: False)(org_id)
    is_org_member = org_id in user_org_ids

    try:
        invoices = service.list_org_invoices(
            org_id,
            is_site_admin=is_site_admin,
            is_org_admin=is_org_admin,
            is_org_member=is_org_member,
            skip=skip,
            limit=limit,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    return invoices

@router.get(
    "/{invoice_id}",
    response_model=InvoiceRead,
)
def get_invoice_detail(
    invoice_id: UUID,
    service: InvoicesService = Depends(get_invoice_service),
    current_user=Depends(get_current_user),
):
    is_site_admin = getattr(current_user, "is_site_admin", False)
    user_org_ids = _user_org_ids(current_user)

    try:
        invoice = service.get_invoice(
            invoice_id,
            is_site_admin=is_site_admin,
            user_org_ids=user_org_ids,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return invoice

@router.get("/organization/{org_id:uuid}", response_model=List[InvoiceRead])
def get_organization_invoices(
    org_id: UUID,
    user: User = Depends(get_current_user),
    service: InvoicesService = Depends(get_invoice_service),
    organizations_public: OrganizationsPublic = Depends(get_organizations_public),
):
    """
    Get all invoices for an organization.
    """
    # Check permissions
    is_site_admin = user.role == "admin"
    is_org_admin = organizations_public.is_org_admin(user.id, org_id)
    is_org_member = organizations_public.is_org_member(user.id, org_id)
    
    return service.list_org_invoices(
        org_id=org_id,
        is_site_admin=is_site_admin,
        is_org_admin=is_org_admin,
        is_org_member=is_org_member,
    )