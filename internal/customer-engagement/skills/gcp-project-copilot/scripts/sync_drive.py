#!/usr/bin/env python3
"""Synchronize a customer workspace's project/ Markdown hierarchy with Google Drive as native Google Docs.

Workspace-agnostic script for the `gcp-project-copilot` skill:
1. Resolves the target customer workspace via `--workspace` / `-w` or by searching
   upward from the current working directory for `specs/specs_project.md`.
2. Reads the Root Project Drive Folder ID dynamically from `specs/specs_project.md`
   or `specs/gdrive_sync_manifest.json` (zero hardcoded IDs).
3. Partitions `.md` files in `project/` into topological link-dependency waves:
   existing documents (whose Google Doc IDs/URLs are already in the manifest) run
   concurrently in Wave 0 across `--jobs` workers (default: 6), while brand-new
   documents execute wave-by-wave (`topics/` & leaf `questions/` -> `meetings/` ->
   `common/`) so internal relative `.md` links always resolve to real Google Docs URLs.
4. Prefetches open-comment status across dirty documents in a single concurrent
   `gdocs readonly stream comments --open-only` batch call, preserves comments via
   `gdocs mutate sync` when open comments exist, and uses fast `gdocs mutate import-md`
   (with automatic retry/backoff on transient `429`/`503` errors) otherwise.
5. Automatically updates Section 2.2 (`Synchronized Drive Subfolders`,
   `Synchronized Native Google Docs`, and `Synchronized Diagram & Spec Assets`)
   in `specs/specs_project.md`.
"""

import argparse
import atexit
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import hashlib
import json
import os
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

GDRIVE_BIN = "/google/bin/releases/gemini-agents-gdrive/gdrive"
GDOCS_BIN = "/google/bin/releases/gemini-agents-gdocs/gdocs"

DEFAULT_JOBS = 6

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

SIMPLE_INLINE_MATH_MAP = {
    r"\rightarrow": "→",
    r"\to": "→",
    r"\leftarrow": "←",
    r"\leftrightarrow": "↔",
    r"\Rightarrow": "⇒",
    r"\Leftarrow": "⇐",
    r"\Leftrightarrow": "⇔",
    r"\times": "×",
    r"\le": "≤",
    r"\leq": "≤",
    r"\ge": "≥",
    r"\geq": "≥",
    r"\ne": "≠",
    r"\neq": "≠",
    r"\approx": "≈",
    r"\pm": "±",
    r"\subset": "⊂",
    r"\subseteq": "⊆",
    r"\in": "∈",
    r"\cap": "∩",
    r"\cup": "∪",
    r"\bowtie": "⋈",
    r"\infty": "∞",
}

TRANSIENT_CLI_RE = re.compile(
    r"(?:"
    r"\b429\b|rateLimitExceeded|userRateLimitExceeded|RATE_LIMIT_EXCEEDED|"
    r"Quota exceeded|ResourceExhausted|DEADLINE_EXCEEDED|UNAVAILABLE|"
    r"500 Internal|502 Bad Gateway|503 Service Unavailable|504 Gateway|"
    r"Internal Error|backendError|connection reset by peer|TLS handshake timeout"
    r")",
    flags=re.IGNORECASE,
)

PRINT_LOCK = threading.Lock()
MANIFEST_LOCK = threading.Lock()
FOLDER_CACHE_LOCK = threading.Lock()
TEMP_LOCK = threading.Lock()

FOLDER_CHILDREN_CACHE: Dict[str, List[Dict]] = {}
ACTIVE_TEMP_PATHS: Set[str] = set()
ACTIVE_CHECKPOINTER: Optional["ManifestCheckpointer"] = None


def log_line(msg: str) -> None:
  """Thread-safe line logger with immediate stdout flush."""
  with PRINT_LOCK:
    print(msg, flush=True)


def register_temp_path(path: str) -> None:
  with TEMP_LOCK:
    ACTIVE_TEMP_PATHS.add(path)


def unregister_and_remove_temp_path(path: str) -> None:
  with TEMP_LOCK:
    ACTIVE_TEMP_PATHS.discard(path)
  try:
    if os.path.exists(path):
      os.remove(path)
  except OSError:
    pass


def cleanup_all_active_temps() -> None:
  """Remove any in-flight temporary staging files on exit or signal."""
  with TEMP_LOCK:
    paths = list(ACTIVE_TEMP_PATHS)
    ACTIVE_TEMP_PATHS.clear()
  for path in paths:
    try:
      if os.path.exists(path):
        os.remove(path)
    except OSError:
      pass


def sweep_stale_temp_files(project_dir: str) -> int:
  """Sweep any leftover *-gdoc-tmp.* staging files from prior interrupted runs."""
  removed = 0
  if not os.path.isdir(project_dir):
    return 0
  for dirpath, _, filenames in os.walk(project_dir):
    for fn in filenames:
      if "-gdoc-tmp." in fn or fn.endswith("-gdoc-tmp.md"):
        stale = os.path.join(dirpath, fn)
        try:
          os.remove(stale)
          removed += 1
        except OSError:
          pass
  return removed


class ManifestCheckpointer:
  """Thread-safe coalesced atomic writer for gdrive_sync_manifest.json."""

  def __init__(self, manifest_path: str, manifest: Dict, flush_every: int = 5):
    self.manifest_path = manifest_path
    self.manifest = manifest
    self.flush_every = max(1, flush_every)
    self._dirty_count = 0

  def record_mutation(self, force_flush: bool = False) -> None:
    with MANIFEST_LOCK:
      self._dirty_count += 1
      if force_flush or self._dirty_count >= self.flush_every:
        self._write_locked()
        self._dirty_count = 0

  def flush(self) -> None:
    with MANIFEST_LOCK:
      if self._dirty_count > 0:
        self._write_locked()
        self._dirty_count = 0

  def _write_locked(self) -> None:
    os.makedirs(os.path.dirname(self.manifest_path), exist_ok=True)
    self.manifest["last_synced_at"] = (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )
    tmp_path = (
        f"{self.manifest_path}.tmp.{os.getpid()}.{threading.get_ident()}"
    )
    try:
      with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
      os.replace(tmp_path, self.manifest_path)
    finally:
      if os.path.exists(tmp_path):
        try:
          os.remove(tmp_path)
        except OSError:
          pass


def _install_signal_handlers() -> None:
  atexit.register(cleanup_all_active_temps)

  def _handle_signal(signum: int, _frame) -> None:
    cleanup_all_active_temps()
    if ACTIVE_CHECKPOINTER is not None:
      try:
        ACTIVE_CHECKPOINTER.flush()
      except Exception:  # pylint: disable=broad-except
        pass
    sys.exit(128 + signum)

  for sig in (signal.SIGINT, signal.SIGTERM):
    try:
      signal.signal(sig, _handle_signal)
    except (ValueError, OSError):
      pass


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
    args: List[str],
    cwd: str,
    check: bool = True,
    max_retries: int = 3,
) -> subprocess.CompletedProcess:
  """Execute a CLI command with exponential backoff retry on transient quota/server errors."""
  attempt = 0
  while True:
    try:
      proc = subprocess.run(
          args,
          cwd=cwd,
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE,
          text=True,
      )
    except OSError as exc:
      if getattr(exc, "errno", None) == 126:
        raise RuntimeError(
            f"LOAS certificate expired while accessing '{args[0]}' (Errno 126: Required key not available). "
            "Please run `gcert` in your terminal and retry."
        ) from exc
      raise
    if proc.returncode == 0:
      return proc

    combined = f"{proc.stdout}\n{proc.stderr}"
    if attempt < max_retries and TRANSIENT_CLI_RE.search(combined):
      delay = (2.0 ** attempt) * 1.5 + random.uniform(0.15, 0.85)
      log_line(
          f"[Retry {attempt + 1}/{max_retries}] Transient API error on "
          f"'{' '.join(args[:4])}...', sleeping {delay:.1f}s"
      )
      time.sleep(delay)
      attempt += 1
      continue

    if check:
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
      data.setdefault("assets", {})
      return data
  return {
      "root_folder_id": root_folder_id,
      "root_folder_name": root_folder_name or "Root Project Drive Folder",
      "root_folder_url": f"https://drive.google.com/drive/folders/{root_folder_id}",
      "last_synced_at": None,
      "folders": {},
      "documents": {},
      "assets": {},
  }


def save_manifest(manifest_path: str, manifest: Dict) -> None:
  """Persist the sync manifest atomically to disk."""
  checkpointer = ManifestCheckpointer(manifest_path, manifest, flush_every=1)
  checkpointer.record_mutation(force_flush=True)


def invalidate_folder_cache(parent_id: str) -> None:
  with FOLDER_CACHE_LOCK:
    FOLDER_CHILDREN_CACHE.pop(parent_id, None)


def list_drive_children(
    parent_id: str, cwd: str, use_cache: bool = True
) -> List[Dict]:
  """List children in a Google Drive folder using gdrive readonly ls --json with per-parent caching."""
  if use_cache:
    with FOLDER_CACHE_LOCK:
      if parent_id in FOLDER_CHILDREN_CACHE:
        return list(FOLDER_CHILDREN_CACHE[parent_id])

  proc = run_cli(
      [GDRIVE_BIN, "readonly", "ls", parent_id, "--max", "500", "--json"],
      cwd=cwd,
      check=False,
  )
  items: List[Dict] = []
  if proc.returncode == 0 and proc.stdout.strip():
    try:
      parsed = json.loads(proc.stdout)
      if isinstance(parsed, list):
        items = parsed
      elif isinstance(parsed, dict) and "files" in parsed:
        items = parsed["files"]
    except json.JSONDecodeError:
      pass

  if proc.returncode == 0:
    with FOLDER_CACHE_LOCK:
      FOLDER_CHILDREN_CACHE[parent_id] = list(items)
  return items


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
    checkpointer: ManifestCheckpointer,
    cwd: str,
    dry_run: bool = False,
) -> str:
  """Ensure a subfolder exists in Drive under parent_id and return its folder ID."""
  with MANIFEST_LOCK:
    existing_folder = manifest["folders"].get(rel_dir)
    if existing_folder and existing_folder.get("id"):
      folder_id = existing_folder["id"]
      log_line(f"[Folder OK] {rel_dir} -> {folder_id}")
      return folder_id

  folder_name = os.path.basename(rel_dir)
  if dry_run:
    fake_id = f"DRYRUN_FOLDER_{rel_dir.replace('/', '_')}"
    with MANIFEST_LOCK:
      manifest["folders"][rel_dir] = {
          "id": fake_id,
          "name": folder_name,
          "parent_id": parent_id,
          "url": f"https://drive.google.com/drive/folders/{fake_id}",
      }
    log_line(f"[DryRun Folder Create] {rel_dir} under {parent_id}")
    return fake_id

  children = list_drive_children(parent_id, cwd=cwd, use_cache=True)
  for child in children:
    c_name = child.get("name") or child.get("Name")
    c_mime = child.get("mimeType") or child.get("MimeType") or child.get("Type")
    c_id = child.get("id") or child.get("ID")
    if c_name == folder_name and c_id and ("folder" in str(c_mime).lower()):
      with MANIFEST_LOCK:
        manifest["folders"][rel_dir] = {
            "id": c_id,
            "name": folder_name,
            "parent_id": parent_id,
            "url": f"https://drive.google.com/drive/folders/{c_id}",
        }
      checkpointer.record_mutation()
      log_line(f"[Folder Found] {rel_dir} -> {c_id}")
      return c_id

  proc = run_cli(
      [GDRIVE_BIN, "mutate", "mkdir", folder_name, "--parent", parent_id],
      cwd=cwd,
  )
  invalidate_folder_cache(parent_id)
  folder_id = extract_id_from_output(proc.stdout + "\n" + proc.stderr)
  if not folder_id:
    children = list_drive_children(parent_id, cwd=cwd, use_cache=False)
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

  with MANIFEST_LOCK:
    manifest["folders"][rel_dir] = {
        "id": folder_id,
        "name": folder_name,
        "parent_id": parent_id,
        "url": f"https://drive.google.com/drive/folders/{folder_id}",
    }
  checkpointer.record_mutation()
  log_line(f"[Folder Created] {rel_dir} -> {folder_id}")
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


def doc_tier_priority(rel_path: str) -> Tuple[int, int, str]:
  """Return (tier, sub_order, rel_path) for the 3-tier knowledge base hierarchy."""
  # Tier 1: topics/ and questions/ (synced before meetings/ and common/ so hub links resolve)
  if rel_path.startswith("topics/"):
    return (1, 1, rel_path)
  if rel_path.startswith("questions/"):
    return (1, 2, rel_path)
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


def collect_ordered_markdown_files(
    project_dir: str,
) -> Tuple[List[str], Dict[str, Set[str]]]:
  """Return (ordered_md_files, dag_deps_map) under project/ sorted in 3-tier & topological order."""
  all_md: List[str] = []
  for dirpath, dirnames, filenames in os.walk(project_dir):
    dirnames[:] = sorted(
        d for d in dirnames if not d.startswith(".") and d != "__pycache__"
    )
    for fn in sorted(filenames):
      if fn.endswith(".md") and not fn.startswith(".") and not fn.endswith("-gdoc-tmp.md"):
        rel = os.path.relpath(os.path.join(dirpath, fn), project_dir)
        all_md.append(rel)

  all_md_set = set(all_md)
  raw_deps: Dict[str, Set[str]] = {
      rel: extract_internal_md_dependencies(project_dir, rel, all_md_set)
      for rel in all_md
  }
  # Filter out upward tier back-links (e.g., Tier 1 questions/ -> Tier 3 common/)
  tier_filtered: Dict[str, Set[str]] = {
      rel: {
          dep
          for dep in deps
          if doc_tier_priority(dep)[0] <= doc_tier_priority(rel)[0]
      }
      for rel, deps in raw_deps.items()
  }

  def _can_reach(src: str, dst: str) -> bool:
    seen: Set[str] = set()
    stack = [src]
    while stack:
      cur = stack.pop()
      if cur == dst:
        return True
      for nxt in tier_filtered.get(cur, set()):
        if nxt not in seen:
          seen.add(nxt)
          stack.append(nxt)
    return False

  # Break mutual same-tier cycles deterministically by doc_tier_priority so deps_map is a pure DAG
  deps_map: Dict[str, Set[str]] = {
      rel: {
          dep
          for dep in deps
          if not (
              _can_reach(dep, rel)
              and doc_tier_priority(rel) < doc_tier_priority(dep)
          )
      }
      for rel, deps in tier_filtered.items()
  }

  ordered: List[str] = []
  visited: Set[str] = set()
  visiting: Set[str] = set()

  def visit(node: str) -> None:
    if node in visited or node in visiting:
      return
    visiting.add(node)
    for dep in sorted(deps_map.get(node, set()), key=doc_tier_priority):
      visit(dep)
    visiting.remove(node)
    visited.add(node)
    ordered.append(node)

  for rel in sorted(all_md, key=doc_tier_priority):
    visit(rel)

  return ordered, deps_map


def build_execution_waves(
    ordered_files: List[str],
    deps_map: Dict[str, Set[str]],
    manifest: Dict,
) -> List[List[str]]:
  """Partition target Markdown files into concurrent execution waves.

  A target file `B` only waits for `A` if `A` is also in `ordered_files` AND
  `A` does not yet have a permanent `id` and `url` in `manifest['documents']`.
  All updates to existing documents have zero unresolved URL dependencies and
  execute together in Wave 0.
  """
  if not ordered_files:
    return []

  with MANIFEST_LOCK:
    resolved_docs: Set[str] = {
        rel
        for rel, info in manifest.get("documents", {}).items()
        if info.get("id") and info.get("url")
    }

  pending = list(ordered_files)
  waves: List[List[str]] = []

  while pending:
    pending_set = set(pending)
    ready: List[str] = []
    for rel in pending:
      unresolved_deps = [
          dep
          for dep in deps_map.get(rel, set())
          if dep in pending_set and dep not in resolved_docs
      ]
      if not unresolved_deps:
        ready.append(rel)

    if not ready:
      # Break mutual-link cycles in the earliest pending tier by selecting one
      # canonical node from every independent root strongly-connected component.
      min_tier = min(doc_tier_priority(r)[0] for r in pending)
      tier_nodes = [
          r for r in pending if doc_tier_priority(r)[0] == min_tier
      ]
      tier_set = set(tier_nodes)
      idx_counter = 0
      indices: Dict[str, int] = {}
      lowlink: Dict[str, int] = {}
      stack: List[str] = []
      on_stack: Set[str] = set()
      sccs: List[List[str]] = []

      def strongconnect(v: str) -> None:
        nonlocal idx_counter
        indices[v] = idx_counter
        lowlink[v] = idx_counter
        idx_counter += 1
        stack.append(v)
        on_stack.add(v)
        for w in deps_map.get(v, set()):
          if w not in tier_set or w in resolved_docs:
            continue
          if w not in indices:
            strongconnect(w)
            lowlink[v] = min(lowlink[v], lowlink[w])
          elif w in on_stack:
            lowlink[v] = min(lowlink[v], indices[w])
        if lowlink[v] == indices[v]:
          comp: List[str] = []
          while True:
            w = stack.pop()
            on_stack.remove(w)
            comp.append(w)
            if w == v:
              break
          sccs.append(comp)

      for node in tier_nodes:
        if node not in indices:
          strongconnect(node)

      for comp in sccs:
        comp_set = set(comp)
        ext_deps = [
            w
            for u in comp
            for w in deps_map.get(u, set())
            if w in pending_set and w not in resolved_docs and w not in comp_set
        ]
        if not ext_deps:
          ready.append(min(comp, key=doc_tier_priority))
      if not ready:
        ready = [min(tier_nodes, key=doc_tier_priority)]

    waves.append(ready)
    ready_set = set(ready)
    resolved_docs.update(ready_set)
    pending = [rel for rel in pending if rel not in ready_set]

  return waves


def preprocess_markdown_for_gdocs(
    workspace_root: str, project_dir: str, rel_path: str, manifest: Dict
) -> Tuple[str, Dict[str, str]]:
  """Preprocess local Markdown content for clean Google Docs import.

  NOTE: Keep output deterministic and unchanged so existing SHA-256 hashes in
  `gdrive_sync_manifest.json` remain 100% compatible across versions.
  """
  abs_path = os.path.join(project_dir, rel_path)
  base_dir = os.path.dirname(abs_path)
  with open(abs_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

  with MANIFEST_LOCK:
    docs_snapshot = dict(manifest.get("documents", {}))
    assets_snapshot = dict(manifest.get("assets", {}))
    folders_snapshot = dict(manifest.get("folders", {}))
    root_url = manifest.get("root_folder_url", "")

  resolved_links: Dict[str, str] = {}
  # Match non-image Markdown links `[label](target)` so inline images `![alt](...)` stay untouched
  link_pattern = re.compile(r"(?<!!)(\[[^\]]+\])\(([^)]+)\)")

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
      if target_rel in docs_snapshot:
        doc_url = docs_snapshot[target_rel]["url"]
        resolved_links[target] = doc_url
        return f"{label}({doc_url})"
      if target_rel in assets_snapshot:
        asset_url = assets_snapshot[target_rel]["url"]
        resolved_links[target] = asset_url
        return f"{label}({asset_url})"
      if target_rel in folders_snapshot:
        folder_url = folders_snapshot[target_rel]["url"]
        resolved_links[target] = folder_url
        return f"{label}({folder_url})"
    elif abs_target.startswith(os.path.join(workspace_root, "specs")):
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


def optimize_staged_gdoc_markdown(
    gdoc_md: str, has_local_svgs: bool
) -> Tuple[str, bool, bool]:
  """Normalize single-token LaTeX symbols on staged Markdown and return (md, needs_math, needs_diagrams).

  Executed strictly AFTER `content_hash` computation so manifest SHA-256 values
  are never invalidated.
  """
  out_lines: List[str] = []
  non_code_fragments: List[str] = []
  in_fence = False
  needs_diagrams = has_local_svgs

  for line in gdoc_md.splitlines():
    stripped = line.strip()
    if stripped.startswith("```"):
      if not in_fence:
        lang = stripped[3:].strip().lower()
        if lang in ("mermaid", "dot", "graphviz", "sequence-diagram", "image"):
          needs_diagrams = True
      in_fence = not in_fence
      out_lines.append(line)
      continue

    if in_fence:
      out_lines.append(line)
      continue

    # Split outside inline backtick spans `...`
    parts = re.split(r"(`+[^`]*`+)", line)
    for idx in range(0, len(parts), 2):
      parts[idx] = re.sub(
          r"\$\s*(\\[A-Za-z]+)\s*\$",
          lambda m: SIMPLE_INLINE_MATH_MAP.get(m.group(1), m.group(0)),
          parts[idx],
      )
      non_code_fragments.append(parts[idx])
    out_lines.append("".join(parts))

  non_code_text = "\n".join(non_code_fragments)
  # Conservative math check: only disable --render-math if ZERO '$', '\(', or '\[' remain outside code
  needs_math = (
      ("$" in non_code_text)
      or (r"\(" in non_code_text)
      or (r"\[" in non_code_text)
  )
  return "\n".join(out_lines) + "\n", needs_math, needs_diagrams


def has_open_comments(doc_id: str, cwd: str) -> bool:
  """Check if a single existing Google Doc has unresolved comments."""
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


def batch_check_open_comments(
    doc_ids: List[str], cwd: str, concurrency: int = 16
) -> Dict[str, bool]:
  """Prefetch open-comment presence across multiple docs in one `gdocs readonly stream` call."""
  unique_ids = list(dict.fromkeys(d for d in doc_ids if d))
  if not unique_ids:
    return {}
  if len(unique_ids) == 1:
    did = unique_ids[0]
    return {did: has_open_comments(did, cwd=cwd)}

  results: Dict[str, bool] = {}
  with tempfile.TemporaryDirectory(prefix="sync_drive_comments_") as tmp_dir:
    in_path = os.path.join(tmp_dir, "in.jsonl")
    out_path = os.path.join(tmp_dir, "out.jsonl")
    with open(in_path, "w", encoding="utf-8") as f:
      for did in unique_ids:
        f.write(json.dumps({"_id": did, "doc_id": did}) + "\n")

    proc = run_cli(
        [
            GDOCS_BIN,
            "readonly",
            "stream",
            "comments",
            "--open-only",
            "-i",
            in_path,
            "-o",
            out_path,
            "-c",
            str(min(concurrency, len(unique_ids))),
        ],
        cwd=cwd,
        check=False,
    )
    if proc.returncode == 0 and os.path.isfile(out_path):
      with open(out_path, "r", encoding="utf-8") as f:
        for line in f:
          line = line.strip()
          if not line:
            continue
          try:
            obj = json.loads(line)
          except json.JSONDecodeError:
            continue
          did = obj.get("doc_id") or obj.get("_id")
          if did and obj.get("_ok") is True:
            results[did] = bool(obj.get("comments"))

  # Fallback per-doc check for any IDs not returned by stream
  missing = [did for did in unique_ids if did not in results]
  for did in missing:
    results[did] = has_open_comments(did, cwd=cwd)
  return results


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


def rasterize_svg_to_png(abs_svg: str, abs_png: str) -> bool:
  """Rasterize an SVG file to a 2x HiDPI PNG (144 DPI, white background)."""
  magick_bin = shutil.which("magick") or shutil.which("convert")
  rsvg_bin = shutil.which("rsvg-convert")
  if magick_bin:
    cmd_svg = [
        magick_bin,
        "-density",
        "144",
        "-background",
        "white",
        abs_svg,
        abs_png,
    ]
  elif rsvg_bin:
    cmd_svg = [rsvg_bin, "-z", "2", "-f", "png", "-o", abs_png, abs_svg]
  else:
    return False
  proc_svg = subprocess.run(
      cmd_svg,
      capture_output=True,
      text=True,
      check=False,
  )
  return proc_svg.returncode == 0 and os.path.isfile(abs_png)


def ensure_png_for_svgs(
    project_dir: str,
    force: bool = False,
    dry_run: bool = False,
    jobs: int = DEFAULT_JOBS,
) -> None:
  """Ensure every .svg diagram under project/ has an up-to-date companion .png in the same folder."""
  render_tasks: List[Tuple[str, str, str]] = []
  for dirpath, dirnames, filenames in os.walk(project_dir):
    dirnames[:] = sorted(
        d for d in dirnames if not d.startswith(".") and d != "__pycache__"
    )
    for fn in sorted(filenames):
      if not fn.lower().endswith(".svg") or fn.startswith("."):
        continue
      abs_svg = os.path.join(dirpath, fn)
      abs_png = os.path.splitext(abs_svg)[0] + ".png"
      rel_png = os.path.relpath(abs_png, project_dir)
      needs_render = force or (not os.path.isfile(abs_png))
      if not needs_render:
        try:
          if os.path.getmtime(abs_svg) > os.path.getmtime(abs_png):
            needs_render = True
        except OSError:
          needs_render = True
      if needs_render:
        if dry_run:
          log_line(f"[DryRun PNG Render] {rel_png}")
        else:
          render_tasks.append((abs_svg, abs_png, rel_png))

  if not render_tasks:
    return

  def _render_one(item: Tuple[str, str, str]) -> None:
    abs_svg, abs_png, rel_png = item
    if rasterize_svg_to_png(abs_svg, abs_png):
      log_line(f"[PNG Rendered] {rel_png}")

  with ThreadPoolExecutor(max_workers=max(1, min(jobs, len(render_tasks)))) as pool:
    futures = [pool.submit(_render_one, t) for t in render_tasks]
    for fut in as_completed(futures):
      fut.result()


def find_local_images(
    base_dir: str, markdown_text: str
) -> List[Tuple[str, str]]:
  """Return list of (markdown_target, abs_image_path) for local .svg/.png/.jpg/.jpeg images in markdown_text."""
  img_pattern = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
  supported_exts = (".svg", ".png", ".jpg", ".jpeg")
  found: List[Tuple[str, str]] = []
  seen = set()
  for match in img_pattern.finditer(markdown_text):
    target = match.group(1).strip()
    if target.startswith(("http://", "https://", "data:")):
      continue
    clean_target = target.split("#")[0].split("?")[0]
    if not clean_target.lower().endswith(supported_exts):
      continue
    abs_img = os.path.normpath(os.path.join(base_dir, clean_target))
    if os.path.isfile(abs_img) and (target, abs_img) not in seen:
      seen.add((target, abs_img))
      found.append((target, abs_img))
  return found


class PreparedDocSync(NamedTuple):
  rel_path: str
  abs_path: str
  base_dir: str
  rel_dir: str
  parent_folder_id: str
  doc_title: str
  processed_md: str
  resolved_links_count: int
  local_images: List[Tuple[str, str]]
  content_hash: str
  existing_id: Optional[str]
  existing_url: Optional[str]


def prepare_document_sync(
    workspace_root: str,
    project_dir: str,
    rel_path: str,
    manifest: Dict,
    force: bool = False,
    dry_run: bool = False,
) -> Optional[PreparedDocSync]:
  """Preprocess and hash a Markdown file; return None if up-to-date (or handled in dry-run)."""
  processed_md, resolved_links = preprocess_markdown_for_gdocs(
      workspace_root, project_dir, rel_path, manifest
  )
  abs_path = os.path.join(project_dir, rel_path)
  base_dir = os.path.dirname(abs_path)
  local_images = find_local_images(base_dir, processed_md)

  hasher = hashlib.sha256(processed_md.encode("utf-8"))
  for _, abs_img in local_images:
    try:
      with open(abs_img, "rb") as sf:
        hasher.update(sf.read())
    except OSError:
      pass
  content_hash = hasher.hexdigest()

  rel_dir = os.path.dirname(rel_path)
  with MANIFEST_LOCK:
    parent_folder_id = (
        manifest["root_folder_id"]
        if rel_dir == ""
        else manifest["folders"][rel_dir]["id"]
    )
    existing = manifest["documents"].get(rel_path)
    existing_id = existing.get("id") if existing else None
    existing_url = existing.get("url") if existing else None
    existing_sha = existing.get("sha256") if existing else None

  doc_title = os.path.splitext(os.path.basename(rel_path))[0]

  if existing_id and not force and existing_sha == content_hash:
    log_line(f"[Doc Up-to-Date] {rel_path} -> {existing_id}")
    return None

  if dry_run:
    action = "Update" if existing_id else "Import"
    dry_doc_id = existing_id or f"DRYRUN_DOC_{doc_title}"
    dry_doc_url = (
        existing_url or f"https://docs.google.com/document/d/{dry_doc_id}/edit"
    )
    with MANIFEST_LOCK:
      manifest["documents"][rel_path] = {
          "id": dry_doc_id,
          "title": doc_title,
          "parent_folder": rel_dir,
          "parent_folder_id": parent_folder_id,
          "url": dry_doc_url,
          "sha256": content_hash,
      }
    log_line(
        f"[DryRun Doc {action}] {rel_path} (title='{doc_title}', "
        f"parent={parent_folder_id}, links_rewritten={len(resolved_links)}, "
        f"local_images={len(local_images)})"
    )
    return None

  return PreparedDocSync(
      rel_path=rel_path,
      abs_path=abs_path,
      base_dir=base_dir,
      rel_dir=rel_dir,
      parent_folder_id=parent_folder_id,
      doc_title=doc_title,
      processed_md=processed_md,
      resolved_links_count=len(resolved_links),
      local_images=local_images,
      content_hash=content_hash,
      existing_id=existing_id,
      existing_url=existing_url,
  )


def execute_prepared_doc_sync(
    workspace_root: str,
    plan: PreparedDocSync,
    open_comments_map: Dict[str, bool],
    manifest: Dict,
    checkpointer: ManifestCheckpointer,
) -> None:
  """Execute the Google Docs import/update/sync for a single prepared dirty document."""
  pid = os.getpid()
  tmp_md_path = os.path.join(
      plan.base_dir, f"{plan.doc_title}-{pid}-gdoc-tmp.md"
  )
  tmp_img_paths: List[str] = []
  register_temp_path(tmp_md_path)

  try:
    gdoc_md = plan.processed_md
    safe_doc = re.sub(r"[^a-zA-Z0-9-]+", "-", plan.doc_title).strip("-")
    for idx, (img_target, abs_img) in enumerate(plan.local_images, start=1):
      img_stem, img_ext = os.path.splitext(os.path.basename(abs_img))
      safe_stem = re.sub(r"[^a-zA-Z0-9-]+", "-", img_stem).strip("-")
      ext_lower = img_ext.lower()
      if ext_lower == ".svg":
        tmp_img_name = f"{safe_doc}-{pid}-{idx}-{safe_stem}-gdoc-tmp.png"
        tmp_img = os.path.join(plan.base_dir, tmp_img_name)
        register_temp_path(tmp_img)
        companion_png = os.path.splitext(abs_img)[0] + ".png"
        if os.path.isfile(companion_png):
          shutil.copy2(companion_png, tmp_img)
          tmp_img_paths.append(tmp_img)
          gdoc_md = gdoc_md.replace(f"({img_target})", f"(./{tmp_img_name})")
        elif rasterize_svg_to_png(abs_img, tmp_img):
          tmp_img_paths.append(tmp_img)
          gdoc_md = gdoc_md.replace(f"({img_target})", f"(./{tmp_img_name})")
        else:
          unregister_and_remove_temp_path(tmp_img)
      else:
        tmp_img_name = f"{safe_doc}-{pid}-{idx}-{safe_stem}-gdoc-tmp{ext_lower}"
        tmp_img = os.path.join(plan.base_dir, tmp_img_name)
        register_temp_path(tmp_img)
        shutil.copy2(abs_img, tmp_img)
        tmp_img_paths.append(tmp_img)
        gdoc_md = gdoc_md.replace(f"({img_target})", f"(./{tmp_img_name})")

    gdoc_md, needs_math, needs_diagrams = optimize_staged_gdoc_markdown(
        gdoc_md, has_local_svgs=bool(tmp_img_paths)
    )

    with open(tmp_md_path, "w", encoding="utf-8") as f:
      f.write(gdoc_md)

    fast_flags: List[str] = []
    if not needs_math:
      fast_flags.append("--render-math=false")
    if not needs_diagrams:
      fast_flags.append("--render-diagrams=false")

    if plan.existing_id:
      doc_id = plan.existing_id
      preserve_comments = open_comments_map.get(doc_id)
      if preserve_comments is None:
        preserve_comments = has_open_comments(doc_id, cwd=workspace_root)

      if preserve_comments:
        log_line(f"[Doc Sync (preserving comments)] {plan.rel_path} -> {doc_id}")
        run_cli(
            [
                GDOCS_BIN,
                "mutate",
                "sync",
                doc_id,
                tmp_md_path,
                "--save-base=false",
            ]
            + fast_flags,
            cwd=workspace_root,
        )
      else:
        log_line(f"[Doc Update] {plan.rel_path} -> {doc_id}")
        run_cli(
            [
                GDOCS_BIN,
                "mutate",
                "import-md",
                tmp_md_path,
                "--update",
                doc_id,
                "--pageless",
            ]
            + fast_flags,
            cwd=workspace_root,
        )
      doc_url = plan.existing_url or get_canonical_doc_url(
          doc_id, cwd=workspace_root
      )
    else:
      log_line(f"[Doc Import] {plan.rel_path} -> title='{plan.doc_title}'")
      proc = run_cli(
          [
              GDOCS_BIN,
              "mutate",
              "import-md",
              tmp_md_path,
              "--title",
              plan.doc_title,
              "--pageless",
          ]
          + fast_flags,
          cwd=workspace_root,
      )
      doc_id = extract_id_from_output(proc.stdout + "\n" + proc.stderr)
      if not doc_id:
        raise RuntimeError(
            f"Could not extract Document ID from import-md output for {plan.rel_path}:\n"
            f"{proc.stdout}\n{proc.stderr}"
        )
      run_cli(
          [GDRIVE_BIN, "mutate", "mv", doc_id, plan.parent_folder_id],
          cwd=workspace_root,
      )
      invalidate_folder_cache(plan.parent_folder_id)
      doc_url = get_canonical_doc_url(doc_id, cwd=workspace_root)
      log_line(
          f"[Doc Imported & Moved] {plan.rel_path} -> {doc_id} (folder {plan.parent_folder_id})"
      )

    with MANIFEST_LOCK:
      manifest["documents"][plan.rel_path] = {
          "id": doc_id,
          "title": plan.doc_title,
          "parent_folder": plan.rel_dir,
          "parent_folder_id": plan.parent_folder_id,
          "url": doc_url,
          "sha256": plan.content_hash,
          "resolved_links_count": plan.resolved_links_count,
          "updated_at": (
              datetime.datetime.now(datetime.timezone.utc)
              .replace(microsecond=0)
              .isoformat()
          ),
      }
    checkpointer.record_mutation()
  finally:
    unregister_and_remove_temp_path(tmp_md_path)
    for tmp_img in tmp_img_paths:
      unregister_and_remove_temp_path(tmp_img)


def collect_asset_files(project_dir: str) -> List[str]:
  """Return all diagram, spec, and data export asset files (.svg, .png, .jpg, .jpeg, .json, .csv) under project/."""
  asset_exts = {".svg", ".png", ".jpg", ".jpeg", ".json", ".csv"}
  assets: List[str] = []
  for dirpath, dirnames, filenames in os.walk(project_dir):
    dirnames[:] = sorted(
        d for d in dirnames if not d.startswith(".") and d != "__pycache__"
    )
    for fn in sorted(filenames):
      if "-gdoc-tmp." in fn or fn.startswith("."):
        continue
      ext = os.path.splitext(fn)[1].lower()
      if ext in asset_exts:
        rel = os.path.relpath(os.path.join(dirpath, fn), project_dir)
        assets.append(rel)
  return assets


def sync_asset_file(
    workspace_root: str,
    project_dir: str,
    rel_path: str,
    manifest: Dict,
    checkpointer: ManifestCheckpointer,
    force: bool = False,
    dry_run: bool = False,
) -> bool:
  """Upload or update a raw diagram/spec/CSV file in Google Drive. Returns True if mutated."""
  abs_path = os.path.join(project_dir, rel_path)
  with open(abs_path, "rb") as f:
    content_hash = hashlib.sha256(f.read()).hexdigest()

  rel_dir = os.path.dirname(rel_path)
  file_name = os.path.basename(rel_path)
  with MANIFEST_LOCK:
    parent_folder_id = (
        manifest["root_folder_id"]
        if rel_dir == ""
        else manifest["folders"][rel_dir]["id"]
    )
    manifest.setdefault("assets", {})
    existing = manifest["assets"].get(rel_path)
    existing_id = existing.get("id") if existing else None
    existing_sha = existing.get("sha256") if existing else None

  if existing_id and not force and existing_sha == content_hash:
    log_line(f"[Asset Up-to-Date] {rel_path} -> {existing_id}")
    return False

  if dry_run:
    action = "Update" if existing_id else "Upload"
    dry_id = existing_id or f"DRYRUN_ASSET_{file_name}"
    with MANIFEST_LOCK:
      manifest["assets"][rel_path] = {
          "id": dry_id,
          "name": file_name,
          "parent_folder": rel_dir,
          "parent_folder_id": parent_folder_id,
          "url": f"https://drive.google.com/file/d/{dry_id}/view",
          "sha256": content_hash,
      }
    log_line(f"[DryRun Asset {action}] {rel_path} (parent={parent_folder_id})")
    return False

  file_id: Optional[str] = existing_id
  if not file_id:
    children = list_drive_children(parent_folder_id, cwd=workspace_root, use_cache=True)
    for child in children:
      c_name = child.get("name") or child.get("Name")
      c_id = child.get("id") or child.get("ID")
      c_mime = child.get("mimeType") or child.get("MimeType") or child.get("Type")
      if c_name == file_name and c_id and ("folder" not in str(c_mime).lower()):
        file_id = c_id
        break

  if file_id:
    log_line(f"[Asset Update] {rel_path} -> {file_id}")
    run_cli(
        [GDRIVE_BIN, "mutate", "update", file_id, abs_path, "--json"],
        cwd=workspace_root,
    )
  else:
    log_line(f"[Asset Upload] {rel_path} -> folder {parent_folder_id}")
    proc = run_cli(
        [
            GDRIVE_BIN,
            "mutate",
            "upload",
            abs_path,
            "--parent",
            parent_folder_id,
            "--json",
        ],
        cwd=workspace_root,
    )
    invalidate_folder_cache(parent_folder_id)
    file_id = extract_id_from_output(proc.stdout + "\n" + proc.stderr)
    if not file_id:
      children = list_drive_children(
          parent_folder_id, cwd=workspace_root, use_cache=False
      )
      for child in children:
        c_name = child.get("name") or child.get("Name")
        c_id = child.get("id") or child.get("ID")
        if c_name == file_name and c_id:
          file_id = c_id
          break
    if not file_id:
      raise RuntimeError(
          f"Could not extract File ID after upload for {rel_path}:\n{proc.stdout}\n{proc.stderr}"
      )

  file_url = f"https://drive.google.com/file/d/{file_id}/view"
  with MANIFEST_LOCK:
    manifest["assets"][rel_path] = {
        "id": file_id,
        "name": file_name,
        "parent_folder": rel_dir,
        "parent_folder_id": parent_folder_id,
        "url": file_url,
        "sha256": content_hash,
        "updated_at": (
            datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
        ),
    }
  checkpointer.record_mutation()
  return True


def update_specs_project_registry(
    specs_project_path: str, manifest: Dict
) -> bool:
  """Update Section 2.2 (Subfolders, Native Google Docs, and Assets tables) in specs/specs_project.md."""
  if not os.path.exists(specs_project_path):
    return False

  with open(specs_project_path, "r", encoding="utf-8") as f:
    original_text = f.read()

  root_name = manifest.get("root_folder_name") or "20 Project"
  folders = manifest.get("folders", {})
  documents = manifest.get("documents", {})
  assets = manifest.get("assets", {})

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
    if rel_path.startswith("questions/"):
      return (4, os.path.dirname(rel_path), 1, rel_path)
    return (5, os.path.dirname(rel_path), 1, rel_path)

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
    elif rel_path.startswith("questions/"):
      layer_label = "**Layer 4 (`questions/`)**"
    else:
      layer_label = "**Project (`project/`)**"
    doc_lines.append(
        f"| {layer_label} | [`{rel_path}`](../project/{rel_path}) | [{d_title}]({d_url}) |"
    )

  sections = ["\n".join(folder_lines), "\n".join(doc_lines)]

  if assets:
    sorted_assets = sorted(assets.keys())
    asset_lines = [
        f"#### C. Synchronized Diagram & Spec Assets ({len(sorted_assets)} Files)",
        "",
        "| Parent Folder | Local Asset Path (`project/...`) | Synchronized Google Drive File |",
        "| :--- | :--- | :--- |",
    ]
    for rel_path in sorted_assets:
      a_info = assets[rel_path]
      a_name = a_info.get("name") or os.path.basename(rel_path)
      a_url = a_info.get("url", "")
      a_parent = a_info.get("parent_folder", os.path.dirname(rel_path))
      asset_lines.append(
          f"| `{a_parent}/` | [`{rel_path}`](../project/{rel_path}) | [`{a_name}`]({a_url}) |"
      )
    sections.append("\n".join(asset_lines))

  replacement_block = "\n\n".join(sections) + "\n"

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
    log_line(f"[Specs Updated] Refreshed Section 2.2 in {specs_project_path}")
    return True
  return False


def main() -> int:
  global ACTIVE_CHECKPOINTER  # pylint: disable=global-statement
  t_start = time.monotonic()
  _install_signal_handlers()

  parser = argparse.ArgumentParser(
      description="Synchronize local project/ folder with Google Drive as native Google Docs and Drive assets."
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
  parser.add_argument(
      "--file",
      "-f",
      action="append",
      default=None,
      help=(
          "Optional Markdown file, asset file, or subdirectory path (relative to workspace or project/) "
          "to synchronize instead of all documents (repeatable)"
      ),
  )
  parser.add_argument(
      "--jobs",
      "-j",
      type=int,
      default=DEFAULT_JOBS,
      help=(
          f"Maximum concurrent Google Docs/Drive worker threads per dependency wave "
          f"(default: {DEFAULT_JOBS}; pass 1 for serial execution)"
      ),
  )
  args = parser.parse_args()
  jobs = max(1, args.jobs)

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

  if not args.dry_run:
    swept = sweep_stale_temp_files(project_dir)
    if swept:
      log_line(f"[Cleanup] Removed {swept} stale *-gdoc-tmp.* file(s) from prior run")

  root_folder_id, root_folder_name = resolve_root_folder_from_specs(
      specs_project_path, manifest_path, args.root_folder_id
  )
  manifest = load_manifest(manifest_path, root_folder_id, root_folder_name)
  checkpointer = ManifestCheckpointer(manifest_path, manifest, flush_every=5)
  ACTIVE_CHECKPOINTER = checkpointer

  try:
    # 1. Discover all directories under project/ in top-down order
    rel_dirs: List[str] = []
    for dirpath, dirnames, filenames in os.walk(project_dir):
      dirnames[:] = sorted(
          d for d in dirnames if not d.startswith(".") and d != "__pycache__"
      )
      rel = os.path.relpath(dirpath, project_dir)
      if rel != ".":
        if rel == "questions" and not dirnames and not [
            fn for fn in filenames if not fn.startswith(".")
        ]:
          continue
        rel_dirs.append(rel)

    log_line(f"=== Target Workspace: {workspace_root} (jobs={jobs}) ===")
    log_line(f"=== Phase 1: Ensuring {len(rel_dirs)} Folders under {root_folder_id} ===")
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
          checkpointer,
          cwd=workspace_root,
          dry_run=args.dry_run,
      )
    if not args.dry_run:
      checkpointer.flush()

    # 2. Ensure companion .png files exist for all .svg diagrams, then collect Markdown & asset files
    ensure_png_for_svgs(
        project_dir,
        force=(args.force and not args.file),
        dry_run=args.dry_run,
        jobs=jobs,
    )
    ordered_files, deps_map = collect_ordered_markdown_files(project_dir)
    asset_files = collect_asset_files(project_dir)

    if args.file:
      selected_md: Set[str] = set()
      selected_assets: Set[str] = set()
      for raw_target in args.file:
        candidate = os.path.abspath(raw_target)
        if not os.path.exists(candidate):
          candidate = os.path.abspath(os.path.join(project_dir, raw_target))
        rel_target = os.path.relpath(candidate, project_dir)
        if os.path.isdir(candidate):
          prefix = "" if rel_target == "." else rel_target.rstrip("/") + "/"
          for f in ordered_files:
            if prefix == "" or f.startswith(prefix):
              selected_md.add(f)
          for a in asset_files:
            if prefix == "" or a.startswith(prefix):
              selected_assets.add(a)
        elif rel_target in ordered_files:
          selected_md.add(rel_target)
          doc_stem = os.path.splitext(os.path.basename(rel_target))[0]
          base_stem = (
              doc_stem[: -len("_slides-prompt")]
              if doc_stem.endswith("_slides-prompt")
              else doc_stem
          )
          abs_md = os.path.join(project_dir, rel_target)
          referenced_rel_assets: Set[str] = set()
          try:
            with open(abs_md, "r", encoding="utf-8") as mf:
              md_txt = mf.read()
            md_base_dir = os.path.dirname(abs_md)
            for _, abs_img in find_local_images(md_base_dir, md_txt):
              if abs_img.startswith(project_dir + os.sep):
                referenced_rel_assets.add(os.path.relpath(abs_img, project_dir))
                if abs_img.lower().endswith(".svg"):
                  comp = os.path.splitext(abs_img)[0] + ".png"
                  if os.path.isfile(comp):
                    referenced_rel_assets.add(os.path.relpath(comp, project_dir))
            for link_m in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", md_txt):
              raw_lnk = link_m.group(1).strip().split("#")[0].split("?")[0]
              if not raw_lnk or raw_lnk.startswith(("http://", "https://", "mailto:")):
                continue
              abs_lnk = os.path.normpath(os.path.join(md_base_dir, raw_lnk))
              if abs_lnk.startswith(project_dir + os.sep) and os.path.isfile(abs_lnk):
                referenced_rel_assets.add(os.path.relpath(abs_lnk, project_dir))
          except OSError:
            pass
          for a in asset_files:
            if (
                f"/diagrams/{doc_stem}/" in f"/{a}"
                or f"/screenshots/{doc_stem}/" in f"/{a}"
                or f"/diagrams/{base_stem}/" in f"/{a}"
                or f"/screenshots/{base_stem}/" in f"/{a}"
                or a in referenced_rel_assets
            ):
              selected_assets.add(a)
        elif rel_target in asset_files:
          selected_assets.add(rel_target)
          if rel_target.lower().endswith(".svg"):
            companion_png = os.path.splitext(rel_target)[0] + ".png"
            if companion_png in asset_files:
              selected_assets.add(companion_png)
        else:
          raise RuntimeError(
              f"Target file or directory '{raw_target}' (resolved to '{rel_target}') not found in project/"
          )
      ordered_files = [f for f in ordered_files if f in selected_md]
      asset_files = [a for a in asset_files if a in selected_assets]
      if args.force and not args.dry_run:
        for a in asset_files:
          if a.lower().endswith(".svg"):
            abs_svg = os.path.join(project_dir, a)
            abs_png = os.path.splitext(abs_svg)[0] + ".png"
            if rasterize_svg_to_png(abs_svg, abs_png):
              log_line(f"[PNG Rendered] {os.path.relpath(abs_png, project_dir)}")

    total_mutated_assets = 0
    if asset_files:
      log_line(
          f"\n=== Phase 2: Synchronizing {len(asset_files)} Diagram, Screenshot & Spec Assets (jobs={jobs}) ==="
      )
      asset_workers = max(1, min(jobs, len(asset_files)))
      if asset_workers == 1 or args.dry_run:
        for rel_path in asset_files:
          if sync_asset_file(
              workspace_root,
              project_dir,
              rel_path,
              manifest,
              checkpointer,
              force=args.force,
              dry_run=args.dry_run,
          ):
            total_mutated_assets += 1
      else:
        asset_errors: List[Exception] = []
        with ThreadPoolExecutor(max_workers=asset_workers) as pool:
          fut_map = {
              pool.submit(
                  sync_asset_file,
                  workspace_root,
                  project_dir,
                  rel_path,
                  manifest,
                  checkpointer,
                  args.force,
                  args.dry_run,
              ): rel_path
              for rel_path in asset_files
          }
          for fut in as_completed(fut_map):
            try:
              if fut.result():
                total_mutated_assets += 1
            except Exception as exc:  # pylint: disable=broad-except
              asset_errors.append(exc)
              log_line(f"[ERROR] Failed asset sync {fut_map[fut]}: {exc}")
        if asset_errors:
          checkpointer.flush()
          raise asset_errors[0]
      if not args.dry_run:
        checkpointer.flush()

    waves = build_execution_waves(ordered_files, deps_map, manifest)
    log_line(
        f"\n=== Phase 3: Synchronizing {len(ordered_files)} Markdown Documents "
        f"across {len(waves)} wave(s) (jobs={jobs}) ==="
    )

    total_mutated_docs = 0
    for wave_idx, wave_files in enumerate(waves, start=1):
      dirty_plans: List[PreparedDocSync] = []
      for rel_path in wave_files:
        plan = prepare_document_sync(
            workspace_root,
            project_dir,
            rel_path,
            manifest,
            force=args.force,
            dry_run=args.dry_run,
        )
        if plan is not None:
          dirty_plans.append(plan)

      if not dirty_plans:
        continue

      if len(waves) > 1:
        log_line(
            f"--- Wave {wave_idx}/{len(waves)}: {len(dirty_plans)} document(s) to sync ---"
        )

      existing_dirty_ids = [
          p.existing_id for p in dirty_plans if p.existing_id is not None
      ]
      open_comments_map: Dict[str, bool] = {}
      if existing_dirty_ids:
        t_c0 = time.monotonic()
        open_comments_map = batch_check_open_comments(
            existing_dirty_ids, cwd=workspace_root
        )
        if len(existing_dirty_ids) >= 2:
          log_line(
              f"[Prefetch] Checked open comments for {len(existing_dirty_ids)} docs "
              f"in {time.monotonic() - t_c0:.2f}s"
          )

      worker_count = max(1, min(jobs, len(dirty_plans)))
      if worker_count == 1:
        for plan in dirty_plans:
          execute_prepared_doc_sync(
              workspace_root,
              plan,
              open_comments_map,
              manifest,
              checkpointer,
          )
      else:
        errors: List[Exception] = []
        with ThreadPoolExecutor(max_workers=worker_count) as pool:
          future_to_rel = {
              pool.submit(
                  execute_prepared_doc_sync,
                  workspace_root,
                  plan,
                  open_comments_map,
                  manifest,
                  checkpointer,
              ): plan.rel_path
              for plan in dirty_plans
          }
          for fut in as_completed(future_to_rel):
            try:
              fut.result()
            except Exception as exc:  # pylint: disable=broad-except
              errors.append(exc)
              log_line(f"[ERROR] Failed syncing {future_to_rel[fut]}: {exc}")
        if errors:
          checkpointer.flush()
          raise errors[0]

      total_mutated_docs += len(dirty_plans)
      checkpointer.flush()

    # 4. Auto-update Section 2.2 in specs/specs_project.md
    if not args.dry_run and not args.no_update_specs:
      update_specs_project_registry(specs_project_path, manifest)

  finally:
    cleanup_all_active_temps()
    if not args.dry_run:
      checkpointer.flush()

  elapsed = time.monotonic() - t_start
  log_line(
      f"\n=== Synchronization Complete in {elapsed:.1f}s "
      f"({total_mutated_docs} doc(s), {total_mutated_assets} asset(s) mutated) ==="
  )
  log_line(f"Manifest saved to: {manifest_path}")
  return 0


if __name__ == "__main__":
  sys.exit(main())
