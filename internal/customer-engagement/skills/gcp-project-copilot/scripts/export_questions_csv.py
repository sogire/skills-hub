#!/usr/bin/env python3
"""Export coded questions from project/common/project_questions-log.md to a Google Sheets-ready CSV.

Workspace-agnostic script for the `gcp-project-copilot` skill:
1. Resolves the target customer workspace via `--workspace` / `-w` or by searching
   upward from the current working directory for `specs/specs_project.md`.
2. Parses `project/common/project_questions-log.md` across all canonical domains
   (`D1..Dn` and `P1..Pn`).
3. By default, exports only Customer Technical Questions (`[D#-Q##]` / `[P1-Q##]`)
   so `project/questions-answered/question-list.csv` aligns with Customer evaluations
   in `project/questions-answered/`. Pass `--include-discovery` to also include
   Discovery & Scoping Questions (`[D#-S##]` / `[P1-S##]`).
4. Writes an RFC 4180 UTF-8 CSV to `project/questions-answered/question-list.csv` with the
   columns: `Updated,Code,Section,Asked By,Session Date,Question,Answer`.
5. Populates the `Answer` column using a zero-token deterministic 3-tier resolution pipeline:
   - Tier 1: Explicit `* **Summary Answer:**` sub-bullet in `project/common/project_questions-log.md`.
   - Tier 2: Deterministic AST/regex extraction from `<workspace>/project/questions-answered/<CODE>_*.md`
     (combining the Section 4 `[!TIP]` executive recommendation or Section 1 Direct Answer with
     structured bullets from the Section 1 Solution Matrix table).
   - Tier 3: Incremental fallback cache from existing `question-list.csv` (or empty string `""`
     for questions without a dedicated file in `project/questions-answered/`).
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


def clean_markdown_inline(text: str) -> str:
  """Strip Markdown links, LaTeX arrows, HTML line breaks, and emphasis markers for CSV cells."""
  s = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
  s = re.sub(r"\[([A-Z]\d+-(?:Q|S)\d+)\]", r"\1", s)
  s = s.replace(r"$\rightarrow$", "->").replace(r"\rightarrow", "->")
  s = s.replace(r"$\times$", "x").replace(r"\times", "x")
  s = s.replace("<br>", " / ").replace("<br/>", " / ").replace("<br />", " / ")
  s = s.replace("**", "").replace("`", "").replace("*", "")
  # Remove internal section references like (§2.1, §2.2)
  s = re.sub(r"\s*\(§\d+(?:\.\d+)?(?:,\s*§\d+(?:\.\d+)?)*\)", "", s)
  s = re.sub(r"\s+", " ", s).strip()
  return s


def extract_answer_summary_from_md(md_path: Path) -> str:
  """Deterministically extract a concise executive summary and bullet list from a question-answered .md file."""
  if not md_path.is_file():
    return ""

  txt = md_path.read_text(encoding="utf-8")
  lines = txt.splitlines()

  # 1. Extract [!TIP] executive synthesis from Section 4 (or fallback [!TIP] in file)
  in_sec4 = False
  collecting_tip = False
  tip_lines: List[str] = []
  fallback_tip_lines: List[str] = []
  collecting_fallback = False

  for line in lines:
    s = line.strip()
    if re.match(r"^##\s+4\.", s):
      in_sec4 = True
    elif re.match(r"^##\s+[567]\.", s):
      in_sec4 = False

    if re.match(r"^>\s*\[!TIP\]", s):
      if in_sec4:
        collecting_tip = True
        tip_lines = []
      elif not fallback_tip_lines:
        collecting_fallback = True
      continue

    if collecting_tip:
      if s.startswith(">"):
        tip_lines.append(s.lstrip(">").strip())
      else:
        collecting_tip = False

    if collecting_fallback:
      if s.startswith(">"):
        fallback_tip_lines.append(s.lstrip(">").strip())
      else:
        collecting_fallback = False

  chosen_tip = " ".join(tip_lines or fallback_tip_lines)
  tip_text = clean_markdown_inline(chosen_tip)
  tip_text = re.sub(
      r"^Recommended Target Architecture[^:]*:\s*", "", tip_text, flags=re.I
  ).strip()

  # 2. Extract opening Direct Answer paragraph and Solution Matrix rows from Section 1
  m1 = re.search(
      r"^##\s+1\.\s+Executive Summary.*?\n+(.*?)(?=\n##\s+2\.|\Z)",
      txt,
      re.M | re.S,
  )
  bullets: List[str] = []
  sec1_first_para = ""
  if m1:
    sec1 = m1.group(1).strip()
    paras = [
        p.strip()
        for p in re.split(r"\n\s*\n", sec1)
        if p.strip()
        and not p.strip().startswith("|")
        and not p.strip().startswith("#")
        and not p.strip().startswith(">")
    ]
    if paras:
      sec1_first_para = clean_markdown_inline(paras[0])
      sec1_first_para = re.sub(
          r"^Direct Answer:\s*", "", sec1_first_para, flags=re.I
      ).strip()

    sec1_lines = [l.strip() for l in sec1.splitlines()]
    in_table_body = False
    for line in sec1_lines:
      if not line.startswith("|"):
        if in_table_body and bullets:
          break
        in_table_body = False
        continue
      if re.match(r"^\|\s*[:\-]+", line):
        in_table_body = True
        continue
      if in_table_body:
        cols = [clean_markdown_inline(c) for c in line.strip("|").split("|")]
        if len(cols) >= 2 and cols[0] and cols[1]:
          c0 = re.sub(r"^\d+\.\s*", "", cols[0]).strip()
          val = cols[1]
          if len(cols) >= 3 and len(cols[1]) < 45 and cols[2]:
            val = f"{cols[1]} — {cols[2]}"
          bullets.append(f"  • {c0}: {val}")

  lead = tip_text or sec1_first_para
  if bullets:
    return lead + "\n" + "\n".join(bullets[:6])
  if sec1_first_para and tip_text and sec1_first_para != tip_text:
    return sec1_first_para + "\n  • Recommended Architecture: " + tip_text
  return lead


def load_existing_csv_answers(csv_path: Path) -> Dict[str, str]:
  """Load existing Code -> Answer mappings from question-list.csv if present."""
  if not csv_path.is_file():
    return {}
  cached: Dict[str, str] = {}
  try:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
      reader = csv.DictReader(f)
      if not reader.fieldnames or "Code" not in reader.fieldnames or "Answer" not in reader.fieldnames:
        return {}
      for row in reader:
        code = (row.get("Code") or "").strip()
        ans = (row.get("Answer") or "").strip()
        if code and ans:
          cached[code] = ans
  except Exception:
    return {}
  return cached


def index_questions_answered_dir(qa_dir: Path) -> Dict[str, Path]:
  """Map question code (e.g., D1-Q01) to its file in project/questions-answered/."""
  mapping: Dict[str, Path] = {}
  if not qa_dir.is_dir():
    return mapping
  for p in sorted(qa_dir.glob("*.md")):
    m = re.match(r"^([A-Z]\d+-(?:Q|S)\d+)_", p.name)
    if m:
      mapping[m.group(1)] = p
  return mapping


def parse_questions(
    md_path: Path,
    updated_date: str,
    qa_dir: Optional[Path] = None,
    cached_answers: Optional[Dict[str, str]] = None,
    include_discovery: bool = False,
    unanswered_placeholder: str = "",
) -> List[Dict[str, str]]:
  """Parse coded questions from project_questions-log.md and resolve executive Answer summaries."""
  if not md_path.is_file():
    raise RuntimeError(f"Questions log file not found: {md_path}")

  qa_map = index_questions_answered_dir(qa_dir) if qa_dir else {}
  cached_answers = cached_answers or {}

  lines = md_path.read_text(encoding="utf-8").splitlines()
  current_section: Optional[str] = None
  questions: List[Dict[str, str]] = []
  current_q: Optional[Dict[str, str]] = None
  collecting_summary_bullets = False

  section_re = re.compile(r"^#+\s+\*\*((?:D\d+|P\d+)\.\s+.+?)\*\*\s*$")
  question_re = re.compile(
      r"^\*\s+\*\*`\[([A-Z]\d+-(Q|S)\d+)\]`\s+(.+?)\*\*\s*$"
  )
  asked_by_re = re.compile(r"^\s+\*\s+\*\*Asked By:\*\*\s+(.+?)\s*$")
  session_re = re.compile(
      r"^\s+\*\s+\*\*Session:\*\*\s+(?:\[)?(\d{4}-\d{2}-\d{2})\b"
  )
  answer_link_re = re.compile(
      r"^\s+\*\s+\*\*Answer:\*\*\s+.*?\]\(([^\)]+\.md)\)"
  )
  summary_answer_re = re.compile(
      r"^\s+\*\s+\*\*Summary Answer:\*\*\s*(.*?)\s*$"
  )
  summary_subbullet_re = re.compile(r"^\s{4,}\*\s+(.+?)\s*$")

  def finalize_question(q: Dict[str, str]) -> None:
    code = q["Code"]
    explicit_summary = q.pop("_explicit_summary", "").strip()
    answer_rel_path = q.pop("_answer_rel_path", "").strip()

    # Tier 1: Explicit '* **Summary Answer:**' in project_questions-log.md
    if explicit_summary:
      q["Answer"] = explicit_summary
      return

    # Tier 2: Deterministic extraction from project/questions-answered/<CODE>_*.md
    ans_file: Optional[Path] = None
    if answer_rel_path:
      candidate = (md_path.parent / answer_rel_path).resolve()
      if candidate.is_file():
        ans_file = candidate
    if not ans_file and code in qa_map:
      ans_file = qa_map[code]

    if ans_file:
      extracted = extract_answer_summary_from_md(ans_file)
      if extracted:
        q["Answer"] = extracted
        return

    # Tier 3: Incremental CSV cache fallback or unanswered placeholder
    if code in cached_answers:
      q["Answer"] = cached_answers[code]
    else:
      q["Answer"] = unanswered_placeholder

  for line in lines:
    sec_m = section_re.match(line)
    if sec_m:
      if current_q:
        finalize_question(current_q)
        questions.append(current_q)
        current_q = None
      collecting_summary_bullets = False
      current_section = sec_m.group(1).strip()
      continue

    q_m = question_re.match(line)
    if q_m:
      if current_q:
        finalize_question(current_q)
        questions.append(current_q)
        current_q = None
      collecting_summary_bullets = False
      code = q_m.group(1).strip()
      qtype = q_m.group(2).strip()
      if qtype == "S" and not include_discovery:
        continue
      raw_q = q_m.group(3).strip()
      clean_q = raw_q.replace("`", "")
      current_q = {
          "Updated": updated_date,
          "Code": code,
          "Section": current_section or "",
          "Asked By": "",
          "Session Date": "",
          "Question": clean_q,
          "Answer": "",
          "_explicit_summary": "",
          "_answer_rel_path": "",
      }
      continue

    if current_q:
      ab_m = asked_by_re.match(line)
      if ab_m:
        collecting_summary_bullets = False
        current_q["Asked By"] = ab_m.group(1).replace("*", "").strip()
        continue

      sess_m = session_re.match(line)
      if sess_m:
        collecting_summary_bullets = False
        current_q["Session Date"] = sess_m.group(1).strip()
        continue

      ans_m = answer_link_re.match(line)
      if ans_m:
        collecting_summary_bullets = False
        current_q["_answer_rel_path"] = ans_m.group(1).strip()
        continue

      sum_m = summary_answer_re.match(line)
      if sum_m:
        collecting_summary_bullets = True
        lead_sum = clean_markdown_inline(sum_m.group(1))
        current_q["_explicit_summary"] = lead_sum
        continue

      if collecting_summary_bullets:
        sub_m = summary_subbullet_re.match(line)
        if sub_m:
          bullet_txt = clean_markdown_inline(sub_m.group(1))
          if not bullet_txt.startswith("•"):
            bullet_txt = f"• {bullet_txt}"
          if current_q["_explicit_summary"]:
            current_q["_explicit_summary"] += f"\n  {bullet_txt}"
          else:
            current_q["_explicit_summary"] = f"  {bullet_txt}"
          continue
        elif line.strip():
          collecting_summary_bullets = False

  if current_q:
    finalize_question(current_q)
    questions.append(current_q)

  return questions


def main() -> int:
  parser = argparse.ArgumentParser(
      description=(
          "Export coded questions from project/common/project_questions-log.md "
          "to project/questions-answered/question-list.csv for Google Sheets import."
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
          "(defaults to <workspace>/project/questions-answered/question-list.csv)"
      ),
  )
  parser.add_argument(
      "--updated-date",
      default=datetime.date.today().isoformat(),
      help="ISO date string (YYYY-MM-DD) for the 'Updated' column (defaults to today)",
  )
  parser.add_argument(
      "--include-discovery",
      action="store_true",
      help="Also include Discovery & Scoping questions ([D#-S##] / [P1-S##]) in addition to Customer Technical Questions ([D#-Q##] / [P1-Q##])",
  )
  parser.add_argument(
      "--unanswered-placeholder",
      default="",
      help="Fallback text for the 'Answer' column when a question has no evaluation file yet (defaults to empty string '')",
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
      else workspace_root / "project" / "questions-answered" / "question-list.csv"
  )
  qa_dir = workspace_root / "project" / "questions-answered"
  cached_answers = load_existing_csv_answers(output_csv)

  questions = parse_questions(
      source_md,
      args.updated_date,
      qa_dir=qa_dir,
      cached_answers=cached_answers,
      include_discovery=args.include_discovery,
      unanswered_placeholder=args.unanswered_placeholder,
  )
  output_csv.parent.mkdir(parents=True, exist_ok=True)

  fieldnames = [
      "Updated",
      "Code",
      "Section",
      "Asked By",
      "Session Date",
      "Question",
      "Answer",
  ]
  required_fields = [
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
      if not all(q.get(k) for k in required_fields)
  ]
  if missing:
    raise RuntimeError(
        f"Exported {len(questions)} questions, but found incomplete required fields in: {missing}"
    )

  answered_count = sum(1 for q in questions if q.get("Answer", "").strip())
  rel_out = (
      os.path.relpath(output_csv, workspace_root)
      if str(output_csv).startswith(str(workspace_root))
      else str(output_csv)
  )
  scope_label = "all (Q + S)" if args.include_discovery else "Customer (Q)"
  print(
      f"[CSV Exported] {len(questions)} {scope_label} questions "
      f"({answered_count} with Answer summary, {len(questions) - answered_count} pending) -> {rel_out}"
  )
  return 0


if __name__ == "__main__":
  sys.exit(main())
