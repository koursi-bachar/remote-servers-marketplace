from dataclasses import dataclass
from uuid import UUID
from datetime import datetime, timezone


@dataclass
class AgentProvisionResult:
    """
    Represents the agent's response when provisioning access.
    For our use csae:
    - the VPN config file
    - a generated SSH user or key fingerprint
    """
    vpn_config_uri: str
    ssh_public_key_fingerprint: str

class ProviderAgentClient:
    """
    This describes what operations the provider agent must support.
    """
    def provision_access(self, *, booking_id: UUID, user_id: UUID, machine_id: UUID) -> AgentProvisionResult:
        """
        Provision VPN and SSH credentials for a user on a machine.
        """
        mock_vpn_uri = f"s3://mock-agent/vpn/{booking_id}.ovpn"
        mock_ssh_fp = f"MOCK-FP-{booking_id}"
        return AgentProvisionResult(
            vpn_config_uri=mock_vpn_uri,
            ssh_public_key_fingerprint=mock_ssh_fp,
        )

    def revoke_access(self, *, credential_id: UUID) -> bool:
        """
        Tell the provider agent to revoke all access associated with an issued credential.
        Default mock implementation prints for now.
        """
        print(f"[Agent] revoke_access({credential_id}) at {datetime.now(timezone.utc)}")
        return True

    def collect_metrics(self, *, machine_id: UUID) -> dict:
        """
        Mock metrics collection.
        Example return: {"gpu": 40, "cpu": 13, "mem_gb": 5.3}
        """
        #Mock values
        return {
            "machine_id": str(machine_id),
            "gpu_util": 42,
            "cpu_util": 16,
            "mem_gb": 5.3,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }
    
    def collect_metrics_raw(self, machine_id: UUID) -> dict:
        """
        Same as collect_metrics(), but explicitly named for raw data retrieval.
        This avoids importing domain DTOs here.
        """
        return self.collect_metrics(machine_id=machine_id)


def get_agent_client() -> ProviderAgentClient:
    return ProviderAgentClient()