#!/usr/bin/env python3
"""Manage persistent per-persona Chrome CDP browser profiles for GCP Console demos.

Zero external dependencies (Python 3 standard library only).
Caches profiles globally by sanitized email under:
  ~/.cache/gcp-console-demo-generator/profiles/<email-slug>/
so each Argolis / Sandbox persona account signs into Google SSO once and is
reused across all customer engagement workspaces.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_CACHE_ROOT = os.path.expanduser("~/.cache/gcp-console-demo-generator")
BASE_CDP_PORT = 9222
MAX_PORT_SCAN = 50
GDRIVE_BIN = "/google/bin/releases/gemini-agents-gdrive/gdrive"
GDOCS_BIN = "/google/bin/releases/gemini-agents-gdocs/gdocs"

AUTH_HOST_PREFIXES = (
    "https://accounts.google.com",
    "https://login.corp.google.com",
    "https://myaccount.google.com/signin",
)

EXTRACT_CONSOLE_EMAIL_EXPR = """(() => {
  const els = document.querySelectorAll('[aria-label*="Account:"], a[aria-label*="Google Account"], button[aria-label*="Google Account"]');
  for (const el of els) {
    const lbl = el.getAttribute('aria-label') || '';
    const m = lbl.match(/\\(([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)\\)/);
    if (m) return m[1].toLowerCase();
  }
  return '';
})()"""


def find_chrome_binary() -> str:
  """Locate an installed Google Chrome or Chromium binary."""
  env_bin = os.environ.get("CHROME_BIN")
  if env_bin and os.path.isfile(env_bin) and os.access(env_bin, os.X_OK):
    return env_bin
  candidates = [
      "/usr/bin/google-chrome-stable",
      "/usr/bin/google-chrome",
      "/opt/google/chrome/google-chrome",
      shutil.which("google-chrome-stable"),
      shutil.which("google-chrome"),
      shutil.which("chromium"),
      shutil.which("chromium-browser"),
  ]
  for cand in candidates:
    if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
      return cand
  raise RuntimeError(
      "Google Chrome binary not found. Install google-chrome-stable or set CHROME_BIN."
  )


def email_to_slug(email: str) -> str:
  """Convert an email address into a safe filesystem directory slug."""
  cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", email.strip().lower()).strip("_")
  short_hash = hashlib.sha1(email.strip().lower().encode("utf-8")).hexdigest()[:6]
  return f"{cleaned}-{short_hash}"


def load_registry(cache_root: str) -> Dict[str, Any]:
  reg_path = os.path.join(cache_root, "registry.json")
  if os.path.isfile(reg_path):
    try:
      with open(reg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
      if isinstance(data, dict):
        data.setdefault("profiles", {})
        return data
    except (OSError, json.JSONDecodeError):
      pass
  return {"profiles": {}}


def save_registry(cache_root: str, registry: Dict[str, Any]) -> None:
  os.makedirs(cache_root, exist_ok=True)
  reg_path = os.path.join(cache_root, "registry.json")
  tmp_path = f"{reg_path}.tmp.{os.getpid()}"
  with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)
    f.write("\n")
  os.replace(tmp_path, reg_path)


def is_tcp_port_open(port: int, host: str = "127.0.0.1") -> bool:
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.4)
    return sock.connect_ex((host, port)) == 0


def cdp_get_json(port: int, path: str, timeout: float = 1.5) -> Optional[Any]:
  url = f"http://127.0.0.1:{port}{path}"
  try:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
      if resp.status == 200:
        return json.loads(resp.read().decode("utf-8"))
  except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
    return None
  return None


def allocate_port_for_email(
    email: str, registry: Dict[str, Any], preferred_port: Optional[int] = None
) -> int:
  """Return existing assigned port for email or allocate a free deterministic port."""
  key = email.strip().lower()
  profiles = registry.setdefault("profiles", {})
  if key in profiles and isinstance(profiles[key].get("cdp_port"), int):
    existing_port = profiles[key]["cdp_port"]
    if preferred_port is None or preferred_port == existing_port:
      return existing_port

  used_ports = {
      info.get("cdp_port")
      for em, info in profiles.items()
      if em != key and isinstance(info.get("cdp_port"), int)
  }
  if preferred_port and preferred_port not in used_ports:
    return preferred_port

  for candidate in range(BASE_CDP_PORT, BASE_CDP_PORT + MAX_PORT_SCAN):
    if candidate in used_ports:
      continue
    if not is_tcp_port_open(candidate):
      return candidate
  raise RuntimeError(
      f"Unable to allocate an unused CDP port in range {BASE_CDP_PORT}..{BASE_CDP_PORT + MAX_PORT_SCAN}"
  )


def cdp_eval_js_on_ws(ws_url: str, expression: str, timeout: float = 2.5) -> Any:
  """Evaluate a lightweight JavaScript expression over a CDP WebSocket (pure stdlib)."""
  parsed = urllib.parse.urlparse(ws_url)
  host = parsed.hostname or "127.0.0.1"
  port = parsed.port or 80
  path = parsed.path or "/"
  if parsed.query:
    path = f"{path}?{parsed.query}"

  sock = socket.create_connection((host, port), timeout=timeout)
  try:
    sock.settimeout(timeout)
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    handshake = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(handshake.encode("ascii"))
    buf = bytearray()
    while b"\r\n\r\n" not in buf:
      chunk = sock.recv(4096)
      if not chunk:
        return None
      buf.extend(chunk)
    sep = buf.index(b"\r\n\r\n") + 4
    status_line = bytes(buf[:sep]).splitlines()[0].decode("latin1", errors="replace")
    del buf[:sep]
    if "101" not in status_line:
      return None

    def _read_exact(n: int) -> bytes:
      while len(buf) < n:
        chunk = sock.recv(max(4096, n - len(buf)))
        if not chunk:
          raise RuntimeError("closed")
        buf.extend(chunk)
      out = bytes(buf[:n])
      del buf[:n]
      return out

    def _send_text(text: str) -> None:
      payload = text.encode("utf-8")
      mask = os.urandom(4)
      hdr = bytearray([0x81])
      plen = len(payload)
      if plen < 126:
        hdr.append(0x80 | plen)
      elif plen < 65536:
        hdr.append(0x80 | 126)
        hdr.extend(struct.pack("!H", plen))
      else:
        hdr.append(0x80 | 127)
        hdr.extend(struct.pack("!Q", plen))
      hdr.extend(mask)
      sock.sendall(bytes(hdr) + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    req_msg = json.dumps({
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {"expression": expression, "returnByValue": True},
    })
    _send_text(req_msg)

    deadline = time.time() + timeout
    while time.time() < deadline:
      b1, b2 = _read_exact(2)
      fin = bool(b1 & 0x80)
      opcode = b1 & 0x0F
      masked = bool(b2 & 0x80)
      length = b2 & 0x7F
      if length == 126:
        (length,) = struct.unpack("!H", _read_exact(2))
      elif length == 127:
        (length,) = struct.unpack("!Q", _read_exact(8))
      mkey = _read_exact(4) if masked else b""
      data = _read_exact(length)
      if masked:
        data = bytes(b ^ mkey[i % 4] for i, b in enumerate(data))
      if opcode == 0x8:
        return None
      if opcode == 0x9 or not fin:
        continue
      obj = json.loads(data.decode("utf-8", errors="replace"))
      if obj.get("id") == 1:
        return ((obj.get("result") or {}).get("result") or {}).get("value")
  except Exception:
    return None
  finally:
    try:
      sock.close()
    except Exception:
      pass
  return None


def classify_cdp_auth_state(
    port: int, expected_email: str = ""
) -> Tuple[str, List[Dict[str, str]], str]:
  """Inspect open tabs on a running Chrome CDP port and verify signed-in account email."""
  version = cdp_get_json(port, "/json/version")
  if not version:
    return "STOPPED", [], ""

  targets = cdp_get_json(port, "/json/list") or []
  page_targets = [t for t in targets if t.get("type") == "page"]
  pages = [
      {"url": str(t.get("url", "")), "title": str(t.get("title", ""))}
      for t in page_targets
  ]

  for p in pages:
    url_lower = p["url"].lower()
    title_lower = p["title"].lower()
    if any(url_lower.startswith(pref) for pref in AUTH_HOST_PREFIXES) or (
        "sign in - google accounts" in title_lower
    ):
      return "AUTH_REQUIRED", pages, ""

  expected_norm = expected_email.strip().lower()
  for t in page_targets:
    url_lower = str(t.get("url", "")).lower()
    if url_lower.startswith("https://console.cloud.google.com"):
      actual_email = ""
      ws_url = t.get("webSocketDebuggerUrl")
      if isinstance(ws_url, str) and ws_url:
        val = cdp_eval_js_on_ws(ws_url, EXTRACT_CONSOLE_EMAIL_EXPR)
        if isinstance(val, str):
          actual_email = val.strip().lower()
      if expected_norm and actual_email and actual_email != expected_norm:
        return "WRONG_ACCOUNT", pages, actual_email
      return "AUTHENTICATED", pages, actual_email

  return "RUNNING_UNVERIFIED", pages, ""


def launch_chrome_profile(
    chrome_bin: str,
    profile_dir: str,
    port: int,
    start_url: str,
    headless: bool = False,
) -> int:
  """Launch detached Google Chrome instance with dedicated --user-data-dir and CDP port."""
  os.makedirs(profile_dir, exist_ok=True)
  for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
    lp = os.path.join(profile_dir, lock_name)
    if os.path.lexists(lp):
      try:
        os.unlink(lp)
      except OSError:
        pass

  cmd = [chrome_bin]
  if headless:
    cmd.extend(["--headless=new", "--disable-gpu", "--disable-dev-shm-usage"])
  cmd.extend([
      f"--user-data-dir={profile_dir}",
      f"--remote-debugging-port={port}",
      "--remote-debugging-address=127.0.0.1",
      "--no-first-run",
      "--no-default-browser-check",
      "--window-size=1600,1040",
      start_url,
  ])
  proc = subprocess.Popen(
      cmd,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
      stdin=subprocess.DEVNULL,
      start_new_session=True,
  )
  pid_file = os.path.join(profile_dir, "chrome_cdp.pid")
  with open(pid_file, "w", encoding="utf-8") as f:
    f.write(f"{proc.pid}\n")

  deadline = time.time() + 12.0
  while time.time() < deadline:
    if cdp_get_json(port, "/json/version") is not None:
      # Give initial navigation a brief moment to settle or redirect to accounts.google.com
      time.sleep(2.0)
      return proc.pid
    time.sleep(0.4)

  raise RuntimeError(
      f"Chrome launched (PID {proc.pid}) for {profile_dir} on port {port}, "
      "but CDP endpoint did not respond within 12s."
  )


def load_personas_from_env(env_path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
  with open(env_path, "r", encoding="utf-8") as f:
    env_data = json.load(f)
  project_id = env_data.get("sandbox_project_id", "")
  raw_personas = env_data.get("personas", {})
  normalized: List[Dict[str, Any]] = []
  if isinstance(raw_personas, dict):
    for role, info in raw_personas.items():
      if isinstance(info, dict) and info.get("argolis_email"):
        normalized.append({
            "persona": role,
            "email": info["argolis_email"],
            "display_alias": info.get("display_alias", ""),
            "cdp_port": info.get("cdp_port"),
            "project_id": project_id,
        })
  elif isinstance(raw_personas, list):
    for item in raw_personas:
      if isinstance(item, dict) and item.get("argolis_email"):
        normalized.append({
            "persona": item.get("persona") or item.get("role") or "default",
            "email": item["argolis_email"],
            "display_alias": item.get("display_alias", ""),
            "cdp_port": item.get("cdp_port"),
            "project_id": project_id,
        })
  return env_data, normalized


def update_env_ports(env_path: str, env_data: Dict[str, Any], results: List[Dict[str, Any]]) -> None:
  port_by_persona = {r["persona"]: r["cdp_port"] for r in results}
  raw_personas = env_data.get("personas")
  mutated = False
  if isinstance(raw_personas, dict):
    for role, info in raw_personas.items():
      if role in port_by_persona and isinstance(info, dict):
        if info.get("cdp_port") != port_by_persona[role]:
          info["cdp_port"] = port_by_persona[role]
          mutated = True
  if mutated:
    tmp_path = f"{env_path}.tmp.{os.getpid()}"
    with open(tmp_path, "w", encoding="utf-8") as f:
      json.dump(env_data, f, indent=2, ensure_ascii=False)
      f.write("\n")
    os.replace(tmp_path, env_path)


def cmd_ensure_or_status(args: argparse.Namespace, launch_missing: bool) -> int:
  cache_root = os.path.abspath(os.path.expanduser(args.cache_dir))
  registry = load_registry(cache_root)
  env_data: Optional[Dict[str, Any]] = None
  targets: List[Dict[str, Any]] = []

  if args.env:
    env_data, targets = load_personas_from_env(args.env)
  elif args.email:
    targets.append({
        "persona": args.persona or "default",
        "email": args.email,
        "display_alias": "",
        "cdp_port": args.port,
        "project_id": args.project or "",
    })
  else:
    raise RuntimeError("Provide either --env <demo_env.json> or --email <argolis-email>.")

  chrome_bin = find_chrome_binary() if launch_missing else ""
  results: List[Dict[str, Any]] = []

  for item in targets:
    email = item["email"].strip()
    key = email.lower()
    slug = email_to_slug(email)
    profile_dir = os.path.join(cache_root, "profiles", slug)
    port = allocate_port_for_email(email, registry, preferred_port=item.get("cdp_port"))

    if launch_missing and getattr(args, "reset", False):
      pid_file = os.path.join(profile_dir, "chrome_cdp.pid")
      if os.path.isfile(pid_file):
        try:
          with open(pid_file, "r", encoding="utf-8") as f:
            os.kill(int(f.read().strip()), signal.SIGTERM)
          time.sleep(0.6)
        except Exception:
          pass
      if os.path.isdir(profile_dir):
        shutil.rmtree(profile_dir, ignore_errors=True)
      if key in registry.get("profiles", {}):
        registry["profiles"][key]["last_state"] = "STOPPED"

    state, pages, actual_email = classify_cdp_auth_state(port, expected_email=email)
    launched_now = False
    if state == "STOPPED" and launch_missing:
      proj_query = f"?project={item['project_id']}" if item.get("project_id") else ""
      console_url = args.url or f"https://console.cloud.google.com/home/dashboard{proj_query}"
      prev_state = (registry.get("profiles", {}).get(key) or {}).get("last_state")
      if prev_state == "AUTHENTICATED" and not getattr(args, "reset", False):
        start_url = console_url
      else:
        start_url = (
            "https://accounts.google.com/AddSession?Email="
            + urllib.parse.quote(email, safe="")
            + "&continue="
            + urllib.parse.quote(console_url, safe="")
        )
      launch_chrome_profile(
          chrome_bin,
          profile_dir,
          port,
          start_url,
          headless=bool(getattr(args, "headless", False)),
      )
      launched_now = True
      state, pages, actual_email = classify_cdp_auth_state(port, expected_email=email)

    registry["profiles"][key] = {
        "email": email,
        "slug": slug,
        "profile_dir": profile_dir,
        "cdp_port": port,
        "last_persona": item["persona"],
        "last_state": state,
        "actual_email": actual_email,
        "updated_at": int(time.time()),
    }
    results.append({
        "persona": item["persona"],
        "email": email,
        "actual_email": actual_email,
        "cdp_port": port,
        "profile_dir": profile_dir,
        "state": state,
        "launched": launched_now,
        "active_urls": [p["url"] for p in pages[:3]],
    })

  save_registry(cache_root, registry)
  if args.env and env_data is not None and launch_missing:
    update_env_ports(args.env, env_data, results)

  if args.json:
    print(json.dumps({"personas": results}, indent=2))
  else:
    for r in results:
      if r["state"] == "WRONG_ACCOUNT":
        badge = (
            f"[WRONG_ACCOUNT - Signed into '{r['actual_email']}'; "
            "re-run `ensure --reset`]"
        )
      else:
        badge = {
            "AUTHENTICATED": "[AUTHENTICATED]",
            "AUTH_REQUIRED": "[AUTH_REQUIRED - Sign in needed in opened Chrome window]",
            "RUNNING_UNVERIFIED": "[RUNNING - Open console.cloud.google.com tab to verify]",
            "STOPPED": "[STOPPED]",
        }.get(r["state"], f"[{r['state']}]")
      verified_suffix = (
          f" verified='{r['actual_email']}'" if r.get("actual_email") else ""
      )
      print(
          f"{badge} persona='{r['persona']}' email='{r['email']}'{verified_suffix} "
          f"cdp=http://127.0.0.1:{r['cdp_port']} profile='{r['profile_dir']}'",
          flush=True,
      )

  if launch_missing and getattr(args, "keep_alive", False):
    print(
        "[DAEMON] Keeping Chrome CDP profile session(s) alive. "
        "Monitoring SSO authentication state...",
        flush=True,
    )
    last_states = {
        r["email"].lower(): (r["state"], r.get("actual_email", "")) for r in results
    }
    try:
      while True:
        time.sleep(3.0)
        changed = False
        for r in results:
          ekey = r["email"].lower()
          cur_state, _, cur_actual = classify_cdp_auth_state(
              r["cdp_port"], expected_email=r["email"]
          )
          if (cur_state, cur_actual) != last_states.get(ekey):
            last_states[ekey] = (cur_state, cur_actual)
            if ekey in registry.get("profiles", {}):
              registry["profiles"][ekey]["last_state"] = cur_state
              registry["profiles"][ekey]["actual_email"] = cur_actual
              registry["profiles"][ekey]["updated_at"] = int(time.time())
              changed = True
            extra = f" actual='{cur_actual}'" if cur_actual else ""
            print(
                f"[{cur_state}] persona='{r['persona']}' email='{r['email']}'{extra} "
                f"cdp=http://127.0.0.1:{r['cdp_port']}",
                flush=True,
            )
        if changed:
          save_registry(cache_root, registry)
    except KeyboardInterrupt:
      return 0

  if any(r["state"] in ("AUTH_REQUIRED", "WRONG_ACCOUNT") for r in results):
    return 2
  if any(r["state"] == "STOPPED" for r in results) and launch_missing:
    return 1
  return 0


def check_corp_cli_binary(bin_path: str) -> Dict[str, Any]:
  """Check whether a Corp /google/bin CLI (gdrive / gdocs) is mounted and LOAS (gcert) ready."""
  try:
    with open(bin_path, "rb") as f:
      f.read(4)
  except FileNotFoundError:
    return {
        "binary": bin_path,
        "status": "SANDBOX_UNMOUNTED",
        "ok": False,
        "hint": "Path not mounted in sandbox; run outside sandbox to access /google/bin.",
    }
  except OSError as exc:
    if getattr(exc, "errno", None) == 126:
      return {
          "binary": bin_path,
          "status": "GCERT_REQUIRED",
          "ok": False,
          "hint": "LOAS certificate expired or missing (Errno 126). Run `gcert` on your workstation first.",
      }
    return {
        "binary": bin_path,
        "status": "OS_ERROR",
        "ok": False,
        "hint": str(exc),
    }

  try:
    proc = subprocess.run(
        [bin_path, "--help"],
        capture_output=True,
        text=True,
        timeout=5.0,
        check=False,
    )
    if proc.returncode == 0:
      return {"binary": bin_path, "status": "OK", "ok": True, "hint": ""}
    return {
        "binary": bin_path,
        "status": "CLI_ERROR",
        "ok": False,
        "hint": (proc.stderr or proc.stdout).strip()[:200],
    }
  except OSError as exc:
    if getattr(exc, "errno", None) == 126:
      return {
          "binary": bin_path,
          "status": "GCERT_REQUIRED",
          "ok": False,
          "hint": "LOAS certificate expired or missing (Errno 126). Run `gcert` on your workstation first.",
      }
    return {"binary": bin_path, "status": "OS_ERROR", "ok": False, "hint": str(exc)}
  except subprocess.TimeoutExpired:
    return {
        "binary": bin_path,
        "status": "TIMEOUT",
        "ok": False,
        "hint": "Timed out invoking --help (check LOAS / objfs mount).",
    }


def cmd_precheck(args: argparse.Namespace) -> int:
  """Fast upfront readiness check for Chrome binary, cached/live persona SSO, and optional gcert/Drive CLIs."""
  cache_root = os.path.abspath(os.path.expanduser(args.cache_dir))
  registry = load_registry(cache_root)

  chrome_info: Dict[str, Any]
  try:
    cbin = find_chrome_binary()
    chrome_info = {"ok": True, "binary": cbin}
  except RuntimeError as exc:
    chrome_info = {"ok": False, "binary": "", "error": str(exc)}

  targets: List[Dict[str, Any]] = []
  if args.env:
    _, targets = load_personas_from_env(args.env)
  elif args.email:
    targets.append({
        "persona": args.persona or "default",
        "email": args.email,
        "display_alias": "",
        "cdp_port": args.port,
        "project_id": "",
    })

  persona_checks: List[Dict[str, Any]] = []
  for item in targets:
    email = item["email"].strip()
    key = email.lower()
    slug = email_to_slug(email)
    reg_entry = (registry.get("profiles") or {}).get(key) or {}
    profile_dir = reg_entry.get("profile_dir") or os.path.join(
        cache_root, "profiles", slug
    )
    port = allocate_port_for_email(
        email, registry, preferred_port=item.get("cdp_port")
    )
    cached_exists = os.path.isdir(profile_dir)
    last_state = str(reg_entry.get("last_state") or "UNCACHED")
    live_state, _, actual_email = classify_cdp_auth_state(port, expected_email=email)

    ready = False
    hint = ""
    if live_state == "AUTHENTICATED":
      ready = True
    elif live_state == "WRONG_ACCOUNT":
      ready = False
      hint = (
          f"Port {port} is signed into '{actual_email}' instead of '{email}'. "
          "Run `manage_persona_profiles.py ensure --reset --keep-alive`."
      )
    elif live_state == "AUTH_REQUIRED":
      ready = False
      hint = f"Sign into '{email}' in the open Chrome window on port {port}."
    elif live_state == "STOPPED" and cached_exists and last_state == "AUTHENTICATED":
      ready = True
      hint = "Cached AUTHENTICATED profile ready (will auto-spawn headless during capture)."
    else:
      ready = False
      hint = "Run `manage_persona_profiles.py ensure --env .runtime/demo_env.json --keep-alive` for one-time SSO login."

    persona_checks.append({
        "persona": item["persona"],
        "email": email,
        "cdp_port": port,
        "profile_dir": profile_dir,
        "cached_profile_exists": cached_exists,
        "registry_last_state": last_state,
        "live_state": live_state,
        "actual_email": actual_email,
        "ready": ready,
        "hint": hint,
    })

  drive_checks: List[Dict[str, Any]] = []
  if getattr(args, "check_drive", False):
    drive_checks = [
        check_corp_cli_binary(GDRIVE_BIN),
        check_corp_cli_binary(GDOCS_BIN),
    ]

  overall_ok = bool(chrome_info["ok"]) and all(
      p["ready"] for p in persona_checks
  ) and all(d["ok"] for d in drive_checks)

  report = {
      "ok": overall_ok,
      "chrome": chrome_info,
      "personas": persona_checks,
      "drive_clis": drive_checks,
  }

  if args.json:
    print(json.dumps(report, indent=2))
  else:
    c_badge = "[OK]" if chrome_info["ok"] else "[FAIL]"
    print(
        f"{c_badge} Chrome binary: {chrome_info.get('binary') or chrome_info.get('error')}"
    )
    for p in persona_checks:
      p_badge = "[READY]" if p["ready"] else f"[{p['live_state']}]"
      extra = f" ({p['hint']})" if p["hint"] else ""
      print(
          f"{p_badge} Persona '{p['persona']}' ({p['email']}) -> port {p['cdp_port']} "
          f"[live={p['live_state']}, cached={p['registry_last_state']}]{extra}"
      )
    for d in drive_checks:
      d_badge = "[OK]" if d["ok"] else f"[{d['status']}]"
      extra = f" — {d['hint']}" if d["hint"] else ""
      print(f"{d_badge} {os.path.basename(d['binary'])}: {d['binary']}{extra}")

  if not chrome_info["ok"]:
    return 1
  if any(d["status"] == "GCERT_REQUIRED" for d in drive_checks):
    return 2
  if any(not d["ok"] for d in drive_checks):
    return 1
  if any(not p["ready"] for p in persona_checks):
    return 2
  return 0


def cmd_list(args: argparse.Namespace) -> int:
  cache_root = os.path.abspath(os.path.expanduser(args.cache_dir))
  registry = load_registry(cache_root)
  rows = []
  for _, info in sorted(registry.get("profiles", {}).items()):
    port = info.get("cdp_port")
    email = str(info.get("email", ""))
    state, _, actual = (
        classify_cdp_auth_state(port, expected_email=email)
        if isinstance(port, int)
        else ("STOPPED", [], "")
    )
    rows.append({**info, "live_state": state, "live_email": actual})

  if args.json:
    print(json.dumps({"profiles": rows}, indent=2))
  elif not rows:
    print(f"No cached persona profiles found in {cache_root}")
  else:
    for r in rows:
      actual_note = (
          f", signed_in='{r['live_email']}'" if r.get("live_email") else ""
      )
      print(
          f"[{r['live_state']}] {r['email']} -> port {r['cdp_port']} "
          f"(persona='{r.get('last_persona', '')}'{actual_note}, dir='{r['profile_dir']}')"
      )
  return 0


def cmd_stop(args: argparse.Namespace) -> int:
  cache_root = os.path.abspath(os.path.expanduser(args.cache_dir))
  registry = load_registry(cache_root)
  profiles = registry.get("profiles", {})
  target_emails: List[str] = []

  if args.all:
    target_emails = list(profiles.keys())
  elif args.env:
    _, loaded = load_personas_from_env(args.env)
    target_emails = [p["email"].strip().lower() for p in loaded]
  elif args.email:
    target_emails = [args.email.strip().lower()]
  else:
    raise RuntimeError("Pass --env <demo_env.json>, --email <email>, or --all to stop.")

  stopped = 0
  for key in target_emails:
    info = profiles.get(key)
    if not info:
      continue
    pid_file = os.path.join(info["profile_dir"], "chrome_cdp.pid")
    if os.path.isfile(pid_file):
      try:
        with open(pid_file, "r", encoding="utf-8") as f:
          pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        stopped += 1
        print(f"[STOPPED] {info['email']} (PID {pid})")
      except (ValueError, ProcessLookupError, PermissionError, OSError):
        pass
      try:
        os.remove(pid_file)
      except OSError:
        pass
  print(f"Stopped {stopped} Chrome CDP profile instance(s).")
  return 0


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
      description="Manage persistent Argolis/Sandbox Chrome CDP profiles for GCP Console demos."
  )
  parser.add_argument(
      "--cache-dir",
      default=DEFAULT_CACHE_ROOT,
      help=f"Root cache directory for Chrome profiles (default: {DEFAULT_CACHE_ROOT})",
  )
  sub = parser.add_subparsers(dest="subcommand", required=True)

  for name, help_text in (
      ("ensure", "Launch missing Chrome CDP profiles and verify Google Console SSO state"),
      ("status", "Check running CDP ports and Google Console SSO state without launching"),
  ):
    p = sub.add_parser(name, help=help_text)
    p.add_argument("--env", help="Path to .runtime/demo_env.json")
    p.add_argument("--persona", help="Single persona role name (when not using --env)")
    p.add_argument("--email", help="Single Argolis/Sandbox email (when not using --env)")
    p.add_argument("--project", help="Optional Sandbox GCP Project ID for initial URL")
    p.add_argument("--port", type=int, help="Optional explicit CDP port override")
    p.add_argument("--url", help="Optional initial URL override")
    p.add_argument("--json", action="store_true", help="Emit JSON output")
    if name == "ensure":
      p.add_argument(
          "--keep-alive",
          action="store_true",
          help="Keep foreground daemon alive so subprocess runners do not reap Chrome children",
      )
      p.add_argument(
          "--reset",
          action="store_true",
          help="Wipe cached profile directory before launching (useful if wrong Google account was signed in)",
      )
      p.add_argument(
          "--headless",
          action="store_true",
          help="Launch Chrome in --headless=new mode (only use for already-authenticated profiles)",
      )

  p_pre = sub.add_parser(
      "precheck",
      help="Verify Chrome binary, persona SSO cache/account match, and optional gdrive/gdocs LOAS (gcert) readiness",
  )
  p_pre.add_argument("--env", help="Path to .runtime/demo_env.json")
  p_pre.add_argument("--persona", help="Single persona role name (when not using --env)")
  p_pre.add_argument("--email", help="Single Argolis/Sandbox email (when not using --env)")
  p_pre.add_argument("--port", type=int, help="Optional explicit CDP port override")
  p_pre.add_argument(
      "--check-drive",
      action="store_true",
      help="Also verify gdrive/gdocs Corp CLI mount and LOAS (gcert) readiness",
  )
  p_pre.add_argument("--json", action="store_true", help="Emit JSON output")

  p_list = sub.add_parser("list", help="List all cached Chrome persona profiles")
  p_list.add_argument("--json", action="store_true", help="Emit JSON output")

  p_stop = sub.add_parser("stop", help="Stop Chrome CDP profile browser processes")
  p_stop.add_argument("--env", help="Stop personas listed in .runtime/demo_env.json")
  p_stop.add_argument("--email", help="Stop a specific persona email profile")
  p_stop.add_argument("--all", action="store_true", help="Stop all cached profiles")

  return parser


def main() -> int:
  parser = build_parser()
  args = parser.parse_args()
  try:
    if args.subcommand == "ensure":
      return cmd_ensure_or_status(args, launch_missing=True)
    if args.subcommand == "status":
      return cmd_ensure_or_status(args, launch_missing=False)
    if args.subcommand == "precheck":
      return cmd_precheck(args)
    if args.subcommand == "list":
      return cmd_list(args)
    if args.subcommand == "stop":
      return cmd_stop(args)
  except RuntimeError as exc:
    print(f"Error: {exc}", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  sys.exit(main())

