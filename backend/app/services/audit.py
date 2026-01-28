"""
GOATCRD Audit Service
Append-only audit event logging
"""
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditEvent


class AuditService:
    """Service for recording audit events."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_event(
        self,
        event_type: str,
        *,
        actor_id: UUID | None = None,
        actor_role: str | None = None,
        actor_ip: str | None = None,
        resource_type: str | None = None,
        resource_id: UUID | None = None,
        event_data: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Log an audit event (append-only)."""
        event = AuditEvent(
            actor_id=actor_id,
            actor_role=actor_role,
            actor_ip=actor_ip,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            event_data=json.dumps(event_data) if event_data else None,
        )
        
        self.db.add(event)
        await self.db.flush()
        
        return event
    
    async def log_case_created(
        self, case_id: UUID, actor_id: UUID, actor_role: str, actor_ip: str | None = None
    ) -> AuditEvent:
        """Log case creation."""
        return await self.log_event(
            "case.created",
            actor_id=actor_id,
            actor_role=actor_role,
            actor_ip=actor_ip,
            resource_type="case",
            resource_id=case_id,
        )
    
    async def log_intake_submitted(
        self,
        case_id: UUID,
        snapshot_id: UUID,
        actor_id: UUID,
        actor_role: str,
        actor_ip: str | None = None,
    ) -> AuditEvent:
        """Log intake submission."""
        return await self.log_event(
            "intake.submitted",
            actor_id=actor_id,
            actor_role=actor_role,
            actor_ip=actor_ip,
            resource_type="intake_snapshot",
            resource_id=snapshot_id,
            event_data={"case_id": str(case_id)},
        )
    
    async def log_consent_granted(
        self,
        consent_id: UUID,
        scope: str,
        actor_id: UUID,
        actor_ip: str | None = None,
    ) -> AuditEvent:
        """Log consent grant."""
        return await self.log_event(
            "consent.granted",
            actor_id=actor_id,
            actor_role="consumer",
            actor_ip=actor_ip,
            resource_type="consent",
            resource_id=consent_id,
            event_data={"scope": scope},
        )
    
    async def log_consent_revoked(
        self,
        consent_id: UUID,
        scope: str,
        actor_id: UUID,
        actor_ip: str | None = None,
    ) -> AuditEvent:
        """Log consent revocation."""
        return await self.log_event(
            "consent.revoked",
            actor_id=actor_id,
            actor_role="consumer",
            actor_ip=actor_ip,
            resource_type="consent",
            resource_id=consent_id,
            event_data={"scope": scope},
        )
    
    async def log_data_accessed(
        self,
        resource_type: str,
        resource_id: UUID,
        action: str,
        actor_id: UUID | None,
        actor_role: str | None,
        actor_ip: str | None = None,
    ) -> AuditEvent:
        """Log data access for 1033 compliance."""
        return await self.log_event(
            "data.accessed",
            actor_id=actor_id,
            actor_role=actor_role,
            actor_ip=actor_ip,
            resource_type=resource_type,
            resource_id=resource_id,
            event_data={"action": action},
        )
    
    async def log_scenario_run(
        self,
        case_id: UUID,
        run_id: UUID,
        actor_id: UUID,
        actor_role: str,
    ) -> AuditEvent:
        """Log scenario generation run."""
        return await self.log_event(
            "scenario.run_completed",
            actor_id=actor_id,
            actor_role=actor_role,
            resource_type="scenario_run",
            resource_id=run_id,
            event_data={"case_id": str(case_id)},
        )
    
    async def log_override(
        self,
        ticket_id: UUID,
        override_id: UUID,
        override_type: str,
        actor_id: UUID,
        actor_role: str,
    ) -> AuditEvent:
        """Log human override."""
        return await self.log_event(
            "review.override",
            actor_id=actor_id,
            actor_role=actor_role,
            resource_type="override",
            resource_id=override_id,
            event_data={"ticket_id": str(ticket_id), "override_type": override_type},
        )
    
    async def log_export_generated(
        self,
        case_id: UUID,
        export_id: UUID,
        export_type: str,
        actor_id: UUID,
        actor_role: str,
    ) -> AuditEvent:
        """Log export generation."""
        return await self.log_event(
            "export.generated",
            actor_id=actor_id,
            actor_role=actor_role,
            resource_type="export",
            resource_id=export_id,
            event_data={"case_id": str(case_id), "export_type": export_type},
        )
