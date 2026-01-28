"""
Tests for GOATCRD LaaS SDK
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.sdk.laas import (
    LaaSSDK,
    PartnerConfig,
    EmbedContext,
    WebhookPayload,
    WidgetEmbed,
)


class TestLaaSSDK:
    """Test suite for LaaSSDK."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sdk = LaaSSDK()
    
    def test_register_partner_creates_config(self):
        """Test partner registration creates config."""
        config = self.sdk.register_partner(
            partner_name="Test Partner",
            webhook_url="https://example.com/webhook",
            allowed_programs=["personal_loan", "credit_builder"],
            branding={"primary_color": "#0066FF"},
        )
        
        assert config is not None
        assert config.partner_name == "Test Partner"
        assert config.api_key.startswith("goat_")
        assert config.webhook_url == "https://example.com/webhook"
        assert config.is_active is True
    
    def test_validate_api_key_returns_partner(self):
        """Test API key validation."""
        config = self.sdk.register_partner(
            partner_name="Validation Test",
        )
        
        validated = self.sdk.validate_api_key(config.api_key)
        
        assert validated is not None
        assert validated.partner_id == config.partner_id
    
    def test_validate_api_key_returns_none_for_invalid(self):
        """Test invalid API key returns None."""
        result = self.sdk.validate_api_key("invalid_key_12345")
        
        assert result is None
    
    def test_create_session_success(self):
        """Test session creation."""
        config = self.sdk.register_partner(partner_name="Session Test")
        
        session = self.sdk.create_session(
            partner_id=config.partner_id,
            consumer_reference="consumer_123",
            prefilled_data={"annual_income": 75000},
            mode="full",
            return_url="https://partner.com/callback",
        )
        
        assert session is not None
        assert session.consumer_reference == "consumer_123"
        assert session.mode == "full"
        assert session.prefilled_data["annual_income"] == 75000
    
    def test_create_session_fails_for_unknown_partner(self):
        """Test session creation fails for unknown partner."""
        with pytest.raises(ValueError, match="Partner not found"):
            self.sdk.create_session(
                partner_id=uuid4(),
                consumer_reference="test",
            )
    
    def test_create_session_fails_for_inactive_partner(self):
        """Test session creation fails for inactive partner."""
        config = self.sdk.register_partner(partner_name="Inactive Test")
        config.is_active = False
        
        with pytest.raises(ValueError, match="not active"):
            self.sdk.create_session(
                partner_id=config.partner_id,
                consumer_reference="test",
            )
    
    def test_get_embed_url_returns_valid_url(self):
        """Test embed URL generation."""
        config = self.sdk.register_partner(partner_name="URL Test")
        session = self.sdk.create_session(
            partner_id=config.partner_id,
            consumer_reference="test",
            mode="prequalify",
        )
        
        url = self.sdk.get_embed_url(session.session_id)
        
        assert url.startswith("https://app.goatcrd.com/embed/")
        assert str(session.session_id) in url
        assert "mode=prequalify" in url
    
    def test_get_embed_url_fails_for_unknown_session(self):
        """Test embed URL fails for unknown session."""
        with pytest.raises(ValueError, match="Session not found"):
            self.sdk.get_embed_url(uuid4())
    
    def test_get_session_returns_valid_session(self):
        """Test getting session by ID."""
        config = self.sdk.register_partner(partner_name="Get Test")
        session = self.sdk.create_session(
            partner_id=config.partner_id,
            consumer_reference="test_consumer",
        )
        
        retrieved = self.sdk.get_session(session.session_id)
        
        assert retrieved is not None
        assert retrieved.consumer_reference == "test_consumer"
    
    def test_get_session_returns_none_for_unknown(self):
        """Test getting unknown session returns None."""
        result = self.sdk.get_session(uuid4())
        
        assert result is None
    
    def test_generate_widget_config(self):
        """Test widget config generation."""
        config = self.sdk.register_partner(
            partner_name="Widget Test",
            branding={"logo": "https://example.com/logo.png"},
        )
        session = self.sdk.create_session(
            partner_id=config.partner_id,
            consumer_reference="test",
            prefilled_data={"credit_score": 720},
            mode="full",
        )
        
        widget_config = self.sdk.generate_widget_config(session.session_id)
        
        assert widget_config["sessionId"] == str(session.session_id)
        assert widget_config["mode"] == "full"
        assert "credit_score" in widget_config["prefilled"]
        assert widget_config["features"]["whatIf"] is True
        assert widget_config["features"]["scenarios"] is True


class TestWidgetEmbed:
    """Test suite for WidgetEmbed."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.embed = WidgetEmbed()
        self.session_id = uuid4()
    
    def test_generate_script_contains_session_id(self):
        """Test script generation includes session ID."""
        script = self.embed.generate_script(self.session_id)
        
        assert str(self.session_id) in script
        assert "GOATCRD.init" in script
        assert "goatcrd-container" in script
    
    def test_generate_script_with_custom_container(self):
        """Test script with custom container ID."""
        script = self.embed.generate_script(
            self.session_id,
            container_id="my-custom-widget",
        )
        
        assert "my-custom-widget" in script
    
    def test_generate_script_with_options(self):
        """Test script with custom options."""
        script = self.embed.generate_script(
            self.session_id,
            options={"theme": "dark", "showProgress": True},
        )
        
        assert "dark" in script
        assert "showProgress" in script
    
    def test_generate_react_component(self):
        """Test React component generation."""
        component = self.embed.generate_react_component(self.session_id)
        
        assert str(self.session_id) in component
        assert "GOATCRDWidget" in component
        assert "onComplete" in component
        assert "onError" in component
