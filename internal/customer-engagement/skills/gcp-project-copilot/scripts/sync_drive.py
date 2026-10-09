#!/usr/bin/env python3
"""Synchronize a customer workspace's project/ Markdown hierarchy with Google Drive as native Google Docs.

Workspace-agnostic script for the `gcp-project-copilot` skill:
1. Resolves the target customer workspace via `--workspace` / `-w` or by searching
   upward from the current working directory for `specs/specs_project.md`.
2. Reads the Root Project Drive Folder ID dynamically from `specs/specs_project.md`
   or `specs/gdrive_sync_manifest.json` (zero hardcoded IDs).
3. Topologically sorts all `.md` files in `project/` based on their internal
   relative `.md` link dependencies across 3 tiers (`topics/` -> `meetings/` -> `common/`).
4. Rewrites internal relative `.md` links to resolved Google Docs URLs and imports
   or updates each document (`gdocs mutate sync` when open comments exist, or
   `gdocs mutate import-md --update` otherwise).
5. Automatically updates Section 2.2 (`Synchronized Drive Subfolders` and
   `Synchronized Native Google Docs`) in `specs/specs_project.md`.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Set, Tuple

GDRIVE_BIN = "/google/bin/releases/gemini-agents-gdrive/gdrive"
GDOCS_BIN = "/google/bin/releases/gemini-agents-gdocs/gdocs"

RECOGNIZED_CODE_LANGS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "cpp",
    "go",
    "rust",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "scala",
    "r",
    "perl",
    "html",
    "css",
    "xml",
    "json",
    "yaml",
    "sql",
    "bash",
    "sh",
    "shell",
    "proto",
    "lua",
    "haskell",
    "dart",
    "dockerfile",
    "makefile",
    "markdown",
    "mermaid",
    "dot",
    "graphviz",
}


def resolve_workspace_root(cli_workspace: Optional[str] = None) -> str:
  """Resolve target customer workspace root from CLI flag or upward search from cwd."""
  if cli_workspace:
    ws = os.path.abspath(os.path.expanduser(cli_workspace))
    if not os.path.isdir(ws):
      raise RuntimeError(f"Specified workspace directory does not exist: {ws}")
    return ws

  curr = os.path.abspath(os.getcwd())
  while True:
    if os.path.exists(os.path.join(curr, "specs", "specs_project.md")) or (
        os.path.isdir(os.path.join(curr, "project"))
        and os.path.isdir(os.path.join(curr, "specs"))
    ):
      return curr
    parent = os.path.dirname(curr)
    if parent == curr:
      break
    curr = parent

  return os.path.abspath(os.getcwd())


def run_cli(
    args: List[str], cwd: str, check: bool = True
) -> subprocess.CompletedProcess:
  """Execute a CLI command and return the CompletedProcess."""
  proc = subprocess.run(
      args,
      cwd=cwd,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
  )
  if check and proc.returncode != 0:
    raise RuntimeError(
        f"Command failed ({proc.returncode}): {' '.join(args)}\n"
        f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
    )
  return proc


def _is_placeholder_id(candidate: Optional[str]) -> bool:
  """Return True if candidate is empty or a template placeholder."""
  if not candidate:
    return True
  c = candidate.strip()
  return (
      not c
      or "{{" in c
      or "}}" in c
      or c.upper() in ("YOUR_FOLDER_ID", "DRIVE_ROOT_FOLDER_ID", "TBD", "TODO")
  )


def resolve_root_folder_from_specs(
    specs_project_path: str,
    manifest_path: str,
    cli_root_folder_id: Optional[str] = None,
) -> Tuple[str, Optional[str]]:
  """Resolve Root Project Drive Folder ID (and optional display name) from CLI, specs_project.md, or manifest."""
  init_script_path = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "init_workspace.py"
  )
  if cli_root_folder_id:
    raw = cli_root_folder_id.strip()
    url_m = re.search(r"folders/([A-Za-z0-9_-]{15,})", raw)
    resolved = url_m.group(1) if url_m else raw
    if not _is_placeholder_id(resolved):
      return resolved, None

  # 1. Primary source of truth: specs/specs_project.md (Section 2.1 table)
  if os.path.exists(specs_project_path):
    with open(specs_project_path, "r", encoding="utf-8") as f:
      specs_text = f.read()
    for line in specs_text.splitlines():
      if "Root Project Drive Folder" in line and "|" in line:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2:
          label_cell, id_cell = cells[0], cells[1]
          name_match = re.search(r"\(`([^`]+)`\)", label_cell)
          folder_name = (
              name_match.group(1)
              if name_match and not _is_placeholder_id(name_match.group(1))
              else None
          )
          if "{{" in id_cell or "}}" in id_cell:
            break
          url_match = re.search(r"folders/([A-Za-z0-9_-]{15,})", id_cell)
          if url_match and not _is_placeholder_id(url_match.group(1)):
            return url_match.group(1), folder_name
          id_match = re.search(r"\b([A-Za-z0-9_-]{20,})\b", id_cell)
          if id_match and not _is_placeholder_id(id_match.group(1)):
            return id_match.group(1), folder_name

  # 2. Fallback: existing gdrive_sync_manifest.json
  if os.path.exists(manifest_path):
    with open(manifest_path, "r", encoding="utf-8") as f:
      data = json.load(f)
      cand_id = data.get("root_folder_id")
      if not _is_placeholder_id(cand_id):
        return cand_id, data.get("root_folder_name")

  raise RuntimeError(
      "Root Project Drive Folder ID is not configured yet (or still set to a "
      f"template placeholder) in {specs_project_path} and {manifest_path}.\n"
      "Action required: Ask the user for their target Google Drive Folder URL "
      "or ID, then run:\n"
      f"  python3 {init_script_path} --workspace {os.path.dirname(os.path.dirname(specs_project_path))} "
      '--update-config --root-folder "<DRIVE_FOLDER_URL_OR_ID>"'
  )


def load_manifest(
    manifest_path: str,
    root_folder_id: str,
    root_folder_name: Optional[str] = None,
) -> Dict:
  """Load existing sync manifest or initialize a new one if root_folder_id changed."""
  if os.path.exists(manifest_path):
    with open(manifest_path, "r", encoding="utf-8") as f:
      data = json.load(f)
    if data.get("root_folder_id") == root_folder_id:
      if root_folder_name and not data.get("root_folder_name"):
        data["root_folder_name"] = root_folder_name
      data.setdefault("folders", {})
      data.setdefault("documents", {})
      return data
  return {
      "root_folder_id": root_folder_id,
      "root_folder_name": root_folder_name or "Root Project Drive Folder",
      "root_folder_url": f"https://drive.google.com/drive/folders/{root_folder_id}",
      "last_synced_at": None,
      "folders": {},
      "documents": {},
  }


def save_manifest(manifest_path: str, manifest: Dict) -> None:
  """Persist the sync manifest to disk."""
  os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
  manifest["last_synced_at"] = (
      datetime.datetime.now(datetime.timezone.utc)
      .replace(microsecond=0)
      .isoformat()
  )
  with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write("\n")


def list_drive_children(parent_id: str, cwd: str) -> List[Dict]:
  """List children in a Google Drive folder using gdrive readonly ls --json."""
  proc = run_cli(
      [GDRIVE_BIN, "readonly", "ls", parent_id, "--max", "200", "--json"],
      cwd=cwd,
      check=False,
  )
  if proc.returncode != 0 or not proc.stdout.strip():
    return []
  try:
    parsed = json.loads(proc.stdout)
    if isinstance(parsed, list):
      return parsed
    if isinstance(parsed, dict) and "files" in parsed:
      return parsed["files"]
  except json.JSONDecodeError:
    pass
  return []


def extract_id_from_output(output: str) -> Optional[str]:
  """Extract a Drive folder or Doc ID from CLI stdout/stderr."""
  patterns = [
      r"https://docs\.google\.com/document/d/([A-Za-z0-9_-]{20,})",
      r"https://drive\.google\.com/(?:corp/)?drive/folders/([A-Za-z0-9_-]{20,})",
      r'"(?:documentId|id)"\s*:\s*"([A-Za-z0-9_-]{20,})"',
      r"(?:Document ID|Folder ID|ID)\s*:\s*([A-Za-z0-9_-]{20,})",
      r"\(([A-Za-z0-9_-]{25,})\)",
  ]
  for pat in patterns:
    m = re.search(pat, output)
    if m:
      return m.group(1)
  return None


def ensure_folder(
    rel_dir: str,
    parent_id: str,
    manifest: Dict,
    manifest_path: str,
    cwd: str,
    dry_run: bool = False,
) -> str:
  """Ensure a subfolder exists in Drive under parent_id and return its folder ID."""
  if rel_dir in manifest["folders"] and manifest["folders"][rel_dir].get("id"):
    folder_id = manifest["folders"][rel_dir]["id"]
    print(f"[Folder OK] {rel_dir} -> {folder_id}")
    return folder_id

  folder_name = os.path.basename(rel_dir)
  if dry_run:
    fake_id = f"DRYRUN_FOLDER_{rel_dir.replace('/', '_')}"
    manifest["folders"][rel_dir] = {
        "id": fake_id,
        "name": folder_name,
        "parent_id": parent_id,
        "url": f"https://drive.google.com/drive/folders/{fake_id}",
    }
    print(f"[DryRun Folder Create] {rel_dir} under {parent_id}")
    return fake_id

  children = list_drive_children(parent_id, cwd=cwd)
  for child in children:
    c_name = child.get("name") or child.get("Name")
    c_mime = child.get("mimeType") or child.get("MimeType") or child.get("Type")
    c_id = child.get("id") or child.get("ID")
    if c_name == folder_name and c_id and ("folder" in str(c_mime).lower()):
      manifest["folders"][rel_dir] = {
          "id": c_id,
          "name": folder_name,
          "parent_id": parent_id,
          "url": f"https://drive.google.com/drive/folders/{c_id}",
      }
      save_manifest(manifest_path, manifest)
      print(f"[Folder Found] {rel_dir} -> {c_id}")
      return c_id

  proc = run_cli(
      [GDRIVE_BIN, "mutate", "mkdir", folder_name, "--parent", parent_id],
      cwd=cwd,
  )
  folder_id = extract_id_from_output(proc.stdout + "\n" + proc.stderr)
  if not folder_id:
    children = list_drive_children(parent_id, cwd=cwd)
    for child in children:
      c_name = child.get("name") or child.get("Name")
      c_id = child.get("id") or child.get("ID")
      if c_name == folder_name and c_id:
        folder_id = c_id
        break
  if not folder_id:
    raise RuntimeError(
        f"Failed to extract folder ID after mkdir for {rel_dir}: {proc.stdout}"
    )

  manifest["folders"][rel_dir] = {
      "id": folder_id,
      "name": folder_name,
      "parent_id": parent_id,
      "url": f"https://drive.google.com/drive/folders/{folder_id}",
  }
  save_manifest(manifest_path, manifest)
  print(f"[Folder Created] {rel_dir} -> {folder_id}")
  return folder_id


def extract_internal_md_dependencies(
    project_dir: str, rel_path: str, all_md_set: Set[str]
) -> Set[str]:
  """Return the set of project-relative .md files that `rel_path` links to."""
  abs_path = os.path.join(project_dir, rel_path)
  base_dir = os.path.dirname(abs_path)
  deps: Set[str] = set()
  link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
  try:
    with open(abs_path, "r", encoding="utf-8") as f:
      text = f.read()
  except OSError:
    return deps

  for match in link_pattern.finditer(text):
    target = match.group(1).strip()
    if target.startswith(
        ("http://", "https://", "mailto:", "#", "conversation://")
    ):
      continue
    target_path = target.split("#")[0]
    if not target_path:
      continue
    abs_target = os.path.normpath(os.path.join(base_dir, target_path))
    if abs_target.startswith(project_dir + os.sep):
      target_rel = os.path.relpath(abs_target, project_dir)
      if target_rel in all_md_set and target_rel != rel_path:
        deps.add(target_rel)
  return deps


def collect_ordered_markdown_files(project_dir: str) -> List[str]:
  """Return all .md files under project/ sorted in 3-tier & topological link-dependency order."""
  all_md: List[str] = []
  for dirpath, _, filenames in os.walk(project_dir):
    for fn in sorted(filenames):
      if fn.endswith(".md") and not fn.endswith("-gdoc-tmp.md"):
        rel = os.path.relpath(os.path.join(dirpath, fn), project_dir)
        all_md.append(rel)

  all_md_set = set(all_md)
  deps_map: Dict[str, Set[str]] = {
      rel: extract_internal_md_dependencies(project_dir, rel, all_md_set)
      for rel in all_md
  }

  def base_priority(rel_path: str) -> Tuple[int, int, str]:
    # Tier 1: topics/
    if rel_path.startswith("topics/"):
      return (1, 1, rel_path)
    # Tier 2: meetings/ (challenges before questions-log)
    if rel_path.startswith("meetings/"):
      if "_challenges_" in rel_path:
        return (2, 1, rel_path)
      return (2, 2, rel_path)
    # Tier 3: common/ in standard dependency order
    common_order = {
        "common/project_glossary.md": 1,
        "common/project_members.md": 2,
        "common/project_challenges.md": 3,
        "common/project_questions-log.md": 4,
        "common/meetings_registry.md": 5,
    }
    return (3, common_order.get(rel_path, 9), rel_path)

  # Deterministic topological sort respecting base_priority as tie-breaker
  ordered: List[str] = []
  visited: Set[str] = set()
  visiting: Set[str] = set()

  def visit(node: str) -> None:
    if node in visited:
      return
    if node in visiting:
      # Cycle detected; break cycle gracefully
      return
    visiting.add(node)
    for dep in sorted(deps_map.get(node, set()), key=base_priority):
      visit(dep)
    visiting.remove(node)
    visited.add(node)
    ordered.append(node)

  for rel in sorted(all_md, key=base_priority):
    visit(rel)

  return ordered


def preprocess_markdown_for_gdocs(
    workspace_root: str, project_dir: str, rel_path: str, manifest: Dict
) -> Tuple[str, Dict[str, str]]:
  """Preprocess local Markdown content for clean Google Docs import.

  Rewrites internal relative .md links to their resolved Google Docs URLs,
  converts GitHub alerts to bold callouts, removes standalone --- dividers,
  ensures blank lines before tables, and normalizes code fence language tags.
  """
  abs_path = os.path.join(project_dir, rel_path)
  base_dir = os.path.dirname(abs_path)
  with open(abs_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

  resolved_links: Dict[str, str] = {}
  link_pattern = re.compile(r"(\[[^\]]+\])\(([^)]+)\)")

  def replace_link(match: re.Match) -> str:
    label = match.group(1)
    target = match.group(2).strip()
    if target.startswith(
        ("http://", "https://", "mailto:", "#", "conversation://")
    ):
      return match.group(0)
    target_path = target.split("#")[0]
    if not target_path:
      return match.group(0)

    abs_target = os.path.normpath(os.path.join(base_dir, target_path))
    if abs_target.startswith(project_dir + os.sep):
      target_rel = os.path.relpath(abs_target, project_dir)
      if target_rel in manifest["documents"]:
        doc_url = manifest["documents"][target_rel]["url"]
        resolved_links[target] = doc_url
        return f"{label}({doc_url})"
      if target_rel in manifest["folders"]:
        folder_url = manifest["folders"][target_rel]["url"]
        resolved_links[target] = folder_url
        return f"{label}({folder_url})"
    elif abs_target.startswith(os.path.join(workspace_root, "specs")):
      root_url = manifest["root_folder_url"]
      resolved_links[target] = root_url
      return f"{label}({root_url})"
    return match.group(0)

  lines = raw_text.splitlines()
  out_lines: List[str] = []
  in_code_block = False

  alert_map = {
      "NOTE": "Note:",
      "IMPORTANT": "Important:",
      "TIP": "Tip:",
      "WARNING": "Warning:",
      "CAUTION": "Caution:",
  }

  for line in lines:
    stripped = line.strip()
    if stripped.startswith("```"):
      if not in_code_block:
        in_code_block = True
        lang = stripped[3:].strip().lower()
        if not lang or lang not in RECOGNIZED_CODE_LANGS:
          indent = line[: len(line) - len(line.lstrip())]
          out_lines.append(f"{indent}```go")
        else:
          out_lines.append(line)
      else:
        in_code_block = False
        indent = line[: len(line) - len(line.lstrip())]
        out_lines.append(f"{indent}```")
      continue

    if in_code_block:
      out_lines.append(line)
      continue

    # Remove standalone horizontal rule ---
    if re.match(r"^\s*---\s*$", line):
      out_lines.append("")
      continue

    # Convert GitHub-style alerts (> [!NOTE] etc.)
    alert_match = re.match(
        r"^(\s*>\s*)\[!(NOTE|IMPORTANT|TIP|WARNING|CAUTION)\]\s*(.*)$",
        line,
        flags=re.IGNORECASE,
    )
    if alert_match:
      prefix, kind, rest = alert_match.groups()
      label = alert_map.get(kind.upper(), "Note:")
      line = f"{prefix}**{label}** {rest}".rstrip()

    # Rewrite relative links
    line = link_pattern.sub(replace_link, line)

    # Ensure blank line before table start
    if stripped.startswith("|") and stripped.endswith("|"):
      if out_lines and out_lines[-1].strip() != "" and not (
          out_lines[-1].strip().startswith("|")
          and out_lines[-1].strip().endswith("|")
      ):
        out_lines.append("")

    out_lines.append(line)

  processed = "\n".join(out_lines) + "\n"
  return processed, resolved_links


def has_open_comments(doc_id: str, cwd: str) -> bool:
  """Check if an existing Google Doc has unresolved comments."""
  proc = run_cli(
      [GDOCS_BIN, "readonly", "list-comments", doc_id, "--open-only", "--json"],
      cwd=cwd,
      check=False,
  )
  if proc.returncode != 0 or not proc.stdout.strip():
    return False
  try:
    data = json.loads(proc.stdout)
    if isinstance(data, list) and len(data) > 0:
      return True
    if isinstance(data, dict) and data.get("comments"):
      return True
  except json.JSONDecodeError:
    pass
  return False


def get_canonical_doc_url(doc_id: str, cwd: str) -> str:
  """Get the shareable URL for a Google Doc via gdocs readonly get-url."""
  proc = run_cli(
      [GDOCS_BIN, "readonly", "get-url", doc_id], cwd=cwd, check=False
  )
  for line in (proc.stdout + "\n" + proc.stderr).splitlines():
    line = line.strip()
    if line.startswith("https://docs.google.com/document/d/"):
      return line
  return f"https://docs.google.com/document/d/{doc_id}/edit"


def sync_document(
    workspace_root: str,
    project_dir: str,
    rel_path: str,
    manifest: Dict,
    manifest_path: str,
    force: bool = False,
    dry_run: bool = False,
) -> None:
  """Import or update a single Markdown file into Google Drive as a Google Doc."""
  processed_md, resolved_links = preprocess_markdown_for_gdocs(
      workspace_root, project_dir, rel_path, manifest
  )
  content_hash = hashlib.sha256(processed_md.encode("utf-8")).hexdigest()

  rel_dir = os.path.dirname(rel_path)
  parent_folder_id = (
      manifest["root_folder_id"]
      if rel_dir == ""
      else manifest["folders"][rel_dir]["id"]
  )
  doc_title = os.path.splitext(os.path.basename(rel_path))[0]

  existing = manifest["documents"].get(rel_path)
  if existing and existing.get("id") and not force:
    if existing.get("sha256") == content_hash:
      print(f"[Doc Up-to-Date] {rel_path} -> {existing['id']}")
      return

  if dry_run:
    action = "Update" if existing else "Import"
    fake_doc_id = f"DRYRUN_DOC_{doc_title}"
    manifest["documents"][rel_path] = {
        "id": fake_doc_id,
        "title": doc_title,
        "parent_folder": rel_dir,
        "parent_folder_id": parent_folder_id,
        "url": f"https://docs.google.com/document/d/{fake_doc_id}/edit",
        "sha256": content_hash,
    }
    print(
        f"[DryRun Doc {action}] {rel_path} (title='{doc_title}', "
        f"parent={parent_folder_id}, links_rewritten={len(resolved_links)})"
    )
    return

  abs_path = os.path.join(project_dir, rel_path)
  tmp_md_path = os.path.join(
      os.path.dirname(abs_path), f"{doc_title}-gdoc-tmp.md"
  )
  try:
    with open(tmp_md_path, "w", encoding="utf-8") as f:
      f.write(processed_md)

    if existing and existing.get("id"):
      doc_id = existing["id"]
      if has_open_comments(doc_id, cwd=workspace_root):
        print(f"[Doc Sync (preserving comments)] {rel_path} -> {doc_id}")
        run_cli(
            [GDOCS_BIN, "mutate", "sync", doc_id, tmp_md_path],
            cwd=workspace_root,
        )
      else:
        print(f"[Doc Update] {rel_path} -> {doc_id}")
        run_cli(
            [
                GDOCS_BIN,
                "mutate",
                "import-md",
                tmp_md_path,
                "--update",
                doc_id,
                "--pageless",
            ],
            cwd=workspace_root,
        )
      doc_url = existing.get("url") or get_canonical_doc_url(
          doc_id, cwd=workspace_root
      )
    else:
      print(f"[Doc Import] {rel_path} -> title='{doc_title}'")
      proc = run_cli(
          [
              GDOCS_BIN,
              "mutate",
              "import-md",
              tmp_md_path,
              "--title",
              doc_title,
              "--pageless",
          ],
          cwd=workspace_root,
      )
      doc_id = extract_id_from_output(proc.stdout + "\n" + proc.stderr)
      if not doc_id:
        raise RuntimeError(
            f"Could not extract Document ID from import-md output for {rel_path}:\n"
            f"{proc.stdout}\n{proc.stderr}"
        )
      run_cli(
          [GDRIVE_BIN, "mutate", "mv", doc_id, parent_folder_id],
          cwd=workspace_root,
      )
      doc_url = get_canonical_doc_url(doc_id, cwd=workspace_root)
      print(
          f"[Doc Imported & Moved] {rel_path} -> {doc_id} (folder {parent_folder_id})"
      )

    manifest["documents"][rel_path] = {
        "id": doc_id,
        "title": doc_title,
        "parent_folder": rel_dir,
        "parent_folder_id": parent_folder_id,
        "url": doc_url,
        "sha256": content_hash,
        "resolved_links_count": len(resolved_links),
        "updated_at": (
            datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
        ),
    }
    save_manifest(manifest_path, manifest)
  finally:
    if os.path.exists(tmp_md_path):
      os.remove(tmp_md_path)


def update_specs_project_registry(
    specs_project_path: str, manifest: Dict
) -> bool:
  """Update Section 2.2 (Subfolders & Native Google Docs tables) in specs/specs_project.md."""
  if not os.path.exists(specs_project_path):
    return False

  with open(specs_project_path, "r", encoding="utf-8") as f:
    original_text = f.read()

  root_name = manifest.get("root_folder_name") or "20 Project"
  folders = manifest.get("folders", {})
  documents = manifest.get("documents", {})

  # Build Table A: Synchronized Drive Subfolders
  folder_lines = [
      f"#### A. Synchronized Drive Subfolders (Under `{root_name}`)",
      "",
      "| Local Directory (`project/...`) | Google Drive Folder Link | Parent Folder |",
      "| :--- | :--- | :--- |",
  ]
  for rel_dir in sorted(folders.keys()):
    f_info = folders[rel_dir]
    f_id = f_info.get("id", "")
    f_url = f_info.get("url", f"https://drive.google.com/drive/folders/{f_id}")
    parent_rel = os.path.dirname(rel_dir)
    parent_label = f"`{root_name}`" if not parent_rel else f"`{parent_rel}/`"
    folder_lines.append(
        f"| `{rel_dir}/` | [`{f_id}`]({f_url}) | {parent_label} |"
    )

  # Build Table B: Synchronized Native Google Docs
  def doc_display_sort_key(rel_path: str) -> Tuple[int, int, str]:
    if rel_path.startswith("common/"):
      common_display_order = {
          "common/meetings_registry.md": 1,
          "common/project_members.md": 2,
          "common/project_glossary.md": 3,
          "common/project_questions-log.md": 4,
          "common/project_challenges.md": 5,
      }
      return (1, common_display_order.get(rel_path, 9), rel_path)
    if rel_path.startswith("meetings/"):
      sub_order = 1 if "_questions-log_" in rel_path else 2
      return (2, sub_order, rel_path)
    if rel_path.startswith("topics/"):
      return (3, 1, rel_path)
    return (4, 1, rel_path)

  # Sort meetings grouped by folder, with questions-log before challenges
  def doc_table_key(rel_path: str) -> Tuple[int, str, int, str]:
    if rel_path.startswith("common/"):
      common_display_order = {
          "common/meetings_registry.md": 1,
          "common/project_members.md": 2,
          "common/project_glossary.md": 3,
          "common/project_questions-log.md": 4,
          "common/project_challenges.md": 5,
      }
      return (1, "", common_display_order.get(rel_path, 9), rel_path)
    if rel_path.startswith("meetings/"):
      folder = os.path.dirname(rel_path)
      sub = 1 if "_questions-log_" in rel_path else 2
      return (2, folder, sub, rel_path)
    if rel_path.startswith("topics/"):
      return (3, os.path.dirname(rel_path), 1, rel_path)
    return (4, os.path.dirname(rel_path), 1, rel_path)

  sorted_docs = sorted(documents.keys(), key=doc_table_key)
  doc_lines = [
      f"#### B. Synchronized Native Google Docs ({len(sorted_docs)} Documents)",
      "",
      "| Layer / Scope | Local Markdown Source (`project/...`) | Synchronized Google Doc |",
      "| :--- | :--- | :--- |",
  ]
  for rel_path in sorted_docs:
    d_info = documents[rel_path]
    d_title = d_info.get("title") or os.path.splitext(os.path.basename(rel_path))[0]
    d_url = d_info.get("url", "")
    if rel_path.startswith("common/"):
      layer_label = "**Layer 1 (`common/`)**"
    elif rel_path.startswith("meetings/"):
      layer_label = "**Layer 2 (`meetings/`)**"
    elif rel_path.startswith("topics/"):
      layer_label = "**Layer 3 (`topics/`)**"
    else:
      layer_label = "**Project (`project/`)**"
    doc_lines.append(
        f"| {layer_label} | [`{rel_path}`](../project/{rel_path}) | [{d_title}]({d_url}) |"
    )

  replacement_block = (
      "\n".join(folder_lines) + "\n\n" + "\n".join(doc_lines) + "\n"
  )

  pattern = re.compile(
      r"(#### A\. Synchronized Drive Subfolders.*?)(?=\n## 3\.|\Z)",
      flags=re.DOTALL,
  )
  if not pattern.search(original_text):
    return False

  updated_text = pattern.sub(replacement_block + "\n", original_text, count=1)
  if updated_text != original_text:
    with open(specs_project_path, "w", encoding="utf-8") as f:
      f.write(updated_text)
    print(f"[Specs Updated] Refreshed Section 2.2 in {specs_project_path}")
    return True
  return False


def main() -> int:
  parser = argparse.ArgumentParser(
      description="Synchronize local project/ folder with Google Drive as native Google Docs."
  )
  parser.add_argument(
      "--workspace",
      "-w",
      default=None,
      help=(
          "Target customer workspace root directory "
          "(defaults to auto-detecting upward from current working directory)"
      ),
  )
  parser.add_argument(
      "--root-folder-id",
      default=None,
      help=(
          "Optional Root Project Drive Folder ID override "
          "(defaults to parsing Section 2.1 of specs/specs_project.md)"
      ),
  )
  parser.add_argument(
      "--force",
      action="store_true",
      help="Force re-import/update even if SHA-256 matches",
  )
  parser.add_argument(
      "--dry-run",
      action="store_true",
      help="Print actions without calling gdrive/gdocs mutate commands",
  )
  parser.add_argument(
      "--no-update-specs",
      action="store_true",
      help="Skip automatic update of Section 2.2 in specs/specs_project.md",
  )
  args = parser.parse_args()

  workspace_root = resolve_workspace_root(args.workspace)
  project_dir = os.path.join(workspace_root, "project")
  specs_project_path = os.path.join(workspace_root, "specs", "specs_project.md")
  manifest_path = os.path.join(
      workspace_root, "specs", "gdrive_sync_manifest.json"
  )

  if not os.path.isdir(project_dir):
    raise RuntimeError(
        f"Project directory not found at {project_dir}. "
        "Pass --workspace <path> pointing to a valid customer workspace."
    )

  root_folder_id, root_folder_name = resolve_root_folder_from_specs(
      specs_project_path, manifest_path, args.root_folder_id
  )
  manifest = load_manifest(manifest_path, root_folder_id, root_folder_name)

  # 1. Discover all directories under project/ in top-down order
  rel_dirs: List[str] = []
  for dirpath, dirnames, _ in os.walk(project_dir):
    dirnames.sort()
    rel = os.path.relpath(dirpath, project_dir)
    if rel != ".":
      rel_dirs.append(rel)

  print(f"=== Target Workspace: {workspace_root} ===")
  print(f"=== Phase 1: Ensuring {len(rel_dirs)} Folders under {root_folder_id} ===")
  for rel_dir in rel_dirs:
    parent_rel = os.path.dirname(rel_dir)
    parent_id = (
        root_folder_id
        if parent_rel == ""
        else manifest["folders"][parent_rel]["id"]
    )
    ensure_folder(
        rel_dir,
        parent_id,
        manifest,
        manifest_path,
        cwd=workspace_root,
        dry_run=args.dry_run,
    )

  # 2. Collect and sync all Markdown files in topological dependency order
  ordered_files = collect_ordered_markdown_files(project_dir)
  print(f"\n=== Phase 2: Synchronizing {len(ordered_files)} Markdown Documents ===")
  for rel_path in ordered_files:
    sync_document(
        workspace_root,
        project_dir,
        rel_path,
        manifest,
        manifest_path,
        force=args.force,
        dry_run=args.dry_run,
    )

  # 3. Auto-update Section 2.2 in specs/specs_project.md
  if not args.dry_run and not args.no_update_specs:
    update_specs_project_registry(specs_project_path, manifest)

  print("\n=== Synchronization Complete ===")
  print(f"Manifest saved to: {manifest_path}")
  return 0


if __name__ == "__main__":
  sys.exit(main())

