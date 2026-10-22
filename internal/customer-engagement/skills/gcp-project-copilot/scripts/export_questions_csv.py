#!/usr/bin/env python3
"""Export all coded questions from project/common/project_questions-log.md to a Google Sheets-ready CSV.

Workspace-agnostic script for the `gcp-project-copilot` skill:
1. Resolves the target customer workspace via `--workspace` / `-w` or by searching
   upward from the current working directory for `specs/specs_project.md`.
2. Parses `project/common/project_questions-log.md` across all canonical domains
   (`D1..Dn` and `P1..Pn`).
3. Writes an RFC 4180 UTF-8 CSV to `project/questions/question-list.csv` with the
   columns: `Updated,Code,Section,Asked By,Session Date,Question`.
"""

import argparse
import csv
import datetime
import os
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional


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


def parse_questions(md_path: Path, updated_date: str) -> List[Dict[str, str]]:
  """Parse all coded questions from project_questions-log.md."""
  if not md_path.is_file():
    raise RuntimeError(f"Questions log file not found: {md_path}")

  lines = md_path.read_text(encoding="utf-8").splitlines()
  current_section: Optional[str] = None
  questions: List[Dict[str, str]] = []
  current_q: Optional[Dict[str, str]] = None

  section_re = re.compile(r"^#+\s+\*\*((?:D\d+|P\d+)\.\s+.+?)\*\*\s*$")
  question_re = re.compile(r"^\*\s+\*\*`\[([A-Z]\d+-Q\d+)\]`\s+(.+?)\*\*\s*$")
  asked_by_re = re.compile(r"^\s+\*\s+\*\*Asked By:\*\*\s+(.+?)\s*$")
  session_re = re.compile(
      r"^\s+\*\s+\*\*Session:\*\*\s+(?:\[)?(\d{4}-\d{2}-\d{2})\b"
  )

  for line in lines:
    sec_m = section_re.match(line)
    if sec_m:
      current_section = sec_m.group(1).strip()
      continue

    q_m = question_re.match(line)
    if q_m:
      if current_q:
        questions.append(current_q)
      code = q_m.group(1).strip()
      raw_q = q_m.group(2).strip()
      clean_q = raw_q.replace("`", "")
      current_q = {
          "Updated": updated_date,
          "Code": code,
          "Section": current_section or "",
          "Asked By": "",
          "Session Date": "",
          "Question": clean_q,
      }
      continue

    if current_q:
      ab_m = asked_by_re.match(line)
      if ab_m:
        current_q["Asked By"] = ab_m.group(1).replace("*", "").strip()
        continue

      sess_m = session_re.match(line)
      if sess_m:
        current_q["Session Date"] = sess_m.group(1).strip()
        continue

  if current_q:
    questions.append(current_q)

  return questions


def main() -> int:
  parser = argparse.ArgumentParser(
      description=(
          "Export coded questions from project/common/project_questions-log.md "
          "to project/questions/question-list.csv for Google Sheets import."
      )
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
      "--input",
      "-i",
      default=None,
      help=(
          "Optional path to source project_questions-log.md "
          "(defaults to <workspace>/project/common/project_questions-log.md)"
      ),
  )
  parser.add_argument(
      "--output",
      "-o",
      default=None,
      help=(
          "Optional path to output CSV file "
          "(defaults to <workspace>/project/questions/question-list.csv)"
      ),
  )
  parser.add_argument(
      "--updated-date",
      default=datetime.date.today().isoformat(),
      help="ISO date string (YYYY-MM-DD) for the 'Updated' column (defaults to today)",
  )
  args = parser.parse_args()

  workspace_root = resolve_workspace_root(args.workspace)
  source_md = (
      Path(args.input).expanduser().resolve()
      if args.input
      else workspace_root / "project" / "common" / "project_questions-log.md"
  )
  output_csv = (
      Path(args.output).expanduser().resolve()
      if args.output
      else workspace_root / "project" / "questions" / "question-list.csv"
  )

  questions = parse_questions(source_md, args.updated_date)
  output_csv.parent.mkdir(parents=True, exist_ok=True)

  fieldnames = [
      "Updated",
      "Code",
      "Section",
      "Asked By",
      "Session Date",
      "Question",
  ]
  with output_csv.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(questions)

  missing = [
      q.get("Code", "<unknown>")
      for q in questions
      if not all(q.get(k) for k in fieldnames)
  ]
  if missing:
    raise RuntimeError(
        f"Exported {len(questions)} questions, but found incomplete fields in: {missing}"
    )

  rel_out = (
      os.path.relpath(output_csv, workspace_root)
      if str(output_csv).startswith(str(workspace_root))
      else str(output_csv)
  )
  print(f"[CSV Exported] {len(questions)} questions -> {rel_out}")
  return 0


if __name__ == "__main__":
  sys.exit(main())

