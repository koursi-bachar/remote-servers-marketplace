import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime, timezone

from app.machines.public import MachinesPublic

from app.metrics.service import MetricsService
from app.metrics.repository import MetricsRepository
from app.metrics.schemas import MetricSampleCreate, MetricSampleRead, MetricSampleListItem, MetricsQueryParams
from app.metrics.models import MetricSample


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def mock_repository():
    """Mock MetricsRepository fixture"""
    return Mock(spec=MetricsRepository)

@pytest.fixture
def mock_machines_public():
    """Mock MachinesPublic fixture"""
    return Mock(spec=MachinesPublic)

@pytest.fixture
def metrics_service(mock_db, mock_repository, mock_machines_public):
    """MetricsService fixture with all dependencies"""
    return MetricsService(
        db=mock_db,
        repo=mock_repository,
        machines_public=mock_machines_public
    )

@pytest.fixture
def sample_machine():
    """Fixture for a mock machine object"""
    machine = Mock()
    machine.id = uuid4()
    machine.provider_id = uuid4()
    return machine

@pytest.fixture
def sample_metric_sample():
    """Fixture for a mock MetricSample object"""
    sample = Mock(spec=MetricSample)
    sample.id = uuid4()
    sample.machine_id = uuid4()
    sample.recorded_at = datetime.now(timezone.utc)
    sample.gpu_util = 75.5
    sample.cpu_util = 65.2
    sample.mem_used_gb = 16.8
    sample.net_rx_mb = 1024.5
    sample.net_tx_mb = 512.3
    return sample

@pytest.fixture
def sample_metric_sample_create():
    """Fixture for sample metric creation data"""
    return MetricSampleCreate(
        recorded_at=datetime.now(timezone.utc),
        gpu_util=75.5,
        cpu_util=65.2,
        mem_used_gb=16.8,
        net_rx_mb=1024.5,
        net_tx_mb=512.3
    )

@pytest.fixture
def sample_metrics_query_params():
    """Fixture for metrics query parameters"""
    return MetricsQueryParams(
        start=datetime.now(timezone.utc),
        end=datetime.now(timezone.utc),
        limit=100
    )

@pytest.fixture
def sample_raw_metrics():
    """Fixture for raw metrics data"""
    return {
        "collected_at": datetime.now(timezone.utc),
        "gpu_util": 75.5,
        "cpu_util": 65.2,
        "mem_gb": 16.8
    }

class TestMetricsService:
    
    def test_ingest_metrics_successfully_creates_sample(self, metrics_service, mock_db, mock_repository, mock_machines_public, sample_machine, sample_metric_sample_create, sample_metric_sample):
        """Test successful metric ingestion when provider owns machine"""
        machine_id = uuid4()
        provider_id = uuid4()
        sample_machine.id = machine_id
        sample_machine.provider_id = provider_id
        
        mock_machines_public.get_machine.return_value = sample_machine
        mock_machines_public.provider_owns_machine.return_value = True
        mock_repository.create_sample.return_value = sample_metric_sample
        
        with patch.object(MetricSampleRead, 'model_validate', return_value=Mock(spec=MetricSampleRead)) as mock_validate:
            result = metrics_service.ingest_metrics(machine_id, sample_metric_sample_create, provider_id)
        
        mock_machines_public.get_machine.assert_called_once_with(machine_id)
        mock_machines_public.provider_owns_machine.assert_called_once_with(
            provider_id=provider_id,
            machine_id=machine_id
        )
        mock_repository.create_sample.assert_called_once()
        assert isinstance(result, Mock)

    def test_ingest_metrics_raises_error_when_machine_not_found(self, metrics_service, mock_machines_public, sample_metric_sample_create):
        """Test metric ingestion fails when machine doesn't exist"""
        machine_id = uuid4()
        provider_id = uuid4()
        
        mock_machines_public.get_machine.return_value = None
        
        with pytest.raises(ValueError, match="Machine does not exist."):
            metrics_service.ingest_metrics(machine_id, sample_metric_sample_create, provider_id)
        
        mock_machines_public.get_machine.assert_called_once_with(machine_id)
        mock_machines_public.provider_owns_machine.assert_not_called()

    def test_ingest_metrics_raises_permission_error_when_not_machine_owner(self, metrics_service, mock_machines_public, sample_machine, sample_metric_sample_create):
        """Test metric ingestion fails when provider doesn't own machine"""
        machine_id = uuid4()
        provider_id = uuid4()
        different_provider_id = uuid4()
        
        sample_machine.id = machine_id
        sample_machine.provider_id = provider_id
        mock_machines_public.get_machine.return_value = sample_machine
        mock_machines_public.provider_owns_machine.return_value = False
        
        with pytest.raises(PermissionError, match="User does not own machine."):
            metrics_service.ingest_metrics(machine_id, sample_metric_sample_create, different_provider_id)
        
        mock_machines_public.get_machine.assert_called_once_with(machine_id)
        mock_machines_public.provider_owns_machine.assert_called_once_with(
            provider_id=different_provider_id,
            machine_id=machine_id
        )

    def test_ingest_metrics_uses_current_time_when_recorded_at_not_provided(self, metrics_service, mock_db, mock_repository, mock_machines_public, sample_machine, sample_metric_sample):
        """Test metric ingestion uses current time when recorded_at is not provided"""
        machine_id = uuid4()
        provider_id = uuid4()
        sample_machine.id = machine_id
        sample_machine.provider_id = provider_id
        
        mock_machines_public.get_machine.return_value = sample_machine
        mock_machines_public.provider_owns_machine.return_value = True
        mock_repository.create_sample.return_value = sample_metric_sample
        
        sample_without_time = MetricSampleCreate(
            recorded_at=None,
            gpu_util=75.5,
            cpu_util=65.2,
            mem_used_gb=16.8,
            net_rx_mb=1024.5,
            net_tx_mb=512.3
        )
        
        with patch.object(MetricSampleRead, 'model_validate', return_value=Mock(spec=MetricSampleRead)):
            metrics_service.ingest_metrics(machine_id, sample_without_time, provider_id)
        
        mock_repository.create_sample.assert_called_once()
        call_args = mock_repository.create_sample.call_args
        assert call_args[1]['recorded_at'] is not None

    def test_ingest_raw_metrics_converts_and_delegates(self, metrics_service, mock_machines_public, sample_machine, sample_raw_metrics):
        """Test raw metric ingestion converts to MetricSampleCreate and delegates"""
        machine_id = uuid4()
        provider_id = uuid4()
        sample_machine.id = machine_id
        sample_machine.provider_id = provider_id
        
        mock_machines_public.get_machine.return_value = sample_machine
        mock_machines_public.provider_owns_machine.return_value = True
        
        with patch.object(metrics_service, 'ingest_metrics', return_value=Mock(spec=MetricSampleRead)) as mock_ingest:
            result = metrics_service.ingest_raw_metrics(machine_id, sample_raw_metrics, provider_id)
        
        # Verify ingest_metrics was called once
        assert mock_ingest.call_count == 1
        
        # Get the call arguments
        call_args = mock_ingest.call_args
        assert call_args is not None
        
        # Check keyword arguments
        kwargs = call_args[1]  # Keyword arguments dict
        assert kwargs['machine_id'] == machine_id
        assert kwargs['provider_id'] == provider_id
        
        # Check the payload
        payload = kwargs['payload']
        assert isinstance(payload, MetricSampleCreate)
        assert payload.gpu_util == sample_raw_metrics["gpu_util"]
        assert payload.cpu_util == sample_raw_metrics["cpu_util"]
        assert payload.mem_used_gb == sample_raw_metrics["mem_gb"]
        assert payload.recorded_at == sample_raw_metrics["collected_at"]
        
        assert result == mock_ingest.return_value

    def test_list_machine_metrics_returns_samples_when_machine_exists(self, metrics_service, mock_db, mock_repository, mock_machines_public, sample_machine, sample_metric_sample, sample_metrics_query_params):
        """Test listing metrics returns samples when machine exists"""
        machine_id = uuid4()
        sample_machine.id = machine_id
        
        mock_machines_public.get_machine.return_value = sample_machine
        mock_repository.list_samples.return_value = [sample_metric_sample]
        
        mock_list_item = Mock(spec=MetricSampleListItem)
        with patch.object(MetricSampleListItem, 'model_validate', return_value=mock_list_item):
            result = metrics_service.list_machine_metrics(machine_id, sample_metrics_query_params)
        
        mock_machines_public.get_machine.assert_called_once_with(machine_id)
        mock_repository.list_samples.assert_called_once_with(
            mock_db,
            machine_id=machine_id,
            start=sample_metrics_query_params.start,
            end=sample_metrics_query_params.end,
            limit=sample_metrics_query_params.limit
        )
        assert len(result) == 1
        assert result[0] == mock_list_item

    def test_list_machine_metrics_raises_error_when_machine_not_found(self, metrics_service, mock_machines_public, sample_metrics_query_params):
        """Test listing metrics fails when machine doesn't exist"""
        machine_id = uuid4()
        
        mock_machines_public.get_machine.return_value = None
        
        with pytest.raises(ValueError, match="Machine does not exist."):
            metrics_service.list_machine_metrics(machine_id, sample_metrics_query_params)
        
        mock_machines_public.get_machine.assert_called_once_with(machine_id)

    def test_list_machine_metrics_returns_empty_list_when_no_samples(self, metrics_service, mock_db, mock_repository, mock_machines_public, sample_machine, sample_metrics_query_params):
        """Test listing metrics returns empty list when no samples exist"""
        machine_id = uuid4()
        sample_machine.id = machine_id
        
        mock_machines_public.get_machine.return_value = sample_machine
        mock_repository.list_samples.return_value = []
        
        result = metrics_service.list_machine_metrics(machine_id, sample_metrics_query_params)
        
        mock_machines_public.get_machine.assert_called_once_with(machine_id)
        mock_repository.list_samples.assert_called_once_with(
            mock_db,
            machine_id=machine_id,
            start=sample_metrics_query_params.start,
            end=sample_metrics_query_params.end,
            limit=sample_metrics_query_params.limit
        )
        assert result == []

    def test_get_latest_metrics_returns_sample_when_exists(self, metrics_service, mock_db, mock_repository, mock_machines_public, sample_machine, sample_metric_sample):
        """Test getting latest metrics returns sample when exists"""
        machine_id = uuid4()
        sample_machine.id = machine_id
        
        mock_machines_public.get_machine.return_value = sample_machine
        mock_repository.get_latest_sample.return_value = sample_metric_sample
        
        mock_sample_read = Mock(spec=MetricSampleRead)
        with patch.object(MetricSampleRead, 'model_validate', return_value=mock_sample_read):
            result = metrics_service.get_latest_metrics(machine_id)
        
        mock_machines_public.get_machine.assert_called_once_with(machine_id)
        mock_repository.get_latest_sample.assert_called_once_with(mock_db, machine_id)
        assert result == mock_sample_read

    def test_get_latest_metrics_returns_none_when_no_samples(self, metrics_service, mock_db, mock_repository, mock_machines_public, sample_machine):
        """Test getting latest metrics returns None when no samples exist"""
        machine_id = uuid4()
        sample_machine.id = machine_id
        
        mock_machines_public.get_machine.return_value = sample_machine
        mock_repository.get_latest_sample.return_value = None
        
        result = metrics_service.get_latest_metrics(machine_id)
        
        mock_machines_public.get_machine.assert_called_once_with(machine_id)
        mock_repository.get_latest_sample.assert_called_once_with(mock_db, machine_id)
        assert result is None

    def test_get_latest_metrics_raises_error_when_machine_not_found(self, metrics_service, mock_machines_public):
        """Test getting latest metrics fails when machine doesn't exist"""
        machine_id = uuid4()
        
        mock_machines_public.get_machine.return_value = None
        
        with pytest.raises(ValueError, match="Machine does not exist."):
            metrics_service.get_latest_metrics(machine_id)
        
        mock_machines_public.get_machine.assert_called_once_with(machine_id)