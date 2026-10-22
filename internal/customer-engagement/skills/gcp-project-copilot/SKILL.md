---
name: gcp-project-copilot
description: >-
  Manages end-to-end Google Cloud customer architecture engagements by scaffolding
  project workspaces, interactively customizing specs/specs_project.md and
  specs/gdrive_sync_manifest.json, analyzing multi-tab Google Meet notes and
  transcripts, maintaining a 4-layer Markdown project knowledge base
  (project/common/, project/meetings/, project/topics/, project/questions/),
  answering technical questions using workspace Google Cloud skills, and
  synchronizing local Markdown deliverables into Google Drive as native Google Docs.
  Activate when setting up or bootstrapping a customer project workspace,
  customizing specs_project.md or gdrive_sync_manifest.json, analyzing customer
  meeting notes or transcripts, updating project rosters/glossaries/question
  logs/challenges, answering selected technical questions in project/questions/,
  exporting the cumulative question log to a Google Sheets-ready CSV
  (project/questions/question-list.csv), creating topic deep-dives or story-driven
  GCP Console screenshot demos, or syncing project documentation with Google Drive.
  Do not use for ad-hoc single-document Google Docs edits outside a project
  workspace (use gdocs) or standalone application code implementation.
---

# GCP Project Copilot (`gcp-project-copilot`)

`gcp-project-copilot` equips the agent to operate as a **Customer Architecture Engagement Copilot** across any Google Cloud customer project. It scaffolds and configures new customer workspaces, customizes project metadata and Google Drive mappings (`specs/specs_project.md` and `specs/gdrive_sync_manifest.json`), transforms multi-tab Google Meet notes (`Quick notes`, `Full notes`, `Transcript`) into a structured Markdown knowledge base (`project/common/`, `project/meetings/`, `project/topics/`, `project/questions/`), evaluates and answers technical questions using specialized Google Cloud skills available in the workspace, and synchronizes the hierarchy to Google Drive as native, cross-linked Google Docs.

---

## When to Use This Skill

- **Activate when**:
  1. **Setting up or scaffolding a customer workspace**: Creating the `specs/` and `project/{common,meetings,topics,questions}` hierarchy and initializing `specs/specs_project.md`, `specs/gdrive_sync_manifest.json`, and the 5 living master documents via [`scripts/init_workspace.py`](./scripts/init_workspace.py).
  2. **Customizing `specs/specs_project.md` or `specs/gdrive_sync_manifest.json`**: Helping the user configure or update customer identity, Google Drive Folder URLs/IDs, Canonical Architectural Domains (`D1..Dn`), or ASR speaker aliases.
  3. **Analyzing customer meeting notes**: Extracting technical questions, architectural challenges, stakeholder rosters, and glossary terms from Google Meet notes (`https://docs.google.com/document/d/<DOC_ID>`).
  4. **Answering one or more technical questions (or a domain/session group) and/or generating 1-slide question summary prompts**: Analyzing relevant Google Cloud skills available in the workspace to evaluate selected questions (`[D#-Q##]` / `[P1-Q##]`), saving an individual structured answer per question in `project/questions/` using [`resources/templates/template_answers_to_questions.md`](./resources/templates/template_answers_to_questions.md), and synchronizing `project/questions/` with Google Drive.
  5. **Promoting a domain challenge into a deep-dive workstream**: Creating architectural evaluations and slide guides under `project/topics/<topic-slug>/docs/`.
  6. **Synchronizing the workspace with Google Drive**: Running [`scripts/sync_drive.py`](./scripts/sync_drive.py) from the workspace to mirror folders, import/update native Google Docs, and refresh Section 2.2 of `specs/specs_project.md`.
  7. **Exporting the cumulative question list to CSV for Google Sheets**: Running [`scripts/export_questions_csv.py`](./scripts/export_questions_csv.py) to parse all coded questions (`[D#-Q##]` / `[P1-Q##]`) from `project/common/project_questions-log.md` into `project/questions/question-list.csv` (`Updated,Code,Section,Asked By,Session Date,Question`).
  8. **Generating a story-driven GCP Console screenshot demo**: Collaborating with sibling skill [`gcp-console-demo-generator`](../gcp-console-demo-generator/SKILL.md) to build Act-by-Act visual demo guides, single-Sandbox GCP setups (`.runtime/`), and sanitized multi-persona Console screenshots under `project/topics/<topic-slug>/demos/<demo-slug>/`.
- **Do NOT activate when (Anti-Scope)**:
  - Reading or editing standalone Google Docs unrelated to a structured customer project workspace (use the `gdocs` skill directly).
  - Building standalone production pipelines or application code outside of customer architectural evaluations (note: when answering technical questions in **Workflow 6**, `gcp-project-copilot` **does** inspect and leverage specialized GCP skills available in the workspace to ground its answers and code snippets).

---

## Workspace Architecture & The 2 Project-Specific Configuration Files

Every customer engagement workspace is powered by **two project-specific configuration files** in `<workspace-root>/specs/` and a **four-layer knowledge base** in `<workspace-root>/project/`, while all generic methodology, templates, and automation scripts reside inside this skill directory (`<skill-dir>/`):

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
    ├── topics/                                   # LAYER 3: Deep-Dive Topic Workstreams & Demos (Created Lazily per Domain)
    │   └── <topic-slug>/                         # Matches domain slug in specs/specs_project.md
    │       ├── docs/                             # Deep-dive Markdown deliverables (<doc-stem>.md)
    │       ├── diagrams/                         # Per-document architecture diagrams & JSON specs
    │       │   └── <doc-stem>/                   # Matches Markdown filename stem
    │       │       ├── *.svg                     # Official GCP Reference Architecture vector diagrams
    │       │       ├── *.png                     # Companion 2x HiDPI (144 DPI) PNGs for Slides/Docs
    │       │       └── specs/
    │       │           └── *.json                # Declarative JSON topology specs
    │       └── demos/                            # Story-driven GCP Console screenshot demos (gcp-console-demo-generator)
    │           └── <demo-slug>/
    │               ├── docs/                     # Visual Demo Guide (<demo>.md) & optional Slides prompt (<demo>_slides-prompt.md)
    │               ├── screenshots/<demo-stem>/  # Sanitized 2x HiDPI GCP Console PNGs with callouts
    │               ├── diagrams/<demo-stem>/     # Companion GCP Reference Architecture SVG/PNG
    │               └── .runtime/                 # Local-only Sandbox scripts & state (ignored by sync_drive.py)
    │
    └── questions/                                # LAYER 4: Individual Technical Question Evaluations & CSV Exports
        ├── question-list.csv                     # Google Sheets-ready CSV export of all coded questions (export_questions_csv.py)
        └── <DOMAIN_ID>-Q<NN>_<question-slug>.md  # One individual structured answer file per question (template_answers_to_questions.md)

```

---

## Mandatory Architectural Guardrails

1. **Zero Hardcoded Identifiers**:
   Never hardcode customer names, GCP project IDs, or Google Drive Folder/Document IDs inside skill scripts or templates. Always resolve project parameters dynamically at runtime from `<workspace-root>/specs/specs_project.md` and `<workspace-root>/specs/gdrive_sync_manifest.json`.
2. **Portable Relative Paths in Repository Markdown**:
   Every internal file or directory link written inside `<workspace-root>/specs/` and `<workspace-root>/project/` MUST use portable relative paths (e.g., `./project_members.md`, `../meetings/YYYY-MM-DD_<slug>/...`). Never write `file:///` URIs or absolute filesystem paths (`/usr/...`) inside repository `.md` files.
3. **Official Stakeholder Directory Separation**:
   Because `project/common/project_members.md` is a clean, customer-facing stakeholder directory, speech-to-text (ASR) phonetic aliases and transcript misspellings must reside **exclusively** in Section 5 (*Transcript Phonetic Alias & Handle Dictionary*) of `specs/specs_project.md` and must **never** appear in `project_members.md`.
4. **Domain Taxonomy Interactive Gatekeeper & Lazy `project/topics/` Creation**:
   - **Keyword Expansion First**: If a meeting introduces a sub-topic sharing the same governance boundary or GCP service family as an existing domain `D#`, map it to `D#` and append the new keywords in `specs/specs_project.md`.
   - **Interactive Approval for `D(n+1)`**: If a meeting introduces a genuinely distinct architectural pillar ($\ge 2$ questions or a dedicated agenda segment outside `D1..Dn`), pause before writing files and use `ask_question` to confirm whether to create `D(n+1)` or merge into an existing domain.
   - **Logical Slug First**: Record new domain slugs in `specs/specs_project.md` as plain code (`` `<new-slug>` ``) without creating an empty folder. Create `project/topics/<new-slug>/docs/` only when a deep-dive deliverable is actually generated.
5. **Strict Template Adherence & Subagent Delegation Gate (`project/questions/`)**:
   - Every question evaluation written to `<workspace-root>/project/questions/` MUST strictly match [`resources/templates/template_answers_to_questions.md`](./resources/templates/template_answers_to_questions.md) (exact dual H1 header, exact 7-row metadata table with **zero** skills/status rows, and exact 6 numbered `##` sections).
   - **Subagent Batch Rule**: Whenever delegating question batches to parallel subagents (`invoke_subagent`), the parent prompt MUST pass the absolute path to `<skill-dir>/resources/templates/template_answers_to_questions.md`, instruct every subagent to read that template verbatim via `read_file` **before** authoring any file, forbid improvising custom headings (`Original Question`, `TL;DR`, bulleted metadata, etc.), and require passing [`scripts/validate_question_answers.py`](./scripts/validate_question_answers.py) (`exit 0`) prior to completion.

---

## Core Workflows & Execution Checklists

> [!IMPORTANT]
> **Resolving `<skill-dir>` for Script Execution**:
> All helper scripts live inside the same directory as this `SKILL.md` file (`<skill-dir>/scripts/`). Whenever running `init_workspace.py` or `sync_drive.py`, invoke them using the absolute path of `<skill-dir>/scripts/<script>.py` and pass `--workspace <workspace-root>`.

### Workflow 1: Setup & Scaffold a Customer Workspace (`scripts/init_workspace.py`)

Read **[`references/workspace_setup_and_customization.md`](./references/workspace_setup_and_customization.md)** for full details.

1. **Collect Customer & Drive Parameters**:
   - If the user provides a kickoff Google Meet document (`https://docs.google.com/document/d/<DOC_ID>`), read its tabs via `gdocs` first to auto-extract `CUSTOMER_NAME`, `PROJECT_NAME`, `PROGRAM_NAME`, `PILOT_DOMAIN`, `UPCOMING_DOMAINS`, `EXTERNAL_PARTNERS`, initial `D1..Dn` domains, and ASR aliases.
   - Ask the user for any missing parameters (especially the **Root Project Google Drive Folder URL or ID** where `project/` will be synchronized).
2. **Execute [`scripts/init_workspace.py`](./scripts/init_workspace.py)**:
   ```bash
   python3 <skill-dir>/scripts/init_workspace.py \
     --workspace <workspace-root> \
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
   This scaffolds `specs/`, `project/common/`, `project/meetings/`, `project/topics/`, renders `specs/specs_project.md` and `specs/gdrive_sync_manifest.json`, and initializes all 5 living master documents in `project/common/`.

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
  - `YYYYMMDD_questions-log_<slug>.md` (following [`resources/templates/template_questions-log.md`](./resources/templates/template_questions-log.md), prefixing every question with its permanent domain-scoped code `[D#-Q##]` or `[P1-Q##]`)
  - `YYYYMMDD_challenges_<slug>.md` (following [`resources/templates/template_challenges.md`](./resources/templates/template_challenges.md))
- [ ] **Step 5 — Upsert Living Master Documents (`project/common/` & `specs/specs_project.md`)**:
  Update `meetings_registry.md`, `project_members.md` (ASR aliases in `specs_project.md` only), `project_glossary.md`, `project_questions-log.md`, and `project_challenges.md`.
- [ ] **Step 6 — Execute Google Drive Synchronization (**Workflow 4**)**.

### Workflow 4: Execute Google Drive Synchronization from the Workspace (`scripts/sync_drive.py`)

Whenever synchronizing `<workspace-root>/project/` with Google Drive:

1. **Pre-Flight Check (`specs_project.md` & `gdrive_sync_manifest.json`)**:
   Verify that the **Root Project Drive Folder** in Section 2.1 of `<workspace-root>/specs/specs_project.md` (or `root_folder_id` in `specs/gdrive_sync_manifest.json`) contains a valid Google Drive Folder ID (not `{{DRIVE_ROOT_FOLDER_ID}}`). If missing, ask the user for the Google Drive Folder URL/ID and run **Workflow 2** (`init_workspace.py --update-config --root-folder "<URL_OR_ID>"`).
2. **Run [`scripts/sync_drive.py`](./scripts/sync_drive.py)**:
   ```bash
   # Execute live wave-parallel synchronization (default --jobs 6 workers):
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root>

   # Tune worker concurrency explicitly (e.g., --jobs 8 for large batches, or --jobs 1 for serial):
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --jobs 8

   # Synchronize only the project/questions/ folder (or pass repeatable --file flags for specific files):
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --file project/questions

   # Or synchronize one or more specific Markdown documents (and any companion diagrams/<doc-stem>/ folders):
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> \
     --file project/topics/<topic-slug>/docs/<doc-stem>.md

   # Or preview actions first without modifying Google Drive:
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --dry-run
   ```
   `sync_drive.py` automatically creates missing Drive subfolders under the Root Project Drive Folder (including `questions/`, `diagrams/<doc-stem>/`, `screenshots/<demo-stem>/`, and `diagrams/<doc-stem>/specs/`), ensures every `.svg` diagram has an up-to-date 2× HiDPI companion `.png`, uploads/updates standalone `.svg`, `.png`, `.json`, and `.csv` assets first (Phase 2), partitions `.md` files into topological link-dependency waves (`topics/` & leaf `questions/` $\to$ `meetings/` $\to$ `common/`, running all updates to existing Google Docs concurrently in Wave 0 across `--jobs` workers), prefetches open-comment status in a single `gdocs readonly stream comments` batch call, rewrites internal `.md` and non-image asset links (`[foo.png](...)`, `[question-list.csv](...)`) to Google Docs/Drive URLs, imports/updates native Google Docs (preserving open comments via 3-way `gdocs mutate sync`), atomically checkpoints `specs/gdrive_sync_manifest.json`, and refreshes Section 2.2 in `specs/specs_project.md`.

### Workflow 5: Promote a Domain Challenge into a Deep-Dive Topic Workstream (`project/topics/`)

1. Create `<workspace>/project/topics/<topic-slug>/docs/` matching the domain's slug in `specs/specs_project.md`, and store any architecture diagrams and JSON specs for `<doc-stem>.md` under `<workspace>/project/topics/<topic-slug>/diagrams/<doc-stem>/` (`*.svg`, `*.png`, and `specs/*.json`).
2. Author the deep-dive architectural analysis Markdown document addressing the domain's questions from `project_questions-log.md` and challenges from `project_challenges.md`.
3. Convert the plain-text slug in Section 3 of `specs/specs_project.md` and `**Deep-Dive Deliverables:**` in `project/common/project_challenges.md` into active relative links pointing to the new deliverable, then execute **Workflow 4** (`sync_drive.py`).

### Workflow 6: Answer Selected Technical Questions Using Workspace GCP Skills (`project/questions/`)

When the user asks to answer one or more technical questions (e.g., `D3-Q14`, `D3-Q14, D3-Q15`, or a group such as all questions in domain `D3` or from a specific meeting):

- [ ] **Step 1 — Select Target Question(s) & Load Project Context**:
  - Read `<workspace>/specs/specs_project.md`, `project/common/project_questions-log.md`, and `project/common/project_challenges.md` to extract the verbatim question text, `Asked By` stakeholder attribution, session date, transcript deep-link, and customer architectural context for each selected question (`[D#-Q##]` or `[P1-Q##]`).
  - **One Individual File Per Question by Default**: Even when multiple questions or a domain/session group are selected, generate **one individual Markdown response file per question** (do not aggregate multiple questions into a single file unless explicitly instructed by the user).
- [ ] **Step 2 — Analyze Available Workspace Google Cloud Skills & Official Documentation**:
  - Inspect the skills available in the workspace that match the question's technical domain (e.g., `bigquery-sql`, `bigquery-optimization`, `bigquery-basics`, `bigquery-slot-cost-optimizer`, `bigquery-observability`, `iam-helper-for-policy-management`, `google-cloud-waf-security`, `gcp-spark`, `dataform-bigquery`, `dbt-bigquery`, `retrieving-developer-knowledge`, etc.).
  - Read the `SKILL.md` and relevant `references/*.md` files of those matching workspace skills, and verify exact IAM permissions, quotas, DDL syntax, or platform limits against official Google Cloud documentation (`https://docs.cloud.google.com/...`).
- [ ] **Step 3 — Evaluate & Save Individual Answer in `project/questions/`**:
  - Ensure `<workspace>/project/questions/` exists and save each question's evaluation as `<workspace>/project/questions/<DOMAIN_ID>-Q<NN>_<short-kebab-slug>.md` (e.g., `project/questions/D3-Q14_bigquery-row-limits-and-export-controls.md`).
  - Follow the canonical structure in [`resources/templates/template_answers_to_questions.md`](./resources/templates/template_answers_to_questions.md):
    1. **Header & Metadata Table**: Include `Customer / Project`, `Question ID` (`[D#-Q##]`), the verbatim **`Question` phrase**, `Canonical Domain`, `Asked By`, `Source Session & Log` (portable relative links), and `Date Answered` *(do not list skills in the top metadata table)*.
    2. **Section 1 — Executive Summary & Solution Matrix**: Direct architectural answer and a summary table (`| Requirement / Sub-Question | Recommended Google Cloud Solution | Architectural Layer | Implementation / Enforcement Mechanism |`) mapping each sub-requirement to its recommended Google Cloud solution, layer, and implementation/enforcement mechanism.
    3. **Section 2 — Technical Evaluation & Google Cloud Architecture**: Numbered `### 2.1`, `### 2.2`, `### 2.3`, ... subsections (including any architecture diagrams or trade-off matrices so zero unnumbered `###` headings exist in Section 2) with production-ready SQL DDL, IAM JSON, CLI, or Terraform snippets. Adapt subsection titles semantically to the question's nature—never force a single noun across all answers:
       - **`Step 1 / 2 / 3`** (or **`Stage 1 / 2 / 3`**) for chronological workflows, lifecycles, or troubleshooting runbooks (`### 2.1 Step 1 — ...`).
       - **`Control 1 / 2 / 3`** for defense-in-depth security, IAM, RLS/CLS, data-egress, or FinOps guardrails (`### 2.1 Control 1 — ...`).
       - **`Pattern A / B / C`** for distinct architectural design patterns or implementation alternatives (`### 2.1 Pattern A — ...`).
       - **Direct Descriptive Titles** (`### 2.x <Descriptive Title>`) for architecture diagrams, comparative trade-off matrices, cost worksheets, platform mechanics, or mixed evaluations.
    4. **Section 3 — IAM Permissions, Security Guardrails & Platform Caveats**: Exact IAM permission matrix (including predefined roles to avoid and how to restrict via Custom Roles or IAM v2 Deny Policies) plus `> [!IMPORTANT]` callouts on critical platform caveats or edge cases.
    5. **Section 4 — Summary Recommendation & Next Steps for `{{CUSTOMER_NAME}}`**: Prioritized recommendation (`> [!TIP]`), owner-attributed next steps, and portable relative links to `../common/project_questions-log.md` and `../common/project_challenges.md`.
    6. **Section 5 — Google Cloud Documentation Reference Links**: Curated list of official Google Cloud documentation URLs supporting the evaluation.
    7. **Section 6 — Skills Employed**: Structured table listing each workspace skill employed in the analysis (`| Workspace Skill | Technical Contribution to This Evaluation |`) and its specific technical contribution to the evaluation.
  - **Subagent Delegation Requirement**: If delegating one or more questions to subagents (`invoke_subagent`), pass the exact `<skill-dir>/resources/templates/template_answers_to_questions.md` path in every subagent prompt and require each subagent to read it via `read_file` before writing files. Never let a subagent invent custom `H1`/`H2` headings or put `Grounded Workspace Skills` in the top metadata table.
- [ ] **Step 3b — Validate Question Answer Structure (`scripts/validate_question_answers.py`)**:
  - Run the structural validator across the newly generated or updated file(s) and fix any reported deviations before finishing:
    ```bash
    # Validate all question answers in project/questions/:
    python3 <skill-dir>/scripts/validate_question_answers.py --workspace <workspace-root>

    # Or validate specific question file(s):
    python3 <skill-dir>/scripts/validate_question_answers.py --workspace <workspace-root> --file project/questions/<DOMAIN_ID>-Q<NN>_<short-kebab-slug>.md
    ```
- [ ] **Step 4 — Cross-Link the Answer in `project_questions-log.md` (and Session Log)**:
  - Append `* **Answer:** [<Short Title>](../questions/<DOMAIN_ID>-Q<NN>_<short-kebab-slug>.md)` under the corresponding question entry in `project/common/project_questions-log.md` (and `../../questions/<DOMAIN_ID>-Q<NN>_<short-kebab-slug>.md` in the per-meeting `YYYYMMDD_questions-log_<slug>.md`).
- [ ] **Step 5 — Synchronize `project/questions/` with Google Drive (If Required by the User)**:
  - If requested by the user (or after confirming with the user), synchronize the answer(s) in `project/questions/` and the updated `project_questions-log.md` to Google Drive via **Workflow 4**:
    ```bash
    # Sync only the project/questions/ folder:
    python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --file project/questions

    # Or sync the full project/ hierarchy (including updated links in common/project_questions-log.md):
    python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root>
    ```

### Workflow 7: Export Consolidated Question List to CSV for Google Sheets (`scripts/export_questions_csv.py`)

When the user asks to generate or refresh a CSV export of all project questions from `project/common/project_questions-log.md` for importing into Google Sheets:

1. **Run [`scripts/export_questions_csv.py`](./scripts/export_questions_csv.py)**:
   ```bash
   python3 <skill-dir>/scripts/export_questions_csv.py --workspace <workspace-root>
   ```
   - Parses every coded question (`[D#-Q##]` and `[P#-Q##]`) from `<workspace-root>/project/common/project_questions-log.md`.
   - Writes an RFC 4180 UTF-8 CSV file to `<workspace-root>/project/questions/question-list.csv` with the columns:
     - `Updated`: ISO date (`YYYY-MM-DD`) when the CSV file was generated/updated
     - `Code`: Question code without brackets or backticks (e.g., `D1-Q01`, `P1-Q08`)
     - `Section`: Full canonical domain/section heading (e.g., `D1. Data Mesh, Data Products & Platform Framework`)
     - `Asked By`: Stakeholder name with Markdown emphasis markers removed
     - `Session Date`: ISO session date (`YYYY-MM-DD`)
     - `Question`: Plain-text question with outer bolding (`**`) and inline backticks (`` ` ``) stripped for clean spreadsheet cells
2. **Synchronize `project/questions/question-list.csv` to Google Drive (Optional / On Request)**:
   ```bash
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --file project/questions/question-list.csv
   ```

### Workflow 8: Create a Story-Driven GCP Console Demo & Screenshot Walkthrough (`gcp-console-demo-generator`)

When the user asks to design a narrative / "history" demo for a topic (`D1..Dn`), set up demo assets/permissions in a Sandbox GCP project, and capture Google Cloud Console screenshots:

1. **Read & Activate [`gcp-console-demo-generator`](../gcp-console-demo-generator/SKILL.md)**:
   Follow its 4-Phase workflow (`Grill-Me Storyboard` $\to$ `Single-Sandbox Provisioning (.runtime/)` $\to$ `Multi-Persona Chrome CDP Screenshot Capture` $\to$ `Validation & Drive Sync`).
2. **Store Output Under `project/topics/<topic-slug>/demos/<demo-slug>/`**:
   - Keep real Sandbox Project IDs, Argolis test user emails, `provision.sh`, `teardown.sh`, and `state.json` strictly inside dot-prefixed `.runtime/` (automatically ignored by `sync_drive.py`) and optional Section 6 of `specs/specs_project.md`.
   - Store customer-facing deliverables in `docs/<demo-stem>.md` (plus optional `docs/<demo-stem>_slides-prompt.md`), `screenshots/<demo-stem>/*.png`, and `diagrams/<demo-stem>/*.svg`.
3. **Cross-Link & Synchronize to Google Drive via Workflow 4**:
   Link the new demo under its domain in `project/common/project_challenges.md`, preview link/image resolution with `--dry-run`, and synchronize both the demo bundle and `project_challenges.md`:
   ```bash
   python3 <skill-dir>/scripts/sync_drive.py \
     --workspace <workspace-root> \
     --file project/topics/<topic-slug>/demos/<demo-slug> \
     --file project/common/project_challenges.md \
     --dry-run

   python3 <skill-dir>/scripts/sync_drive.py \
     --workspace <workspace-root> \
     --file project/topics/<topic-slug>/demos/<demo-slug> \
     --file project/common/project_challenges.md
   ```
   `sync_drive.py` automatically skips `.runtime/`, uploads all screenshot and diagram assets first (so companion `_slides-prompt.md` asset links resolve on the first pass), and stages local `../screenshots/*.png` and `../diagrams/*.svg` images into native Google Docs.

---

## References, Templates & Scripts

- **Workspace Setup, Customization & Sync Guide**: [`references/workspace_setup_and_customization.md`](./references/workspace_setup_and_customization.md)
- **Detailed Extraction & Upsert Rules**: [`references/extraction_and_upsert_rules.md`](./references/extraction_and_upsert_rules.md)
- **Prompt Examples Catalog**: [`references/prompt_catalog.md`](./references/prompt_catalog.md)
- **Executable Scripts**:
  - [`scripts/init_workspace.py`](./scripts/init_workspace.py) — Workspace scaffolding & config customization (`specs_project.md` + `gdrive_sync_manifest.json`)
  - [`scripts/sync_drive.py`](./scripts/sync_drive.py) — Dependency-ordered Google Drive & native Google Docs synchronization
  - [`scripts/export_questions_csv.py`](./scripts/export_questions_csv.py) — Export all coded questions from `project/common/project_questions-log.md` to `project/questions/question-list.csv` for Google Sheets import
  - [`scripts/validate_question_answers.py`](./scripts/validate_question_answers.py) — Validate `project/questions/*.md` files against `template_answers_to_questions.md` and Mermaid/path hygiene guardrails
- **Canonical Starter Templates**:
  - [`resources/templates/template_specs_project.md`](./resources/templates/template_specs_project.md)
  - [`resources/templates/template_meetings_registry.md`](./resources/templates/template_meetings_registry.md)
  - [`resources/templates/template_members.md`](./resources/templates/template_members.md)
  - [`resources/templates/template_glossary.md`](./resources/templates/template_glossary.md)
  - [`resources/templates/template_questions-log.md`](./resources/templates/template_questions-log.md)
  - [`resources/templates/template_challenges.md`](./resources/templates/template_challenges.md)
  - [`resources/templates/template_answers_to_questions.md`](./resources/templates/template_answers_to_questions.md)
