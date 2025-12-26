import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.listings.public import ListingsPublicImpl


def test_listings_public_implements_protocol():
    """Test that ListingsPublicImpl properly implements the ListingsPublic protocol"""
    #Verify all protocol methods exist and are callable
    mock_service = Mock()
    public_impl = ListingsPublicImpl(mock_service)
    
    #Verify all protocol methods exist and are callable
    assert hasattr(public_impl, 'create_listing')
    assert hasattr(public_impl, 'get_listing_by_id')
    assert hasattr(public_impl, 'search_listings_by_name')
    assert hasattr(public_impl, 'list_listings')
    
    #Verify they're callable
    assert callable(public_impl.create_listing)
    assert callable(public_impl.get_listing_by_id)
    assert callable(public_impl.search_listings_by_name)
    assert callable(public_impl.list_listings)

def test_listings_public_delegates_to_service():
    """Test that all public methods correctly delegate to the service layer"""
    mock_service = Mock()
    public_impl = ListingsPublicImpl(mock_service)
    
    #Test data
    provider_id = uuid4()
    listing_id = uuid4()
    mock_listing_payload = Mock()
    mock_listing_result = Mock()
    mock_search_result = [Mock(), Mock()]
    mock_listings_result = [Mock(), Mock(), Mock()]
    
    #Test create_listing delegation
    mock_service.create_listing.return_value = mock_listing_result
    result = public_impl.create_listing(provider_id, mock_listing_payload)
    assert result == mock_listing_result
    mock_service.create_listing.assert_called_once_with(provider_id, mock_listing_payload)
    
    #Reset mock for next test
    mock_service.reset_mock()
    
    #Test get_listing_by_id delegation
    mock_service.get_listing_by_id.return_value = mock_listing_result
    result = public_impl.get_listing_by_id(listing_id)
    assert result == mock_listing_result
    mock_service.get_listing_by_id.assert_called_once_with(listing_id)
    
    #Reset mock for next test
    mock_service.reset_mock()
    
    #Test search_listings_by_name delegation
    search_term = "test search"
    mock_service.search_listings_by_name.return_value = mock_search_result
    result = public_impl.search_listings_by_name(search_term)
    assert result == mock_search_result
    mock_service.search_listings_by_name.assert_called_once_with(search_term)
    
    #Reset mock for next test
    mock_service.reset_mock()
    
    #Test list_listings delegation
    mock_service.list_listings.return_value = mock_listings_result
    result = public_impl.list_listings()
    assert result == mock_listings_result
    mock_service.list_listings.assert_called_once()