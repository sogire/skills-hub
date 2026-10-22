# Phase 1 Guide: Interactive Storyboard ("Grill-Me") & Single-Sandbox Simulation

## 1. Conducting the Phase 1 "Grill-Me" Interview

Follow these rules when interviewing the user in Phase 1:
1. **Explore Workspace Context First**: Before asking any question, inspect `<workspace>/specs/specs_project.md`, `project/common/project_questions-log.md`, `project/common/project_challenges.md`, and existing `project/topics/<topic-slug>/docs/` so you never ask what the repository already answers.
2. **One Question at a Time via `ask_question`**: Put your recommended option first, prefixed with `(Recommended)`.
3. **5 Decision Branches to Resolve**:
   - **Branch A — Canonical Domain & Topic Slug**: Map the demo to `D1..Dn` (e.g., `platform-framework`, `access-management`, `security-compliance`, `data-quality-dlq`, `catalog-lineage`, `observability-monitoring`, `ai-agents-finops`). Target path: `project/topics/<topic-slug>/demos/<demo-slug>/`.
   - **Branch B — Storyline Hook & Customer Parallel**:
     - *Pattern 1 (Recommended for executive + technical workshops)*: **Universal Detective Metaphor + Customer Industry Parallel** — e.g., a crisp 20–50 row synthetic dataset with 1 planted anomaly (a tampered container seal, a rogue supplier rebate, a miscalibrated plant sensor) paired explicitly with the customer's real business domain from `specs_project.md`.
     - *Pattern 2*: **Synthetic Customer-Domain Dataset** — synthetic tables named directly after the customer's Pilot Domain entities (using 100% synthetic values).
   - **Branch C — Act Structure & Contrast Beats (3–6 Acts)**:
     Every strong GCP Console story includes:
     - **Setup / Curation Act** (`Producer` persona): Rich table/column "nutrition labels," graph/relational relationships, and governance tags.
     - **Consumption / Speed Act** (`Consumer` persona): Instant discovery, zero-copy Linked Dataset mounting, or AI/SQL insight locating the planted anomaly.
     - **Security / Governance Contrast Act** (`Restricted` vs. `Authorized` persona): Side-by-side proof where an unauthorized query hits a kernel block or dynamic mask (`red` callout) while the governed path succeeds (`green` callout).
     - **Observability / FinOps Act** (`Producer` or `Platform` persona): Audit trail (`INFORMATION_SCHEMA` / Lineage / DQ scorecard) proving governance without bottlenecks.
   - **Branch D — Sandbox Project & Argolis Persona Roster**:
     Check Section 6 of `specs/specs_project.md`. If missing, collect:
     - Single `SANDBOX_PROJECT_ID` and `BQ_LOCATION` / `GCP_REGION` (e.g., `EU` / `europe-west1`).
     - Argolis test user emails per persona (e.g., `producer` = primary owner account, `consumer` = secondary Argolis user `consumer-test@...` with restricted IAM so Console screenshots show authentic `Access Denied` / masked states).
   - **Branch E — Deliverable Bundle**:
     Confirm whether to generate the optional companion `docs/<demo-stem>_slides-prompt.md` alongside the default `docs/<demo-stem>.md` + `diagrams/<demo-stem>/architecture-flow.svg` + `screenshots/<demo-stem>/*.png`.

---

## 2. Simulating Multi-Project Data Mesh Topologies in a Single Sandbox Project

Because we strictly deploy into **one existing Sandbox GCP Project** (never creating/deleting GCP projects), use **Domain Resource Prefixing + Per-Scene DOM Project Aliasing** to simulate cross-project architectures cleanly:

| Architectural Plane in the Story | Physical Resource in Single `SANDBOX_PROJECT_ID` | Persona IAM Granted on Physical Resource | `project_display_alias` Applied in Scene Screenshot |
| :--- | :--- | :--- | :--- |
| **Producer "Yellow Box" Project** | Dataset `<demo>_prod_<dataset>` + Exchange `<demo>_exchange` + Policy Tag Taxonomy | `producer` email: Project Owner / Data Owner + Policy Tag Admin | `gcp-<producer-domain>` (e.g., `gcp-logistics-domain`) |
| **Consumer "Blue Box" Project** | Subscribed Linked Dataset `<demo>_cons_<shared_dataset>` (subscribed inside the same project!) + Consumer Scratch Dataset `<demo>_cons_workspace` | `consumer` email: `roles/bigquery.jobUser` at project level + `roles/analyticshub.subscriber` on Listing + `roles/bigquery.dataViewer` **only** on `<demo>_cons_*` (**zero** IAM on `<demo>_prod_*`!) | `gcp-<consumer-domain>` (e.g., `gcp-supplychain-domain`) |
| **Data Clean Room** | Exchange `<demo>_dcr_exchange` (`dcrExchangeConfig`) + Privacy View in `<demo>_prod_<dataset>` $\rightarrow$ Linked Dataset `<demo>_cons_<dcr_linked>` | `consumer` email: Subscriber on Clean Room listing (blocked from raw `SELECT *` and small cohorts $< k$) | `gcp-<consumer-domain>` |
| **Central Governance / Catalog** | Dataplex Lake/Zone or Knowledge Catalog Data Product & Data Quality Scan `<demo>_dq_*` | `producer` / `steward` email: Dataplex Admin; `consumer` email: Catalog Viewer | `gcp-governance-hub` |

> [!TIP]
> **Why This Works Authentically in BigQuery & Analytics Hub**:
> Even within a single GCP project, a user who only holds `roles/bigquery.jobUser` at the project level and dataset-level IAM on `<demo>_cons_*` has **zero visibility or read access** to `<demo>_prod_*`! Meanwhile, subscribing to an Analytics Hub Listing creates a true read-only Linked Dataset (`<demo>_cons_<shared_dataset>`), enforces Data Catalog Policy Tags (`CLS`) and Row-Level Security (`RLS`), enforces Restricted Export (`CTAS` block), and logs queries to `INFORMATION_SCHEMA.SHARED_DATASET_USAGE`. Combined with `capture_gcp_console.py` replacing `<demo>_prod_` / `<demo>_cons_` and `SANDBOX_PROJECT_ID` in the DOM per scene, every screenshot looks and behaves identically to a multi-project enterprise deployment.

---

## 3. Storyboard Approval Table Template (Gate 1)

Present a compact approval table like this before running Phase 2:

| Act | Story Beat | Active Persona (`Chrome Profile`) | Physical Sandbox Target | GCP Capability Proven | Target Screenshot (`screenshots/<stem>/`) |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | Curate & Publish Data Product | `producer` | `<demo>_prod_cargo` + `<demo>_exchange` | Rich metadata + Private Exchange Listing | `act-01-exchange-listing.png` |
| **2** | Zero-Copy Subscribe & Trace Anomaly | `consumer` | `<demo>_cons_cargo_shared` | `< 2s` Linked Dataset mount + SQL anomaly trace | `act-02-linked-investigation.png` |
| **3A** | Unauthorized Passcode Query Blocked | `consumer` | `maritime_security_registry.clc_ovr_cd` | Kernel Column-Level Security (`CLS`) block | `act-03a-cls-blocked.png` |
| **3B** | Authorized Columns Unmask Custodian | `consumer` | `SELECT * EXCEPT(clc_ovr_cd)` | View-less fine-grained governance | `act-03b-cls-authorized.png` |
| **4** | Egress Lock Blocks `CTAS` Copy | `consumer` | `restrictedExportConfig = true` | Anti-exfiltration taint tracking | `act-04-egress-ctas-blocked.png` |

