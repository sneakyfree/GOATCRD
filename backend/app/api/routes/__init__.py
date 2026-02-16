"""API Routes package init."""
from app.api.routes.auth import router as auth_router
from app.api.routes.cases import router as cases_router
from app.api.routes.consents import router as consents_router
from app.api.routes.scenarios import router as scenarios_router
from app.api.routes.exports import router as exports_router
from app.api.routes.verification import router as verification_router
from app.api.routes.agents import router as agents_router
from app.api.routes.partners import router as partners_router
from app.api.routes.programs import router as programs_router
from app.api.routes.rulesets import router as rulesets_router
from app.api.routes.review import router as review_router
from app.api.routes.retention import router as retention_router
from app.api.routes.pulse import router as pulse_router
from app.api.routes.pulse import cases_pulse_router
from app.api.routes.fairness import router as fairness_router
from app.api.routes.alternative_data import router as alt_data_router
from app.api.routes.payments import router as payments_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.notifications import router as notifications_router

__all__ = [
    "auth_router",
    "cases_router",
    "consents_router",
    "scenarios_router",
    "exports_router",
    "verification_router",
    "agents_router",
    "partners_router",
    "programs_router",
    "rulesets_router",
    "review_router",
    "retention_router",
    "pulse_router",
    "cases_pulse_router",
    "fairness_router",
    "alt_data_router",
    "payments_router",
    "metrics_router",
    "notifications_router",
]
