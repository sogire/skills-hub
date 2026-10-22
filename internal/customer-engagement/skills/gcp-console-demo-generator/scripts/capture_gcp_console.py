#!/usr/bin/env python3
"""Capture sanitized, callout-annotated 2x HiDPI Google Cloud Console screenshots.

100% Python 3 Standard Library (zero external pip/uv dependencies; uses a native
RFC 6455 WebSocket + Chrome DevTools Protocol client).

Usage:
  # Live multi-persona capture against Chrome CDP profiles from manage_persona_profiles.py:
  python3 capture_gcp_console.py --manifest .runtime/capture_manifest.json

  # Local headless Chrome test mode (for HTML fixtures / non-SSO verification):
  python3 capture_gcp_console.py --manifest .runtime/capture_manifest.json --headless-local
"""

import argparse
import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

AUTH_URL_PREFIXES = (
    "https://accounts.google.com",
    "https://login.corp.google.com",
    "https://myaccount.google.com/signin",
)

COLOR_PALETTE: Dict[str, Dict[str, str]] = {
    "blue": {
        "border": "#1A73E8",
        "fill": "rgba(26, 115, 232, 0.09)",
        "badge_bg": "#1A73E8",
        "pill_bg": "#E8F0FE",
        "pill_fg": "#174EA6",
    },
    "amber": {
        "border": "#F9AB00",
        "fill": "rgba(249, 171, 0, 0.11)",
        "badge_bg": "#E37400",
        "pill_bg": "#FEF7E0",
        "pill_fg": "#B06000",
    },
    "red": {
        "border": "#D93025",
        "fill": "rgba(217, 48, 37, 0.09)",
        "badge_bg": "#D93025",
        "pill_bg": "#FCE8E6",
        "pill_fg": "#A50E0E",
    },
    "green": {
        "border": "#1E8E3E",
        "fill": "rgba(30, 142, 62, 0.09)",
        "badge_bg": "#1E8E3E",
        "pill_bg": "#E6F4EA",
        "pill_fg": "#0D652D",
    },
    "purple": {
        "border": "#9334E6",
        "fill": "rgba(147, 52, 230, 0.09)",
        "badge_bg": "#9334E6",
        "pill_bg": "#F3E8FD",
        "pill_fg": "#681DA8",
    },
}

DEFAULT_SPINNER_SELECTORS = [
    "mat-progress-spinner:visible",
    "mat-spinner:visible",
    'mat-progress-bar[mode="indeterminate"]:visible',
    ".cfc-progress-spinner:visible",
]

# Shadow-DOM-aware selector helper supporting:
#   - Standard CSS selectors ("#id", ".monaco-editor", "[role='tab']")
#   - ":visible" suffix
#   - "text=Foo" / "text='Foo'" substring text match
#   - "<css>:has-text('Run')" / '<css>:has-text("Run")'
FIND_ELEMENT_JS = r"""
(rawSelector, requireVisible) => {
  function isVisible(el) {
    if (!el || !el.getBoundingClientRect) return false;
    const style = window.getComputedStyle(el);
    if (!style || style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity || '1') === 0) {
      return false;
    }
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }

  function collectAllElements(root, out) {
    if (!root) return;
    const children = root.children || [];
    for (let i = 0; i < children.length; i++) {
      const el = children[i];
      out.push(el);
      if (el.shadowRoot) {
        collectAllElements(el.shadowRoot, out);
      }
      collectAllElements(el, out);
    }
  }

  function queryCssDeep(root, css, out) {
    if (!root) return;
    try {
      const matched = root.querySelectorAll(css);
      for (let i = 0; i < matched.length; i++) out.push(matched[i]);
    } catch (e) {}
    const all = [];
    collectAllElements(root, all);
    for (const el of all) {
      if (el.shadowRoot) {
        try {
          const sm = el.shadowRoot.querySelectorAll(css);
          for (let j = 0; j < sm.length; j++) out.push(sm[j]);
        } catch (e) {}
      }
    }
  }

  let sel = String(rawSelector || '').trim();
  let mustBeVisible = Boolean(requireVisible);
  if (sel.endsWith(':visible')) {
    mustBeVisible = true;
    sel = sel.slice(0, -8).trim();
  }

  let candidates = [];
  const hasTextMatch = sel.match(/^(.*):has-text\((['"]?)(.*?)\2\)\s*$/i);

  if (sel.startsWith('text=')) {
    let needle = sel.slice(5).trim();
    if ((needle.startsWith('"') && needle.endsWith('"')) || (needle.startsWith("'") && needle.endsWith("'"))) {
      needle = needle.slice(1, -1);
    }
    const needleLower = needle.toLowerCase();
    const all = [];
    collectAllElements(document.documentElement, all);
    // Prefer deepest matching visible element
    for (const el of all) {
      if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') continue;
      const txt = (el.innerText || el.textContent || '').trim();
      if (txt.toLowerCase().includes(needleLower)) {
        candidates.push(el);
      }
    }
    candidates.reverse();
  } else if (hasTextMatch) {
    const baseCss = hasTextMatch[1].trim() || '*';
    const needleLower = hasTextMatch[3].toLowerCase();
    const baseMatches = [];
    queryCssDeep(document, baseCss, baseMatches);
    for (const el of baseMatches) {
      const txt = (el.innerText || el.textContent || '').trim();
      if (txt.toLowerCase().includes(needleLower)) candidates.push(el);
    }
  } else {
    const parts = sel.split(',').map(s => s.trim()).filter(Boolean);
    for (const part of parts) {
      const cleanPart = part.endsWith(':visible') ? part.slice(0, -8).trim() : part;
      queryCssDeep(document, cleanPart, candidates);
    }
  }

  for (const el of candidates) {
    if (!mustBeVisible || isVisible(el)) {
      const r = el.getBoundingClientRect();
      return {
        found: true,
        tagName: el.tagName,
        x: r.left,
        y: r.top,
        width: r.width,
        height: r.height,
        centerX: r.left + r.width / 2,
        centerY: r.top + r.height / 2,
      };
    }
  }
  return { found: false };
}
"""

DOM_SANITIZE_AND_OVERLAY_JS = r"""
async (payload) => {
  window.__gcpDemoReverts = window.__gcpDemoReverts || [];
  const reverts = window.__gcpDemoReverts;
  const pairs = payload.replacements || [];

  function applyPairs(str) {
    if (!str || typeof str !== 'string') return str;
    let out = str;
    for (const [needle, repl] of pairs) {
      if (needle && out.includes(needle)) {
        out = out.split(needle).join(repl);
      }
    }
    return out;
  }

  function walkRoot(root) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
    let node = walker.currentNode;
    while (node) {
      if (node.nodeType === Node.TEXT_NODE) {
        const parentTag = node.parentElement ? node.parentElement.tagName : '';
        if (parentTag !== 'SCRIPT' && parentTag !== 'STYLE') {
          const orig = node.nodeValue;
          const updated = applyPairs(orig);
          if (updated !== orig) {
            node.nodeValue = updated;
            const targetNode = node;
            reverts.push(() => { targetNode.nodeValue = orig; });
          }
        }
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        const el = node;
        for (const attr of ['title', 'aria-label', 'placeholder']) {
          if (el.hasAttribute && el.hasAttribute(attr)) {
            const origAttr = el.getAttribute(attr);
            const updatedAttr = applyPairs(origAttr);
            if (updatedAttr !== origAttr) {
              el.setAttribute(attr, updatedAttr);
              reverts.push(() => { el.setAttribute(attr, origAttr); });
            }
          }
        }
        if ((el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') && typeof el.value === 'string') {
          const origVal = el.value;
          const updatedVal = applyPairs(origVal);
          if (updatedVal !== origVal) {
            el.value = updatedVal;
            reverts.push(() => { el.value = origVal; });
          }
        }
        if (el.shadowRoot) {
          walkRoot(el.shadowRoot);
        }
      }
      node = walker.nextNode();
    }
  }

  if (document.activeElement && typeof document.activeElement.blur === 'function') {
    try { document.activeElement.blur(); } catch (e) {}
  }

  // Hide Google cookie notification bars that overlap bottom persona badges
  const allDivs = document.querySelectorAll('div, section, aside, cfc-cookie-banner, glue-cookie-notification-bar');
  for (const el of allDivs) {
    const txt = (el.innerText || '').trim();
    if (txt.includes('uses cookies from Google to deliver and enhance') && el.getBoundingClientRect().height < 140) {
      const prevVis = el.style.visibility;
      el.style.setProperty('visibility', 'hidden', 'important');
      reverts.push(() => { el.style.visibility = prevVis; });
    }
  }

  const hideSelectors = [
    'cfc-cookie-banner',
    '.cfc-promo-banner',
    '.cfc-survey-banner',
    'img[src*="googleusercontent.com"]',
    'img[src*="lh3.google.com"]',
    ...(payload.extra_hide_selectors || [])
  ];
  const styleEl = document.createElement('style');
  styleEl.id = '__gcp_demo_temp_style__';
  styleEl.textContent = hideSelectors.map(s => `${s} { visibility: hidden !important; }`).join('\n');
  document.head.appendChild(styleEl);
  reverts.push(() => { styleEl.remove(); });

  const overlay = document.createElement('div');
  overlay.id = '__gcp_demo_overlay_root__';
  Object.assign(overlay.style, {
    position: 'fixed',
    inset: '0',
    width: '100vw',
    height: '100vh',
    pointerEvents: 'none',
    zIndex: '2147483646',
    fontFamily: '"Google Sans", Roboto, Arial, sans-serif',
  });

  if (payload.persona_banner && payload.persona_banner.label) {
    const pb = payload.persona_banner;
    const theme = payload.palette[pb.color || 'blue'] || payload.palette.blue;
    const pos = pb.position || 'bottom-right';
    const banner = document.createElement('div');
    const posStyle = pos === 'top-right'
      ? { top: '8px', right: '16px' }
      : pos === 'bottom-left'
        ? { bottom: '14px', left: '18px' }
        : { bottom: '14px', right: '18px' };
    Object.assign(banner.style, {
      position: 'fixed',
      ...posStyle,
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '6px 14px',
      borderRadius: '999px',
      background: theme.pill_bg,
      color: theme.pill_fg,
      border: `2px solid ${theme.border}`,
      fontSize: '13px',
      fontWeight: '700',
      boxShadow: '0 2px 10px rgba(0,0,0,0.18)',
      letterSpacing: '0.1px',
    });
    const dot = document.createElement('span');
    Object.assign(dot.style, {
      width: '9px',
      height: '9px',
      borderRadius: '50%',
      background: theme.badge_bg,
      display: 'inline-block',
    });
    const txt = document.createElement('span');
    txt.textContent = pb.label;
    banner.appendChild(dot);
    banner.appendChild(txt);
    overlay.appendChild(banner);
  }

  const vw = window.innerWidth || 1600;
  const vh = window.innerHeight || 1000;

  for (const item of (payload.resolved_callouts || [])) {
    const theme = payload.palette[item.color || 'blue'] || payload.palette.blue;
    const pad = typeof item.padding === 'number' ? item.padding : 6;
    const bx = Math.max(2, item.x - pad);
    const by = Math.max(2, item.y - pad);
    const bw = Math.min(vw - bx - 2, item.width + pad * 2);
    const bh = Math.min(vh - by - 2, item.height + pad * 2);

    const box = document.createElement('div');
    Object.assign(box.style, {
      position: 'fixed',
      left: `${bx}px`,
      top: `${by}px`,
      width: `${bw}px`,
      height: `${bh}px`,
      border: `3px solid ${theme.border}`,
      background: theme.fill,
      borderRadius: '8px',
      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.14)',
      boxSizing: 'border-box',
    });
    overlay.appendChild(box);

    if (item.step !== undefined && item.step !== null) {
      const badgeSize = 28;
      const anchor = item.anchor || 'top-right';
      let cx = bx + bw - 14;
      let cy = by - 16;
      if (anchor === 'top-left') { cx = bx - 12; cy = by - 16; }
      else if (anchor === 'top-right') { cx = bx + bw - (item.label ? 240 : 14); cy = by - 16; }
      else if (anchor === 'bottom-left') { cx = bx + 8; cy = by + bh + 6; }
      else if (anchor === 'bottom-right') { cx = bx + bw - (item.label ? 240 : 14); cy = by + bh + 6; }
      else if (anchor === 'left') { cx = bx - 16; cy = by + (bh / 2) - 14; }
      else if (anchor === 'right') { cx = bx + bw + 8; cy = by + (bh / 2) - 14; }

      cx = Math.max(4, Math.min(vw - badgeSize - 4, cx));
      cy = Math.max(4, Math.min(vh - badgeSize - 4, cy));

      const badge = document.createElement('div');
      Object.assign(badge.style, {
        position: 'fixed',
        left: `${cx}px`,
        top: `${cy}px`,
        width: `${badgeSize}px`,
        height: `${badgeSize}px`,
        borderRadius: '50%',
        background: theme.badge_bg,
        color: '#FFFFFF',
        border: '2px solid #FFFFFF',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '14px',
        fontWeight: '800',
        boxShadow: '0 2px 6px rgba(0, 0, 0, 0.28)',
      });
      badge.textContent = String(item.step);
      overlay.appendChild(badge);

      if (item.label) {
        const pill = document.createElement('div');
        const pillLeft = Math.max(8, Math.min(vw - 320, cx + badgeSize + 6));
        const pillTop = cy + 1;
        Object.assign(pill.style, {
          position: 'fixed',
          left: `${pillLeft}px`,
          top: `${pillTop}px`,
          maxWidth: '340px',
          padding: '4px 10px',
          borderRadius: '6px',
          background: theme.pill_bg,
          color: theme.pill_fg,
          border: `1.5px solid ${theme.border}`,
          fontSize: '12px',
          fontWeight: '700',
          lineHeight: '1.25',
          boxShadow: '0 2px 6px rgba(0, 0, 0, 0.16)',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        });
        pill.textContent = item.label;
        overlay.appendChild(pill);
      }
    }
  }

  document.body.appendChild(overlay);
  reverts.push(() => { overlay.remove(); });

  // Wait one frame after style/overlay injection so Monaco finishes any font/layout reflow,
  // then perform text node replacement synchronously right before screenshot capture.
  await new Promise(resolve => setTimeout(resolve, 120));
  if (pairs.length > 0) {
    walkRoot(document.body || document.documentElement);
  }
  return true;
}
"""

DOM_RESTORE_JS = r"""
() => {
  const reverts = window.__gcpDemoReverts || [];
  while (reverts.length > 0) {
    const fn = reverts.pop();
    try { fn(); } catch (e) {}
  }
  return true;
}
"""


class CDPWebSocket:
  """Minimal RFC 6455 WebSocket + Chrome DevTools Protocol JSON-RPC client (pure stdlib)."""

  def __init__(self, ws_url: str, timeout: float = 30.0):
    parsed = urllib.parse.urlparse(ws_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 80
    path = parsed.path or "/"
    if parsed.query:
      path = f"{path}?{parsed.query}"

    self._sock = socket.create_connection((host, port), timeout=timeout)
    self._buf = bytearray()
    self._next_id = 1
    self._events: List[Dict[str, Any]] = []

    key = base64.b64encode(os.urandom(16)).decode("ascii")
    handshake = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    self._sock.sendall(handshake.encode("ascii"))

    while b"\r\n\r\n" not in self._buf:
      chunk = self._sock.recv(4096)
      if not chunk:
        raise RuntimeError(f"CDP WebSocket handshake closed unexpectedly ({ws_url})")
      self._buf.extend(chunk)

    sep = self._buf.index(b"\r\n\r\n") + 4
    header_bytes = bytes(self._buf[:sep])
    del self._buf[:sep]
    status_line = header_bytes.splitlines()[0].decode("latin1", errors="replace")
    if "101" not in status_line:
      raise RuntimeError(f"CDP WebSocket upgrade failed: {status_line}")

  def _read_exact(self, n: int) -> bytes:
    while len(self._buf) < n:
      chunk = self._sock.recv(max(65536, n - len(self._buf)))
      if not chunk:
        raise RuntimeError("CDP WebSocket closed while reading frame")
      self._buf.extend(chunk)
    out = bytes(self._buf[:n])
    del self._buf[:n]
    return out

  def _send_frame(self, opcode: int, payload: bytes) -> None:
    mask_key = os.urandom(4)
    first_byte = 0x80 | (opcode & 0x0F)
    length = len(payload)
    header = bytearray([first_byte])
    if length < 126:
      header.append(0x80 | length)
    elif length < 65536:
      header.append(0x80 | 126)
      header.extend(struct.pack("!H", length))
    else:
      header.append(0x80 | 127)
      header.extend(struct.pack("!Q", length))
    header.extend(mask_key)
    masked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    self._sock.sendall(bytes(header) + masked)

  def _recv_message(self) -> str:
    fragments: List[bytes] = []
    while True:
      b1, b2 = self._read_exact(2)
      fin = bool(b1 & 0x80)
      opcode = b1 & 0x0F
      masked = bool(b2 & 0x80)
      length = b2 & 0x7F
      if length == 126:
        (length,) = struct.unpack("!H", self._read_exact(2))
      elif length == 127:
        (length,) = struct.unpack("!Q", self._read_exact(8))
      mask_key = self._read_exact(4) if masked else b""
      payload = self._read_exact(length)
      if masked:
        payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))

      if opcode == 0x8:  # Close
        raise RuntimeError("CDP WebSocket closed by browser")
      if opcode == 0x9:  # Ping -> Pong
        self._send_frame(0xA, payload)
        continue
      if opcode == 0xA:  # Pong
        continue

      fragments.append(payload)
      if fin:
        return b"".join(fragments).decode("utf-8")

  def call(
      self,
      method: str,
      params: Optional[Dict[str, Any]] = None,
      timeout: float = 45.0,
  ) -> Dict[str, Any]:
    req_id = self._next_id
    self._next_id += 1
    msg = json.dumps({"id": req_id, "method": method, "params": params or {}})
    self._sock.settimeout(timeout)
    self._send_frame(0x1, msg.encode("utf-8"))

    deadline = time.time() + timeout
    while time.time() < deadline:
      raw = self._recv_message()
      data = json.loads(raw)
      if data.get("id") == req_id:
        if "error" in data:
          raise RuntimeError(f"CDP {method} error: {data['error']}")
        return data.get("result") or {}
      if "method" in data:
        if data["method"] == "Page.javascriptDialogOpening":
          dlg_id = self._next_id
          self._next_id += 1
          dlg_msg = json.dumps({
              "id": dlg_id,
              "method": "Page.handleJavaScriptDialog",
              "params": {"accept": True},
          })
          self._send_frame(0x1, dlg_msg.encode("utf-8"))
        self._events.append(data)
    raise RuntimeError(f"CDP {method} timed out after {timeout}s")

  def drain_events(self, method_name: Optional[str] = None) -> List[Dict[str, Any]]:
    if method_name is None:
      ev = list(self._events)
      self._events.clear()
      return ev
    matched = [e for e in self._events if e.get("method") == method_name]
    self._events = [e for e in self._events if e.get("method") != method_name]
    return matched

  def wait_for_event(self, method_name: str, timeout: float = 30.0) -> bool:
    if self.drain_events(method_name):
      return True
    deadline = time.time() + timeout
    while time.time() < deadline:
      self._sock.settimeout(max(0.2, deadline - time.time()))
      try:
        raw = self._recv_message()
      except (TimeoutError, socket.timeout):
        return False
      data = json.loads(raw)
      if data.get("method") == method_name:
        return True
      if "method" in data:
        if data["method"] == "Page.javascriptDialogOpening":
          dlg_id = self._next_id
          self._next_id += 1
          dlg_msg = json.dumps({
              "id": dlg_id,
              "method": "Page.handleJavaScriptDialog",
              "params": {"accept": True},
          })
          self._send_frame(0x1, dlg_msg.encode("utf-8"))
        self._events.append(data)
    return False

  def close(self) -> None:
    try:
      self._send_frame(0x8, b"")
    except Exception:
      pass
    try:
      self._sock.close()
    except Exception:
      pass


class CDPPageSession:
  """High-level wrapper around a Chrome CDP Page target."""

  def __init__(self, port: int, target_id: str, ws_url: str):
    self.port = port
    self.target_id = target_id
    self.ws = CDPWebSocket(ws_url)
    self.ws.call("Page.enable")
    self.ws.call("Runtime.enable")
    self.ws.call("DOM.enable")

  @classmethod
  def create_tab(cls, port: int) -> "CDPPageSession":
    base = f"http://127.0.0.1:{port}"
    target: Optional[Dict[str, Any]] = None
    for http_method in ("PUT", "GET"):
      req = urllib.request.Request(f"{base}/json/new?about:blank", method=http_method)
      try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:
          if resp.status == 200:
            target = json.loads(resp.read().decode("utf-8"))
            break
      except Exception:
        continue
    if not target or not target.get("webSocketDebuggerUrl"):
      raise RuntimeError(f"Failed to open new CDP tab on port {port}")
    return cls(port, target["id"], target["webSocketDebuggerUrl"])

  def set_hidpi_viewport(self, width: int, height: int, scale: float) -> None:
    self.ws.call(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": height,
            "deviceScaleFactor": scale,
            "mobile": False,
        },
    )

  def eval_js(self, fn_source: str, *args: Any, timeout: float = 30.0) -> Any:
    arg_json = ", ".join(json.dumps(a) for a in args)
    expr = f"({fn_source})({arg_json})"
    res = self.ws.call(
        "Runtime.evaluate",
        {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": True,
        },
        timeout=timeout,
    )
    if "exceptionDetails" in res:
      raise RuntimeError(f"JS evaluation exception: {res['exceptionDetails']}")
    return (res.get("result") or {}).get("value")

  def get_url_and_title(self) -> Tuple[str, str]:
    info = self.eval_js("() => ({ url: String(location.href || ''), title: String(document.title || '') })")
    if isinstance(info, dict):
      return info.get("url", ""), info.get("title", "")
    return "", ""

  def goto(self, url: str, timeout_ms: int = 45000) -> None:
    self.ws.drain_events("Page.loadEventFired")
    self.ws.call("Page.navigate", {"url": url}, timeout=timeout_ms / 1000.0)
    self.ws.wait_for_event("Page.loadEventFired", timeout=min(15.0, timeout_ms / 1000.0))
    # Ensure readyState is at least interactive
    deadline = time.time() + (timeout_ms / 1000.0)
    while time.time() < deadline:
      rs = self.eval_js("() => document.readyState")
      if rs in ("interactive", "complete"):
        return
      time.sleep(0.15)

  def find_element(self, selector: str, require_visible: bool = True) -> Dict[str, Any]:
    res = self.eval_js(FIND_ELEMENT_JS, selector, require_visible)
    return res if isinstance(res, dict) else {"found": False}

  def wait_for_selector(self, selector: str, timeout_ms: int = 30000) -> Dict[str, Any]:
    deadline = time.time() + (timeout_ms / 1000.0)
    while time.time() < deadline:
      info = self.find_element(selector, require_visible=True)
      if info.get("found"):
        return info
      time.sleep(0.25)
    raise RuntimeError(f"Timed out waiting ({timeout_ms}ms) for selector: {selector}")

  def click_selector(self, selector: str, timeout_ms: int = 30000, optional: bool = False) -> None:
    try:
      info = self.wait_for_selector(selector, timeout_ms=2000 if optional else timeout_ms)
    except RuntimeError:
      if optional:
        return
      raise
    cx, cy = float(info["centerX"]), float(info["centerY"])
    for ev_type in ("mouseMoved", "mousePressed", "mouseReleased"):
      params: Dict[str, Any] = {"type": ev_type, "x": cx, "y": cy}
      if ev_type in ("mousePressed", "mouseReleased"):
        params["button"] = "left"
        params["clickCount"] = 1
      self.ws.call("Input.dispatchMouseEvent", params)

  def capture_png(self, out_path: str, clip: Optional[Dict[str, Any]] = None) -> None:
    params: Dict[str, Any] = {"format": "png", "captureBeyondViewport": False}
    if isinstance(clip, dict):
      params["clip"] = {
          "x": float(clip["x"]),
          "y": float(clip["y"]),
          "width": float(clip["width"]),
          "height": float(clip["height"]),
          "scale": float(clip.get("scale", 1)),
      }
    res = self.ws.call("Page.captureScreenshot", params, timeout=30.0)
    png_bytes = base64.b64decode(res["data"])
    with open(out_path, "wb") as f:
      f.write(png_bytes)

  def close_tab(self) -> None:
    self.ws.close()
    try:
      urllib.request.urlopen(
          f"http://127.0.0.1:{self.port}/json/close/{self.target_id}", timeout=2.0
      ).read()
    except Exception:
      pass


def find_chrome_binary() -> str:
  for cand in (
      os.environ.get("CHROME_BIN"),
      "/usr/bin/google-chrome-stable",
      "/usr/bin/google-chrome",
      "/opt/google/chrome/google-chrome",
      shutil.which("google-chrome-stable"),
      shutil.which("chromium"),
  ):
    if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
      return cand
  raise RuntimeError(
      "Google Chrome binary not found (checked /usr/bin/google-chrome-stable and CHROME_BIN). "
      "If running inside a restricted container without /opt/google/chrome mounted, run on host."
  )


def pick_free_port() -> int:
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("127.0.0.1", 0))
    return int(s.getsockname()[1])


def launch_ephemeral_headless_chrome(profile_dir: str) -> Tuple[subprocess.Popen, int]:
  chrome_bin = find_chrome_binary()
  port = pick_free_port()
  cmd = [
      chrome_bin,
      "--headless=new",
      "--no-sandbox",
      "--disable-gpu",
      "--disable-dev-shm-usage",
      f"--user-data-dir={profile_dir}",
      f"--remote-debugging-port={port}",
      "--remote-debugging-address=127.0.0.1",
      "--no-first-run",
      "--window-size=1600,1000",
      "about:blank",
  ]
  proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  deadline = time.time() + 12.0
  while time.time() < deadline:
    try:
      with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1.0) as r:
        if r.status == 200:
          return proc, port
    except Exception:
      time.sleep(0.25)
  proc.terminate()
  raise RuntimeError(f"Headless Chrome failed to open CDP port {port} within 12s.")


def load_json_file(path: str) -> Dict[str, Any]:
  with open(path, "r", encoding="utf-8") as f:
    return json.load(f)


def build_replacement_pairs(
    env_data: Dict[str, Any],
    manifest: Dict[str, Any],
    scene: Dict[str, Any],
) -> List[List[str]]:
  mapping: Dict[str, str] = {}

  real_proj = env_data.get("sandbox_project_id")
  default_proj_alias = scene.get("project_display_alias") or env_data.get(
      "default_project_alias"
  )
  if real_proj and default_proj_alias and real_proj != default_proj_alias:
    mapping[str(real_proj)] = str(default_proj_alias)

  real_num = env_data.get("sandbox_project_number")
  alias_num = env_data.get("alias_project_number")
  if real_num and alias_num and str(real_num) != str(alias_num):
    mapping[str(real_num)] = str(alias_num)

  real_name = env_data.get("sandbox_project_name")
  alias_name = env_data.get("alias_project_name") or default_proj_alias
  if real_name and alias_name and str(real_name) != str(alias_name):
    mapping[str(real_name)] = str(alias_name)

  for real_ds, alias_ds in (env_data.get("dataset_aliases") or {}).items():
    if real_ds and alias_ds and real_ds != alias_ds:
      mapping[str(real_ds)] = str(alias_ds)

  personas = env_data.get("personas") or {}
  if isinstance(personas, dict):
    for _, pinfo in personas.items():
      if isinstance(pinfo, dict):
        em = pinfo.get("argolis_email")
        al = pinfo.get("display_alias")
        if em and al and em != al:
          mapping[str(em)] = str(al)

  for source in (
      manifest.get("dom_replacements") or {},
      scene.get("dom_replacements") or {},
  ):
    if isinstance(source, dict):
      for k, v in source.items():
        if k and v is not None and str(k) != str(v):
          mapping[str(k)] = str(v)
    elif isinstance(source, list):
      for pair in source:
        if isinstance(pair, (list, tuple)) and len(pair) == 2 and pair[0]:
          mapping[str(pair[0])] = str(pair[1])

  ordered = sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True)
  return [[k, v] for k, v in ordered]


def verify_not_auth_wall(
    session: CDPPageSession,
    persona: str,
    allow_auth: bool,
    expected_email: str = "",
) -> None:
  if allow_auth:
    return
  cur_url, title = session.get_url_and_title()
  url_l = cur_url.lower()
  title_l = title.lower()
  if any(url_l.startswith(pref) for pref in AUTH_URL_PREFIXES) or (
      "sign in - google accounts" in title_l
  ):
    raise RuntimeError(
        f"AUTH_REQUIRED: Persona '{persona}' redirected to Google Sign-In ({cur_url}). "
        "Complete one-time Google SSO sign-in in that persona's Chrome window via "
        "`manage_persona_profiles.py ensure`, then re-run capture."
    )
  if expected_email and url_l.startswith("https://console.cloud.google.com"):
    actual_email = session.eval_js(
        """() => {
          const els = document.querySelectorAll('[aria-label*="Account:"], a[aria-label*="Google Account"], button[aria-label*="Google Account"]');
          for (const el of els) {
            const lbl = el.getAttribute('aria-label') || '';
            const m = lbl.match(/\\(([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)\\)/);
            if (m) return m[1].toLowerCase();
          }
          return '';
        }"""
    )
    if actual_email and actual_email != expected_email.strip().lower():
      raise RuntimeError(
          f"AUTH_REQUIRED: Persona '{persona}' expected '{expected_email}' "
          f"but Chrome profile is signed into '{actual_email}'. "
          "Re-run `manage_persona_profiles.py ensure --reset` for that persona."
      )


def wait_for_spinners_gone(session: CDPPageSession, timeout_ms: int = 20000) -> None:
  deadline = time.time() + (timeout_ms / 1000.0)
  while time.time() < deadline:
    busy = False
    for sel in DEFAULT_SPINNER_SELECTORS:
      if session.find_element(sel, require_visible=True).get("found"):
        busy = True
        break
    if not busy:
      return
    time.sleep(0.35)


def execute_scene_actions(session: CDPPageSession, actions: List[Dict[str, Any]]) -> None:
  for act in actions:
    kind = act.get("type", "").strip()
    timeout_ms = int(act.get("timeout_ms", 30000))

    if kind == "goto":
      session.goto(act["url"], timeout_ms=timeout_ms)
    elif kind == "wait_for_selector":
      session.wait_for_selector(act["selector"], timeout_ms=timeout_ms)
    elif kind == "wait_for_text":
      session.wait_for_selector(f"text={json.dumps(str(act['text']))}", timeout_ms=timeout_ms)
    elif kind == "wait_for_spinners_gone":
      wait_for_spinners_gone(session, timeout_ms=timeout_ms)
    elif kind == "click":
      session.click_selector(
          act["selector"], timeout_ms=timeout_ms, optional=bool(act.get("optional"))
      )
    elif kind == "fill":
      session.click_selector(act["selector"], timeout_ms=timeout_ms)
      session.eval_js(
          """(sel, val) => {
            const el = document.activeElement;
            if (el && ('value' in el)) {
              el.value = val;
              el.dispatchEvent(new Event('input', { bubbles: true }));
              el.dispatchEvent(new Event('change', { bubbles: true }));
            }
          }""",
          act["selector"],
          str(act["value"]),
      )
    elif kind == "press":
      if act.get("selector"):
        session.click_selector(act["selector"], timeout_ms=timeout_ms)
      key = str(act["key"])
      session.ws.call("Input.dispatchKeyEvent", {"type": "keyDown", "key": key})
      session.ws.call("Input.dispatchKeyEvent", {"type": "keyUp", "key": key})
    elif kind == "bq_set_query":
      sql = str(act["sql"])
      if act.get("clean_tabs", True):
        clean_bigquery_studio_tabs(session, timeout_ms=min(timeout_ms, 10000))

      deadline = time.time() + (timeout_ms / 1000.0)
      clicked_new_tab = False
      focused_ta = False
      while time.time() < deadline:
        probe = session.eval_js(
            """(alreadyClicked) => {
              const tas = [...document.querySelectorAll('textarea.inputarea')].filter(el => {
                const r = el.getBoundingClientRect();
                const parent = el.closest('.monaco-editor');
                if (parent) {
                  const pr = parent.getBoundingClientRect();
                  return pr.width > 0 && pr.height > 0;
                }
                return r.width > 0 || r.height > 0 || document.body.contains(el);
              });
              if (tas.length > 0) {
                const ta = tas[tas.length - 1];
                ta.focus();
                return { status: 'READY' };
              }
              if (!alreadyClicked) {
                const btns = [...document.querySelectorAll('button, [role="button"]')].filter(b => {
                  const r = b.getBoundingClientRect();
                  return r.width > 0 && r.height > 0;
                });
                const sqlBtn =
                  btns.find(b => (b.innerText || '').trim() === 'SQL query') ||
                  btns.find(b => /sql query|compose a? ?new query|new sql query|add new editor tab/i.test(
                    (b.getAttribute('aria-label') || '') + ' ' + (b.getAttribute('mattooltip') || '') + ' ' + (b.getAttribute('title') || '')
                  ));
                if (sqlBtn) {
                  const r = sqlBtn.getBoundingClientRect();
                  return {
                    status: 'CLICK_NEW_TAB',
                    cx: r.left + r.width / 2,
                    cy: r.top + r.height / 2,
                  };
                }
              }
              return { status: 'WAITING' };
            }""",
            clicked_new_tab,
        )
        status = probe.get("status") if isinstance(probe, dict) else "WAITING"
        if status == "READY":
          focused_ta = True
          break
        if status == "CLICK_NEW_TAB" and isinstance(probe, dict):
          dispatch_trusted_click(session, float(probe["cx"]), float(probe["cy"]))
          clicked_new_tab = True
          time.sleep(1.4)
        else:
          time.sleep(0.45)

      if not focused_ta:
        raise RuntimeError(f"Timed out waiting ({timeout_ms}ms) for BigQuery SQL editor textarea.")

      used_monaco = session.eval_js(
          """(sqlText) => {
            if (window.monaco && window.monaco.editor && window.monaco.editor.getModels) {
              const models = window.monaco.editor.getModels();
              if (models && models.length > 0) {
                models[models.length - 1].setValue(sqlText);
                return true;
              }
            }
            return false;
          }""",
          sql,
      )
      if not used_monaco:
        session.ws.call(
            "Input.dispatchKeyEvent",
            {"type": "keyDown", "modifiers": 2, "key": "a", "code": "KeyA", "windowsVirtualKeyCode": 65},
        )
        session.ws.call(
            "Input.dispatchKeyEvent",
            {"type": "keyUp", "modifiers": 2, "key": "a", "code": "KeyA", "windowsVirtualKeyCode": 65},
        )
        session.ws.call(
            "Input.dispatchKeyEvent",
            {"type": "keyDown", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8},
        )
        session.ws.call(
            "Input.dispatchKeyEvent",
            {"type": "keyUp", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8},
        )
        time.sleep(0.15)
        session.ws.call("Input.insertText", {"text": sql})
      time.sleep(0.8)
    elif kind == "bq_run_query":
      run_timeout_ms = int(act.get("timeout_ms", 45000))
      deadline = time.time() + (run_timeout_ms / 1000.0)
      triggered = False
      while time.time() < deadline:
        target_btn = session.eval_js(
            """() => {
              const cfcBtns = [...document.querySelectorAll('cfc-progress-button button')];
              for (const b of cfcBtns) {
                const r = b.getBoundingClientRect();
                if (r.width <= 0 || r.height <= 0 || r.top > 135) continue;
                if (b.disabled || b.getAttribute('aria-disabled') === 'true') continue;
                if ((b.innerText || '').trim() === 'Run') {
                  return { cx: r.left + r.width / 2, cy: r.top + r.height / 2 };
                }
              }
              const topBtns = [...document.querySelectorAll('button')];
              for (const b of topBtns) {
                const r = b.getBoundingClientRect();
                if (r.width <= 0 || r.height <= 0 || r.top > 120) continue;
                if (b.disabled || b.getAttribute('aria-disabled') === 'true') continue;
                if ((b.innerText || '').trim() === 'Run') {
                  return { cx: r.left + r.width / 2, cy: r.top + r.height / 2 };
                }
              }
              if (cfcBtns.length === 0 && location.hostname !== 'console.cloud.google.com') {
                for (const b of topBtns) {
                  const r = b.getBoundingClientRect();
                  if (r.width <= 0 || r.height <= 0) continue;
                  if (b.disabled || b.getAttribute('aria-disabled') === 'true') continue;
                  if ((b.innerText || '').trim() === 'Run') {
                    return { cx: r.left + r.width / 2, cy: r.top + r.height / 2 };
                  }
                }
              }
              return null;
            }"""
        )
        if isinstance(target_btn, dict):
          dispatch_trusted_click(session, float(target_btn["cx"]), float(target_btn["cy"]))
          triggered = True
          break
        time.sleep(0.35)
      if not triggered:
        raise RuntimeError(f"Timed out waiting ({run_timeout_ms}ms) for enabled BigQuery 'Run' button.")
      time.sleep(0.9)
      if act.get("wait_for_completion", True):
        wait_for_bq_job_completion(session, deadline=deadline, timeout_ms=run_timeout_ms)
    elif kind == "scroll_into_view":
      session.wait_for_selector(act["selector"], timeout_ms=timeout_ms)
      session.eval_js(
          """(sel) => {
            const el = document.querySelector(sel);
            if (el && el.scrollIntoView) el.scrollIntoView({ block: 'center' });
          }""",
          act["selector"],
      )
    elif kind == "evaluate":
      session.ws.call(
          "Runtime.evaluate",
          {"expression": str(act["js"]), "returnByValue": True, "awaitPromise": True},
      )
    elif kind == "sleep":
      time.sleep(int(act.get("ms", 1000)) / 1000.0)
    else:
      raise RuntimeError(f"Unsupported scene action type: '{kind}'")


def dispatch_trusted_click(session: CDPPageSession, cx: float, cy: float) -> None:
  """Dispatch a trusted CDP mouse click at viewport coordinates (cx, cy)."""
  for ev_type in ("mouseMoved", "mousePressed", "mouseReleased"):
    mparams: Dict[str, Any] = {"type": ev_type, "x": cx, "y": cy}
    if ev_type in ("mousePressed", "mouseReleased"):
      mparams["button"] = "left"
      mparams["clickCount"] = 1
    session.ws.call("Input.dispatchMouseEvent", mparams)


def clean_bigquery_studio_tabs(session: CDPPageSession, timeout_ms: int = 8000) -> None:
  """Close restored BigQuery Studio query tabs so each scene starts with zero stale result drawers."""
  hydrate_deadline = time.time() + min(6.0, timeout_ms / 1000.0)
  while time.time() < hydrate_deadline:
    hydrated = session.eval_js(
        """() => {
          if (document.querySelector('textarea.inputarea')) return true;
          if (document.querySelector('[role="tab"]')) return true;
          const btns = [...document.querySelectorAll('button')];
          return btns.some(b => {
            const txt = (b.innerText || '').trim();
            const aria = (b.getAttribute('aria-label') || '');
            return txt === 'SQL query' || /sql query|compose a? ?new query/i.test(aria);
          });
        }"""
    )
    if hydrated:
      break
    time.sleep(0.35)

  for _ in range(8):
    close_target = session.eval_js(
        """() => {
          const tabs = [...document.querySelectorAll('[role="tab"], .cfc-tab, .mat-mdc-tab, .mat-tab-label')];
          const closeTargets = [];
          for (const tab of tabs) {
            const tr = tab.getBoundingClientRect();
            if (tr.width <= 0 || tr.height <= 0 || tr.top < 30 || tr.top > 140) continue;
            const tabText = ((tab.innerText || '') + ' ' + (tab.getAttribute('aria-label') || '')).trim().toLowerCase();
            // Keep the BigQuery Studio Home/Welcome tab untouched so its 'SQL query' launcher stays available
            if (tabText === 'home' || tabText === 'welcome' || tabText.startsWith('home ')) continue;
            const btns = [...tab.querySelectorAll('button, [role="button"], mat-icon')];
            for (const b of btns) {
              const meta = (
                (b.getAttribute('aria-label') || '') + ' ' +
                (b.getAttribute('title') || '') + ' ' +
                (b.getAttribute('mattooltip') || '') + ' ' +
                (b.innerText || '')
              ).trim();
              if (/close/i.test(meta)) {
                const r = b.getBoundingClientRect();
                if (r.width > 0 && r.height > 0) {
                  closeTargets.push({ cx: r.left + r.width / 2, cy: r.top + r.height / 2 });
                  break;
                }
              }
            }
          }
          return closeTargets.length > 0 ? closeTargets[closeTargets.length - 1] : null;
        }"""
    )
    if not isinstance(close_target, dict):
      break
    dispatch_trusted_click(session, float(close_target["cx"]), float(close_target["cy"]))
    time.sleep(0.3)
    confirm_btn = session.eval_js(
        """() => {
          const dialogs = [...document.querySelectorAll('mat-dialog-container, [role="dialog"], .cdk-overlay-pane')];
          for (const dlg of dialogs) {
            const btns = [...dlg.querySelectorAll('button')];
            for (const b of btns) {
              const r = b.getBoundingClientRect();
              if (r.width <= 0 || r.height <= 0) continue;
              const txt = (b.innerText || '').trim();
              if (/^(discard|discard changes|close without saving|close tab|leave|confirm|yes)$/i.test(txt)) {
                return { cx: r.left + r.width / 2, cy: r.top + r.height / 2 };
              }
            }
          }
          return null;
        }"""
    )
    if isinstance(confirm_btn, dict):
      dispatch_trusted_click(session, float(confirm_btn["cx"]), float(confirm_btn["cy"]))
      time.sleep(0.3)


def wait_for_bq_job_completion(
    session: CDPPageSession, deadline: float, timeout_ms: int
) -> None:
  """Wait until BigQuery Studio finishes executing a query (either rows rendered or error banner)."""
  while time.time() < deadline:
    busy = False
    for sel in DEFAULT_SPINNER_SELECTORS:
      if session.find_element(sel, require_visible=True).get("found"):
        busy = True
        break
    if not busy:
      done = session.eval_js(
          """() => {
            const cfcRunBtns = [...document.querySelectorAll('cfc-progress-button button')].filter(b => {
              const r = b.getBoundingClientRect();
              return r.width > 0 && r.height > 0 && r.top <= 135;
            });
            for (const b of cfcRunBtns) {
              const t = (b.innerText || '').trim().toLowerCase();
              if (t === 'cancel' || t === 'running') return false;
            }
            const bodyText = (document.body && document.body.innerText) ? document.body.innerText : '';
            const terminalPhrases = [
              'Query completed',
              'Query complete',
              'Results per page',
              'There is no data to display',
              'Access Denied',
              'Permission denied',
              'Query error',
              'Syntax error',
              'Not found:',
            ];
            for (const phrase of terminalPhrases) {
              if (bodyText.includes(phrase)) return true;
            }
            const saveBtns = [...document.querySelectorAll('button')].filter(b => {
              const r = b.getBoundingClientRect();
              return r.width > 0 && r.height > 0 && r.top > 250 && !b.disabled && b.getAttribute('aria-disabled') !== 'true';
            });
            if (saveBtns.some(b => /save results/i.test((b.innerText || '').trim()))) {
              return true;
            }
            return false;
          }"""
      )
      if done:
        time.sleep(0.4)
        return
    time.sleep(0.35)
  raise RuntimeError(
      f"Timed out waiting ({timeout_ms}ms) for BigQuery query job completion."
  )


INSPECT_SCENE_DOM_JS = r"""
() => {
  function vis(el) {
    if (!el || !el.getBoundingClientRect) return null;
    const st = window.getComputedStyle(el);
    if (!st || st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity || '1') === 0) return null;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return null;
    return {
      x: Math.round(r.left),
      y: Math.round(r.top),
      width: Math.round(r.width),
      height: Math.round(r.height),
    };
  }

  let actualEmail = '';
  const acctEls = document.querySelectorAll('[aria-label*="Account:"], a[aria-label*="Google Account"], button[aria-label*="Google Account"]');
  for (const el of acctEls) {
    const lbl = el.getAttribute('aria-label') || '';
    const m = lbl.match(/\(([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)\)/);
    if (m) { actualEmail = m[1].toLowerCase(); break; }
  }

  const tabs = [];
  for (const el of document.querySelectorAll('[role="tab"]')) {
    const box = vis(el);
    if (!box) continue;
    tabs.push({
      text: (el.innerText || '').trim().slice(0, 80),
      ariaLabel: (el.getAttribute('aria-label') || '').slice(0, 80),
      selected: el.getAttribute('aria-selected') === 'true',
      ...box,
    });
  }

  const buttons = [];
  for (const el of document.querySelectorAll('button, [role="button"]')) {
    const box = vis(el);
    if (!box) continue;
    const text = (el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 80);
    const ariaLabel = (el.getAttribute('aria-label') || '').slice(0, 80);
    if (!text && !ariaLabel) continue;
    buttons.push({
      text,
      ariaLabel,
      disabled: Boolean(el.disabled || el.getAttribute('aria-disabled') === 'true'),
      ...box,
    });
    if (buttons.length >= 60) break;
  }

  const canvases = [];
  for (const el of document.querySelectorAll('canvas')) {
    const box = vis(el);
    if (box) canvases.push(box);
  }

  const statusMatchers = [
    'Query completed',
    'Query complete',
    'This query will process',
    'Query results',
    'Results per page',
    'Access Denied',
    'Permission denied',
    'Query error',
  ];
  const banners = [];
  const seen = new Set();
  for (const el of document.querySelectorAll('div, span, p, section, cfc-message, mat-error')) {
    const box = vis(el);
    if (!box || box.height > 220) continue;
    const txt = (el.innerText || '').trim().replace(/\s+/g, ' ');
    if (!txt || txt.length > 260) continue;
    if (statusMatchers.some(m => txt.includes(m))) {
      const key = `${txt}@${box.x},${box.y}`;
      if (!seen.has(key)) {
        seen.add(key);
        banners.push({ text: txt, ...box });
      }
    }
    if (banners.length >= 25) break;
  }

  return {
    url: String(location.href || ''),
    title: String(document.title || ''),
    actual_email: actualEmail,
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight,
      devicePixelRatio: window.devicePixelRatio,
    },
    tabs,
    buttons,
    canvases,
    banners_and_status: banners,
  };
}
"""


def resolve_callouts(
    session: CDPPageSession, callouts: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
  resolved: List[Dict[str, Any]] = []
  for idx, c in enumerate(callouts, start=1):
    box: Optional[Dict[str, float]] = None
    selector = c.get("selector")
    if selector:
      info = session.find_element(selector, require_visible=True)
      if info.get("found"):
        box = {
            "x": float(info["x"]),
            "y": float(info["y"]),
            "width": float(info["width"]),
            "height": float(info["height"]),
        }
      elif not c.get("optional", False) and "x" not in c:
        raise RuntimeError(
            f"Callout #{c.get('step', idx)} selector '{selector}' did not match a visible element."
        )
    if not box and all(k in c for k in ("x", "y", "width", "height")):
      box = {
          "x": float(c["x"]),
          "y": float(c["y"]),
          "width": float(c["width"]),
          "height": float(c["height"]),
      }
    if box:
      resolved.append({
          "step": c.get("step", idx),
          "label": c.get("label", ""),
          "color": c.get("color", "blue"),
          "anchor": c.get("anchor", "top-left"),
          "padding": c.get("padding", 6),
          "x": box["x"],
          "y": box["y"],
          "width": box["width"],
          "height": box["height"],
      })
  return resolved


def ensure_persona_cdp_running(
    persona: str,
    port: int,
    env_data: Dict[str, Any],
    spawned_by_port: Dict[int, Dict[str, Any]],
    force_headed: bool = False,
) -> None:
  """If CDP port is not currently listening, auto-launch cached persona profile (headless if AUTHENTICATED)."""
  try:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1.2) as r:
      if r.status == 200:
        return
  except Exception:
    pass

  pinfo = (env_data.get("personas") or {}).get(persona) or {}
  email = str(pinfo.get("argolis_email") or "").strip().lower()
  if not email:
    raise RuntimeError(
        f"CDP port {port} is closed and no `argolis_email` found for persona '{persona}'."
    )

  cache_root = os.path.expanduser("~/.cache/gcp-console-demo-generator")
  reg_path = os.path.join(cache_root, "registry.json")
  profile_dir = ""
  last_state = ""
  if os.path.isfile(reg_path):
    try:
      reg = load_json_file(reg_path)
      reg_entry = (reg.get("profiles") or {}).get(email) or {}
      profile_dir = str(reg_entry.get("profile_dir") or "")
      last_state = str(reg_entry.get("last_state") or "")
    except Exception:
      profile_dir = ""

  if not profile_dir or not os.path.isdir(profile_dir):
    raise RuntimeError(
        f"AUTH_REQUIRED: CDP port {port} is closed and no cached profile found for '{email}'. "
        "Run `manage_persona_profiles.py ensure --env .runtime/demo_env.json --keep-alive` first."
    )

  # Remove stale SingletonLock if previous Chrome exited cleanly/abruptly
  for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
    lp = os.path.join(profile_dir, lock_name)
    if os.path.lexists(lp):
      try:
        os.unlink(lp)
      except OSError:
        pass

  use_headless = (last_state == "AUTHENTICATED") and not force_headed
  chrome_bin = find_chrome_binary()
  cmd = [chrome_bin]
  if use_headless:
    cmd.extend(["--headless=new", "--disable-gpu", "--disable-dev-shm-usage"])
  cmd.extend([
      f"--user-data-dir={profile_dir}",
      f"--remote-debugging-port={port}",
      "--remote-debugging-address=127.0.0.1",
      "--no-first-run",
      "--no-default-browser-check",
      "--window-size=1600,1040",
      "about:blank",
  ])
  proc = subprocess.Popen(
      cmd,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
      stdin=subprocess.DEVNULL,
  )
  spawned_by_port[port] = {
      "proc": proc,
      "headless": use_headless,
      "profile_dir": profile_dir,
      "email": email,
  }
  deadline = time.time() + 14.0
  while time.time() < deadline:
    try:
      with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1.0) as r:
        if r.status == 200:
          return
    except Exception:
      time.sleep(0.35)
  raise RuntimeError(
      f"Auto-launched Chrome for '{email}' on port {port}, but CDP did not respond within 14s."
  )


def resolve_persona_cdp_port(
    persona: str, env_data: Dict[str, Any], manifest: Dict[str, Any]
) -> int:
  for source in (manifest.get("personas") or {}, env_data.get("personas") or {}):
    if isinstance(source, dict) and persona in source:
      port = source[persona].get("cdp_port")
      if isinstance(port, int):
        return port
  raise RuntimeError(
      f"No `cdp_port` found for persona '{persona}'. Run "
      "`manage_persona_profiles.py ensure --env .runtime/demo_env.json` first."
  )


def open_scene_tab_and_navigate(
    port: int,
    scene: Dict[str, Any],
    persona: str,
    expected_email: str,
    vp_width: int,
    vp_height: int,
    vp_scale: float,
    env_data: Dict[str, Any],
    spawned_by_port: Dict[int, Dict[str, Any]],
    headless_local: bool,
) -> CDPPageSession:
  """Open isolated tab, navigate to scene URL, and auto-fallback from headless to headed if OS keyring blocks cookies."""
  session = CDPPageSession.create_tab(port)
  try:
    session.set_hidpi_viewport(vp_width, vp_height, vp_scale)
    if scene.get("url"):
      session.goto(str(scene["url"]), timeout_ms=int(scene.get("timeout_ms", 45000)))
    verify_not_auth_wall(
        session,
        persona=persona,
        allow_auth=bool(scene.get("allow_auth_screen")),
        expected_email=expected_email,
    )
    return session
  except RuntimeError as exc:
    spawn_info = spawned_by_port.get(port)
    if (
        not headless_local
        and "AUTH_REQUIRED" in str(exc)
        and spawn_info is not None
        and spawn_info.get("headless") is True
    ):
      print(
          f"  [Fallback] Headless Chrome on port {port} hit Google Sign-In; "
          "relaunching once in headed mode to access desktop cookie keyring...",
          file=sys.stderr,
      )
      session.close_tab()
      proc = spawn_info["proc"]
      proc.terminate()
      try:
        proc.wait(timeout=3)
      except Exception:
        proc.kill()
      del spawned_by_port[port]
      time.sleep(0.4)
      ensure_persona_cdp_running(
          persona, port, env_data, spawned_by_port, force_headed=True
      )
      retry_session = CDPPageSession.create_tab(port)
      try:
        retry_session.set_hidpi_viewport(vp_width, vp_height, vp_scale)
        if scene.get("url"):
          retry_session.goto(
              str(scene["url"]), timeout_ms=int(scene.get("timeout_ms", 45000))
          )
        verify_not_auth_wall(
            retry_session,
            persona=persona,
            allow_auth=bool(scene.get("allow_auth_screen")),
            expected_email=expected_email,
        )
        return retry_session
      except Exception:
        retry_session.close_tab()
        raise
    session.close_tab()
    raise


def run_capture(args: argparse.Namespace) -> int:
  manifest_path = os.path.abspath(args.manifest)
  manifest_dir = os.path.dirname(manifest_path)
  manifest = load_json_file(manifest_path)

  env_data: Dict[str, Any] = {}
  env_rel = manifest.get("env_file", "demo_env.json")
  env_candidate = (
      env_rel if os.path.isabs(env_rel) else os.path.join(manifest_dir, env_rel)
  )
  if args.env:
    env_candidate = os.path.abspath(args.env)
  if os.path.isfile(env_candidate):
    env_data = load_json_file(env_candidate)

  viewport = manifest.get("viewport") or {}
  vp_width = int(viewport.get("width", 1600))
  vp_height = int(viewport.get("height", 1000))
  vp_scale = float(viewport.get("device_scale_factor", 2))

  output_base = manifest.get("output_dir", "../screenshots")
  if not os.path.isabs(output_base):
    output_base = os.path.normpath(os.path.join(manifest_dir, output_base))

  inspect_id = getattr(args, "inspect_scene", None)
  scenes: List[Dict[str, Any]] = manifest.get("scenes") or []
  if inspect_id:
    scenes = [s for s in scenes if s.get("id") == inspect_id]
    if not scenes:
      raise RuntimeError(f"No scene matched --inspect-scene '{inspect_id}'")
  elif args.scene:
    wanted = set(args.scene)
    scenes = [s for s in scenes if s.get("id") in wanted]
    if not scenes:
      raise RuntimeError(f"No scenes matched --scene {args.scene}")

  if not inspect_id:
    os.makedirs(output_base, exist_ok=True)

  verified_ports: set = set()
  spawned_by_port: Dict[int, Dict[str, Any]] = {}
  headless_proc: Optional[subprocess.Popen] = None
  headless_tmp_dir: Optional[str] = None
  headless_port: Optional[int] = None
  captured_files: List[str] = []

  try:
    if args.headless_local:
      headless_tmp_dir = tempfile.mkdtemp(prefix="gcp_demo_headless_")
      headless_proc, headless_port = launch_ephemeral_headless_chrome(headless_tmp_dir)

    for idx, scene in enumerate(scenes, start=1):
      scene_id = scene.get("id", f"scene-{idx:02d}")
      persona = scene.get("persona", "default")
      out_name = scene.get("output_file", f"{scene_id}.png")
      out_path = (
          out_name
          if os.path.isabs(out_name)
          else os.path.join(output_base, out_name)
      )

      port = (
          int(headless_port)
          if args.headless_local and headless_port is not None
          else resolve_persona_cdp_port(persona, env_data, manifest)
      )
      if not args.headless_local and port not in verified_ports:
        ensure_persona_cdp_running(
            persona,
            port,
            env_data,
            spawned_by_port,
            force_headed=bool(getattr(args, "headed", False)),
        )
        verified_ports.add(port)

      expected_email = ""
      if not args.headless_local and isinstance(
          (env_data.get("personas") or {}).get(persona), dict
      ):
        expected_email = str(
            env_data["personas"][persona].get("argolis_email") or ""
        ).strip()

      if not inspect_id:
        print(f"[{idx}/{len(scenes)}] Navigating scene '{scene_id}' (persona='{persona}')...")

      session = open_scene_tab_and_navigate(
          port=port,
          scene=scene,
          persona=persona,
          expected_email=expected_email,
          vp_width=vp_width,
          vp_height=vp_height,
          vp_scale=vp_scale,
          env_data=env_data,
          spawned_by_port=spawned_by_port,
          headless_local=bool(args.headless_local),
      )
      try:
        if scene.get("wait_for_spinners", True) and not args.headless_local:
          wait_for_spinners_gone(session, timeout_ms=15000)
          verify_not_auth_wall(
              session,
              persona=persona,
              allow_auth=bool(scene.get("allow_auth_screen")),
              expected_email=expected_email,
          )

        if not (inspect_id and getattr(args, "no_actions", False)):
          execute_scene_actions(session, scene.get("actions") or [])

        verify_not_auth_wall(
            session,
            persona=persona,
            allow_auth=bool(scene.get("allow_auth_screen")),
            expected_email=expected_email,
        )
        if scene.get("settle_ms", 800):
          time.sleep(int(scene.get("settle_ms", 800)) / 1000.0)

        if inspect_id:
          diag_png = getattr(args, "inspect_out", None) or os.path.join(
              tempfile.gettempdir(), f"gcp_console_inspect_{scene_id}.png"
          )
          os.makedirs(os.path.dirname(os.path.abspath(diag_png)), exist_ok=True)
          diag = session.eval_js(INSPECT_SCENE_DOM_JS)
          session.capture_png(diag_png, clip=scene.get("clip"))
          report = {
              "scene_id": scene_id,
              "persona": persona,
              "expected_email": expected_email,
              "diagnostic_png": os.path.abspath(diag_png),
              **(diag if isinstance(diag, dict) else {}),
          }
          print(json.dumps(report, indent=2))
          return 0

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        # Blur Monaco/active inputs before DOM text replacement so cursor blink does not re-render text nodes
        session.eval_js(
            "() => { if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); }"
        )
        time.sleep(0.3)

        replacements = build_replacement_pairs(env_data, manifest, scene)
        resolved_callouts = resolve_callouts(session, scene.get("callouts") or [])

        persona_banner = scene.get("persona_banner")
        if persona_banner is None and isinstance(
            (env_data.get("personas") or {}).get(persona), dict
        ):
          pinfo = env_data["personas"][persona]
          if pinfo.get("banner_label"):
            persona_banner = {
                "label": pinfo["banner_label"],
                "color": pinfo.get("banner_color", "blue"),
            }

        try:
          session.eval_js(
              DOM_SANITIZE_AND_OVERLAY_JS,
              {
                  "replacements": replacements,
                  "resolved_callouts": resolved_callouts,
                  "persona_banner": persona_banner,
                  "extra_hide_selectors": scene.get("hide_selectors") or [],
                  "palette": COLOR_PALETTE,
              },
          )
          session.capture_png(out_path, clip=scene.get("clip"))
          captured_files.append(out_path)
          print(
              f"  -> Saved {out_path} (callouts={len(resolved_callouts)}, masks={len(replacements)})"
          )
        finally:
          try:
            session.eval_js(DOM_RESTORE_JS)
          except Exception:
            pass
      finally:
        session.close_tab()
  finally:
    for sinfo in spawned_by_port.values():
      pproc = sinfo["proc"]
      pproc.terminate()
      try:
        pproc.wait(timeout=3)
      except Exception:
        pproc.kill()
    if headless_proc is not None:
      headless_proc.terminate()
      try:
        headless_proc.wait(timeout=3)
      except Exception:
        headless_proc.kill()
    if headless_tmp_dir and os.path.isdir(headless_tmp_dir):
      shutil.rmtree(headless_tmp_dir, ignore_errors=True)

  print(f"\nCompleted {len(captured_files)} screenshot capture(s) successfully.")
  return 0


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
      description="Capture sanitized, callout-annotated 2x HiDPI GCP Console screenshots (zero-pip CDP)."
  )
  parser.add_argument(
      "--manifest",
      "-m",
      required=True,
      help="Path to declarative capture_manifest.json",
  )
  parser.add_argument(
      "--env",
      "-e",
      default=None,
      help="Optional path override for demo_env.json",
  )
  parser.add_argument(
      "--scene",
      "-s",
      action="append",
      default=None,
      help="Capture only specific scene ID(s) (repeatable)",
  )
  parser.add_argument(
      "--headed",
      action="store_true",
      help="Force visible GUI Chrome window when auto-launching cached AUTHENTICATED profiles (default: --headless=new)",
  )
  parser.add_argument(
      "--inspect-scene",
      default=None,
      help="Inspect live DOM state (signed-in email, tabs, buttons, canvases, banners) for a scene ID and emit JSON",
  )
  parser.add_argument(
      "--inspect-out",
      default=None,
      help="Optional raw PNG path for --inspect-scene (defaults to /tmp/gcp_console_inspect_<scene-id>.png)",
  )
  parser.add_argument(
      "--no-actions",
      action="store_true",
      help="With --inspect-scene, inspect page state immediately after navigation without executing scene actions",
  )
  parser.add_argument(
      "--headless-local",
      action="store_true",
      help="Launch local headless Chrome instead of connecting over CDP (for testing / local HTML)",
  )
  return parser


def main() -> int:
  parser = build_parser()
  args = parser.parse_args()
  try:
    return run_capture(args)
  except RuntimeError as exc:
    msg = str(exc)
    print(f"Error: {msg}", file=sys.stderr)
    return 2 if "AUTH_REQUIRED" in msg else 1


if __name__ == "__main__":
  sys.exit(main())
