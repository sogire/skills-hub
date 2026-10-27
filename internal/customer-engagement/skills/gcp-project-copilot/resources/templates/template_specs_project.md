# Customer & Project Specification (`specs_project.md`)

> [!IMPORTANT]
> This file is the **customer-specific configuration companion** to the `gcp-project-copilot` skill.
> Keep the skill assets unchanged and customize only this `specs/specs_project.md` file (and `specs/gdrive_sync_manifest.json`) for each customer project workspace.

---

## 1. Customer & Project Identity

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **`CUSTOMER_NAME`** | **{{CUSTOMER_NAME}}** | {{CUSTOMER_DESCRIPTION}} (e.g., Enterprise industry & primary domain `example.com`) |
| **`PROJECT_NAME`** | **{{PROJECT_NAME}}** | {{PROJECT_DESCRIPTION}} (e.g., Enterprise data platform modernizing ingestion, governance, and AI/BI) |
| **`PROGRAM_NAME`** | **{{PROGRAM_NAME}}** | Umbrella digital/AI/data transformation initiative sponsoring the platform |
| **`PILOT_DOMAIN`** | **{{PILOT_DOMAIN}}** | Initial domain building the blueprint pipeline, data products, and governance model on GCP |
| **`UPCOMING_DOMAINS`** | {{UPCOMING_DOMAINS}} | Target business or engineering domains for subsequent platform onboarding |
| **`EXTERNAL_PARTNERS`** | **{{EXTERNAL_PARTNERS}}** | External system integrators or consulting partners collaborating on the project |

---

## 2. Google Drive Directories & Reference Documents

> [!TIP]
> Add or update main Google Drive folder URLs and shared deliverable documents below so the agent can discover new meeting notes or export/synchronize Markdown outputs directly to Google Drive.

### 2.1 Main Google Drive Folders

| Directory Purpose | Google Drive Folder URL / ID | Notes |
| :--- | :--- | :--- |
| **Root Project Drive Folder (`{{DRIVE_ROOT_FOLDER_NAME}}`)** | [{{DRIVE_ROOT_FOLDER_ID}}](https://drive.google.com/drive/folders/{{DRIVE_ROOT_FOLDER_ID}}) | Main shared folder for the engagement (`project/` mirror root) |
| **Meeting Notes & Recordings Folder** | [{{MEETING_NOTES_FOLDER_ID}}](https://drive.google.com/drive/folders/{{MEETING_NOTES_FOLDER_ID}}) | Location where Google Meet Gemini notes & transcripts are stored |
| **Architecture & Deliverables Folder** | [{{DELIVERABLES_FOLDER_ID}}](https://drive.google.com/drive/folders/{{DELIVERABLES_FOLDER_ID}}) | Location for shared Google Docs, architecture blueprints, and slide decks |

### 2.2 Synchronized `project/` Google Drive Hierarchy & Native Google Docs Registry

> [!NOTE]
> All synchronized Google Drive subfolder IDs, native Google Docs URLs, diagram/screenshot/CSV asset links, and SHA-256 content hashes for [`project/`](../project/) are managed automatically in [`specs/gdrive_sync_manifest.json`](./gdrive_sync_manifest.json) via `sync_drive.py`.

---

## 3. Canonical Architectural Domain Taxonomy

All extracted questions (`questions-log`) and architectural topics (`challenges`) for this customer project must be mapped to the following canonical domains (`D1..Dn`).

> [!IMPORTANT]
> **New Domain Governance Protocol (Interactive Gatekeeper & Logical Slug First)**:
> 1. **Prefer Keyword Expansion First**: If a meeting introduces a sub-topic that shares the same governance boundary or GCP service family as an existing domain (`D1..Dn`), map it to that existing domain and append the new keywords to its `Core Technical Scope & Keywords` cell below.
> 2. **Interactive User Approval Before Creating `D(n+1)`**: If a meeting introduces a genuinely distinct architectural pillar (e.g., a dedicated agenda segment or $\ge 2$ questions that do not fit `D1..Dn`), the agent MUST pause before generating output files and ask the user via `ask_question` whether to:
>    - **Create a new domain `D(n+1)`** in this table, OR
>    - **Merge it into an existing domain `D#`** (expanding its keywords).
> 3. **Logical Slug First (Lazy `project/topics/` Creation)**: When a new domain `D(n+1)` is approved, record its `project/topics/` Directory Slug below as plain code (e.g., `` `<new-slug>` ``) without creating an empty physical folder under `project/topics/`. Only create the physical directory `project/topics/<new-slug>/docs/` and convert the slug into a clickable relative link (`[<new-slug>](../project/topics/<new-slug>/...)`) when a deep-dive deliverable is actually generated.

| Domain ID | Canonical Domain Name | `project/topics/` Directory Slug | Core Technical Scope & Keywords |
| :--- | :--- | :--- | :--- |
| **D1** | **Data Platform Foundation, Ingestion & Data Products** | `platform-framework` | Medallion architecture (`Bronze` / `Silver` / `Gold`), Data Product classification & contracts, batch/streaming ingestion (`Dataflow`, `Pub/Sub`, `DTS`), ELT pipelines (`Dataform`, `dbt`, `Managed Spark`), GCP Project Factory & Terraform IaC |
| **D2** | **Data Sharing, Consumer Authorization & Access Management** | `access-management` | Consumer application & user authorization models, least-privilege view-level access (`Authorized Views` / `Authorized Datasets`), stable semantic interface datasets, `BigQuery Sharing (Analytics Hub)`, approval workflows & IAM scale quotas |
| **D3** | **Data Governance, Knowledge Catalog, Quality & Security** | `governance-security` | `Dataplex Universal Catalog` (Knowledge Catalog Data Products, business glossary, aspect types, `Data Lineage`), automated Data Quality & profiling scans, banking/enterprise compliance, `Cloud DLP`, BigQuery Column-Level Security (`Policy Tags` / Dynamic Masking), Row-Level Security (`RLS`), CMEK & `VPC-SC` |
| **D4** | **Analytics Consumption, Semantic Layer, BI & Applied ML** | `analytics-bi-ml` | Enterprise BI & governed semantic layer (`Looker`, `Conversational Analytics`), analytical SQL patterns, `BigQuery ML` (`BQML`), Python/Spark analytics (`BigFrames`, notebooks), unstructured & graph analytics (`BigLake`, `BigQuery Graph`) |
| **D5** | **Platform Observability, Capacity Optimization & FinOps** | `observability-finops` | `BigQuery Editions` slot reservations & autoscaling, physical/logical storage & partitioning/clustering optimization, centralized `INFORMATION_SCHEMA` & Cloud Logging telemetry, and producer vs. consumer compute cost attribution |
| **D6** | **AI Agents Architecture, Orchestration & Data Grounding** | `ai-agents-architecture` | Agentic design & multi-agent orchestration (`Google ADK`, `Gemini Enterprise`), grounding agents on governed Data Products (`Google Cloud MCP`, `BigQuery Data Agents`, `Data Agent Kit`, Vector Search/RAG), and end-to-end identity passthrough (`OAuth On-Behalf-Of` $\rightarrow$ `SESSION_USER()`) |
| **D7** | **AgentOps, Evaluation, Security Guardrails & AI FinOps** | `agentops-governance` | Agent evaluation datasets & quality metrics (`ADK Eval`, `Vertex AI Evaluation`), agent tracing & telemetry (`Cloud Trace`, `Cloud Logging`), prompt/tool security guardrails (`Model Armor`, IAM tool boundaries), and combined LLM token + BigQuery slot FinOps guardrails |
| **P1** | **Project Organization, Workstream Alignment & Delivery Governance** | `project-organization` | Engagement roadmap & milestone prioritization, workshop cadence & session preparation, cross-workstream alignment across Data, Analytics & Agents, and PoC/pilot handoff logistics |

---

## 4. Customer Glossary & Stakeholder References (`project/common/`)

To avoid duplication, the full **Customer Glossary of Terms** and **Stakeholder Roster** are maintained exclusively at the project level in `project/common/`:
- **Living Customer Glossary**: [`project/common/project_glossary.md`](../project/common/project_glossary.md)
- **Living Stakeholder Roster**: [`project/common/project_members.md`](../project/common/project_members.md)

---

## 5. Transcript Phonetic Alias & Handle Dictionary (Internal Only)

> [!IMPORTANT]
> **Official Document Separation**: Because [`project/common/project_members.md`](../project/common/project_members.md) is a clean, customer-facing stakeholder directory, **Transcript Phonetic Aliases and ASR variants must reside exclusively in this section of `specs_project.md`** and must never appear in `project_members.md`.
> Voice transcripts generated by Google Meet frequently misspell participant names or show handles/markers. Always use this dictionary to normalize transcript aliases to their canonical stakeholder identity when updating [`project_members.md`](../project/common/project_members.md), `questions-log`, and `challenges`:

| Canonical Full Name | Organization | Handle / Email Prefix | Known Transcript Aliases & ASR Variants |
| :--- | :--- | :--- | :--- |
| **{{STAKEHOLDER_FULL_NAME}}** | {{CUSTOMER_NAME}} | `@{{HANDLE}}` | `{{ASR_VARIANT_1}}`, `{{ASR_VARIANT_2}}` |
| **{{ARCHITECT_FULL_NAME}}** | Google Cloud | `@{{GOOGLE_HANDLE}}` | `{{ASR_VARIANT_1}}`, `{{ASR_VARIANT_2}}` |
| **{{PARTNER_FULL_NAME}}** | External Partner | `@{{PARTNER_HANDLE}}` | `{{ASR_VARIANT_1}}` |

---

## 6. Sandbox GCP Demo Environment & Persona Accounts (Internal Only — Optional)

> [!IMPORTANT]
> **Local-Only Demo Configuration (`gcp-console-demo-generator`)**:
> Because `specs/specs_project.md` is excluded from Google Drive synchronization, store your single Sandbox / Argolis GCP Project ID and test persona emails here so `gcp-console-demo-generator` can provision demo assets in `.runtime/` and mask these internal identifiers with customer-aligned aliases in all screenshots and `project/` deliverables.

| Parameter / Persona Role | Internal Sandbox / Argolis Value | Customer-Facing Story Alias (`docs/` & DOM Mask) | Notes |
| :--- | :--- | :--- | :--- |
| **`SANDBOX_PROJECT_ID`** | `{{SANDBOX_PROJECT_ID}}` | `gcp-producer-domain` / `gcp-consumer-domain` | Single existing Sandbox GCP project hosting prefixed `<demo>_*` assets |
| **`SANDBOX_REGION` / `BQ_LOCATION`** | `{{SANDBOX_REGION}}` / `{{BQ_LOCATION}}` | `{{BQ_LOCATION}}` | Regional / multi-regional location for demo datasets & exchanges |
| **Persona: `producer` (Owner / Steward)** | `{{PRODUCER_ARGOLIS_EMAIL}}` | `steward@producer-domain` | Persistent Chrome CDP profile cached by email |
| **Persona: `consumer` (Subscriber / Analyst)** | `{{CONSUMER_ARGOLIS_EMAIL}}` | `analyst@consumer-domain` | Least-privilege test user demonstrating CLS/RLS/Egress enforcement |

