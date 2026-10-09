# Workspace Setup, Config Customization & Google Drive Sync Guide (`gcp-project-copilot`)

This reference defines the exact procedures and CLI invocations for:
1. **Scaffolding a customer project workspace** (`specs/`, `project/common/`, `project/meetings/`, `project/topics/`).
2. **Interactively customizing `specs/specs_project.md` and `specs/gdrive_sync_manifest.json`**.
3. **Executing Google Drive synchronization** (`scripts/sync_drive.py`) from any workspace.

---

## 1. Resolving Skill Script Paths from Any Workspace

Because `gcp-project-copilot` is a workspace-agnostic skill, its executable scripts live inside the skill directory alongside `SKILL.md`:
- **Workspace Scaffolding & Config Customization Script**: `<skill-dir>/scripts/init_workspace.py`
- **Google Drive & Native Google Docs Sync Script**: `<skill-dir>/scripts/sync_drive.py`

*(Note: When `SKILL.md` is loaded from `/path/to/gcp-project-copilot/SKILL.md`, `<skill-dir>` is `/path/to/gcp-project-copilot`).*

---

## 2. Scaffolding a New Workspace (`scripts/init_workspace.py`)

When the user asks to set up, initialize, or scaffold `gcp-project-copilot` in a workspace:

### Step 2.1: Gather Project & Google Drive Parameters
Determine whether the user has provided:
- **Option A — Kickoff Meeting Google Doc (`https://docs.google.com/document/d/<DOC_ID>`)**:
  Read the `Quick notes`, `Full notes`, and `Transcript` tabs via `gdocs` first to automatically infer `CUSTOMER_NAME`, `PROJECT_NAME`, `PROGRAM_NAME`, `PILOT_DOMAIN`, `UPCOMING_DOMAINS`, `EXTERNAL_PARTNERS`, initial `D1..Dn` domains, and speaker ASR aliases. Only ask the user for missing Google Drive Folder URLs (`Root Project Drive Folder`, etc.).
- **Option B — Interactive Setup (No Kickoff Doc Yet)**:
  Ask the user for the core project identity and Google Drive Folder URL(s):
  1. **Customer & Project Name** (`CUSTOMER_NAME`, `PROJECT_NAME`, `PROGRAM_NAME`, `PILOT_DOMAIN`)
  2. **Root Project Google Drive Folder URL or ID** (e.g., `https://drive.google.com/drive/folders/<ID>`, where `common/`, `meetings/`, and `topics/` will be mirrored)
  3. *(Optional)* **Meeting Notes Folder URL/ID** and **Deliverables Folder URL/ID**

### Step 2.2: Run `scripts/init_workspace.py`
Execute `init_workspace.py` targeting the workspace root (`--workspace .`):

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
  --meeting-notes-folder "<Notes Drive Folder URL or ID>" \
  --deliverables-folder "<Deliverables Drive Folder URL or ID>" \
  --discover-drive \
  --with-gemini-rules
```

**What this command creates**:
- `<workspace-root>/specs/specs_project.md` (populated with customer identity and Drive folder links)
- `<workspace-root>/specs/gdrive_sync_manifest.json` (initialized with `root_folder_id`, `root_folder_name`, `root_folder_url`, and any existing remote `common/`, `meetings/`, `topics/` folders discovered via `--discover-drive`)
- `<workspace-root>/project/common/meetings_registry.md`
- `<workspace-root>/project/common/project_members.md`
- `<workspace-root>/project/common/project_glossary.md`
- `<workspace-root>/project/common/project_questions-log.md`
- `<workspace-root>/project/common/project_challenges.md`
- `<workspace-root>/project/meetings/` and `<workspace-root>/project/topics/`
- `<workspace-root>/GEMINI.md` (when `--with-gemini-rules` is passed)

---

## 3. Customizing `specs/specs_project.md` & `specs/gdrive_sync_manifest.json` in an Existing Workspace

Whenever the user asks to configure, customize, or update project settings, Google Drive links, domains, or stakeholder aliases:

### A. Updating Customer Identity or Google Drive Folder URLs (`--update-config`)
To update Section 1 (Customer Identity) or Section 2.1 (Google Drive Folders) in `specs/specs_project.md` **and** automatically synchronize `specs/gdrive_sync_manifest.json` without touching existing `project/common/` files:

```bash
python3 <skill-dir>/scripts/init_workspace.py \
  --workspace <workspace-root> \
  --update-config \
  --root-folder "https://drive.google.com/drive/folders/<NEW_FOLDER_ID>" \
  --root-folder-name "20 Project" \
  --discover-drive
```
- **Automatic URL Parsing**: `init_workspace.py` accepts either a full `https://drive.google.com/.../folders/<ID>` URL or a raw folder ID and extracts the canonical ID automatically.
- **Two-File Consistency**: Updating `--root-folder` updates both Section 2.1 of `specs/specs_project.md` and `root_folder_id` / `root_folder_url` in `specs/gdrive_sync_manifest.json`. If the `root_folder_id` changed to a different Drive folder, stale folder/document mappings are cleared automatically (unless `--keep-manifest-entries` is passed) so the next `sync_drive.py` run mirrors cleanly into the new Drive folder.

### B. Customizing Canonical Architectural Domains (`D1..Dn` in Section 3)
- Section 3 of `specs/specs_project.md` defines the canonical domains (`D1..Dn`) used to categorize `questions-log` and `challenges`.
- When tailoring domains for a customer:
  1. Update the Section 3 table in `specs/specs_project.md` (`Domain ID`, `Canonical Domain Name`, plain-code `` `<topic-slug>` ``, and `Core Technical Scope & Keywords`).
  2. Ensure the domain headings in `project/common/project_questions-log.md` and `project/common/project_challenges.md` match `D1..Dn`.

### C. Customizing Transcript Phonetic Aliases (Section 5)
- Section 5 of `specs/specs_project.md` stores internal-only speech-to-text (ASR) variants and handle mappings.
- Add or refine rows in Section 5 (`Canonical Full Name | Organization | Handle / Email Prefix | Known Transcript Aliases & ASR Variants`), and keep `project/common/project_members.md` free of ASR misspellings.

---

## 4. Executing Google Drive Synchronization from the Workspace (`scripts/sync_drive.py`)

Whenever a workflow step or direct user prompt asks to synchronize the workspace (`project/`) with Google Drive:

### Step 4.1: Pre-Flight Configuration Check
1. Inspect `specs/specs_project.md` (Section 2.1) and `specs/gdrive_sync_manifest.json` (`root_folder_id`).
2. If the Root Project Drive Folder ID is missing or still set to a template placeholder (`{{DRIVE_ROOT_FOLDER_ID}}`):
   - Pause and ask the user for the target Google Drive Folder URL or ID.
   - Run `python3 <skill-dir>/scripts/init_workspace.py --workspace <workspace-root> --update-config --root-folder "<URL_OR_ID>"` to persist it in both `specs/specs_project.md` and `specs/gdrive_sync_manifest.json`.

### Step 4.2: Run `scripts/sync_drive.py`
Execute `sync_drive.py` from the skill's `scripts/` directory, passing `--workspace <workspace-root>` (or running it with `Cwd` set to `<workspace-root>`):

```bash
# Preview changes without modifying Google Drive (optional dry-run)
python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root> --dry-run

# Execute live synchronization to Google Drive
python3 <skill-dir>/scripts/sync_drive.py --workspace <workspace-root>
```

**What `sync_drive.py` does automatically**:
1. **Resolves Target Workspace & Root Drive Folder ID**: Reads `specs/specs_project.md` and `specs/gdrive_sync_manifest.json` in `<workspace-root>`.
2. **Phase 1 — Folder Mirroring**: Ensures every subfolder under `project/` (`common/`, `meetings/...`, `topics/...`) exists in Google Drive under the Root Project Drive Folder and records its folder ID in `specs/gdrive_sync_manifest.json`.
3. **Phase 2 — Topological Native Google Docs Sync**:
   - Sorts all `.md` files in `project/` in 3-tier link-dependency order (`topics/` $\to$ `meetings/` $\to$ `common/`) so any referenced document is synced before the document that links to it.
   - Rewrites relative `.md` links to their resolved Google Docs URLs.
   - Imports new documents (`gdocs mutate import-md --pageless` + `gdrive mutate mv`) or updates modified documents (`gdocs mutate sync` when open comments exist, or `gdocs mutate import-md --update` otherwise) based on SHA-256 hashes in `specs/gdrive_sync_manifest.json`.
4. **Phase 3 — Registry Refresh**: Automatically rewrites Section 2.2 (`#### A. Synchronized Drive Subfolders` and `#### B. Synchronized Native Google Docs`) in `specs/specs_project.md` so the human-readable spec and `gdrive_sync_manifest.json` remain 100% synchronized.

