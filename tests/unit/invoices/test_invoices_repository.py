import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timezone

from app.invoices.repository import InvoicesRepository
from app.invoices.models import Invoice, InvoiceStatus


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def invoices_repository():
    """InvoicesRepository instance fixture"""
    return InvoicesRepository()

@pytest.fixture
def sample_invoice():
    """Fixture for a mock invoice object"""
    invoice = Mock(spec=Invoice)
    invoice.id = uuid4()
    invoice.organization_id = uuid4()
    invoice.period_start = datetime.now(timezone.utc)
    invoice.period_end = datetime.now(timezone.utc)
    invoice.total_amount = 150.75
    invoice.currency = "USD"
    invoice.status = InvoiceStatus.PENDING
    invoice.created_at = datetime.now(timezone.utc)
    return invoice

@pytest.fixture
def sample_invoice_data():
    """Fixture for invoice creation data"""
    return {
        "organization_id": uuid4(),
        "period_start": datetime.now(timezone.utc),
        "period_end": datetime.now(timezone.utc),
        "total_amount": 150.75,
        "currency": "USD",
        "status": InvoiceStatus.PENDING
    }

class TestInvoicesRepository:
    
    def test_create_performs_database_operations(self, invoices_repository, mock_db, sample_invoice_data):
        """Test that invoice creation performs database operations"""
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        result = invoices_repository.create(
            db=mock_db,
            organization_id=sample_invoice_data["organization_id"],
            period_start=sample_invoice_data["period_start"],
            period_end=sample_invoice_data["period_end"],
            total_amount=sample_invoice_data["total_amount"],
            currency=sample_invoice_data["currency"],
            status=sample_invoice_data["status"]
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_get_returns_invoice_when_exists(self, invoices_repository, mock_db, sample_invoice):
        """Test getting invoice by ID returns invoice when it exists"""
        invoice_id = uuid4()
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query

        filter_result = Mock()
        filter_result.first.return_value = sample_invoice
        mock_query.filter.return_value = filter_result
        
        result = invoices_repository.get(db=mock_db, invoice_id=invoice_id)
        
        assert result == sample_invoice
        mock_db.query.assert_called_once_with(Invoice)
        mock_query.filter.assert_called_once()
        filter_result.first.assert_called_once()

    def test_get_returns_none_when_not_found(self, invoices_repository, mock_db):
        """Test getting invoice by ID returns None when not found"""
        invoice_id = uuid4()
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        filter_result = Mock()
        filter_result.first.return_value = None
        mock_query.filter.return_value = filter_result
        
        result = invoices_repository.get(db=mock_db, invoice_id=invoice_id)
        
        assert result is None
        mock_db.query.assert_called_once_with(Invoice)
        mock_query.filter.assert_called_once()
        filter_result.first.assert_called_once()

    def test_get_for_period_returns_invoice_when_exists(self, invoices_repository, mock_db, sample_invoice):
        """Test getting invoice for period returns invoice when it exists"""
        organization_id = uuid4()
        period_start = datetime.now(timezone.utc)
        period_end = datetime.now(timezone.utc)
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        filter_result = Mock()
        filter_result.first.return_value = sample_invoice
        mock_query.filter.return_value = filter_result
        
        result = invoices_repository.get_for_period(
            db=mock_db,
            organization_id=organization_id,
            period_start=period_start,
            period_end=period_end
        )
        
        assert result == sample_invoice
        mock_db.query.assert_called_once_with(Invoice)
        mock_query.filter.assert_called_once()
        filter_result.first.assert_called_once()

    def test_get_for_period_returns_none_when_not_found(self, invoices_repository, mock_db):
        """Test getting invoice for period returns None when not found"""
        organization_id = uuid4()
        period_start = datetime.now(timezone.utc)
        period_end = datetime.now(timezone.utc)
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        filter_result = Mock()
        filter_result.first.return_value = None
        mock_query.filter.return_value = filter_result
        
        result = invoices_repository.get_for_period(
            db=mock_db,
            organization_id=organization_id,
            period_start=period_start,
            period_end=period_end
        )
        
        assert result is None
        mock_db.query.assert_called_once_with(Invoice)
        mock_query.filter.assert_called_once()
        filter_result.first.assert_called_once()

    def test_list_for_org_returns_invoices_sorted_by_period(self, invoices_repository, mock_db):
        """Test getting invoices for organization returns sorted list"""
        organization_id = uuid4()
        mock_invoices = [Mock(spec=Invoice), Mock(spec=Invoice)]
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        filter_result = Mock()
        order_result = Mock()
        offset_result = Mock()
        limit_result = Mock()
        
        mock_query.filter.return_value = filter_result
        filter_result.order_by.return_value = order_result
        order_result.offset.return_value = offset_result
        offset_result.limit.return_value = limit_result
        limit_result.all.return_value = mock_invoices
        
        result = invoices_repository.list_for_org(db=mock_db, organization_id=organization_id)
        
        assert result == mock_invoices
        mock_db.query.assert_called_once_with(Invoice)
        mock_query.filter.assert_called_once()

        filter_result.order_by.assert_called_once()
        assert len(filter_result.order_by.call_args[0]) == 1
        
        order_result.offset.assert_called_once_with(0)
        offset_result.limit.assert_called_once_with(100)
        limit_result.all.assert_called_once()

    def test_list_for_org_returns_empty_list_when_none_exist(self, invoices_repository, mock_db):
        """Test getting invoices for organization returns empty list when none exist"""
        organization_id = uuid4()
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        filter_result = Mock()
        order_result = Mock()
        offset_result = Mock()
        limit_result = Mock()
        
        mock_query.filter.return_value = filter_result
        filter_result.order_by.return_value = order_result
        order_result.offset.return_value = offset_result
        offset_result.limit.return_value = limit_result
        limit_result.all.return_value = []
        
        result = invoices_repository.list_for_org(db=mock_db, organization_id=organization_id)
        
        assert result == []
        mock_db.query.assert_called_once_with(Invoice)
        mock_query.filter.assert_called_once()
        

        filter_result.order_by.assert_called_once()
        assert len(filter_result.order_by.call_args[0]) == 1
        
        order_result.offset.assert_called_once_with(0)
        offset_result.limit.assert_called_once_with(100)
        limit_result.all.assert_called_once()

    def test_list_for_org_respects_skip_and_limit(self, invoices_repository, mock_db):
        """Test getting invoices for organization respects skip and limit parameters"""
        organization_id = uuid4()
        skip = 10
        limit = 25
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        filter_result = Mock()
        order_result = Mock()
        offset_result = Mock()
        limit_result = Mock()
        
        mock_query.filter.return_value = filter_result
        filter_result.order_by.return_value = order_result
        order_result.offset.return_value = offset_result
        offset_result.limit.return_value = limit_result
        limit_result.all.return_value = []
        
        result = invoices_repository.list_for_org(
            db=mock_db, 
            organization_id=organization_id, 
            skip=skip, 
            limit=limit
        )
        
        assert result == []
        mock_db.query.assert_called_once_with(Invoice)
        mock_query.filter.assert_called_once()

        filter_result.order_by.assert_called_once()
        assert len(filter_result.order_by.call_args[0]) == 1
        
        order_result.offset.assert_called_once_with(skip)
        offset_result.limit.assert_called_once_with(limit)
        limit_result.all.assert_called_once()

    def test_list_all_returns_invoices_sorted_by_created_at(self, invoices_repository, mock_db):
        """Test getting all invoices returns sorted list"""
        mock_invoices = [Mock(spec=Invoice), Mock(spec=Invoice)]
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        order_result = Mock()
        offset_result = Mock()
        limit_result = Mock()
        
        mock_query.order_by.return_value = order_result
        order_result.offset.return_value = offset_result
        offset_result.limit.return_value = limit_result
        limit_result.all.return_value = mock_invoices
        
        result = invoices_repository.list_all(db=mock_db)
        
        assert result == mock_invoices
        mock_db.query.assert_called_once_with(Invoice)
     
        mock_query.order_by.assert_called_once()
        assert len(mock_query.order_by.call_args[0]) == 1
        
        order_result.offset.assert_called_once_with(0)
        offset_result.limit.assert_called_once_with(100)
        limit_result.all.assert_called_once()

    def test_list_all_returns_empty_list_when_none_exist(self, invoices_repository, mock_db):
        """Test getting all invoices returns empty list when none exist"""
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        order_result = Mock()
        offset_result = Mock()
        limit_result = Mock()
        
        mock_query.order_by.return_value = order_result
        order_result.offset.return_value = offset_result
        offset_result.limit.return_value = limit_result
        limit_result.all.return_value = []
        
        result = invoices_repository.list_all(db=mock_db)
        
        assert result == []
        mock_db.query.assert_called_once_with(Invoice)

        mock_query.order_by.assert_called_once()
        assert len(mock_query.order_by.call_args[0]) == 1
        
        order_result.offset.assert_called_once_with(0)
        offset_result.limit.assert_called_once_with(100)
        limit_result.all.assert_called_once()

    def test_list_all_respects_skip_and_limit(self, invoices_repository, mock_db):
        """Test getting all invoices respects skip and limit parameters"""
        skip = 5
        limit = 50
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        order_result = Mock()
        offset_result = Mock()
        limit_result = Mock()
        
        mock_query.order_by.return_value = order_result
        order_result.offset.return_value = offset_result
        offset_result.limit.return_value = limit_result
        limit_result.all.return_value = []
        
        result = invoices_repository.list_all(db=mock_db, skip=skip, limit=limit)
        
        assert result == []
        mock_db.query.assert_called_once_with(Invoice)
        
        mock_query.order_by.assert_called_once()
        assert len(mock_query.order_by.call_args[0]) == 1
        
        order_result.offset.assert_called_once_with(skip)
        offset_result.limit.assert_called_once_with(limit)
        limit_result.all.assert_called_once()

    def test_update_status_updates_existing_invoice(self, invoices_repository, mock_db, sample_invoice):
        """Test updating status for existing invoice"""
        new_status = InvoiceStatus.PAID
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        result = invoices_repository.update_status(db=mock_db, invoice=sample_invoice, new_status=new_status)
        
        assert sample_invoice.status == new_status
        mock_db.add.assert_called_once_with(sample_invoice)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_invoice)