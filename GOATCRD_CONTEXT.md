# GOATCRD (Goat Consumer/Credit) — Repository Context File (Vision + Guardrails)
> Filename: `GOATCRD_CONTEXT.md`  
> Purpose: Canonical vision + non-negotiables for GOATCRD.  
> Positioning: GOATCRD is the “TurboTax-meets-Compliance-meets-Decisioning” platform for consumer credit and credit-adjacent financial recommendations, built with extreme fairness, auditability, and regulator-grade disclosure hygiene.

## 0) Naming Clarity (Non-Negotiable)
- GOATCY = Cyber Insurance (commercial cyber underwriting + security posture)
- GOATCRD = Consumer/Credit Risk (highly regulated, fairness + adverse action + UDAP exposure)

## 1) The GOAT Organism (Shared GOAT CORE Pattern)
Secure Link Invite → TurboTax Intake → Validation/Contradictions → Eligibility/Triage → Scenario Universe → Ranking → Layered Explanations → Export + Audit Snapshot

For GOATCRD, the same organism applies, but with heavier constraints:
- more disclosures
- more consent UX
- more audit trails
- stricter “no-black-box” requirements

## 2) North Star Vision (Begin With The End In Mind)
GOATCRD enables a Day-1 professional (or consumer self-serve) to:
- collect complete and accurate consumer financial + goal inputs
- generate multiple outcome scenarios (not just one recommendation)
- explain tradeoffs in plain language
- clearly separate: “what we know” vs “what we estimate” vs “what must be verified”
- produce regulator-grade documentation for every action and output

## 3) GOATCRD Laws (Hard Guardrails)
These are non-negotiable and must be enforced technically (not just in copy).

### 3.1 No Hallucination / No Unverifiable Claims
- Never invent terms, rates, approvals, or eligibility thresholds.
- All offers/terms must be source-labeled: lender API / bureau / manual / estimate.
- Any estimate must be labeled “estimate” and must never be framed as an approval.

### 3.2 Fairness / ECOA / Disparate Impact Risk Controls
- No hidden decisioning.
- Every decision output must be explainable and auditable.
- Features must be documented with lawful basis for use.
- “Sensitive attribute” handling must follow policy: do not request or infer protected class attributes.

### 3.3 Adverse Action + Explanation Hygiene
- If the system indicates denial/unfavorable terms, it must:
  - provide standardized reason categories (configurable)
  - provide a “what can improve” pathway without promising outcomes
  - store a complete audit record of inputs + model + rules + versions

### 3.4 UDAP / Deception Avoidance
- Must not mislead users about:
  - certainty
  - approval likelihood
  - reasons for outcomes
  - who is offering the product
- Must show disclaimers clearly and early.

### 3.5 Consent, Privacy, Security
- Explicit consent before pulling any bureau data or external data.
- Minimize PII, tokenize where possible, strict RBAC.
- Encryption at rest/in transit.
- Data retention policy is explicit and enforced.

### 3.6 Human-in-the-Loop for High-Risk Decisions
- For any low-confidence decision or missing required verification, the system must escalate to:
  - “REFER” workflow with checklist
  - or “Needs human review”
- Never “auto-decline” without explanation scaffolding and audit completeness.

## 4) What GOATCRD Actually Does (MVP Scope)
GOATCRD is not “approve/deny magic.”
It is a scenario engine that can (depending on integrations and permissions):
- gather consumer financial and goal inputs
- optionally enrich with verified data (only with consent)
- generate scenarios across configured products
- rank scenarios by different criteria (payment, total cost, risk, speed, certainty)
- explain tradeoffs and next steps
- produce a compliance-grade “decision packet” record

## 5) Output Layers (Mandatory)
1) Consumer view: plain language + tradeoffs + next steps + verify checklist
2) Pro view (advisor/LO/agent): talk tracks + compliance-safe phrasing
3) Compliance/audit view: full rationale + feature provenance + version stamps
4) Deep technical view: rules + model versions + inputs + logs

## 6) Architecture Preference
- Backend: Python-first (FastAPI + Pydantic + Postgres)
- Frontend: best UX (PWA recommended)
- Every output is tied to an immutable audit snapshot ID.

## 7) What “Exhaustive” Means Here
Exhaustive = all configured product programs + connected sources + rulesets.
Never “the whole internet.”

## 8) Acceptance Criteria (GOATCRD Done-Right)
- Every output is explainable, source-labeled, and version-stamped.
- Any uncertainty triggers “REFER” with verify checklist.
- Fairness and compliance controls are engineered-in (not “policy docs only”).
- Full audit snapshots reproduce outputs deterministically or show deltas.

---
