from fastapi import Depends
from dataclasses import dataclass
from app.provider_agent.client import ProviderAgentClient, get_agent_client


@dataclass
class IssuedCredentialPayload:
    """
    Returned by issuer.issue().
    Service layer persists these values through the repository.
    """
    vpn_config_uri: str
    ssh_public_key_fingerprint: str

class CredentialIssuer:
    """
    Abstract interface for issuing & revoking credentials.
    """
    def issue(self, *, booking, user, machine) -> IssuedCredentialPayload:
        ...

    def revoke(self, credential):
        ...

class VpnAndSshIssuer(CredentialIssuer):
    """
    Concrete issuer, delegates to ProviderAgentClient.
    """
    def __init__(self, agent_client: ProviderAgentClient):
        self.agent = agent_client

    def issue(self, *, booking, user, machine) -> IssuedCredentialPayload:
        """
        Fully delegate provisioning to the agent client.
        """
        result = self.agent.provision_access(
            booking_id=booking.id,
            user_id=user.id,
            machine_id=machine.id,
        )

        return IssuedCredentialPayload(
            vpn_config_uri=result.vpn_config_uri,
            ssh_public_key_fingerprint=result.ssh_public_key_fingerprint,
        )

    def revoke(self, credential):
        """
        Delegate revocation to provider agent.
        """
        return self.agent.revoke_access(
            credential_id=credential.id
        )

def get_credential_issuer(
    agent: ProviderAgentClient = Depends(get_agent_client),
) -> CredentialIssuer:
    """Dependency injection provider for issuer interface."""
    return VpnAndSshIssuer(agent)