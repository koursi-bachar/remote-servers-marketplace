import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.invoices.public import InvoicesPublicImpl


def test_invoices_public_implements_protocol():
    """Test that InvoicesPublicImpl properly implements the InvoicesPublic protocol"""
    mock_db = Mock()
    mock_repo = Mock()
    mock_service = Mock()
    
    public_impl = InvoicesPublicImpl(db=mock_db, repo=mock_repo, service=mock_service)
    
    assert hasattr(public_impl, 'get_invoice')
    assert hasattr(public_impl, 'get_invoices_for_org')
    
    assert callable(public_impl.get_invoice)
    assert callable(public_impl.get_invoices_for_org)
    
    assert public_impl.db == mock_db
    assert public_impl.repo == mock_repo
    assert public_impl.service == mock_service

def test_invoices_public_delegates_to_repository():
    """Test that all public methods correctly delegate to the repository layer"""
    mock_db = Mock()
    mock_repo = Mock()
    mock_service = Mock()
    
    public_impl = InvoicesPublicImpl(db=mock_db, repo=mock_repo, service=mock_service)
    
    invoice_id = uuid4()
    org_id = uuid4()
    limit = 50
    
    mock_invoice = Mock()
    mock_repo.get.return_value = mock_invoice
    
    result = public_impl.get_invoice(invoice_id)
    
    assert result == mock_invoice
    mock_repo.get.assert_called_once_with(invoice_id)
    
    mock_repo.reset_mock()
    mock_invoices_list = [Mock(), Mock(), Mock()]
    mock_repo.list_for_org.return_value = mock_invoices_list
    
    result = public_impl.get_invoices_for_org(org_id, limit=limit)
    
    assert result == mock_invoices_list
    mock_repo.list_for_org.assert_called_once_with(organization_id=org_id, limit=limit)