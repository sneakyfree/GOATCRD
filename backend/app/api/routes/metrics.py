"""
GOATCRD Metrics API Route
Admin-facing observability dashboard endpoint
"""
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import AdminUser
from app.core.metrics import (
    registry,
    http_requests_total,
    http_request_duration,
    scenarios_generated_total,
    scenario_generation_duration,
    agent_invocations_total,
    agent_processing_duration,
    review_queue_size,
    review_decisions_total,
    fairness_tests_total,
    disparate_impact_ratio,
    partner_api_calls_total,
    consents_granted_total,
    consents_revoked_total,
    active_sessions,
    db_connections_active,
)

router = APIRouter(prefix="/metrics", tags=["metrics"])


class MetricSummary(BaseModel):
    """Summary of a single metric."""

    name: str
    type: str
    value: float
    labels: dict[str, str] = {}


class DashboardResponse(BaseModel):
    """Observability dashboard data."""

    timestamp: str
    uptime_seconds: float
    request_metrics: dict[str, Any]
    scenario_metrics: dict[str, Any]
    agent_metrics: dict[str, Any]
    review_metrics: dict[str, Any]
    fairness_metrics: dict[str, Any]
    partner_metrics: dict[str, Any]
    consent_metrics: dict[str, Any]
    system_metrics: dict[str, Any]


_start_time = time.time()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_metrics(
    current_user: AdminUser,
) -> DashboardResponse:
    """
    Get formatted metrics for the admin observability dashboard.

    Requires admin role.
    """
    now = datetime.now(timezone.utc)
    uptime = time.time() - _start_time

    return DashboardResponse(
        timestamp=now.isoformat(),
        uptime_seconds=round(uptime, 2),
        request_metrics={
            "total_requests": sum(
                v for v in http_requests_total._values.values()
            ),
            "by_status": {
                "2xx": sum(
                    v
                    for k, v in http_requests_total._values.items()
                    if k and len(k) > 2 and k[2].startswith("2")
                ),
                "4xx": sum(
                    v
                    for k, v in http_requests_total._values.items()
                    if k and len(k) > 2 and k[2].startswith("4")
                ),
                "5xx": sum(
                    v
                    for k, v in http_requests_total._values.items()
                    if k and len(k) > 2 and k[2].startswith("5")
                ),
            },
            "avg_latency_ms": round(
                http_request_duration.get_percentile(50) * 1000, 2
            ),
            "p95_latency_ms": round(
                http_request_duration.get_percentile(95) * 1000, 2
            ),
            "p99_latency_ms": round(
                http_request_duration.get_percentile(99) * 1000, 2
            ),
        },
        scenario_metrics={
            "total_generated": sum(
                v for v in scenarios_generated_total._values.values()
            ),
            "avg_generation_ms": round(
                scenario_generation_duration.get_percentile(50) * 1000, 2
            ),
        },
        agent_metrics={
            "total_invocations": sum(
                v for v in agent_invocations_total._values.values()
            ),
            "avg_processing_ms": round(
                agent_processing_duration.get_percentile(50) * 1000, 2
            ),
        },
        review_metrics={
            "queue_size": sum(v for v in review_queue_size._values.values()),
            "total_decisions": sum(
                v for v in review_decisions_total._values.values()
            ),
        },
        fairness_metrics={
            "total_tests": sum(
                v for v in fairness_tests_total._values.values()
            ),
        },
        partner_metrics={
            "total_api_calls": sum(
                v for v in partner_api_calls_total._values.values()
            ),
        },
        consent_metrics={
            "total_granted": sum(
                v for v in consents_granted_total._values.values()
            ),
            "total_revoked": sum(
                v for v in consents_revoked_total._values.values()
            ),
        },
        system_metrics={
            "active_sessions": active_sessions.get(),
            "db_connections": db_connections_active.get(),
            "uptime_hours": round(uptime / 3600, 2),
        },
    )


@router.get("/prometheus")
async def get_prometheus_metrics(
    current_user: AdminUser,
) -> str:
    """
    Export metrics in Prometheus text format.

    Requires admin role.
    """
    return registry.export_prometheus_format()


@router.get("/raw")
async def get_raw_metrics(
    current_user: AdminUser,
) -> dict[str, Any]:
    """
    Get all raw metrics as JSON.

    Requires admin role.
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": registry.export_all(),
    }
