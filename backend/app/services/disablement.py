"""
Downstream Disablement Service
S4.1 - Verify and manage program dependency chains
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from enum import Enum


class DisablementAction(str, Enum):
    """Action taken during disablement."""
    DISABLED = "disabled"
    DEPRECATED = "deprecated"
    NOTIFIED = "notified"
    BLOCKED = "blocked"


@dataclass
class ProgramDependency:
    """Represents a dependency between programs."""
    
    parent_program_id: UUID
    child_program_id: UUID
    dependency_type: str  # "requires", "inherits", "references"
    is_critical: bool = False  # If true, child cannot function without parent


@dataclass
class DisablementEvent:
    """Record of a disablement action."""
    
    event_id: UUID
    program_id: UUID
    action: DisablementAction
    affected_programs: list[UUID]
    reason: str
    triggered_by: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    notifications_sent: list[str] = field(default_factory=list)


class DownstreamDisablementService:
    """
    Manages program dependency chains and cascading disablement.
    
    When a program is deprecated or disabled, this service:
    1. Identifies all dependent programs
    2. Validates if disablement is safe
    3. Notifies stakeholders
    4. Applies cascading actions
    """
    
    def __init__(self):
        self.dependencies: list[ProgramDependency] = []
        self.events: list[DisablementEvent] = []
        self._notification_callback = None
    
    def register_dependency(
        self,
        parent_id: UUID,
        child_id: UUID,
        dependency_type: str = "requires",
        is_critical: bool = False,
    ) -> ProgramDependency:
        """Register a dependency between programs."""
        dep = ProgramDependency(
            parent_program_id=parent_id,
            child_program_id=child_id,
            dependency_type=dependency_type,
            is_critical=is_critical,
        )
        self.dependencies.append(dep)
        return dep
    
    def get_dependents(self, program_id: UUID) -> list[ProgramDependency]:
        """Get all programs that depend on the given program."""
        return [d for d in self.dependencies if d.parent_program_id == program_id]
    
    def get_dependencies(self, program_id: UUID) -> list[ProgramDependency]:
        """Get all programs that the given program depends on."""
        return [d for d in self.dependencies if d.child_program_id == program_id]
    
    def get_dependency_chain(self, program_id: UUID) -> list[UUID]:
        """Get full downstream dependency chain (recursive)."""
        chain = []
        visited = set()
        
        def _traverse(pid: UUID):
            if pid in visited:
                return
            visited.add(pid)
            
            for dep in self.get_dependents(pid):
                chain.append(dep.child_program_id)
                _traverse(dep.child_program_id)
        
        _traverse(program_id)
        return chain
    
    def verify_disablement_safe(
        self,
        program_id: UUID,
    ) -> dict[str, Any]:
        """
        Verify if a program can be safely disabled.
        
        Returns impact analysis and any blockers.
        """
        dependents = self.get_dependents(program_id)
        chain = self.get_dependency_chain(program_id)
        
        critical_deps = [d for d in dependents if d.is_critical]
        
        return {
            "program_id": str(program_id),
            "can_disable": len(critical_deps) == 0,
            "direct_dependents": len(dependents),
            "total_affected": len(chain),
            "critical_blockers": [
                {
                    "child_program_id": str(d.child_program_id),
                    "dependency_type": d.dependency_type,
                }
                for d in critical_deps
            ],
            "warnings": [
                f"Program {d.child_program_id} will be affected"
                for d in dependents if not d.is_critical
            ],
        }
    
    def disable_program(
        self,
        program_id: UUID,
        reason: str,
        triggered_by: str,
        force: bool = False,
    ) -> DisablementEvent | None:
        """
        Disable a program and handle downstream effects.
        
        Args:
            program_id: Program to disable
            reason: Reason for disablement
            triggered_by: User/system that triggered action
            force: If True, disable even with critical blockers
        
        Returns:
            DisablementEvent if successful, None if blocked
        """
        verification = self.verify_disablement_safe(program_id)
        
        if not verification["can_disable"] and not force:
            return None
        
        # Get affected programs
        affected = self.get_dependency_chain(program_id)
        
        # Create event
        event = DisablementEvent(
            event_id=uuid4(),
            program_id=program_id,
            action=DisablementAction.DISABLED,
            affected_programs=affected,
            reason=reason,
            triggered_by=triggered_by,
        )
        
        # Send notifications
        notifications = []
        for dep in self.get_dependents(program_id):
            notif = f"Program {dep.child_program_id} notified of upstream disable"
            notifications.append(notif)
        
        event.notifications_sent = notifications
        self.events.append(event)
        
        return event
    
    def deprecate_program(
        self,
        program_id: UUID,
        reason: str,
        triggered_by: str,
        sunset_date: datetime | None = None,
    ) -> DisablementEvent:
        """
        Mark a program as deprecated (soft disable).
        
        Programs will continue to work but will show warnings.
        """
        affected = self.get_dependency_chain(program_id)
        
        event = DisablementEvent(
            event_id=uuid4(),
            program_id=program_id,
            action=DisablementAction.DEPRECATED,
            affected_programs=affected,
            reason=reason,
            triggered_by=triggered_by,
        )
        
        notifications = []
        for dep in self.get_dependents(program_id):
            notif = f"Program {dep.child_program_id} notified of deprecation"
            if sunset_date:
                notif += f" with sunset date {sunset_date.isoformat()}"
            notifications.append(notif)
        
        event.notifications_sent = notifications
        self.events.append(event)
        
        return event
    
    def get_events(
        self,
        program_id: UUID | None = None,
        limit: int = 100,
    ) -> list[DisablementEvent]:
        """Get disablement events, optionally filtered by program."""
        events = self.events
        
        if program_id:
            events = [e for e in events if e.program_id == program_id]
        
        return sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def export_dependency_graph(self) -> dict[str, Any]:
        """Export dependency graph for visualization."""
        nodes = set()
        edges = []
        
        for dep in self.dependencies:
            nodes.add(str(dep.parent_program_id))
            nodes.add(str(dep.child_program_id))
            edges.append({
                "source": str(dep.parent_program_id),
                "target": str(dep.child_program_id),
                "type": dep.dependency_type,
                "critical": dep.is_critical,
            })
        
        return {
            "nodes": list(nodes),
            "edges": edges,
        }


# Singleton instance
disablement_service = DownstreamDisablementService()
