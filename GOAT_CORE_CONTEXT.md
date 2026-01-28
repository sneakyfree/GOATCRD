# GOAT CORE — Context File (Canonical, Shared Across All GOAT Repositories)
> Filename suggestion: `GOAT_CORE_CONTEXT.md`  
> Purpose: This is the **single source of truth** for how every GOAT platform is built (GOATLO, GOATMA, GOATFP, GOATIA and all GOATIA sub-specialists).  
> Paste this into every repo (or reference it from a monorepo) so no context is ever lost.

---

## 0) The GOAT Mission (North Star)
GOAT platforms are “Day-1 Superpower” systems for professionals who must compare complex product options under eligibility constraints.

**Definition of GOAT:**
A brand-new professional on Day 1 using GOAT can outperform a 20-year veteran by producing a more complete, accurate, explainable, and defensible comparison — faster than any human could do manually.

GOAT achieves this by implementing the same organism across domains:
**Deep Intake DNA → Validation → Eligibility/Constraints Rules → Universe Builder → Scenario Generation → Ranking → Explainability → Exports/Audit**

---

## 1) The GOAT Pattern (Universal Workflow)
Every GOAT platform follows this exact high-level workflow:

1) **Invite**
- Professional enters client phone/email → system sends secure magic link (SMS + email).

2) **Intake (“DNA Interview”)**
- Client completes mobile-first TurboTax-style interview (save/resume).
- Intake collects enough structured data to power exhaustive scenario generation.

3) **Validation + Contradictions**
- System validates required fields and flags contradictions.
- System generates verification questions and data-gap checklist.

4) **Eligibility / Constraints**
- Rules engine determines what is:
  - eligible & actionable now,
  - eligible later (timing or prerequisites),
  - not eligible / not available (with specific reasons).

5) **Universe Build**
- System enumerates the full set of options within connected sources and configured rule libraries.

6) **Scenario Generation**
- System builds a large scenario list (often dozens+) with consistent “Scenario Card” structure.

7) **Ranking + Sorting**
- System ranks scenarios multiple ways (cost, coverage, fit, risk, speed, etc.).
- System produces “Top 3 / Top 5” recommendations with reasons.

8) **Explainability Layers**
- Client View (simple)
- Sales View (talk tracks + objections)
- Technical View (analyst/underwriter style)
- Deep Details (expandable drill-down)

9) **Export + Audit**
- System exports proposal/report, and stores immutable evidence pack (inputs → sources → rules → outputs).

---

## 2) What “Exhaustive” Means (Non-Negotiable Truth)
GOAT never claims “scour the entire internet live.”

**Exhaustive = exhaustive within:**
- ingested datasets + snapshots,
- connected APIs/feeds,
- configured rule libraries (eligibility/appetite/constraints),
- and verified manual inputs (structured).

Every output must clearly show:
- sources used + timestamps
- assumptions
- confidence score
- missing data / verification checklist

**No silent guessing. Ever.**

---

## 3) The “Blockers + Unlockers” Engine (Core GOAT Magic)
GOAT is not just “what you qualify for.” It also outputs:

- **Blockers:** why an option is not currently eligible/quotable/enrollable
- **Unlockers:** what to verify or change to potentially enable it
- **Verification Questions:** prompts to resolve uncertainty (“Are you on Medicaid? Which level?” etc.)

Blockers types:
- **Hard no:** cannot qualify (out of geography, prohibited class, etc.)
- **Verifyable:** unknown status/missing info (ask questions, request docs)
- **Unlockable:** small changes can help (deductible, controls, timing, etc.)

All unlockers are phrased as “may qualify if” and “verify whether” — never promises.

---

## 4) Mobile-First Intake (No App Store Required)
The default GOAT intake experience is:
- **Secure magic link** via SMS/email
- **Mobile-first PWA web flow** (TurboTax style)
- Save/resume, accessibility, minimal typing
- Optional “Add to Home Screen” prompt after completion

Native apps are optional later, not required.

---

## 5) The 4 Output Layers (Always)
Each scenario/strategy must support these views:

### A) Client View (Plain-English)
- pros/cons
- key tradeoffs
- next steps
- minimal jargon

### B) Sales / Advisor View
- talking points
- objection handling
- compliance-safe phrasing
- personalized “because you said X…”

### C) Technical View (Analyst / Underwriter)
- assumptions
- sensitivity analysis
- risk flags
- missing docs / verification checklist

### D) Deep Details
- expandable drill-down
- forms/docs references when available
- source notes and lineage

---

## 6) Python-First Backend Standard (Non-Negotiable)
All GOAT systems are **Python-first** on the backend.

### Backend reference stack (recommended)
- **FastAPI** (APIs)
- **Pydantic** (typed schemas)
- **PostgreSQL** (system of record)
- **Redis** (cache + job coordination)
- **Celery/RQ** (background jobs)
- **S3-compatible storage** (documents, exports, evidence packs)
- **Prefect/Airflow** (scheduled ingestion pipelines) as needed

### Frontend (best UX, not forced to Python)
- **React/Next.js PWA** recommended for highest-quality UX and mobile-first intake
- React Native optional later; not required

---

## 7) GOAT CORE Modules (Shared Across All Repos)
GOAT CORE is the reusable “chassis” all GOAT products depend on.

### Core packages/modules (conceptual)
- `goat_core.auth`  
  Roles, permissions, secure link tokens, session management

- `goat_core.invites`  
  SMS/email link generation, expiry, one-time use, audit events

- `goat_core.intake_shell`  
  TurboTax-style interview engine (shared UI patterns + schema-driven screens)

- `goat_core.schemas`  
  Canonical typed schemas (Pydantic): Intake DNA, Scenario Cards, Plugin Contracts, Audit Snapshots

- `goat_core.validation`  
  Required fields, contradiction detection, verification question generation

- `goat_core.rules_framework`  
  Versioned rules engine interface for eligibility/constraints/triage/appetite logic

- `goat_core.universe_framework`  
  Base interface to enumerate option universes from connected sources

- `goat_core.scenario_builder`  
  Standard scenario construction pipeline (normalize → enrich → score → explain)

- `goat_core.ranking`  
  Multi-sort ranking + weighted scoring + tie-breakers + “avoid misleading rank” guardrails

- `goat_core.explain`  
  Layered explanations (client/sales/technical/deep), template-driven, optionally LLM-assisted
  **LLM NEVER invents facts**—it only explains known scenario fields or labeled assumptions.

- `goat_core.audit`  
  Immutable audit snapshots: input DNA + versions + sources + outputs + evidence pack

- `goat_core.exports`  
  PDF/report generation + action checklists

- `goat_core.plugins`  
  Plugin registry + plugin contracts + version pinning

- `goat_core.admin`  
  Configuration UI/services for rules versions, templates, appetite matrices, data sources

- `goat_core.observability`  
  Logs/metrics/traces, error budgets, anomaly detection hooks

---

## 8) Plugin Model (How Specialization Works)
GOAT CORE stays stable; specialization happens via plugins.

### Two plugin layers
1) **Vertical plugins:** GOATLO, GOATMA, GOATFP, GOATIA
2) **Sub-specialist plugins:** e.g., GOATIA → Trucking/Cyber/BuildersRisk/CommercialLines

### Plugin contract must define
- Intake extension schema (Pydantic)
- Rulesets (eligibility/triage/appetite/constraints) + version
- Universe builder connectors (ingested sources / APIs / manual sources)
- Scenario template requirements
- Ranking dimensions (what matters most)
- Required documents + checklist rules
- Blockers/unlockers library (structured)

GOAT CORE provides the engine; plugins provide the domain DNA.

---

## 9) Schema Discipline (Typed Interfaces Everywhere)
All major boundaries must be typed and versioned (Pydantic models):

- Intake DNA schema (base + extensions)
- Scenario Card schema
- Plugin contract schema
- Audit snapshot schema
- Export artifact schema

This enables:
- reliable delegation to lower-context coding models
- safe refactoring
- reproducible outputs

---

## 10) Confidence Scoring (Required Everywhere)
Every scenario/strategy must include:
- overall confidence: low/medium/high
- drivers of confidence
- data gaps / missing fields
- verification checklist

Confidence is lowered when:
- key docs missing
- unknown eligibility flags
- missing pricing sources
- incomplete inputs

---

## 11) Auditability (E&O / Compliance Grade)
Every generated output must be reproducible.

Audit snapshot stores:
- intake DNA snapshot (immutable)
- plugin versions used
- rules versions used
- data snapshot ids used + timestamps
- scenario output list
- export artifacts
- user actions (who generated, who viewed, who exported)

---

## 12) Non-Goals (MVP)
- Live “internet scraping for exhaustiveness”
- Guaranteed outcomes (rates, eligibility, returns, bindability)
- Perfect third-party directory accuracy (provider lists, vendor directories, etc.)
- Binding/enrolling/submitting unless integrated with licensed workflows

---

## 13) Build Strategy (How We Ship Without Losing Depth)
### Rule:
**Build GOAT CORE once, then build specialists individually.**

- CORE delivers reusable power: intake shell, validation, ranking, explainability, audit, exports.
- Each vertical/specialty is added via plugins one at a time, preserving real depth.

Why:
- Shipping “all specialties at once” produces shallow, fake expertise.
- Shipping one niche deeply produces “holy crap” demos and real value.

---

## 14) Repository Placement Guidance
The GOAT CORE context should exist in all repos in one of two ways:

### Preferred
- Single shared repo (or monorepo `/core`) and each product references it as a dependency.
- Each product repo includes this file as documentation and points back to the canonical core.

### Acceptable
- Copy this file into each repo as documentation, but do NOT fork core code. Keep core code centralized to avoid drift.

---

## 15) “GOAT Done-Right” Checklist
A GOAT product is considered correctly built only if:
- A Day-1 professional can produce a complete, ranked, explainable comparison
- Not-eligible options produce blockers/unlockers + verification questions
- Output is layered (client/sales/technical/deep)
- Every claim is sourced, assumed, or explicitly unknown
- Mobile secure link intake works perfectly
- Audit snapshots make outputs reproducible and defensible
- Backend is Python-first, typed, versioned, and modular
