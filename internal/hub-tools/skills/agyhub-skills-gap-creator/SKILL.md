---
name: agyhub-skills-gap-creator
description: Guides the agent in creating a new, specialized internal skill based on an identified gap (from a cluster role definition or an ad-hoc requirement). Conducts a rigorous 'Grill Me' interview to confirm scope, anti-scope, and typology group, solicits authoritative documentation (web links or local files), synthesizes best practices, and authors a complete, verified skill in internal/<typology>/skills/<skill-name>/.
---

# Agyhub Skills Gap Creator: Specialized Skill Authoring Assistant

This skill equips an agent to act as a **Skill Engineer** within the Antigravity Skills Hub. It provides a structured, rigorous methodology for transforming an identified capability gap—whether documented in a cluster role specification (`clusters/<role-name>.md`) or requested on-demand by a user—into a production-grade, highly targeted, and verified internal skill.

---

## When to Use This Skill

Activate this skill whenever:
- The user requests to create or author a missing skill identified during a cluster gap analysis (e.g., `gcp-analytics-hub-data-sharing`, `dataplex-data-quality-autodq`, `cloud-dlp-sensitive-data-protection`).
- The user asks to build a new custom skill for a specific workflow, tool, or integration from scratch.
- An agent needs guidance on interviewing the user, gathering authoritative documentation links, defining strict scope boundaries, and packaging an Antigravity skill using progressive disclosure.

> [!NOTE]
> **Independent Lifecycle**: Creating gap skills is completely decoupled from role creation. It can be run as a standalone task at any time, for any domain or team.

---

## The 5-Phase Skill Creation Lifecycle

```mermaid
flowchart TD
    A["Phase 1: Gap Ingestion & Triage<br>(From cluster markdown or user prompt)"] --> B["Phase 2: 'Grill Me' Clarification Interview<br>(Scope, anti-scope, triggers, doc links, typology)"]
    B --> C["Phase 3: Documentation Ingestion & Research<br>(Read web URLs, local specs, API docs)"]
    C --> D["Phase 4: Progressive Disclosure Authoring<br>(internal/&lt;typology&gt;/skills/&lt;name&gt;/SKILL.md + assets)"]
    D --> E["Phase 5: Hub Validation & Optional Cluster Sync<br>(agyhub info, test enable, cluster JSON update)"]
```

---

### Phase 1: Gap Ingestion & Triage

Accept and parse the skill requirement from either of two entry points:

1. **From an Existing Cluster Blueprint**:
   - Locate the cluster companion markdown: `clusters/<role-name>.md`.
   - Inspect **Section 3: Missing Skills Analysis (Catalog Gaps)**.
   - Extract the recommended skill identifier, architectural need, and key capabilities.
2. **From an Ad-Hoc User Request**:
   - Extract the user's intended skill name, target platform/technology, and desired automation.

---

### Phase 2: The "Grill Me" Clarification Interview

To prevent bloated, vague, or overlapping skills, the agent **must** conduct an interactive interview ("Grill Me") with the user before writing any files. Use interactive tools (e.g., `ask_question`) or structured inquiries.

#### Mandatory Interview Gates

#### Gate 1: Precise Boundaries & Anti-Scope
- **What MUST this skill do?** What are the top 2–4 concrete workflows or tasks it automates?
- **What must this skill NOT do (Anti-Scope)?** Where are the boundaries? 
  *Example*: For `gcp-analytics-hub-data-sharing`, it designs and manages exchanges and listings, but does *not* write ETL transformations (handled by `gcp-data-pipelines`) or configure VPC networks (handled by `foundation-builder`).

#### Gate 2: Activation Triggers & User Intent
- What specific user prompts, questions, or file contexts should cause an agent to activate this skill?
- What third-person description should be placed in YAML frontmatter to ensure accurate progressive disclosure?

#### Gate 3: Authoritative Documentation & Reference Links
- Ask the user for authoritative documentation links:
  - **Official vendor documentation URLs** (e.g. Google Cloud docs, API reference, Terraform registry).
  - **Local specification files or reference implementations** (e.g. existing YAML configs, Python scripts, architectural schemas).
  - If the user does not have links immediately at hand, propose authoritative documentation sources and confirm with the user before proceeding.

#### Gate 4: Execution Architecture & Asset Model
- Will this skill be purely procedural guidance in `SKILL.md`, or does it require:
  - **Executable scripts** in `scripts/` (e.g. validation script, CLI wrapper, linter)?
  - **Templates / Schemas** in `resources/` (e.g. declarative YAML templates, JSON schemas, policy templates)?
  - **Deep-dive references** in `references/` (e.g. API parameter tables, troubleshooting matrices) for progressive disclosure?

#### Gate 5: Typology & Group Organization
- Which **typology or domain group** should this skill belong to?
  - `hub-tools/`: Hub automation, authoring, and management assistants (`internal/hub-tools/skills/`).
  - Domain typologies: `data-platform/`, `security/`, `mlops/`, `devops/`, etc. (`internal/<typology>/skills/`).
  - Starter templates: `templates/` (`internal/templates/skills/`).
- Quick scaffolding via CLI:
  ```bash
  python3 bin/agyhub create skill <skill-name> -g <typology>
  ```

---

### Phase 3: Documentation Ingestion & Research

Once reference URLs or local files are identified:
1. **Fetch & Read Documentation**:
   - Use `read_url_content` to fetch public documentation pages.
   - Use `view_file` to inspect local files or repository references.
   - If specific API endpoints or gcloud flags are ambiguous, search official docs to retrieve exact parameter names.
2. **Synthesize Technical Facts**:
   - Extract exact CLI commands (e.g., `gcloud ...`, `bq ...`, `terraform ...`).
   - Extract exact configuration schemas, mandatory fields, and default values.
   - Identify common error patterns, quotas, or failure modes.

---

### Phase 4: Progressive Disclosure Authoring & Packaging

Scaffold the skill inside `internal/<typology>/skills/<skill-name>/` (or run `agyhub create skill <name> -g <typology>`) following the Antigravity skill architecture:

```text
internal/<typology>/skills/<skill_name>/
├── SKILL.md          # Required: Main instruction file with YAML frontmatter
├── references/       # Recommended: Deep API reference, parameter guides, manuals
├── scripts/          # Optional: Python or shell helper scripts
└── resources/        # Optional: Reusable YAML templates, JSON schemas, boilerplates
```

#### 1. Authoring `SKILL.md`

`SKILL.md` must be lean, structured, and focused. Bulky reference tables belong in `references/`.

```markdown
---
name: <skill-name>
description: >-
  <Third-person description stating EXACTLY what the skill does and WHEN to activate it.>
  Example: "Guides designing, publishing, and subscribing to Google Cloud Analytics Hub data exchanges and clean rooms. Activate when configuring cross-project dataset sharing or listings."
---

# <Skill Title>

<Brief 2-3 sentence overview of the capability.>

## When to Use This Skill
- **Activate when**: <List 3-5 explicit trigger scenarios, user questions, or file types>
- **Do NOT activate when**: <Explicit anti-scope boundaries; mention which other skills handle those>

## Workflow & Guidelines

### 1. <Step 1: Prerequisites / Discovery>
<Instructions, discovery commands, or pre-flight checks.>

### 2. <Step 2: Core Procedure / Configuration>
<Numbered, copy-pasteable commands and declarative configurations.>

```bash
# Example command
...
```

### 3. <Step 3: Verification & Quality Validation>
<How to verify the output, check logs, or validate syntax.>

## References & Resources
- Link to deep-dive files in `references/` (e.g., `[API Reference](./references/api-guide.md)`).
- Link to templates in `resources/` (e.g., `[Sample YAML](./resources/template.yaml)`).
- Link to helper scripts in `scripts/` (e.g., `[Validator](./scripts/validate.py)`).
```

#### 2. Authoring Supporting Assets (As Needed)

- **`references/`**: Place detailed manual excerpts, exhaustive CLI flag references, and troubleshooting guides here. The agent will only load these files when needed, saving context tokens.
- **`resources/`**: Store boilerplate YAML files, Terraform snippets, or JSON schemas that users or agents can copy directly.
- **`scripts/`**: Ensure all scripts use the Python standard library (zero-pip dependencies) or POSIX shell, with `--help` and clean exit codes.

---

### Phase 5: Hub Validation & Optional Cluster Synchronization

After authoring the files:

1. **Verify Discovery with `agyhub`**:
   ```bash
   python3 bin/agyhub list
   python3 bin/agyhub info <skill-name>
   ```
   *Confirm the skill appears under `internal/<typology>` and its documentation renders without errors.*

2. **Test Workspace Activation**:
   ```bash
   TMP_DIR=$(mktemp -d)
   python3 bin/agyhub -w "$TMP_DIR" enable <skill-name>
   python3 bin/agyhub -w "$TMP_DIR" status
   python3 bin/agyhub -w "$TMP_DIR" disable <skill-name>
   rm -rf "$TMP_DIR"
   ```

3. **Optional Cluster Synchronization**:
   - If the skill was created to resolve a gap from a cluster (e.g., `gcp-data-enterprise-architect`):
     - Offer to add the new skill name to `clusters/<role-name>.json` under `"skills": [...]`.
     - Offer to update `clusters/<role-name>.md` to mark the gap as implemented and add it to the competency matrix.
   - If the skill is general-purpose, it is immediately available for any cluster or workspace via `agyhub enable <skill-name>`.

---

## Best Practices Checklist

- [ ] **Third-Person Description**: The YAML frontmatter `description` uses third-person syntax ("Designs...", "Configures...", "Activate when...").
- [ ] **Clear Anti-Scope**: Explicitly documents what the skill does *not* do to prevent overlap.
- [ ] **Progressive Disclosure**: Bulky documentation is moved to `references/` rather than clogging the main `SKILL.md`.
- [ ] **Zero-Pip Helper Scripts**: Any scripts in `scripts/` rely strictly on the Python Standard Library.
- [ ] **Tested with `agyhub`**: Verified using `agyhub info <skill-name>` and test workspace enablement.
