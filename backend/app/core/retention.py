"""
GOATCRD Retention Policy Module
Data lifecycle management and automated purge
"""
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

logger = logging.getLogger(__name__)


class DataType(str, Enum):
    """Types of data with different retention policies."""
    AUDIT_EVENTS = "audit_events"
    SESSION_DATA = "session_data"
    INTAKE_DRAFTS = "intake_drafts"
    EXPORTS = "exports"
    PULSE_ALERTS = "pulse_alerts"
    ACCESS_LOGS = "access_logs"
    AGENT_ACTIONS = "agent_actions"


# Default retention periods (in days)
DEFAULT_RETENTION_POLICIES = {
    DataType.AUDIT_EVENTS: 2555,      # 7 years (compliance)
    DataType.SESSION_DATA: 90,         # 90 days
    DataType.INTAKE_DRAFTS: 365,       # 1 year
    DataType.EXPORTS: 30,              # 30 days
    DataType.PULSE_ALERTS: 180,        # 6 months
    DataType.ACCESS_LOGS: 2555,        # 7 years (compliance)
    DataType.AGENT_ACTIONS: 365,       # 1 year
}


class RetentionPolicy:
    """
    Manages data retention policies and purge operations.
    
    Usage:
        policy = RetentionPolicy(db_session)
        await policy.purge_expired_data(DataType.SESSION_DATA)
    """
    
    def __init__(
        self,
        db: AsyncSession,
        custom_policies: Optional[dict[DataType, int]] = None,
    ):
        self.db = db
        self.policies = {**DEFAULT_RETENTION_POLICIES}
        if custom_policies:
            self.policies.update(custom_policies)
    
    def get_retention_days(self, data_type: DataType) -> int:
        """Get retention period for a data type."""
        return self.policies.get(data_type, 365)
    
    def get_cutoff_date(self, data_type: DataType) -> datetime:
        """Get the cutoff date for purging expired data."""
        retention_days = self.get_retention_days(data_type)
        return datetime.now(timezone.utc) - timedelta(days=retention_days)
    
    async def purge_expired_data(
        self,
        data_type: DataType,
        dry_run: bool = False,
    ) -> int:
        """
        Purge expired data of specified type.
        
        Args:
            data_type: Type of data to purge
            dry_run: If True, only count without deleting
            
        Returns:
            Number of records deleted (or would be deleted if dry_run)
        """
        cutoff = self.get_cutoff_date(data_type)
        count = 0
        
        # Import models here to avoid circular imports
        from app.models import AuditEvent, AccessLog
        from app.models.case import IntakeDraft
        from app.models.scenario import Export
        
        model_map = {
            DataType.AUDIT_EVENTS: AuditEvent,
            DataType.SESSION_DATA: None,  # Handled by session store
            DataType.INTAKE_DRAFTS: IntakeDraft,
            DataType.EXPORTS: Export,
            DataType.PULSE_ALERTS: None,  # Will add when model exists
            DataType.ACCESS_LOGS: AccessLog,
            DataType.AGENT_ACTIONS: None,  # Will add when model exists
        }
        
        model = model_map.get(data_type)
        if not model:
            logger.warning(f"No model configured for purge: {data_type}")
            return 0
        
        # Count records to purge
        count_stmt = select(model).where(model.created_at < cutoff)
        result = await self.db.execute(count_stmt)
        expired_records = list(result.scalars().all())
        count = len(expired_records)
        
        if dry_run:
            logger.info(f"[DRY RUN] Would purge {count} {data_type.value} records")
            return count
        
        if count > 0:
            # Perform deletion
            delete_stmt = delete(model).where(model.created_at < cutoff)
            await self.db.execute(delete_stmt)
            
            # Log the purge
            await self._log_purge_event(data_type, count, cutoff)
            
            logger.info(f"Purged {count} {data_type.value} records older than {cutoff}")
        
        return count
    
    async def purge_all_expired(self, dry_run: bool = False) -> dict[str, int]:
        """
        Purge all expired data across all types.
        
        Returns:
            Dict mapping data type to count of deleted records
        """
        results = {}
        for data_type in DataType:
            try:
                count = await self.purge_expired_data(data_type, dry_run)
                results[data_type.value] = count
            except Exception as e:
                logger.error(f"Failed to purge {data_type.value}: {e}")
                results[data_type.value] = -1
        
        return results
    
    async def _log_purge_event(
        self,
        data_type: DataType,
        count: int,
        cutoff: datetime,
    ) -> None:
        """Log a purge event to audit trail."""
        from app.models import AuditEvent
        
        event = AuditEvent(
            event_type="data_purge",
            actor_id=None,  # System action
            event_data={
                "data_type": data_type.value,
                "records_purged": count,
                "cutoff_date": cutoff.isoformat(),
                "retention_days": self.get_retention_days(data_type),
            },
        )
        self.db.add(event)
    
    async def get_purge_preview(self) -> dict[str, dict]:
        """
        Get a preview of what would be purged for each data type.
        
        Returns:
            Dict with data type info, cutoff dates, and counts
        """
        preview = {}
        
        for data_type in DataType:
            count = await self.purge_expired_data(data_type, dry_run=True)
            preview[data_type.value] = {
                "retention_days": self.get_retention_days(data_type),
                "cutoff_date": self.get_cutoff_date(data_type).isoformat(),
                "records_to_purge": count,
            }
        
        return preview


async def run_scheduled_purge(db: AsyncSession) -> dict:
    """
    Scheduled task to run retention purge.
    Called by Celery/background scheduler.
    """
    policy = RetentionPolicy(db)
    results = await policy.purge_all_expired()
    
    total = sum(v for v in results.values() if v > 0)
    logger.info(f"Scheduled purge complete: {total} total records purged")
    
    return results
