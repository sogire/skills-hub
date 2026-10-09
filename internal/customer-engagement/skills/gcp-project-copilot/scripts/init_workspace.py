#!/usr/bin/env python3
"""Scaffold and customize a customer engagement workspace for `gcp-project-copilot`.

Capabilities:
1. Scaffolds the directory hierarchy inside the target workspace (`--workspace` / `-w`):
   - `specs/`
   - `project/common/`
   - `project/meetings/`
   - `project/topics/`
2. Renders and customizes `specs/specs_project.md` and `specs/gdrive_sync_manifest.json`
   using CLI flags (accepting either full Google Drive URLs or raw Folder IDs).
3. Supports `--update-config` to update customer identity or Google Drive folder
   IDs/URLs in an existing `specs/specs_project.md` and `specs/gdrive_sync_manifest.json`
   while preserving existing domains (`D1..Dn`), ASR aliases, and `project/common/` files.
4. Supports `--discover-drive` to query the Root Project Drive Folder via `gdrive`
   and pre-populate existing `common/`, `meetings/`, and `topics/` folder IDs.
5. Initializes the 5 living master documents in `project/common/` (`meetings_registry.md`,
   `project_members.md`, `project_glossary.md`, `project_questions-log.md`,
   `project_challenges.md`) and optional `GEMINI.md` workspace rules.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

SKILL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATES_DIR = os.path.join(SKILL_ROOT, "resources", "templates")
GDRIVE_BIN = "/google/bin/releases/gemini-agents-gdrive/gdrive"


def extract_drive_id(url_or_id: Optional[str]) -> Optional[str]:
  """Extract a Google Drive folder or document ID from a URL or raw ID string."""
  if not url_or_id:
    return None
  raw = url_or_id.strip()
  if not raw or "{{" in raw or "}}" in raw:
    return None
  folder_match = re.search(r"folders/([A-Za-z0-9_-]{15,})", raw)
  if folder_match:
    return folder_match.group(1)
  doc_match = re.search(r"/d/([A-Za-z0-9_-]{15,})", raw)
  if doc_match:
    return doc_match.group(1)
  id_match = re.match(r"^([A-Za-z0-9_-]{15,})$", raw)
  if id_match:
    return id_match.group(1)
  return raw


def format_drive_folder_url(folder_id: str) -> str:
  """Return canonical Google Drive folder URL for a folder ID."""
  if folder_id.startswith("{{"):
    return f"https://drive.google.com/drive/folders/{folder_id}"
  return f"https://drive.google.com/drive/folders/{folder_id}"


def discover_drive_subfolders(
    root_folder_id: str, cwd: str
) -> Dict[str, Dict[str, str]]:
  """Inspect root_folder_id in Google Drive to find existing common/meetings/topics folders."""
  discovered: Dict[str, Dict[str, str]] = {}
  if not root_folder_id or root_folder_id.startswith("{{"):
    return discovered
  if not os.path.exists(GDRIVE_BIN):
    return discovered

  proc = subprocess.run(
      [GDRIVE_BIN, "readonly", "ls", root_folder_id, "--max", "200", "--json"],
      cwd=cwd,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
      check=False,
  )
  if proc.returncode != 0 or not proc.stdout.strip():
    return discovered
  try:
    parsed = json.loads(proc.stdout)
    items = (
        parsed
        if isinstance(parsed, list)
        else parsed.get("files", [])
        if isinstance(parsed, dict)
        else []
    )
    for item in items:
      c_name = item.get("name") or item.get("Name")
      c_mime = item.get("mimeType") or item.get("MimeType") or item.get("Type")
      c_id = item.get("id") or item.get("ID")
      if (
          c_name in ("common", "meetings", "topics")
          and c_id
          and ("folder" in str(c_mime).lower())
      ):
        discovered[c_name] = {
            "id": c_id,
            "name": c_name,
            "parent_id": root_folder_id,
            "url": format_drive_folder_url(c_id),
        }
  except json.JSONDecodeError:
    pass
  return discovered


def build_replacements(args: argparse.Namespace) -> Dict[str, str]:
  """Build template placeholder dictionary from CLI arguments."""
  today = datetime.date.today().isoformat()
  customer_name = args.customer_name or "Customer"
  customer_domain = (
      args.customer_domain
      or re.sub(r"[^a-z0-9]+", "", customer_name.lower()) + ".com"
  )
  project_name = args.project_name or f"{customer_name} Data Platform"
  words = [w for w in re.split(r"\s+", project_name) if w]
  default_acronym = (
      "".join(w[0].upper() for w in words[:4]) if len(words) >= 2 else "EDP"
  )
  project_acronym = args.project_acronym or default_acronym

  root_id = extract_drive_id(args.root_folder) or "{{DRIVE_ROOT_FOLDER_ID}}"
  notes_id = (
      extract_drive_id(args.meeting_notes_folder)
      or "{{MEETING_NOTES_FOLDER_ID}}"
  )
  deliverables_id = (
      extract_drive_id(args.deliverables_folder)
      or "{{DELIVERABLES_FOLDER_ID}}"
  )
  root_name = args.root_folder_name or "20 Project"

  return {
      "{{CUSTOMER_NAME}}": customer_name,
      "{{CUSTOMER_DESCRIPTION}}": (
          args.customer_description
          or f"Enterprise organization (`{customer_domain}`)"
      ),
      "{{CUSTOMER_DOMAIN}}": customer_domain,
      "{{PROJECT_NAME}}": project_name,
      "{{PROJECT_ACRONYM}}": project_acronym,
      "{{PROJECT_DESCRIPTION}}": (
          args.project_description
          or "Enterprise data & AI platform modernizing data ingestion, governance, and cross-domain sharing on Google Cloud"
      ),
      "{{PROGRAM_NAME}}": args.program_name or "Enterprise Data & AI Program",
      "{{PROGRAM_ALIAS}}": args.program_name or "Data & AI Program",
      "{{PILOT_DOMAIN}}": args.pilot_domain or "Initial Pilot Domain",
      "{{PILOT_USE_CASE}}": f"{args.pilot_domain or 'Pilot'} Analytics 360",
      "{{UPCOMING_DOMAINS}}": (
          args.upcoming_domains
          or "Finance, Supply Chain, Operations, Engineering"
      ),
      "{{EXTERNAL_PARTNERS}}": args.external_partners or "TBD",
      "{{DRIVE_ROOT_FOLDER_NAME}}": root_name,
      "{{DRIVE_ROOT_FOLDER_ID}}": root_id,
      "{{MEETING_NOTES_FOLDER_ID}}": notes_id,
      "{{DELIVERABLES_FOLDER_ID}}": deliverables_id,
      "{{YYYY-MM-DD}}": today,
      "{{YYYYMMDD}}": today.replace("-", ""),
      "{{TOTAL_COUNT}}": "0",
      "{{CUSTOMER_COUNT}}": "0",
      "{{GOOGLE_COUNT}}": "0",
      "{{PARTNER_COUNT}}": "0",
      "{{COUNT_1}}": "2",
      "{{COUNT_2}}": "2",
      "{{COUNT_3}}": "2",
      "{{COUNT_4}}": "3",
      "{{COUNT_5}}": "2",
      "{{COUNT_6}}": "2",
      "{{TOTAL_QUESTIONS}}": "0",
      "{{Q_COUNT}}": "0",
  }


def apply_replacements(text: str, replacements: Dict[str, str]) -> str:
  """Substitute known placeholders in template text."""
  for key, val in replacements.items():
    text = text.replace(key, val)
  return text


def render_clean_master_doc(
    template_name: str, replacements: Dict[str, str]
) -> str:
  """Render a project/common/ master document from its template with customer metadata."""
  tpl_path = os.path.join(TEMPLATES_DIR, template_name)
  with open(tpl_path, "r", encoding="utf-8") as f:
    raw = f.read()
  return apply_replacements(raw, replacements)


def update_existing_specs_project(
    specs_project_path: str, args: argparse.Namespace
) -> None:
  """Update Section 1 and Section 2.1 in an existing specs/specs_project.md file."""
  with open(specs_project_path, "r", encoding="utf-8") as f:
    text = f.read()

  def update_param_row(
      content: str,
      param_key: str,
      new_val: Optional[str],
      new_desc: Optional[str] = None,
  ) -> str:
    if not new_val and not new_desc:
      return content
    pattern = re.compile(
        rf"^(\|\s*\*\*`{re.escape(param_key)}`\*\*\s*\|\s*)([^|]+)(\|\s*)([^|]+)(\|.*)$",
        flags=re.MULTILINE,
    )

    def repl(m: re.Match) -> str:
      val_cell = f"**{new_val}** " if new_val else m.group(2)
      desc_cell = f"{new_desc} " if new_desc else m.group(4)
      return f"{m.group(1)}{val_cell}{m.group(3)}{desc_cell}{m.group(5)}"

    return pattern.sub(repl, content)

  text = update_param_row(
      text, "CUSTOMER_NAME", args.customer_name, args.customer_description
  )
  text = update_param_row(
      text, "PROJECT_NAME", args.project_name, args.project_description
  )
  text = update_param_row(text, "PROGRAM_NAME", args.program_name)
  text = update_param_row(text, "PILOT_DOMAIN", args.pilot_domain)
  if args.upcoming_domains:
    pattern_up = re.compile(
        r"^(\|\s*\*\*`UPCOMING_DOMAINS`\*\*\s*\|\s*)([^|]+)(\|.*)$",
        flags=re.MULTILINE,
    )
    text = pattern_up.sub(rf"\g<1>{args.upcoming_domains} \g<3>", text)
  text = update_param_row(text, "EXTERNAL_PARTNERS", args.external_partners)

  # Update Section 2.1 Drive folder rows if provided
  root_id = extract_drive_id(args.root_folder)
  if root_id:
    root_url = format_drive_folder_url(root_id)
    if args.root_folder_name:
      pattern_root_name = re.compile(
          r"(\|\s*\*\*Root Project Drive Folder \(`)([^`]+)(`\)\*\*\s*\|\s*)([^|]+)(\|)",
          flags=re.MULTILINE,
      )
      text = pattern_root_name.sub(
          rf"\g<1>{args.root_folder_name}\g<3>[{root_id}]({root_url}) \g<5>",
          text,
      )
    else:
      pattern_root = re.compile(
          r"(\|\s*\*\*Root Project Drive Folder[^|]*\|\s*)([^|]+)(\|)",
          flags=re.MULTILINE,
      )
      text = pattern_root.sub(rf"\g<1>[{root_id}]({root_url}) \g<3>", text)

  notes_id = extract_drive_id(args.meeting_notes_folder)
  if notes_id:
    notes_url = format_drive_folder_url(notes_id)
    pattern_notes = re.compile(
        r"(\|\s*\*\*Meeting Notes & Recordings Folder\*\*\s*\|\s*)([^|]+)(\|)",
        flags=re.MULTILINE,
    )
    text = pattern_notes.sub(rf"\g<1>[{notes_id}]({notes_url}) \g<3>", text)

  deliv_id = extract_drive_id(args.deliverables_folder)
  if deliv_id:
    deliv_url = format_drive_folder_url(deliv_id)
    pattern_deliv = re.compile(
        r"(\|\s*\*\*Architecture & Deliverables Folder\*\*\s*\|\s*)([^|]+)(\|)",
        flags=re.MULTILINE,
    )
    text = pattern_deliv.sub(rf"\g<1>[{deliv_id}]({deliv_url}) \g<3>", text)

  with open(specs_project_path, "w", encoding="utf-8") as f:
    f.write(text)
  print(f"[Updated] {specs_project_path}")


def parse_root_folder_from_specs_file(
    specs_project_path: str,
) -> Tuple[Optional[str], Optional[str]]:
  """Parse Root Project Drive Folder ID and name from specs/specs_project.md."""
  if not os.path.exists(specs_project_path):
    return None, None
  with open(specs_project_path, "r", encoding="utf-8") as f:
    for line in f:
      if "Root Project Drive Folder" in line and "|" in line:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2:
          name_match = re.search(r"\(`([^`]+)`\)", cells[0])
          folder_name = name_match.group(1) if name_match else None
          folder_id = extract_drive_id(cells[1])
          return folder_id, folder_name
  return None, None


def init_or_update_manifest(
    manifest_path: str,
    specs_project_path: str,
    args: argparse.Namespace,
    workspace_root: str,
) -> Dict:
  """Create or update specs/gdrive_sync_manifest.json synchronized with specs_project.md."""
  spec_root_id, spec_root_name = parse_root_folder_from_specs_file(
      specs_project_path
  )
  cli_root_id = extract_drive_id(args.root_folder)
  root_id = cli_root_id or spec_root_id or "{{DRIVE_ROOT_FOLDER_ID}}"
  root_name = args.root_folder_name or spec_root_name or "20 Project"

  manifest: Dict = {}
  if os.path.exists(manifest_path):
    try:
      with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    except json.JSONDecodeError:
      manifest = {}

  old_root_id = manifest.get("root_folder_id")
  manifest["root_folder_id"] = root_id
  manifest["root_folder_name"] = root_name
  manifest["root_folder_url"] = format_drive_folder_url(root_id)
  manifest.setdefault("last_synced_at", None)

  if old_root_id and old_root_id != root_id and not args.keep_manifest_entries:
    manifest["folders"] = {}
    manifest["documents"] = {}
  else:
    manifest.setdefault("folders", {})
    manifest.setdefault("documents", {})

  if args.discover_drive and root_id and not root_id.startswith("{{"):
    discovered = discover_drive_subfolders(root_id, cwd=workspace_root)
    for k, v in discovered.items():
      manifest["folders"][k] = v
      print(f"[Drive Discovered] {k}/ -> {v['id']}")

  os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
  with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write("\n")
  print(f"[Manifest Ready] {manifest_path} (root_folder_id={root_id})")
  return manifest


def write_gemini_rules(workspace_root: str, force: bool = False) -> None:
  """Create GEMINI.md workspace rules if requested."""
  gemini_path = os.path.join(workspace_root, "GEMINI.md")
  if os.path.exists(gemini_path) and not force:
    print(f"[Skipped Existing] {gemini_path}")
    return
  content = """# Workspace Agent Rules (`GEMINI.md`)

## 1. Project-Specific Configuration (`specs/`)
- Keep customer-specific parameters, Google Drive Folder IDs, Canonical Architectural Domains (`D1..Dn`), and ASR phonetic aliases in [`specs/specs_project.md`](./specs/specs_project.md) and [`specs/gdrive_sync_manifest.json`](./specs/gdrive_sync_manifest.json).
- Never hardcode Google Drive IDs, Google Doc IDs, or customer names inside scripts.

## 2. Portable Relative Paths in Repository Markdown Files
- All internal links across [`specs/`](./specs/) and [`project/`](./project/) (`project/common/`, `project/meetings/`, `project/topics/`) must use portable relative paths (never `file:///` URIs or absolute `/usr/...` filesystem paths inside `.md` files).

## 3. Official Stakeholder Directory Separation
- Maintain speech-to-text (ASR) phonetic aliases and transcript variants **exclusively** in Section 5 of [`specs/specs_project.md`](./specs/specs_project.md). Never include ASR misspellings in [`project/common/project_members.md`](./project/common/project_members.md), which is a clean, customer-facing stakeholder directory.
"""
  with open(gemini_path, "w", encoding="utf-8") as f:
    f.write(content)
  print(f"[Created] {gemini_path}")


def main() -> int:
  parser = argparse.ArgumentParser(
      description=(
          "Scaffold a customer project workspace and customize "
          "specs/specs_project.md and specs/gdrive_sync_manifest.json."
      )
  )
  parser.add_argument(
      "--workspace",
      "-w",
      default=None,
      help="Target workspace root directory (defaults to current working directory)",
  )
  parser.add_argument(
      "--update-config",
      action="store_true",
      help=(
          "Update specs/specs_project.md and specs/gdrive_sync_manifest.json "
          "in-place without overwriting existing project/common/ documents"
      ),
  )
  parser.add_argument(
      "--force",
      action="store_true",
      help="Overwrite existing specs_project.md and project/common/ files from templates",
  )
  parser.add_argument(
      "--customer-name", default=None, help="Customer organization name"
  )
  parser.add_argument(
      "--customer-description",
      default=None,
      help="Short customer industry/domain description",
  )
  parser.add_argument(
      "--customer-domain",
      default=None,
      help="Customer email/web domain (e.g. company.com)",
  )
  parser.add_argument(
      "--project-name", default=None, help="Customer project/platform name"
  )
  parser.add_argument(
      "--project-acronym", default=None, help="Short project acronym (e.g. UDP)"
  )
  parser.add_argument(
      "--project-description",
      default=None,
      help="Short description of the customer project scope",
  )
  parser.add_argument(
      "--program-name",
      default=None,
      help="Umbrella transformation/AI program name",
  )
  parser.add_argument(
      "--pilot-domain",
      default=None,
      help="Initial pilot business/technical domain",
  )
  parser.add_argument(
      "--upcoming-domains",
      default=None,
      help="Comma-separated list of upcoming onboarding domains",
  )
  parser.add_argument(
      "--external-partners",
      default=None,
      help="External system integrators or consulting partners",
  )
  parser.add_argument(
      "--root-folder",
      default=None,
      help="Root Project Google Drive Folder URL or Folder ID",
  )
  parser.add_argument(
      "--root-folder-name",
      default=None,
      help="Display name of the Root Project Drive Folder (default: '20 Project')",
  )
  parser.add_argument(
      "--meeting-notes-folder",
      default=None,
      help="Meeting Notes & Recordings Google Drive Folder URL or ID",
  )
  parser.add_argument(
      "--deliverables-folder",
      default=None,
      help="Architecture & Deliverables Google Drive Folder URL or ID",
  )
  parser.add_argument(
      "--discover-drive",
      action="store_true",
      help="Query Google Drive to auto-discover existing common/, meetings/, and topics/ subfolders",
  )
  parser.add_argument(
      "--keep-manifest-entries",
      action="store_true",
      help="Keep existing folders/documents in gdrive_sync_manifest.json even if root_folder_id changed",
  )
  parser.add_argument(
      "--with-gemini-rules",
      action="store_true",
      help="Also scaffold GEMINI.md workspace rules if not present",
  )

  args = parser.parse_args()
  workspace_root = os.path.abspath(
      os.path.expanduser(args.workspace or os.getcwd())
  )

  # 1. Scaffold required directories
  dirs_to_create = [
      os.path.join(workspace_root, "specs"),
      os.path.join(workspace_root, "project", "common"),
      os.path.join(workspace_root, "project", "meetings"),
      os.path.join(workspace_root, "project", "topics"),
  ]
  for d in dirs_to_create:
    os.makedirs(d, exist_ok=True)
    print(f"[Dir Ready] {os.path.relpath(d, workspace_root)}/")

  specs_project_path = os.path.join(workspace_root, "specs", "specs_project.md")
  manifest_path = os.path.join(
      workspace_root, "specs", "gdrive_sync_manifest.json"
  )

  replacements = build_replacements(args)

  # 2. Create or update specs/specs_project.md
  if os.path.exists(specs_project_path) and not args.force:
    if any([
        args.update_config,
        args.customer_name,
        args.project_name,
        args.program_name,
        args.pilot_domain,
        args.upcoming_domains,
        args.external_partners,
        args.root_folder,
        args.meeting_notes_folder,
        args.deliverables_folder,
    ]):
      update_existing_specs_project(specs_project_path, args)
    else:
      print(f"[Exists] {specs_project_path} (use --update-config or --force)")
  else:
    rendered_specs = render_clean_master_doc(
        "template_specs_project.md", replacements
    )
    with open(specs_project_path, "w", encoding="utf-8") as f:
      f.write(rendered_specs)
    print(f"[Created] {specs_project_path}")

  # 3. Initialize or update specs/gdrive_sync_manifest.json
  init_or_update_manifest(
      manifest_path, specs_project_path, args, workspace_root
  )

  # 4. Initialize the 5 master files in project/common/ (unless --update-config only)
  if not args.update_config:
    master_files_map = {
        "meetings_registry.md": "template_meetings_registry.md",
        "project_members.md": "template_members.md",
        "project_glossary.md": "template_glossary.md",
        "project_questions-log.md": "template_questions-log.md",
        "project_challenges.md": "template_challenges.md",
    }
    for target_name, tpl_name in master_files_map.items():
      target_path = os.path.join(
          workspace_root, "project", "common", target_name
      )
      if os.path.exists(target_path) and not args.force:
        print(f"[Skipped Existing] project/common/{target_name}")
        continue
      content = render_clean_master_doc(tpl_name, replacements)
      with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
      print(f"[Created] project/common/{target_name}")

  if args.with_gemini_rules:
    write_gemini_rules(workspace_root, force=args.force)

  print("\n=== Workspace Setup & Customization Complete ===")
  return 0


if __name__ == "__main__":
  sys.exit(main())
