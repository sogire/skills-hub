#!/usr/bin/env python3
"""Validate a generated GCP Console demo bundle for customer-sync safety and hygiene.

Zero external dependencies (Python 3 standard library only).
Checks:
1. Customer-facing Markdown deliverables exist under `<demo-dir>/docs/`.
2. Zero plaintext leaks of real Sandbox Project IDs/numbers/names or
   `@gcp.altostrat.com` / `@altostrat.com` / `@google.com` emails across
   `docs/*.md` and `diagrams/**/*.{svg,json}`.
3. Portable relative links only (zero `file:///` or absolute `/usr/...`, `/home/...` paths).
4. Mermaid syntax safety (zero `;` or `<br>` inside ```mermaid blocks).
5. Every local image (`![...](...)`) resolves to an existing non-empty file and
   valid PNG `IHDR` dimensions.
6. When `.runtime/` is present, `.runtime/teardown.sh` exists, is executable,
   and passes `bash -n` syntax checking.
"""

import argparse
import json
import os
import re
import struct
import subprocess
import sys
from typing import Dict, List, Optional, Set, Tuple

INTERNAL_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+-]+@(?:[a-zA-Z0-9.-]+\.)?(?:altostrat\.com|google\.com)\b",
    flags=re.IGNORECASE,
)
ABS_PATH_LINK_RE = re.compile(
    r"!?\[[^\]]*\]\((?:\s*)(file:///|/usr/|/home/|/var/|/tmp/)[^)]+\)"
)
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HTML_BR_RE = re.compile(r"<\s*br\s*/?\s*>", flags=re.IGNORECASE)


def parse_png_dimensions(path: str) -> Optional[Tuple[int, int]]:
  """Read PNG magic header and IHDR width/height using pure stdlib."""
  try:
    with open(path, "rb") as f:
      head = f.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
      return None
    width, height = struct.unpack(">II", head[16:24])
    return int(width), int(height)
  except OSError:
    return None


def collect_forbidden_tokens(demo_dir: str) -> Dict[str, str]:
  """Build {token: reason} deny-list from .runtime/demo_env.json if present."""
  forbidden: Dict[str, str] = {}
  env_path = os.path.join(demo_dir, ".runtime", "demo_env.json")
  if not os.path.isfile(env_path):
    return forbidden

  try:
    with open(env_path, "r", encoding="utf-8") as f:
      env = json.load(f)
  except (OSError, json.JSONDecodeError) as exc:
    raise RuntimeError(f"Invalid JSON in {env_path}: {exc}") from exc

  default_alias = str(env.get("default_project_alias") or "")
  alias_num = str(env.get("alias_project_number") or "")
  alias_name = str(env.get("alias_project_name") or "")

  proj_id = str(env.get("sandbox_project_id") or "").strip()
  if proj_id and proj_id != default_alias:
    forbidden[proj_id] = "real sandbox_project_id from .runtime/demo_env.json"

  proj_num = str(env.get("sandbox_project_number") or "").strip()
  if proj_num and proj_num != alias_num:
    forbidden[proj_num] = "real sandbox_project_number from .runtime/demo_env.json"

  proj_name = str(env.get("sandbox_project_name") or "").strip()
  if proj_name and proj_name not in (default_alias, alias_name):
    forbidden[proj_name] = "real sandbox_project_name from .runtime/demo_env.json"

  personas = env.get("personas") or {}
  if isinstance(personas, dict):
    for role, pinfo in personas.items():
      if isinstance(pinfo, dict):
        em = str(pinfo.get("argolis_email") or "").strip()
        disp = str(pinfo.get("display_alias") or "").strip()
        if em and em != disp:
          forbidden[em] = f"real persona email ({role}) from .runtime/demo_env.json"

  return forbidden


def check_mermaid_blocks(rel_file: str, text: str, errors: List[str]) -> None:
  in_mermaid = False
  fence_start = 0
  for lineno, line in enumerate(text.splitlines(), start=1):
    stripped = line.strip()
    if stripped.startswith("```"):
      if not in_mermaid:
        lang = stripped[3:].strip().lower()
        if lang == "mermaid":
          in_mermaid = True
          fence_start = lineno
      else:
        in_mermaid = False
      continue

    if in_mermaid:
      if ";" in line:
        errors.append(
            f"[{rel_file}:{lineno}] Semicolon ';' inside Mermaid block (started line {fence_start})"
        )
      if HTML_BR_RE.search(line):
        errors.append(
            f"[{rel_file}:{lineno}] HTML <br> tag inside Mermaid block (started line {fence_start})"
        )


def validate_demo_dir(demo_dir: str, require_runtime: bool = False) -> Tuple[List[str], List[str]]:
  errors: List[str] = []
  info_notes: List[str] = []

  docs_dir = os.path.join(demo_dir, "docs")
  if not os.path.isdir(docs_dir):
    errors.append(f"Missing customer deliverable directory: {docs_dir}")
    return errors, info_notes

  md_files = sorted(
      os.path.join(docs_dir, fn)
      for fn in os.listdir(docs_dir)
      if fn.endswith(".md") and not fn.startswith(".") and "-gdoc-tmp" not in fn
  )
  if not md_files:
    errors.append(f"No Markdown deliverables (*.md) found inside {docs_dir}")

  forbidden = collect_forbidden_tokens(demo_dir)

  # Scan customer-visible text assets (docs/*.md and diagrams/**/*.{svg,json})
  scan_files: List[str] = list(md_files)
  diagrams_dir = os.path.join(demo_dir, "diagrams")
  if os.path.isdir(diagrams_dir):
    for root, dirs, files in os.walk(diagrams_dir):
      dirs[:] = [d for d in dirs if not d.startswith(".")]
      for fn in sorted(files):
        if fn.lower().endswith((".svg", ".json")):
          scan_files.append(os.path.join(root, fn))

  checked_images: Set[str] = set()

  for abs_file in scan_files:
    rel_file = os.path.relpath(abs_file, demo_dir)
    try:
      with open(abs_file, "r", encoding="utf-8") as f:
        text = f.read()
    except OSError as exc:
      errors.append(f"[{rel_file}] Unable to read file: {exc}")
      continue

    # 1. Check forbidden Sandbox tokens & internal Google/Argolis emails
    for lineno, line in enumerate(text.splitlines(), start=1):
      for needle, reason in forbidden.items():
        if needle in line:
          errors.append(f"[{rel_file}:{lineno}] Leaked {reason}: '{needle}'")
      for m in INTERNAL_EMAIL_RE.finditer(line):
        errors.append(
            f"[{rel_file}:{lineno}] Leaked internal Google/Argolis email: '{m.group(0)}'"
        )

    if not abs_file.endswith(".md"):
      continue

    # 2. Portable relative path & target existence check
    base_dir = os.path.dirname(abs_file)
    for lineno, line in enumerate(text.splitlines(), start=1):
      if ABS_PATH_LINK_RE.search(line):
        errors.append(
            f"[{rel_file}:{lineno}] Non-portable absolute or file:/// link detected: {line.strip()}"
        )
      for lm in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", line):
        ltarget = lm.group(1).strip().split()[0].split("#")[0]
        if not ltarget or ltarget.startswith(("http://", "https://", "mailto:")):
          continue
        if "{{" in ltarget:
          continue
        resolved_link = os.path.normpath(os.path.join(base_dir, ltarget))
        if not os.path.exists(resolved_link):
          errors.append(
              f"[{rel_file}:{lineno}] Broken relative link target '{ltarget}' (resolved: {resolved_link})"
          )

    # 3. Mermaid hygiene check
    check_mermaid_blocks(rel_file, text, errors)

    # 4. Local image existence & PNG resolution check
    for m in MD_IMAGE_RE.finditer(text):
      raw_target = m.group(1).strip()
      if raw_target.startswith(("http://", "https://", "data:")):
        continue
      clean_target = raw_target.split("#")[0].split("?")[0]
      abs_img = os.path.normpath(os.path.join(base_dir, clean_target))
      rel_img = os.path.relpath(abs_img, demo_dir)
      if not os.path.isfile(abs_img):
        errors.append(
            f"[{rel_file}] Broken image reference '{raw_target}' -> missing file '{rel_img}'"
        )
        continue
      if os.path.getsize(abs_img) == 0:
        errors.append(f"[{rel_file}] Referenced image is empty (0 bytes): '{rel_img}'")
        continue

      if abs_img.lower().endswith(".png") and abs_img not in checked_images:
        checked_images.add(abs_img)
        dims = parse_png_dimensions(abs_img)
        if not dims:
          errors.append(f"[{rel_img}] File is not a valid PNG image")
        else:
          w, h = dims
          if w < 400 or h < 200:
            errors.append(
                f"[{rel_img}] PNG dimensions suspiciously small ({w}x{h}); expected Console screenshot"
            )
          else:
            info_notes.append(f"Verified PNG '{rel_img}' ({w}x{h} px)")

  # 5. Check .runtime/teardown.sh when .runtime/ exists or --require-runtime is set
  runtime_dir = os.path.join(demo_dir, ".runtime")
  if require_runtime and not os.path.isdir(runtime_dir):
    errors.append(f"Missing required .runtime/ directory at {runtime_dir}")

  if os.path.isdir(runtime_dir):
    teardown_sh = os.path.join(runtime_dir, "teardown.sh")
    if not os.path.isfile(teardown_sh):
      errors.append("Missing mandatory '.runtime/teardown.sh' cleanup script")
    else:
      if not os.access(teardown_sh, os.X_OK):
        errors.append("'.runtime/teardown.sh' is not marked executable (run chmod +x)")
      proc = subprocess.run(
          ["bash", "-n", teardown_sh],
          capture_output=True,
          text=True,
          check=False,
      )
      if proc.returncode != 0:
        errors.append(
            f"'.runtime/teardown.sh' failed `bash -n` syntax validation: {proc.stderr.strip()}"
        )
      else:
        info_notes.append("Verified '.runtime/teardown.sh' (executable, valid bash syntax)")

  return errors, info_notes


def main() -> int:
  parser = argparse.ArgumentParser(
      description="Validate a GCP Console demo bundle for leaked IDs, broken screenshots, and hygiene."
  )
  parser.add_argument(
      "--demo-dir",
      "-d",
      required=True,
      help="Path to project/topics/<topic-slug>/demos/<demo-slug>",
  )
  parser.add_argument(
      "--require-runtime",
      action="store_true",
      help="Fail if .runtime/ and .runtime/teardown.sh are not present",
  )
  args = parser.parse_args()

  demo_dir = os.path.abspath(args.demo_dir)
  if not os.path.isdir(demo_dir):
    print(f"Error: Demo directory not found: {demo_dir}", file=sys.stderr)
    return 1

  try:
    errors, notes = validate_demo_dir(demo_dir, require_runtime=args.require_runtime)
  except RuntimeError as exc:
    print(f"Error: {exc}", file=sys.stderr)
    return 1

  for note in notes:
    print(f"  [OK] {note}")

  if errors:
    print(f"\n[FAIL] {len(errors)} validation issue(s) in {demo_dir}:", file=sys.stderr)
    for err in errors:
      print(f"  - {err}", file=sys.stderr)
    return 1

  print(f"\n[PASS] Demo bundle validated cleanly: {demo_dir}")
  return 0


if __name__ == "__main__":
  sys.exit(main())

