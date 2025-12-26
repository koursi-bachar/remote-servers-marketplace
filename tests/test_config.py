"""
Centralized test configuration for modularizing our test data.
"""

class TestConfig:
    # Base URLs
    BASE_URL = "/api/v1"
    
    # User credentials by role
    ADMIN_EMAIL = "admin@example.com"
    ADMIN_PASSWORD = "admin"
    
    PROVIDER_EMAIL = "provider@example.com"
    PROVIDER_PASSWORD = "provider"
    
    BUYER_EMAIL = "buyer@example.com" 
    BUYER_PASSWORD = "buyer"
    
    # Additional test users for scenarios needing multiple users
    SECOND_BUYER_EMAIL = "two_buyer@example.com"
    SECOND_PROVIDER_EMAIL = "two_provider@example.com"
    
    # Default test data
    DEFAULT_LISTING_TITLE = "Default Title"
    DEFAULT_LISTING_PRICE = 10
    DEFAULT_MACHINE_NAME = "Test Machine"

    # Default machine data
    DEFAULT_MACHINE_HOSTNAME = "test-machine"
    DEFAULT_MACHINE_REGION = "us-west"
    DEFAULT_MACHINE_GPU_MODEL = "RTX 4090"
    DEFAULT_MACHINE_GPU_COUNT = 1
    DEFAULT_MACHINE_VRAM_GB = 24
    DEFAULT_MACHINE_CPU_MODEL = "Intel i9"
    DEFAULT_MACHINE_CPU_CORES = 8
    DEFAULT_MACHINE_RAM_GB = 16
    DEFAULT_MACHINE_STORAGE_GB = 500
    DEFAULT_MACHINE_NETWORK_MBPS = 1000


def get_email_by_role(role: str) -> str:
    """Get a standardized email for a given role."""
    role_map = {
        "admin": TestConfig.ADMIN_EMAIL,
        "provider": TestConfig.PROVIDER_EMAIL,
        "buyer": TestConfig.BUYER_EMAIL,
    }
    return role_map.get(role.lower(), TestConfig.BUYER_EMAIL)