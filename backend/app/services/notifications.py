"""
GOATCRD Notification Service
Handles invite delivery via email/SMS with provider abstraction and feature flags.
"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailProvider(ABC):
    """Abstract email provider interface."""
    
    @abstractmethod
    async def send(self, to: str, subject: str, body_html: str) -> bool:
        """Send an email. Returns True on success."""
        ...


class SMSProvider(ABC):
    """Abstract SMS provider interface."""
    
    @abstractmethod
    async def send(self, to: str, body: str) -> bool:
        """Send an SMS. Returns True on success."""
        ...


class LogOnlyEmailProvider(EmailProvider):
    """Development email provider — logs instead of sending."""
    
    async def send(self, to: str, subject: str, body_html: str) -> bool:
        logger.info(
            "EMAIL [dev-mode] to=%s subject=%s body_length=%d",
            to, subject, len(body_html),
        )
        return True


class LogOnlySMSProvider(SMSProvider):
    """Development SMS provider — logs instead of sending."""
    
    async def send(self, to: str, body: str) -> bool:
        logger.info("SMS [dev-mode] to=%s body=%s", to, body[:100])
        return True


class SendGridEmailProvider(EmailProvider):
    """SendGrid email provider for production use."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def send(self, to: str, subject: str, body_html: str) -> bool:
        try:
            import sendgrid
            from sendgrid.helpers.mail import Content, Email, Mail, To
            
            sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
            from_email = Email(getattr(settings, "from_email", "noreply@goatcrd.com"))
            to_email = To(to)
            content = Content("text/html", body_html)
            mail = Mail(from_email, to_email, subject, content)
            
            response = sg.client.mail.send.post(request_body=mail.get())
            success = response.status_code in (200, 201, 202)
            
            if success:
                logger.info("EMAIL sent to=%s subject=%s status=%d", to, subject, response.status_code)
            else:
                logger.error("EMAIL failed to=%s status=%d", to, response.status_code)
            
            return success
        except ImportError:
            logger.warning("sendgrid package not installed — falling back to log-only")
            return await LogOnlyEmailProvider().send(to, subject, body_html)
        except Exception as e:
            logger.error("EMAIL error to=%s: %s", to, str(e))
            return False


class TwilioSMSProvider(SMSProvider):
    """Twilio SMS provider for production use."""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
    
    async def send(self, to: str, body: str) -> bool:
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            message = client.messages.create(
                body=body,
                from_=self.from_number,
                to=to,
            )
            
            logger.info("SMS sent to=%s sid=%s", to, message.sid)
            return True
        except ImportError:
            logger.warning("twilio package not installed — falling back to log-only")
            return await LogOnlySMSProvider().send(to, body)
        except Exception as e:
            logger.error("SMS error to=%s: %s", to, str(e))
            return False


def render_invite_email(token: str, expires_at: datetime, base_url: str | None = None) -> str:
    """Render invite email HTML template."""
    url = base_url or getattr(settings, "frontend_url", "https://app.goatcrd.com")
    invite_url = f"{url}/intake/invite/{token}"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body style="font-family: system-ui, sans-serif; background: #f8fafc; padding: 2rem;">
        <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h1 style="color: #0f172a; font-size: 1.5rem; margin-bottom: 0.5rem;">
                🐐 GOATCRD
            </h1>
            <h2 style="color: #334155; font-size: 1.1rem; font-weight: 500;">
                You've been invited to complete your credit intake
            </h2>
            <p style="color: #64748b; line-height: 1.6;">
                A credit professional has invited you to securely provide your financial
                information. This link is unique to you and will expire on
                <strong>{expires_at.strftime('%B %d, %Y at %I:%M %p')}</strong>.
            </p>
            <div style="text-align: center; margin: 2rem 0;">
                <a href="{invite_url}"
                   style="display: inline-block; background: #3b82f6; color: white;
                          padding: 12px 32px; border-radius: 8px; text-decoration: none;
                          font-weight: 600; font-size: 1rem;">
                    Start Your Intake →
                </a>
            </div>
            <p style="color: #94a3b8; font-size: 0.85rem;">
                This is a secure, one-time link. Your data is encrypted and protected
                under Section 1033 consumer data rights.
            </p>
        </div>
    </body>
    </html>
    """


def render_invite_sms(token: str, expires_hours: int, base_url: str | None = None) -> str:
    """Render invite SMS body."""
    url = base_url or getattr(settings, "frontend_url", "https://app.goatcrd.com")
    return f"GOATCRD: Complete your credit intake here: {url}/intake/invite/{token} (expires in {expires_hours}h)"


class NotificationService:
    """
    Unified notification service with feature-flag gating.
    
    When ENABLE_EMAIL_DELIVERY / ENABLE_SMS_DELIVERY are false (default),
    notifications are logged but not actually sent. This lets the full
    invite workflow execute without requiring vendor credentials.
    """
    
    def __init__(self):
        self._email_provider = self._create_email_provider()
        self._sms_provider = self._create_sms_provider()
    
    def _create_email_provider(self) -> EmailProvider:
        api_key = getattr(settings, "sendgrid_api_key", "")
        enabled = getattr(settings, "enable_email_delivery", False)
        
        if enabled and api_key:
            return SendGridEmailProvider(api_key)
        return LogOnlyEmailProvider()
    
    def _create_sms_provider(self) -> SMSProvider:
        sid = getattr(settings, "twilio_account_sid", "")
        token = getattr(settings, "twilio_auth_token", "")
        number = getattr(settings, "twilio_from_number", "")
        enabled = getattr(settings, "enable_sms_delivery", False)
        
        if enabled and sid and token and number:
            return TwilioSMSProvider(sid, token, number)
        return LogOnlySMSProvider()
    
    async def send_email(self, to: str, subject: str, body_html: str) -> bool:
        """Send an email via the configured provider."""
        return await self._email_provider.send(to, subject, body_html)
    
    async def send_sms(self, to: str, body: str) -> bool:
        """Send an SMS via the configured provider."""
        return await self._sms_provider.send(to, body)
    
    async def send_invite(
        self,
        token: str,
        expires_at: datetime,
        email: str | None = None,
        phone: str | None = None,
        expires_hours: int = 72,
    ) -> dict[str, bool]:
        """
        Send an invite via email and/or SMS.
        Returns dict of {channel: success_bool}.
        """
        results: dict[str, bool] = {}
        
        if email:
            html = render_invite_email(token, expires_at)
            results["email"] = await self.send_email(
                to=email,
                subject="Your GOATCRD Intake Link",
                body_html=html,
            )
        
        if phone:
            body = render_invite_sms(token, expires_hours)
            results["sms"] = await self.send_sms(to=phone, body=body)
        
        return results
