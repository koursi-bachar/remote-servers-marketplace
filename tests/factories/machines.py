from factories.users import create_user_by_role, auth_headers_by_role
from test_config import TestConfig


def machine_payload(**overrides):
    base = {
        "name": TestConfig.DEFAULT_MACHINE_NAME,
        "cpu": "4 vCPU",
        "ram": "16 GB", 
        "storage": "200 GB",
    }
    base.update(overrides)
    return base

def machine_payload(provider_id, **overrides):
    base = {
        "hostname": TestConfig.DEFAULT_MACHINE_HOSTNAME,
        "location_region": TestConfig.DEFAULT_MACHINE_REGION,
        "gpu_model": TestConfig.DEFAULT_MACHINE_GPU_MODEL,
        "gpu_count": TestConfig.DEFAULT_MACHINE_GPU_COUNT,
        "vram_gb": TestConfig.DEFAULT_MACHINE_VRAM_GB,
        "cpu_model": TestConfig.DEFAULT_MACHINE_CPU_MODEL,
        "cpu_cores": TestConfig.DEFAULT_MACHINE_CPU_CORES,
        "ram_gb": TestConfig.DEFAULT_MACHINE_RAM_GB,
        "storage_gb": TestConfig.DEFAULT_MACHINE_STORAGE_GB,
        "network_mbps": TestConfig.DEFAULT_MACHINE_NETWORK_MBPS,
        "provider_id": str(provider_id),
        "notes": None,
    }
    base.update(overrides)
    return base

def create_machine(client, db_session, provider_role="provider", **overrides):
    """
    Create machine using config-based provider
    """
    provider_user = create_user_by_role(db_session, provider_role)
    
    # Ensure provider has a verified profile
    from app.providers.models import ProviderProfile, ProviderVerificationStatus
    profile = db_session.query(ProviderProfile).filter(ProviderProfile.user_id == provider_user.id).first()
    if not profile:
        profile = ProviderProfile(
            user_id=provider_user.id,
            verification_status=ProviderVerificationStatus.VERIFIED,
            payout_account_ref="test_payout_ref"
        )
        db_session.add(profile)
    else:
        profile.verification_status = ProviderVerificationStatus.VERIFIED
    db_session.commit()
    
    # The provider_id will be converted to string in machine_payload
    payload = machine_payload(provider_id=provider_user.id, **overrides)
    
    # Debug: print the final payload to verify all UUIDs are strings
    print(f"Machine payload: {payload}")
    
    resp = client.post(
        "/api/v1/machines/",
        json=payload,
        headers=auth_headers_by_role(provider_role),
    )
    assert resp.status_code == 201
    return resp.json()

def valid_machine_payload(**overrides):
    """Return a valid machine payload for testing."""
    return machine_payload(**overrides)