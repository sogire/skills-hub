# {{PROJECT_NAME}}: Prioritized GCP Topics & Exploration Roadmap

**Context:** {{CUSTOMER_NAME}} — {{PROJECT_NAME}} ({{PROGRAM_NAME}}) — {{MEETING_TITLE}}  
**Reference Document:** [{{MEETING_DOC_TITLE}}](https://docs.google.com/document/d/{{DOC_ID}}/edit)  
**Participants & Key Stakeholders:** {{PARTICIPANTS_LIST}}  

---

## Session Structure & Presentation Flow (Customer-Led vs. Google-Led)

> [!NOTE]
> **Per-Meeting vs. Project-Level Usage**:
> - In **per-meeting files** (`project/meetings/YYYY-MM-DD_<slug>/YYYYMMDD_challenges_<slug>.md`), use this table to document the chronological **Customer-Led** vs. **Google-Led** segments of the session.
> - In the **project-level master file** ([`project/common/project_challenges.md`](../../project/common/project_challenges.md)), pair or replace this table with the cumulative **Architectural Challenge Overview (`D1..Dn`)** table linking to all covered sessions and deep-dive deliverables.

| Segment # | Leadership | Time Range | Lead Presenter(s) | Segment Focus, Demos & Artifacts Shown | Primary Domains |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Customer-Led (`{{CUSTOMER_NAME}}`)** | `00:00 – 00:45` | {{CUSTOMER_PRESENTERS}} | Presented current {{PILOT_DOMAIN}} pipeline architecture (`Bronze` / `Silver` / `Gold`), source system ingestion patterns, and governance requirements. | `D1`, `D3`, `D4` |
| **2** | **Google-Led (`Google Cloud`)** | `00:45 – 01:30` | {{GOOGLE_PRESENTERS}} | Presented Data Mesh product tier boundaries, Analytics Hub zero-copy sharing ("Consumer Pays"), hybrid RBAC/ABAC security patterns, and FinOps guardrails. | `D1`, `D2`, `D3`, `D7` |

---

## 1. {{TOPIC_1_TITLE}} (D1)

### 1. Customer Current State, Implementations & Ambitions ({{CUSTOMER_NAME}}-Led)
* **Current Domain Pipeline Setup:** {{CUSTOMER_NAME}}'s engineering team ingests operational source feeds into `Bronze` and executes `Dataform` transformations across `Silver` and `Gold` to build the initial **{{PILOT_DOMAIN}}** data products.
* **Enterprise Scaling Ambition:** {{CUSTOMER_NAME}} aims to standardize project provisioning (via Terraform / Project Factory with `{{EXTERNAL_PARTNERS}}`) to onboard upcoming domains (`{{UPCOMING_DOMAINS}}`).

### 2. Core Architectural Challenges & Friction Points
* **Medallion Layer vs. Data Product Classification Ambiguity:** Uncertainty around whether normalized `Silver` entities should be shared directly from `Silver` or promoted to `Gold`, and how to define boundaries between **Source**, **Aggregated**, and **Consumer** Data Products.
* **Source Ownership & Manual Data Feeds:** Operational source systems are managed by central IT rather than domain data stewards, and manual CSV/spreadsheet snapshots require delta extraction and schema validation.

### 3. Google Cloud Architectural Solutions & Recommendations (Google-Led)
* **Normalize in `Silver`, Expose Exclusively via `Gold`:** Keep `Bronze`, `Silver`, and `Gold` as internal engineering layers. Perform entity reconciliation in `Silver`, and publish governed views in `Gold` as **Source-Aligned Data Products** so downstream consumers never couple to internal transformation schemas.
* **Tripartite Data Product Standard:**
  * **Source Data Products:** Clean, normalized operational entities exposed in `Gold`.
  * **Aggregated Data Products:** Cross-source domain star schemas in `Gold`.
  * **Consumer Data Products:** Use-case-specific marts and semantic views exposed via **Analytics Hub**.

### 4. Proposed Exploration Roadmap & Action Items (Owner-Attributed)
* **`[Google Cloud — {{GOOGLE_ARCHITECT_NAME}}]` Share Data Mesh Reference Blueprint:** Provide reference documentation and naming standards for Source, Aggregated, and Consumer Data Products.
* **`[{{CUSTOMER_NAME}} — {{CUSTOMER_LEAD_NAME}}]` Validate Terraform Project Factory Template:** Align declarative GCP project provisioning templates across `dev`, `staging`, and `prod` environments.

---

## 2. {{TOPIC_2_TITLE}} (D2)

### 1. Customer Current State, Implementations & Ambitions ({{CUSTOMER_NAME}}-Led)
* **Cross-Domain Sharing & FinOps Objective:** {{CUSTOMER_NAME}} wants to share curated datasets across multiple business units, BI dashboards, and AI agents while ensuring the producer domain only pays for storage and ETL creation and consumer domains pay for their own query compute.

### 2. Core Architectural Challenges & Friction Points
* **Direct IAM Sprawl & Compute Attribution:** Granting external consumers direct IAM roles inside producer datasets creates permission sprawl and charges consumer query slot usage back to the producer GCP project.
* **End-User Identity Propagation:** Shared service accounts for BI or AI agents can obscure `SESSION_USER()`, breaking row- and column-level security policies.

### 3. Google Cloud Architectural Solutions & Recommendations (Google-Led)
* **Zero-Copy Sharing via `BigQuery Analytics Hub`:** Publish curated `Gold` Data Products into a central **Analytics Hub** Exchange. Subscribers mount zero-copy virtual **Linked Datasets** inside their own consumer GCP projects, ensuring real-time updates where the producer pays for storage and the subscriber pays 100% of query compute.
* **Enforce `RLS` and `CLS` Once on Producer `Gold` Tables:** Define Row-Level Security (`RLS`) and Dataplex Policy Tags (`CLS` / Dynamic Data Masking) on the authoritative `Gold` tables; Analytics Hub linked datasets automatically inherit and enforce these policies at subscriber query time.

### 4. Proposed Exploration Roadmap & Action Items (Owner-Attributed)
* **`[Google Cloud — {{GOOGLE_ARCHITECT_NAME}}]` Analytics Hub Live Prototype:** Demonstrate end-to-end publisher-subscriber linked dataset creation and `INFORMATION_SCHEMA.JOBS_BY_PROJECT` compute attribution.
* **`[Joint — {{CUSTOMER_LEAD_NAME}} & {{GOOGLE_ARCHITECT_NAME}}]` Access Governance Workshop:** Schedule a deep-dive session on hybrid persona-based `RBAC` and dynamic entitlement-table `ABAC` patterns.

