"""
GOATCRD Pulse Event Source
Abstraction for credit monitoring event sources with mock fallback.
"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)


class PulseEvent:
    """Represents a detected credit-relevant event."""
    
    def __init__(
        self,
        event_type: str,
        summary: str,
        impact: str | None = None,
        suggested_action: str | None = None,
        event_data: dict[str, Any] | None = None,
        detected_at: datetime | None = None,
    ):
        self.event_type = event_type
        self.summary = summary
        self.impact = impact
        self.suggested_action = suggested_action
        self.event_data = event_data or {}
        self.detected_at = detected_at or datetime.now(timezone.utc)


class PulseEventSource(ABC):
    """Abstract interface for pulse event sources."""
    
    @abstractmethod
    async def check_for_events(self, consumer_id: str) -> list[PulseEvent]:
        """Check for new credit-relevant events."""
        ...


class MockPulseSource(PulseEventSource):
    """Mock event source for development and demos."""
    
    async def check_for_events(self, consumer_id: str) -> list[PulseEvent]:
        """Return simulated events for demo purposes."""
        return [
            PulseEvent(
                event_type="balance_change",
                summary="Checking account balance decreased by $450",
                impact="Your debt-to-income ratio may be affected",
                suggested_action="Review your budget and consider scenario refresh",
                event_data={
                    "account": "Primary Checking",
                    "previous_balance": 4700.00,
                    "current_balance": 4250.00,
                    "change": -450.00,
                    "_mock": True,
                },
            ),
            PulseEvent(
                event_type="new_inquiry",
                summary="New credit inquiry detected from Auto Finance Co",
                impact="Hard inquiries may temporarily lower your credit score by 5-10 points",
                suggested_action="If you didn't apply for this, dispute it with the credit bureau",
                event_data={
                    "inquirer": "Auto Finance Co",
                    "inquiry_type": "hard",
                    "estimated_impact": -7,
                    "_mock": True,
                },
            ),
        ]


class PlaidTransactionSource(PulseEventSource):
    """
    Real event source using Plaid transaction webhooks.
    Detects balance changes and unusual transactions.
    """
    
    def __init__(self):
        from app.providers.plaid import PlaidProvider
        self.plaid = PlaidProvider()
    
    async def check_for_events(self, consumer_id: str) -> list[PulseEvent]:
        """Check Plaid for recent transaction-based events."""
        if not self.plaid.is_live:
            # Fall back to mock if Plaid not configured
            return await MockPulseSource().check_for_events(consumer_id)
        
        events: list[PulseEvent] = []
        try:
            # In production, access_token would be retrieved from DB
            # For now, log that we'd check Plaid
            logger.info("Would check Plaid for consumer=%s events", consumer_id)
        except Exception as e:
            logger.error("Plaid event check failed: %s", str(e))
        
        return events


def create_pulse_source() -> PulseEventSource:
    """Factory: create the appropriate pulse event source based on config."""
    from app.core.config import settings
    
    if settings.plaid_client_id and settings.plaid_secret:
        return PlaidTransactionSource()
    return MockPulseSource()
