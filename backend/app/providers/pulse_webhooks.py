"""
GOATCRD Pulse Webhook Handler
Ingest credit monitoring events
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pulse import PulseAlert, PulseEventType, PulseSubscription


class WebhookSource(str, Enum):
    """Webhook event sources."""
    EXPERIAN = "experian"
    EQUIFAX = "equifax"
    TRANSUNION = "transunion"
    CREDITKARMA = "creditkarma"
    PLAID = "plaid"


@dataclass
class WebhookEvent:
    """Parsed webhook event."""
    source: WebhookSource
    event_type: str
    consumer_external_id: str
    event_data: dict
    received_at: datetime


class PulseWebhookHandler:
    """
    Handler for credit monitoring webhook events.
    
    Processes incoming webhooks from credit bureaus and
    creates pulse alerts for subscribed consumers.
    """
    
    # Map external event types to internal types
    EVENT_TYPE_MAP = {
        # Experian
        "HARD_INQUIRY": PulseEventType.HARD_INQUIRY,
        "NEW_ACCOUNT_OPENED": PulseEventType.NEW_ACCOUNT,
        "BALANCE_UPDATE": PulseEventType.BALANCE_CHANGE,
        "PAYMENT_POSTED": PulseEventType.PAYMENT_REPORTED,
        "LATE_PAYMENT": PulseEventType.DELINQUENCY,
        "SCORE_CHANGE": PulseEventType.CREDIT_SCORE_CHANGE,
        
        # Equifax
        "inquiry_detected": PulseEventType.HARD_INQUIRY,
        "tradeline_added": PulseEventType.NEW_ACCOUNT,
        "balance_change": PulseEventType.BALANCE_CHANGE,
        "score_update": PulseEventType.CREDIT_SCORE_CHANGE,
        
        # TransUnion
        "INQUIRY": PulseEventType.HARD_INQUIRY,
        "NEW_TRADELINE": PulseEventType.NEW_ACCOUNT,
        "ACCOUNT_UPDATE": PulseEventType.BALANCE_CHANGE,
        "DELINQUENCY": PulseEventType.DELINQUENCY,
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def handle_webhook(
        self,
        source: WebhookSource,
        payload: dict,
        signature: str | None = None,
    ) -> list[PulseAlert]:
        """
        Handle incoming webhook event.
        
        Args:
            source: Webhook source (bureau)
            payload: Raw webhook payload
            signature: Webhook signature for verification
        
        Returns:
            List of created alerts
        """
        # Verify signature (in production)
        if not await self._verify_signature(source, payload, signature):
            raise ValueError("Invalid webhook signature")
        
        # Parse event
        event = self._parse_event(source, payload)
        
        # Find subscribed consumer
        consumer_id = await self._lookup_consumer(event.consumer_external_id)
        if not consumer_id:
            return []  # Consumer not in system
        
        # Check if consumer has active subscription
        subscription = await self._get_active_subscription(consumer_id)
        if not subscription:
            return []  # Not subscribed
        
        # Check if event type matches subscription filters
        internal_type = self._map_event_type(event.event_type)
        if not self._matches_subscription(subscription, internal_type):
            return []  # Event type not in subscription
        
        # Create alert
        alert = await self._create_alert(
            consumer_id=consumer_id,
            subscription=subscription,
            event=event,
            event_type=internal_type,
        )
        
        return [alert]
    
    async def _verify_signature(
        self,
        source: WebhookSource,
        payload: dict,
        signature: str | None,
    ) -> bool:
        """Verify webhook signature."""
        # In production, would verify HMAC signature
        # For development, accept all
        return True
    
    def _parse_event(
        self,
        source: WebhookSource,
        payload: dict,
    ) -> WebhookEvent:
        """Parse webhook payload into standard event."""
        # Source-specific parsing
        if source == WebhookSource.EXPERIAN:
            return WebhookEvent(
                source=source,
                event_type=payload.get("eventType", ""),
                consumer_external_id=payload.get("consumerId", ""),
                event_data=payload.get("data", {}),
                received_at=datetime.now(timezone.utc),
            )
        elif source == WebhookSource.EQUIFAX:
            return WebhookEvent(
                source=source,
                event_type=payload.get("event_type", ""),
                consumer_external_id=payload.get("consumer_id", ""),
                event_data=payload.get("event_data", {}),
                received_at=datetime.now(timezone.utc),
            )
        else:
            # Generic parsing
            return WebhookEvent(
                source=source,
                event_type=payload.get("type", payload.get("event_type", "")),
                consumer_external_id=payload.get("consumer_id", payload.get("user_id", "")),
                event_data=payload,
                received_at=datetime.now(timezone.utc),
            )
    
    async def _lookup_consumer(self, external_id: str) -> UUID | None:
        """Look up consumer by external ID."""
        # In production, would look up in consumer_external_ids table
        from app.models import User
        
        result = await self.db.execute(
            select(User).where(User.email == external_id)  # Simplified lookup
        )
        user = result.scalar_one_or_none()
        return user.id if user else None
    
    async def _get_active_subscription(
        self,
        consumer_id: UUID,
    ) -> PulseSubscription | None:
        """Get active pulse subscription for consumer."""
        result = await self.db.execute(
            select(PulseSubscription).where(
                PulseSubscription.consumer_id == consumer_id,
                PulseSubscription.is_active == True,
            )
        )
        return result.scalar_one_or_none()
    
    def _map_event_type(self, external_type: str) -> PulseEventType:
        """Map external event type to internal type."""
        return self.EVENT_TYPE_MAP.get(
            external_type,
            PulseEventType.BALANCE_CHANGE,  # Default
        )
    
    def _matches_subscription(
        self,
        subscription: PulseSubscription,
        event_type: PulseEventType,
    ) -> bool:
        """Check if event type matches subscription filters."""
        # Empty filter = all events
        if not subscription.event_types:
            return True
        
        return event_type.value in subscription.event_types
    
    async def _create_alert(
        self,
        consumer_id: UUID,
        subscription: PulseSubscription,
        event: WebhookEvent,
        event_type: PulseEventType,
    ) -> PulseAlert:
        """Create pulse alert from event."""
        # Generate summary and impact based on event type
        summary, impact, suggested_action = self._generate_alert_content(
            event_type,
            event.event_data,
        )
        
        alert = PulseAlert(
            consumer_id=consumer_id,
            subscription_id=subscription.id,
            event_type=event_type,
            detected_at=event.received_at,
            summary=summary,
            impact=impact,
            suggested_action=suggested_action,
            event_data=event.event_data,
            scenario_refresh_available=event_type in (
                PulseEventType.CREDIT_SCORE_CHANGE,
                PulseEventType.BALANCE_CHANGE,
            ),
        )
        
        self.db.add(alert)
        await self.db.flush()
        await self.db.refresh(alert)
        
        return alert
    
    def _generate_alert_content(
        self,
        event_type: PulseEventType,
        event_data: dict,
    ) -> tuple[str, str | None, str | None]:
        """Generate human-readable alert content."""
        templates = {
            PulseEventType.HARD_INQUIRY: (
                "A hard inquiry was added to your credit report",
                f"Inquiry from {event_data.get('creditor', 'Unknown')}",
                "Review this inquiry and report if unauthorized",
            ),
            PulseEventType.NEW_ACCOUNT: (
                "A new account appeared on your credit report",
                f"New {event_data.get('account_type', 'account')} opened",
                "Verify this is your account",
            ),
            PulseEventType.BALANCE_CHANGE: (
                "Your credit card balance changed",
                f"Balance is now ${event_data.get('new_balance', 0):,.0f}",
                "Keep utilization under 30% for best impact",
            ),
            PulseEventType.PAYMENT_REPORTED: (
                "A payment was reported to the bureaus",
                "On-time payments build positive history",
                None,
            ),
            PulseEventType.DELINQUENCY: (
                "⚠️ A late payment was reported",
                "This may impact your credit score",
                "Contact the creditor to resolve and request goodwill removal",
            ),
            PulseEventType.CREDIT_SCORE_CHANGE: (
                "Your credit score changed",
                f"Score is now {event_data.get('new_score', 'N/A')}",
                "Refresh your scenarios to see updated options",
            ),
            PulseEventType.UTILIZATION_CHANGE: (
                "Your credit utilization changed",
                f"Utilization is now {event_data.get('utilization', 0):.0f}%",
                "Target under 30% for optimal credit impact",
            ),
        }
        
        return templates.get(
            event_type,
            ("Credit activity detected", None, None),
        )


# Convenience function for route handlers
async def process_webhook(
    db: AsyncSession,
    source: str,
    payload: dict,
    signature: str | None = None,
) -> list[PulseAlert]:
    """Process incoming webhook."""
    handler = PulseWebhookHandler(db)
    
    try:
        source_enum = WebhookSource(source.lower())
    except ValueError:
        source_enum = WebhookSource.EXPERIAN  # Default
    
    return await handler.handle_webhook(source_enum, payload, signature)
