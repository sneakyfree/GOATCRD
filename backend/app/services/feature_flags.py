"""
Feature Flags Service
S4.5 - Environment-based feature flag management
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
import os


@dataclass
class FeatureFlag:
    """Represents a feature flag configuration."""
    
    flag_id: UUID
    key: str  # e.g., "ENABLE_FAIRNESS_CHECKS"
    name: str
    description: str
    
    # Values
    default_value: bool = False
    environment_overrides: dict[str, bool] = field(default_factory=dict)
    
    # Targeting
    user_percentage: float = 100.0  # 0-100
    allowed_partners: list[str] = field(default_factory=list)
    
    # Metadata
    category: str = "general"
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class FeatureFlagService:
    """
    Environment-aware feature flag management.
    
    Supports:
    - Environment-specific overrides (dev, staging, prod)
    - Percentage rollouts
    - Partner-specific flags
    """
    
    def __init__(self):
        self.flags: dict[str, FeatureFlag] = {}
        self.environment = os.getenv("GOATCRD_ENV", "development")
        self._init_default_flags()
    
    def _init_default_flags(self):
        """Initialize default feature flags."""
        defaults = [
            {
                "key": "ENABLE_FAIRNESS_GATE",
                "name": "Fairness Gate",
                "description": "Block deployments that fail fairness thresholds",
                "default_value": False,
                "environment_overrides": {"production": True, "staging": True},
                "category": "compliance",
            },
            {
                "key": "ENABLE_LDA_SEARCH",
                "name": "LDA Search Automation",
                "description": "Automated Less Discriminatory Alternative search",
                "default_value": True,
                "category": "fairness",
            },
            {
                "key": "ENABLE_DOWNSTREAM_DISABLE",
                "name": "Downstream Disablement",
                "description": "Automatically disable downstream programs on deprecation",
                "default_value": True,
                "environment_overrides": {"development": False},
                "category": "governance",
            },
            {
                "key": "ENABLE_VERSION_PINNING",
                "name": "Version Pinning",
                "description": "Pin decisions to specific program versions",
                "default_value": True,
                "category": "reproducibility",
            },
            {
                "key": "ENABLE_AUDIT_SNAPSHOTS",
                "name": "Audit Snapshots",
                "description": "Create immutable snapshots for audit trail",
                "default_value": True,
                "category": "compliance",
            },
            {
                "key": "ENABLE_HUMAN_REVIEW_OVERRIDES",
                "name": "Human Review Overrides",
                "description": "Allow human reviewers to override automated decisions",
                "default_value": True,
                "category": "hitl",
            },
            {
                "key": "ENABLE_PARTNER_WEBHOOKS",
                "name": "Partner Webhooks",
                "description": "Send webhook notifications to LaaS partners",
                "default_value": True,
                "environment_overrides": {"development": False},
                "category": "laas",
            },
            {
                "key": "ENABLE_SCENARIO_CACHING",
                "name": "Scenario Caching",
                "description": "Cache scenario results for performance",
                "default_value": False,
                "environment_overrides": {"production": True},
                "category": "performance",
            },
        ]
        
        for config in defaults:
            self.register_flag(**config)
    
    def register_flag(
        self,
        key: str,
        name: str,
        description: str,
        default_value: bool = False,
        environment_overrides: dict[str, bool] | None = None,
        category: str = "general",
    ) -> FeatureFlag:
        """Register a new feature flag."""
        
        flag = FeatureFlag(
            flag_id=uuid4(),
            key=key,
            name=name,
            description=description,
            default_value=default_value,
            environment_overrides=environment_overrides or {},
            category=category,
        )
        
        self.flags[key] = flag
        return flag
    
    def is_enabled(
        self,
        key: str,
        partner_id: str | None = None,
    ) -> bool:
        """
        Check if a feature flag is enabled.
        
        Checks in order:
        1. Partner-specific override
        2. Environment override
        3. Default value
        """
        flag = self.flags.get(key)
        if not flag or not flag.is_active:
            return False
        
        # Check partner targeting
        if partner_id and flag.allowed_partners:
            if partner_id not in flag.allowed_partners:
                return False
        
        # Check environment override
        if self.environment in flag.environment_overrides:
            return flag.environment_overrides[self.environment]
        
        return flag.default_value
    
    def get_flag(self, key: str) -> FeatureFlag | None:
        """Get a specific feature flag."""
        return self.flags.get(key)
    
    def update_flag(
        self,
        key: str,
        default_value: bool | None = None,
        environment_overrides: dict[str, bool] | None = None,
        is_active: bool | None = None,
    ) -> FeatureFlag | None:
        """Update a feature flag."""
        flag = self.flags.get(key)
        if not flag:
            return None
        
        if default_value is not None:
            flag.default_value = default_value
        
        if environment_overrides is not None:
            flag.environment_overrides = environment_overrides
        
        if is_active is not None:
            flag.is_active = is_active
        
        flag.updated_at = datetime.now(timezone.utc)
        return flag
    
    def list_flags(self, category: str | None = None) -> list[FeatureFlag]:
        """List all feature flags, optionally filtered by category."""
        flags = list(self.flags.values())
        
        if category:
            flags = [f for f in flags if f.category == category]
        
        return sorted(flags, key=lambda x: x.key)
    
    def get_flags_summary(self) -> dict[str, Any]:
        """Get summary of all flags for current environment."""
        return {
            "environment": self.environment,
            "flags": {
                key: self.is_enabled(key)
                for key in self.flags.keys()
            },
            "categories": list(set(f.category for f in self.flags.values())),
        }
    
    def export_flags(self) -> list[dict[str, Any]]:
        """Export all flags for admin UI."""
        return [
            {
                "key": f.key,
                "name": f.name,
                "description": f.description,
                "default_value": f.default_value,
                "environment_overrides": f.environment_overrides,
                "current_value": self.is_enabled(f.key),
                "category": f.category,
                "is_active": f.is_active,
            }
            for f in self.list_flags()
        ]


# Singleton instance
feature_flags = FeatureFlagService()


# Convenience functions
def is_enabled(key: str, partner_id: str | None = None) -> bool:
    """Check if a feature is enabled."""
    return feature_flags.is_enabled(key, partner_id)


def get_all_flags() -> dict[str, bool]:
    """Get all flag values for current environment."""
    return feature_flags.get_flags_summary()["flags"]
