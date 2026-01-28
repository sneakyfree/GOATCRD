"""
GOATCRD Alternative Data API Routes
Bank connection and alternative data source management
"""
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.engines.alternative_data import (
    AltDataSource,
    alternative_data_engine,
)


router = APIRouter(prefix="/alt-data", tags=["Alternative Data"])


# ============================================================================
# Schemas
# ============================================================================


class LinkTokenRequest(BaseModel):
    """Request for Plaid link token."""
    redirect_uri: str | None = None


class LinkTokenResponse(BaseModel):
    """Response with Plaid link token."""
    link_token: str
    expiration: datetime
    request_id: str


class PublicTokenExchange(BaseModel):
    """Exchange public token for access token."""
    public_token: str
    institution_id: str
    institution_name: str
    accounts: list[dict[str, Any]]


class ConnectedAccount(BaseModel):
    """A connected bank account."""
    id: str
    institution_name: str
    account_name: str
    account_type: str
    account_mask: str
    balance: float | None
    connected_at: datetime
    status: str


class AltDataAccountsResponse(BaseModel):
    """Response listing connected accounts."""
    accounts: list[ConnectedAccount]
    total_count: int


class CashFlowResponse(BaseModel):
    """Cash flow analysis response."""
    avg_monthly_income: float
    avg_monthly_expenses: float
    net_monthly_cash_flow: float
    savings_rate: float
    income_volatility: float
    income_sources: list[dict]
    risk_indicators: dict
    confidence: int
    analyzed_at: datetime


# ============================================================================
# Mock Data Store (would be database in production)
# ============================================================================

_connected_accounts: dict[str, list[ConnectedAccount]] = {}


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/link-token", response_model=LinkTokenResponse)
async def create_link_token(
    request: LinkTokenRequest,
    current_user: dict = Depends(get_current_user),
) -> LinkTokenResponse:
    """
    Generate a Plaid Link token for bank connection.
    
    In production, this would call Plaid's /link/token/create endpoint.
    For demo purposes, returns a mock token.
    """
    # Mock Plaid link token response
    return LinkTokenResponse(
        link_token=f"link-sandbox-{uuid4().hex[:16]}",
        expiration=datetime.now(timezone.utc).replace(hour=23, minute=59),
        request_id=str(uuid4()),
    )


@router.post("/exchange", response_model=ConnectedAccount)
async def exchange_public_token(
    exchange: PublicTokenExchange,
    current_user: dict = Depends(get_current_user),
) -> ConnectedAccount:
    """
    Exchange Plaid public token and store connected account.
    
    In production, this would:
    1. Call Plaid's /item/public_token/exchange
    2. Store the access_token securely
    3. Fetch account details
    """
    user_id = str(current_user.get("id", "demo"))
    
    # Create connected account record
    new_account = ConnectedAccount(
        id=str(uuid4()),
        institution_name=exchange.institution_name,
        account_name=exchange.accounts[0].get("name", "Checking") if exchange.accounts else "Primary Account",
        account_type=exchange.accounts[0].get("type", "depository") if exchange.accounts else "depository",
        account_mask=exchange.accounts[0].get("mask", "1234") if exchange.accounts else "1234",
        balance=exchange.accounts[0].get("balance", 5000.00) if exchange.accounts else 5000.00,
        connected_at=datetime.now(timezone.utc),
        status="active",
    )
    
    # Store in mock database
    if user_id not in _connected_accounts:
        _connected_accounts[user_id] = []
    _connected_accounts[user_id].append(new_account)
    
    return new_account


@router.get("/accounts", response_model=AltDataAccountsResponse)
async def list_connected_accounts(
    current_user: dict = Depends(get_current_user),
) -> AltDataAccountsResponse:
    """List all connected bank accounts for the current user."""
    user_id = str(current_user.get("id", "demo"))
    accounts = _connected_accounts.get(user_id, [])
    
    return AltDataAccountsResponse(
        accounts=accounts,
        total_count=len(accounts),
    )


@router.delete("/accounts/{account_id}")
async def disconnect_account(
    account_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Disconnect a bank account.
    
    This removes the connection and any stored data.
    In production, would also call Plaid's /item/remove endpoint.
    """
    user_id = str(current_user.get("id", "demo"))
    accounts = _connected_accounts.get(user_id, [])
    
    # Find and remove account
    for i, account in enumerate(accounts):
        if account.id == account_id:
            del accounts[i]
            return {
                "success": True,
                "message": f"Account {account_id} disconnected",
                "downstream_disabled": True,
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Account not found",
    )


@router.get("/accounts/{account_id}/cash-flow", response_model=CashFlowResponse)
async def get_cash_flow_analysis(
    account_id: str,
    period_days: int = 90,
    current_user: dict = Depends(get_current_user),
) -> CashFlowResponse:
    """
    Get cash flow analysis for a connected account.
    
    Returns income patterns, expense analysis, and risk indicators.
    """
    user_id = str(current_user.get("id", "demo"))
    accounts = _connected_accounts.get(user_id, [])
    
    # Verify account exists
    account = next((a for a in accounts if a.id == account_id), None)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    # Mock transaction data for analysis
    mock_transactions = [
        {"amount": 3500, "description": "Payroll Direct Deposit", "timestamp": datetime.now(timezone.utc).timestamp() - 86400 * 5},
        {"amount": 3500, "description": "Payroll Direct Deposit", "timestamp": datetime.now(timezone.utc).timestamp() - 86400 * 35},
        {"amount": 3500, "description": "Payroll Direct Deposit", "timestamp": datetime.now(timezone.utc).timestamp() - 86400 * 65},
        {"amount": -1500, "description": "Rent Payment", "timestamp": datetime.now(timezone.utc).timestamp() - 86400 * 3},
        {"amount": -150, "description": "Electric Bill", "timestamp": datetime.now(timezone.utc).timestamp() - 86400 * 10},
        {"amount": -200, "description": "Grocery Store", "timestamp": datetime.now(timezone.utc).timestamp() - 86400 * 2},
        {"amount": -50, "description": "Gas Station", "timestamp": datetime.now(timezone.utc).timestamp() - 86400 * 1},
    ]
    
    # Run analysis
    analysis = await alternative_data_engine.analyze_cash_flow(
        consumer_id=UUID(user_id) if user_id != "demo" else uuid4(),
        transactions=mock_transactions,
        period_days=period_days,
    )
    
    return CashFlowResponse(
        avg_monthly_income=analysis.avg_monthly_income,
        avg_monthly_expenses=analysis.avg_monthly_expenses,
        net_monthly_cash_flow=analysis.net_monthly_cash_flow,
        savings_rate=analysis.savings_rate,
        income_volatility=analysis.income_volatility,
        income_sources=analysis.income_sources,
        risk_indicators={
            "overdraft_count": analysis.overdraft_count,
            "nsf_count": analysis.nsf_count,
            "avg_low_balance_days": analysis.avg_low_balance_days,
        },
        confidence=analysis.confidence,
        analyzed_at=analysis.analyzed_at,
    )


@router.post("/process/{source}")
async def process_alternative_data(
    source: AltDataSource,
    raw_data: dict[str, Any],
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Process raw alternative data from a source.
    
    Returns normalized records for credit assessment.
    """
    user_id = str(current_user.get("id", "demo"))
    consumer_id = UUID(user_id) if user_id != "demo" else uuid4()
    
    records = await alternative_data_engine.process_data(
        consumer_id=consumer_id,
        source=source,
        raw_data=raw_data,
    )
    
    return {
        "success": True,
        "records_created": len(records),
        "records": [
            {
                "field_name": r.field_name,
                "value": r.normalized_value,
                "confidence": r.confidence,
                "source": r.source.value,
            }
            for r in records
        ],
    }
