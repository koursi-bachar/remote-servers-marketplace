import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timezone

from app.benchmarks.repository import BenchmarksRepository
from app.benchmarks.models import MachineBenchmark
from app.benchmarks.schemas import BenchmarkCreate


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def benchmark_repository():
    """BenchmarksRepository instance fixture"""
    return BenchmarksRepository()

@pytest.fixture
def sample_machine_benchmark():
    """Fixture for a mock machine benchmark object"""
    benchmark = Mock(spec=MachineBenchmark)
    benchmark.id = uuid4()
    benchmark.machine_id = uuid4()
    benchmark.listing_id = uuid4()
    benchmark.name = "3DMark Time Spy"
    benchmark.score = 12500.5
    benchmark.methodology_uri = "https://example.com/methodology.pdf"
    benchmark.artifact_uri = "https://example.com/artifact.zip"
    benchmark.created_at = datetime.now(timezone.utc)
    return benchmark

@pytest.fixture
def sample_benchmark_create():
    """Fixture for benchmark creation data"""
    benchmark_create = Mock(spec=BenchmarkCreate)
    benchmark_create.listing_id = uuid4()
    benchmark_create.name = "Cinebench R23"
    benchmark_create.score = 28500.0
    benchmark_create.methodology_uri = "https://example.com/methodology.pdf"
    benchmark_create.artifact_uri = "https://example.com/artifact.zip"
    return benchmark_create

class TestBenchmarksRepository:
    
    def test_create_performs_database_operations(self, benchmark_repository, mock_db, sample_benchmark_create):
        """Test that benchmark creation performs database operations"""
        machine_id = uuid4()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        result = benchmark_repository.create(
            db=mock_db,
            machine_id=machine_id,
            payload=sample_benchmark_create
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_list_for_machine_returns_benchmarks_sorted_by_created_at(self, benchmark_repository, mock_db):
        """Test listing benchmarks for machine returns sorted list"""
        machine_id = uuid4()
        mock_benchmarks = [Mock(spec=MachineBenchmark), Mock(spec=MachineBenchmark)]
        
        mock_query = Mock()
        filter_result = Mock()
        order_result = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = filter_result
        filter_result.order_by.return_value = order_result
        order_result.all.return_value = mock_benchmarks
        
        result = benchmark_repository.list_for_machine(db=mock_db, machine_id=machine_id)
        
        assert result == mock_benchmarks
        mock_db.query.assert_called_once_with(MachineBenchmark)
        mock_query.filter.assert_called_once()
        filter_result.order_by.assert_called_once()
        order_result.all.assert_called_once()

    def test_list_for_machine_returns_empty_list_when_none_exist(self, benchmark_repository, mock_db):
        """Test listing benchmarks for machine returns empty list when none exist"""
        machine_id = uuid4()
        
        mock_query = Mock()
        filter_result = Mock()
        order_result = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = filter_result
        filter_result.order_by.return_value = order_result
        order_result.all.return_value = []
        
        result = benchmark_repository.list_for_machine(db=mock_db, machine_id=machine_id)
        
        assert result == []
        mock_db.query.assert_called_once_with(MachineBenchmark)
        mock_query.filter.assert_called_once()
        filter_result.order_by.assert_called_once()
        order_result.all.assert_called_once()

    def test_list_for_listing_returns_benchmarks_sorted_by_created_at(self, benchmark_repository, mock_db):
        """Test listing benchmarks for listing returns sorted list"""
        listing_id = uuid4()
        mock_benchmarks = [Mock(spec=MachineBenchmark), Mock(spec=MachineBenchmark)]
        
        mock_query = Mock()
        filter_result = Mock()
        order_result = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = filter_result
        filter_result.order_by.return_value = order_result
        order_result.all.return_value = mock_benchmarks
        
        result = benchmark_repository.list_for_listing(db=mock_db, listing_id=listing_id)
        
        assert result == mock_benchmarks
        mock_db.query.assert_called_once_with(MachineBenchmark)
        mock_query.filter.assert_called_once()
        filter_result.order_by.assert_called_once()
        order_result.all.assert_called_once()

    def test_list_for_listing_returns_empty_list_when_none_exist(self, benchmark_repository, mock_db):
        """Test listing benchmarks for listing returns empty list when none exist"""
        listing_id = uuid4()
        
        mock_query = Mock()
        filter_result = Mock()
        order_result = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = filter_result
        filter_result.order_by.return_value = order_result
        order_result.all.return_value = []
        
        result = benchmark_repository.list_for_listing(db=mock_db, listing_id=listing_id)
        
        assert result == []
        mock_db.query.assert_called_once_with(MachineBenchmark)
        mock_query.filter.assert_called_once()
        filter_result.order_by.assert_called_once()
        order_result.all.assert_called_once()

    def test_create_with_none_uris_handles_properly(self, benchmark_repository, mock_db):
        """Test that benchmark creation handles None URIs appropriately"""
        machine_id = uuid4()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        benchmark_create = Mock(spec=BenchmarkCreate)
        benchmark_create.listing_id = uuid4()
        benchmark_create.name = "Geekbench 6"
        benchmark_create.score = 2500.0
        benchmark_create.methodology_uri = None
        benchmark_create.artifact_uri = None
        
        result = benchmark_repository.create(
            db=mock_db,
            machine_id=machine_id,
            payload=benchmark_create
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_with_string_uris_converts_properly(self, benchmark_repository, mock_db):
        """Test that benchmark creation converts string URIs properly"""
        machine_id = uuid4()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        benchmark_create = Mock(spec=BenchmarkCreate)
        benchmark_create.listing_id = uuid4()
        benchmark_create.name = "Blender Benchmark"
        benchmark_create.score = 350.5
        methodology_uri = "https://example.com/methodology"
        artifact_uri = "https://example.com/artifact"
        benchmark_create.methodology_uri = methodology_uri
        benchmark_create.artifact_uri = artifact_uri
        
        result = benchmark_repository.create(
            db=mock_db,
            machine_id=machine_id,
            payload=benchmark_create
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_handles_different_data_types(self, benchmark_repository, mock_db):
        """Test that benchmark creation handles different data types in the payload"""
        machine_id = uuid4()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        benchmark_create = Mock(spec=BenchmarkCreate)
        benchmark_create.listing_id = uuid4()
        benchmark_create.name = "Minimal Benchmark"
        benchmark_create.score = 100.0
        benchmark_create.methodology_uri = None
        benchmark_create.artifact_uri = None
        
        result = benchmark_repository.create(
            db=mock_db,
            machine_id=machine_id,
            payload=benchmark_create
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()