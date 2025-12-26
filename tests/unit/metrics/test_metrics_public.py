import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.metrics.public import MetricsPublicImpl


def test_metrics_public_implements_protocol():
    """Test that MetricsPublicImpl properly implements the MetricsPublic protocol"""
    mock_service = Mock()
    
    public_impl = MetricsPublicImpl(service=mock_service)
    
    assert hasattr(public_impl, 'get_latest_metrics')
    assert hasattr(public_impl, 'list_metrics_for_machine')
    assert hasattr(public_impl, 'ingest_raw_metrics')
    
    assert callable(public_impl.get_latest_metrics)
    assert callable(public_impl.list_metrics_for_machine)
    assert callable(public_impl.ingest_raw_metrics)

    assert public_impl.service == mock_service

def test_metrics_public_delegates_to_service():
    """Test that all public methods correctly delegate to the service layer"""
    mock_service = Mock()
    
    public_impl = MetricsPublicImpl(service=mock_service)
    
    machine_id = uuid4()
    provider_id = uuid4()
    
    mock_latest_metric = Mock()
    mock_service.get_latest_metrics.return_value = mock_latest_metric
    
    result = public_impl.get_latest_metrics(machine_id)
    
    assert result == mock_latest_metric
    mock_service.get_latest_metrics.assert_called_once_with(machine_id)
    
    mock_service.reset_mock()
    mock_query = Mock()
    mock_metrics_list = [Mock(), Mock(), Mock()]
    mock_service.list_machine_metrics.return_value = mock_metrics_list
    
    result = public_impl.list_metrics_for_machine(machine_id, mock_query)
    
    assert result == mock_metrics_list
    mock_service.list_machine_metrics.assert_called_once_with(machine_id, mock_query)
    
    mock_service.reset_mock()
    raw_metrics = {"cpu": 75.5, "gpu": 80.2}
    mock_service.ingest_raw_metrics.return_value = None
    
    result = public_impl.ingest_raw_metrics(machine_id, raw_metrics, provider_id)
    
    assert result is None
    mock_service.ingest_raw_metrics.assert_called_once_with(machine_id, raw_metrics, provider_id)