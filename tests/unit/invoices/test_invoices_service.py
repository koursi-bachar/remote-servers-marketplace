import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal

from app.invoices.service import InvoicesService, BookingSummary, PaymentSummary
from app.invoices.repository import InvoicesRepository
from app.invoices.models import Invoice, InvoiceStatus
from app.invoices.schemas import InvoiceCreate
from app.bookings.public import BookingsPublic
from app.payments.public import PaymentsPublic
from app.organizations.public import OrganizationsPublic
from app.notifications.public import NotificationsPublic


@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_repository():
    return Mock(spec=InvoicesRepository)

@pytest.fixture
def mock_bookings_public():
    return Mock(spec=BookingsPublic)

@pytest.fixture
def mock_payments_public():
    return Mock(spec=PaymentsPublic)

@pytest.fixture
def mock_organizations_public():
    return Mock(spec=OrganizationsPublic)

@pytest.fixture
def mock_notifications_public():
    return Mock(spec=NotificationsPublic)

@pytest.fixture
def invoice_service(
    mock_db, mock_repository, mock_bookings_public, mock_payments_public,
    mock_organizations_public, mock_notifications_public
):
    """Main service fixture that composes other fixtures"""
    return InvoicesService(
        db=mock_db,
        repo=mock_repository,
        bookings_public=mock_bookings_public,
        payments_public=mock_payments_public,
        organizations_public=mock_organizations_public,
        notifications_public=mock_notifications_public,
    )

@pytest.fixture
def sample_invoice_data():
    """Fixture for sample invoice creation data"""
    return InvoiceCreate(
        organization_id=uuid4(),
        period_start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        period_end=datetime(2024, 1, 31, tzinfo=timezone.utc),
        currency="USD",
    )

@pytest.fixture
def sample_invoice():
    """Fixture for a sample invoice instance"""
    invoice = Mock(spec=Invoice)
    invoice.id = uuid4()
    invoice.organization_id = uuid4()
    invoice.period_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    invoice.period_end = datetime(2024, 1, 31, tzinfo=timezone.utc)
    invoice.total_amount = Decimal("1500.00")
    invoice.currency = "USD"
    invoice.status = InvoiceStatus.PENDING
    invoice.organization = Mock()
    return invoice

@pytest.fixture
def sample_booking_summaries():
    """Fixture for sample booking summaries"""
    return [
        BookingSummary(
            id=uuid4(),
            organization_id=uuid4(),
            start_time=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc),
            currency="USD",
        ),
        BookingSummary(
            id=uuid4(),
            organization_id=uuid4(),
            start_time=datetime(2024, 1, 20, 14, 0, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 20, 16, 0, tzinfo=timezone.utc),
            currency="USD",
        ),
    ]

@pytest.fixture
def sample_payment_summaries():
    """Fixture for sample payment summaries"""
    return [
        PaymentSummary(
            id=uuid4(),
            booking_id=uuid4(),
            amount=Decimal("500.00"),
            currency="USD",
            status="captured",
        ),
        PaymentSummary(
            id=uuid4(),
            booking_id=uuid4(),
            amount=Decimal("200.00"),
            currency="USD",
            status="refunded",
        ),
        PaymentSummary(
            id=uuid4(),
            booking_id=uuid4(),
            amount=Decimal("1200.00"),
            currency="USD",
            status="captured",
        ),
    ]

@pytest.fixture
def sample_organization():
    """Fixture for sample organization"""
    org = Mock()
    org.id = uuid4()
    org.name = "Test Organization"
    return org

class TestInvoicesService:
    
    def test_generate_invoice_success_admin(
        self, invoice_service, mock_db, mock_repository, mock_organizations_public,
        mock_bookings_public, mock_payments_public, mock_notifications_public,
        sample_invoice_data, sample_organization, sample_booking_summaries,
        sample_payment_summaries
    ):
        """Test successful invoice generation by admin"""
        total_amount = Decimal("1500.00")  # 500 + 1200 - 200
        mock_new_invoice = Mock(spec=Invoice)
        
        mock_organizations_public.get_organization.return_value = sample_organization
        mock_repository.get_for_period.return_value = None
        mock_bookings_public.get_org_bookings_in_period.return_value = sample_booking_summaries
        mock_payments_public.get_payments_for_bookings.return_value = sample_payment_summaries
        mock_repository.create.return_value = mock_new_invoice
        
        result = invoice_service.generate_invoice(
            sample_invoice_data,
            is_site_admin=True,
        )
        
        assert result == mock_new_invoice
        mock_organizations_public.get_organization.assert_called_once_with(
            sample_invoice_data.organization_id
        )
        mock_repository.get_for_period.assert_called_once_with(
            mock_db,
            organization_id=sample_invoice_data.organization_id,
            period_start=sample_invoice_data.period_start,
            period_end=sample_invoice_data.period_end,
        )
        mock_bookings_public.get_org_bookings_in_period.assert_called_once_with(
            org_id=sample_invoice_data.organization_id,
            period_start=sample_invoice_data.period_start,
            period_end=sample_invoice_data.period_end,
        )
        mock_payments_public.get_payments_for_bookings.assert_called_once_with(
            booking_ids=[b.id for b in sample_booking_summaries]
        )
        mock_repository.create.assert_called_once_with(
            mock_db,
            organization_id=sample_invoice_data.organization_id,
            period_start=sample_invoice_data.period_start,
            period_end=sample_invoice_data.period_end,
            total_amount=total_amount,
            currency=sample_invoice_data.currency,
            status=InvoiceStatus.PENDING,
        )
        mock_notifications_public.invoice_generated.assert_called_once_with(
            sample_organization, mock_new_invoice
        )

    def test_generate_invoice_raises_error_when_not_admin(
        self, invoice_service, sample_invoice_data
    ):
        """Test error when non-admin tries to generate invoice"""
        with pytest.raises(PermissionError, match="Only site admins may generate invoices."):
            invoice_service.generate_invoice(
                sample_invoice_data,
                is_site_admin=False,
            )

    def test_generate_invoice_raises_error_when_org_not_found(
        self, invoice_service, mock_organizations_public, sample_invoice_data
    ):
        """Test error when organization doesn't exist"""
        mock_organizations_public.get_organization.return_value = None
        
        with pytest.raises(ValueError, match="Organization not found."):
            invoice_service.generate_invoice(
                sample_invoice_data,
                is_site_admin=True,
            )

    def test_generate_invoice_raises_error_when_invoice_exists_for_period(
        self, invoice_service, mock_organizations_public, mock_repository,
        sample_invoice_data, sample_organization
    ):
        """Test error when invoice already exists for period"""
        mock_organizations_public.get_organization.return_value = sample_organization
        mock_existing_invoice = Mock(spec=Invoice)
        mock_repository.get_for_period.return_value = mock_existing_invoice
        
        with pytest.raises(ValueError, match="Invoice already exists for this period."):
            invoice_service.generate_invoice(
                sample_invoice_data,
                is_site_admin=True,
            )

    def test_list_org_invoices_success_admin(
        self, invoice_service, mock_db, mock_repository, mock_organizations_public
    ):
        """Test admin can list org invoices"""
        org_id = uuid4()
        mock_invoices = [Mock(spec=Invoice), Mock(spec=Invoice)]
        
        mock_organizations_public.get_organization.return_value = Mock()
        mock_repository.list_for_org.return_value = mock_invoices
        
        result = invoice_service.list_org_invoices(
            org_id=org_id,
            is_site_admin=True,
            is_org_admin=False,
            is_org_member=False,
            skip=10,
            limit=50,
        )
        
        assert result == mock_invoices
        mock_organizations_public.get_organization.assert_called_once_with(org_id)
        mock_repository.list_for_org.assert_called_once_with(
            mock_db,
            organization_id=org_id,
            skip=10,
            limit=50,
        )

    def test_list_org_invoices_success_org_admin(
        self, invoice_service, mock_db, mock_repository, mock_organizations_public
    ):
        """Test org admin can list org invoices"""
        org_id = uuid4()
        mock_invoices = [Mock(spec=Invoice), Mock(spec=Invoice)]
        
        mock_organizations_public.get_organization.return_value = Mock()
        mock_repository.list_for_org.return_value = mock_invoices
        
        result = invoice_service.list_org_invoices(
            org_id=org_id,
            is_site_admin=False,
            is_org_admin=True,
            is_org_member=False,
        )
        
        assert result == mock_invoices
        mock_organizations_public.get_organization.assert_called_once_with(org_id)

    def test_list_org_invoices_success_org_member(
        self, invoice_service, mock_db, mock_repository, mock_organizations_public
    ):
        """Test org member can list org invoices"""
        org_id = uuid4()
        mock_invoices = [Mock(spec=Invoice), Mock(spec=Invoice)]
        
        mock_organizations_public.get_organization.return_value = Mock()
        mock_repository.list_for_org.return_value = mock_invoices
        
        result = invoice_service.list_org_invoices(
            org_id=org_id,
            is_site_admin=False,
            is_org_admin=False,
            is_org_member=True,
        )
        
        assert result == mock_invoices
        mock_organizations_public.get_organization.assert_called_once_with(org_id)

    def test_list_org_invoices_raises_error_when_not_authorized(
        self, invoice_service
    ):
        """Test error when user has no permissions"""
        org_id = uuid4()
        
        with pytest.raises(PermissionError, match="Not allowed to view these invoices."):
            invoice_service.list_org_invoices(
                org_id=org_id,
                is_site_admin=False,
                is_org_admin=False,
                is_org_member=False,
            )

    def test_list_org_invoices_raises_error_when_org_not_found(
        self, invoice_service, mock_organizations_public
    ):
        """Test error when organization doesn't exist"""
        org_id = uuid4()
        
        mock_organizations_public.get_organization.return_value = None
        
        with pytest.raises(ValueError, match="Organization not found."):
            invoice_service.list_org_invoices(
                org_id=org_id,
                is_site_admin=True,
                is_org_admin=False,
                is_org_member=False,
            )

    def test_list_all_invoices_success_admin(
        self, invoice_service, mock_db, mock_repository
    ):
        """Test admin can list all invoices"""
        mock_invoices = [Mock(spec=Invoice), Mock(spec=Invoice)]
        
        mock_repository.list_all.return_value = mock_invoices
        
        result = invoice_service.list_all_invoices(
            is_site_admin=True,
            skip=5,
            limit=20,
        )
        
        assert result == mock_invoices
        mock_repository.list_all.assert_called_once_with(
            mock_db,
            skip=5,
            limit=20,
        )

    def test_list_all_invoices_raises_error_when_not_admin(
        self, invoice_service
    ):
        """Test error when non-admin tries to list all invoices"""
        with pytest.raises(PermissionError, match="Only site admins may list all invoices."):
            invoice_service.list_all_invoices(
                is_site_admin=False,
            )

    def test_get_invoice_success_admin(
        self, invoice_service, mock_db, mock_repository, sample_invoice
    ):
        """Test admin can get any invoice"""
        mock_repository.get.return_value = sample_invoice
        
        result = invoice_service.get_invoice(
            invoice_id=sample_invoice.id,
            is_site_admin=True,
            user_org_ids=[uuid4()],  # Admin can access regardless of org membership
        )
        
        assert result == sample_invoice
        mock_repository.get.assert_called_once_with(mock_db, sample_invoice.id)

    def test_get_invoice_success_org_member(
        self, invoice_service, mock_db, mock_repository, sample_invoice
    ):
        """Test org member can get invoice from their org"""
        user_org_ids = [sample_invoice.organization_id, uuid4()]
        
        mock_repository.get.return_value = sample_invoice
        
        result = invoice_service.get_invoice(
            invoice_id=sample_invoice.id,
            is_site_admin=False,
            user_org_ids=user_org_ids,
        )
        
        assert result == sample_invoice
        mock_repository.get.assert_called_once_with(mock_db, sample_invoice.id)

    def test_get_invoice_raises_error_when_not_found(
        self, invoice_service, mock_db, mock_repository
    ):
        """Test error when invoice doesn't exist"""
        invoice_id = uuid4()
        
        mock_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Invoice not found."):
            invoice_service.get_invoice(
                invoice_id=invoice_id,
                is_site_admin=True,
                user_org_ids=[uuid4()],
            )

    def test_get_invoice_raises_error_when_not_authorized(
        self, invoice_service, mock_db, mock_repository, sample_invoice
    ):
        """Test error when user tries to access invoice from another org"""
        user_org_ids = [uuid4()]  # Different org than invoice
        
        mock_repository.get.return_value = sample_invoice
        
        with pytest.raises(PermissionError, match="Not allowed to view this invoice."):
            invoice_service.get_invoice(
                invoice_id=sample_invoice.id,
                is_site_admin=False,
                user_org_ids=user_org_ids,
            )

    def test_finalize_invoice_success_admin(
        self, invoice_service, mock_db, mock_repository, mock_notifications_public,
        sample_invoice
    ):
        """Test admin can finalize pending invoice"""
        sample_invoice.status = InvoiceStatus.PENDING
        mock_finalized_invoice = Mock(spec=Invoice)
        mock_finalized_invoice.organization = Mock()
        
        mock_repository.get.return_value = sample_invoice
        mock_repository.update_status.return_value = mock_finalized_invoice
        
        result = invoice_service.finalize_invoice(
            invoice_id=sample_invoice.id,
            is_site_admin=True,
        )
        
        assert result == mock_finalized_invoice
        mock_repository.get.assert_called_once_with(mock_db, sample_invoice.id)
        mock_repository.update_status.assert_called_once_with(
            mock_db,
            sample_invoice,
            InvoiceStatus.FINALIZED,
        )
        mock_notifications_public.invoice_finalized.assert_called_once_with(
            mock_finalized_invoice.organization, mock_finalized_invoice
        )

    def test_finalize_invoice_raises_error_when_not_admin(
        self, invoice_service, sample_invoice
    ):
        """Test error when non-admin tries to finalize invoice"""
        with pytest.raises(PermissionError, match="Only site admins may finalize invoices."):
            invoice_service.finalize_invoice(
                invoice_id=sample_invoice.id,
                is_site_admin=False,
            )

    def test_finalize_invoice_raises_error_when_not_found(
        self, invoice_service, mock_db, mock_repository
    ):
        """Test error when invoice doesn't exist"""
        invoice_id = uuid4()
        
        mock_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Invoice not found."):
            invoice_service.finalize_invoice(
                invoice_id=invoice_id,
                is_site_admin=True,
            )

    def test_finalize_invoice_raises_error_when_not_pending(
        self, invoice_service, mock_db, mock_repository, sample_invoice
    ):
        """Test error when trying to finalize non-pending invoice"""
        sample_invoice.status = InvoiceStatus.FINALIZED
        
        mock_repository.get.return_value = sample_invoice
        
        with pytest.raises(ValueError, match="Only pending invoices can be finalized."):
            invoice_service.finalize_invoice(
                invoice_id=sample_invoice.id,
                is_site_admin=True,
            )
        
        mock_repository.update_status.assert_not_called()

    def test_void_invoice_success_admin(
        self, invoice_service, mock_db, mock_repository, sample_invoice
    ):
        """Test admin can void non-paid invoice"""
        sample_invoice.status = InvoiceStatus.PENDING
        mock_voided_invoice = Mock(spec=Invoice)
        
        mock_repository.get.return_value = sample_invoice
        mock_repository.update_status.return_value = mock_voided_invoice
        
        result = invoice_service.void_invoice(
            invoice_id=sample_invoice.id,
            is_site_admin=True,
        )
        
        assert result == mock_voided_invoice
        mock_repository.get.assert_called_once_with(mock_db, sample_invoice.id)
        mock_repository.update_status.assert_called_once_with(
            mock_db,
            sample_invoice,
            InvoiceStatus.VOID,
        )

    def test_void_invoice_raises_error_when_not_admin(
        self, invoice_service, sample_invoice
    ):
        """Test error when non-admin tries to void invoice"""
        with pytest.raises(PermissionError, match="Only site admins may void invoices."):
            invoice_service.void_invoice(
                invoice_id=sample_invoice.id,
                is_site_admin=False,
            )

    def test_void_invoice_raises_error_when_not_found(
        self, invoice_service, mock_db, mock_repository
    ):
        """Test error when invoice doesn't exist"""
        invoice_id = uuid4()
        
        mock_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Invoice not found."):
            invoice_service.void_invoice(
                invoice_id=invoice_id,
                is_site_admin=True,
            )

    def test_void_invoice_raises_error_when_paid(
        self, invoice_service, mock_db, mock_repository, sample_invoice
    ):
        """Test error when trying to void paid invoice"""
        sample_invoice.status = InvoiceStatus.PAID
        
        mock_repository.get.return_value = sample_invoice
        
        with pytest.raises(ValueError, match="Cannot void a paid invoice."):
            invoice_service.void_invoice(
                invoice_id=sample_invoice.id,
                is_site_admin=True,
            )
        
        mock_repository.update_status.assert_not_called()

    def test_mark_invoice_paid_success_admin(
        self, invoice_service, mock_db, mock_repository, sample_invoice
    ):
        """Test admin can mark finalized invoice as paid"""
        sample_invoice.status = InvoiceStatus.FINALIZED
        mock_paid_invoice = Mock(spec=Invoice)
        
        mock_repository.get.return_value = sample_invoice
        mock_repository.update_status.return_value = mock_paid_invoice
        
        result = invoice_service.mark_invoice_paid(
            invoice_id=sample_invoice.id,
            is_site_admin=True,
        )
        
        assert result == mock_paid_invoice
        mock_repository.get.assert_called_once_with(mock_db, sample_invoice.id)
        mock_repository.update_status.assert_called_once_with(
            mock_db,
            sample_invoice,
            InvoiceStatus.PAID,
        )

    def test_mark_invoice_paid_raises_error_when_not_admin(
        self, invoice_service, sample_invoice
    ):
        """Test error when non-admin tries to mark invoice as paid"""
        with pytest.raises(PermissionError, match="Only site admins may mark invoices as paid."):
            invoice_service.mark_invoice_paid(
                invoice_id=sample_invoice.id,
                is_site_admin=False,
            )

    def test_mark_invoice_paid_raises_error_when_not_found(
        self, invoice_service, mock_db, mock_repository
    ):
        """Test error when invoice doesn't exist"""
        invoice_id = uuid4()
        
        mock_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Invoice not found."):
            invoice_service.mark_invoice_paid(
                invoice_id=invoice_id,
                is_site_admin=True,
            )

    def test_mark_invoice_paid_raises_error_when_not_finalized(
        self, invoice_service, mock_db, mock_repository, sample_invoice
    ):
        """Test error when trying to mark non-finalized invoice as paid"""
        sample_invoice.status = InvoiceStatus.PENDING
        
        mock_repository.get.return_value = sample_invoice
        
        with pytest.raises(ValueError, match="Only finalized invoices can be marked as paid."):
            invoice_service.mark_invoice_paid(
                invoice_id=sample_invoice.id,
                is_site_admin=True,
            )
        
        mock_repository.update_status.assert_not_called()

    def test_aggregate_total_amount_calculates_correctly(
        self, invoice_service, mock_payments_public, sample_booking_summaries,
        sample_payment_summaries
    ):
        """Test total amount calculation from bookings and payments"""
        mock_payments_public.get_payments_for_bookings.return_value = sample_payment_summaries
        
        result = invoice_service._aggregate_total_amount(sample_booking_summaries)
        
        # captured: 500 + 1200 = 1700, refunded: 200, total: 1500
        expected = Decimal("1500.00")
        assert result == expected
        mock_payments_public.get_payments_for_bookings.assert_called_once_with(
            booking_ids=[b.id for b in sample_booking_summaries]
        )

    def test_aggregate_total_amount_returns_zero_for_no_bookings(
        self, invoice_service
    ):
        """Test total amount is zero when no bookings"""
        result = invoice_service._aggregate_total_amount([])
        
        assert result == Decimal("0.00")

    def test_aggregate_total_amount_handles_only_captured_payments(
        self, invoice_service, mock_payments_public
    ):
        """Test total amount with only captured payments"""
        bookings = [Mock(spec=BookingSummary, id=uuid4())]
        payments = [
            PaymentSummary(
                id=uuid4(),
                booking_id=bookings[0].id,
                amount=Decimal("300.00"),
                currency="USD",
                status="captured",
            ),
            PaymentSummary(
                id=uuid4(),
                booking_id=bookings[0].id,
                amount=Decimal("700.00"),
                currency="USD",
                status="captured",
            ),
        ]
        
        mock_payments_public.get_payments_for_bookings.return_value = payments
        
        result = invoice_service._aggregate_total_amount(bookings)
        
        assert result == Decimal("1000.00")

    def test_aggregate_total_amount_handles_only_refunded_payments(
        self, invoice_service, mock_payments_public
    ):
        """Test total amount with only refunded payments"""
        bookings = [Mock(spec=BookingSummary, id=uuid4())]
        payments = [
            PaymentSummary(
                id=uuid4(),
                booking_id=bookings[0].id,
                amount=Decimal("300.00"),
                currency="USD",
                status="refunded",
            ),
        ]
        
        mock_payments_public.get_payments_for_bookings.return_value = payments
        
        result = invoice_service._aggregate_total_amount(bookings)
        
        # Should be negative since only refunds
        assert result == Decimal("-300.00")

    def test_ensure_org_exists_success(
        self, invoice_service, mock_organizations_public
    ):
        """Test org exists validation succeeds"""
        org_id = uuid4()
        mock_organization = Mock()
        
        mock_organizations_public.get_organization.return_value = mock_organization
        
        # Should not raise an exception
        invoice_service._ensure_org_exists(org_id)
        
        mock_organizations_public.get_organization.assert_called_once_with(org_id)

    def test_ensure_org_exists_raises_error_when_not_found(
        self, invoice_service, mock_organizations_public
    ):
        """Test org exists validation fails"""
        org_id = uuid4()
        
        mock_organizations_public.get_organization.return_value = None
        
        with pytest.raises(ValueError, match="Organization not found."):
            invoice_service._ensure_org_exists(org_id)