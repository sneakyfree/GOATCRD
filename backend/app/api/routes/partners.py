"""
GOATCRD Partner API Routes
Embedded finance and partner management
"""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel

from app.api.deps import CurrentUser, DBSession, AdminUser
from app.sdk import laas_sdk, widget_embed

router = APIRouter(prefix="/partners", tags=["partners"])


class RegisterPartnerRequest(BaseModel):
    """Request to register a partner."""
    
    partner_name: str
    webhook_url: str | None = None
    allowed_programs: list[str] | None = None
    branding: dict[str, str] | None = None


class PartnerResponse(BaseModel):
    """Partner registration response."""
    
    partner_id: str
    partner_name: str
    api_key: str
    webhook_url: str | None
    is_active: bool


class CreateSessionRequest(BaseModel):
    """Request to create embedded session."""
    
    consumer_reference: str
    prefilled_data: dict[str, Any] | None = None
    mode: str = "full"
    return_url: str | None = None


class SessionResponse(BaseModel):
    """Embedded session response."""
    
    session_id: str
    embed_url: str
    expires_at: str | None
    widget_config: dict[str, Any]


class WidgetCodeResponse(BaseModel):
    """Widget embed code response."""
    
    html_embed: str
    react_component: str


@router.post("/register", response_model=PartnerResponse)
async def register_partner(
    request: RegisterPartnerRequest,
    current_user: AdminUser,
    db: DBSession,
) -> PartnerResponse:
    """
    Register a new LaaS partner.
    
    Requires admin role.
    """
    config = laas_sdk.register_partner(
        partner_name=request.partner_name,
        webhook_url=request.webhook_url,
        allowed_programs=request.allowed_programs,
        branding=request.branding,
    )
    
    return PartnerResponse(
        partner_id=str(config.partner_id),
        partner_name=config.partner_name,
        api_key=config.api_key,
        webhook_url=config.webhook_url,
        is_active=config.is_active,
    )


@router.post("/sessions", response_model=SessionResponse)
async def create_embed_session(
    request: CreateSessionRequest,
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> SessionResponse:
    """
    Create an embedded session.
    
    Requires partner API key in X-API-Key header.
    """
    partner = laas_sdk.validate_api_key(x_api_key)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    try:
        session = laas_sdk.create_session(
            partner_id=partner.partner_id,
            consumer_reference=request.consumer_reference,
            prefilled_data=request.prefilled_data,
            mode=request.mode,
            return_url=request.return_url,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    embed_url = laas_sdk.get_embed_url(session.session_id)
    widget_config = laas_sdk.generate_widget_config(session.session_id)
    
    return SessionResponse(
        session_id=str(session.session_id),
        embed_url=embed_url,
        expires_at=session.expires_at.isoformat() if session.expires_at else None,
        widget_config=widget_config,
    )


@router.get("/sessions/{session_id}/widget-code", response_model=WidgetCodeResponse)
async def get_widget_code(
    session_id: UUID,
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> WidgetCodeResponse:
    """
    Get widget embed code for a session.
    """
    partner = laas_sdk.validate_api_key(x_api_key)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    session = laas_sdk.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )
    
    if session.partner_id != partner.partner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session belongs to different partner",
        )
    
    return WidgetCodeResponse(
        html_embed=widget_embed.generate_script(session_id),
        react_component=widget_embed.generate_react_component(session_id),
    )


@router.get("/sessions/{session_id}")
async def get_session_status(
    session_id: UUID,
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> dict[str, Any]:
    """
    Get session status and results.
    """
    partner = laas_sdk.validate_api_key(x_api_key)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    session = laas_sdk.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )
    
    if session.partner_id != partner.partner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session belongs to different partner",
        )
    
    return {
        "session_id": str(session.session_id),
        "consumer_reference": session.consumer_reference,
        "mode": session.mode,
        "created_at": session.created_at.isoformat(),
        "expires_at": session.expires_at.isoformat() if session.expires_at else None,
        "status": "active" if session.expires_at and session.expires_at > session.created_at else "expired",
    }
