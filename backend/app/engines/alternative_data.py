"""
GOATCRD Alternative Data Engine
Connectors and processing for non-traditional data sources
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class AltDataSource(str, Enum):
    """Alternative data source types."""
    
    OPEN_BANKING = "open_banking"
    GIG_INCOME = "gig_income"
    RENT_PAYMENTS = "rent_payments"
    UTILITY_PAYMENTS = "utility_payments"
    TELECOM = "telecom"
    SUBSCRIPTION = "subscription"
    CASH_FLOW = "cash_flow"


@dataclass
class AltDataRecord:
    """Record from alternative data source."""
    
    record_id: UUID
    consumer_id: UUID
    source: AltDataSource
    
    raw_data: dict[str, Any]
    normalized_value: Any
    field_name: str
    
    confidence: int
    extracted_at: datetime
    
    metadata: dict[str, Any] | None = None


@dataclass
class CashFlowAnalysis:
    """Cash flow analysis from bank transaction data."""
    
    consumer_id: UUID
    analysis_period_days: int
    
    # Income patterns
    avg_monthly_income: float
    income_volatility: float  # 0-1, lower is more stable
    income_sources: list[dict]
    
    # Expense patterns
    avg_monthly_expenses: float
    fixed_expenses: float
    variable_expenses: float
    
    # Derived metrics
    net_monthly_cash_flow: float
    savings_rate: float
    expense_to_income_ratio: float
    
    # Risk indicators
    overdraft_count: int
    nsf_count: int
    avg_low_balance_days: float
    
    confidence: int
    analyzed_at: datetime


class AlternativeDataEngine:
    """
    Processes alternative data for credit assessment.
    
    Sources:
    - Open Banking (transaction data)
    - Gig income (Uber, DoorDash, etc.)
    - Rent payment history
    - Utility payments
    - Telecom payment history
    """
    
    def __init__(self):
        self.processors = {
            AltDataSource.OPEN_BANKING: self._process_open_banking,
            AltDataSource.GIG_INCOME: self._process_gig_income,
            AltDataSource.RENT_PAYMENTS: self._process_rent_payments,
            AltDataSource.CASH_FLOW: self._process_cash_flow,
        }
    
    async def process_data(
        self,
        consumer_id: UUID,
        source: AltDataSource,
        raw_data: dict[str, Any],
    ) -> list[AltDataRecord]:
        """
        Process raw data from an alternative source.
        
        Returns normalized records for credit assessment.
        """
        processor = self.processors.get(source)
        if not processor:
            return []
        
        return await processor(consumer_id, raw_data)
    
    async def analyze_cash_flow(
        self,
        consumer_id: UUID,
        transactions: list[dict],
        period_days: int = 90,
    ) -> CashFlowAnalysis:
        """
        Perform cash flow analysis on transaction data.
        """
        # Filter to period
        cutoff = datetime.now(timezone.utc).timestamp() - (period_days * 86400)
        
        period_transactions = [
            t for t in transactions
            if t.get("timestamp", 0) > cutoff
        ]
        
        # Categorize transactions
        income = [t for t in period_transactions if t.get("amount", 0) > 0]
        expenses = [t for t in period_transactions if t.get("amount", 0) < 0]
        
        # Calculate metrics
        total_income = sum(t.get("amount", 0) for t in income)
        total_expenses = abs(sum(t.get("amount", 0) for t in expenses))
        
        months = period_days / 30
        avg_monthly_income = total_income / months if months > 0 else 0
        avg_monthly_expenses = total_expenses / months if months > 0 else 0
        
        # Income volatility (coefficient of variation)
        monthly_incomes = self._group_by_month(income)
        income_volatility = self._calculate_volatility(monthly_incomes)
        
        # Detect income sources
        income_sources = self._detect_income_sources(income)
        
        # Fixed vs variable expenses
        fixed_expenses = self._estimate_fixed_expenses(expenses)
        variable_expenses = avg_monthly_expenses - fixed_expenses
        
        # Risk indicators
        overdraft_count = len([t for t in period_transactions if t.get("type") == "overdraft"])
        nsf_count = len([t for t in period_transactions if t.get("type") == "nsf"])
        
        # Calculate confidence based on data quality
        confidence = self._calculate_analysis_confidence(
            len(period_transactions),
            period_days,
            income_volatility,
        )
        
        return CashFlowAnalysis(
            consumer_id=consumer_id,
            analysis_period_days=period_days,
            avg_monthly_income=round(avg_monthly_income, 2),
            income_volatility=round(income_volatility, 2),
            income_sources=income_sources,
            avg_monthly_expenses=round(avg_monthly_expenses, 2),
            fixed_expenses=round(fixed_expenses, 2),
            variable_expenses=round(variable_expenses, 2),
            net_monthly_cash_flow=round(avg_monthly_income - avg_monthly_expenses, 2),
            savings_rate=round((avg_monthly_income - avg_monthly_expenses) / avg_monthly_income, 2) if avg_monthly_income > 0 else 0,
            expense_to_income_ratio=round(avg_monthly_expenses / avg_monthly_income, 2) if avg_monthly_income > 0 else 0,
            overdraft_count=overdraft_count,
            nsf_count=nsf_count,
            avg_low_balance_days=0,  # Would calculate from daily balances
            confidence=confidence,
            analyzed_at=datetime.now(timezone.utc),
        )
    
    async def _process_open_banking(
        self,
        consumer_id: UUID,
        raw_data: dict,
    ) -> list[AltDataRecord]:
        """Process Open Banking data."""
        records = []
        now = datetime.now(timezone.utc)
        
        # Extract account balances
        if "accounts" in raw_data:
            for account in raw_data["accounts"]:
                records.append(AltDataRecord(
                    record_id=uuid4(),
                    consumer_id=consumer_id,
                    source=AltDataSource.OPEN_BANKING,
                    raw_data=account,
                    normalized_value=account.get("balance", 0),
                    field_name="bank_balance",
                    confidence=95,
                    extracted_at=now,
                    metadata={"account_type": account.get("type")},
                ))
        
        # Extract transaction patterns
        if "transactions" in raw_data:
            # Calculate monthly average deposits
            deposits = [t for t in raw_data["transactions"] if t.get("amount", 0) > 0]
            if deposits:
                avg_deposit = sum(t["amount"] for t in deposits) / len(deposits)
                records.append(AltDataRecord(
                    record_id=uuid4(),
                    consumer_id=consumer_id,
                    source=AltDataSource.OPEN_BANKING,
                    raw_data={"deposit_count": len(deposits)},
                    normalized_value=avg_deposit,
                    field_name="avg_deposit_amount",
                    confidence=90,
                    extracted_at=now,
                ))
        
        return records
    
    async def _process_gig_income(
        self,
        consumer_id: UUID,
        raw_data: dict,
    ) -> list[AltDataRecord]:
        """Process gig economy income data."""
        records = []
        now = datetime.now(timezone.utc)
        
        # Extract platform earnings
        for platform, earnings in raw_data.get("platforms", {}).items():
            monthly_avg = sum(earnings.get("monthly_earnings", [])) / 12
            
            records.append(AltDataRecord(
                record_id=uuid4(),
                consumer_id=consumer_id,
                source=AltDataSource.GIG_INCOME,
                raw_data=earnings,
                normalized_value=monthly_avg * 12,  # Annualized
                field_name="gig_annual_income",
                confidence=85,
                extracted_at=now,
                metadata={"platform": platform},
            ))
        
        return records
    
    async def _process_rent_payments(
        self,
        consumer_id: UUID,
        raw_data: dict,
    ) -> list[AltDataRecord]:
        """Process rent payment history."""
        records = []
        now = datetime.now(timezone.utc)
        
        payments = raw_data.get("payments", [])
        if payments:
            # Calculate on-time payment rate
            on_time = len([p for p in payments if p.get("on_time", False)])
            total = len(payments)
            on_time_rate = on_time / total if total > 0 else 0
            
            records.append(AltDataRecord(
                record_id=uuid4(),
                consumer_id=consumer_id,
                source=AltDataSource.RENT_PAYMENTS,
                raw_data=raw_data,
                normalized_value=on_time_rate,
                field_name="rent_payment_rate",
                confidence=90,
                extracted_at=now,
                metadata={"total_payments": total, "on_time": on_time},
            ))
            
            # Average rent amount
            avg_rent = sum(p.get("amount", 0) for p in payments) / len(payments)
            records.append(AltDataRecord(
                record_id=uuid4(),
                consumer_id=consumer_id,
                source=AltDataSource.RENT_PAYMENTS,
                raw_data=raw_data,
                normalized_value=avg_rent,
                field_name="monthly_rent",
                confidence=90,
                extracted_at=now,
            ))
        
        return records
    
    async def _process_cash_flow(
        self,
        consumer_id: UUID,
        raw_data: dict,
    ) -> list[AltDataRecord]:
        """Process cash flow data."""
        transactions = raw_data.get("transactions", [])
        
        if not transactions:
            return []
        
        analysis = await self.analyze_cash_flow(consumer_id, transactions)
        
        records = [
            AltDataRecord(
                record_id=uuid4(),
                consumer_id=consumer_id,
                source=AltDataSource.CASH_FLOW,
                raw_data={"analysis_id": str(uuid4())},
                normalized_value=analysis.avg_monthly_income,
                field_name="cash_flow_income",
                confidence=analysis.confidence,
                extracted_at=analysis.analyzed_at,
            ),
            AltDataRecord(
                record_id=uuid4(),
                consumer_id=consumer_id,
                source=AltDataSource.CASH_FLOW,
                raw_data={"analysis_id": str(uuid4())},
                normalized_value=analysis.income_volatility,
                field_name="income_stability",
                confidence=analysis.confidence,
                extracted_at=analysis.analyzed_at,
            ),
        ]
        
        return records
    
    def _group_by_month(self, transactions: list[dict]) -> list[float]:
        """Group transactions by month and return totals."""
        # Simplified: return list of monthly totals
        if not transactions:
            return []
        
        # This would properly group by month in production
        total = sum(t.get("amount", 0) for t in transactions)
        return [total / 3, total / 3, total / 3]  # Simplified
    
    def _calculate_volatility(self, monthly_values: list[float]) -> float:
        """Calculate coefficient of variation."""
        if not monthly_values or len(monthly_values) < 2:
            return 0.5  # Unknown = moderate volatility
        
        mean = sum(monthly_values) / len(monthly_values)
        if mean == 0:
            return 0.5
        
        variance = sum((x - mean) ** 2 for x in monthly_values) / len(monthly_values)
        std_dev = variance ** 0.5
        
        return min(1.0, std_dev / mean)  # Cap at 1.0
    
    def _detect_income_sources(self, income_transactions: list[dict]) -> list[dict]:
        """Detect and categorize income sources."""
        sources = {}
        
        for t in income_transactions:
            desc = t.get("description", "").lower()
            category = "other"
            
            if any(w in desc for w in ["payroll", "salary", "direct deposit"]):
                category = "employment"
            elif any(w in desc for w in ["uber", "lyft", "doordash", "instacart"]):
                category = "gig_economy"
            elif any(w in desc for w in ["rent", "rental"]):
                category = "rental_income"
            
            if category not in sources:
                sources[category] = {"total": 0, "count": 0}
            
            sources[category]["total"] += t.get("amount", 0)
            sources[category]["count"] += 1
        
        return [
            {"source": k, "total": v["total"], "count": v["count"]}
            for k, v in sources.items()
        ]
    
    def _estimate_fixed_expenses(self, expense_transactions: list[dict]) -> float:
        """Estimate fixed monthly expenses."""
        # Look for recurring similar amounts
        amounts = [abs(t.get("amount", 0)) for t in expense_transactions]
        
        # Simplified: assume 60% of expenses are fixed
        return sum(amounts) * 0.6 / 3  # Monthly avg
    
    def _calculate_analysis_confidence(
        self,
        transaction_count: int,
        period_days: int,
        volatility: float,
    ) -> int:
        """Calculate confidence in cash flow analysis."""
        # Base confidence from transaction density
        density = transaction_count / period_days
        
        if density > 2:
            base = 90
        elif density > 1:
            base = 80
        elif density > 0.5:
            base = 70
        else:
            base = 50
        
        # Penalize high volatility
        volatility_penalty = int(volatility * 20)
        
        return max(30, base - volatility_penalty)


# Singleton instance
alternative_data_engine = AlternativeDataEngine()
