"""
Program Version Pinning Service
S4.2 - Pin program versions to decisions for reproducibility
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
import hashlib
import json


@dataclass
class ProgramVersion:
    """Represents a specific version of a program."""
    
    program_id: UUID
    version: str  # semver format: 1.2.3
    version_hash: str  # SHA-256 of config
    
    # Config snapshot
    rules: list[dict[str, Any]]
    thresholds: dict[str, Any]
    metadata: dict[str, Any]
    
    # Lifecycle
    is_active: bool = True
    deprecated_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"


@dataclass
class VersionPin:
    """Pin for a specific decision to a program version."""
    
    pin_id: UUID
    decision_id: UUID
    program_id: UUID
    version: str
    version_hash: str
    
    # Context
    pinned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str = "decision_execution"


class ProgramVersionService:
    """
    Manages program version pinning for reproducibility.
    
    Ensures that decisions can be re-evaluated using the exact
    same program configuration that was active at decision time.
    """
    
    def __init__(self):
        self.versions: dict[UUID, list[ProgramVersion]] = {}
        self.pins: dict[UUID, VersionPin] = {}  # decision_id -> pin
        self.active_versions: dict[UUID, str] = {}  # program_id -> version
    
    def register_version(
        self,
        program_id: UUID,
        version: str,
        rules: list[dict[str, Any]],
        thresholds: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        created_by: str = "admin",
    ) -> ProgramVersion:
        """Register a new program version."""
        
        # Generate version hash
        config_data = json.dumps({
            "rules": rules,
            "thresholds": thresholds,
        }, sort_keys=True)
        version_hash = hashlib.sha256(config_data.encode()).hexdigest()[:16]
        
        program_version = ProgramVersion(
            program_id=program_id,
            version=version,
            version_hash=version_hash,
            rules=rules,
            thresholds=thresholds,
            metadata=metadata or {},
            created_by=created_by,
        )
        
        if program_id not in self.versions:
            self.versions[program_id] = []
        
        self.versions[program_id].append(program_version)
        self.active_versions[program_id] = version
        
        return program_version
    
    def get_active_version(self, program_id: UUID) -> ProgramVersion | None:
        """Get the current active version for a program."""
        if program_id not in self.versions:
            return None
        
        active_ver = self.active_versions.get(program_id)
        if not active_ver:
            return None
        
        for v in self.versions[program_id]:
            if v.version == active_ver and v.is_active:
                return v
        
        return None
    
    def get_version(self, program_id: UUID, version: str) -> ProgramVersion | None:
        """Get a specific version of a program."""
        if program_id not in self.versions:
            return None
        
        for v in self.versions[program_id]:
            if v.version == version:
                return v
        
        return None
    
    def pin_decision(
        self,
        decision_id: UUID,
        program_id: UUID,
        reason: str = "decision_execution",
    ) -> VersionPin:
        """Pin a decision to the current active program version."""
        
        active = self.get_active_version(program_id)
        if not active:
            raise ValueError(f"No active version for program {program_id}")
        
        pin = VersionPin(
            pin_id=uuid4(),
            decision_id=decision_id,
            program_id=program_id,
            version=active.version,
            version_hash=active.version_hash,
            reason=reason,
        )
        
        self.pins[decision_id] = pin
        return pin
    
    def get_pinned_version(self, decision_id: UUID) -> ProgramVersion | None:
        """Get the pinned version for a decision."""
        pin = self.pins.get(decision_id)
        if not pin:
            return None
        
        return self.get_version(pin.program_id, pin.version)
    
    def deprecate_version(
        self,
        program_id: UUID,
        version: str,
    ) -> bool:
        """Mark a version as deprecated (still usable for pinned decisions)."""
        v = self.get_version(program_id, version)
        if not v:
            return False
        
        v.deprecated_at = datetime.now(timezone.utc)
        return True
    
    def list_versions(self, program_id: UUID) -> list[ProgramVersion]:
        """List all versions for a program."""
        return self.versions.get(program_id, [])
    
    def get_version_history(
        self,
        program_id: UUID,
        include_deprecated: bool = True,
    ) -> list[dict[str, Any]]:
        """Get version history for a program."""
        versions = self.list_versions(program_id)
        
        if not include_deprecated:
            versions = [v for v in versions if not v.deprecated_at]
        
        return [
            {
                "version": v.version,
                "version_hash": v.version_hash,
                "is_active": v.is_active,
                "deprecated_at": v.deprecated_at.isoformat() if v.deprecated_at else None,
                "created_at": v.created_at.isoformat(),
                "created_by": v.created_by,
                "rule_count": len(v.rules),
            }
            for v in sorted(versions, key=lambda x: x.created_at, reverse=True)
        ]


# Singleton instance
version_service = ProgramVersionService()
