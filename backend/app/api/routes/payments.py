"""
GOATCRD Stripe Payments Router

Handles subscription checkout, webhooks, and pricing tiers.
"""

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Header, HTTPException, status
from pydantic import BaseModel

import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])

# ============================================================================
# Pricing Tiers
# ============================================================================

PRICING_TIERS = {
    "free": {
        "name": "Free",
        "price_id": None,
        "price_monthly": 0,
        "features": [
            "10 credit assessments per month",
            "Basic intake wizard",
            "Standard reason codes",
            "Email support",
        ],
    },
    "pro": {
        "name": "Pro",
        "price_id": os.getenv("STRIPE_PRO_PRICE_ID", "price_pro"),
        "price_monthly": 79,
        "features": [
            "Unlimited assessments",
            "Full 7-agent analysis",
            "What-If simulator",
            "Alternative data integration",
            "Fairness monitoring",
            "API access",
            "Priority support",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", "price_enterprise"),
        "price_monthly": 299,
        "features": [
            "Everything in Pro",
            "Multi-program management",
            "Custom rulesets engine",
            "White-label partner portal",
            "SOC2 compliance reports",
            "Dedicated success manager",
            "SLA guarantee",
        ],
    },
}


# ============================================================================
# Request/Response Models
# ============================================================================

class CheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    tier_id: str
    success_url: str
    cancel_url: str
    user_email: Optional[str] = None


class CheckoutResponse(BaseModel):
    """Response with checkout URL."""
    checkout_url: str
    session_id: str


class SubscriptionStatus(BaseModel):
    """Current subscription status."""
    tier_id: str
    tier_name: str
    status: str
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/pricing")
async def get_pricing():
    """Get available pricing tiers."""
    return {
        "tiers": [
            {
                "id": tier_id,
                **tier_info,
            }
            for tier_id, tier_info in PRICING_TIERS.items()
        ]
    }


@router.post("/create-checkout-session", response_model=CheckoutResponse)
async def create_checkout_session(request: CheckoutRequest):
    """Create a Stripe checkout session."""
    import stripe

    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    if not stripe.api_key:
        logger.warning("Stripe API key not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service not configured",
        )

    tier = PRICING_TIERS.get(request.tier_id)
    if not tier or request.tier_id == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tier or free tier does not require checkout",
        )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": tier["price_id"],
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            customer_email=request.user_email,
            metadata={
                "tier_id": request.tier_id,
            },
        )

        logger.info(
            "Checkout session created",
            session_id=session.id,
            tier_id=request.tier_id,
        )

        return CheckoutResponse(
            checkout_url=session.url,
            session_id=session.id,
        )

    except stripe.error.StripeError as e:
        logger.error("Stripe error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session",
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
):
    """Handle Stripe webhooks."""
    import stripe

    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        logger.warning("Stripe webhook secret not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured",
        )

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    event_type = event["type"]
    data = event["data"]["object"]

    logger.info("Stripe webhook received", event_type=event_type)

    # Handle subscription events
    if event_type == "checkout.session.completed":
        tier_id = data.get("metadata", {}).get("tier_id")
        customer_email = data.get("customer_email")
        subscription_id = data.get("subscription")

        logger.info(
            "Subscription created",
            tier_id=tier_id,
            customer_email=customer_email,
            subscription_id=subscription_id,
        )
        # TODO: Update user subscription in database

    elif event_type == "customer.subscription.updated":
        subscription_id = data.get("id")
        status = data.get("status")

        logger.info(
            "Subscription updated",
            subscription_id=subscription_id,
            status=status,
        )
        # TODO: Update subscription status in database

    elif event_type == "customer.subscription.deleted":
        subscription_id = data.get("id")

        logger.info(
            "Subscription cancelled",
            subscription_id=subscription_id,
        )
        # TODO: Downgrade user to free tier

    return {"status": "received"}


@router.get("/subscription/status", response_model=SubscriptionStatus)
async def get_subscription_status():
    """Get current user subscription status."""
    # TODO: Get actual subscription from database based on authenticated user
    return SubscriptionStatus(
        tier_id="free",
        tier_name="Free",
        status="active",
        cancel_at_period_end=False,
    )
