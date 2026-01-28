# GOATCRD DNA Strand Master Plan — A+ Edition
> **Version:** 1.0 (A+ Blueprint)  
> **Status:** Canonical Build Specification  
> **Audience:** Regulators, Auditors, Engineers, Enterprise Buyers  
> **Philosophy:** Agentic Soul + Compliance Spine

---

## 1) One-Sentence Definition

**GOATCRD** is an agentic, compliance-first consumer credit intelligence platform that proactively collects borrower inputs, monitors for changes with consent, generates source-labeled scenario universes across configured programs, ranks and explains options with counterfactual reasoning, and produces immutable audit snapshots and CFPB-grade reason codes—without hallucinating approvals, pricing, or eligibility.

---

## 2) Begin With The End In Mind — Measurable Outcomes

### 2.1 Consumer Outcomes
- Complete a TurboTax-style intake in <10 minutes (mobile-first)
- See **multiple ranked scenarios**, not a single "answer"
- Understand **exactly why** options are ELIGIBLE, REFER, or NOT_ELIGIBLE
- Receive **proactive nudges** when credit profile changes (opt-in)
- Simulate "What If" actions: "If I pay $500, what changes?"
- Export all personal data at any time (1033 compliance)
- Revoke data access with verified downstream disablement

### 2.2 Operator Outcomes (Lenders, Advisors, Partners)
- Day-1 operator outperforms 20-year veteran on completeness and defensibility
- Generate audit-ready packets in <30 seconds
- White-label via Embedded Finance SDK
- Zero hallucinated approvals or fabricated terms

### 2.3 Regulator/Compliance Outcomes
- Every decision reproducible from snapshot ID
- Reason codes mapped to adverse-action-safe categories
- Fairness testing artifacts stored with every model/rules version
- Full consent + access logs for 1033 examinations
- Delta reports show exactly what changed between versions

---

## 3) GOATCRD Laws (Engineering-Enforced Guardrails)

### Law 1: No Hallucination
- Never invent approvals, rates, APR, fees, eligibility thresholds
- All values labeled: `lender_api` | `bureau` | `open_banking` | `manual` | `estimate` | `unknown`
- Estimates must include confidence caps and never use "approved" language

### Law 2: Exhaustive ≠ Internet Scraping
- Exhaustive = configured catalogs + connected sources + ingested datasets + manual entry
- Never claim "searched the entire market"

### Law 3: REFER-by-Default
- Uncertainty, contradictions, missing verification → REFER + verify checklist
- Never auto-decline from weak evidence

### Law 4: Explainability + Reason Codes
- NOT_ELIGIBLE must produce reason codes and "what can improve" (directional, no promises)
- 4-layer explanations: Consumer / Pro / Compliance / Deep Technical

### Law 5: Fairness is Mandatory
- Disparate impact testing hooks in Phase 1
- Full CI/CD gates by Phase 4
- No deployment without passing fairness checks

### Law 6: Audit Snapshots + Determinism
- Every run produces immutable snapshot with pinned versions
- External API responses stored with hash + timestamp
- Same snapshot → same output (or documented delta)

### Law 7: 1033-Native Consumer Rights
- Consent-first access for all data pulls
- Machine-readable data export (JSON/CSV)
- Access logs: who accessed what, when
- Revocation with downstream verification
- Data minimization + configurable retention

### Law 8: Bounded Agentic Behavior
**Agents CAN:**
- Ask clarifying questions
- Suggest actions
- Draft scenarios and explanations
- Monitor for changes (with consent)
- Escalate to human review

**Agents MUST NEVER:**
- Claim approvals
- Hide uncertainty
- Modify authoritative rules without governance
- Use or infer protected class attributes
- Contact external parties outside approved integrations

---

## 4) Scope Envelope

### 4.1 In-Scope (MVP → v2)
- Mobile-first TurboTax intake via secure link
- Program catalog (manual + API connectors)
- Eligibility triage: ELIGIBLE / REFER / NOT_ELIGIBLE
- Scenario generation + ranking
- Reason codes engine
- 4-layer explainability
- Counterfactual / "What If" simulator
- Human review workflow
- Alternative data ingestion (Open Banking, rent, utilities)
- Credit Pulse monitoring (real-time, opt-in)
- GOATCRD Crew (agentic orchestration)
- Fairness CI/CD pipeline
- Embedded Finance SDK (B2B LaaS)
- Audit snapshots + reproducibility
- Python-first backend (FastAPI + Pydantic + Postgres)
- PWA frontend (recommended)

### 4.2 Explicit Non-Goals
- Binding/closing/issuing credit automatically
- Scraping lender websites
- Automated adverse action notices as legal documents (we store codes; final notices are downstream)
- Modeling protected classes or proxy attributes
- Guarantees of approval
- Real-time lender bidding (future consideration)

---

## 5) Architecture Overview — Module Map

### Core Runtime Modules
| Module | Name | Responsibility |
|--------|------|----------------|
| **M1** | Crew Conductor | Agentic orchestration, agent lifecycle, checkpoint gates |
| **M2** | Intake Engine | Schema-driven TurboTax flow, mobile-first |
| **M3** | Validation + Normalization | Contradiction detection, data cleaning |
| **M4** | Program Catalog | Versioned program definitions, governance |
| **M5** | Data Provenance Layer | Source labels, confidence, timestamps |
| **M6** | Eligibility/Triage Engine | Rules evaluation, status assignment |
| **M7** | Scenario Universe Builder | Deterministic enumeration |
| **M8** | Pricing/Term Resolver | Source-labeled pricing lookup |
| **M9** | Confidence Scoring | Caps, drivers, verify checklist |
| **M10** | Ranking Engine | Multi-mode ranking with gating |
| **M11** | Reason Codes Engine | Rule hits → adverse-action-safe codes |
| **M12** | Explainability Engine | 4-layer outputs, no-new-facts |
| **M13** | Human Review Workflow | Queues, overrides, escalation |
| **M14** | Audit Snapshot Engine | Immutable snapshots, delta reporting |
| **M15** | Export Engine | Consumer/Pro/Compliance packets |
| **M16** | Security/RBAC | Access control, audit logging |

### New Agentic Modules
| Module | Name | Responsibility |
|--------|------|----------------|
| **M19** | Alternative Data Engine | Open Banking, rent, utilities, gig income |
| **M20** | Credit Pulse Monitor | Real-time change detection, proactive nudges |
| **M21** | Embedded Finance SDK | B2B LaaS API, partner management |
| **M22** | Counterfactual Simulator | "What If" engine |
| **M23** | Coach Agent | Proactive consumer guidance |

### Specialized Agents (within M1 Crew)
| Agent | Role | Autonomy |
|-------|------|----------|
| Intake Agent | Guides intake, resolves contradictions | Semi-autonomous |
| Triage Agent | Runs eligibility, identifies blockers | Fully autonomous |
| Scenario Architect | Builds universe, ranks options | Fully autonomous |
| Explainer Agent | Generates explanations, answers questions | Semi-autonomous |
| Coach Agent | Proactive improvement suggestions | Consent-gated |
| Compliance Guardian | Monitors all agents for violations | Supervisor |

---

## 6) Intake DNA (TurboTax Chapters)

### 6.1 Intake Chapters
1. **Identity & Contact** — Minimal; avoid overcollection
2. **Goals** — Purchase/refi/consolidation/card/personal loan
3. **Income & Employment** — Self-reported; verified later with consent
4. **Assets & Reserves** — Buckets/ranges to minimize PII
5. **Debts & Obligations** — Buckets/ranges
6. **Credit Snapshot** — Self-reported ranges; optional pull later
7. **Housing Profile** — Rent/own, timeline, geography
8. **Risk/Preference Settings** — Speed vs cost vs certainty weights
9. **Consents & Disclosures** — Per data source, granular scope
10. **Review & Verify** — Contradiction resolution, missing items

### 6.2 Field Design Principles
- Prefer **buckets/ranges** early to reduce PII and abandonment
- Upgrade to precise values only when needed and consented
- Every field has:
  - `required_for`: which engine needs it
  - `provenance`: provided/verified/estimated/unknown
  - `sensitivity_level`: low/medium/high

### 6.3 Contradiction Detection
| Pattern | Action |
|---------|--------|
| Income "low" + debt payments "high" | Flag, request clarification |
| Employment "unemployed" + income "salary" | Flag, REFER if unresolved |
| Credit "excellent" + bankruptcy "yes" | Flag, cap confidence |

**Rule:** Contradictions never auto-deny. Route to REFER + verify checklist.

---

## 7) Consent & Data Rights UX (1033-Native)

### 7.1 Consent Object Schema
```python
class Consent(BaseModel):
    consent_id: UUID
    consumer_id: UUID
    scope: ConsentScope  # e.g., credit_report, bank_link, employment
    provider: str
    granted_at: datetime
    expires_at: Optional[datetime]
    revoked_at: Optional[datetime]
    purpose: str
    retention_policy_id: UUID
```

### 7.2 Consent Lifecycle Events
- `consent.requested` → `consent.granted` | `consent.denied`
- `consent.revoked` → downstream disablement verified

### 7.3 1033 Consumer Rights Features
| Feature | Implementation |
|---------|----------------|
| **Data Export** | `GET /consumers/{id}/data-export` returns JSON/CSV |
| **Access Log** | `GET /consumers/{id}/access-log` shows all accesses |
| **Revoke** | `POST /consents/{id}/revoke` with downstream verification |
| **Retention Control** | Configurable per data type; automated expiry |

### 7.4 Acceptance Tests
- [ ] Consumer can export all data in <10 seconds
- [ ] Revocation triggers downstream disablement within 24 hours
- [ ] Access log shows every data access with timestamp

---

## 8) Data Provenance Layer

### 8.1 Provenance States
| State | Meaning | Confidence Impact |
|-------|---------|-------------------|
| `verified` | From authoritative source (bureau, lender API) | Full confidence |
| `provided` | User-supplied | Medium confidence |
| `estimated` | Calculated/modeled | Labeled; caps apply |
| `unknown` | Missing | Forces REFER or caps outcome |

### 8.2 Confidence Scoring Formula
```
base_confidence = min(field_confidences)
caps_applied = apply_caps(contradictions, missing_fields, estimate_count)
final_confidence = min(base_confidence, caps_applied)
```

### 8.3 Provenance Record Schema
```python
class ProvenanceRecord(BaseModel):
    field_name: str
    value: Any
    state: Literal["verified", "provided", "estimated", "unknown"]
    source: str  # lender_api, bureau, open_banking, manual, etc.
    timestamp: datetime
    confidence: int  # 0-100
    caps_applied: List[str]
```

---

## 9) Program Catalog + Versioning

### 9.1 Program Schema
```python
class Program(BaseModel):
    program_id: UUID
    program_type: ProgramType  # credit_card, personal_loan, mortgage, auto
    provider_id: UUID
    geography_constraints: List[str]  # state codes
    eligibility_ruleset_id: UUID
    pricing_source: Literal["api", "manual", "estimate", "unknown"]
    required_docs: List[str]
    disclosures: List[UUID]
    effective_date: date
    deprecated_date: Optional[date]
    version: int
```

### 9.2 Versioning Rules
- Every change creates new version
- Cases pin specific version at runtime
- Delta queries show what changed between versions

### 9.3 Governance
- Only `admin` role can modify programs
- All changes logged with author + reason
- Deprecation requires 30-day notice (configurable)

---

## 10) Eligibility/Triage Engine

### 10.1 Status Definitions
| Status | Meaning | Required Output |
|--------|---------|-----------------|
| `ELIGIBLE` | Meets configured rules, required inputs present | Scenario generated |
| `REFER` | Missing verification or uncertain inputs | Verify checklist, human queue |
| `NOT_ELIGIBLE` | Fails configured rule with adequate confidence | Reason codes required |

### 10.2 Rules Engine Architecture
- Config-driven (YAML/JSON compiled to evaluators)
- Human-readable rule definitions
- Outputs: status, rule_hits, missing_inputs, reason_code_refs

### 10.3 Acceptance Tests
- [ ] Same inputs + same rules version → same status
- [ ] Every NOT_ELIGIBLE has at least one reason code
- [ ] Missing required field → REFER (not NOT_ELIGIBLE)

---

## 11) Reason Codes Engine

### 11.1 Adverse-Action-Safe Categories
| Code | Category | Example Rule Hit |
|------|----------|------------------|
| `RC001` | Insufficient credit history | thin_file = true |
| `RC002` | Credit score below threshold | score < program.min_score |
| `RC003` | Debt-to-income too high | dti > program.max_dti |
| `RC004` | Insufficient income | income < program.min_income |
| `RC005` | Unverifiable income | income_source = unknown |
| `RC006` | Recent delinquency | delinquency_months < 24 |
| `RC007` | Recent bankruptcy | bankruptcy_months < 48 |
| `RC008` | State/geography ineligible | state not in program.states |
| `RC009` | Missing required verification | verified_fields < required |

### 11.2 "What Can Improve" Generator
- Produces directional actions (e.g., "Reducing credit utilization may improve eligibility")
- Never promises outcomes
- Never references protected classes

---

## 12) Explainability Engine

### 12.1 Four-Layer Outputs
| Layer | Audience | Content |
|-------|----------|---------|
| Consumer | End user | Plain language, tradeoffs, next steps |
| Pro | Advisor/LO | Talk tracks, compliance phrasing, workflow |
| Compliance | Examiner | Provenance, versions, reason codes, audit refs |
| Deep Tech | Engineer | Rule hits, calculations, raw inputs |

### 12.2 No-New-Facts Enforcement
- Templates reference only stored fields
- LLM (if used) can rephrase but never invent claims
- Validator runs before output: any unknown field reference → error

### 12.3 Schema
```python
class Explanation(BaseModel):
    scenario_id: UUID
    layer: Literal["consumer", "pro", "compliance", "deep"]
    content: str
    field_references: List[str]  # validated against snapshot
    generated_at: datetime
```

---

## 13) Counterfactual Simulator (What-If Engine) — M22

### 13.1 Purpose
Allow consumers to simulate hypothetical changes and see estimated impact on eligibility and scenarios.

### 13.2 Inputs
```python
class CounterfactualRequest(BaseModel):
    case_id: UUID
    hypothetical_changes: Dict[str, Any]
    # e.g., {"credit_utilization": 0.20, "debt_payments": 1500}
```

### 13.3 Outputs
```python
class CounterfactualResult(BaseModel):
    original_status: Dict[str, str]  # program_id → status
    simulated_status: Dict[str, str]
    changes_summary: List[str]  # Plain language diffs
    confidence: Literal["low", "medium", "high"]
    confidence_reason: str
    disclaimer: str  # "This is an estimate, not a guarantee"
```

### 13.4 Guardrails
- Labeled as "simulation" everywhere
- Confidence capped if hypothetical changes are unverified
- Cannot simulate protected class changes (blocked)

### 13.5 Acceptance Tests
- [ ] Simulation with valid changes returns result in <2 seconds
- [ ] Protected class fields rejected with clear error
- [ ] Disclaimer always present in output

---

## 14) Alternative Data Engine — M19

### 14.1 Purpose
Ingest non-traditional data sources to serve credit-invisible and thin-file consumers.

### 14.2 Supported Sources
| Source | Provider Examples | Data Type |
|--------|-------------------|-----------|
| Open Banking | Plaid, MX, Finicity | Transactions, balances, income |
| Rent Payments | Experian RentBureau, Esusu | Payment history |
| Utility Payments | PRBC, data aggregators | Payment history |
| Gig Income | Argyle, Atomic | Earnings verification |

### 14.3 Consent Requirements
- Explicit consent per source
- Consent logged with scope, provider, timestamp
- Revocable at any time

### 14.4 Data Processing
```python
class AltDataRecord(BaseModel):
    source: str
    data_type: str
    raw_payload_hash: str  # stored separately
    normalized_fields: Dict[str, Any]
    provenance: Literal["verified"]
    retrieved_at: datetime
    consent_id: UUID
```

### 14.5 Failure Modes
| Failure | Handling |
|---------|----------|
| Provider timeout | Mark source as `unknown`, proceed with available data |
| Invalid credentials | Prompt re-authentication |
| Consent expired | Block pull, prompt renewal |

### 14.6 Acceptance Tests
- [ ] Open Banking pull completes in <10 seconds
- [ ] Revoked consent blocks subsequent pulls
- [ ] Thin-file consumer gets additional scenarios from alt data

---

## 15) Credit Pulse Monitor — M20

### 15.1 Purpose
Continuously monitor consumer credit profile (with consent) and trigger proactive alerts when changes affect scenarios.

### 15.2 Monitored Events
| Event | Source | Trigger |
|-------|--------|---------|
| New hard inquiry | Bureau | Alert + re-score |
| Balance change >10% | Open Banking | Re-run if threshold |
| New account opened | Bureau | Alert + scenario refresh |
| Payment reported | Bureau/Alt Data | Positive nudge if improvement |
| Delinquency reported | Bureau | Alert + coaching suggestion |

### 15.3 Consumer Controls
- Opt-in only (not default)
- Granular frequency settings (real-time, daily, weekly)
- Pause/resume/revoke at any time

### 15.4 Alert Schema
```python
class PulseAlert(BaseModel):
    consumer_id: UUID
    event_type: str
    detected_at: datetime
    summary: str
    impact: str  # "Your credit utilization improved to 23%"
    suggested_action: Optional[str]
    scenario_refresh_available: bool
```

### 15.5 Guardrails
- Alerts never claim approval changes
- Coach nudges are optional and labeled as suggestions
- Alert frequency respects consumer preferences (no spam)

### 15.6 Acceptance Tests
- [ ] Opt-in creates monitoring subscription
- [ ] Revocation stops all monitoring within 24 hours
- [ ] Alert generated within 15 minutes of detected change

---

## 16) Ranking Engine

### 16.1 Ranking Modes
| Mode | Primary Sort | Gate |
|------|--------------|------|
| `lowest_payment` | Monthly payment | Pricing confidence > 50 |
| `lowest_total_cost` | Total cost over term | Pricing confidence > 50 |
| `fastest_close` | Time to close | Doc completeness |
| `highest_certainty` | Confidence score | None |
| `best_goal_fit` | Goal alignment score | Goal specified |

### 16.2 Tie-Breakers
1. ELIGIBLE > REFER > NOT_ELIGIBLE
2. Higher confidence
3. Fewer missing verifications
4. Better goal fit

### 16.3 Sensitivity Notes
- If top-N scenarios are within 5% on primary metric, note equivalence
- Never mislead by implying false precision

---

## 17) Human Review Workflow

### 17.1 Queue Triggers
- Confidence < 50
- Contradictions unresolved
- Required verification missing
- Consumer disputes outcome
- Agent escalation

### 17.2 Review Ticket Schema
```python
class ReviewTicket(BaseModel):
    ticket_id: UUID
    case_id: UUID
    trigger_reason: str
    assigned_to: Optional[UUID]
    status: Literal["pending", "in_review", "resolved", "escalated"]
    created_at: datetime
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
```

### 17.3 Override Rules
- Every override requires: reason, notes, evidence (optional)
- Override creates new snapshot version
- Original snapshot preserved for audit

---

## 18) GOATCRD Crew (Agentic Orchestration)

### 18.1 Crew Conductor (M1 Replacement)

**Purpose:** Orchestrate all agents, manage lifecycle, enforce guardrails.

**Responsibilities:**
- Spawn and manage agent instances per case
- Route messages between agents
- Enforce checkpoint gates before state transitions
- Log all agent actions to audit trail
- Kill rogue agents (timeout, violation detection)

### 18.2 Agent Definitions

#### Intake Agent
- **Role:** Guide consumer through intake, ask clarifying questions
- **Allowed:** Ask questions, save drafts, flag contradictions
- **Forbidden:** Skip required fields, claim approvals

#### Triage Agent
- **Role:** Run eligibility rules, identify blockers/unlockers
- **Allowed:** Evaluate rules, assign status, generate reason codes
- **Forbidden:** Invent rules, override configured logic

#### Scenario Architect
- **Role:** Build universe, calculate rankings
- **Allowed:** Enumerate scenarios, calculate rankings, tag confidence
- **Forbidden:** Fabricate programs, invent pricing

#### Explainer Agent
- **Role:** Generate explanations, answer consumer questions
- **Allowed:** Rephrase stored facts, reference provenance
- **Forbidden:** Invent new facts, promise outcomes

#### Coach Agent
- **Role:** Proactive improvement suggestions
- **Allowed:** Suggest actions based on "what can improve" engine
- **Forbidden:** Guarantee results, pressure consumer

#### Compliance Guardian (Supervisor)
- **Role:** Monitor all agents for violations
- **Allowed:** Block outputs, escalate, terminate agents
- **Forbidden:** Override human governance decisions

### 18.3 Checkpoint Gates
| Gate | Condition | Action on Fail |
|------|-----------|----------------|
| Pre-Triage | All required intake fields present | Block, return to Intake Agent |
| Pre-Explanation | Snapshot saved | Block, save snapshot first |
| Pre-Export | Human review completed (if required) | Block, escalate to queue |

### 18.4 Agent Audit Logging
```python
class AgentAction(BaseModel):
    action_id: UUID
    agent_type: str
    case_id: UUID
    action_type: str
    inputs: Dict
    outputs: Dict
    timestamp: datetime
    checkpoint_passed: bool
```

---

## 19) Fairness CI/CD Pipeline (Mandatory)

### 19.1 Pre-Deployment Tests
| Test | Description | Threshold |
|------|-------------|-----------|
| Disparate Impact Ratio | Approval rate ratio across demographic proxies | > 0.80 |
| LDA Search | Identify less discriminatory alternatives | Documented |
| Feature Audit | Confirm no protected class proxies | Pass/Fail |

### 19.2 Deployment Gate
- Tests run automatically on PR to `main`
- Failure blocks deployment
- Human approval required for edge cases
- All test artifacts stored with version

### 19.3 Rollback Procedure
- If post-deploy monitoring detects drift, auto-rollback to previous version
- Alert sent to Fairness Lead

### 19.4 Monitoring Dashboard
- Real-time approval rates by demographic proxy
- Trend analysis over 7/30/90 days
- Anomaly detection with alerting

### 19.5 Artifact Storage
```python
class FairnessTestResult(BaseModel):
    test_id: UUID
    model_version: str
    rules_version: str
    test_type: str
    passed: bool
    metrics: Dict[str, float]
    run_at: datetime
    approved_by: Optional[UUID]
```

---

## 20) Embedded Finance SDK / LaaS — M21

### 20.1 Purpose
Enable B2B partners to embed GOATCRD scenarios in their platforms.

### 20.2 Partner Configuration
```python
class PartnerConfig(BaseModel):
    partner_id: UUID
    partner_name: str
    allowed_programs: List[UUID]
    branding: BrandingConfig
    disclosure_templates: List[UUID]
    callback_urls: Dict[str, str]
    created_at: datetime
```

### 20.3 API Surface
| Endpoint | Purpose |
|----------|---------|
| `POST /partners/{id}/cases` | Create case in partner context |
| `GET /partners/{id}/scenarios` | Retrieve scenarios for partner |
| `POST /partners/{id}/exports` | Generate partner-branded export |

### 20.4 Partner Guardrails
- Partner cannot modify program rules
- Partner cannot suppress reason codes or disclaimers
- Partner-specific audit trails maintained
- Deceptive UX patterns blocked by validation

### 20.5 Acceptance Tests
- [ ] Partner receives only allowed programs
- [ ] Reason codes always included in partner responses
- [ ] Audit log shows partner attribution

---

## 21) Security & Privacy Architecture

### 21.1 RBAC Roles
| Role | Permissions |
|------|-------------|
| `consumer` | Own data, own scenarios, own exports |
| `pro_user` | Assigned cases, limited PII view |
| `reviewer` | Queue access, override capability |
| `admin` | Full access, config changes, user management |
| `partner` | Partner-scoped access via SDK |

### 21.2 Encryption
- At rest: AES-256 for sensitive fields
- In transit: TLS 1.3 minimum
- Secrets: Vault-based, rotated quarterly

### 21.3 Retention
- Configurable per data type
- Default: 7 years for audit data, 90 days for session data
- Automated purge with verification

### 21.4 Redaction
- Consumer exports minimize PII
- Compliance exports require elevated role
- Redaction rules configurable per field

---

## 22) APIs (FastAPI)

### 22.1 Core Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/cases` | Create case |
| POST | `/cases/{id}/intake` | Submit intake |
| POST | `/cases/{id}/consent` | Grant/revoke consent |
| POST | `/cases/{id}/run` | Generate scenarios |
| GET | `/cases/{id}/scenarios` | List scenarios |
| GET | `/cases/{id}/rankings` | Get rankings |
| POST | `/cases/{id}/simulate` | Run counterfactual |
| GET | `/cases/{id}/pulse` | Get pulse alerts |
| POST | `/cases/{id}/exports` | Generate export |
| GET | `/cases/{id}/audit-snapshot` | Retrieve snapshot |

### 22.2 Consumer Rights Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/consumers/{id}/data-export` | 1033 data export |
| GET | `/consumers/{id}/access-log` | Access history |
| POST | `/consents/{id}/revoke` | Revoke consent |

### 22.3 Admin Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| CRUD | `/programs` | Program management |
| CRUD | `/rulesets` | Ruleset management |
| CRUD | `/reason-codes` | Reason code mapping |
| GET | `/fairness/dashboard` | Fairness metrics |

---

## 23) Postgres Data Model

### 23.1 Core Tables
| Table | Key Columns |
|-------|-------------|
| `cases` | id, consumer_id, status, created_at |
| `intake_snapshots` | id, case_id, data, version, created_at |
| `consents` | id, consumer_id, scope, granted_at, revoked_at |
| `programs` | id, type, provider_id, version, effective_date |
| `program_versions` | id, program_id, version, data, created_at |
| `rulesets` | id, name, version, rules_json |
| `scenarios` | id, case_id, program_id, status, pricing, confidence |
| `rankings` | id, case_id, mode, ranked_scenarios |
| `reason_codes` | id, code, category, description |
| `review_tickets` | id, case_id, status, assigned_to, resolved_at |
| `overrides` | id, ticket_id, reason, notes, created_by |
| `exports` | id, case_id, type, file_path, created_at |
| `audit_snapshots` | id, case_id, snapshot_data, version_pins |
| `audit_events` | id, event_type, actor_id, data, created_at |
| `agent_actions` | id, agent_type, case_id, action_type, data |
| `pulse_subscriptions` | id, consumer_id, frequency, active |
| `pulse_alerts` | id, consumer_id, event_type, summary |
| `alt_data_records` | id, consumer_id, source, data_hash |
| `fairness_tests` | id, model_version, passed, metrics |
| `partners` | id, name, config, created_at |

### 23.2 Version Stamps
All mutable tables include:
- `version: int`
- `created_at: timestamp`
- `updated_at: timestamp`
- `created_by: uuid`

---

## 24) Audit Snapshot & Reproducibility Contract

### 24.1 Snapshot Contents
- Intake snapshot (raw + normalized)
- Consent states at runtime
- Pinned program/rules versions
- Pricing sources + timestamps
- Scenario outputs + rankings
- Reason codes
- Explainability outputs
- Agent actions log
- Environment metadata (app version, feature flags)

### 24.2 Determinism Guarantee
- Same snapshot ID → same output
- External API responses stored with hash
- If reproduction differs, delta report generated

### 24.3 Delta Reporting
```python
class DeltaReport(BaseModel):
    snapshot_a: UUID
    snapshot_b: UUID
    rules_changed: List[str]
    programs_changed: List[str]
    outcomes_changed: Dict[str, str]  # program_id → "ELIGIBLE → NOT_ELIGIBLE"
    reason: str
```

---

## 25) Phased Delivery Plan

### Phase 0 — Foundation (2 sprints)
**Deliverables:** Repo, FastAPI skeleton, Postgres, RBAC, audit event log, basic intake schema
**Acceptance:** Create case → save intake → snapshot created

### Phase 1 — MVP Scenario Engine (4 sprints)
**Deliverables:** Program catalog (manual), rules engine, triage, scenario builder, ranking, reason codes, exports, basic fairness hooks
**Acceptance:** Same snapshot reproduces identical scenarios; NOT_ELIGIBLE has reason codes

### Phase 2 — Consent + Provenance Hardening (3 sprints)
**Deliverables:** Consent UX, provenance tags, confidence engine, human review queue
**Acceptance:** No external pull without consent; override requires notes

### Phase 3 — Alternative Data + Pulse (4 sprints)
**Deliverables:** M19 (Alt Data), M20 (Pulse), Open Banking integration, rent/utility
**Acceptance:** Thin-file consumer gets additional scenarios; Pulse alerts on change

### Phase 4 — Agentic Crew + Fairness CI/CD (4 sprints)
**Deliverables:** M1 (Crew Conductor), all agents, M22 (Counterfactual), Fairness CI/CD
**Acceptance:** Agents orchestrate end-to-end; deployment blocked without fairness pass

### Phase 5 — Embedded Finance + Scale (3 sprints)
**Deliverables:** M21 (LaaS SDK), partner onboarding, multi-tenant hardening
**Acceptance:** Partner creates case via SDK; partner audit trail separate

---

## 26) Delegation Prompts (30 Tasks)

Each prompt below is designed for a smaller coding model. Interfaces and tests specified.

1. **Postgres schema migrations:** `cases`, `intake_snapshots`, `consents`
2. **RBAC middleware:** Role model, permission checks
3. **Audit event writer:** Append-only, query interface
4. **Intake schema renderer:** JSON Schema + UI metadata
5. **Intake draft save/resume:** Endpoints + storage
6. **Normalization layer:** Buckets → numeric, schema-based
7. **Contradiction detector:** Configurable rules, flag output
8. **Consent objects + endpoints:** Grant, revoke, logging
9. **Program catalog tables:** Programs + versions + governance
10. **Ruleset storage:** YAML/JSON, versioning, compilation
11. **Rules evaluator:** Deterministic, returns hits
12. **Triage status generator:** Status + missing inputs
13. **Scenario enumeration:** Stable dedup keys, deterministic
14. **Pricing resolver:** Source lookup, provenance tags
15. **Confidence scoring:** Caps, drivers, verify checklist
16. **Ranking engine:** Multi-mode, gating, tie-breakers
17. **Reason code mapper:** Rule hits → codes
18. **"What can improve" generator:** Directional, no promises
19. **Explainability templates:** 4 layers, validation
20. **No-new-facts validator:** Template field checker
21. **Review queue + assignment:** Ticket lifecycle
22. **Override workflow:** Notes, audit, snapshot versioning
23. **Export packet generator:** Redaction, formats
24. **Audit snapshot writer:** Immutable, version pins
25. **Delta report generator:** Snapshot comparison
26. **Counterfactual engine:** Hypothetical input → simulated output
27. **Alt Data connector (Plaid):** OAuth, pull, normalize
28. **Pulse subscription manager:** Opt-in, frequency, revocation
29. **Pulse change detector:** Event detection, alert generation
30. **Crew Conductor scaffold:** Agent lifecycle, checkpoint gates

---

## 27) Appendix: Source Hardening Plan

### 27.1 Stats Requiring Citations
| Claim | Source Required |
|-------|-----------------|
| Credit invisible population | CFPB report, Census data |
| Market size | Industry analyst report |
| Regulatory requirements | CFPB circular, Federal Register |

### 27.2 Citation Storage
```python
class Citation(BaseModel):
    citation_id: UUID
    claim: str
    source_url: str
    source_name: str
    retrieved_at: datetime
    confidence: Literal["high", "medium", "low"]
```

### 27.3 Overclaim Prevention
- Marketing claims reviewed by compliance
- Engineering docs cite sources or mark as "assumption"
- Assumptions labeled clearly throughout this document

---

**END OF MASTER PLAN**

*This document is the canonical build specification for GOATCRD A+ Edition. All implementation should trace back to sections herein. Questions should be escalated to the Architecture Lead.*
