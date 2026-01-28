"""
GOATCRD Lending-as-a-Service (LaaS) SDK
Embeddable credit decisioning for partners
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import UUID, uuid4
import hmac
import hashlib
import json


@dataclass
class PartnerConfig:
    """Configuration for a LaaS partner."""
    
    partner_id: UUID
    partner_name: str
    api_key: str
    webhook_url: str | None = None
    
    # Permissions
    allowed_programs: list[str] = field(default_factory=list)
    rate_limit_per_minute: int = 60
    
    # Branding
    branding: dict[str, str] = field(default_factory=dict)
    
    # Callbacks
    callback_events: list[str] = field(default_factory=list)
    
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EmbedContext:
    """Context for an embedded session."""
    
    session_id: UUID
    partner_id: UUID
    consumer_reference: str  # Partner's consumer ID
    
    # Pre-filled data from partner
    prefilled_data: dict[str, Any] = field(default_factory=dict)
    
    # Session settings
    mode: str = "full"  # full, prequalify, what_if
    return_url: str | None = None
    
    # Tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None


@dataclass
class WebhookPayload:
    """Payload for partner webhook."""
    
    event_type: str
    partner_id: UUID
    session_id: UUID
    consumer_reference: str
    
    data: dict[str, Any]
    
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signature: str | None = None


class LaaSSDK:
    """
    Lending-as-a-Service SDK for embedded credit decisioning.
    
    Enables partners to embed GOATCRD scenario generation
    into their own applications.
    """
    
    def __init__(self):
        self.partners: dict[UUID, PartnerConfig] = {}
        self.sessions: dict[UUID, EmbedContext] = {}
        self._webhook_callback: Callable | None = None
    
    def register_partner(
        self,
        partner_name: str,
        webhook_url: str | None = None,
        allowed_programs: list[str] | None = None,
        branding: dict[str, str] | None = None,
    ) -> PartnerConfig:
        """
        Register a new LaaS partner.
        
        Returns partner config with API key.
        """
        partner_id = uuid4()
        api_key = self._generate_api_key(partner_id)
        
        config = PartnerConfig(
            partner_id=partner_id,
            partner_name=partner_name,
            api_key=api_key,
            webhook_url=webhook_url,
            allowed_programs=allowed_programs or ["*"],
            branding=branding or {},
            callback_events=["session.completed", "scenario.eligible", "consent.granted"],
        )
        
        self.partners[partner_id] = config
        return config
    
    def validate_api_key(self, api_key: str) -> PartnerConfig | None:
        """Validate an API key and return partner config."""
        for config in self.partners.values():
            if config.api_key == api_key and config.is_active:
                return config
        return None
    
    def create_session(
        self,
        partner_id: UUID,
        consumer_reference: str,
        prefilled_data: dict[str, Any] | None = None,
        mode: str = "full",
        return_url: str | None = None,
    ) -> EmbedContext:
        """
        Create an embedded session for a partner.
        
        Returns session context with embed URL.
        """
        if partner_id not in self.partners:
            raise ValueError("Partner not found")
        
        partner = self.partners[partner_id]
        if not partner.is_active:
            raise ValueError("Partner is not active")
        
        session_id = uuid4()
        expires_at = datetime.now(timezone.utc).replace(
            hour=23, minute=59, second=59
        )  # End of day
        
        context = EmbedContext(
            session_id=session_id,
            partner_id=partner_id,
            consumer_reference=consumer_reference,
            prefilled_data=prefilled_data or {},
            mode=mode,
            return_url=return_url,
            expires_at=expires_at,
        )
        
        self.sessions[session_id] = context
        return context
    
    def get_embed_url(
        self,
        session_id: UUID,
        base_url: str = "https://app.goatcrd.com",
    ) -> str:
        """
        Generate embed URL for a session.
        """
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        session = self.sessions[session_id]
        token = self._generate_session_token(session)
        
        return f"{base_url}/embed/{session_id}?token={token}&mode={session.mode}"
    
    def get_session(self, session_id: UUID) -> EmbedContext | None:
        """Get session by ID."""
        session = self.sessions.get(session_id)
        
        if session and session.expires_at:
            if session.expires_at < datetime.now(timezone.utc):
                return None
        
        return session
    
    async def send_webhook(
        self,
        partner_id: UUID,
        event_type: str,
        session_id: UUID,
        consumer_reference: str,
        data: dict[str, Any],
    ) -> bool:
        """
        Send webhook to partner.
        
        Returns True if successful.
        """
        if partner_id not in self.partners:
            return False
        
        partner = self.partners[partner_id]
        
        if not partner.webhook_url:
            return False
        
        if event_type not in partner.callback_events:
            return False
        
        payload = WebhookPayload(
            event_type=event_type,
            partner_id=partner_id,
            session_id=session_id,
            consumer_reference=consumer_reference,
            data=data,
        )
        
        # Sign payload
        payload.signature = self._sign_payload(payload, partner.api_key)
        
        # In production, this would make HTTP request
        if self._webhook_callback:
            await self._webhook_callback(partner.webhook_url, payload)
        
        return True
    
    def generate_widget_config(
        self,
        session_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate configuration for JavaScript widget.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found or expired")
        
        partner = self.partners.get(session.partner_id)
        if not partner:
            raise ValueError("Partner not found")
        
        return {
            "sessionId": str(session_id),
            "mode": session.mode,
            "returnUrl": session.return_url,
            "branding": partner.branding,
            "prefilled": list(session.prefilled_data.keys()),
            "features": {
                "whatIf": session.mode in ("full", "what_if"),
                "scenarios": session.mode in ("full", "prequalify"),
                "explanations": True,
            },
        }
    
    def _generate_api_key(self, partner_id: UUID) -> str:
        """Generate API key for partner."""
        import secrets
        return f"goat_{secrets.token_urlsafe(32)}"
    
    def _generate_session_token(self, session: EmbedContext) -> str:
        """Generate session token."""
        import secrets
        return secrets.token_urlsafe(24)
    
    def _sign_payload(self, payload: WebhookPayload, api_key: str) -> str:
        """Sign webhook payload."""
        data = json.dumps({
            "event_type": payload.event_type,
            "session_id": str(payload.session_id),
            "timestamp": payload.timestamp.isoformat(),
        }, sort_keys=True)
        
        return hmac.new(
            api_key.encode(),
            data.encode(),
            hashlib.sha256,
        ).hexdigest()


@dataclass
class WidgetEmbed:
    """JavaScript widget embed code generator."""
    
    sdk_url: str = "https://cdn.goatcrd.com/widget.js"
    
    def generate_script(
        self,
        session_id: UUID,
        container_id: str = "goatcrd-container",
        options: dict[str, Any] | None = None,
    ) -> str:
        """Generate embed script tag."""
        opts = json.dumps(options or {})
        
        return f'''
<div id="{container_id}"></div>
<script src="{self.sdk_url}"></script>
<script>
  GOATCRD.init({{
    sessionId: "{session_id}",
    container: "#{container_id}",
    options: {opts},
    onComplete: function(result) {{
      console.log("GOATCRD complete:", result);
    }},
    onError: function(error) {{
      console.error("GOATCRD error:", error);
    }}
  }});
</script>
'''
    
    def generate_react_component(self, session_id: UUID) -> str:
        """Generate React component usage."""
        return f'''
import {{ GOATCRDWidget }} from '@goatcrd/react';

function CreditCheck() {{
  return (
    <GOATCRDWidget
      sessionId="{session_id}"
      onComplete={{(result) => console.log(result)}}
      onError={{(error) => console.error(error)}}
    />
  );
}}
'''


# Singleton instance
laas_sdk = LaaSSDK()
widget_embed = WidgetEmbed()
