"""
Pytest configuration for GOATCRD tests.
"""
import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_intake_data() -> dict:
    """Sample intake data for testing."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "date_of_birth": "1985-03-15",
        "ssn_last_four": "1234",
        "annual_income": 85000,
        "employment_status": "employed",
        "employer_name": "Tech Corp",
        "employment_length_months": 36,
        "monthly_housing_payment": 1500,
        "credit_score": 720,
        "loan_amount_requested": 15000,
        "loan_purpose": "debt_consolidation",
    }


@pytest.fixture
def sample_scenarios() -> list:
    """Sample scenario results for testing."""
    return [
        {
            "id": "scenario_1",
            "program_name": "Prime Personal Loan",
            "status": "eligible",
            "confidence_score": 92,
            "pricing": {
                "apr": 0.089,
                "monthly_payment": 287,
                "total_cost": 10332,
            },
            "reason_codes": [],
            "verify_checklist": [],
        },
        {
            "id": "scenario_2",
            "program_name": "Credit Builder Plus",
            "status": "eligible",
            "confidence_score": 85,
            "pricing": {
                "apr": 0.129,
                "monthly_payment": 195,
                "total_cost": 7020,
            },
            "reason_codes": [],
            "verify_checklist": ["Verify employment"],
        },
        {
            "id": "scenario_3",
            "program_name": "Express Loan",
            "status": "refer",
            "confidence_score": 68,
            "reason_codes": ["RC002", "RC003"],
            "verify_checklist": ["Upload pay stubs", "Link bank account"],
        },
        {
            "id": "scenario_4",
            "program_name": "Premium Credit",
            "status": "not_eligible",
            "confidence_score": 90,
            "reason_codes": ["RC001"],
            "verify_checklist": [],
        },
    ]


@pytest.fixture
def sample_provenance() -> dict:
    """Sample provenance data for testing."""
    return {
        "annual_income": {
            "source": "payroll_api",
            "confidence": 95,
            "verified_at": "2026-01-15T10:30:00Z",
            "value": 85000,
        },
        "credit_score": {
            "source": "credit_bureau",
            "confidence": 98,
            "verified_at": "2026-01-15T10:32:00Z",
            "value": 720,
        },
        "employment_status": {
            "source": "user_stated",
            "confidence": 60,
            "value": "employed",
        },
    }
