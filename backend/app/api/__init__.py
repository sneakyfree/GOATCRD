"""API package init."""
from fastapi import APIRouter

from app.api.routes import (
    auth_router,
    cases_router,
    consents_router,
    scenarios_router,
    exports_router,
    verification_router,
    agents_router,
    partners_router,
    programs_router,
    rulesets_router,
    review_router,
    retention_router,
    pulse_router,
    cases_pulse_router,
    fairness_router,
    alt_data_router,
)

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(cases_router)
api_router.include_router(consents_router)
api_router.include_router(scenarios_router)
api_router.include_router(exports_router)
api_router.include_router(verification_router)
api_router.include_router(agents_router)
api_router.include_router(partners_router)
api_router.include_router(programs_router)
api_router.include_router(rulesets_router)
api_router.include_router(review_router)
api_router.include_router(retention_router)
api_router.include_router(pulse_router)
api_router.include_router(cases_pulse_router)
api_router.include_router(fairness_router)
api_router.include_router(alt_data_router)

__all__ = ["api_router"]




