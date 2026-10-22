#!/usr/bin/env python3
"""Validate question evaluation Markdown files in project/questions/ against the canonical template.

Workspace-agnostic structural validator for the `gcp-project-copilot` skill:
1. Resolves `<workspace-root>` via `--workspace` / `-w` or upward search for `specs/specs_project.md`.
2. Dynamically extracts `CUSTOMER_NAME` from `<workspace-root>/specs/specs_project.md` (zero hardcoded IDs).
3. Verifies that every target `<DOMAIN_ID>-Q<NN>_<slug>.md` file strictly matches
   `resources/templates/template_answers_to_questions.md`:
   - Dual H1 header (`# **Technical Question Evaluation & Architectural Answer**` + customer/code H1)
   - Exact 7-row top Metadata Table (and zero skills/status rows in the top table)
   - Exact 6 canonical `##` sections (`1`..`6`) in order
   - Contiguous numbered `### 2.1`, `### 2.2`, ... subsections in Section 2 (zero orphan unnumbered `###` headings),
     `### 3.1`, `### 3.2`, `> [!IMPORTANT]`, `> [!TIP]`, deliverables links,
     official Google Cloud doc URLs, and `| Workspace Skill | Technical Contribution to This Evaluation |`
   - Repository hygiene: portable relative paths only (no `file://` or `/usr/...`) and Mermaid syntax
     safety (no `<br>` HTML tags or `;` semicolons inside `mermaid` fenced blocks).
"""

import argparse
import os
from pathlib import Path
import re
import sys
from typing import List, Optional, Tuple


EXPECTED_META_KEYS = [
    "**Customer / Project**",
    "**Question ID**",
    "**Question**",
    "**Canonical Domain**",
    "**Asked By**",
    "**Source Session & Log**",
    "**Date Answered**",
]


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
  m = re.search(
      r"\|\s*\*\*`CUSTOMER_NAME`\*\*\s*\|\s*(.+?)\s*\|",
      text,
  )
  if not m:
    return None
  raw = m.group(1).strip()
  clean = re.sub(r"[*`]", "", raw).strip()
  if not clean or "{{" in clean:
    return None
  return clean


def strip_fenced_code(md_text: str) -> str:
  """Remove fenced code blocks so headings/links inside code samples do not confuse structural parsing."""
  return re.sub(r"```.*?```", "", md_text, flags=re.DOTALL)


def split_h2_sections(non_code_text: str) -> List[Tuple[str, str]]:
  """Return list of (h2_line, section_body) outside fenced code blocks."""
  lines = non_code_text.splitlines()
  sections: List[Tuple[str, str]] = []
  current_h2: Optional[str] = None
  buf: List[str] = []
  for line in lines:
    if line.startswith("## "):
      if current_h2 is not None:
        sections.append((current_h2, "\n".join(buf)))
      current_h2 = line.strip()
      buf = []
    elif current_h2 is not None:
      buf.append(line)
  if current_h2 is not None:
    sections.append((current_h2, "\n".join(buf)))
  return sections


def validate_file(md_path: Path, customer_name: Optional[str]) -> List[str]:
  """Validate a single question evaluation Markdown file and return a list of errors."""
  errors: List[str] = []
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
    return errors

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

  # Check for non-table lines in header (besides the 2 H1s and table rows)
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
        errors.append(
            f"'**Question ID**' cell must contain '[{expected_code}]'"
        )
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

  # 2. Validate 6 Canonical H2 Sections (outside fenced code blocks)
  non_code = strip_fenced_code(text)
  sections = split_h2_sections(non_code)
  actual_h2s = [h for h, _ in sections]

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
    errors.append(f"Expected 6 canonical H2 sections, found {len(actual_h2s)}: {actual_h2s}")
  else:
    for idx, (act, exp) in enumerate(zip(actual_h2s, expected_h2s), start=1):
      if idx == 4 and sec4_expected is None:
        if not act.startswith(exp):
          errors.append(f"Section 4 H2 mismatch: got '{act}'")
      elif act != exp:
        errors.append(f"Section {idx} H2 mismatch: expected '{exp}', got '{act}'")

  # Detailed per-section invariants when all 6 sections are present
  if len(sections) == 6:
    s1_body = sections[0][1]
    s2_body = sections[1][1]
    s3_body = sections[2][1]
    s4_body = sections[3][1]
    s5_body = sections[4][1]
    s6_body = sections[5][1]

    if not re.search(r"^\|.+\|\s*$", s1_body, flags=re.MULTILINE):
      errors.append("Section 1 must include a Markdown Solution Matrix table")

    s2_h3s = [
        l.strip() for l in s2_body.splitlines() if l.strip().startswith("### ")
    ]
    if len(s2_h3s) < 2:
      errors.append(
          f"Section 2 must include at least 2 numbered '### 2.x <Title>' subsections, found {len(s2_h3s)}"
      )
    else:
      for sub_idx, h3_line in enumerate(s2_h3s, start=1):
        expected_prefix = f"### 2.{sub_idx} "
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
          # Strip parenthetical status qualifiers like '(Edge-Case Pattern)' before checking tautology
          rest_main = re.sub(r"\([^)]*\)", "", rest)
          if re.search(rf"\b{re.escape(noun)}s?\b", rest_main, flags=re.IGNORECASE):
            errors.append(
                f"Tautological repetition of '{noun}' in Section 2 heading: '{h3_line}'"
            )

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

    if not re.search(
        r"\|\s*Workspace Skill\s*\|\s*Technical Contribution to This Evaluation\s*\|",
        s6_body,
    ):
      errors.append(
          "Section 6 must include table header '| Workspace Skill | Technical Contribution to This Evaluation |'"
      )

  # 3. Repository Path Portability & Mermaid Syntax Hygiene
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

  return errors


def collect_target_files(workspace_root: Path, cli_files: Optional[List[str]]) -> List[Path]:
  """Resolve list of question Markdown files to validate."""
  if not cli_files:
    q_dir = workspace_root / "project" / "questions"
    if not q_dir.is_dir():
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
          "Validate project/questions/*.md files against "
          "resources/templates/template_answers_to_questions.md."
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
  args = parser.parse_args()

  workspace_root = resolve_workspace_root(args.workspace)
  customer_name = extract_customer_name(workspace_root / "specs" / "specs_project.md")
  targets = collect_target_files(workspace_root, args.file)

  if not targets:
    print("No question Markdown files found to validate.")
    return 0

  passed = 0
  failed = 0
  for md_path in targets:
    rel = (
        os.path.relpath(md_path, workspace_root)
        if str(md_path).startswith(str(workspace_root))
        else str(md_path)
    )
    errs = validate_file(md_path, customer_name)
    if errs:
      failed += 1
      print(f"[FAIL] {rel}")
      for e in errs:
        print(f"  - {e}")
    else:
      passed += 1

  print(
      f"\n[Validation Summary] {passed}/{len(targets)} passed, {failed}/{len(targets)} failed"
      + (f" (Customer: {customer_name})" if customer_name else "")
  )
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())

