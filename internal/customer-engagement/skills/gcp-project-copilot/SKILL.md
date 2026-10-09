---
name: gcp-project-copilot
description: >-
  Manages end-to-end Google Cloud customer architecture engagements by scaffolding
  project workspaces, interactively customizing specs/specs_project.md and
  specs/gdrive_sync_manifest.json, analyzing multi-tab Google Meet notes and
  transcripts, maintaining a 3-layer Markdown project knowledge base
  (project/common/, project/meetings/, project/topics/), and synchronizing local
  Markdown deliverables into Google Drive as native Google Docs. Activate when
  setting up or bootstrapping a customer project workspace, customizing
  specs_project.md or gdrive_sync_manifest.json, analyzing customer meeting notes
  or transcripts, updating project rosters/glossaries/question logs/challenges,
  creating topic deep-dives, or syncing project documentation with Google Drive.
  Do not use for ad-hoc single-document Google Docs edits outside a project
  workspace (use gdocs) or single-service code implementation.
---

# GCP Project Copilot (`gcp-project-copilot`)

`gcp-project-copilot` equips the agent to operate as a **Customer Architecture Engagement Copilot** across any Google Cloud customer project. It scaffolds and configures new customer workspaces, customizes project metadata and Google Drive mappings (`specs/specs_project.md` and `specs/gdrive_sync_manifest.json`), transforms multi-tab Google Meet notes (`Quick notes`, `Full notes`, `Transcript`) into a three-layer Markdown knowledge base (`project/common/`, `project/meetings/`, `project/topics/`), and synchronizes the entire hierarchy to Google Drive as native, cross-linked Google Docs.

---

## When to Use This Skill

- **Activate when**:
  1. **Setting up or scaffolding a customer workspace**: Creating the `specs/` and `project/{common,meetings,topics}` hierarchy and initializing `specs/specs_project.md`, `specs/gdrive_sync_manifest.json`, and the 5 living master documents via [`scripts/init_workspace.py`](./scripts/init_workspace.py).
  2. **Customizing `specs/specs_project.md` or `specs/gdrive_sync_manifest.json`**: Helping the user configure or update customer identity, Google Drive Folder URLs/IDs, Canonical Architectural Domains (`D1..Dn`), or ASR speaker aliases.
  3. **Analyzing customer meeting notes**: Extracting technical questions, architectural challenges, stakeholder rosters, and glossary terms from Google Meet notes (`https://docs.google.com/document/d/<DOC_ID>`).
  4. **Promoting a domain challenge into a deep-dive workstream**: Creating architectural evaluations and slide guides under `project/topics/<topic-slug>/docs/`.
  5. **Synchronizing the workspace with Google Drive**: Running [`scripts/sync_drive.py`](./scripts/sync_drive.py) from the workspace to mirror folders, import/update native Google Docs, and refresh Section 2.2 of `specs/specs_project.md`.
- **Do NOT activate when (Anti-Scope)**:
  - Reading or editing standalone Google Docs unrelated to a structured customer project workspace (use the `gdocs` skill directly).
  - Authoring product-specific code or pipelines such as Dataform SQLX (`dataform-bigquery`), dbt (`dbt-bigquery`), Spark (`gcp-spark`), or IAM policies (`iam-helper-for-policy-management`).

---

## Workspace Architecture & The 2 Project-Specific Configuration Files

Every customer engagement workspace is powered by **two project-specific configuration files** in `<workspace-root>/specs/` and a **three-layer knowledge base** in `<workspace-root>/project/`, while all generic methodology, templates, and automation scripts reside inside this skill directory (`<skill-dir>/`):

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
    └── topics/                                   # LAYER 3: Deep-Dive Topic Workstreams (Created Lazily per Domain)
        └── <topic-slug>/                         # Matches domain slug in specs/specs_project.md
            └── docs/
                ├── sources/
                └── output/
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
   # Execute live synchronization from the workspace to Google Drive
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root>

   # Or preview actions first without modifying Google Drive:
   python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --dry-run
   ```
   `sync_drive.py` automatically creates missing Drive subfolders under the Root Project Drive Folder, topologically sorts all `.md` files (`topics/` $\to$ `meetings/` $\to$ `common/`), rewrites internal `.md` links to Google Docs URLs, imports/updates native Google Docs (preserving open comments via 3-way `gdocs mutate sync`), saves `specs/gdrive_sync_manifest.json`, and refreshes Section 2.2 in `specs/specs_project.md`.

### Workflow 5: Promote a Domain Challenge into a Deep-Dive Topic Workstream (`project/topics/`)

1. Create `<workspace>/project/topics/<topic-slug>/docs/` matching the domain's slug in `specs/specs_project.md`.
2. Author the deep-dive architectural analysis Markdown document addressing the domain's questions from `project_questions-log.md` and challenges from `project_challenges.md`.
3. Convert the plain-text slug in Section 3 of `specs/specs_project.md` and `**Deep-Dive Deliverables:**` in `project/common/project_challenges.md` into active relative links pointing to the new deliverable, then execute **Workflow 4** (`sync_drive.py`).

---

## References, Templates & Scripts

- **Workspace Setup, Customization & Sync Guide**: [`references/workspace_setup_and_customization.md`](./references/workspace_setup_and_customization.md)
- **Detailed Extraction & Upsert Rules**: [`references/extraction_and_upsert_rules.md`](./references/extraction_and_upsert_rules.md)
- **Prompt Examples Catalog**: [`references/prompt_catalog.md`](./references/prompt_catalog.md)
- **Executable Scripts**:
  - [`scripts/init_workspace.py`](./scripts/init_workspace.py) — Workspace scaffolding & config customization (`specs_project.md` + `gdrive_sync_manifest.json`)
  - [`scripts/sync_drive.py`](./scripts/sync_drive.py) — Dependency-ordered Google Drive & native Google Docs synchronization
- **Canonical Starter Templates**:
  - [`resources/templates/template_specs_project.md`](./resources/templates/template_specs_project.md)
  - [`resources/templates/template_meetings_registry.md`](./resources/templates/template_meetings_registry.md)
  - [`resources/templates/template_members.md`](./resources/templates/template_members.md)
  - [`resources/templates/template_glossary.md`](./resources/templates/template_glossary.md)
  - [`resources/templates/template_questions-log.md`](./resources/templates/template_questions-log.md)
  - [`resources/templates/template_challenges.md`](./resources/templates/template_challenges.md)
