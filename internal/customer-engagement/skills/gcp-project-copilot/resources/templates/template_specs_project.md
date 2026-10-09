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
> Maintained automatically via `sync_drive.py` and [`specs/gdrive_sync_manifest.json`](./gdrive_sync_manifest.json). Run `sync_drive.py` to synchronize any new or modified Markdown files in [`project/`](../project/) to Google Drive.

#### A. Synchronized Drive Subfolders (Under `{{DRIVE_ROOT_FOLDER_NAME}}`)

| Local Directory (`project/...`) | Google Drive Folder Link | Parent Folder |
| :--- | :--- | :--- |
| `common/` | [`{{COMMON_FOLDER_ID}}`](https://drive.google.com/drive/folders/{{COMMON_FOLDER_ID}}) | `{{DRIVE_ROOT_FOLDER_NAME}}` |
| `meetings/` | [`{{MEETINGS_FOLDER_ID}}`](https://drive.google.com/drive/folders/{{MEETINGS_FOLDER_ID}}) | `{{DRIVE_ROOT_FOLDER_NAME}}` |
| `topics/` | [`{{TOPICS_FOLDER_ID}}`](https://drive.google.com/drive/folders/{{TOPICS_FOLDER_ID}}) | `{{DRIVE_ROOT_FOLDER_NAME}}` |

#### B. Synchronized Native Google Docs (0 Documents)

| Layer / Scope | Local Markdown Source (`project/...`) | Synchronized Google Doc |
| :--- | :--- | :--- |
| **Layer 1 (`common/`)** | [`common/meetings_registry.md`](../project/common/meetings_registry.md) | [meetings_registry](https://docs.google.com/document/d/{{DOC_ID}}/edit) |

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
| **D1** | **Data Mesh, Data Products & Platform Framework** | `platform-framework` | Medallion layer boundaries (`Bronze` / `Silver` / `Gold`), Data Product classification, GCP Project Factory, declarative IaC/Terraform, naming standards |
| **D2** | **Analytics Hub, Data Sharing & Access Management** | `access-management` | Cross-project IAM vs. Analytics Hub Exchanges/Listings, decoupled compute ("consumer pays"), Dataplex ABAC, Data Clean Rooms, identity propagation |
| **D3** | **Data Security, Confidentiality & Compliance** | `security-compliance` | Tenant/domain isolation, Sensitive Data Protection (Cloud DLP), BigQuery Column-Level Security (CLS), Dynamic Data Masking, Row-Level Security (RLS) |
| **D4** | **Data Quality, Schema Evolution & Dead-Letter Queues** | `data-quality-dlq` | Dataplex Data Quality / profiling scans, schema drift handling, enforceable Data Contracts, quarantine / Dead-Letter Queue (DLQ) patterns |
| **D5** | **Metadata Automation, Knowledge Catalog & Lineage** | `catalog-lineage` | Dataplex Universal Catalog, Business Glossary ingestion, AI-generated metadata descriptions, BigLake unstructured GCS governance, Data Lineage API |
| **D6** | **Cross-Project Observability & Centralized Monitoring** | `observability-monitoring` | Centralized observability GCP project, cross-project Cloud Logging sinks, BigQuery `INFORMATION_SCHEMA` telemetry, pipeline health dashboards |
| **D7** | **AI Agents, Data Agent Kit (DAK) & FinOps Guardrails** | `ai-agents-finops` | Data Agent Kit (DAK) evaluation, slot consumption vs. LLM token billing, FinOps guardrails (`maximum_bytes_billed`, dry-runs), hybrid agentic/deterministic split |
| **P1** | **Project Organization, Workstream Alignment & Delivery Governance** | `project-organization` | Engagement roadmap & milestone prioritization, workshop cadence & review slot scheduling, cross-workstream scope alignment, schema/data handoff logistics & unblocking workarounds |

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

