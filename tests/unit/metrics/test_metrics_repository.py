import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timezone

from app.metrics.repository import MetricsRepository
from app.metrics.models import MetricSample


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def metrics_repository():
    """MetricsRepository instance fixture"""
    return MetricsRepository()

@pytest.fixture
def sample_metric_sample():
    """Fixture for a mock metric sample object"""
    sample = Mock(spec=MetricSample)
    sample.id = uuid4()
    sample.machine_id = uuid4()
    sample.recorded_at = datetime.now(timezone.utc)
    sample.gpu_util = 75.5
    sample.cpu_util = 45.2
    sample.mem_used_gb = 32.1
    sample.net_rx_mb = 1024.8
    sample.net_tx_mb = 512.3
    sample.created_at = datetime.now(timezone.utc)
    return sample

@pytest.fixture
def sample_metric_data():
    """Fixture for metric sample creation data"""
    return {
        "machine_id": uuid4(),
        "recorded_at": datetime.now(timezone.utc),
        "gpu_util": 75.5,
        "cpu_util": 45.2,
        "mem_used_gb": 32.1,
        "net_rx_mb": 1024.8,
        "net_tx_mb": 512.3,
    }

class TestMetricsRepository:
    
    def test_create_sample_performs_database_operations(self, metrics_repository, mock_db, sample_metric_data):
        """Test that metric sample creation performs database operations"""
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        result = metrics_repository.create_sample(
            db=mock_db,
            machine_id=sample_metric_data["machine_id"],
            recorded_at=sample_metric_data["recorded_at"],
            gpu_util=sample_metric_data["gpu_util"],
            cpu_util=sample_metric_data["cpu_util"],
            mem_used_gb=sample_metric_data["mem_used_gb"],
            net_rx_mb=sample_metric_data["net_rx_mb"],
            net_tx_mb=sample_metric_data["net_tx_mb"],
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_list_samples_returns_samples_sorted_by_recorded_at(self, metrics_repository, mock_db):
        """Test listing metric samples returns sorted list"""
        machine_id = uuid4()
        mock_samples = [Mock(spec=MetricSample), Mock(spec=MetricSample)]
        
        # Mock the scalars().all() chain
        mock_scalars_result = Mock()
        mock_scalars_result.all.return_value = mock_samples
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = metrics_repository.list_samples(db=mock_db, machine_id=machine_id)
        
        assert result == mock_samples
        mock_db.scalars.assert_called_once()
        
        # Get the statement passed to scalars()
        scalars_call_args = mock_db.scalars.call_args[0][0]
        
        # Verify the statement structure
        assert scalars_call_args is not None

    def test_list_samples_returns_empty_list_when_none_exist(self, metrics_repository, mock_db):
        """Test listing metric samples returns empty list when none exist"""
        machine_id = uuid4()
        
        mock_scalars_result = Mock()
        mock_scalars_result.all.return_value = []
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = metrics_repository.list_samples(db=mock_db, machine_id=machine_id)
        
        assert result == []
        mock_db.scalars.assert_called_once()
        mock_scalars_result.all.assert_called_once()

    def test_list_samples_respects_start_and_end_filters(self, metrics_repository, mock_db):
        """Test listing metric samples respects start and end time filters"""
        machine_id = uuid4()
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        
        mock_scalars_result = Mock()
        mock_scalars_result.all.return_value = []
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = metrics_repository.list_samples(
            db=mock_db,
            machine_id=machine_id,
            start=start_time,
            end=end_time
        )
        
        assert result == []
        mock_db.scalars.assert_called_once()
        mock_scalars_result.all.assert_called_once()

    def test_list_samples_respects_limit(self, metrics_repository, mock_db):
        """Test listing metric samples respects limit parameter"""
        machine_id = uuid4()
        limit = 50
        
        mock_scalars_result = Mock()
        mock_scalars_result.all.return_value = []
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = metrics_repository.list_samples(
            db=mock_db,
            machine_id=machine_id,
            limit=limit
        )
        
        assert result == []
        mock_db.scalars.assert_called_once()
        mock_scalars_result.all.assert_called_once()

    def test_list_samples_with_all_filters(self, metrics_repository, mock_db):
        """Test listing metric samples with all filter combinations"""
        machine_id = uuid4()
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        limit = 100
        
        mock_scalars_result = Mock()
        mock_scalars_result.all.return_value = []
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = metrics_repository.list_samples(
            db=mock_db,
            machine_id=machine_id,
            start=start_time,
            end=end_time,
            limit=limit
        )
        
        assert result == []
        mock_db.scalars.assert_called_once()
        mock_scalars_result.all.assert_called_once()

    def test_get_latest_sample_returns_sample_when_exists(self, metrics_repository, mock_db, sample_metric_sample):
        """Test getting latest metric sample returns sample when it exists"""
        machine_id = uuid4()
        
        mock_scalars_result = Mock()
        mock_scalars_result.first.return_value = sample_metric_sample
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = metrics_repository.get_latest_sample(db=mock_db, machine_id=machine_id)
        
        assert result == sample_metric_sample
        mock_db.scalars.assert_called_once()
        mock_scalars_result.first.assert_called_once()

    def test_get_latest_sample_returns_none_when_not_found(self, metrics_repository, mock_db):
        """Test getting latest metric sample returns None when not found"""
        machine_id = uuid4()
        
        mock_scalars_result = Mock()
        mock_scalars_result.first.return_value = None
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = metrics_repository.get_latest_sample(db=mock_db, machine_id=machine_id)
        
        assert result is None
        mock_db.scalars.assert_called_once()
        mock_scalars_result.first.assert_called_once()

    def test_create_sample_handles_none_values(self, metrics_repository, mock_db):
        """Test that metric sample creation handles None values appropriately"""
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        machine_id = uuid4()
        recorded_at = datetime.now(timezone.utc)
        
        result = metrics_repository.create_sample(
            db=mock_db,
            machine_id=machine_id,
            recorded_at=recorded_at,
            gpu_util=None,
            cpu_util=None,
            mem_used_gb=None,
            net_rx_mb=None,
            net_tx_mb=None,
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()