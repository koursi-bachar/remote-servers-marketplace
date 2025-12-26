from dataclasses import dataclass
from typing import Any


#Booking events
@dataclass(frozen=True)
class BookingConfirmedEvent:
    user: Any
    booking: Any


@dataclass(frozen=True)
class BookingActivatedEvent:
    user: Any
    booking: Any


@dataclass(frozen=True)
class BookingCompletedEvent:
    user: Any
    booking: Any


@dataclass(frozen=True)
class BookingCancelledEvent:
    user: Any
    booking: Any
    reason: str


#Payment events
@dataclass(frozen=True)
class PaymentCapturedEvent:
    user: Any
    payment: Any


@dataclass(frozen=True)
class PaymentFailedEvent:
    user: Any
    payment: Any


@dataclass(frozen=True)
class RefundIssuedEvent:
    user: Any
    payment: Any


#Credential events
@dataclass(frozen=True)
class CredentialsIssuedEvent:
    user: Any
    credential: Any


@dataclass(frozen=True)
class CredentialsRevokedEvent:
    user: Any
    credential: Any


#Dispute events
@dataclass(frozen=True)
class DisputeOpenedEvent:
    dispute: Any
    user: Any


@dataclass(frozen=True)
class DisputeResolvedEvent:
    dispute: Any
    user: Any


#Compliance events
@dataclass(frozen=True)
class WipeProofSubmittedEvent:
    provider: Any
    booking: Any
    attestation: Any


@dataclass(frozen=True)
class WipeFailureEvent:
    provider: Any
    booking: Any


@dataclass(frozen=True)
class ProviderSuspendedEvent:
    provider: Any
    reason: str


#Invoice events
@dataclass(frozen=True)
class InvoiceGeneratedEvent:
    organization: Any
    invoice: Any


@dataclass(frozen=True)
class InvoiceFinalizedEvent:
    organization: Any
    invoice: Any


#Provider alerts/metrics
@dataclass(frozen=True)
class ProviderAlertEvent:
    provider: Any
    message: str


@dataclass(frozen=True)
class MachineHealthAnomalyEvent:
    provider: Any
    machine: Any
    details: str


@dataclass(frozen=True)
class MachineOfflineEvent:
    provider: Any
    machine: Any