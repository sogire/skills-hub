---
name: gcp-console-demo-generator
description: >-
  Designs story-driven Google Cloud customer demos ("history demos"), provisions
  isolated multi-domain demo assets and persona permissions inside a single
  Sandbox/Argolis GCP project, captures sanitized 2x HiDPI Google Cloud Console
  screenshots across dedicated multi-persona Chrome CDP profiles with numbered
  callout overlays, and assembles Google Docs-ready visual walkthroughs (plus
  optional Google Slides storyboards) under project/topics/<topic-slug>/demos/<demo-slug>/.
  Activate when a user asks to create a narrative or story-based GCP demo,
  provision demo datasets/policies/exchanges for a customer walkthrough, or
  automatically capture Google Cloud Console UI screenshots for a demo flow.
  Do not use for production multi-project landing zones (use
  google-cloud-recipe-foundation-builder), standalone SVG diagram rendering
  without a demo flow (use gcp-architecture-diagram), or interactive React/Streamlit
  web apps (use building-data-apps).
---

# GCP Console Demo & Storyboard Generator (`gcp-console-demo-generator`)

`gcp-console-demo-generator` orchestrates end-to-end **story-driven Google Cloud Console demonstrations** for customer architecture engagements (natively integrated with [`gcp-project-copilot`](../gcp-project-copilot/SKILL.md) and [`gcp-architecture-diagram`](../gcp-architecture-diagram/SKILL.md), or usable standalone). It guides an interactive "Grill-Me" storyboard interview, provisions synthetic datasets and governance controls inside a **single existing Sandbox/Argolis GCP project**, captures sanitized 2× HiDPI Cloud Console screenshots across **dedicated per-persona Chrome profiles**, and packages everything into customer-ready Markdown deliverables that synchronize cleanly to Google Docs and Google Drive.

---

## When to Use This Skill

- **Activate when**:
  1. **Designing a narrative / "history" GCP demo**: Turning a technical domain (`D1..Dn`), architectural pattern, or customer question (`[D#-Q##]`) into a multi-Act detective/day-in-the-life story mapped to real customer business parallels.
  2. **Provisioning a live Sandbox GCP demo**: Setting up synthetic datasets, metadata descriptions, BigQuery Data Sharing (Analytics Hub) exchanges/Clean Rooms, CLS/RLS policies, Dataplex scans, and multi-persona IAM bindings inside a single Sandbox GCP project (with an idempotent `teardown.sh`).
  3. **Capturing Google Cloud Console UI screenshots**: Automating multi-persona Cloud Console navigation via zero-dependency Python Chrome DevTools Protocol (CDP), masking internal Sandbox IDs/Argolis emails in the DOM, adding numbered callout badges (`1`, `2`, `3`), and embedding 2× HiDPI `.png` screenshots into deliverables.
  4. **Upgrading an existing text/SQL demo guide with live Console screenshots**: Retrofitting a Markdown demo playbook with automated GCP Console captures and optional code-free Google Slides storyboards.
- **Do NOT activate when (Anti-Scope)**:
  - Deploying production organization hierarchies or VPC-SC landing zones (use `google-cloud-recipe-foundation-builder`).
  - Rendering standalone architecture diagrams without a demo narrative or Console flow (use `gcp-architecture-diagram`).
  - Building custom React/Vite or Streamlit frontend web dashboards (use `building-data-apps`).

---

## Target Directory Structure (`project/topics/<topic-slug>/demos/<demo-slug>/`)

Inside a `gcp-project-copilot` workspace, every demo belongs to its canonical domain topic (`project/topics/<topic-slug>/demos/<demo-slug>/`). Customer-facing deliverables sit in `docs/`, `screenshots/`, and `diagrams/` (synced to Google Drive), while live Sandbox credentials, real Project IDs, and provisioning state stay strictly inside dot-prefixed `.runtime/` (**100% excluded from Google Drive sync**):

```text
<workspace-root>/
├── specs/
│   └── specs_project.md                                  # Optional Section 6: Sandbox Project ID & Argolis Persona Roster (local-only)
└── project/
    └── topics/
        └── <topic-slug>/
            └── demos/
                └── <demo-slug>/
                    ├── docs/
                    │   ├── <demo-stem>.md                # Visual Demo Guide with embedded screenshots & parameterized code
                    │   └── <demo-stem>_slides-prompt.md  # Optional 100% code-free Google Slides storyboard
                    ├── screenshots/
                    │   └── <demo-stem>/
                    │       ├── act-01-publisher-listing.png
                    │       └── act-02-subscriber-query.png
                    ├── diagrams/
                    │   └── <demo-stem>/
                    │       ├── architecture-flow.svg     # Generated via gcp-architecture-diagram
                    │       ├── architecture-flow.png     # 2x HiDPI companion PNG
                    │       └── specs/
                    │           └── architecture-flow.json
                    └── .runtime/                         # LOCAL-ONLY (ignored by sync_drive.py)
                        ├── demo_env.json                 # Real Sandbox Project ID, region & Argolis persona email bindings
                        ├── provision.sh                  # Live idempotent setup script executed on Sandbox Project
                        ├── seed_data.sql                 # Synthetic storyline DDL/DML & metadata enrichment
                        ├── state.json                    # Tracked inventory of created assets & IAM bindings
                        ├── teardown.sh                   # One-command idempotent cleanup for post-workshop teardown
                        └── capture_manifest.json         # Declarative CDP capture plan (personas, URLs, DOM masks, callouts)
```

---

## Mandatory Guardrails

1. **Zero Internal Identifier Leakage in Customer Deliverables**:
   Never write real Sandbox/Argolis GCP Project IDs, Project Numbers, or `@gcp.altostrat.com` / `@google.com` emails inside `docs/*.md` or `diagrams/**/*.svg`. Keep real identifiers exclusively in `.runtime/` (and `specs/specs_project.md`), use customer-aligned logical aliases (e.g., `gcp-logistics-domain`, `steward@customer-domain.com`) or `{{PROJECT_ID}}` in `docs/`, and enforce DOM sanitization during screenshot capture.
2. **Strictly Single Sandbox GCP Project**:
   Never create or delete GCP projects (`gcloud projects create` / `delete`). Always deploy into **one existing user-supplied Sandbox GCP project**, simulating multi-project or Data Mesh topologies (Producer vs. Consumer vs. Governance) using clear resource prefixes (`<demo_prefix>_producer_*`, `<demo_prefix>_consumer_*`) and distinct Argolis persona accounts.
3. **Keep Demo Assets Live by Default + Mandatory `teardown.sh`**:
   Leave provisioned Sandbox assets **live** after screenshot capture so the user can present the live environment in workshops, and **always** generate an executable, idempotent `.runtime/teardown.sh` backed by `.runtime/state.json`.
4. **Portable Relative Paths & Mermaid Hygiene**:
   All links inside `docs/*.md` must use portable relative paths (`../screenshots/<demo-stem>/...`, `../diagrams/<demo-stem>/...`) — never `file:///` or `/usr/...` paths, and never use `;` or `<br>` inside Mermaid blocks.

---

## The 4-Phase Execution Workflow

> [!IMPORTANT]
> **Resolving `<skill-dir>` for Script Execution**:
> All helper scripts reside inside `<skill-dir>/scripts/` alongside this `SKILL.md`. Always invoke them via their absolute path.

### Phase 1: Story Grill-Me & Storyboard Approval

Read **[`references/storyboard_and_grill_guide.md`](./references/storyboard_and_grill_guide.md)** before starting Phase 1.

- [ ] **Step 1.1 — Load Engagement Context**:
  If working inside a `gcp-project-copilot` workspace, read `<workspace>/specs/specs_project.md`, `project/common/project_questions-log.md`, and `project/common/project_challenges.md` (plus any related `project/topics/<topic-slug>/docs/` or `project/questions/` files).
- [ ] **Step 1.2 — Interactive Grill-Me (`ask_question`, One Question at a Time)**:
  Interview the user on any unresolved story choices, providing a `(Recommended)` option first:
  1. **Target Canonical Domain (`D1..Dn`) & `<topic-slug>`** (if not obvious from the prompt).
  2. **Storyline Metaphor & Customer Parallel** (e.g., an engaging universal detective metaphor like *Lost Cargo* paired with the customer's real industry parallel vs. a direct synthetic customer-industry dataset).
  3. **Acts & Persona Roster** (e.g., `Publisher / Data Owner` vs. `Subscriber / Analyst` vs. `Restricted User`, typically 3–6 crisp Acts proving specific GCP capabilities including at least one "Blocked/Masked vs. Authorized" security beat).
  4. **Sandbox Environment & Argolis Persona Accounts** (confirm the single `SANDBOX_PROJECT_ID`, `BQ_LOCATION` / `GCP_REGION`, and the Argolis emails mapped to each persona if not already recorded in Section 6 of `specs/specs_project.md`).
  5. **Companion Slides Storyboard** (confirm whether to also generate `docs/<demo-stem>_slides-prompt.md` alongside `docs/<demo-stem>.md` and `diagrams/<demo-stem>/`).
- [ ] **Step 1.3 — Gate 1: Present & Approve the Demo Storyboard**:
  Present a concise **Act-by-Act Storyboard Table** (Act, Persona, Single-Project Prefixed Asset, GCP Capability Proven, Target Console Screenshot, Logical Alias Shown on Screen) and obtain user sign-off before running GCP mutations.

---

### Phase 2: Single-Sandbox GCP Provisioning (`.runtime/`)

Read **[`references/provisioning_and_teardown_patterns.md`](./references/provisioning_and_teardown_patterns.md)** before authoring `.runtime/` scripts.

- [ ] **Step 2.1 — Mandatory Auth, Shared-Sandbox `roles/owner` & Safety Pre-Flight**:
  - Follow `google-cloud-auth-verification` (`gcloud auth list`, verify ADC/project access on `SANDBOX_PROJECT_ID`), `accidental-data-loss-prevention` (never drop pre-existing non-demo datasets/tables), and `enforcing-resource-attribution` (`--label="datacloud:antigravity"` on supported `bq` jobs).
  - Inspect existing project IAM roles for every persona email (`gcloud projects get-iam-policy`). In shared Sandboxes where secondary accounts already hold `roles/owner` or `roles/editor`, follow **Section 3.1** of [`references/provisioning_and_teardown_patterns.md`](./references/provisioning_and_teardown_patterns.md) (`RLS`, `CLS` Policy Tags, and IAM v2 Deny Policies enforce cleanly even on `roles/owner`, whereas Dataset RBAC omission requires a non-Owner account).
- [ ] **Step 2.2 — Initialize `.runtime/` Configuration & Provisioning Scripts**:
  Create `<demo-dir>/.runtime/` (`chmod 700` optional) containing:
  - `demo_env.json`: Real `sandbox_project_id`, `sandbox_project_number`, `sandbox_project_name`, `region`, `bq_location`, `demo_prefix`, logical story aliases (`project_aliases`, `dataset_aliases`), and `personas` (`role` $\rightarrow$ `argolis_email`, `display_alias`, `cdp_port`).
  - `seed_data.sql` & `provision.sh`: Idempotent setup (enable APIs, create `<demo_prefix>_*` datasets/tables/graphs/views, enrich all table/column descriptions, attach CLS policy tags / uncorrelated `IN` RLS policies per Section 3.2 of `provisioning_and_teardown_patterns.md` / Exchanges / Clean Rooms, and bind IAM roles to the real Argolis persona emails).
  - `state.json` & `teardown.sh` (`chmod +x`): Deterministic reverse-dependency cleanup script removing **only** the `<demo_prefix>_*` resources and persona bindings created by this demo.
- [ ] **Step 2.3 — Execute & Verify Provisioning**:
  Run `.runtime/provision.sh`, verify all tables/policies/listings via `bq` / `gcloud` / REST checks, and confirm `teardown.sh --dry-run` (or syntax check `bash -n`) passes cleanly.

---

### Phase 3: Multi-Persona GCP Console Screenshot Capture

Read **[`references/console_urls_and_selectors.md`](./references/console_urls_and_selectors.md)** for canonical GCP Console deep-links, BigQuery `<canvas>` grid rules, `--inspect-scene` diagnostics, and `/browser` fallback guidance.

- [ ] **Step 3.1 — Run Upfront `precheck` & Ensure Persistent Persona Chrome Profiles**:
  First run a fast environment precheck verifying Chrome availability, cached/live persona SSO state (including DOM email verification so wrong-account logins are caught immediately as `WRONG_ACCOUNT`), and optional Google Drive LOAS (`gcert`) readiness:
  ```bash
  python3 <skill-dir>/scripts/manage_persona_profiles.py precheck \
    --env <demo-dir>/.runtime/demo_env.json \
    --check-drive
  ```
  - If all personas already report `[READY]` (`AUTHENTICATED` in cache), you do **not** need to open GUI login windows—`capture_gcp_console.py` will automatically launch cached `AUTHENTICATED` profiles in `--headless=new` mode!
  - If any persona reports `UNCACHED`, `AUTH_REQUIRED`, or `WRONG_ACCOUNT`, launch interactive SSO login (`--keep-alive` with `IsDaemon: true` in `run_command`; add `--reset` if `WRONG_ACCOUNT` was reported):
    ```bash
    python3 <skill-dir>/scripts/manage_persona_profiles.py ensure \
      --env <demo-dir>/.runtime/demo_env.json \
      --keep-alive
    ```
    Ask the user to sign into the opened Chrome window (where `<argolis_email>` is pre-filled), verify via `manage_persona_profiles.py status --env <demo-dir>/.runtime/demo_env.json` until all personas report `[AUTHENTICATED]`, and stop the daemon cleanly once capture finishes.
- [ ] **Step 3.2 — Author `.runtime/capture_manifest.json`**:
  Copy and customize [`resources/templates/template_capture_manifest.json`](./resources/templates/template_capture_manifest.json):
  - Map every scene to its `persona`, clean target `url` (`https://console.cloud.google.com/...?project=<SANDBOX_PROJECT_ID>` — never append `&authuser=`), deterministic UI `actions` (`bq_set_query` + `bq_run_query`, `wait_for_selector`, `click`), `dom_replacements`, and `callouts` (`1`, `2`, `3` highlight boxes; use viewport coordinate boxes + `anchor: "bottom-left"` for BigQuery `<canvas>` result rows).
- [ ] **Step 3.3 — Execute Automated 2× HiDPI Screenshot Capture**:
  ```bash
  python3 <skill-dir>/scripts/capture_gcp_console.py \
    --manifest <demo-dir>/.runtime/capture_manifest.json
  ```
  - **Built-In Diagnostics (`--inspect-scene`)**: If a selector or callout box needs calibration, run `capture_gcp_console.py --manifest ... --inspect-scene <scene-id>` (add `--headed` only if visual browser inspection is desired) to emit live button/tab/`<canvas>`/banner coordinates as JSON without writing temporary scripts.
  - **Fallback for Highly Dynamic Canvases**: If an interactive force-directed graph resists automation, recommend or use Antigravity's `/browser` mode for that scene and save the resulting PNG into `screenshots/<demo-stem>/`.
- [ ] **Step 3.4 — Gate 3: Mandatory Visual Inspection of Every Screenshot**:
  Inspect **every** generated `.png` in `screenshots/<demo-stem>/` using `read_file` / `view_file` to verify:
  1. Zero Google login walls, error modals, stale background `Untitled query` tabs, or unresolved loading spinners.
  2. Real `SANDBOX_PROJECT_ID` and `@gcp.altostrat.com` / operator emails are cleanly masked with story aliases in the Console header, Monaco editor, and error banners.
  3. Highlight boxes and numbered callout badges (`1`, `2`, `3`) align cleanly without obscuring key values.
  *(If any frame needs adjustment, refine `.runtime/capture_manifest.json` and re-run `--scene <scene-id>`.)*

---

### Phase 4: Deliverable Assembly, Validation & Google Drive Sync

- [ ] **Step 4.1 — Render Companion GCP Reference Architecture Diagram**:
  Use [`gcp-architecture-diagram`](../gcp-architecture-diagram/SKILL.md) (`render_gcp_diagram.py`) to compile `<demo-dir>/diagrams/<demo-stem>/specs/architecture-flow.json` into `<demo-dir>/diagrams/<demo-stem>/architecture-flow.svg` (and 2× HiDPI `.png`), visually verifying the rendered `.png`.
- [ ] **Step 4.2 — Author Customer Deliverables (`docs/`)**:
  - Author `<demo-dir>/docs/<demo-stem>.md` following [`resources/templates/template_demo_guide.md`](./resources/templates/template_demo_guide.md) (noting that `docs/*.md` sits 5 levels below `project/`, so links to `project/common/` use `../../../../../common/...`), embedding `../diagrams/<demo-stem>/architecture-flow.svg` and each `../screenshots/<demo-stem>/act-*.png` with matching numbered callout explanations and parameterized (`{{PROJECT_ID}}` / logical alias) code snippets.
  - *(Optional)* If requested in Phase 1, author `<demo-dir>/docs/<demo-stem>_slides-prompt.md` following [`resources/templates/template_demo_slides_prompt.md`](./resources/templates/template_demo_slides_prompt.md) (100% code-free slides referencing the captured screenshots).
- [ ] **Step 4.3 — Validate Bundle Hygiene (`exit 0` Required)**:
  ```bash
  python3 <skill-dir>/scripts/validate_demo_bundle.py --demo-dir <demo-dir> --require-runtime
  ```
  Fix any reported leaked sandbox identifiers, broken relative links, missing images, or Mermaid syntax issues before proceeding.
- [ ] **Step 4.4 — Cross-Link & Synchronize to Google Drive (`gcp-project-copilot`)**:
  - In a `gcp-project-copilot` workspace, add relative links to the new demo under the corresponding domain in `project/common/project_challenges.md` (and Section 3 of `specs/specs_project.md` if first deliverable in `<topic-slug>`).
  - Run a `--dry-run` preview first to verify `links_rewritten > 0` and `local_images > 0`, then synchronize **both** the demo folder and `project/common/project_challenges.md` via [`gcp-project-copilot/scripts/sync_drive.py`](../gcp-project-copilot/scripts/sync_drive.py) (which uploads screenshot/diagram assets first, rewrites relative doc and asset links to live Google Drive URLs, stages inline images into native Google Docs, and skips `.runtime/`):
    ```bash
    python3 <copilot-skill-dir>/scripts/sync_drive.py \
      --workspace <workspace-root> \
      --file project/topics/<topic-slug>/demos/<demo-slug> \
      --file project/common/project_challenges.md \
      --dry-run

    python3 <copilot-skill-dir>/scripts/sync_drive.py \
      --workspace <workspace-root> \
      --file project/topics/<topic-slug>/demos/<demo-slug> \
      --file project/common/project_challenges.md
    ```
  - Remind the user that live demo assets remain active in `SANDBOX_PROJECT_ID` for workshops and can be cleaned up anytime via `<demo-dir>/.runtime/teardown.sh`.

---

## References, Templates & Scripts

- **Progressive-Disclosure Guides**:
  - [`references/storyboard_and_grill_guide.md`](./references/storyboard_and_grill_guide.md) — Phase 1 Grill-Me interview tree, story archetypes, and single-project Data Mesh simulation patterns
  - [`references/provisioning_and_teardown_patterns.md`](./references/provisioning_and_teardown_patterns.md) — Phase 2 idempotent `gcloud`/`bq`/REST provisioning, `.runtime/demo_env.json`, `state.json`, and `teardown.sh` patterns
  - [`references/console_urls_and_selectors.md`](./references/console_urls_and_selectors.md) — Phase 3 Cloud Console deep-links, BigQuery/Dataplex/IAM wait strategies, DOM masking, callouts, and `/browser` fallback
- **Executable Scripts**:
  - [`scripts/manage_persona_profiles.py`](./scripts/manage_persona_profiles.py) — Persistent per-Argolis-email Chrome CDP profile launcher & SSO login checker
  - [`scripts/capture_gcp_console.py`](./scripts/capture_gcp_console.py) — Zero-dependency pure-Python CDP Console automation, DOM sanitizer, callout renderer & 2× HiDPI PNG capturer
  - [`scripts/validate_demo_bundle.py`](./scripts/validate_demo_bundle.py) — Zero-leakage, relative-path, Mermaid, screenshot, and `teardown.sh` structural validator
- **Starter Templates**:
  - [`resources/templates/template_demo_guide.md`](./resources/templates/template_demo_guide.md) — Act-by-Act Visual Demo Guide template
  - [`resources/templates/template_demo_slides_prompt.md`](./resources/templates/template_demo_slides_prompt.md) — Companion code-free Google Slides Storyboard prompt template
  - [`resources/templates/template_capture_manifest.json`](./resources/templates/template_capture_manifest.json) — Declarative `capture_gcp_console.py` manifest template
