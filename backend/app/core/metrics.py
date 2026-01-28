"""
Prometheus Metrics Module
S6.2 - Backend observability and monitoring
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from collections import defaultdict
import time
import functools


@dataclass
class MetricValue:
    """A single metric observation."""
    value: float
    labels: dict[str, str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class Counter:
    """Prometheus-style counter metric."""
    
    def __init__(self, name: str, description: str, labels: list[str] | None = None):
        self.name = name
        self.description = description
        self.label_names = labels or []
        self._values: dict[tuple, float] = defaultdict(float)
    
    def inc(self, amount: float = 1.0, **labels):
        """Increment the counter."""
        key = self._make_key(labels)
        self._values[key] += amount
    
    def _make_key(self, labels: dict[str, str]) -> tuple:
        return tuple(labels.get(l, "") for l in self.label_names)
    
    def get(self, **labels) -> float:
        """Get current value."""
        key = self._make_key(labels)
        return self._values[key]
    
    def export(self) -> list[dict]:
        """Export for Prometheus scraping."""
        result = []
        for key, value in self._values.items():
            labels = dict(zip(self.label_names, key))
            result.append({
                "name": self.name,
                "type": "counter",
                "value": value,
                "labels": labels,
            })
        return result


class Gauge:
    """Prometheus-style gauge metric."""
    
    def __init__(self, name: str, description: str, labels: list[str] | None = None):
        self.name = name
        self.description = description
        self.label_names = labels or []
        self._values: dict[tuple, float] = {}
    
    def set(self, value: float, **labels):
        """Set the gauge value."""
        key = self._make_key(labels)
        self._values[key] = value
    
    def inc(self, amount: float = 1.0, **labels):
        """Increment the gauge."""
        key = self._make_key(labels)
        self._values[key] = self._values.get(key, 0) + amount
    
    def dec(self, amount: float = 1.0, **labels):
        """Decrement the gauge."""
        key = self._make_key(labels)
        self._values[key] = self._values.get(key, 0) - amount
    
    def _make_key(self, labels: dict[str, str]) -> tuple:
        return tuple(labels.get(l, "") for l in self.label_names)
    
    def get(self, **labels) -> float:
        """Get current value."""
        key = self._make_key(labels)
        return self._values.get(key, 0)
    
    def export(self) -> list[dict]:
        """Export for Prometheus scraping."""
        result = []
        for key, value in self._values.items():
            labels = dict(zip(self.label_names, key))
            result.append({
                "name": self.name,
                "type": "gauge",
                "value": value,
                "labels": labels,
            })
        return result


class Histogram:
    """Prometheus-style histogram metric."""
    
    DEFAULT_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float('inf'))
    
    def __init__(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        buckets: tuple[float, ...] | None = None,
    ):
        self.name = name
        self.description = description
        self.label_names = labels or []
        self.buckets = buckets or self.DEFAULT_BUCKETS
        self._observations: dict[tuple, list[float]] = defaultdict(list)
    
    def observe(self, value: float, **labels):
        """Record an observation."""
        key = self._make_key(labels)
        self._observations[key].append(value)
    
    def time(self, **labels):
        """Context manager for timing."""
        return HistogramTimer(self, labels)
    
    def _make_key(self, labels: dict[str, str]) -> tuple:
        return tuple(labels.get(l, "") for l in self.label_names)
    
    def get_percentile(self, percentile: float, **labels) -> float:
        """Get percentile value."""
        key = self._make_key(labels)
        observations = sorted(self._observations.get(key, []))
        if not observations:
            return 0.0
        idx = int(len(observations) * percentile / 100)
        return observations[min(idx, len(observations) - 1)]
    
    def export(self) -> list[dict]:
        """Export for Prometheus scraping."""
        result = []
        for key, observations in self._observations.items():
            labels = dict(zip(self.label_names, key))
            
            # Export bucket counts
            for bucket in self.buckets:
                count = sum(1 for o in observations if o <= bucket)
                result.append({
                    "name": f"{self.name}_bucket",
                    "type": "histogram",
                    "value": count,
                    "labels": {**labels, "le": str(bucket)},
                })
            
            # Export sum and count
            result.append({
                "name": f"{self.name}_sum",
                "type": "histogram",
                "value": sum(observations),
                "labels": labels,
            })
            result.append({
                "name": f"{self.name}_count",
                "type": "histogram",
                "value": len(observations),
                "labels": labels,
            })
        
        return result


class HistogramTimer:
    """Context manager for timing histogram observations."""
    
    def __init__(self, histogram: Histogram, labels: dict[str, str]):
        self.histogram = histogram
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        elapsed = time.perf_counter() - self.start_time
        self.histogram.observe(elapsed, **self.labels)


class MetricsRegistry:
    """Central registry for all metrics."""
    
    def __init__(self):
        self._metrics: dict[str, Counter | Gauge | Histogram] = {}
    
    def counter(self, name: str, description: str, labels: list[str] | None = None) -> Counter:
        """Create or get a counter."""
        if name not in self._metrics:
            self._metrics[name] = Counter(name, description, labels)
        return self._metrics[name]
    
    def gauge(self, name: str, description: str, labels: list[str] | None = None) -> Gauge:
        """Create or get a gauge."""
        if name not in self._metrics:
            self._metrics[name] = Gauge(name, description, labels)
        return self._metrics[name]
    
    def histogram(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        buckets: tuple[float, ...] | None = None,
    ) -> Histogram:
        """Create or get a histogram."""
        if name not in self._metrics:
            self._metrics[name] = Histogram(name, description, labels, buckets)
        return self._metrics[name]
    
    def export_all(self) -> list[dict]:
        """Export all metrics."""
        result = []
        for metric in self._metrics.values():
            result.extend(metric.export())
        return result
    
    def export_prometheus_format(self) -> str:
        """Export in Prometheus text format."""
        lines = []
        for metric in self._metrics.values():
            lines.append(f"# HELP {metric.name} {metric.description}")
            lines.append(f"# TYPE {metric.name} {type(metric).__name__.lower()}")
            
            for item in metric.export():
                label_str = ",".join(f'{k}="{v}"' for k, v in item["labels"].items())
                if label_str:
                    lines.append(f'{item["name"]}{{{label_str}}} {item["value"]}')
                else:
                    lines.append(f'{item["name"]} {item["value"]}')
        
        return "\n".join(lines)


# Global registry
registry = MetricsRegistry()

# GOATCRD Application Metrics
# ===========================

# Request metrics
http_requests_total = registry.counter(
    "goatcrd_http_requests_total",
    "Total HTTP requests",
    labels=["method", "endpoint", "status"],
)

http_request_duration = registry.histogram(
    "goatcrd_http_request_duration_seconds",
    "HTTP request duration in seconds",
    labels=["method", "endpoint"],
)

# Scenario metrics
scenarios_generated_total = registry.counter(
    "goatcrd_scenarios_generated_total",
    "Total scenarios generated",
    labels=["program", "outcome"],
)

scenario_generation_duration = registry.histogram(
    "goatcrd_scenario_generation_duration_seconds",
    "Scenario generation duration",
    labels=["program"],
)

# Agent metrics
agent_invocations_total = registry.counter(
    "goatcrd_agent_invocations_total",
    "Total agent invocations",
    labels=["agent_type"],
)

agent_processing_duration = registry.histogram(
    "goatcrd_agent_processing_duration_seconds",
    "Agent processing duration",
    labels=["agent_type"],
)

# Review queue metrics
review_queue_size = registry.gauge(
    "goatcrd_review_queue_size",
    "Current review queue size",
    labels=["priority"],
)

review_decisions_total = registry.counter(
    "goatcrd_review_decisions_total",
    "Total review decisions",
    labels=["outcome"],
)

# Fairness metrics
fairness_tests_total = registry.counter(
    "goatcrd_fairness_tests_total",
    "Total fairness tests run",
    labels=["result"],
)

disparate_impact_ratio = registry.gauge(
    "goatcrd_disparate_impact_ratio",
    "Current disparate impact ratio",
    labels=["program", "attribute"],
)

# Partner/LaaS metrics
partner_api_calls_total = registry.counter(
    "goatcrd_partner_api_calls_total",
    "Total partner API calls",
    labels=["partner_id", "endpoint"],
)

partner_session_duration = registry.histogram(
    "goatcrd_partner_session_duration_seconds",
    "Partner session duration",
    labels=["partner_id"],
)

# Consent metrics
consents_granted_total = registry.counter(
    "goatcrd_consents_granted_total",
    "Total consents granted",
    labels=["consent_type"],
)

consents_revoked_total = registry.counter(
    "goatcrd_consents_revoked_total",
    "Total consents revoked",
    labels=["consent_type", "reason"],
)

# Active sessions gauge
active_sessions = registry.gauge(
    "goatcrd_active_sessions",
    "Current active sessions",
)

# Database metrics
db_query_duration = registry.histogram(
    "goatcrd_db_query_duration_seconds",
    "Database query duration",
    labels=["query_type"],
)

db_connections_active = registry.gauge(
    "goatcrd_db_connections_active",
    "Active database connections",
)


# Decorators
def track_duration(histogram: Histogram, **labels):
    """Decorator to track function duration."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with histogram.time(**labels):
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with histogram.time(**labels):
                return func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def count_calls(counter: Counter, **labels):
    """Decorator to count function calls."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            counter.inc(**labels)
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            counter.inc(**labels)
            return func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
