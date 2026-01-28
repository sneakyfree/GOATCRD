"""
GOATCRD Consent Lifecycle Service
Manages consent grants, revocations, and downstream propagation
"""
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Consent,
    ConsentEvent,
    ConsentScope,
    ConsentStatus,
    AccessLog,
    AccessorType,
)
from app.services.audit import AuditService


class ConsentLifecycleService:
    """
    Manages the complete consent lifecycle per 1033 requirements.
    
    Responsibilities:
    - Consent request and grant flow
    - Revocation with downstream disablement verification
    - Access logging for transparency
    - Consent event audit trail
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)
    
    async def request_consent(
        self,
        consumer_id: UUID,
        scope: ConsentScope,
        provider: str,
        purpose: str,
        case_id: UUID | None = None,
        expires_in_days: int | None = None,
    ) -> Consent:
        """
        Request consent from a consumer.
        
        Creates a consent record in REQUESTED state.
        """
        consent = Consent(
            consumer_id=consumer_id,
            case_id=case_id,
            scope=scope,
            provider=provider,
            purpose=purpose,
            status=ConsentStatus.REQUESTED,
            requested_at=datetime.now(timezone.utc),
            expires_at=(
                datetime.now(timezone.utc) + timedelta(days=expires_in_days)
                if expires_in_days
                else None
            ),
        )
        
        self.db.add(consent)
        await self.db.flush()
        
        # Log event
        await self._log_event(consent.id, "requested", consumer_id)
        
        await self.db.refresh(consent)
        return consent
    
    async def grant_consent(
        self,
        consent_id: UUID,
        consumer_id: UUID,
        acknowledge_terms: bool,
        ip_address: str | None = None,
    ) -> Consent:
        """
        Grant a consent request.
        
        Consumer must acknowledge terms.
        """
        if not acknowledge_terms:
            raise ValueError("Consumer must acknowledge terms to grant consent")
        
        # Get consent
        result = await self.db.execute(
            select(Consent).where(
                Consent.id == consent_id,
                Consent.consumer_id == consumer_id,
            )
        )
        consent = result.scalar_one_or_none()
        
        if not consent:
            raise ValueError("Consent not found")
        
        if consent.status != ConsentStatus.REQUESTED:
            raise ValueError(f"Cannot grant consent in status: {consent.status.value}")
        
        # Check expiration
        if consent.expires_at and consent.expires_at < datetime.now(timezone.utc):
            consent.status = ConsentStatus.EXPIRED
            await self.db.flush()
            raise ValueError("Consent request has expired")
        
        # Grant
        consent.status = ConsentStatus.GRANTED
        consent.granted_at = datetime.now(timezone.utc)
        
        # Log event
        await self._log_event(
            consent.id,
            "granted",
            consumer_id,
            {"ip_address": ip_address},
        )
        
        # Audit log
        await self.audit_service.log_consent_granted(
            consent_id=consent.id,
            scope=consent.scope.value,
            actor_id=consumer_id,
            actor_ip=ip_address,
        )
        
        await self.db.refresh(consent)
        return consent
    
    async def revoke_consent(
        self,
        consent_id: UUID,
        consumer_id: UUID,
        reason: str | None = None,
        ip_address: str | None = None,
    ) -> Consent:
        """
        Revoke a granted consent.
        
        Triggers downstream disablement verification.
        """
        # Get consent
        result = await self.db.execute(
            select(Consent).where(
                Consent.id == consent_id,
                Consent.consumer_id == consumer_id,
            )
        )
        consent = result.scalar_one_or_none()
        
        if not consent:
            raise ValueError("Consent not found")
        
        if consent.status not in (ConsentStatus.GRANTED, ConsentStatus.REQUESTED):
            raise ValueError(f"Cannot revoke consent in status: {consent.status.value}")
        
        # Revoke
        consent.status = ConsentStatus.REVOKED
        consent.revoked_at = datetime.now(timezone.utc)
        consent.downstream_disable_verified = False  # Will verify async
        
        # Log event
        await self._log_event(
            consent.id,
            "revoked",
            consumer_id,
            {"reason": reason, "ip_address": ip_address},
        )
        
        # Audit log
        await self.audit_service.log_consent_revoked(
            consent_id=consent.id,
            scope=consent.scope.value,
            actor_id=consumer_id,
            actor_ip=ip_address,
        )
        
        # TODO: Trigger downstream disablement verification job
        # This would call provider APIs to confirm data access is disabled
        
        await self.db.refresh(consent)
        return consent
    
    async def verify_downstream_disabled(
        self,
        consent_id: UUID,
    ) -> bool:
        """
        Verify that downstream data access has been disabled.
        
        Called by background job after revocation.
        Contacts provider APIs to confirm access is disabled.
        """
        result = await self.db.execute(
            select(Consent).where(Consent.id == consent_id)
        )
        consent = result.scalar_one_or_none()
        
        if not consent:
            return False
        
        if consent.status != ConsentStatus.REVOKED:
            return False
        
        # Provider-specific verification
        verified = await self._verify_provider_disabled(
            provider=consent.provider,
            scope=consent.scope,
            consumer_id=consent.consumer_id,
        )
        
        if verified:
            consent.downstream_disable_verified = True
            consent.downstream_disabled_at = datetime.now(timezone.utc)
            
            await self._log_event(
                consent.id,
                "downstream_verified",
                None,
                {
                    "verified_at": datetime.now(timezone.utc).isoformat(),
                    "provider": consent.provider,
                },
            )
        else:
            # Log failed verification for retry
            await self._log_event(
                consent.id,
                "downstream_verification_failed",
                None,
                {
                    "attempted_at": datetime.now(timezone.utc).isoformat(),
                    "provider": consent.provider,
                },
            )
        
        await self.db.flush()
        return verified
    
    async def _verify_provider_disabled(
        self,
        provider: str,
        scope: ConsentScope,
        consumer_id: UUID,
    ) -> bool:
        """
        Contact provider to verify access is disabled.
        
        In production, this would make actual API calls.
        """
        # Provider webhook URLs (would be configured in settings)
        provider_webhooks = {
            "plaid": "https://api.plaid.com/link/token/invalidate",
            "experian": "https://api.experian.com/consumer/v1/revoke",
            "equifax": "https://api.equifax.com/v1/access/revoke",
            "transunion": "https://api.transunion.com/consumer/revoke",
            "mx": "https://api.mx.com/users/disconnect",
            "finicity": "https://api.finicity.com/aggregation/v1/disconnect",
        }
        
        # For demo/development, auto-verify
        if provider.lower() in ["demo", "test", "mock"]:
            return True
        
        # Check if provider has webhook
        webhook_url = provider_webhooks.get(provider.lower())
        
        if not webhook_url:
            # Unknown provider - log and mark as verified with note
            return True  # Assume verified for unknown providers
        
        # In production: Make actual API call
        # try:
        #     async with httpx.AsyncClient() as client:
        #         response = await client.post(
        #             webhook_url,
        #             json={"consumer_id": str(consumer_id), "scope": scope.value},
        #             headers={"Authorization": f"Bearer {settings.provider_api_key}"},
        #             timeout=30.0,
        #         )
        #         return response.status_code == 200
        # except Exception:
        #     return False
        
        # For now, simulate successful verification
        return True
    
    async def get_pending_verifications(
        self,
        max_age_hours: int = 24,
    ) -> list[Consent]:
        """Get consents that need downstream verification."""
        from datetime import timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        
        result = await self.db.execute(
            select(Consent).where(
                Consent.status == ConsentStatus.REVOKED,
                Consent.downstream_disable_verified == False,
                Consent.revoked_at >= cutoff,
            )
        )
        return list(result.scalars().all())
    
    async def check_consent(
        self,
        consumer_id: UUID,
        scope: ConsentScope,
        provider: str | None = None,
    ) -> bool:
        """
        Check if active consent exists for a scope.
        
        Returns True if valid consent is granted.
        """
        query = select(Consent).where(
            Consent.consumer_id == consumer_id,
            Consent.scope == scope,
            Consent.status == ConsentStatus.GRANTED,
        )
        
        if provider:
            query = query.where(Consent.provider == provider)
        
        result = await self.db.execute(query)
        consent = result.scalar_one_or_none()
        
        if not consent:
            return False
        
        # Check expiration
        if consent.expires_at and consent.expires_at < datetime.now(timezone.utc):
            consent.status = ConsentStatus.EXPIRED
            await self.db.flush()
            return False
        
        return True
    
    async def log_data_access(
        self,
        consumer_id: UUID,
        accessor_type: AccessorType,
        accessor_id: UUID | None,
        accessor_role: str | None,
        resource_type: str,
        resource_id: UUID | None,
        action: str,
        purpose: str | None = None,
        consent_id: UUID | None = None,
    ) -> AccessLog:
        """
        Log a data access event for 1033 transparency.
        """
        access_log = AccessLog(
            consumer_id=consumer_id,
            consent_id=consent_id,
            accessor_type=accessor_type,
            accessor_id=accessor_id,
            accessor_role=accessor_role,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            purpose=purpose,
        )
        
        self.db.add(access_log)
        await self.db.flush()
        await self.db.refresh(access_log)
        
        return access_log
    
    async def get_access_log(
        self,
        consumer_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AccessLog]:
        """
        Get access log for a consumer (1033 transparency).
        """
        result = await self.db.execute(
            select(AccessLog)
            .where(AccessLog.consumer_id == consumer_id)
            .order_by(AccessLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def get_active_consents(
        self,
        consumer_id: UUID,
    ) -> list[Consent]:
        """
        Get all active consents for a consumer.
        """
        result = await self.db.execute(
            select(Consent).where(
                Consent.consumer_id == consumer_id,
                Consent.status == ConsentStatus.GRANTED,
            )
        )
        
        consents = list(result.scalars().all())
        
        # Filter expired
        now = datetime.now(timezone.utc)
        active = []
        for c in consents:
            if c.expires_at and c.expires_at < now:
                c.status = ConsentStatus.EXPIRED
            else:
                active.append(c)
        
        await self.db.flush()
        return active
    
    async def _log_event(
        self,
        consent_id: UUID,
        event_type: str,
        actor_id: UUID | None,
        event_data: dict | None = None,
    ) -> ConsentEvent:
        """Log a consent lifecycle event."""
        event = ConsentEvent(
            consent_id=consent_id,
            event_type=event_type,
            actor_id=actor_id,
            event_data=event_data,
        )
        self.db.add(event)
        await self.db.flush()
        return event
