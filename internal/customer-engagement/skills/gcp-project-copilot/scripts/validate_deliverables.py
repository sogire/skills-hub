#!/usr/bin/env python3
"""Validate customer-facing deliverable Markdown files in project/deliverables/docs/ against template_deliverable.md.

Workspace-agnostic structural, customer-cleanliness, and anti-hallucination validator for `gcp-project-copilot`:
1. Resolves `<workspace-root>` via `--workspace` / `-w` or upward search for `specs/specs_project.md`.
2. Dynamically extracts `CUSTOMER_NAME` from `<workspace-root>/specs/specs_project.md` (zero hardcoded IDs).
3. Enforces 5 Clean Customer-Deliverable Gates against `resources/templates/template_deliverable.md`:
   - Gate 1 (Structure & Clean Metadata Table): Dual H1 header, exact 5-row customer metadata table
     (`Customer / Initiative`, `Deliverable Type & Audience`, `Architectural Scope`, `Document Version`, `Date`),
     and 6 canonical `##` sections (`1`..`6`) including `### 6.1 Official Google Cloud Documentation` and
     `### 6.2 Internal Working Sources (Filename Reference Only)`.
   - Gate 2 (Zero Internal Links & Public-Only Hyperlinks): Rejects any non-image Markdown link `[text](target)`
     pointing to local/relative paths (`../`, `./`, `working-process/`, `questions-answered/`, `common/`,
     `meetings/`, `specs/`), `file://`, `/usr/...`, or internal Google Docs/Drive URLs (`docs.google.com`,
     `drive.google.com`). Only public external `https://` links are permitted in Section 1..6.1, and Section 6.2
     must list plain-code `.md` filenames only with zero URLs or hyperlinks.
   - Gate 3 (Zero Inline Question Codes in Header & Sections 1..5): Rejects `[D#-Q##]` / `[P#-Q##]` or bare
     `D#-Q##` / `P#-Q##` question codes in the title, metadata table, and Sections 1..5 (and 6.1). Question
     filenames (`D1-Q01_...md`) may appear only in `### 6.2 Internal Working Sources (Filename Reference Only)`.
   - Gate 4 (Embedded Local Diagram Verification): Verifies that all embedded local images `![alt](../diagrams/...)`
     exist on disk.
   - Gate 5 (Code Block AST, Offline `gcloud`/`bq` CLI Schema & Mermaid Hygiene): Validates `json`, `yaml`,
     `python`, `sql`/`sqlx`, `gcloud`/`bq` CLI flags, and forbids `;` or `<br>` inside `mermaid` blocks.
"""

import argparse
import os
from pathlib import Path
import re
import sys
from typing import List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
  sys.path.insert(0, str(SCRIPT_DIR))

import validate_question_answers as vqa  # pylint: disable=import-error,wrong-import-position

EXPECTED_DELIVERABLE_META_KEYS = [
    "**Customer / Initiative**",
    "**Deliverable Type & Audience**",
    "**Architectural Scope**",
    "**Document Version**",
    "**Date**",
]

QUESTION_CODE_RE = re.compile(r"\[?[DP]\d+-Q\d+\]?")
NON_IMAGE_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
IMAGE_LINK_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def validate_deliverable_file(
    md_path: Path,
    customer_name: Optional[str],
    cli_schemas: vqa.CliSchemas,
    verify_urls: bool = False,
) -> Tuple[List[str], List[str]]:
  """Validate a single customer deliverable Markdown file and return `(errors, warnings)`."""
  errors: List[str] = []
  warnings: List[str] = []
  text = md_path.read_text(encoding="utf-8")
  lines = text.splitlines()

  if "{{" in vqa.strip_fenced_code(text) and "}}" in vqa.strip_fenced_code(text):
    errors.append("Document still contains unreplaced '{{...}}' template placeholders")

  # Gate 1 — Dual H1 Header & Top 5-Row Metadata Table (before first '---')
  try:
    hr_idx = next(i for i, l in enumerate(lines) if l.strip() == "---")
  except StopIteration:
    errors.append("Missing '---' horizontal rule separating header metadata from Section 1")
    return errors, warnings

  header_text = "\n".join(lines[:hr_idx])
  header_lines = [l.strip() for l in lines[:hr_idx] if l.strip()]
  h1_lines = [l for l in header_lines if l.startswith("# ")]
  if len(h1_lines) != 2:
    errors.append(
        f"Expected exactly 2 H1 ('# ') lines before first '---', found {len(h1_lines)}"
    )
  elif customer_name and customer_name not in h1_lines[1]:
    errors.append(
        f"Second H1 must include customer name '{customer_name}', got: {h1_lines[1]}"
    )

  table_lines = [l for l in header_lines if l.startswith("|")]
  if len(table_lines) < 7:
    errors.append(
        f"Top metadata table must have header + separator + 5 rows (7 lines), found {len(table_lines)}"
    )
  else:
    hdr_cells = [c.strip() for c in table_lines[0].strip("|").split("|")]
    if hdr_cells != ["Metadata Field", "Document Detail"]:
      errors.append(
          f"Metadata table header must be '| Metadata Field | Document Detail |', got: {table_lines[0]}"
      )
    meta_rows = table_lines[2:]
    meta_keys = [r.split("|")[1].strip() for r in meta_rows if "|" in r]
    if meta_keys != EXPECTED_DELIVERABLE_META_KEYS:
      errors.append(
          f"Metadata table keys mismatch: expected {EXPECTED_DELIVERABLE_META_KEYS}, got {meta_keys}"
      )
    else:
      meta_map = {
          r.split("|")[1].strip(): "|".join(r.split("|")[2:-1]).strip()
          for r in meta_rows
      }
      if not re.search(r"\b20\d{2}-\d{2}-\d{2}\b", meta_map["**Date**"]):
        errors.append("'**Date**' cell must contain an ISO date (YYYY-MM-DD)")

  # Check 6 Canonical H2 Sections
  raw_sections = vqa.split_h2_sections(text)
  actual_h2s = [h for h, _ in raw_sections]
  sec5_expected = (
      f"## 5. Implementation Roadmap & Recommended Next Steps for {customer_name}"
      if customer_name
      else None
  )
  expected_h2s = [
      "## 1. Executive Summary & Architectural Decisions",
      "## 2. Customer Context, Current State & Core Challenges",
      "## 3. Recommended Google Cloud Target Architecture",
      "## 4. Detailed Technical Design, Security & FinOps Guardrails",
      sec5_expected or "## 5. Implementation Roadmap & Recommended Next Steps for ",
      "## 6. References & Source Traceability",
  ]

  if len(actual_h2s) != 6:
    errors.append(
        f"Expected 6 canonical H2 sections, found {len(actual_h2s)}: {actual_h2s}"
    )
  else:
    for idx, (act, exp) in enumerate(zip(actual_h2s, expected_h2s), start=1):
      if idx == 5 and sec5_expected is None:
        if not act.startswith(exp):
          errors.append(f"Section 5 H2 mismatch: got '{act}'")
      elif act != exp:
        errors.append(f"Section {idx} H2 mismatch: expected '{exp}', got '{act}'")

  # Inspect Section 6 subsections (6.1 and 6.2)
  s6_raw = raw_sections[5][1] if len(raw_sections) == 6 else ""
  s6_subs = vqa.split_h3_subsections(s6_raw) if s6_raw else []
  s6_1_body = next(
      (b for h, b in s6_subs if h.startswith("### 6.1 Official Google Cloud Documentation")),
      None,
  )
  s6_2_body = next(
      (b for h, b in s6_subs if h.startswith("### 6.2 Internal Working Sources (Filename Reference Only)")),
      None,
  )

  if len(raw_sections) == 6:
    if s6_1_body is None:
      errors.append(
          "Section 6 must include '### 6.1 Official Google Cloud Documentation'"
      )
    elif "https://" not in s6_1_body:
      errors.append(
          "Section 6.1 must include at least one public 'https://' official documentation link"
      )
    elif verify_urls:
      errors.extend(vqa._verify_doc_urls(vqa.strip_fenced_code(s6_1_body)))  # pylint: disable=protected-access

    if s6_2_body is None:
      errors.append(
          "Section 6 must include '### 6.2 Internal Working Sources (Filename Reference Only)'"
      )
    else:
      s6_2_clean = vqa.strip_fenced_code(s6_2_body)
      if NON_IMAGE_LINK_RE.search(s6_2_clean) or "http://" in s6_2_clean or "https://" in s6_2_clean:
        errors.append(
            "Section 6.2 ('Internal Working Sources') must list plain filenames only — zero Markdown links or URLs are permitted"
        )
      cited_md_files = re.findall(r"`?([A-Za-z0-9_.-]+\.md)`?", s6_2_clean)
      if not cited_md_files:
        errors.append(
            "Section 6.2 ('Internal Working Sources') must list at least one internal '.md' filename (e.g., `* `source-file.md``)"
        )
      for cited in cited_md_files:
        if "/" in cited or "\\" in cited:
          errors.append(
              f"Section 6.2 source '{cited}' must be a plain filename basename without directory slashes"
          )

  # Gate 2 — Zero Internal Hyperlinks Across Entire Document
  non_code_full = vqa.strip_fenced_code(text)
  for match in NON_IMAGE_LINK_RE.finditer(non_code_full):
    label, target = match.group(1), match.group(2).strip()
    if target.startswith("#"):
      continue
    if not target.startswith(("https://", "http://")):
      errors.append(
          f"Forbidden internal/relative hyperlink '[{label}]({target})' in customer deliverable (only public external URLs are permitted)"
      )
    elif any(
        internal_host in target.lower()
        for internal_host in (
            "docs.google.com",
            "drive.google.com",
            "who/",
            "corp.google.com",
        )
    ):
      errors.append(
          f"Forbidden internal Google Docs/Drive/Corp URL '[{label}]({target})' in customer deliverable (use public external URLs only)"
      )

  if "file://" in non_code_full or re.search(r"\(/usr/", non_code_full):
    errors.append(
        "Forbidden 'file://' or '/usr/...' path found in deliverable Markdown"
    )

  # Gate 3 — Zero Inline Question Codes ([D#-Q##] / [P#-Q##]) Outside Section 6.2
  body_without_s6_2 = header_text
  if len(raw_sections) == 6:
    body_without_s6_2 += "\n" + "\n".join(b for _, b in raw_sections[:5])
    if s6_1_body:
      body_without_s6_2 += "\n" + s6_1_body
  else:
    body_without_s6_2 = text

  found_q_codes = sorted(set(QUESTION_CODE_RE.findall(vqa.strip_fenced_code(body_without_s6_2))))
  if found_q_codes:
    errors.append(
        f"Forbidden inline question code(s) {found_q_codes} found in deliverable header or Sections 1–5/6.1 (customer deliverables must not contain internal question codes; cite question filenames only in Section 6.2)"
    )

  # Gate 4 — Verify Embedded Local Diagrams Exist on Disk
  base_dir = md_path.parent
  for img_m in IMAGE_LINK_RE.finditer(non_code_full):
    alt_txt, raw_target = img_m.group(1), img_m.group(2).strip()
    if raw_target.startswith(("https://", "http://", "data:")):
      continue
    clean_target = raw_target.split("#")[0].split("?")[0]
    abs_img = (base_dir / clean_target).resolve()
    if not abs_img.is_file():
      errors.append(
          f"Embedded diagram '![{alt_txt}]({raw_target})' does not exist at {abs_img}"
      )

  # Gate 5 — Code Block Syntax, CLI Schema & Mermaid Hygiene
  errors.extend(vqa._validate_code_blocks_in_text(text, cli_schemas))  # pylint: disable=protected-access

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


def collect_target_deliverables(
    workspace_root: Path, cli_files: Optional[List[str]]
) -> List[Path]:
  """Resolve list of customer deliverable Markdown files to validate."""
  if not cli_files:
    d_dir = workspace_root / "project" / "deliverables" / "docs"
    if not d_dir.is_dir():
      return []
    return [
        p
        for p in sorted(d_dir.glob("*.md"))
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
      docs_sub = cand / "docs" if (cand / "docs").is_dir() else cand
      resolved.extend(
          p
          for p in sorted(docs_sub.glob("*.md"))
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
          "Validate project/deliverables/docs/*.md customer deliverables against "
          "resources/templates/template_deliverable.md and PDF-cleanliness gates."
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
      help="Optional specific deliverable file or directory path(s) to validate (repeatable)",
  )
  parser.add_argument(
      "--verify-urls",
      action="store_true",
      help="Perform live HTTP reachability checks on Section 6.1 Google Cloud documentation URLs.",
  )
  args = parser.parse_args()

  workspace_root = vqa.resolve_workspace_root(args.workspace)
  customer_name = vqa.extract_customer_name(
      workspace_root / "specs" / "specs_project.md"
  )
  targets = collect_target_deliverables(workspace_root, args.file)

  if not targets:
    print("No customer deliverable Markdown files found in project/deliverables/docs/.")
    return 0

  cli_schemas = vqa.CliSchemas()
  passed = 0
  failed = 0
  for md_path in targets:
    rel = (
        os.path.relpath(md_path, workspace_root)
        if str(md_path).startswith(str(workspace_root))
        else str(md_path)
    )
    errs, warns = validate_deliverable_file(
        md_path,
        customer_name=customer_name,
        cli_schemas=cli_schemas,
        verify_urls=args.verify_urls,
    )
    if errs:
      failed += 1
      print(f"[FAIL] {rel}")
      for e in errs:
        print(f"  - {e}")
      for w in warns:
        print(f"  - [WARN] {w}")
    else:
      passed += 1
      print(f"[PASS] {rel}")
      for w in warns:
        print(f"  - [WARN] {w}")

  suffix = f" (Customer: {customer_name})" if customer_name else ""
  print(
      f"\n[Deliverable Validation Summary] {passed}/{len(targets)} passed, {failed}/{len(targets)} failed{suffix}"
  )
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())

