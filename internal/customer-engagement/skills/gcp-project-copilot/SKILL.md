---
name: gcp-project-copilot
description: >-
  Manages end-to-end Google Cloud customer architecture engagements by scaffolding
  project workspaces, interactively customizing specs/specs_project.md and
  specs/gdrive_sync_manifest.json, analyzing multi-tab Google Meet notes and
  transcripts, maintaining a 5-layer Markdown project knowledge base
  (project/common/, project/meetings/, project/working-process/,
  project/questions-answered/, project/deliverables/), answering technical
  questions using workspace Google Cloud skills, synthesizing customer-facing
  deliverables, and synchronizing local Markdown documents into Google Drive as
  native Google Docs. Activate when setting up or bootstrapping a customer project
  workspace, customizing specs_project.md or gdrive_sync_manifest.json, analyzing
  customer meeting notes or transcripts, updating project rosters/glossaries/question
  logs/challenges, answering selected technical questions in
  project/questions-answered/, exporting the cumulative question log to a Google
  Sheets-ready CSV (project/questions-answered/question-list.csv), exploring topic
  deep-dives in project/working-process/, synthesizing customer-ready deliverables
  in project/deliverables/, creating story-driven GCP Console screenshot demos, or
  syncing project documentation with Google Drive. Do not use for ad-hoc
  single-document Google Docs edits outside a project workspace (use gdocs) or
  standalone application code implementation.
---

# GCP Project Copilot (`gcp-project-copilot`)

`gcp-project-copilot` equips the agent to operate as a **Customer Architecture Engagement Copilot** across any Google Cloud customer project. It scaffolds and configures new customer workspaces, customizes project metadata and Google Drive mappings (`specs/specs_project.md` and `specs/gdrive_sync_manifest.json`), transforms multi-tab Google Meet notes (`Quick notes`, `Full notes`, `Transcript`) into a structured 5-layer Markdown knowledge base (`project/common/`, `project/meetings/`, `project/working-process/`, `project/questions-answered/`, `project/deliverables/`), evaluates and answers technical questions using specialized Google Cloud skills available in the workspace, synthesizes standalone customer-facing deliverables from working-process sources, and synchronizes the hierarchy to Google Drive as native, cross-linked Google Docs.

---

## When to Use This Skill

- **Activate when**:
  1. **Setting up or scaffolding a customer workspace**: Creating the `specs/` and `project/{common,meetings,working-process,questions-answered,deliverables}` hierarchy and initializing `specs/specs_project.md`, `specs/gdrive_sync_manifest.json`, and the 5 living master documents via [`scripts/init_workspace.py`](./scripts/init_workspace.py).
  2. **Customizing `specs/specs_project.md` or `specs/gdrive_sync_manifest.json`**: Helping the user configure or update customer identity, Google Drive Folder URLs/IDs, Canonical Architectural Domains (`D1..Dn`), or ASR speaker aliases.
  3. **Analyzing customer meeting notes**: Extracting technical questions, architectural challenges, stakeholder rosters, and glossary terms from Google Meet notes (`https://docs.google.com/document/d/<DOC_ID>`).
  4. **Answering one or more technical questions (or a domain/session group) and/or generating 1-slide question summary prompts**: Analyzing relevant Google Cloud skills available in the workspace to evaluate selected questions (`[D#-Q##]` / `[P1-Q##]`), saving an individual structured answer per question in `project/questions-answered/` using [`resources/templates/template_answers_to_questions.md`](./resources/templates/template_answers_to_questions.md), and synchronizing `project/questions-answered/` with Google Drive upon user review.
  5. **Deep-diving into a domain topic to structure architectural thinking (`project/working-process/`)**: Creating exploratory architectural evaluations, trade-off analyses, research sources, and slide guides under `project/working-process/<topic-slug>/docs/`.
  6. **Synthesizing a final customer-facing deliverable (`project/deliverables/`)**: Transforming internal analyses from `project/working-process/` and `project/questions-answered/` into a standalone, PDF-ready customer deliverable in `project/deliverables/docs/` using [`resources/templates/template_deliverable.md`](./resources/templates/template_deliverable.md) and validating it via [`scripts/validate_deliverables.py`](./scripts/validate_deliverables.py).
  7. **Synchronizing the workspace with Google Drive**: Running [`scripts/sync_drive.py`](./scripts/sync_drive.py) from the workspace to mirror folders, import/update native Google Docs and assets, and persist all Drive IDs, URLs, and SHA-256 content hashes in `specs/gdrive_sync_manifest.json`.
  8. **Exporting the cumulative question list to CSV for Google Sheets**: Running [`scripts/export_questions_csv.py`](./scripts/export_questions_csv.py) to parse all coded questions (`[D#-Q##]` / `[P1-Q##]`) from `project/common/project_questions-log.md` into `project/questions-answered/question-list.csv` (`Updated,Code,Section,Asked By,Session Date,Question`).
  9. **Generating a story-driven GCP Console screenshot demo**: Collaborating with sibling skill [`gcp-console-demo-generator`](../gcp-console-demo-generator/SKILL.md) to build Act-by-Act visual demo guides, single-Sandbox GCP setups (`.runtime/`), and sanitized multi-persona Console screenshots under `project/working-process/<topic-slug>/demos/<demo-slug>/` (or `project/deliverables/demos/<demo-slug>/` for finalized customer demos).
- **Do NOT activate when (Anti-Scope)**:
  - Reading or editing standalone Google Docs unrelated to a structured customer project workspace (use the `gdocs` skill directly).
  - Building standalone production pipelines or application code outside of customer architectural evaluations (note: when answering technical questions in **Workflow 6** or authoring deliverables in **Workflow 7**, `gcp-project-copilot` **does** inspect and leverage specialized GCP skills available in the workspace to ground its answers and code snippets).

---

## Workspace Architecture & The 2 Project-Specific Configuration Files

Every customer engagement workspace is powered by **two project-specific configuration files** in `<workspace-root>/specs/` and a **five-layer knowledge base** in `<workspace-root>/project/`, while all generic methodology, templates, and automation scripts reside inside this skill directory (`<skill-dir>/`):

```text
<workspace-root>/
├── specs/                                        # PROJECT-SPECIFIC CONFIGURATION ONLY
│   ├── specs_project.md                          # 1. Customer identity, Drive IDs, Domain Taxonomy (D1..Dn) & ASR Alias Dictionary
│   └── gdrive_sync_manifest.json                 # 2. Machine-readable Drive folder/doc IDs & SHA-256 content hashes
│
└── project/
    ├── common/                                   # LAYER 1: Living Project Master Documents
    │   ├── meetings_registry.md                  # Chronological index of all analyzed Google Meet docs (idempotency gate)
    │   ├── project_members.md                    # Official cumulative stakeholder directory (no ASR misspellings)
    │   ├── project_glossary.md                   # Cumulative business & technical glossary across 6 canonical categories
    │   ├── project_questions-log.md              # Consolidated log of all technical questions grouped by domain (D1..Dn)
    │   └── project_challenges.md                 # Living master architectural synthesis & owner-attributed roadmap (D1..Dn)
    │
    ├── meetings/                                 # LAYER 2: Per-Meeting Session Snapshots (Organized by Date)
    │   └── YYYY-MM-DD_<meeting-slug>/
    │       ├── YYYYMMDD_questions-log_<meeting-slug>.md
    │       └── YYYYMMDD_challenges_<meeting-slug>.md
    │
    ├── working-process/                          # LAYER 3: Deep-Dive Topic Exploration, Thinking Workstreams & Demos (Created Lazily per Domain)
    │   └── <topic-slug>/                         # Matches domain slug in specs/specs_project.md
    │       ├── docs/                             # Exploratory deep-dive Markdown analyses (<doc-stem>.md)
    │       ├── diagrams/                         # Per-document architecture diagrams & JSON specs
    │       │   └── <doc-stem>/                   # Matches Markdown filename stem
    │       │       ├── *.svg                     # Official GCP Reference Architecture vector diagrams
    │       │       ├── *.png                     # Companion 2x HiDPI (144 DPI) PNGs for Slides/Docs
    │       │       └── specs/
    │       │           └── *.json                # Declarative JSON topology specs
    │       ├── sources/                          # Optional reference notes, chronologies & raw exploration inputs
    │       ├── others/                           # Optional slide prompts & auxiliary working notes
    │       └── demos/                            # Story-driven GCP Console screenshot demos (gcp-console-demo-generator)
    │           └── <demo-slug>/
    │               ├── docs/                     # Visual Demo Guide (<demo>.md) & optional Slides prompt (<demo>_slides-prompt.md)
    │               ├── screenshots/<demo-stem>/  # Sanitized 2x HiDPI GCP Console PNGs with callouts
    │               ├── diagrams/<demo-stem>/     # Companion GCP Reference Architecture SVG/PNG
    │               └── .runtime/                 # Local-only Sandbox scripts & state (ignored by sync_drive.py)
    │
    ├── questions-answered/                       # LAYER 4: Individual Technical Question Evaluations & CSV Exports
    │   ├── question-list.csv                     # Google Sheets-ready CSV export of all coded questions (export_questions_csv.py)
    │   └── <DOMAIN_ID>-Q<NN>_<question-slug>.md  # One individual structured answer file per question (template_answers_to_questions.md)
    │
    └── deliverables/                             # LAYER 5: Final Customer-Facing Deliverables (Synthesized from working-process/)
        ├── docs/                                 # Standalone, PDF-clean customer deliverables (<deliverable-stem>.md via template_deliverable.md)
        ├── diagrams/                             # Per-deliverable architecture diagrams & JSON specs
        │   └── <deliverable-stem>/               # Matches deliverable Markdown filename stem
        │       ├── *.svg                         # Official GCP Reference Architecture vector diagrams
        │       ├── *.png                         # Companion 2x HiDPI (144 DPI) PNGs
        │       └── specs/
        │           └── *.json                    # Declarative JSON topology specs
        └── demos/                                # Optional customer-finalized GCP Console screenshot demos
            └── <demo-slug>/
```

---

## Mandatory Architectural Guardrails

1. **Zero Hardcoded Identifiers**:
   Never hardcode customer names, GCP project IDs, or Google Drive Folder/Document IDs inside skill scripts or templates. Always resolve project parameters dynamically at runtime from `<workspace-root>/specs/specs_project.md` and `<workspace-root>/specs/gdrive_sync_manifest.json`.
2. **Portable Relative Paths in Repository Markdown**:
   Every internal file or directory link written inside `<workspace-root>/specs/` and `<workspace-root>/project/` (`project/common/`, `project/meetings/`, `project/working-process/`, `project/questions-answered/`) MUST use portable relative paths (e.g., `./project_members.md`, `../meetings/YYYY-MM-DD_<slug>/...`). Never write `file:///` URIs or absolute filesystem paths (`/usr/...`) inside repository `.md` files. *(Note: Final customer deliverables in `project/deliverables/docs/` forbid internal `.md` links altogether—see Guardrail 6).*
3. **Official Stakeholder Directory Separation**:
   Because `project/common/project_members.md` is a clean, customer-facing stakeholder directory, speech-to-text (ASR) phonetic aliases and transcript misspellings must reside **exclusively** in Section 5 (*Transcript Phonetic Alias & Handle Dictionary*) of `specs/specs_project.md` and must **never** appear in `project_members.md`.
4. **Domain Taxonomy Interactive Gatekeeper & Lazy `project/working-process/` Creation**:
   - **Keyword Expansion First**: If a meeting introduces a sub-topic sharing the same governance boundary or GCP service family as an existing domain `D#`, map it to `D#` and append the new keywords in `specs/specs_project.md`.
   - **Interactive Approval for `D(n+1)`**: If a meeting introduces a genuinely distinct architectural pillar ($\ge 2$ questions or a dedicated agenda segment outside `D1..Dn`), pause before writing files and use `ask_question` to confirm whether to create `D(n+1)` or merge into an existing domain.
   - **Logical Slug First**: Record new domain slugs in `specs/specs_project.md` as plain code (`` `<new-slug>` ``) without creating an empty folder. Create `project/working-process/<new-slug>/docs/` only when a deep-dive working document is actually generated.
5. **Strict Template Adherence, External-Skill-Only Section 6 & Anti-Hallucination Gate (`project/questions-answered/`)**:
   - Every question evaluation written to `<workspace-root>/project/questions-answered/` MUST strictly match [`resources/templates/template_answers_to_questions.md`](./resources/templates/template_answers_to_questions.md) (exact dual H1 header, exact 7-row metadata table with **zero** skills/status rows, exact 6 numbered `##` sections, and the 4-column Section 6 validation matrix).
   - **Never List `agyhub` Internal or IDE Meta-Skills in Section 6**: `## 6. Skills Employed` is customer-facing and MUST list **only external Google Cloud / technical domain skills** (`skills-hub/external/*`, e.g., `bigquery-optimization`, `dataform-bigquery`, `iam-helper-for-policy-management`, `retrieving-developer-knowledge`). Strictly exclude `agyhub` internal skills (`skills-hub/internal/*`: `gcp-project-copilot`, `gcp-architecture-diagram`, `gcp-console-demo-generator`, `agyhub-*`, `template-skill`) and IDE/doc utilities (`agy-customizations`, `antigravity-guide`, `gdocs`, `gdrive`).
   - **Deprecated External Skill Lifecycle Rule**: If an existing historical answer cites an external skill that was valid when authored but later deprecated (e.g., `bigquery-slot-cost-optimizer`), **preserve that historical reference** during routine edits or Drive syncs. Only remove/replace deprecated skills when the user explicitly asks to **completely regenerate** the answer—in which case the regenerated answer MUST strictly use **currently active** external skills (`--require-active-skills`).
   - **100% Skill & Official-Doc Grounding for Code Sections**: Read every cited external skill's `SKILL.md` and relevant `references/*.md` via `read_file` **before** authoring. Whenever any code block (`sql`, `sqlx`, `bash`, `yaml`, `json`, `python`, `hcl`, `lookml`), `gcloud`/`bq` CLI flag, DDL option, or IAM permission is not explicitly covered in the read workspace skills, **mandatorily** execute `retrieving-developer-knowledge` (`search_documents` / `get_documents` / `answer_query` MCP or REST API) to verify exact syntax before writing code, and map 100% of code-bearing `§2.x` subsections and `§3.1` in Section 6.
   - **Subagent Batch Rule**: Whenever delegating question batches to parallel subagents (`invoke_subagent`), the parent prompt MUST pass the absolute path to `<skill-dir>/resources/templates/template_answers_to_questions.md`, instruct every subagent to read both that template and every target external skill's `SKILL.md` via `read_file` **before** authoring any file, forbid internal skills in Section 6 or improvised headings, and require passing [`scripts/validate_question_answers.py`](./scripts/validate_question_answers.py) with `--require-active-skills` (`exit 0`) prior to completion.
6. **Clean Customer-Deliverable Gate (`project/deliverables/`)**:
   - Documents inside `<workspace-root>/project/deliverables/docs/` are final, standalone customer deliverables designed to be shared directly or exported as PDFs. Every deliverable MUST follow [`resources/templates/template_deliverable.md`](./resources/templates/template_deliverable.md) and pass [`scripts/validate_deliverables.py`](./scripts/validate_deliverables.py) (`exit 0`):
     - **Zero Internal Document Links**: Never include relative links to internal repository files (`../working-process/`, `../questions-answered/`, `../common/`, `../meetings/`, `../../specs/`) or internal Google Docs/Drive URLs (`docs.google.com`, `drive.google.com`) anywhere in the document. All hyperlinks `[label](url)` must be **public external URLs** (e.g., `https://docs.cloud.google.com/...`, `https://cloud.google.com/...`), while embedded diagrams use local relative image syntax (`![caption](../diagrams/<deliverable-stem>/<diagram>.svg)`).
     - **Zero Inline Question Codes (`[D#-Q##]` / `[P#-Q##]`) in Title, Metadata, or Sections 1–5**: Never clutter the narrative, headings, or tables with internal question tracking codes (`[D1-Q08]`, `D2-Q26`).
     - **Filename-Only Internal Traceability in Section 6.2**: List the underlying `working-process` and `questions-answered` source files exclusively in `### 6.2 Internal Working Sources (Filename Reference Only)` as plain code basenames (e.g., `` `rethink-data-mesh-architecture-with-knowledge-catalog-data-product.md` ``, `` `D2-Q26_complementary-80-20-knowledge-catalog-and-bigquery-sharing-consumer-pays.md` ``) with **zero URL links**.
7. **Mermaid Diagram Syntax Safety in Markdown Deliverables**:
   Never use semicolons (`;`) or HTML tags (`<br>`) inside Mermaid `sequenceDiagram` notes or `flowchart` labels across any repository Markdown file, as semicolons act as statement terminators in Mermaid and break rendering.
8. **Hold Google Drive Synchronization (`sync_drive.py`) Until User Review**:
   When creating or updating local Markdown files (`project/working-process/`, `project/questions-answered/`, `project/deliverables/`, `project/common/`, `project/meetings/`) or architecture diagrams, generate and verify all local files first and **do not execute `sync_drive.py`** until the user has reviewed the deliverables and explicitly requested synchronization (unless the user explicitly asks to sync immediately in their prompt).

---

## Core Workflows & Execution Checklists

> [!IMPORTANT]
> **Resolving `<skill-dir>` for Script Execution**:
> All helper scripts live inside the same directory as this `SKILL.md` file (`<skill-dir>/scripts/`). Whenever running `init_workspace.py`, `sync_drive.py`, `export_questions_csv.py`, `validate_question_answers.py`, or `validate_deliverables.py`, invoke them using the absolute path of `<skill-dir>/scripts/<script>.py` and pass `--workspace <workspace-root>`.

### Workflow 1: Setup & Scaffold a Customer Workspace (`scripts/init_workspace.py`)

Read **[`references/workspace_setup_and_customization.md`](./references/workspace_setup_and_customization.md)** for full details.

1. **Collect Customer, Drive & Taxonomy Parameters**:
   - If the user provides a kickoff Google Meet document (`https://docs.google.com/document/d/<DOC_ID>`), read its tabs via `gdocs` first to auto-extract `CUSTOMER_NAME`, `PROJECT_NAME`, `PROGRAM_NAME`, `PILOT_DOMAIN`, `UPCOMING_DOMAINS`, `EXTERNAL_PARTNERS`, initial `D1..Dn` domains, and ASR aliases.
   - Ask the user for any missing parameters (especially the **Root Project Google Drive Folder URL or ID** where `project/` will be synchronized).
   - **Select Domain Taxonomy Preset (`--taxonomy`)**: Default to `data-analytics-agents` (**3 Data + 2 Analytics + 2 Agents + `P1`**). If the engagement is strictly focused on AI Agents, Conversational Analytics, and MCP grounding, offer or pass `--taxonomy agentic-ai-platform` (run `init_workspace.py --list-taxonomies` to inspect all presets defined in [`resources/taxonomies/taxonomy_presets.json`](./resources/taxonomies/taxonomy_presets.json)).
2. **Execute [`scripts/init_workspace.py`](./scripts/init_workspace.py)**:
   ```bash
   python3 <skill-dir>/scripts/init_workspace.py \
     --workspace <workspace-root> \
     --taxonomy data-analytics-agents \
     --customer-name "<Customer Name>" \
     --customer-domain "<customer.com>" \
     --project-name "<Project Name>" \
     --program-name "<Program Name>" \
     --pilot-domain "<Pilot Domain>" \
     --upcoming-domains "<Domain A, Domain B>" \
     --external-partners "<Partner Name>" \
     --root-folder "<Google Drive Folder URL or ID>" \
     --root-folder-name "20 Project" \
     --discover-drive \
     --with-gemini-rules
   ```
   This scaffolds `specs/`, `project/common/`, `project/meetings/`, `project/working-process/`, `project/questions-answered/`, `project/deliverables/{docs,diagrams}`, renders `specs/specs_project.md` and `specs/gdrive_sync_manifest.json`, and initializes all 5 living master documents in `project/common/`.

### Workflow 2: Customize `specs/specs_project.md` & `specs/gdrive_sync_manifest.json`

When the user wants to configure or update project settings, Google Drive folder links, domains (`D1..Dn`), or ASR speaker aliases in an existing workspace:

1. **Update Identity or Google Drive Folder URLs/IDs (`--update-config`)**:
   Run `init_workspace.py --update-config` to update Section 1 and Section 2.1 of `specs/specs_project.md` **and** synchronize `root_folder_id` / `root_folder_url` in `specs/gdrive_sync_manifest.json` without overwriting `project/common/` files:
   ```bash
   python3 <skill-dir>/scripts/init_workspace.py \
     --workspace <workspace-root> \
     --update-config \
     --root-folder "<Google Drive Folder URL or ID>" \
     --meeting-notes-folder "<Notes Drive Folder URL or ID>" \
     --deliverables-folder "<Deliverables Drive Folder URL or ID>" \
     --discover-drive
   ```
2. **Customize Domains (`D1..Dn`) or ASR Aliases**:
   - Edit Section 3 (*Canonical Architectural Domain Taxonomy*) in `specs/specs_project.md` and keep `project_questions-log.md` and `project_challenges.md` domain headings aligned.
   - Edit Section 5 (*Transcript Phonetic Alias & Handle Dictionary*) in `specs/specs_project.md` to map ASR misspellings to canonical names.

### Workflow 3: Analyze a New Meeting (or Batch of Meetings)

Read **[`references/extraction_and_upsert_rules.md`](./references/extraction_and_upsert_rules.md)** before executing this checklist for each Google Meet document (`https://docs.google.com/document/d/<DOC_ID>`):

- [ ] **Step 0 — Load Project Context**:
  Read `<workspace>/specs/specs_project.md` (if the workspace is not yet scaffolded, run **Workflow 1** first), `project/common/meetings_registry.md` (check if `<DOC_ID>` was already processed), `project/common/project_members.md`, and `project/common/project_glossary.md`.
- [ ] **Step 1 — Inspect & Read All 3 Google Meet Tabs**:
  List tabs via `/google/bin/releases/gemini-agents-gdocs/gdocs readonly list-tabs <DOC_ID>` and read all three tabs via `gdocs readonly read <DOC_ID> --tab <TAB_ID>` (`Quick notes`, `Full notes`, `Transcript`).
- [ ] **Step 2 — Resolve Deep-Linked Transcript Timestamps**:
  Resolve each question's timestamp heading anchor in the `Transcript` tab:
  ```bash
  /google/bin/releases/gemini-agents-gdocs/gdocs readonly get-url <DOC_ID> --tab <TRANSCRIPT_TAB_ID> --heading "<HH:MM:SS>"
  ```
- [ ] **Step 3 — Evaluate Canonical Domain Taxonomy Fit (`D1..Dn` & `P1` Interactive Gatekeeper)**:
  Map technical architecture questions/topics to `D1..Dn` and project organization, workshop scheduling, cross-workstream alignment, or schema/data handoff questions to **`P1` (`Project Organization, Workstream Alignment & Delivery Governance`)** in `specs/specs_project.md`. If a candidate new technical domain `D(n+1)` emerges, pause and ask the user via `ask_question`.
- [ ] **Step 4 — Generate Per-Meeting Session Snapshots (`project/meetings/YYYY-MM-DD_<slug>/`)**:
  - `YYYYMMDD_questions-log_<slug>.md` (following [`resources/templates/template_questions-log.md`](./resources/templates/template_questions-log.md), splitting each domain into `## 1. Customer Technical Questions ({{CUSTOMER_NAME}})` with `[D#-Q##]` / `[P1-Q##]` codes and `## 2. Discovery & Scoping Questions (Google Cloud & External Partners)` with `[D#-S##]` / `[P1-S##]` codes, and tagging `* **Asked By:** First LASTNAME (<Role — Organization>)` without mixing respondents into `*(with ...)*`)
  - `YYYYMMDD_challenges_<slug>.md` (following [`resources/templates/template_challenges.md`](./resources/templates/template_challenges.md))
- [ ] **Step 5 — Upsert Living Master Documents (`project/common/` & `specs/specs_project.md`)**:
  Update `meetings_registry.md`, `project_members.md` (ASR aliases in `specs_project.md` only), `project_glossary.md`, `project_questions-log.md`, and `project_challenges.md`.
- [ ] **Step 6 — Pause for User Review Before Google Drive Synchronization (**Guardrail 8 / Workflow 4**)**:
  Present the generated session files and updated `project/common/` files for user review first; execute **Workflow 4** (`sync_drive.py`) only when the user explicitly requests synchronization.

### Workflow 4: Execute Google Drive Synchronization from the Workspace (`scripts/sync_drive.py`)

Whenever the user requests synchronizing `<workspace-root>/project/` with Google Drive:

1. **Pre-Flight Check (`specs_project.md` & `gdrive_sync_manifest.json`)**:
   Verify that the **Root Project Drive Folder** in Section 2.1 of `<workspace-root>/specs/specs_project.md` (or `root_folder_id` in `specs/gdrive_sync_manifest.json`) contains a valid Google Drive Folder ID (not `{{DRIVE_ROOT_FOLDER_ID}}`). If missing, ask the user for the Google Drive Folder URL/ID and run **Workflow 2** (`init_workspace.py --update-config --root-folder "<URL_OR_ID>"`).
2. **Run [`scripts/sync_drive.py`](./scripts/sync_drive.py)**:
   ```bash
   # Execute live wave-parallel synchronization (default --jobs 6 workers):
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root>

   # Tune worker concurrency explicitly (e.g., --jobs 8 for large batches, or --jobs 1 for serial):
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --jobs 8

   # Synchronize only the project/questions-answered/ or project/deliverables/ folder (repeatable --file flags):
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --file project/questions-answered
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --file project/deliverables

   # Or synchronize one or more specific Markdown documents (and any companion diagrams/<doc-stem>/ folders):
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> \
     --file project/working-process/<topic-slug>/docs/<doc-stem>.md

   # Or preview actions first without modifying Google Drive:
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --dry-run
   ```
   `sync_drive.py` automatically creates missing Drive subfolders under the Root Project Drive Folder (including `working-process/`, `questions-answered/`, `deliverables/`, `diagrams/<doc-stem>/`, `screenshots/<demo-stem>/`, and `diagrams/<doc-stem>/specs/`), ensures every `.svg` diagram has an up-to-date 2× HiDPI companion `.png`, uploads/updates standalone `.svg`, `.png`, `.json`, and `.csv` assets first (Phase 2), partitions `.md` files into topological link-dependency waves (`working-process/`, `questions-answered/` & `deliverables/` $\to$ `meetings/` $\to$ `common/`, running all updates to existing Google Docs concurrently in Wave 0 across `--jobs` workers), prefetches open-comment status in a single `gdocs readonly stream comments` batch call, rewrites internal `.md` and non-image asset links (`[foo.png](...)`, `[question-list.csv](...)`) to Google Docs/Drive URLs, imports/updates native Google Docs (preserving open comments via 3-way `gdocs mutate sync`), and atomically checkpoints all folder, document, and asset state into `specs/gdrive_sync_manifest.json`.

### Workflow 5: Deep-Dive Topic Exploration & Architectural Thinking (`project/working-process/`)

The primary objective of `project/working-process/` is to help the architect think deeply through domain challenges, compare architectural alternatives, collect technical sources (`sources/`), and iterate on designs with full traceability to `[D#-Q##]` questions and meeting notes before distilling final customer deliverables:

1. Create `<workspace>/project/working-process/<topic-slug>/docs/` matching the domain's slug in `specs/specs_project.md`, and store any architecture diagrams and JSON specs for `<doc-stem>.md` under `<workspace>/project/working-process/<topic-slug>/diagrams/<doc-stem>/` (`*.svg`, `*.png`, and `specs/*.json`).
2. Author the deep-dive architectural analysis Markdown document addressing the domain's questions from `project_questions-log.md` (`project/questions-answered/`) and challenges from `project_challenges.md`.
3. Convert the plain-text slug in Section 3 of `specs/specs_project.md` and `**Working-Process Deep-Dives:**` in `project/common/project_challenges.md` into active relative links pointing to the new working-process document.
4. **Pause for User Review Before Google Drive Sync (Guardrail 8)**: Present the local Markdown document and rendered diagrams to the user for review first; only execute **Workflow 4** (`sync_drive.py`) when the user explicitly requests synchronization.

### Workflow 6: Answer Selected Technical Questions Using Workspace GCP Skills (`project/questions-answered/`)

When the user asks to answer one or more Customer technical questions (e.g., `D3-Q14`, `D3-Q14, D3-Q15`, or a group such as all Customer `[D#-Q##]` questions in domain `D3` or from a specific meeting):

- [ ] **Step 1 — Select Target Customer Question(s) & Load Project Context**:
  - Read `<workspace>/specs/specs_project.md`, `project/common/project_questions-log.md`, and `project/common/project_challenges.md` to extract the verbatim question text, `Asked By` stakeholder attribution, session date, transcript deep-link, and customer architectural context for each selected **Customer Technical Question (`[D#-Q##]` or `[P1-Q##]`)**. *(Never generate `project/questions-answered/` files for Google Cloud or External Partner discovery/scoping `[D#-S##]` / `[P1-S##]` questions).*
  - **One Individual File Per Question by Default**: Even when multiple questions or a domain/session group are selected, generate **one individual Markdown response file per question** (do not aggregate multiple questions into a single file unless explicitly instructed by the user).
- [ ] **Step 2 — Read External Workspace Google Cloud Skills & Ground Code Gaps via Official Documentation**:
  - Inspect the **currently active external** Google Cloud / technical skills in the workspace that match the question's domain (e.g., `bigquery-sql`, `bigquery-optimization`, `bigquery-basics`, `bigquery-observability`, `iam-helper-for-policy-management`, `google-cloud-waf-security`, `gcp-spark`, `dataform-bigquery`, `dbt-bigquery`, `retrieving-developer-knowledge`, etc.). Never select `agyhub` internal skills (`gcp-project-copilot`, `gcp-architecture-diagram`, `gcp-console-demo-generator`, `agyhub-*`) or IDE meta-skills for Section 6.
  - **Read-Before-Write Gate**: Call `read_file` on `SKILL.md` and the specific `references/*.md` files of each selected external skill **before** authoring the evaluation.
  - **Zero-Guess Code Grounding (`retrieving-developer-knowledge` on Skill Gaps)**: Whenever any `gcloud`/`bq` CLI flag, SQL DDL `OPTIONS(...)` key, YAML/JSON/Terraform schema, LookML parameter, or granular IAM permission (`<service>.<resource>.<verb>`) is not verbatim in a read workspace skill, execute `retrieving-developer-knowledge` (`search_documents` / `get_documents` / `answer_query` MCP or `developerknowledge.googleapis.com/v1` REST API) to verify the exact specification against official Google Cloud documentation (`https://docs.cloud.google.com/...` / `https://cloud.google.com/...`) before writing code.
- [ ] **Step 3 — Evaluate & Save Individual Answer in `project/questions-answered/`**:
  - Ensure `<workspace>/project/questions-answered/` exists and save each question's evaluation as `<workspace>/project/questions-answered/<DOMAIN_ID>-Q<NN>_<short-kebab-slug>.md` (e.g., `project/questions-answered/D3-Q14_bigquery-row-limits-and-export-controls.md`).
  - Follow the canonical structure in [`resources/templates/template_answers_to_questions.md`](./resources/templates/template_answers_to_questions.md):
    1. **Header & Metadata Table**: Include `Customer / Project`, `Question ID` (`[D#-Q##]`), the verbatim **`Question` phrase**, `Canonical Domain`, `Asked By`, `Source Session & Log` (portable relative links), and `Date Answered` *(do not list skills in the top metadata table)*.
    2. **Section 1 — Executive Summary & Solution Matrix**: Direct architectural answer and a summary table (`| Requirement / Sub-Question | Recommended Google Cloud Solution | Architectural Layer | Implementation / Enforcement Mechanism |`) mapping each sub-requirement to its recommended Google Cloud solution, layer, and implementation/enforcement mechanism.
    3. **Section 2 — Technical Evaluation & Google Cloud Architecture**: Numbered `### 2.1`, `### 2.2`, `### 2.3`, ... subsections (including any architecture diagrams or trade-off matrices so zero unnumbered `###` headings exist in Section 2) with syntactically valid, skill/doc-verified SQL DDL, IAM JSON (strictly valid JSON without `//` comments), `gcloud`/`bq` CLI, YAML, Python, LookML, or Terraform snippets. Adapt subsection titles semantically to the question's nature—never force a single noun across all answers:
       - **`Step 1 / 2 / 3`** (or **`Stage 1 / 2 / 3`**) for chronological workflows, lifecycles, or troubleshooting runbooks (`### 2.1 Step 1 — ...`).
       - **`Control 1 / 2 / 3`** for defense-in-depth security, IAM, RLS/CLS, data-egress, or FinOps guardrails (`### 2.1 Control 1 — ...`).
       - **`Pattern A / B / C`** for distinct architectural design patterns or implementation alternatives (`### 2.1 Pattern A — ...`).
       - **Direct Descriptive Titles** (`### 2.x <Descriptive Title>`) for architecture diagrams, comparative trade-off matrices, cost worksheets, platform mechanics, or mixed evaluations.
    4. **Section 3 — IAM Permissions, Security Guardrails & Platform Caveats**: Exact IAM permission matrix (listing granular 3-part `<service>.<resource>.<verb>` permissions in Column 2 and `roles/...` predefined roles in Column 3, never swapping roles into Column 2) plus `> [!IMPORTANT]` callouts on critical platform caveats or edge cases.
    5. **Section 4 — Summary Recommendation & Next Steps for `{{CUSTOMER_NAME}}`**: Prioritized recommendation (`> [!TIP]`), owner-attributed next steps, and portable relative links to `../common/project_questions-log.md` and `../common/project_challenges.md`.
    6. **Section 5 — Google Cloud Documentation Reference Links**: Curated list of official Google Cloud documentation URLs supporting the evaluation.
    7. **Section 6 — Skills Employed (4-Column External Skill Validation Matrix)**: Structured 4-column table (`| External Skill | Validated Sections & Code Blocks | Grounding Artifacts Consulted | Technical Contribution to This Evaluation |`) mapping **only external technical skills** (never `gcp-project-copilot` or other `agyhub` internal/IDE meta-skills) to **100% of code-bearing `§2.x` subsections and `§3.1`**, citing the exact on-disk `SKILL.md` / `references/<file>.md` files read or live `retrieving-developer-knowledge` doc lookups executed. *(Note: Preserve previously valid deprecated external skills in historical answers; only replace them with currently active skills when completely regenerating an answer).*
  - **Subagent Delegation Requirement**: If delegating one or more questions to subagents (`invoke_subagent`), pass the exact `<skill-dir>/resources/templates/template_answers_to_questions.md` path in every subagent prompt, require each subagent to read both `template_answers_to_questions.md` and every cited external skill's `SKILL.md` via `read_file` before writing files, forbid listing internal skills in Section 6, and require each subagent to pass `validate_question_answers.py --require-active-skills --transcript <appDataDir>/brain/<subagent-conversation-id>` inside its own session before completing (since each Antigravity `run_command` sandbox isolates `<appDataDir>/brain/<conversation-id>` per agent).
- [ ] **Step 3b — Validate Structure, Skill Grounding & Code Anti-Hallucination Gates (`scripts/validate_question_answers.py`)**:
  - Run the validator across newly generated or regenerated file(s) with `--require-active-skills` (and `--transcript <transcript.jsonl>` when available in an Antigravity session to log-verify every `read_file` / doc lookup call) and fix all reported errors (`exit 0`) before finishing:
    ```bash
    # Validate newly authored or completely regenerated question file(s) (strictly enforces active external skills, 100% §2.x/§3.1 coverage, CLI flags & AST syntax):
    python3 <skill-dir>/scripts/validate_question_answers.py \
      --workspace <workspace-root> \
      --require-active-skills \
      --file project/questions-answered/<DOMAIN_ID>-Q<NN>_<short-kebab-slug>.md

    # Optional: include Antigravity execution transcript proof (--transcript automatically enables --require-active-skills):
    python3 <skill-dir>/scripts/validate_question_answers.py \
      --workspace <workspace-root> \
      --transcript <appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl \
      --file project/questions-answered/<DOMAIN_ID>-Q<NN>_<short-kebab-slug>.md

    # Validate all historical + current question answers in project/questions-answered/ (preserves historical deprecated external skills with [WARN]):
    python3 <skill-dir>/scripts/validate_question_answers.py --workspace <workspace-root>
    ```
- [ ] **Step 4 — Cross-Link the Answer in `project_questions-log.md` (and Session Log)**:
  - Append `* **Answer:** [<Short Title>](../questions-answered/<DOMAIN_ID>-Q<NN>_<short-kebab-slug>.md)` under the corresponding question entry in `project/common/project_questions-log.md` (and `../../questions-answered/<DOMAIN_ID>-Q<NN>_<short-kebab-slug>.md` in the per-meeting `YYYYMMDD_questions-log_<slug>.md`).
- [ ] **Step 5 — Pause for User Review Before Google Drive Sync (Guardrail 8)**:
  - Present the validated answer file(s) and updated `project_questions-log.md` to the user first; only synchronize `project/questions-answered/` with Google Drive via **Workflow 4** when requested by the user:
    ```bash
    # Sync only the project/questions-answered/ folder:
    python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --file project/questions-answered

    # Or sync the full project/ hierarchy (including updated links in common/project_questions-log.md):
    python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root>
    ```

### Workflow 7: Synthesize & Validate a Customer-Facing Deliverable (`project/deliverables/`)

When the user asks to create or promote a final deliverable to share with the customer (based on one or more `project/working-process/` deep-dives and/or `project/questions-answered/` evaluations):

- [ ] **Step 1 — Read Source Working-Process & Question Documents**:
  - Read `<workspace>/specs/specs_project.md`, the relevant working analyses under `<workspace>/project/working-process/<topic-slug>/docs/`, and any supporting question evaluations in `<workspace>/project/questions-answered/`.
- [ ] **Step 2 — Prepare Companion Diagrams in `project/deliverables/diagrams/<deliverable-stem>/`**:
  - Ensure `<workspace>/project/deliverables/docs/` and `<workspace>/project/deliverables/diagrams/<deliverable-stem>/` exist.
  - Copy or render publication-grade GCP Reference Architecture `.svg` and 2× HiDPI `.png` diagrams (plus `specs/*.json`) via [`gcp-architecture-diagram`](../gcp-architecture-diagram/SKILL.md) into `project/deliverables/diagrams/<deliverable-stem>/`.
- [ ] **Step 3 — Author Customer Deliverable in `project/deliverables/docs/<deliverable-stem>.md`**:
  - Follow [`resources/templates/template_deliverable.md`](./resources/templates/template_deliverable.md) and enforce **Guardrail 6 (Clean Customer-Deliverable Gate)**:
    1. **Dual H1 Header & 5-Row Customer Metadata Table**: `Customer / Initiative`, `Deliverable Type & Audience`, `Architectural Scope`, `Document Version`, and `Date` (zero internal links or question codes).
    2. **Sections 1–5 (Standalone Executive & Technical Blueprint)**:
       - `## 1. Executive Summary & Architectural Decisions`
       - `## 2. Customer Context, Current State & Core Challenges`
       - `## 3. Recommended Google Cloud Target Architecture` (embedding `../diagrams/<deliverable-stem>/<diagram>.svg`)
       - `## 4. Detailed Technical Design, Security & FinOps Guardrails`
       - `## 5. Implementation Roadmap & Recommended Next Steps for {{CUSTOMER_NAME}}`
       - Strip all internal `[D#-Q##]` / `[P#-Q##]` question codes and all internal `.md` links from the prose, headings, and tables so the document reads cleanly as a standalone PDF or customer Google Doc.
    3. **Section 6 — References & Source Traceability**:
       - `### 6.1 Official Google Cloud Documentation`: Public external `https://docs.cloud.google.com/...` / `https://cloud.google.com/...` links only.
       - `### 6.2 Internal Working Sources (Filename Reference Only)`: Bulleted list of the plain code filenames from `working-process/` and `questions-answered/` used to build the deliverable (e.g., `` `* \`rethink-data-mesh-architecture-with-knowledge-catalog-data-product.md\`` ``)—with **zero URLs or Markdown hyperlinks**.
- [ ] **Step 4 — Validate Clean Customer Deliverable (`scripts/validate_deliverables.py`)**:
  - Run [`scripts/validate_deliverables.py`](./scripts/validate_deliverables.py) and fix any reported internal link leaks, inline `[D#-Q##]` codes, missing diagrams, CLI flag errors, or Mermaid issues (`exit 0` required):
    ```bash
    python3 <skill-dir>/scripts/validate_deliverables.py \
      --workspace <workspace-root> \
      --file project/deliverables/docs/<deliverable-stem>.md
    ```
- [ ] **Step 5 — Cross-Link from `project_challenges.md` & Hold Drive Sync Until Review (Guardrail 8)**:
  - Add a relative link from `project/common/project_challenges.md` (`**Customer Deliverables:**`) to `../deliverables/docs/<deliverable-stem>.md`.
  - Present the local deliverable to the user for review before running `sync_drive.py`.

### Workflow 8: Export Consolidated Question List to CSV for Google Sheets (`scripts/export_questions_csv.py`)

When the user asks to generate or refresh a CSV export of project questions from `project/common/project_questions-log.md` for importing into Google Sheets:

1. **Run [`scripts/export_questions_csv.py`](./scripts/export_questions_csv.py)**:
   ```bash
   # Default: export Customer Technical Questions ([D#-Q##] / [P#-Q##]) only:
   python3 <skill-dir>/scripts/export_questions_csv.py --workspace <workspace-root>

   # Optional: also include Discovery & Scoping Questions ([D#-S##] / [P#-S##]):
   python3 <skill-dir>/scripts/export_questions_csv.py --workspace <workspace-root> --include-discovery
   ```
   - Parses every coded Customer question (`[D#-Q##]` and `[P#-Q##]`) from `<workspace-root>/project/common/project_questions-log.md` (plus `[D#-S##]` / `[P#-S##]` when `--include-discovery` is passed).
   - Writes an RFC 4180 UTF-8 CSV file to `<workspace-root>/project/questions-answered/question-list.csv` with the columns:
     - `Updated`: ISO date (`YYYY-MM-DD`) when the CSV file was generated/updated
     - `Code`: Question code without brackets or backticks (e.g., `D1-Q01`, `P1-Q08`)
     - `Section`: Full canonical domain/section heading (e.g., `D1. Data Mesh, Data Products & Platform Framework`)
     - `Asked By`: Stakeholder name and role tag with Markdown emphasis markers removed
     - `Session Date`: ISO session date (`YYYY-MM-DD`)
     - `Question`: Plain-text question with outer bolding (`**`) and inline backticks (`` ` ``) stripped for clean spreadsheet cells
     - `Answer`: Concise executive summary + structured `•` bullets resolved at **zero LLM token cost (`0` tokens)** via a 3-tier deterministic pipeline: (1) explicit `* **Summary Answer:**` bullet in `project/common/project_questions-log.md`, (2) automatic AST/regex extraction of the Section 4 `[!TIP]` summary and Section 1 Solution Matrix rows from `<workspace-root>/project/questions-answered/<CODE>_*.md`, or (3) cached `Answer` from existing `question-list.csv` (leaving unanswered questions without a dedicated file in `project/questions-answered/` blank until authored)
2. **Synchronize `project/questions-answered/question-list.csv` to Google Drive (Optional / On Request)**:
   ```bash
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --file project/questions-answered/question-list.csv
   ```

### Workflow 9: Create a Story-Driven GCP Console Demo & Screenshot Walkthrough (`gcp-console-demo-generator`)

When the user asks to design a narrative / "history" demo for a topic (`D1..Dn`), set up demo assets/permissions in a Sandbox GCP project, and capture Google Cloud Console screenshots:

1. **Read & Activate [`gcp-console-demo-generator`](../gcp-console-demo-generator/SKILL.md)**:
   Follow its 4-Phase workflow (`Grill-Me Storyboard` $\to$ `Single-Sandbox Provisioning (.runtime/)` $\to$ `Multi-Persona Chrome CDP Screenshot Capture` $\to$ `Validation & Drive Sync`).
2. **Store Output Under `project/working-process/<topic-slug>/demos/<demo-slug>/` (or `project/deliverables/demos/<demo-slug>/`)**:
   - Keep real Sandbox Project IDs, Argolis test user emails, `provision.sh`, `teardown.sh`, and `state.json` strictly inside dot-prefixed `.runtime/` (automatically ignored by `sync_drive.py`) and optional Section 6 of `specs/specs_project.md`.
   - Store customer-facing deliverables in `docs/<demo-stem>.md` (plus optional `docs/<demo-stem>_slides-prompt.md`), `screenshots/<demo-stem>/*.png`, and `diagrams/<demo-stem>/*.svg`.
3. **Cross-Link & Synchronize to Google Drive on User Approval via Workflow 4**:
   Link the new demo under its domain in `project/common/project_challenges.md`, preview link/image resolution with `--dry-run`, and synchronize when approved by the user:
   ```bash
   python3 <skill-dir>/scripts/sync_drive.py \
     --workspace <workspace-root> \
     --file project/working-process/<topic-slug>/demos/<demo-slug> \
     --file project/common/project_challenges.md \
     --dry-run
   ```

---

## References, Templates & Scripts

- **Workspace Setup, Customization & Sync Guide**: [`references/workspace_setup_and_customization.md`](./references/workspace_setup_and_customization.md)
- **Detailed Extraction & Upsert Rules**: [`references/extraction_and_upsert_rules.md`](./references/extraction_and_upsert_rules.md)
- **Prompt Examples Catalog**: [`references/prompt_catalog.md`](./references/prompt_catalog.md)
- **Executable Scripts**:
  - [`scripts/init_workspace.py`](./scripts/init_workspace.py) — Workspace scaffolding & config customization (`specs_project.md` + `gdrive_sync_manifest.json`)
  - [`scripts/sync_drive.py`](./scripts/sync_drive.py) — Dependency-ordered Google Drive & native Google Docs synchronization
  - [`scripts/export_questions_csv.py`](./scripts/export_questions_csv.py) — Export all coded questions from `project/common/project_questions-log.md` to `project/questions-answered/question-list.csv` for Google Sheets import
  - [`scripts/validate_question_answers.py`](./scripts/validate_question_answers.py) — Validate `project/questions-answered/*.md` files against `template_answers_to_questions.md`, enforcing external-only Section 6 skill attribution, 100% `§2.x`/`§3.1` skill coverage, offline `gcloud`/`bq` CLI flag schemas, JSON/YAML/Python/SQL syntax, IAM permission grammar, and optional `transcript.jsonl` execution proof
  - [`scripts/validate_deliverables.py`](./scripts/validate_deliverables.py) — Validate `project/deliverables/docs/*.md` files against `template_deliverable.md`, enforcing zero internal links, zero inline `[D#-Q##]` codes in Sections 1–5, public external links only, plain source filenames in Section 6.2, diagram existence, and code/CLI/Mermaid hygiene
- **Canonical Starter Templates & Taxonomy Presets**:
  - [`resources/taxonomies/taxonomy_presets.json`](./resources/taxonomies/taxonomy_presets.json) — Selectable canonical architectural domain taxonomy presets (`data-analytics-agents` [default], `agentic-ai-platform`)
  - [`resources/templates/template_specs_project.md`](./resources/templates/template_specs_project.md)
  - [`resources/templates/template_meetings_registry.md`](./resources/templates/template_meetings_registry.md)
  - [`resources/templates/template_members.md`](./resources/templates/template_members.md)
  - [`resources/templates/template_glossary.md`](./resources/templates/template_glossary.md)
  - [`resources/templates/template_questions-log.md`](./resources/templates/template_questions-log.md)
  - [`resources/templates/template_challenges.md`](./resources/templates/template_challenges.md)
  - [`resources/templates/template_answers_to_questions.md`](./resources/templates/template_answers_to_questions.md)
  - [`resources/templates/template_deliverable.md`](./resources/templates/template_deliverable.md)
