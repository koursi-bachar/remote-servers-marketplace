import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.benchmarks.service import BenchmarkService
from app.benchmarks.repository import BenchmarksRepository
from app.benchmarks.schemas import BenchmarkCreate, BenchmarkRead
from app.machines.public import MachinesPublic


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def mock_repository():
    """Mock BenchmarksRepository fixture"""
    return Mock(spec=BenchmarksRepository)

@pytest.fixture
def mock_machines_public():
    """Mock MachinesPublic fixture"""
    return Mock(spec=MachinesPublic)

@pytest.fixture
def benchmark_service(mock_repository, mock_machines_public, mock_db):
    """BenchmarkService fixture with all dependencies"""
    return BenchmarkService(
        db=mock_db,
        repo=mock_repository,
        machines_public=mock_machines_public
    )

@pytest.fixture
def sample_machine_id():
    """Fixture for a machine ID"""
    return uuid4()

@pytest.fixture
def sample_provider_id():
    """Fixture for a provider ID"""
    return uuid4()

@pytest.fixture
def sample_listing_id():
    """Fixture for a listing ID"""
    return uuid4()

@pytest.fixture
def sample_benchmark_create():
    """Fixture for a BenchmarkCreate object"""
    return Mock(spec=BenchmarkCreate)

@pytest.fixture
def sample_benchmark_read():
    """Fixture for a BenchmarkRead object"""
    benchmark = Mock(spec=BenchmarkRead)
    benchmark.id = uuid4()
    benchmark.machine_id = uuid4()
    benchmark.name = "Test Benchmark"
    benchmark.score = "95.5"
    return benchmark

@pytest.fixture
def sample_benchmark_list():
    """Fixture for a list of BenchmarkRead objects"""
    benchmarks = []
    for i in range(3):
        benchmark = Mock(spec=BenchmarkRead)
        benchmark.id = uuid4()
        benchmark.machine_id = uuid4()
        benchmark.name = f"Benchmark {i}"
        benchmark.score = f"{90 + i}.5"
        benchmarks.append(benchmark)
    return benchmarks

class TestBenchmarkService:
    
    def test_create_benchmark_successfully_creates_benchmark(self, benchmark_service, mock_db, mock_repository, mock_machines_public, sample_machine_id, sample_provider_id, sample_benchmark_read):
        """Test successful benchmark creation"""
        mock_machines_public.provider_owns_machine.return_value = True
        mock_repository.create.return_value = sample_benchmark_read
        
        result = benchmark_service.create_benchmark(
            machine_id=sample_machine_id,
            provider_id=sample_provider_id,
            name="Test Benchmark",
            score="95.5",
            methodology_uri="https://example.com/methodology",
            artifact_uri="https://example.com/artifact"
        )
        
        mock_machines_public.provider_owns_machine.assert_called_once_with(sample_provider_id, sample_machine_id)
        mock_repository.create.assert_called_once()
        call_args = mock_repository.create.call_args
        assert call_args[0][0] == mock_db
        assert call_args[0][1] == sample_machine_id
        assert isinstance(call_args[0][2], BenchmarkCreate)
        assert call_args[0][2].name == "Test Benchmark"
        assert call_args[0][2].score == "95.5"
        assert str(call_args[0][2].methodology_uri) == "https://example.com/methodology"
        assert str(call_args[0][2].artifact_uri) == "https://example.com/artifact"
        assert result == sample_benchmark_read
    
    def test_create_benchmark_raises_permission_error_when_not_owner(self, benchmark_service, mock_machines_public, sample_machine_id, sample_provider_id):
        """Test benchmark creation raises PermissionError when provider doesn't own machine"""
        mock_machines_public.provider_owns_machine.return_value = False
        
        with pytest.raises(PermissionError, match="User does not own this machine"):
            benchmark_service.create_benchmark(
                machine_id=sample_machine_id,
                provider_id=sample_provider_id,
                name="Test Benchmark",
                score="95.5"
            )
        
        mock_machines_public.provider_owns_machine.assert_called_once_with(sample_provider_id, sample_machine_id)
    
    def test_create_benchmark_handles_optional_parameters(self, benchmark_service, mock_db, mock_repository, mock_machines_public, sample_machine_id, sample_provider_id, sample_benchmark_read):
        """Test benchmark creation with optional parameters omitted"""
        mock_machines_public.provider_owns_machine.return_value = True
        mock_repository.create.return_value = sample_benchmark_read
        
        result = benchmark_service.create_benchmark(
            machine_id=sample_machine_id,
            provider_id=sample_provider_id,
            name="Test Benchmark",
            score="95.5"
        )
        
        mock_machines_public.provider_owns_machine.assert_called_once_with(sample_provider_id, sample_machine_id)
        mock_repository.create.assert_called_once()
        call_args = mock_repository.create.call_args
        assert call_args[0][0] == mock_db
        assert call_args[0][1] == sample_machine_id
        assert isinstance(call_args[0][2], BenchmarkCreate)
        assert call_args[0][2].name == "Test Benchmark"
        assert call_args[0][2].score == "95.5"
        assert call_args[0][2].methodology_uri is None
        assert call_args[0][2].artifact_uri is None
        assert result == sample_benchmark_read
    
    def test_list_machine_benchmarks_delegates_to_repository(self, benchmark_service, mock_db, mock_repository, sample_machine_id, sample_benchmark_list):
        """Test listing machine benchmarks delegates to repository"""
        mock_repository.list_for_machine.return_value = sample_benchmark_list
        
        result = benchmark_service.list_machine_benchmarks(sample_machine_id)
        
        mock_repository.list_for_machine.assert_called_once_with(mock_db, sample_machine_id)
        assert result == sample_benchmark_list
    
    def test_list_machine_benchmarks_returns_empty_list_when_no_benchmarks(self, benchmark_service, mock_db, mock_repository, sample_machine_id):
        """Test listing machine benchmarks returns empty list when none exist"""
        mock_repository.list_for_machine.return_value = []
        
        result = benchmark_service.list_machine_benchmarks(sample_machine_id)
        
        mock_repository.list_for_machine.assert_called_once_with(mock_db, sample_machine_id)
        assert result == []
    
    def test_list_listing_benchmarks_delegates_to_repository(self, benchmark_service, mock_db, mock_repository, sample_listing_id, sample_benchmark_list):
        """Test listing listing benchmarks delegates to repository"""
        mock_repository.list_for_listing.return_value = sample_benchmark_list
        
        result = benchmark_service.list_listing_benchmarks(sample_listing_id)
        
        mock_repository.list_for_listing.assert_called_once_with(mock_db, sample_listing_id)
        assert result == sample_benchmark_list
    
    def test_list_listing_benchmarks_returns_empty_list_when_no_benchmarks(self, benchmark_service, mock_db, mock_repository, sample_listing_id):
        """Test listing listing benchmarks returns empty list when none exist"""
        mock_repository.list_for_listing.return_value = []
        
        result = benchmark_service.list_listing_benchmarks(sample_listing_id)
        
        mock_repository.list_for_listing.assert_called_once_with(mock_db, sample_listing_id)
        assert result == []
    
    def test_create_benchmark_propagates_repository_exception(self, benchmark_service, mock_machines_public, mock_repository, sample_machine_id, sample_provider_id):
        """Test benchmark creation propagates repository exceptions"""
        mock_machines_public.provider_owns_machine.return_value = True
        mock_repository.create.side_effect = ValueError("Database error")
        
        with pytest.raises(ValueError, match="Database error"):
            benchmark_service.create_benchmark(
                machine_id=sample_machine_id,
                provider_id=sample_provider_id,
                name="Test Benchmark",
                score="95.5"
            )
        
        mock_machines_public.provider_owns_machine.assert_called_once_with(sample_provider_id, sample_machine_id)
    
    def test_list_machine_benchmarks_propagates_repository_exception(self, benchmark_service, mock_repository, sample_machine_id):
        """Test listing machine benchmarks propagates repository exceptions"""
        mock_repository.list_for_machine.side_effect = ValueError("Database error")
        
        with pytest.raises(ValueError, match="Database error"):
            benchmark_service.list_machine_benchmarks(sample_machine_id)
        
        mock_repository.list_for_machine.assert_called_once()
    
    def test_list_listing_benchmarks_propagates_repository_exception(self, benchmark_service, mock_repository, sample_listing_id):
        """Test listing listing benchmarks propagates repository exceptions"""
        mock_repository.list_for_listing.side_effect = ValueError("Database error")
        
        with pytest.raises(ValueError, match="Database error"):
            benchmark_service.list_listing_benchmarks(sample_listing_id)
        
        mock_repository.list_for_listing.assert_called_once()