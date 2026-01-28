"""
GOATCRD Schemas Package
All Pydantic schemas exported from here
"""
from app.schemas.base import (
    BaseSchema,
    ConfidenceScore,
    ErrorResponse,
    PaginatedResponse,
    ProvenanceRecord,
    ProvenanceState,
    SuccessResponse,
)
from app.schemas.user import (
    LoginRequest,
    RefreshTokenRequest,
    Token,
    TokenPayload,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.schemas.case import (
    CaseCreate,
    CaseResponse,
    IntakeChapter,
    IntakeDraftResponse,
    IntakeDraftUpdate,
    IntakeSchema,
    IntakeSnapshotResponse,
    IntakeSubmit,
    InviteCreate,
    InviteResponse,
)
from app.schemas.consent import (
    AccessLogEntry,
    ConsentEventResponse,
    ConsentGrant,
    ConsentRequest,
    ConsentResponse,
    ConsentRevoke,
    DataExportRequest,
)
from app.schemas.scenario import (
    CounterfactualRequest,
    CounterfactualResponse,
    ExplanationLayer,
    ExplanationResponse,
    RankedScenario,
    RankingRequest,
    RankingResponse,
    ScenarioListResponse,
    ScenarioResponse,
    ScenarioRunCreate,
    ScenarioRunResponse,
)

__all__ = [
    # Base
    "BaseSchema",
    "ConfidenceScore",
    "ErrorResponse",
    "PaginatedResponse",
    "ProvenanceRecord",
    "ProvenanceState",
    "SuccessResponse",
    # User
    "LoginRequest",
    "RefreshTokenRequest",
    "Token",
    "TokenPayload",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    # Case
    "CaseCreate",
    "CaseResponse",
    "IntakeChapter",
    "IntakeDraftResponse",
    "IntakeDraftUpdate",
    "IntakeSchema",
    "IntakeSnapshotResponse",
    "IntakeSubmit",
    "InviteCreate",
    "InviteResponse",
    # Consent
    "AccessLogEntry",
    "ConsentEventResponse",
    "ConsentGrant",
    "ConsentRequest",
    "ConsentResponse",
    "ConsentRevoke",
    "DataExportRequest",
    # Scenario
    "CounterfactualRequest",
    "CounterfactualResponse",
    "ExplanationLayer",
    "ExplanationResponse",
    "RankedScenario",
    "RankingRequest",
    "RankingResponse",
    "ScenarioListResponse",
    "ScenarioResponse",
    "ScenarioRunCreate",
    "ScenarioRunResponse",
]
