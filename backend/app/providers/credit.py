"""
GOATCRD Credit Provider
Soft-pull credit data integration
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class CreditBureau(str, Enum):
    """Credit bureaus."""
    EXPERIAN = "experian"
    EQUIFAX = "equifax"
    TRANSUNION = "transunion"


class CreditPullType(str, Enum):
    """Type of credit pull."""
    SOFT = "soft"
    HARD = "hard"


@dataclass
class CreditScore:
    """Credit score data."""
    score: int
    score_type: str  # e.g., "VantageScore 3.0", "FICO 8"
    bureau: CreditBureau
    as_of_date: str


@dataclass
class TradeAccount:
    """Trade line / credit account."""
    account_type: str  # credit_card, auto_loan, mortgage, etc.
    creditor_name: str
    account_status: str  # open, closed, paid
    balance: float
    credit_limit: float | None
    payment_status: str  # current, 30_days, 60_days, etc.
    opened_date: str
    monthly_payment: float | None


@dataclass
class CreditInquiry:
    """Credit inquiry record."""
    inquiry_date: str
    creditor_name: str
    inquiry_type: CreditPullType


@dataclass
class CreditReport:
    """Full credit report."""
    request_id: str
    consumer_id: UUID
    bureau: CreditBureau
    pull_type: CreditPullType
    
    score: CreditScore
    trade_accounts: list[TradeAccount]
    inquiries: list[CreditInquiry]
    
    total_debt: float
    total_available_credit: float
    utilization_ratio: float
    
    public_records: list[dict]
    collections: list[dict]
    
    pulled_at: datetime


class CreditProvider:
    """
    Credit bureau integration for soft-pull credit data.
    
    IMPORTANT: Soft pulls only - never impacts consumer credit.
    
    Provides:
    - Credit score retrieval
    - Trade account summary
    - Debt and utilization calculation
    - Inquiry history
    """
    
    def __init__(
        self,
        api_key: str,
        bureau: CreditBureau = CreditBureau.EXPERIAN,
        environment: str = "sandbox",
    ):
        self.api_key = api_key
        self.bureau = bureau
        self.environment = environment
    
    async def get_credit_report(
        self,
        consumer_id: UUID,
        ssn_last_4: str | None = None,
        dob: str | None = None,
        pull_type: CreditPullType = CreditPullType.SOFT,
    ) -> CreditReport:
        """
        Pull credit report (soft pull only by default).
        
        Args:
            consumer_id: Internal consumer ID
            ssn_last_4: Last 4 digits of SSN for verification
            dob: Date of birth for verification
            pull_type: Type of pull (default: soft)
        
        Returns:
            CreditReport with score and trade accounts
        """
        if pull_type == CreditPullType.HARD:
            raise ValueError("Hard pulls require explicit authorization")
        
        # In production, would make actual API call to bureau
        # This is mock data for development
        
        score = CreditScore(
            score=720,
            score_type="VantageScore 3.0",
            bureau=self.bureau,
            as_of_date=datetime.now(timezone.utc).date().isoformat(),
        )
        
        trade_accounts = [
            TradeAccount(
                account_type="credit_card",
                creditor_name="Chase Sapphire",
                account_status="open",
                balance=2500.00,
                credit_limit=10000.00,
                payment_status="current",
                opened_date="2020-03-15",
                monthly_payment=75.00,
            ),
            TradeAccount(
                account_type="auto_loan",
                creditor_name="Toyota Financial",
                account_status="open",
                balance=18500.00,
                credit_limit=None,
                payment_status="current",
                opened_date="2022-06-01",
                monthly_payment=425.00,
            ),
            TradeAccount(
                account_type="student_loan",
                creditor_name="Navient",
                account_status="open",
                balance=32000.00,
                credit_limit=None,
                payment_status="current",
                opened_date="2016-08-15",
                monthly_payment=350.00,
            ),
        ]
        
        inquiries = [
            CreditInquiry(
                inquiry_date="2025-11-15",
                creditor_name="Chase Bank",
                inquiry_type=CreditPullType.SOFT,
            ),
        ]
        
        total_debt = sum(t.balance for t in trade_accounts)
        total_credit = sum(t.credit_limit or 0 for t in trade_accounts)
        utilization = (2500 / 10000) * 100 if total_credit > 0 else 0
        
        return CreditReport(
            request_id=str(uuid4()),
            consumer_id=consumer_id,
            bureau=self.bureau,
            pull_type=pull_type,
            score=score,
            trade_accounts=trade_accounts,
            inquiries=inquiries,
            total_debt=total_debt,
            total_available_credit=total_credit,
            utilization_ratio=utilization,
            public_records=[],
            collections=[],
            pulled_at=datetime.now(timezone.utc),
        )
    
    async def get_credit_score_only(
        self,
        consumer_id: UUID,
    ) -> CreditScore:
        """Get just the credit score (minimal data)."""
        report = await self.get_credit_report(consumer_id)
        return report.score
    
    async def calculate_dti(
        self,
        consumer_id: UUID,
        monthly_income: float,
    ) -> dict[str, float]:
        """
        Calculate debt-to-income ratio.
        
        Returns:
            Dict with dti_ratio, monthly_debt, and breakdown
        """
        report = await self.get_credit_report(consumer_id)
        
        monthly_debt = sum(
            t.monthly_payment or 0
            for t in report.trade_accounts
            if t.account_status == "open"
        )
        
        dti = (monthly_debt / monthly_income * 100) if monthly_income > 0 else 0
        
        return {
            "dti_ratio": round(dti, 2),
            "monthly_debt": monthly_debt,
            "monthly_income": monthly_income,
            "credit_score": report.score.score,
            "utilization": report.utilization_ratio,
        }
    
    async def check_for_red_flags(
        self,
        consumer_id: UUID,
    ) -> list[dict]:
        """Check for credit red flags."""
        report = await self.get_credit_report(consumer_id)
        
        flags = []
        
        # Check for recent inquiries (last 6 months)
        if len(report.inquiries) > 5:
            flags.append({
                "type": "many_inquiries",
                "severity": "medium",
                "description": f"{len(report.inquiries)} inquiries in report",
            })
        
        # Check for high utilization
        if report.utilization_ratio > 50:
            flags.append({
                "type": "high_utilization",
                "severity": "medium",
                "description": f"Credit utilization at {report.utilization_ratio:.0f}%",
            })
        
        # Check for collections
        if report.collections:
            flags.append({
                "type": "collections",
                "severity": "high",
                "description": f"{len(report.collections)} accounts in collections",
            })
        
        # Check for delinquent accounts
        delinquent = [
            t for t in report.trade_accounts
            if t.payment_status not in ("current", "paid")
        ]
        if delinquent:
            flags.append({
                "type": "delinquencies",
                "severity": "high",
                "description": f"{len(delinquent)} accounts with late payments",
            })
        
        return flags


# Factory function
def create_credit_provider(
    api_key: str | None = None,
    bureau: CreditBureau = CreditBureau.EXPERIAN,
    environment: str = "sandbox",
) -> CreditProvider:
    """Create credit provider instance."""
    return CreditProvider(
        api_key=api_key or "credit_api_key",
        bureau=bureau,
        environment=environment,
    )
