import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.benchmarks.public import BenchmarksPublicImpl


def test_benchmarks_public_implements_protocol():
    """Test that BenchmarksPublicImpl properly implements the BenchmarksPublic protocol"""
    mock_service = Mock()
    
    public_impl = BenchmarksPublicImpl(service=mock_service)
    
    assert hasattr(public_impl, 'get_benchmarks_for_machine')
    assert hasattr(public_impl, 'get_benchmarks_for_listing')
    
    assert callable(public_impl.get_benchmarks_for_machine)
    assert callable(public_impl.get_benchmarks_for_listing)
    
    assert public_impl.service == mock_service

def test_benchmarks_public_delegates_to_service():
    """Test that all public methods correctly delegate to the service layer"""
    mock_service = Mock()
    
    public_impl = BenchmarksPublicImpl(service=mock_service)
    
    machine_id = uuid4()
    listing_id = uuid4()
    
    mock_machine_benchmarks = [Mock(), Mock(), Mock()]
    mock_service.list_machine_benchmarks.return_value = mock_machine_benchmarks
    
    result = public_impl.get_benchmarks_for_machine(machine_id)
    
    assert result == mock_machine_benchmarks
    mock_service.list_machine_benchmarks.assert_called_once_with(machine_id)
    
    mock_service.reset_mock()
    mock_listing_benchmarks = [Mock(), Mock()]
    mock_service.list_listing_benchmarks.return_value = mock_listing_benchmarks
    
    result = public_impl.get_benchmarks_for_listing(listing_id)
    
    assert result == mock_listing_benchmarks
    mock_service.list_listing_benchmarks.assert_called_once_with(listing_id)