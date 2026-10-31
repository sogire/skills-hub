#!/usr/bin/env python3
"""Validate question evaluation Markdown files in project/questions/ against the canonical template.

Workspace-agnostic structural, skill-grounding, and anti-hallucination validator for `gcp-project-copilot`:
1. Resolves `<workspace-root>` via `--workspace` / `-w` or upward search for `specs/specs_project.md`.
2. Dynamically extracts `CUSTOMER_NAME` from `<workspace-root>/specs/specs_project.md` (zero hardcoded IDs).
3. Verifies structural fidelity against `resources/templates/template_answers_to_questions.md`:
   - Dual H1 header (`# **Technical Question Evaluation & Architectural Answer**` + customer/code H1)
   - Exact 7-row top Metadata Table (zero skills/status rows in the top table)
   - Exact 6 canonical `##` sections (`1`..`6`) in order
   - Contiguous numbered `### 2.1`, `### 2.2`, ... subsections in Section 2, `### 3.1`, `### 3.2`,
     `> [!IMPORTANT]`, `> [!TIP]`, deliverables links, and official Google Cloud doc URLs
4. Enforces 6 Anti-Hallucination & Skill-Validation Gates:
   - Gate A (External-Only & Lifecycle Skill Gate): Forbids `agyhub` internal skills (`skills-hub/internal/*`,
     e.g., `gcp-project-copilot`, `gcp-architecture-diagram`, `gcp-console-demo-generator`, `agyhub-*`) and
     IDE built-in/meta/doc skills (`agy-customizations`, `gdocs`, `gdrive`, etc.) in Section 6. Verifies
     cited `SKILL.md` / `references/*.md` artifacts exist on disk. Preserves previously valid deprecated
     external skills in historical files (`[WARN]`), while `--require-active-skills` / `--transcript`
     strictly enforces active external skills for all new or completely regenerated answers (`[FAIL]`).
   - Gate B (100% Code-Block & IAM Coverage Invariant): Verifies every code-bearing `### 2.x` subsection and
     `### 3.1` IAM matrix is explicitly mapped in Section 6's `Validated Sections & Code Blocks` column.
   - Gate C (Offline `gcloud` & `bq` CLI Schema Validator): Validates `gcloud` (`GA`/`alpha`/`beta`) subcommands
     and `--flags` plus `bq` subcommands inside `bash`/`sh` blocks against local Cloud SDK completion schemas.
   - Gate D (Code Block AST & Dialect Linter): Validates `json` (`json.loads`), `yaml`/`yml` (`yaml.safe_load_all`),
     `python` (`ast.parse`), Dataform `sqlx` `config { ... }` balance, and BigQuery GoogleSQL dialect rules.
   - Gate E (Section 3.1 IAM Permission & Role Grammar): Ensures `roles/...` are not placed in the IAM
     Permissions column and every permission row cites valid 3-part `<service>.<resource>.<verb>` permissions.
   - Gate F (Optional Session Transcript Proof & URL Reachability): `--transcript` audits Antigravity JSONL
     logs (including spawned subagents) to prove `read_file` / `retrieving-developer-knowledge` calls occurred;
     `--verify-urls` checks HTTP reachability of Section 5 documentation links.
"""

import argparse
import ast
from dataclasses import dataclass, field
import difflib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import sys
import textwrap
from typing import Any, Dict, List, Optional, Set, Tuple
import urllib.error
import urllib.request

try:
  import yaml
except ImportError:  # pragma: no cover
  yaml = None  # type: ignore


EXPECTED_META_KEYS = [
    "**Customer / Project**",
    "**Question ID**",
    "**Question**",
    "**Canonical Domain**",
    "**Asked By**",
    "**Source Session & Log**",
    "**Date Answered**",
]

# Defensive fallback set of internal/IDE meta-skills that must NEVER appear in customer-facing Section 6,
# even if the validator is executed outside a full skills-hub checkout.
STATIC_FORBIDDEN_INTERNAL_OR_META_SKILLS: Set[str] = {
    # agyhub internal/customer-engagement, internal/hub-tools, internal/templates
    "gcp-project-copilot",
    "gcp-architecture-diagram",
    "gcp-console-demo-generator",
    "agyhub-agent",
    "agyhub-cluster-role-creation",
    "agyhub-skills-gap-creator",
    "template-skill",
    "template-plugin",
    # Antigravity IDE built-in & Google Docs/Drive workspace utility skills
    "agy-customizations",
    "antigravity-guide",
    "antigravity_guide",
    "automation",
    "generative_ui",
    "generative-ui",
    "migrate-workflows",
    "plugin",
    "ui-plugin-navigation",
    "gdocs",
    "gdrive",
}

EXECUTABLE_CODE_LANGS: Set[str] = {
    "sql",
    "sqlx",
    "googlesql",
    "bash",
    "sh",
    "shell",
    "zsh",
    "yaml",
    "yml",
    "json",
    "python",
    "py",
    "hcl",
    "terraform",
    "tf",
    "lookml",
    "lkml",
    "js",
    "javascript",
    "ts",
    "typescript",
    "go",
    "java",
    "xml",
    "toml",
    "ini",
    "dockerfile",
}

GCLOUD_VALUE_GLOBAL_FLAGS: Set[str] = {
    "--account",
    "--billing-project",
    "--configuration",
    "--flags-file",
    "--flatten",
    "--format",
    "--impersonate-service-account",
    "--project",
    "--universe-domain",
    "--verbosity",
}

NON_BIGQUERY_SQL_PATTERNS: List[Tuple[str, str]] = [
    (
        r"\bNVL\s*\(",
        "Non-BigQuery function 'NVL(' detected in SQL block (use BigQuery 'IFNULL(' or 'COALESCE(')",
    ),
    (
        r"\bILIKE\b",
        "Non-BigQuery operator 'ILIKE' detected in SQL block (use 'LOWER(...) LIKE' or 'REGEXP_CONTAINS(...)')",
    ),
    (
        r"\bDATEADD\s*\(",
        "Non-BigQuery function 'DATEADD(' detected in SQL block (use BigQuery 'DATE_ADD(..., INTERVAL ...)')",
    ),
    (
        r"\bAUTOINCREMENT\b",
        "Non-BigQuery keyword 'AUTOINCREMENT' detected in SQL block",
    ),
]


@dataclass
class SkillCatalog:
  """Dynamically discovered external skills, active workspace skills, and forbidden internal/meta skills."""

  external_skills: Dict[str, Path] = field(default_factory=dict)
  active_external_skills: Set[str] = field(default_factory=set)
  forbidden_skills: Set[str] = field(
      default_factory=lambda: set(STATIC_FORBIDDEN_INTERNAL_OR_META_SKILLS)
  )


@dataclass
class CliSchemas:
  """Lazily loaded local Google Cloud SDK (`gcloud` and `bq`) completion schemas."""

  _loaded: bool = False
  gcloud_tree: Optional[Dict[str, Any]] = None
  bq_commands: Set[str] = field(default_factory=set)

  def ensure_loaded(self) -> None:
    if self._loaded:
      return
    self._loaded = True
    loaded = load_cli_schemas()
    self.gcloud_tree = loaded.gcloud_tree
    self.bq_commands = loaded.bq_commands


def resolve_workspace_root(cli_workspace: Optional[str] = None) -> Path:
  """Resolve target customer workspace root from CLI flag or upward search from cwd."""
  if cli_workspace:
    ws = Path(cli_workspace).expanduser().resolve()
    if not ws.is_dir():
      raise RuntimeError(f"Specified workspace directory does not exist: {ws}")
    return ws

  curr = Path.cwd().resolve()
  while True:
    if (curr / "specs" / "specs_project.md").exists() or (
        (curr / "project").is_dir() and (curr / "specs").is_dir()
    ):
      return curr
    if curr.parent == curr:
      break
    curr = curr.parent

  return Path.cwd().resolve()


def extract_customer_name(specs_md: Path) -> Optional[str]:
  """Extract CUSTOMER_NAME dynamically from specs/specs_project.md."""
  if not specs_md.is_file():
    return None
  text = specs_md.read_text(encoding="utf-8")
  m = re.search(r"\|\s*\*\*`CUSTOMER_NAME`\*\*\s*\|\s*(.+?)\s*\|", text)
  if not m:
    return None
  raw = m.group(1).strip()
  clean = re.sub(r"[*`]", "", raw).strip()
  if not clean or "{{" in clean:
    return None
  return clean


def _index_skills_under(root: Path, dest: Dict[str, Path]) -> None:
  """Recursively index skill and plugin directories (`SKILL.md` / `plugin.json`) under `root`."""
  if not root.is_dir():
    return
  for skill_md in root.rglob("SKILL.md"):
    skill_dir = skill_md.parent.resolve()
    dest.setdefault(skill_dir.name, skill_dir)
  for plugin_json in root.rglob("plugin.json"):
    plugin_dir = plugin_json.parent.resolve()
    dest.setdefault(plugin_dir.name, plugin_dir)
    try:
      pdata = json.loads(plugin_json.read_text(encoding="utf-8"))
      pname = pdata.get("name")
      if isinstance(pname, str) and pname.strip():
        dest.setdefault(pname.strip(), plugin_dir)
    except Exception:
      pass


def _parse_manifest_paths(manifest_path: Path) -> List[Path]:
  """Extract skill/plugin target paths from `.agents/{skills,plugins}.json` or `~/.gemini/config/*.json`."""
  if not manifest_path.is_file():
    return []
  try:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
  except Exception:
    return []

  resolved: List[Path] = []
  if isinstance(data, dict):
    # Legacy list format: {"skills": ["/path/to/skill", ...]} or {"plugins": [...]}
    for key in ("skills", "plugins"):
      items = data.get(key)
      if isinstance(items, list):
        for item in items:
          if isinstance(item, str):
            p = Path(item).expanduser()
            if p.exists():
              resolved.append(p.resolve())
    # Modern agyhub format: {"entries": [{"path": "...", "include_only": [...]}]}
    entries = data.get("entries")
    if isinstance(entries, list):
      for entry in entries:
        if not isinstance(entry, dict):
          continue
        base_raw = entry.get("path")
        if not isinstance(base_raw, str):
          continue
        base = Path(base_raw).expanduser()
        if not base.exists():
          continue
        inc = entry.get("include_only")
        if isinstance(inc, list) and inc:
          for sub in inc:
            if isinstance(sub, str) and (base / sub).exists():
              resolved.append((base / sub).resolve())
        else:
          resolved.append(base.resolve())
  return resolved


def _is_internal_or_builtin_path(path: Path) -> bool:
  """Return True if `path` resides inside an `agyhub` `internal/` tree or IDE builtin/config utility dir."""
  parts = path.parts
  if "internal" in parts:
    idx = parts.index("internal")
    # Check if part of a skills-hub layout (sibling 'external' directory exists)
    hub_candidate = Path(*parts[:idx]) if idx > 0 else None
    if hub_candidate and (hub_candidate / "external").is_dir():
      return True
  s = str(path)
  if "/.gemini/antigravity/builtin/" in s:
    return True
  if path.name in ("gdocs", "gdrive"):
    return True
  return False


def discover_skill_catalog(workspace_root: Path) -> SkillCatalog:
  """Dynamically build the catalog of external skills, active workspace skills, and forbidden internal skills."""
  catalog = SkillCatalog()

  # 1. Discover skills-hub root upward from this script (`.../internal/customer-engagement/skills/gcp-project-copilot/scripts/`)
  curr = Path(__file__).resolve().parent
  hub_roots: Set[Path] = set()
  while True:
    if (curr / "external").is_dir() and (curr / "internal").is_dir():
      hub_roots.add(curr)
      break
    if curr.parent == curr:
      break
    curr = curr.parent

  # 2. Parse workspace & global manifests to catch additional hub roots and active skills/plugins
  home = Path.home()
  manifest_files = [
      workspace_root / ".agents" / "skills.json",
      workspace_root / ".agents" / "plugins.json",
      home / ".gemini" / "config" / "skills.json",
      home / ".gemini" / "config" / "plugins.json",
  ]
  manifest_targets: List[Path] = []
  for mf in manifest_files:
    for target in _parse_manifest_paths(mf):
      manifest_targets.append(target)
      anc = target
      while True:
        if (anc / "external").is_dir() and (anc / "internal").is_dir():
          hub_roots.add(anc)
          break
        if anc.parent == anc:
          break
        anc = anc.parent

  # Also check IDE builtin skills directory dynamically
  builtin_dir = home / ".gemini" / "antigravity" / "builtin" / "skills"
  if builtin_dir.is_dir():
    internal_tmp: Dict[str, Path] = {}
    _index_skills_under(builtin_dir, internal_tmp)
    catalog.forbidden_skills.update(internal_tmp.keys())

  # 3. Index hub `internal/` (forbidden) and `external/` (allowed catalog)
  for hub in hub_roots:
    internal_map: Dict[str, Path] = {}
    _index_skills_under(hub / "internal", internal_map)
    catalog.forbidden_skills.update(internal_map.keys())
    _index_skills_under(hub / "external", catalog.external_skills)

  # 4. Index workspace-local `.agents/skills/` (if custom project domain skills exist) and active manifests
  ws_local_skills = workspace_root / ".agents" / "skills"
  if ws_local_skills.is_dir():
    local_map: Dict[str, Path] = {}
    _index_skills_under(ws_local_skills, local_map)
    for sname, spath in local_map.items():
      if not _is_internal_or_builtin_path(spath) and sname not in catalog.forbidden_skills:
        catalog.external_skills.setdefault(sname, spath)
        catalog.active_external_skills.add(sname)

  for target in manifest_targets:
    if _is_internal_or_builtin_path(target):
      catalog.forbidden_skills.add(target.name)
      continue
    if (target / "SKILL.md").is_file() or (target / "plugin.json").is_file():
      if target.name not in catalog.forbidden_skills:
        catalog.external_skills.setdefault(target.name, target)
        catalog.active_external_skills.add(target.name)
    # If target is a plugin or group directory bundling multiple `SKILL.md` skills, mark bundled skills active
    bundled: Dict[str, Path] = {}
    _index_skills_under(target, bundled)
    for bname, bpath in bundled.items():
      if not _is_internal_or_builtin_path(bpath) and bname not in catalog.forbidden_skills:
        catalog.external_skills.setdefault(bname, bpath)
        catalog.active_external_skills.add(bname)

  return catalog


def load_cli_schemas() -> CliSchemas:
  """Load offline `gcloud` and `bq` CLI completion schemas from the local Google Cloud SDK if installed."""
  schemas = CliSchemas()
  gcloud_bin = shutil.which("gcloud")
  if not gcloud_bin:
    return schemas
  sdk_root = Path(os.path.realpath(gcloud_bin)).parent.parent
  cli_data_dir = sdk_root / "data" / "cli"
  if not cli_data_dir.is_dir():
    return schemas

  gcloud_comp = cli_data_dir / "gcloud_completions.py"
  if gcloud_comp.is_file():
    sys_added = False
    cli_dir_str = str(cli_data_dir)
    try:
      if cli_dir_str not in sys.path:
        sys.path.insert(0, cli_dir_str)
        sys_added = True
      import gcloud_completions  # type: ignore

      schemas.gcloud_tree = getattr(
          gcloud_completions, "STATIC_COMPLETION_CLI_TREE", None
      )
    except Exception:
      schemas.gcloud_tree = None
    finally:
      if sys_added and cli_dir_str in sys.path:
        sys.path.remove(cli_dir_str)

  bq_json = cli_data_dir / "bq.json"
  if bq_json.is_file():
    try:
      bq_data = json.loads(bq_json.read_text(encoding="utf-8"))
      cmds = bq_data.get("commands", {})
      if isinstance(cmds, dict):
        schemas.bq_commands = set(cmds.keys())
    except Exception:
      pass

  return schemas


@dataclass
class TranscriptAuditData:
  """Extracted tool execution telemetry across a parent conversation and any spawned subagents."""

  read_paths: List[str] = field(default_factory=list)
  doc_retrieval_invoked: bool = False
  unreachable_subagents: Set[str] = field(default_factory=set)


def load_transcript_audit(transcript_args: Any) -> TranscriptAuditData:
  """Load one or more `transcript_full.jsonl` / `transcript.jsonl` logs (plus reachable child subagent logs)."""
  if isinstance(transcript_args, (str, Path)):
    transcript_list = [str(transcript_args)]
  else:
    transcript_list = [str(x) for x in transcript_args]

  audit = TranscriptAuditData()
  visited_logs: Set[Path] = set()
  queue: List[Path] = []
  brain_dirs: Set[Path] = set()

  for transcript_arg in transcript_list:
    cand = Path(transcript_arg).expanduser().resolve()
    if cand.is_dir():
      # Accept either `<brain>/<conv-id>` or `<brain>/<conv-id>/.system_generated/logs`
      if (cand / "transcript_full.jsonl").is_file():
        root_log = cand / "transcript_full.jsonl"
      elif (cand / "transcript.jsonl").is_file():
        root_log = cand / "transcript.jsonl"
      elif (cand / ".system_generated" / "logs" / "transcript_full.jsonl").is_file():
        root_log = cand / ".system_generated" / "logs" / "transcript_full.jsonl"
      elif (cand / ".system_generated" / "logs" / "transcript.jsonl").is_file():
        root_log = cand / ".system_generated" / "logs" / "transcript.jsonl"
      else:
        raise RuntimeError(f"No transcript.jsonl found under directory: {cand}")
    elif cand.is_file():
      # Prefer sibling transcript_full.jsonl if available so truncated tool_calls are preserved
      full_sibling = cand.parent / "transcript_full.jsonl"
      root_log = full_sibling if full_sibling.is_file() else cand
    else:
      raise RuntimeError(f"Transcript path does not exist: {transcript_arg}")

    queue.append(root_log)
    if (
        root_log.parent.name == "logs"
        and root_log.parent.parent.name == ".system_generated"
    ):
      brain_dirs.add(root_log.parent.parent.parent.parent)

  uuid_re = re.compile(
      r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"
  )
  invoke_subagent_re = re.compile(
      r'"conversationId"\s*:\s*"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"'
  )

  while queue:
    log_file = queue.pop(0)
    if log_file in visited_logs or not log_file.is_file():
      continue
    visited_logs.add(log_file)

    raw_text = log_file.read_text(encoding="utf-8", errors="replace")
    spawned_uuids = set(invoke_subagent_re.findall(raw_text))
    # Discover child subagent conversations referenced in this transcript
    for brain_dir in brain_dirs:
      if not brain_dir.is_dir():
        continue
      for sub_uuid in set(uuid_re.findall(raw_text)):
        sub_logs_dir = brain_dir / sub_uuid / ".system_generated" / "logs"
        found_sub = False
        for fname in ("transcript_full.jsonl", "transcript.jsonl"):
          cand_sub = sub_logs_dir / fname
          if cand_sub.is_file():
            found_sub = True
            if cand_sub not in visited_logs:
              queue.append(cand_sub)
            break
        if not found_sub and sub_uuid in spawned_uuids:
          audit.unreachable_subagents.add(sub_uuid)

    for line in raw_text.splitlines():
      line = line.strip()
      if not line:
        continue
      try:
        step = json.loads(line)
      except Exception:
        continue
      for tc in step.get("tool_calls") or []:
        if not isinstance(tc, dict):
          continue
        tname = str(tc.get("name") or "")
        targs = tc.get("args") or {}
        targs_str = json.dumps(targs)

        if tname == "read_file":
          raw_p = str(targs.get("Path") or "").strip().strip('"').strip("'")
          if raw_p:
            audit.read_paths.append(raw_p)
        elif tname == "run_command":
          cmd = str(targs.get("CommandLine") or "").strip().strip('"')
          if "agyhub" in cmd and any(
              v in cmd for v in (" info ", " show ", " describe ")
          ):
            audit.read_paths.append(cmd)
          if "developerknowledge.googleapis.com" in cmd:
            audit.doc_retrieval_invoked = True
        elif tname in ("call_mcp_tool", "search_web") or any(
            k in tname
            for k in ("answer_query", "search_documents", "get_documents")
        ):
          if tname == "search_web" or any(
              k in (tname + " " + targs_str)
              for k in (
                  "answer_query",
                  "search_documents",
                  "get_documents",
                  "developerknowledge",
              )
          ):
            audit.doc_retrieval_invoked = True

  return audit


def strip_fenced_code(md_text: str) -> str:
  """Remove fenced code blocks so headings/links inside code samples do not confuse structural parsing."""
  return re.sub(r"```.*?```", "", md_text, flags=re.DOTALL)


def split_h2_sections(md_text: str) -> List[Tuple[str, str]]:
  """Return list of `(h2_line, section_body)` while ignoring `## ` inside fenced code blocks."""
  lines = md_text.splitlines()
  sections: List[Tuple[str, str]] = []
  current_h2: Optional[str] = None
  buf: List[str] = []
  in_fence = False
  for line in lines:
    stripped = line.lstrip()
    if stripped.startswith("```"):
      in_fence = not in_fence
      if current_h2 is not None:
        buf.append(line)
      continue
    if not in_fence and line.startswith("## "):
      if current_h2 is not None:
        sections.append((current_h2, "\n".join(buf)))
      current_h2 = line.strip()
      buf = []
    elif current_h2 is not None:
      buf.append(line)
  if current_h2 is not None:
    sections.append((current_h2, "\n".join(buf)))
  return sections


def split_h3_subsections(section_body: str) -> List[Tuple[str, str]]:
  """Split an H2 section body into `(h3_line, h3_body)` pairs while respecting fenced code blocks."""
  lines = section_body.splitlines()
  subs: List[Tuple[str, str]] = []
  current_h3: Optional[str] = None
  buf: List[str] = []
  in_fence = False
  for line in lines:
    stripped = line.lstrip()
    if stripped.startswith("```"):
      in_fence = not in_fence
      if current_h3 is not None:
        buf.append(line)
      continue
    if not in_fence and stripped.startswith("### "):
      if current_h3 is not None:
        subs.append((current_h3, "\n".join(buf)))
      current_h3 = stripped.strip()
      buf = []
    elif current_h3 is not None:
      buf.append(line)
  if current_h3 is not None:
    subs.append((current_h3, "\n".join(buf)))
  return subs


def _validate_gcloud_invocation(
    cmd_tokens: List[str], gcloud_tree: Dict[str, Any]
) -> Optional[str]:
  """Validate a single `gcloud ...` token list (after `gcloud`) against `STATIC_COMPLETION_CLI_TREE`."""
  if "--" in cmd_tokens:
    cmd_tokens = cmd_tokens[: cmd_tokens.index("--")]

  node = gcloud_tree
  inherited_flags: Set[str] = set(node.get("flags", {}).keys())
  path = ["gcloud"]
  i = 0
  n = len(cmd_tokens)

  while i < n:
    tok = cmd_tokens[i]
    if tok.startswith("-"):
      flag_name = tok.split("=", 1)[0]
      if "=" not in tok and flag_name in GCLOUD_VALUE_GLOBAL_FLAGS and i + 1 < n:
        i += 2
      else:
        i += 1
      continue
    cmds = node.get("commands", {})
    if tok in cmds:
      node = cmds[tok]
      inherited_flags |= set(node.get("flags", {}).keys())
      path.append(tok)
      i += 1
    else:
      p_str = " ".join(path)
      is_placeholder = any(c in tok for c in "${}<>")
      if cmds and len(path) == 1 and not is_placeholder:
        suggestions = difflib.get_close_matches(tok, sorted(cmds.keys()), n=2, cutoff=0.6)
        hint = f" (did you mean: {', '.join(suggestions)}?)" if suggestions else ""
        return f"Unknown gcloud group '{tok}'{hint}"
      if cmds and tok not in ("help",) and not is_placeholder:
        suggestions = difflib.get_close_matches(tok, sorted(cmds.keys()), n=2, cutoff=0.6)
        hint = f" (did you mean: {', '.join(suggestions)}?)" if suggestions else ""
        return f"Unknown gcloud subcommand '{tok}' under '{p_str}'{hint}"
      break

  p_str = " ".join(path)
  for tok in cmd_tokens:
    if tok.startswith("--") and len(tok) > 2:
      flag_name = tok.split("=", 1)[0]
      if any(c in flag_name for c in "${}<>"):
        continue
      negated_base = "--" + flag_name[5:] if flag_name.startswith("--no-") else None
      if flag_name not in inherited_flags and (
          not negated_base or negated_base not in inherited_flags
      ):
        suggestions = difflib.get_close_matches(
            flag_name, sorted(inherited_flags), n=3, cutoff=0.55
        )
        hint = f" (did you mean: {', '.join(suggestions)}?)" if suggestions else ""
        return f"Hallucinated or invalid gcloud flag '{flag_name}' for '{p_str}'{hint}"
  return None


def _validate_bq_invocation(cmd_tokens: List[str], bq_commands: Set[str]) -> Optional[str]:
  """Validate a `bq ...` invocation's subcommand against `bq.json`."""
  if not bq_commands:
    return None
  i = 0
  n = len(cmd_tokens)
  while i < n:
    tok = cmd_tokens[i]
    if tok.startswith("-"):
      i += 1
      continue
    if any(c in tok for c in "${}<>"):
      return None
    if tok not in bq_commands:
      suggestions = difflib.get_close_matches(tok, sorted(bq_commands), n=2, cutoff=0.55)
      hint = f" (did you mean: {', '.join(suggestions)}?)" if suggestions else ""
      return f"Unknown bq subcommand '{tok}'{hint}"
    return None
  return None


def _validate_code_blocks_in_text(
    md_text: str, cli_schemas: CliSchemas
) -> List[str]:
  """Run deterministic syntax, AST, SQL dialect, and `gcloud`/`bq` CLI checks across all fenced blocks."""
  errors: List[str] = []
  fence_re = re.compile(r"```([^\n`]*)\n(.*?)```", flags=re.DOTALL)

  for block_idx, match in enumerate(fence_re.finditer(md_text), start=1):
    lang_raw = match.group(1).strip()
    lang = lang_raw.split()[0].lower() if lang_raw else ""
    raw_body = match.group(2)
    body = textwrap.dedent(raw_body).strip()

    if not lang:
      errors.append(
          f"Fenced code block #{block_idx} is missing a language identifier (specify sql, bash, yaml, json, python, hcl, lookml, text, or mermaid)"
      )
      continue

    if "{{" in body and "}}" in body:
      errors.append(
          f"Code block #{block_idx} ({lang}) still contains unreplaced template placeholder '{{{{...}}}}'"
      )
      continue

    has_ellipsis = bool(re.search(r"(?:^|\s)\.\.\.(?:\s|$)", body))

    if lang == "json":
      if not has_ellipsis:
        try:
          json.loads(body)
        except Exception as exc:
          msg = str(exc).splitlines()[0]
          errors.append(
              f"Invalid JSON syntax in ```json block #{block_idx} (do not put '//' comments or trailing commas in strict json blocks): {msg}"
          )

    elif lang in ("yaml", "yml"):
      if yaml is not None and not has_ellipsis:
        try:
          list(yaml.safe_load_all(body))
        except Exception as exc:
          msg = str(exc).splitlines()[0]
          errors.append(
              f"Invalid YAML syntax in ```{lang} block #{block_idx} (if LookML or HCL, tag as ```lookml or ```hcl): {msg}"
          )

    elif lang in ("python", "py"):
      if not has_ellipsis:
        try:
          ast.parse(body)
        except SyntaxError as exc:
          errors.append(
              f"Invalid Python syntax in ```{lang} block #{block_idx} (line {exc.lineno}): {exc.msg}"
          )

    elif lang in ("sql", "sqlx", "googlesql"):
      no_comments = re.sub(r"--[^\n]*", "", body)
      no_comments = re.sub(r"/\*.*?\*/", "", no_comments, flags=re.DOTALL)
      for pat, msg in NON_BIGQUERY_SQL_PATTERNS:
        if re.search(pat, no_comments, flags=re.IGNORECASE):
          errors.append(f"SQL block #{block_idx} ({lang}): {msg}")
      if lang == "sqlx" or re.match(r"^\s*config\s*\{", body):
        # Verify balanced braces in Dataform `config { ... }` header if present
        m_cfg = re.match(r"^\s*config\s*\{", body)
        if m_cfg:
          depth = 0
          closed = False
          for ch in body[m_cfg.start() :]:
            if ch == "{":
              depth += 1
            elif ch == "}":
              depth -= 1
              if depth == 0:
                closed = True
                break
          if not closed:
            errors.append(
                f"Dataform SQLX block #{block_idx} has an unclosed 'config {{ ... }}' block"
            )

    elif lang in ("bash", "sh", "shell", "zsh"):
      joined = re.sub(r"\\\s*\n", " ", body)
      for raw_line in joined.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
          continue
        # Strip leading `$ ` prompt if present
        if line.startswith("$ "):
          line = line[2:].strip()
        if line.startswith("gcloud ") or line.startswith("bq "):
          try:
            toks = shlex.split(line, comments=True)
          except ValueError:
            continue
          if not toks:
            continue
          if toks[0] == "gcloud":
            cli_schemas.ensure_loaded()
            if cli_schemas.gcloud_tree is not None:
              err = _validate_gcloud_invocation(toks[1:], cli_schemas.gcloud_tree)
              if err:
                errors.append(f"CLI block #{block_idx}: {err}")
          elif toks[0] == "bq":
            cli_schemas.ensure_loaded()
            if cli_schemas.bq_commands:
              err = _validate_bq_invocation(toks[1:], cli_schemas.bq_commands)
              if err:
                errors.append(f"CLI block #{block_idx}: {err}")

  return errors


def _extract_section_refs(cell_text: str) -> Set[str]:
  """Parse subsection references like `§2.1`, `2.2`, `§2.1-2.3`, `§3.1` from Section 6 Column 2."""
  refs: Set[str] = set()
  # Handle ranges such as `§2.1-§2.4`, `§2.1–2.4`, `2.1..2.3`
  for m_rng in re.finditer(
      r"§?\b(\d+)\.(\d+)\s*(?:-+|–|—|\.\.)\s*§?(?:(\d+)\.)?(\d+)\b", cell_text
  ):
    maj1, min1 = int(m_rng.group(1)), int(m_rng.group(2))
    maj2 = int(m_rng.group(3)) if m_rng.group(3) else maj1
    min2 = int(m_rng.group(4))
    if maj1 == maj2 and min1 <= min2 and (min2 - min1) <= 25:
      for k in range(min1, min2 + 1):
        refs.add(f"{maj1}.{k}")

  for m_single in re.finditer(r"§?\b([23]\.\d+)\b", cell_text):
    refs.add(m_single.group(1))
  return refs


def _validate_iam_matrix(s3_raw_body: str) -> List[str]:
  """Validate Section 3.1 IAM Permissions & Enforcement Matrix for role/permission confusion."""
  errors: List[str] = []
  subs = split_h3_subsections(s3_raw_body)
  s3_1_body = next(
      (b for h, b in subs if h.startswith("### 3.1 IAM Permissions & Enforcement Matrix")),
      None,
  )
  if s3_1_body is None:
    return errors

  table_rows = [l.strip() for l in s3_1_body.splitlines() if l.strip().startswith("|")]
  if len(table_rows) < 3:
    return errors

  # Match both IAM v1 (`<service>.<resource>.<verb>`) and IAM v2 Deny (`<service>.googleapis.com/<resource>.<verb>`)
  iam_perm_re = re.compile(
      r"^[a-z][a-z0-9-]*(?:\.googleapis\.com/[a-zA-Z0-9_]+|\.[a-zA-Z0-9_]+)\.[a-zA-Z0-9_*]+$"
  )
  for row_idx, row in enumerate(table_rows[2:], start=1):
    cells = [c.strip() for c in row.strip("|").split("|")]
    if len(cells) < 3:
      continue
    op_col, perm_col = cells[0], cells[1]
    if re.search(r"\b(?:n/?a|none|not applicable)\b", perm_col, flags=re.IGNORECASE):
      continue
    code_tokens = [t.strip() for t in re.findall(r"`([^`]+)`", perm_col) if t.strip()]
    for tok in code_tokens:
      if tok.startswith("roles/"):
        errors.append(
            f"Section 3.1 row #{row_idx} ({op_col}): IAM role '{tok}' placed in 'Required IAM Permission(s)' column (move 'roles/...' to Column 3 and list granular '<service>.<resource>.<verb>' permissions in Column 2)"
        )
    has_valid_perm = any(iam_perm_re.match(tok) for tok in code_tokens)
    if not has_valid_perm:
      errors.append(
          f"Section 3.1 row #{row_idx} ({op_col}): 'Required IAM Permission(s)' column must cite at least one valid 3-part Google Cloud IAM permission (`<service>.<resource>.<verb>`), got: {perm_col}"
      )
  return errors


def _verify_doc_urls(s5_body: str) -> List[str]:
  """Check HTTP reachability of Section 5 documentation URLs when `--verify-urls` is enabled."""
  errors: List[str] = []
  urls = sorted(set(re.findall(r"https://[^\s)\]>\"']+", s5_body)))
  for url in urls:
    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "gcp-project-copilot-validator/2.0"},
    )
    try:
      with urllib.request.urlopen(req, timeout=8) as resp:
        if resp.status >= 400:
          errors.append(f"Section 5 URL returned HTTP {resp.status}: {url}")
    except urllib.error.HTTPError as exc:
      # Retry with GET on 405 Method Not Allowed
      if exc.code == 405:
        try:
          req_get = urllib.request.Request(
              url, headers={"User-Agent": "gcp-project-copilot-validator/2.0"}
          )
          with urllib.request.urlopen(req_get, timeout=8) as resp2:
            if resp2.status >= 400:
              errors.append(f"Section 5 URL returned HTTP {resp2.status}: {url}")
        except Exception as exc2:
          errors.append(f"Section 5 URL unreachable ({exc2}): {url}")
      else:
        errors.append(f"Section 5 URL returned HTTP {exc.code}: {url}")
    except Exception as exc:
      errors.append(f"Section 5 URL check failed ({exc}): {url}")
  return errors


def validate_file(
    md_path: Path,
    customer_name: Optional[str],
    catalog: SkillCatalog,
    cli_schemas: CliSchemas,
    require_active_skills: bool = False,
    legacy_section6: bool = False,
    transcript_audit: Optional[TranscriptAuditData] = None,
    verify_urls: bool = False,
) -> Tuple[List[str], List[str]]:
  """Validate a single question evaluation Markdown file and return `(errors, warnings)`."""
  errors: List[str] = []
  warnings: List[str] = []
  text = md_path.read_text(encoding="utf-8")
  lines = text.splitlines()

  code_match = re.match(r"^([A-Z]\d+-Q\d+)_", md_path.name)
  expected_code = code_match.group(1) if code_match else None
  if not expected_code:
    errors.append(
        f"Filename '{md_path.name}' does not match '<DOMAIN_ID>-Q<NN>_<slug>.md'"
    )

  # 1. Dual H1 Header & Top Metadata Region (before first '---')
  try:
    hr_idx = next(i for i, l in enumerate(lines) if l.strip() == "---")
  except StopIteration:
    errors.append("Missing '---' horizontal rule separating header metadata from Section 1")
    return errors, warnings

  header_lines = [l.strip() for l in lines[:hr_idx] if l.strip()]
  h1_lines = [l for l in header_lines if l.startswith("# ")]
  if len(h1_lines) != 2:
    errors.append(
        f"Expected exactly 2 H1 ('# ') lines before first '---', found {len(h1_lines)}"
    )
  else:
    if h1_lines[0] != "# **Technical Question Evaluation & Architectural Answer**":
      errors.append(
          "Line 1 H1 must be '# **Technical Question Evaluation & Architectural Answer**'"
      )
    if expected_code and f"[{expected_code}]" not in h1_lines[1]:
      errors.append(
          f"Second H1 must contain '[{expected_code}]', got: {h1_lines[1]}"
      )
    if customer_name and customer_name not in h1_lines[1]:
      errors.append(
          f"Second H1 must include customer name '{customer_name}', got: {h1_lines[1]}"
      )

  non_table_header = [
      l for l in header_lines if not l.startswith("# ") and not l.startswith("|")
  ]
  if non_table_header:
    errors.append(
        f"Unexpected non-table lines in top header block: {non_table_header[:2]}"
    )

  table_lines = [l for l in header_lines if l.startswith("|")]
  if len(table_lines) < 9:
    errors.append(
        f"Top metadata table must have header + separator + 7 rows (9 lines), found {len(table_lines)}"
    )
  else:
    hdr_cells = [c.strip() for c in table_lines[0].strip("|").split("|")]
    if hdr_cells != ["Metadata Field", "Document Detail"]:
      errors.append(
          f"Metadata table header must be '| Metadata Field | Document Detail |', got: {table_lines[0]}"
      )
    meta_rows = table_lines[2:]
    meta_keys = [r.split("|")[1].strip() for r in meta_rows if "|" in r]
    if meta_keys != EXPECTED_META_KEYS:
      errors.append(
          f"Metadata table keys mismatch: expected {EXPECTED_META_KEYS}, got {meta_keys}"
      )
    else:
      meta_map = {
          r.split("|")[1].strip(): "|".join(r.split("|")[2:-1]).strip()
          for r in meta_rows
      }
      if expected_code and f"[{expected_code}]" not in meta_map["**Question ID**"]:
        errors.append(f"'**Question ID**' cell must contain '[{expected_code}]'")
      if not meta_map["**Question**"] or len(meta_map["**Question**"]) < 15:
        errors.append("'**Question**' cell must contain the verbatim question text")
      if "specs_project.md" not in meta_map["**Canonical Domain**"]:
        errors.append("'**Canonical Domain**' cell must link to specs_project.md")
      if (
          "../meetings/" not in meta_map["**Source Session & Log**"]
          or "../common/project_questions-log.md"
          not in meta_map["**Source Session & Log**"]
      ):
        errors.append(
            "'**Source Session & Log**' must link both '../meetings/...' and '../common/project_questions-log.md'"
        )
      if not re.search(r"\b20\d{2}-\d{2}-\d{2}\b", meta_map["**Date Answered**"]):
        errors.append("'**Date Answered**' must contain an ISO date (YYYY-MM-DD)")

  # 2. Validate 6 Canonical H2 Sections (fence-aware so raw code blocks are preserved per section)
  raw_sections = split_h2_sections(text)
  actual_h2s = [h for h, _ in raw_sections]

  sec4_expected = (
      f"## 4. Summary Recommendation & Next Steps for {customer_name}"
      if customer_name
      else None
  )
  expected_h2s = [
      "## 1. Executive Summary & Solution Matrix",
      "## 2. Technical Evaluation & Google Cloud Architecture",
      "## 3. IAM Permissions, Security Guardrails & Platform Caveats",
      sec4_expected or "## 4. Summary Recommendation & Next Steps for ",
      "## 5. Google Cloud Documentation Reference Links",
      "## 6. Skills Employed",
  ]

  if len(actual_h2s) != 6:
    errors.append(
        f"Expected 6 canonical H2 sections, found {len(actual_h2s)}: {actual_h2s}"
    )
  else:
    for idx, (act, exp) in enumerate(zip(actual_h2s, expected_h2s), start=1):
      if idx == 4 and sec4_expected is None:
        if not act.startswith(exp):
          errors.append(f"Section 4 H2 mismatch: got '{act}'")
      elif act != exp:
        errors.append(f"Section {idx} H2 mismatch: expected '{exp}', got '{act}'")

  if len(raw_sections) == 6:
    s1_raw = raw_sections[0][1]
    s2_raw = raw_sections[1][1]
    s3_raw = raw_sections[2][1]
    s4_raw = raw_sections[3][1]
    s5_raw = raw_sections[4][1]
    s6_raw = raw_sections[5][1]

    s1_body = strip_fenced_code(s1_raw)
    s2_body = strip_fenced_code(s2_raw)
    s3_body = strip_fenced_code(s3_raw)
    s4_body = strip_fenced_code(s4_raw)
    s5_body = strip_fenced_code(s5_raw)
    s6_body = strip_fenced_code(s6_raw)

    if not re.search(r"^\|.+\|\s*$", s1_body, flags=re.MULTILINE):
      errors.append("Section 1 must include a Markdown Solution Matrix table")

    # Parse Section 2 subsections & track which `2.x` subsections contain executable/config code blocks
    s2_subs = split_h3_subsections(s2_raw)
    s2_h3s = [h for h, _ in s2_subs]
    valid_section_ids: Set[str] = {"3.1", "3.2"}
    code_bearing_sections: Set[str] = set()

    if len(s2_h3s) < 2:
      errors.append(
          f"Section 2 must include at least 2 numbered '### 2.x <Title>' subsections, found {len(s2_h3s)}"
      )
    else:
      for sub_idx, (h3_line, h3_raw_body) in enumerate(s2_subs, start=1):
        sec_id = f"2.{sub_idx}"
        valid_section_ids.add(sec_id)
        expected_prefix = f"### {sec_id} "
        if not h3_line.startswith(expected_prefix) or len(h3_line) <= len(expected_prefix):
          errors.append(
              f"Section 2 subsection #{sub_idx} must start with '{expected_prefix}<Title>', got: '{h3_line}'"
          )
        m_dup = re.match(
            r"^### 2\.\d+\s+(Pattern|Control|Step|Stage)\s+[A-Z0-9]+\s*(?:—|:|-)\s*(.+)$",
            h3_line,
            flags=re.IGNORECASE,
        )
        if m_dup:
          noun, rest = m_dup.group(1), m_dup.group(2)
          rest_main = re.sub(r"\([^)]*\)", "", rest)
          if re.search(rf"\b{re.escape(noun)}s?\b", rest_main, flags=re.IGNORECASE):
            errors.append(
                f"Tautological repetition of '{noun}' in Section 2 heading: '{h3_line}'"
            )

        for lang_m in re.finditer(r"```([^\n`]*)\n", h3_raw_body):
          lang_tok = lang_m.group(1).strip().split()[0].lower() if lang_m.group(1).strip() else ""
          if lang_tok in EXECUTABLE_CODE_LANGS or not lang_tok:
            code_bearing_sections.add(sec_id)

    # Check Section 3 structure + Gate E (IAM Permission & Role Grammar)
    if "### 3.1 IAM Permissions & Enforcement Matrix" not in s3_body:
      errors.append(
          "Section 3 must include '### 3.1 IAM Permissions & Enforcement Matrix'"
      )
    if "### 3.2 Critical Architectural Caveats & Edge Cases" not in s3_body:
      errors.append(
          "Section 3 must include '### 3.2 Critical Architectural Caveats & Edge Cases'"
      )
    if not re.search(r"^\|.+\|\s*$", s3_body, flags=re.MULTILINE):
      errors.append("Section 3.1 must include an IAM Permissions Markdown table")
    else:
      code_bearing_sections.add("3.1")
      errors.extend(_validate_iam_matrix(s3_raw))

    if "> [!IMPORTANT]" not in s3_body:
      errors.append("Section 3.2 must include at least one '> [!IMPORTANT]' callout")

    if "> [!TIP]" not in s4_body:
      errors.append("Section 4 must include a '> [!TIP]' recommendation callout")
    if "../common/project_questions-log.md" not in s4_body:
      errors.append(
          "Section 4 must include a relative link to '../common/project_questions-log.md'"
      )
    if "../common/project_challenges.md" not in s4_body:
      errors.append(
          "Section 4 must include a relative link to '../common/project_challenges.md'"
      )

    if "https://" not in s5_body:
      errors.append("Section 5 must include official Google Cloud documentation URLs")
    elif verify_urls:
      errors.extend(_verify_doc_urls(s5_body))

    # Gate A, Gate B & Gate F — Section 6 Skill Validation Matrix
    s6_table_lines = [
        l.strip() for l in s6_body.splitlines() if l.strip().startswith("|")
    ]
    is_4col = bool(
        re.search(
            r"\|\s*External Skill\s*\|\s*Validated Sections & Code Blocks\s*\|\s*Grounding Artifacts Consulted\s*\|\s*Technical Contribution to This Evaluation\s*\|",
            s6_body,
        )
    )
    is_legacy_2col = bool(
        re.search(
            r"\|\s*Workspace Skill\s*\|\s*Technical Contribution to This Evaluation\s*\|",
            s6_body,
        )
    )

    if not is_4col and not (legacy_section6 and is_legacy_2col):
      errors.append(
          "Section 6 must use the 4-column validation matrix header: '| External Skill | Validated Sections & Code Blocks | Grounding Artifacts Consulted | Technical Contribution to This Evaluation |'"
      )
    elif len(s6_table_lines) < 3:
      errors.append("Section 6 table must list at least one external Google Cloud / technical skill")
    else:
      covered_sections: Set[str] = set()
      valid_external_row_count = 0

      for row_idx, rline in enumerate(s6_table_lines[2:], start=1):
        cells = [c.strip() for c in rline.strip("|").split("|")]
        expected_cols = 4 if is_4col else 2
        if len(cells) < expected_cols:
          errors.append(
              f"Section 6 row #{row_idx} has {len(cells)} columns, expected {expected_cols}: {rline}"
          )
          continue

        raw_skill = cells[0]
        skill_name = re.sub(r"[*`]", "", raw_skill).strip()
        if not skill_name or "{{" in skill_name:
          errors.append(
              f"Section 6 row #{row_idx} contains an empty or unreplaced skill placeholder: {raw_skill}"
          )
          continue

        # 1. Strictly reject agyhub internal skills & IDE builtin/meta/doc skills (ALWAYS [FAIL])
        if (
            skill_name in catalog.forbidden_skills
            or skill_name.startswith("agyhub-")
        ):
          errors.append(
              f"Section 6 forbids agyhub internal / IDE meta skill '{skill_name}' (list only external Google Cloud / technical domain skills)"
          )
          continue

        valid_external_row_count += 1
        skill_dir = catalog.external_skills.get(skill_name)

        # 2. Active vs. Deprecated External Skill Lifecycle Check
        effective_require_active = require_active_skills or (transcript_audit is not None)
        if skill_dir is None:
          if effective_require_active:
            errors.append(
                f"Section 6 skill '{skill_name}' is not an active external skill in the catalog (new or regenerated answers must strictly use currently active external skills)"
            )
          else:
            warnings.append(
                f"Section 6 skill '{skill_name}' is not in the live external catalog (preserved as a historical/deprecated external skill reference; replace with active skills only if regenerating the answer)"
            )
        else:
          if (
              effective_require_active
              and catalog.active_external_skills
              and skill_name not in catalog.active_external_skills
          ):
            errors.append(
                f"Section 6 skill '{skill_name}' exists in the hub catalog ({skill_dir}) but is not enabled in the active workspace (.agents/skills.json or plugins.json)"
            )

        # 3. 4-Column Coverage & On-Disk Grounding Artifact Verification
        if is_4col:
          sec_cell, art_cell, contrib_cell = cells[1], cells[2], cells[3]
          if not sec_cell or "{{" in sec_cell:
            errors.append(
                f"Section 6 skill '{skill_name}' must specify 'Validated Sections & Code Blocks' (e.g., `§2.1`, `§3.1`)"
            )
          else:
            row_refs = _extract_section_refs(sec_cell)
            for ref in sorted(row_refs):
              if ref not in valid_section_ids:
                errors.append(
                    f"Section 6 skill '{skill_name}' claims non-existent subsection '§{ref}'"
                )
            covered_sections.update(row_refs)

          if not art_cell or "{{" in art_cell:
            errors.append(
                f"Section 6 skill '{skill_name}' must specify 'Grounding Artifacts Consulted' (e.g., `SKILL.md`, `references/...`, or live doc URI)"
            )
          elif skill_dir is not None:
            # Verify any cited relative skill files (`SKILL.md`, `references/...`, etc.) actually exist on disk
            cited_rel_files = re.findall(
                r"(?:SKILL\.md|[A-Z][A-Z0-9_]+\.md|(?:references|examples|resources|scripts)/[A-Za-z0-9_./-]+)",
                art_cell,
            )
            if not cited_rel_files and skill_name != "retrieving-developer-knowledge":
              errors.append(
                  f"Section 6 skill '{skill_name}' must cite at least `SKILL.md` (or a specific `references/<file>.md`) in 'Grounding Artifacts Consulted', got: {art_cell}"
              )
            for rel_f in cited_rel_files:
              rel_clean = rel_f.rstrip(".,;:)")
              if "*" in rel_clean:
                errors.append(
                    f"Section 6 skill '{skill_name}' cites wildcard '{rel_clean}' in 'Grounding Artifacts Consulted' (cite the exact file(s) actually read)"
                )
              elif not (skill_dir / rel_clean).is_file():
                errors.append(
                    f"Section 6 skill '{skill_name}' cites non-existent file '{rel_clean}' (not found under {skill_dir})"
                )

          if not contrib_cell or "{{" in contrib_cell or len(contrib_cell) < 15:
            errors.append(
                f"Section 6 skill '{skill_name}' must provide a specific 'Technical Contribution to This Evaluation'"
            )

        # 4. Gate F — Optional Execution Transcript Verification (`--transcript`)
        if transcript_audit is not None:
          sub_hint = (
              f" (note: spawned subagent log(s) {sorted(transcript_audit.unreachable_subagents)} are isolated from the parent shell sandbox — run `--transcript <appDataDir>/brain/<subagent-id>` inside each subagent session)"
              if transcript_audit.unreachable_subagents
              else ""
          )
          matched_read = any(
              f"/{skill_name}/" in rp
              or rp.endswith(f"/{skill_name}")
              or (
                  "agyhub" in rp
                  and re.search(rf"\b{re.escape(skill_name)}\b", rp)
              )
              for rp in transcript_audit.read_paths
          )
          if skill_name == "retrieving-developer-knowledge":
            if not (matched_read or transcript_audit.doc_retrieval_invoked):
              errors.append(
                  f"Transcript audit failed: 'retrieving-developer-knowledge' is listed in Section 6, but neither SKILL.md read nor any live Developer Knowledge / documentation lookup was recorded in transcript.jsonl{sub_hint}"
              )
            elif not transcript_audit.doc_retrieval_invoked:
              errors.append(
                  f"Transcript audit failed: 'retrieving-developer-knowledge' SKILL.md was read, but no live documentation retrieval call (search_documents / get_documents / answer_query / REST API) was executed in transcript.jsonl{sub_hint}"
              )
          elif not matched_read:
            errors.append(
                f"Transcript audit failed: skill '{skill_name}' is listed in Section 6, but `read_file` was never called on '{skill_name}/SKILL.md' in transcript.jsonl{sub_hint}"
            )

      if valid_external_row_count == 0:
        errors.append(
            "Section 6 must include at least one valid external Google Cloud / technical domain skill"
        )

      if is_4col and code_bearing_sections:
        uncovered = sorted(code_bearing_sections - covered_sections)
        if uncovered:
          fmt_uncovered = ", ".join(f"§{s}" for s in uncovered)
          errors.append(
              f"100% Skill-Validation Coverage violation: code/IAM subsection(s) {fmt_uncovered} are not mapped to any external skill in Section 6 ('Validated Sections & Code Blocks')"
          )

  # 3. Gate C & Gate D — Code Block Syntax, Dialect & Offline CLI Flag Validation
  errors.extend(_validate_code_blocks_in_text(text, cli_schemas))

  # 4. Repository Path Portability & Mermaid Syntax Hygiene
  non_code = strip_fenced_code(text)
  if "file://" in non_code or re.search(r"\(/usr/", non_code):
    errors.append(
        "Repository Markdown must use portable relative paths (found 'file://' or '/usr/...')"
    )

  for idx, m_block in enumerate(
      re.findall(r"```mermaid\s*(.*?)```", text, flags=re.DOTALL), start=1
  ):
    if re.search(r"<br\s*/?>", m_block, flags=re.IGNORECASE):
      errors.append(
          f"Mermaid block #{idx} contains HTML '<br>' tag (breaks Mermaid rendering)"
      )
    if ";" in m_block:
      errors.append(
          f"Mermaid block #{idx} contains semicolon ';' (acts as statement terminator in Mermaid)"
      )

  return errors, warnings


def collect_target_files(
    workspace_root: Path, cli_files: Optional[List[str]]
) -> List[Path]:
  """Resolve list of question Markdown files to validate."""
  if not cli_files:
    q_dir = workspace_root / "project" / "questions-answered"
    if not q_dir.is_dir():
      legacy_q_dir = workspace_root / "project" / "questions"
      if legacy_q_dir.is_dir():
        q_dir = legacy_q_dir
      else:
        raise RuntimeError(f"Questions directory does not exist: {q_dir}")
    return [
        p
        for p in sorted(q_dir.glob("*.md"))
        if not p.name.endswith("-gdoc-tmp.md")
    ]

  resolved: List[Path] = []
  for raw in cli_files:
    cand = Path(raw).expanduser()
    if not cand.is_absolute():
      cand = (workspace_root / cand).resolve()
    else:
      cand = cand.resolve()
    if cand.is_dir():
      resolved.extend(
          p
          for p in sorted(cand.glob("*.md"))
          if not p.name.endswith("-gdoc-tmp.md")
      )
    elif cand.is_file():
      if not cand.name.endswith("-gdoc-tmp.md"):
        resolved.append(cand)
    else:
      raise RuntimeError(f"Target path does not exist: {raw}")
  return resolved


def main() -> int:
  parser = argparse.ArgumentParser(
      description=(
          "Validate project/questions-answered/*.md files against "
          "resources/templates/template_answers_to_questions.md and anti-hallucination gates."
      )
  )
  parser.add_argument(
      "--workspace",
      "-w",
      default=None,
      help="Target customer workspace root directory (auto-detected if omitted)",
  )
  parser.add_argument(
      "--file",
      "-f",
      action="append",
      default=None,
      help="Optional specific file or directory path(s) to validate (repeatable)",
  )
  parser.add_argument(
      "--require-active-skills",
      action="store_true",
      help=(
          "Require every Section 6 skill to be a currently active external skill in the workspace/catalog "
          "(use for all newly authored or completely regenerated answers; historical runs emit [WARN] on deprecated external skills)."
      ),
  )
  parser.add_argument(
      "--transcript",
      action="append",
      default=None,
      help=(
          "Optional path(s) to Antigravity transcript.jsonl / transcript_full.jsonl (or conversation directory, repeatable) "
          "to log-verify that every Section 6 skill was genuinely read/invoked during the session."
      ),
  )
  parser.add_argument(
      "--verify-urls",
      action="store_true",
      help="Perform live HTTP reachability checks on Section 5 Google Cloud documentation URLs.",
  )
  parser.add_argument(
      "--legacy-section6",
      action="store_true",
      help="Allow legacy 2-column Section 6 table header when auditing pre-v2 historical archives.",
  )
  args = parser.parse_args()

  workspace_root = resolve_workspace_root(args.workspace)
  customer_name = extract_customer_name(
      workspace_root / "specs" / "specs_project.md"
  )
  targets = collect_target_files(workspace_root, args.file)

  if not targets:
    print("No question Markdown files found to validate.")
    return 0

  catalog = discover_skill_catalog(workspace_root)
  cli_schemas = CliSchemas()
  transcript_audit = (
      load_transcript_audit(args.transcript) if args.transcript else None
  )

  passed = 0
  failed = 0
  warned_files = 0
  for md_path in targets:
    rel = (
        os.path.relpath(md_path, workspace_root)
        if str(md_path).startswith(str(workspace_root))
        else str(md_path)
    )
    errs, warns = validate_file(
        md_path,
        customer_name,
        catalog=catalog,
        cli_schemas=cli_schemas,
        require_active_skills=args.require_active_skills,
        legacy_section6=args.legacy_section6,
        transcript_audit=transcript_audit,
        verify_urls=args.verify_urls,
    )
    if warns:
      warned_files += 1
    if errs:
      failed += 1
      print(f"[FAIL] {rel}")
      for e in errs:
        print(f"  - {e}")
      for w in warns:
        print(f"  - [WARN] {w}")
    else:
      passed += 1
      if warns:
        print(f"[PASS with WARN] {rel}")
        for w in warns:
          print(f"  - [WARN] {w}")

  summary_extra = []
  if customer_name:
    summary_extra.append(f"Customer: {customer_name}")
  if warned_files:
    summary_extra.append(f"Files with warnings: {warned_files}")
  suffix = f" ({', '.join(summary_extra)})" if summary_extra else ""
  print(
      f"\n[Validation Summary] {passed}/{len(targets)} passed, {failed}/{len(targets)} failed{suffix}"
  )
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())
