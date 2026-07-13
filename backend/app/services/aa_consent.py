"""Account Aggregator consent flow (Sahamati ecosystem).

Sprint scope: model the consent lifecycle and the FI data-pull handshake
against an AA sandbox. Production hardening (FIU registration, certifier
audit) is post-sprint work and is marked as such.

Flow:
  1. Investor picks their AA handle (e.g. name@onemoney).
  2. Artha (as FIU) raises a consent request: purpose, FI types,
     date range, frequency, expiry.
  3. Investor approves in their AA app.
  4. Artha polls consent status; on ACTIVE, requests an FI data session.
  5. Encrypted FI data arrives; Artha decrypts, normalizes into the
     unified holdings model, and discards the raw payload.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ConsentStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    REVOKED = "revoked"
    EXPIRED = "expired"


class FIType(str, Enum):
    DEPOSIT = "DEPOSIT"
    EQUITIES = "EQUITIES"
    MUTUAL_FUNDS = "MUTUAL_FUNDS"
    ETF = "ETF"
    REIT = "REIT"
    INVIT = "INVIT"
    DEBENTURES = "DEBENTURES"


@dataclass
class ConsentRequest:
    user_id: str
    aa_handle: str
    fi_types: list[FIType]
    purpose_code: str = "102"          # per ReBIT purpose codes: portfolio view
    frequency_per_day: int = 4
    expiry: datetime | None = None
    status: ConsentStatus = ConsentStatus.PENDING
    consent_id: str | None = None
    audit: list[dict] = field(default_factory=list)

    def record(self, event: str) -> None:
        self.audit.append({"event": event, "at": datetime.utcnow().isoformat()})


class AAClient:
    """Thin client over the AA gateway APIs. Sandbox implementation."""

    def __init__(self, fiu_id: str, base_url: str):
        self.fiu_id = fiu_id
        self.base_url = base_url

    async def raise_consent(self, req: ConsentRequest) -> ConsentRequest:
        """POST /Consent — raises the consent artefact with the AA."""
        req.record("consent_raised")
        raise NotImplementedError("Wire to AA sandbox during sprint")

    async def check_status(self, consent_id: str) -> ConsentStatus:
        """GET /Consent/{id} — investor may approve, pause, or revoke any time."""
        raise NotImplementedError("Wire to AA sandbox during sprint")

    async def request_fi_data(self, consent_id: str) -> dict:
        """POST /FI/request then GET /FI/fetch — returns decrypted, normalized payload.

        Raw encrypted payload is discarded after normalization. Only the
        normalized holdings enter the Artha schema.
        """
        raise NotImplementedError("Wire to AA sandbox during sprint")
