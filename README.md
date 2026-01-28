# GOATCRD — Agentic Consumer Credit Intelligence Platform

> **Compliance-first. Agentic by design. Consumer-empowering.**

GOATCRD is an A+ category-defining blueprint for consumer credit decisioning that proactively collects borrower inputs, generates source-labeled scenario universes, ranks and explains options with counterfactual reasoning, and produces immutable audit snapshots—all without hallucinating approvals, pricing, or eligibility.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 16 (or use Docker)

### Development Setup

```bash
# Clone and enter directory
cd GOATCRD

# Start infrastructure (Postgres + Redis)
docker-compose up -d db redis

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### With Docker Compose

```bash
docker-compose up
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/v1/docs
```

## Architecture

```
GOATCRD/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Config, database, security
│   │   ├── engines/           # Rules, Confidence, Explainability
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── alembic/               # Database migrations
│   └── tests/                 # Pytest suite
├── frontend/                   # React + Vite + TailwindCSS
│   └── src/
│       ├── components/        # React components
│       ├── pages/             # Page components
│       └── stores/            # Zustand stores
└── docker-compose.yml         # Local dev infrastructure
```

## Core Engines

| Engine | Purpose |
|--------|---------|
| **RulesEngine** | Deterministic eligibility evaluation with configurable rulesets |
| **ConfidenceEngine** | Calculates confidence scores with caps and verify checklists |
| **ExplainabilityEngine** | 4-layer explanations (consumer/pro/compliance/deep) with no-new-facts |

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/auth/register` | User registration |
| `POST /api/v1/auth/login` | Authentication |
| `POST /api/v1/cases` | Create case |
| `PUT /api/v1/cases/{id}/intake/draft` | Save intake progress |
| `POST /api/v1/cases/{id}/intake/submit` | Submit intake snapshot |
| `POST /api/v1/cases/{id}/scenarios/run` | Generate scenarios |
| `POST /api/v1/cases/{id}/scenarios/simulate` | What-If simulation |
| `POST /api/v1/consents/{id}/grant` | Grant data consent |
| `POST /api/v1/consents/{id}/revoke` | Revoke consent |
| `GET /api/v1/consents/access-log` | 1033 access log |

## GOATCRD Laws (Engineering Guardrails)

1. **No Hallucination** — Never invent approvals, rates, or eligibility
2. **REFER-by-Default** — Uncertainty → human review, not auto-decline
3. **Fairness Mandatory** — Disparate impact testing in CI/CD
4. **Audit Snapshots** — Immutable, reproducible, deterministic
5. **1033-Native** — Consumer data rights by design
6. **Bounded Agents** — Agents suggest, never claim approvals

## Phased Roadmap

- **Phase 0** ✅ Foundation (repo, models, API skeleton, engines)
- **Phase 1** 🔲 MVP Scenario Engine (catalog, rules, ranking, exports)
- **Phase 2** 🔲 Consent + Provenance Hardening
- **Phase 3** 🔲 Alternative Data + Credit Pulse
- **Phase 4** 🔲 Agentic Crew + Fairness CI/CD
- **Phase 5** 🔲 Embedded Finance SDK

## License

Proprietary. All rights reserved.
