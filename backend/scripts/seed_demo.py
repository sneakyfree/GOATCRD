"""
GOATCRD Database Seed Script
Creates demo data for testing and preview

[HARDENING] Task 2.2, 2.3: Seed demo user, programs, rulesets
"""
import asyncio
import sys
from datetime import datetime, timezone
from uuid import uuid4

# Add app to path
sys.path.insert(0, "/home/user1-gpu/Desktop/grants_folder/GOATCRD/backend")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.models import (
    User, UserRole,
    Case, CaseStatus, CaseType,
    Program, ProgramType, Ruleset,
    IntakeDraft,
)
from app.core.security import get_password_hash
from app.core.config import settings


async def seed_database():
    """Seed the database with demo data."""
    
    # Create engine
    engine = create_async_engine(
        str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://"),
        echo=True,
    )
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print("🌱 Starting database seed...")
        
        # Check if already seeded
        result = await db.execute(select(User).where(User.email == "demo@goatcrd.com"))
        if result.scalar_one_or_none():
            print("✅ Database already seeded. Use --force to reseed.")
            return
        
        # 1. Create demo users
        print("👤 Creating demo users...")
        
        demo_user = User(
            id=uuid4(),
            email="demo@goatcrd.com",
            hashed_password=get_password_hash("demo123"),
            first_name="Demo",
            last_name="User",
            phone="+15551234567",
            role=UserRole.CONSUMER,
            is_active=True,
        )
        db.add(demo_user)
        
        admin_user = User(
            id=uuid4(),
            email="admin@goatcrd.com",
            hashed_password=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        
        await db.flush()
        print(f"  ✓ Demo user: demo@goatcrd.com / demo123")
        print(f"  ✓ Admin user: admin@goatcrd.com / admin123")
        
        # 2. Create programs
        print("📦 Creating credit programs...")
        
        programs = [
            Program(
                id=uuid4(),
                name="Prime Personal Loan",
                program_type=ProgramType.PERSONAL_LOAN,
                description="Best rates for excellent credit",
                is_active=True,
                version=1,
                config={
                    "min_credit_score": 720,
                    "max_dti": 0.35,
                    "min_income": 50000,
                    "apr_range": [0.079, 0.129],
                    "term_months": [12, 24, 36, 48, 60],
                    "min_amount": 5000,
                    "max_amount": 50000,
                },
            ),
            Program(
                id=uuid4(),
                name="Credit Builder Plus",
                program_type=ProgramType.CREDIT_BUILDER,
                description="Build credit while saving",
                is_active=True,
                version=1,
                config={
                    "min_credit_score": 580,
                    "max_dti": 0.45,
                    "min_income": 25000,
                    "apr_range": [0.129, 0.189],
                    "term_months": [12, 24, 36],
                    "min_amount": 1000,
                    "max_amount": 15000,
                },
            ),
            Program(
                id=uuid4(),
                name="Flex Credit Line",
                program_type=ProgramType.LINE_OF_CREDIT,
                description="Flexible credit for everyday needs",
                is_active=True,
                version=1,
                config={
                    "min_credit_score": 640,
                    "max_dti": 0.40,
                    "min_income": 35000,
                    "apr_range": [0.149, 0.229],
                    "min_amount": 2000,
                    "max_amount": 25000,
                },
            ),
            Program(
                id=uuid4(),
                name="Express Loan",
                program_type=ProgramType.PERSONAL_LOAN,
                description="Fast funding for urgent needs",
                is_active=True,
                version=1,
                config={
                    "min_credit_score": 600,
                    "max_dti": 0.50,
                    "min_income": 20000,
                    "apr_range": [0.189, 0.299],
                    "term_months": [6, 12, 18, 24],
                    "min_amount": 1000,
                    "max_amount": 10000,
                },
            ),
            Program(
                id=uuid4(),
                name="Premium Credit",
                program_type=ProgramType.PERSONAL_LOAN,
                description="Premium rates for top-tier borrowers",
                is_active=True,
                version=1,
                config={
                    "min_credit_score": 760,
                    "max_dti": 0.30,
                    "min_income": 75000,
                    "apr_range": [0.059, 0.089],
                    "term_months": [24, 36, 48, 60, 72],
                    "min_amount": 10000,
                    "max_amount": 100000,
                },
            ),
        ]
        
        for prog in programs:
            db.add(prog)
        
        await db.flush()
        print(f"  ✓ Created {len(programs)} programs")
        
        # 3. Create rulesets
        print("📋 Creating rulesets...")
        
        ruleset = Ruleset(
            id=uuid4(),
            name="Standard Credit Rules v1",
            version=1,
            is_active=True,
            rules={
                "credit_score_minimum": {
                    "type": "threshold",
                    "field": "credit_score",
                    "operator": ">=",
                    "affects": "eligibility",
                },
                "dti_maximum": {
                    "type": "threshold",
                    "field": "dti_ratio",
                    "operator": "<=",
                    "affects": "eligibility",
                },
                "income_verification": {
                    "type": "verification",
                    "field": "annual_income",
                    "source_required": ["payroll_api", "tax_return", "bank_statement"],
                    "affects": "confidence",
                },
                "employment_stability": {
                    "type": "threshold",
                    "field": "employment_months",
                    "operator": ">=",
                    "value": 6,
                    "affects": "confidence",
                },
            },
        )
        db.add(ruleset)
        await db.flush()
        print(f"  ✓ Created ruleset: {ruleset.name}")
        
        # 4. Create demo case with intake
        print("📁 Creating demo case...")
        
        demo_case = Case(
            id=uuid4(),
            consumer_id=demo_user.id,
            case_type=CaseType.PERSONAL_LOAN,
            status=CaseStatus.INTAKE_IN_PROGRESS,
        )
        db.add(demo_case)
        await db.flush()
        
        # Create intake draft with sample data
        intake_draft = IntakeDraft(
            id=uuid4(),
            case_id=demo_case.id,
            current_chapter=3,
            data={
                "first_name": "Demo",
                "last_name": "User",
                "email": "demo@goatcrd.com",
                "phone": "+15551234567",
                "date_of_birth": "1985-06-15",
                "ssn_last_four": "1234",
                "goal": "debt_consolidation",
                "loan_amount_requested": 15000,
                "annual_income": 72000,
                "employment_status": "employed",
                "employer_name": "TechCorp Inc",
                "employment_months": 36,
                "monthly_housing_payment": 1800,
                "credit_score_estimate": 710,
            },
            provenance={
                "annual_income": {"source": "user_stated", "confidence": 60},
                "credit_score_estimate": {"source": "user_stated", "confidence": 40},
                "employment_status": {"source": "user_stated", "confidence": 60},
            },
        )
        db.add(intake_draft)
        await db.flush()
        print(f"  ✓ Created demo case with intake draft")
        
        # Commit all changes
        await db.commit()
        
        print("\n🎉 Database seeded successfully!")
        print("\n📋 Quick Login Credentials:")
        print("  Demo User: demo@goatcrd.com / demo123")
        print("  Admin User: admin@goatcrd.com / admin123")


if __name__ == "__main__":
    asyncio.run(seed_database())
