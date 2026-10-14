#!/usr/bin/env python3
"""Google Cloud Reference Architecture SVG Compiler (`render_gcp_diagram.py`).

Compiles declarative JSON architecture specifications or Mermaid flowcharts into
publication-grade Google Cloud Reference Architecture SVGs featuring:
  - Nested colored zone containers (`#e3f2fd` Central blue, `#fff8e1` Producer/Consumer amber,
    `#fbe9e7` coral, `#e8f5e9` green, `#f3e5f5` purple, `#f5f5f5` neutral grey)
  - White 2-line GCP service cards (`512x512` official Google Cloud vector icons +
    bold capability title + muted GCP product subtitle + optional 3rd-line badge)
  - Orthogonal right-angle connectors with explicit polygon arrowheads, automatic port
    distribution, edge label pills, and numbered sequence callout badges (`1`, `2`, `3`...).

Zero external Python dependencies (uses Python Standard Library only).
"""

import argparse
import html
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Color Palettes & Theme Tokens (Matched to Google Cloud Reference SVGs)
# ---------------------------------------------------------------------------

ZONE_PALETTES = {
    "classic": {
        "blue": {"fill": "#e3f2fd", "stroke": "none", "stroke_width": 0, "dash": "", "label": "#616161", "rx": 2},
        "amber": {"fill": "#fff8e1", "stroke": "none", "stroke_width": 0, "dash": "", "label": "#616161", "rx": 2},
        "yellow": {"fill": "#fff8e1", "stroke": "none", "stroke_width": 0, "dash": "", "label": "#616161", "rx": 2},
        "coral": {"fill": "#fbe9e7", "stroke": "none", "stroke_width": 0, "dash": "", "label": "#616161", "rx": 2},
        "red": {"fill": "#fbe9e7", "stroke": "none", "stroke_width": 0, "dash": "", "label": "#616161", "rx": 2},
        "green": {"fill": "#e8f5e9", "stroke": "none", "stroke_width": 0, "dash": "", "label": "#616161", "rx": 2},
        "purple": {"fill": "#f3e5f5", "stroke": "none", "stroke_width": 0, "dash": "", "label": "#616161", "rx": 2},
        "grey": {"fill": "#f5f5f5", "stroke": "#e0e0e0", "stroke_width": 1, "dash": "", "label": "#616161", "rx": 2},
        "white": {"fill": "#ffffff", "stroke": "#dadce0", "stroke_width": 1, "dash": "", "label": "#616161", "rx": 2},
    },
    "modern": {
        "blue": {"fill": "#e8f0fe", "stroke": "#174ea6", "stroke_width": 1.5, "dash": "10,4", "label": "#174ea6", "rx": 8},
        "amber": {"fill": "#fef7e0", "stroke": "#b06000", "stroke_width": 1.5, "dash": "10,4", "label": "#b06000", "rx": 8},
        "yellow": {"fill": "#fef7e0", "stroke": "#b06000", "stroke_width": 1.5, "dash": "10,4", "label": "#b06000", "rx": 8},
        "coral": {"fill": "#fce8e6", "stroke": "#c5221f", "stroke_width": 1.5, "dash": "10,4", "label": "#c5221f", "rx": 8},
        "red": {"fill": "#fce8e6", "stroke": "#c5221f", "stroke_width": 1.5, "dash": "10,4", "label": "#c5221f", "rx": 8},
        "green": {"fill": "#e6f4ea", "stroke": "#0d652d", "stroke_width": 1.5, "dash": "10,4", "label": "#0d652d", "rx": 8},
        "purple": {"fill": "#f3e8fd", "stroke": "#681da8", "stroke_width": 1.5, "dash": "10,4", "label": "#681da8", "rx": 8},
        "grey": {"fill": "#f8f9fa", "stroke": "#5f6368", "stroke_width": 1.2, "dash": "8,4", "label": "#3c4043", "rx": 8},
        "white": {"fill": "#ffffff", "stroke": "#dadce0", "stroke_width": 1.2, "dash": "", "label": "#202124", "rx": 8},
    },
}


# ---------------------------------------------------------------------------
# Icon Resolution & Vector Embedding
# ---------------------------------------------------------------------------

class IconLibrary:
    """Loads normalized 512x512 Google Cloud vector SVG icons and resolves aliases."""

    def __init__(self, icons_dir: Optional[str] = None):
        if icons_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icons_dir = os.path.abspath(os.path.join(script_dir, "..", "resources", "icons"))
        self.icons_dir = icons_dir
        self.manifest_path = os.path.join(icons_dir, "icon_manifest.json")
        self.aliases: Dict[str, str] = {}
        self.available_icons: List[str] = []
        self._svg_cache: Dict[str, List[ET.Element]] = {}

        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.aliases = data.get("aliases", {})
                self.available_icons = data.get("icons", [])

    def resolve_icon_slug(self, raw_icon: Optional[str], title: str = "", subtitle: str = "") -> str:
        """Resolves an icon slug from an explicit key or infers it from card text."""
        exact_candidates = [c for c in (raw_icon, subtitle, title) if c]
        for cand in exact_candidates:
            norm = re.sub(r"[^a-zA-Z0-9]+", "_", cand.strip().lower()).strip("_")
            if not norm:
                continue
            if norm in self.available_icons:
                return norm
            if norm in self.aliases:
                return self.aliases[norm]

        # Substring matching: check explicit raw_icon first, then title, then subtitle
        substr_candidates = [c for c in (raw_icon, title, subtitle) if c]
        for cand in substr_candidates:
            norm = re.sub(r"[^a-zA-Z0-9]+", "_", cand.strip().lower()).strip("_")
            if not norm:
                continue
            for alias_key in sorted(self.aliases.keys(), key=len, reverse=True):
                if re.search(r"(^|_)" + re.escape(alias_key) + r"($|_)", norm):
                    return self.aliases[alias_key]
            for icon_key in sorted(self.available_icons, key=len, reverse=True):
                if re.search(r"(^|_)" + re.escape(icon_key) + r"($|_)", norm):
                    return icon_key

        return "data_analytics"

    def get_icon_children(self, slug: str) -> List[ET.Element]:
        """Returns the inner SVG child elements for a 512x512 icon."""
        if slug in self._svg_cache:
            return self._svg_cache[slug]

        svg_path = os.path.join(self.icons_dir, f"{slug}.svg")
        if not os.path.exists(svg_path):
            svg_path = os.path.join(self.icons_dir, "data_analytics.svg")
            if not os.path.exists(svg_path):
                return []

        root = ET.parse(svg_path).getroot()
        for el in root.iter():
            if "}" in el.tag:
                el.tag = el.tag.split("}", 1)[1]
        children = list(root)
        self._svg_cache[slug] = children
        return children


# ---------------------------------------------------------------------------
# Auto-Layout & Geometry Engine
# ---------------------------------------------------------------------------

CARD_DEFAULT_H = 42.0
CARD_BADGE_H = 52.0
CARD_MIN_W = 118.0
CARD_MAX_W = 290.0
CARD_GAP_X = 28.0
CARD_GAP_Y = 30.0

ZONE_PAD_TOP = 30.0
ZONE_PAD_BOTTOM = 16.0
ZONE_PAD_X = 16.0
ZONE_GAP_X = 26.0
ZONE_GAP_Y = 36.0


def estimate_text_width(text: str, font_size: float) -> float:
    """Estimates rendered pixel width of a string in Roboto/Arial."""
    if not text:
        return 0.0
    width = 0.0
    for ch in text:
        if ch in "iIl1|!.,:;':":
            width += font_size * 0.30
        elif ch in "MW@#%&":
            width += font_size * 0.82
        elif ch.isupper():
            width += font_size * 0.64
        else:
            width += font_size * 0.53
    return width


def truncate_text_to_width(text: str, font_size: float, max_width: float) -> str:
    """Truncates text cleanly with an ellipsis if its estimated pixel width exceeds max_width."""
    if not text or estimate_text_width(text, font_size) <= max_width:
        return text
    ellipsis = "…"
    ell_w = estimate_text_width(ellipsis, font_size)
    target_w = max(10.0, max_width - ell_w)
    out = []
    curr_w = 0.0
    for ch in text:
        ch_w = estimate_text_width(ch, font_size)
        if curr_w + ch_w > target_w:
            break
        out.append(ch)
        curr_w += ch_w
    return "".join(out).rstrip(" ,;:-·") + ellipsis


def compute_card_size(card: Dict[str, Any]) -> Tuple[float, float]:
    """Calculates `(width, height)` for a white GCP service card."""
    if "w" in card and "h" in card:
        return float(card["w"]), float(card["h"])

    title = str(card.get("title", ""))
    subtitle = str(card.get("subtitle", ""))
    badge = str(card.get("badge", ""))

    w_title = estimate_text_width(title, 10.5)
    w_sub = estimate_text_width(subtitle, 9.2)
    w_badge = estimate_text_width(badge, 8.5) + 12.0 if badge else 0.0

    text_w = max(w_title, w_sub, w_badge)
    # 8px left pad + 26px icon + 8px gap + text_w + 14px right pad = text_w + 56
    calc_w = max(CARD_MIN_W, min(CARD_MAX_W, math.ceil(text_w + 56.0)))
    if "w" in card:
        calc_w = float(card["w"])

    calc_h = CARD_BADGE_H if badge else CARD_DEFAULT_H
    if "h" in card:
        calc_h = float(card["h"])

    return calc_w, calc_h


class LayoutEngine:
    """Computes bottom-up sizes and top-down coordinates for zones, subzones, and cards."""

    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec
        self.card_boxes: Dict[str, Dict[str, float]] = {}
        self.zone_boxes: Dict[str, Dict[str, float]] = {}

    def measure_zone(self, zone: Dict[str, Any], depth: int = 0) -> Tuple[float, float]:
        """Recursively measures `(width, height)` required by a zone."""
        subzones = zone.get("subzones") or zone.get("zones") or []
        cards = zone.get("cards") or zone.get("nodes") or []
        layout = zone.get("layout", "horizontal" if depth > 0 else "horizontal").lower()
        cols = int(zone.get("columns", 0))

        # Measure child subzones first
        sub_sizes: List[Tuple[Dict[str, Any], float, float]] = []
        for sz in subzones:
            sw, sh = self.measure_zone(sz, depth + 1)
            sub_sizes.append((sz, sw, sh))

        # Measure direct cards
        card_sizes: List[Tuple[Dict[str, Any], float, float]] = []
        for c in cards:
            cw, ch = compute_card_size(c)
            c["_w"], c["_h"] = cw, ch
            card_sizes.append((c, cw, ch))

        content_w = 0.0
        content_h = 0.0

        # Arrange subzones if present
        if sub_sizes:
            sz_grid = self._arrange_items(
                [(item, w, h) for item, w, h in sub_sizes],
                layout=layout,
                cols=cols,
                gap_x=ZONE_GAP_X,
                gap_y=ZONE_GAP_Y,
            )
            zone["_subzone_grid"] = sz_grid
            content_w = max(content_w, sz_grid["total_w"])
            content_h += sz_grid["total_h"]

        # Arrange cards if present
        if card_sizes:
            card_layout = zone.get("card_layout", layout).lower()
            card_cols = int(zone.get("card_columns", cols))
            c_grid = self._arrange_items(
                [(item, w, h) for item, w, h in card_sizes],
                layout=card_layout,
                cols=card_cols,
                gap_x=CARD_GAP_X,
                gap_y=CARD_GAP_Y,
            )
            zone["_card_grid"] = c_grid
            content_w = max(content_w, c_grid["total_w"])
            if sub_sizes:
                content_h += ZONE_GAP_Y
            content_h += c_grid["total_h"]

        label = zone.get("label", zone.get("title", ""))
        is_transparent = bool(zone.get("transparent", False)) or (not label and zone.get("stroke") == "none" and zone.get("color") in ("white", "none", None))
        pad_x = 0.0 if is_transparent else ZONE_PAD_X
        pad_top = 0.0 if is_transparent else (ZONE_PAD_TOP if label else 16.0)
        pad_bottom = 0.0 if is_transparent else ZONE_PAD_BOTTOM
        zone["_pad_x"], zone["_pad_top"], zone["_pad_bottom"] = pad_x, pad_top, pad_bottom
        zone["_transparent"] = is_transparent

        label_w = (estimate_text_width(label, 11.5) + 28.0) if label else 0.0
        total_w = max(content_w + 2 * pad_x, label_w, float(zone.get("min_w", 0.0 if is_transparent else 140.0)))
        total_h = max(content_h + pad_top + pad_bottom, float(zone.get("min_h", 0.0 if is_transparent else 76.0)))

        if "w" in zone:
            total_w = float(zone["w"])
        if "h" in zone:
            total_h = float(zone["h"])

        zone["_w"] = total_w
        zone["_h"] = total_h
        return total_w, total_h

    def _arrange_items(
        self,
        items: List[Tuple[Dict[str, Any], float, float]],
        layout: str,
        cols: int,
        gap_x: float,
        gap_y: float,
    ) -> Dict[str, Any]:
        """Places items into rows/columns and returns relative offsets and total dimensions."""
        n = len(items)
        if n == 0:
            return {"rows": [], "total_w": 0.0, "total_h": 0.0}

        has_explicit_rc = any("row" in it[0] or "col" in it[0] for it in items)
        rows_map: Dict[int, List[Tuple[int, Dict[str, Any], float, float]]] = {}

        if has_explicit_rc:
            for idx, (it, w, h) in enumerate(items):
                r = int(it.get("row", 0))
                c = int(it.get("col", idx))
                rows_map.setdefault(r, []).append((c, it, w, h))
            ordered_rows = []
            for r in sorted(rows_map.keys()):
                row_items = [
                    (it, w, h)
                    for _, it, w, h in sorted(rows_map[r], key=lambda x: x[0])
                ]
                ordered_rows.append(row_items)
        else:
            if cols > 0:
                per_row = cols
            elif layout == "vertical":
                per_row = 1
            else:
                per_row = n
            ordered_rows = []
            for i in range(0, n, per_row):
                ordered_rows.append(items[i : i + per_row])

        max_cols = max(len(r) for r in ordered_rows)
        col_widths = [0.0] * max_cols
        for r in ordered_rows:
            for c_idx, (_, w, _) in enumerate(r):
                col_widths[c_idx] = max(col_widths[c_idx], w)

        row_heights = [max(h for _, _, h in r) for r in ordered_rows]

        placed_rows = []
        curr_y = 0.0
        max_row_w = 0.0
        for r_idx, r in enumerate(ordered_rows):
            curr_x = 0.0
            rh = row_heights[r_idx]
            placed_items = []
            for c_idx, (it, w, h) in enumerate(r):
                slot_w = col_widths[c_idx] if len(ordered_rows) > 1 and len(r) == max_cols else w
                placed_items.append((it, curr_x, curr_y, slot_w, w, h, rh))
                curr_x += slot_w + gap_x
            row_w = curr_x - gap_x if r else 0.0
            max_row_w = max(max_row_w, row_w)
            placed_rows.append((placed_items, row_w, rh))
            curr_y += rh + gap_y

        total_h = curr_y - gap_y if ordered_rows else 0.0
        return {
            "rows": placed_rows,
            "total_w": max_row_w,
            "total_h": total_h,
        }

    def position_zone(self, zone: Dict[str, Any], x: float, y: float, w: float, h: float) -> None:
        """Assigns absolute `(x, y, w, h)` to a zone and recursively positions its children."""
        zx = float(zone.get("x", x))
        zy = float(zone.get("y", y))
        zw = float(zone.get("w", max(w, zone.get("_w", w))))
        zh = float(zone.get("h", max(h, zone.get("_h", h))))

        zone["_x"], zone["_y"], zone["_w"], zone["_h"] = zx, zy, zw, zh
        zid = zone.get("id")
        if zid:
            self.zone_boxes[zid] = {"x": zx, "y": zy, "w": zw, "h": zh}

        pad_x = zone.get("_pad_x", ZONE_PAD_X)
        pad_top = zone.get("_pad_top", ZONE_PAD_TOP)
        inner_x = zx + pad_x
        inner_y = zy + pad_top
        avail_w = zw - 2 * pad_x

        # Position subzones
        if "_subzone_grid" in zone:
            sz_grid = zone["_subzone_grid"]
            for placed_items, row_w, rh in sz_grid["rows"]:
                stretch = zone.get("stretch_subzones", True)
                row_extra = max(0.0, avail_w - row_w) if stretch and len(placed_items) > 0 else 0.0
                per_item_extra = row_extra / len(placed_items) if placed_items else 0.0
                shift_x = 0.0
                for sz, ox, oy, slot_w, item_w, item_h, row_h in placed_items:
                    final_w = slot_w + per_item_extra
                    final_h = row_h if zone.get("align_subzone_heights", True) else item_h
                    self.position_zone(sz, inner_x + ox + shift_x, inner_y + oy, final_w, final_h)
                    shift_x += per_item_extra
            inner_y += sz_grid["total_h"] + ZONE_GAP_Y

        # Position cards
        if "_card_grid" in zone:
            c_grid = zone["_card_grid"]
            stretch_cards = zone.get("stretch_cards", True)
            for placed_items, row_w, rh in c_grid["rows"]:
                row_extra = max(0.0, avail_w - row_w) if stretch_cards and len(placed_items) > 0 else 0.0
                # Cap extra width per card so single cards don't stretch absurdly wide
                per_card_extra = min(36.0, row_extra / len(placed_items)) if placed_items else 0.0
                total_used_w = row_w + per_card_extra * len(placed_items)
                offset_x = max(0.0, (avail_w - total_used_w) / 2.0) if zone.get("center_cards", False) else 0.0
                shift_x = 0.0
                for card, ox, oy, slot_w, cw, ch, row_h in placed_items:
                    final_cw = float(card.get("w", slot_w + per_card_extra))
                    final_ch = float(card.get("h", ch))
                    cx = float(card.get("x", inner_x + offset_x + ox + shift_x))
                    cy = float(card.get("y", inner_y + oy))
                    card["_x"], card["_y"], card["_w"], card["_h"] = cx, cy, final_cw, final_ch
                    cid = card.get("id")
                    if cid:
                        self.card_boxes[cid] = {"x": cx, "y": cy, "w": final_cw, "h": final_ch}
                    shift_x += per_card_extra

    def run(self) -> Tuple[float, float]:
        """Executes full layout calculation and returns `(canvas_width, canvas_height)`."""
        margin_x = float(self.spec.get("margin_x", 28.0))
        title = self.spec.get("title", "")
        subtitle = self.spec.get("subtitle", "")
        header_h = 0.0
        if title:
            header_h += 32.0
        if subtitle:
            header_h += 18.0
        margin_top = float(self.spec.get("margin_top", 16.0 + header_h))
        margin_bottom = float(self.spec.get("margin_bottom", 20.0))

        zones = self.spec.get("zones", [])
        standalone_cards = self.spec.get("cards", self.spec.get("nodes", []))
        top_layout = self.spec.get("layout", "vertical").lower()
        top_cols = int(self.spec.get("columns", 0))

        zone_items = []
        for z in zones:
            zw, zh = self.measure_zone(z, depth=0)
            zone_items.append((z, zw, zh))

        top_gap_x = ZONE_GAP_X
        if top_layout == "horizontal":
            edge_labels = [str(e.get("label", "")) for e in self.spec.get("edges", []) if e.get("label")]
            if edge_labels:
                max_lbl_w = max(estimate_text_width(lbl, 8.8) + 28.0 for lbl in edge_labels)
                top_gap_x = max(ZONE_GAP_X, min(145.0, max_lbl_w + 18.0))

        top_grid = self._arrange_items(
            zone_items,
            layout=top_layout,
            cols=top_cols,
            gap_x=top_gap_x,
            gap_y=ZONE_GAP_Y,
        )

        max_total_w = top_grid["total_w"]
        for placed_items, row_w, rh in top_grid["rows"]:
            stretch = self.spec.get("stretch_zones", True)
            row_extra = max(0.0, max_total_w - row_w) if stretch and len(placed_items) > 0 else 0.0
            per_item_extra = row_extra / len(placed_items) if placed_items else 0.0
            shift_x = 0.0
            for z, ox, oy, slot_w, zw, zh, row_h in placed_items:
                final_w = slot_w + per_item_extra
                final_h = row_h if self.spec.get("align_zone_heights", True) else zh
                self.position_zone(z, margin_x + ox + shift_x, margin_top + oy, final_w, final_h)
                shift_x += per_item_extra

        curr_card_y = margin_top + top_grid["total_h"] + (ZONE_GAP_Y if zone_items else 0.0)
        curr_card_x = margin_x
        for c in standalone_cards:
            cw, ch = compute_card_size(c)
            cx = float(c.get("x", curr_card_x))
            cy = float(c.get("y", curr_card_y))
            c["_x"], c["_y"], c["_w"], c["_h"] = cx, cy, cw, ch
            cid = c.get("id")
            if cid:
                self.card_boxes[cid] = {"x": cx, "y": cy, "w": cw, "h": ch}
            curr_card_x += cw + CARD_GAP_X

        all_boxes = list(self.zone_boxes.values()) + list(self.card_boxes.values())
        for z in zones:
            all_boxes.append({"x": z["_x"], "y": z["_y"], "w": z["_w"], "h": z["_h"]})

        if all_boxes:
            max_x = max(b["x"] + b["w"] for b in all_boxes)
            max_y = max(b["y"] + b["h"] for b in all_boxes)
        else:
            max_x, max_y = 960.0 - margin_x, 540.0 - margin_bottom

        canvas_w = float(self.spec.get("width", max(math.ceil(max_x + margin_x), 640)))
        canvas_h = float(self.spec.get("height", max(math.ceil(max_y + margin_bottom), 320)))
        return canvas_w, canvas_h


# ---------------------------------------------------------------------------
# Orthogonal Connector Router & Port Distributor
# ---------------------------------------------------------------------------

def choose_sides(
    src: Dict[str, float],
    dst: Dict[str, float],
    from_side: Optional[str] = None,
    to_side: Optional[str] = None,
) -> Tuple[str, str]:
    """Determines optimal (`from_side`, `to_side`) for two bounding boxes."""
    if from_side and from_side != "auto" and to_side and to_side != "auto":
        return from_side, to_side

    sx_c = src["x"] + src["w"] / 2.0
    sy_c = src["y"] + src["h"] / 2.0
    dx_c = dst["x"] + dst["w"] / 2.0
    dy_c = dst["y"] + dst["h"] / 2.0

    dx = dx_c - sx_c
    dy = dy_c - sy_c

    horiz_gap = max(dst["x"] - (src["x"] + src["w"]), src["x"] - (dst["x"] + dst["w"]))
    vert_gap = max(dst["y"] - (src["y"] + src["h"]), src["y"] - (dst["y"] + dst["h"]))

    if horiz_gap >= vert_gap and horiz_gap > -10:
        f_side = "right" if dx >= 0 else "left"
        t_side = "left" if dx >= 0 else "right"
    else:
        f_side = "bottom" if dy >= 0 else "top"
        t_side = "top" if dy >= 0 else "bottom"

    if from_side and from_side != "auto":
        f_side = from_side
    if to_side and to_side != "auto":
        t_side = to_side
    return f_side, t_side


def get_port_point(box: Dict[str, float], side: str, slot_idx: int = 0, slot_count: int = 1) -> Tuple[float, float]:
    """Computes exact `(x, y)` port coordinates on `side` of `box`, distributed across slots."""
    frac = 0.5
    if slot_count > 1:
        frac = 0.25 + 0.50 * (slot_idx / (slot_count - 1))

    if side == "right":
        return box["x"] + box["w"], box["y"] + box["h"] * frac
    if side == "left":
        return box["x"], box["y"] + box["h"] * frac
    if side == "bottom":
        return box["x"] + box["w"] * frac, box["y"] + box["h"]
    if side == "top":
        return box["x"] + box["w"] * frac, box["y"]
    return box["x"] + box["w"] / 2.0, box["y"] + box["h"] / 2.0


def compute_orthogonal_waypoints(
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    from_side: str,
    to_side: str,
    route_offset: float = 0.0,
) -> List[Tuple[float, float]]:
    """Computes clean orthogonal right-angle waypoints between `p1` and `p2`."""
    x1, y1 = p1
    x2, y2 = p2
    stub = 14.0

    if (from_side == "right" and to_side == "left") or (from_side == "left" and to_side == "right"):
        if abs(y1 - y2) < 1.5 and ((from_side == "right" and x2 > x1) or (from_side == "left" and x2 < x1)):
            return [(x1, y1), (x2, y2)]
        mid_x = (x1 + x2) / 2.0 + route_offset
        return [(x1, y1), (mid_x, y1), (mid_x, y2), (x2, y2)]

    if (from_side == "bottom" and to_side == "top") or (from_side == "top" and to_side == "bottom"):
        if abs(x1 - x2) < 1.5 and ((from_side == "bottom" and y2 > y1) or (from_side == "top" and y2 < y1)):
            return [(x1, y1), (x2, y2)]
        # Account for asymmetric top (header) vs bottom padding of nested zones
        bias_y = -11.0 if abs(y2 - y1) > 75.0 else 0.0
        mid_y = (y1 + y2) / 2.0 + bias_y + route_offset
        return [(x1, y1), (x1, mid_y), (x2, mid_y), (x2, y2)]

    if from_side in ("right", "left") and to_side in ("top", "bottom"):
        return [(x1, y1), (x2, y1), (x2, y2)]
    if from_side in ("top", "bottom") and to_side in ("right", "left"):
        return [(x1, y1), (x1, y2), (x2, y2)]

    if from_side == "right" and to_side == "right":
        outer_x = max(x1, x2) + stub + abs(route_offset)
        return [(x1, y1), (outer_x, y1), (outer_x, y2), (x2, y2)]
    if from_side == "left" and to_side == "left":
        outer_x = min(x1, x2) - stub - abs(route_offset)
        return [(x1, y1), (outer_x, y1), (outer_x, y2), (x2, y2)]
    if from_side == "bottom" and to_side == "bottom":
        outer_y = max(y1, y2) + stub + abs(route_offset)
        return [(x1, y1), (x1, outer_y), (x2, outer_y), (x2, y2)]
    if from_side == "top" and to_side == "top":
        outer_y = min(y1, y2) - stub - abs(route_offset)
        return [(x1, y1), (x1, outer_y), (x2, outer_y), (x2, y2)]

    mid_x = (x1 + x2) / 2.0
    return [(x1, y1), (mid_x, y1), (mid_x, y2), (x2, y2)]


# ---------------------------------------------------------------------------
# SVG Renderer
# ---------------------------------------------------------------------------

class GCPDiagramRenderer:
    """Renders a laid-out architecture specification to a pure-vector SVG document."""

    def __init__(self, spec: Dict[str, Any], icon_lib: IconLibrary):
        self.spec = spec
        self.icon_lib = icon_lib
        self.theme_name = spec.get("theme", "classic").lower()
        if self.theme_name not in ZONE_PALETTES:
            self.theme_name = "classic"
        self.palette = ZONE_PALETTES[self.theme_name]

    def render(self) -> str:
        engine = LayoutEngine(self.spec)
        canvas_w, canvas_h = engine.run()

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        svg = ET.Element(
            "svg",
            {
                "xmlns": "http://www.w3.org/2000/svg",
                "version": "1.1",
                "viewBox": f"0 0 {canvas_w:.1f} {canvas_h:.1f}",
                "width": f"{int(canvas_w)}",
                "height": f"{int(canvas_h)}",
                "font-family": "Roboto, Arial, Helvetica, sans-serif",
            },
        )

        bg_color = self.spec.get("background", "#ffffff")
        ET.SubElement(
            svg,
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": f"{canvas_w:.1f}",
                "height": f"{canvas_h:.1f}",
                "fill": bg_color,
            },
        )

        title = self.spec.get("title", "")
        subtitle = self.spec.get("subtitle", "")
        margin_x = float(self.spec.get("margin_x", 28.0))
        curr_title_y = 26.0
        if title:
            t_el = ET.SubElement(
                svg,
                "text",
                {
                    "x": f"{margin_x:.1f}",
                    "y": f"{curr_title_y:.1f}",
                    "fill": "#202124",
                    "font-size": "15",
                    "font-weight": "700",
                },
            )
            t_el.text = str(title)
            curr_title_y += 18.0
        if subtitle:
            st_el = ET.SubElement(
                svg,
                "text",
                {
                    "x": f"{margin_x:.1f}",
                    "y": f"{curr_title_y:.1f}",
                    "fill": "#5f6368",
                    "font-size": "11",
                    "font-weight": "400",
                },
            )
            st_el.text = str(subtitle)

        zones_group = ET.SubElement(svg, "g", {"id": "zones"})
        cards_group = ET.SubElement(svg, "g", {"id": "cards"})

        for z in self.spec.get("zones", []):
            self._render_zone(z, zones_group, cards_group, depth=0)

        for c in self.spec.get("cards", self.spec.get("nodes", [])):
            self._render_card(c, cards_group)

        edges_group = ET.SubElement(svg, "g", {"id": "edges"})
        all_boxes = {}
        all_boxes.update(engine.zone_boxes)
        all_boxes.update(engine.card_boxes)
        self._render_edges(self.spec.get("edges", self.spec.get("flows", [])), all_boxes, edges_group)

        raw_xml = ET.tostring(svg, encoding="unicode")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + raw_xml

    def _render_zone(self, zone: Dict[str, Any], zones_group: ET.Element, cards_group: ET.Element, depth: int) -> None:
        zx, zy, zw, zh = zone["_x"], zone["_y"], zone["_w"], zone["_h"]
        if not zone.get("_transparent", False):
            default_color = "blue" if depth == 0 else "amber"
            color_key = str(zone.get("color", default_color)).lower()
            style = self.palette.get(color_key, self.palette[default_color])

            fill_color = zone.get("fill", style["fill"])
            stroke_color = zone.get("stroke", style["stroke"])
            stroke_w = zone.get("stroke_width", style["stroke_width"])
            dash = zone.get("dash", style["dash"])
            rx = zone.get("rx", style["rx"])

            sw = float(stroke_w) if stroke_color and stroke_color != "none" else 0.0
            if sw > 0 and not dash:
                ET.SubElement(
                    zones_group,
                    "rect",
                    {
                        "x": f"{zx - sw:.2f}",
                        "y": f"{zy - sw:.2f}",
                        "width": f"{zw + 2 * sw:.2f}",
                        "height": f"{zh + 2 * sw:.2f}",
                        "fill": str(stroke_color),
                        "rx": f"{float(rx) + sw:.1f}",
                        "ry": f"{float(rx) + sw:.1f}",
                    },
                )

            rect_attrib = {
                "x": f"{zx:.2f}",
                "y": f"{zy:.2f}",
                "width": f"{zw:.2f}",
                "height": f"{zh:.2f}",
                "fill": fill_color,
                "rx": f"{rx}",
                "ry": f"{rx}",
            }
            ET.SubElement(zones_group, "rect", rect_attrib)

            if sw > 0 and dash:
                border_pts = [
                    (zx, zy),
                    (zx + zw, zy),
                    (zx + zw, zy + zh),
                    (zx, zy + zh),
                    (zx, zy),
                ]
                self._draw_orthogonal_segments(zones_group, border_pts, str(stroke_color), sw, "dashed")

            label = zone.get("label", zone.get("title", ""))
            if label:
                lbl_color = zone.get("label_color", style["label"])
                lbl_el = ET.SubElement(
                    zones_group,
                    "text",
                    {
                        "x": f"{zx + 12.0:.2f}",
                        "y": f"{zy + 19.0:.2f}",
                        "fill": lbl_color,
                        "font-size": "11",
                        "font-weight": "600",
                    },
                )
                lbl_el.text = str(label)

        for sz in zone.get("subzones") or zone.get("zones") or []:
            self._render_zone(sz, zones_group, cards_group, depth + (0 if zone.get("_transparent") else 1))

        for c in zone.get("cards") or zone.get("nodes") or []:
            self._render_card(c, cards_group)

    def _render_card(self, card: Dict[str, Any], cards_group: ET.Element) -> None:
        cx, cy, cw, ch = card["_x"], card["_y"], card["_w"], card["_h"]
        card_g = ET.SubElement(cards_group, "g")

        # Subtle drop shadow rectangle for crisp visual elevation
        ET.SubElement(
            card_g,
            "rect",
            {
                "x": f"{cx + 1.0:.2f}",
                "y": f"{cy + 1.5:.2f}",
                "width": f"{cw:.2f}",
                "height": f"{ch:.2f}",
                "fill": "#000000",
                "fill-opacity": "0.06",
                "rx": "2.5",
                "ry": "2.5",
            },
        )

        # Crisp border backing rectangle (universal across MSVG, oksvg, and browsers)
        border_color = str(card.get("stroke", "#c4c7c5"))
        ET.SubElement(
            card_g,
            "rect",
            {
                "x": f"{cx - 0.7:.2f}",
                "y": f"{cy - 0.7:.2f}",
                "width": f"{cw + 1.4:.2f}",
                "height": f"{ch + 1.4:.2f}",
                "fill": border_color,
                "rx": "3.0",
                "ry": "3.0",
            },
        )

        # White card body matching data-mesh-architecture.svg
        ET.SubElement(
            card_g,
            "rect",
            {
                "x": f"{cx:.2f}",
                "y": f"{cy:.2f}",
                "width": f"{cw:.2f}",
                "height": f"{ch:.2f}",
                "fill": card.get("fill", "#ffffff"),
                "rx": "2.5",
                "ry": "2.5",
            },
        )

        title = str(card.get("title", ""))
        subtitle = str(card.get("subtitle", ""))
        badge = str(card.get("badge", ""))

        # Resolve and embed 512x512 vector icon scaled to 26x26
        icon_slug = self.icon_lib.resolve_icon_slug(card.get("icon"), title=title, subtitle=subtitle)
        icon_children = self.icon_lib.get_icon_children(icon_slug)
        icon_size = 26.0
        icon_x = cx + 8.0
        icon_y = cy + (ch - icon_size) / 2.0
        scale = icon_size / 512.0

        icon_g = ET.SubElement(
            card_g,
            "g",
            {"transform": f"translate({icon_x:.2f},{icon_y:.2f}) scale({scale:.5f})"},
        )
        for child in icon_children:
            icon_g.append(child)

        # Text lines on the right of the icon
        text_x = cx + 40.0
        if subtitle and badge:
            title_y = cy + 15.0
            sub_y = cy + 28.0
            badge_y = cy + 41.0
        elif subtitle:
            title_y = cy + (ch / 2.0) - 3.0
            sub_y = cy + (ch / 2.0) + 10.5
            badge_y = 0.0
        else:
            title_y = cy + (ch / 2.0) + 3.5
            sub_y = 0.0
            badge_y = 0.0

        max_text_w = max(60.0, cw - 48.0)

        if title:
            t_el = ET.SubElement(
                card_g,
                "text",
                {
                    "x": f"{text_x:.2f}",
                    "y": f"{title_y:.2f}",
                    "fill": "#212121",
                    "font-size": "10.2",
                    "font-weight": "600",
                },
            )
            t_el.text = truncate_text_to_width(title, 10.2, max_text_w)

        if subtitle:
            s_el = ET.SubElement(
                card_g,
                "text",
                {
                    "x": f"{text_x:.2f}",
                    "y": f"{sub_y:.2f}",
                    "fill": "#757575",
                    "font-size": "9.0",
                    "font-weight": "400",
                },
            )
            s_el.text = truncate_text_to_width(subtitle, 9.0, max_text_w)

        if badge:
            b_el = ET.SubElement(
                card_g,
                "text",
                {
                    "x": f"{text_x:.2f}",
                    "y": f"{badge_y:.2f}",
                    "fill": "#1a73e8",
                    "font-size": "8.2",
                    "font-weight": "500",
                },
            )
            b_el.text = truncate_text_to_width(badge, 8.2, max_text_w)

    def _render_edges(
        self,
        edges: List[Dict[str, Any]],
        boxes: Dict[str, Dict[str, float]],
        edges_group: ET.Element,
    ) -> None:
        # First pass: determine sides for all valid edges and group ports per (node_id, side)
        resolved_edges = []
        port_usage: Dict[Tuple[str, str], List[Tuple[int, str, float]]] = {}

        for idx, e in enumerate(edges):
            u = e.get("from", e.get("source"))
            v = e.get("to", e.get("target"))
            if u not in boxes or v not in boxes:
                continue
            src_box = boxes[u]
            dst_box = boxes[v]
            f_side, t_side = choose_sides(
                src_box,
                dst_box,
                e.get("from_side"),
                e.get("to_side"),
            )
            resolved_edges.append((idx, e, u, v, f_side, t_side))

            # Sort key for port ordering: target's orthogonal coordinate so lines don't cross
            dst_coord = dst_box["y"] if f_side in ("left", "right") else dst_box["x"]
            src_coord = src_box["y"] if t_side in ("left", "right") else src_box["x"]
            port_usage.setdefault((u, f_side), []).append((idx, "out", dst_coord))
            port_usage.setdefault((v, t_side), []).append((idx, "in", src_coord))

        port_slots: Dict[Tuple[int, str], Tuple[int, int]] = {}
        for key, usage_list in port_usage.items():
            sorted_usage = sorted(usage_list, key=lambda item: item[2])
            total = len(sorted_usage)
            for slot_i, (edge_idx, direction, _) in enumerate(sorted_usage):
                port_slots[(edge_idx, direction)] = (slot_i, total)

        # Group vertical-to-vertical and horizontal-to-horizontal edges sharing the same mid-channel
        # so parallel segments are staggered automatically when "offset" is not explicitly set
        horiz_corridors: List[Tuple[float, List[int]]] = []
        vert_corridors: List[Tuple[float, List[int]]] = []
        edge_endpoints: Dict[int, Tuple[Tuple[float, float], Tuple[float, float]]] = {}

        for idx, e, u, v, f_side, t_side in resolved_edges:
            src_box = boxes[u]
            dst_box = boxes[v]
            out_slot, out_total = port_slots.get((idx, "out"), (0, 1))
            in_slot, in_total = port_slots.get((idx, "in"), (0, 1))
            p1 = get_port_point(src_box, f_side, out_slot, out_total)
            p2 = get_port_point(dst_box, t_side, in_slot, in_total)
            edge_endpoints[idx] = (p1, p2)

            if "offset" in e:
                continue
            if (f_side in ("top", "bottom") and t_side in ("top", "bottom")) and abs(p1[0] - p2[0]) >= 1.5:
                base_mid_y = (p1[1] + p2[1]) / 2.0
                matched = False
                for c_y, group_list in horiz_corridors:
                    if abs(c_y - base_mid_y) < 18.0:
                        group_list.append(idx)
                        matched = True
                        break
                if not matched:
                    horiz_corridors.append((base_mid_y, [idx]))
            elif (f_side in ("left", "right") and t_side in ("left", "right")) and abs(p1[1] - p2[1]) >= 1.5:
                base_mid_x = (p1[0] + p2[0]) / 2.0
                matched = False
                for c_x, group_list in vert_corridors:
                    if abs(c_x - base_mid_x) < 18.0:
                        group_list.append(idx)
                        matched = True
                        break
                if not matched:
                    vert_corridors.append((base_mid_x, [idx]))

        auto_offsets: Dict[int, float] = {}
        for _, group_list in horiz_corridors:
            if len(group_list) > 1:
                spacing = 11.0
                for g_i, edge_idx in enumerate(group_list):
                    auto_offsets[edge_idx] = (g_i - (len(group_list) - 1) / 2.0) * spacing
        for _, group_list in vert_corridors:
            if len(group_list) > 1:
                spacing = 11.0
                for g_i, edge_idx in enumerate(group_list):
                    auto_offsets[edge_idx] = (g_i - (len(group_list) - 1) / 2.0) * spacing

        # Second pass: draw orthogonal segments, explicit arrowheads, and collect labels/badges
        labels_and_badges: List[Tuple[Dict[str, Any], List[Tuple[float, float]], str]] = []

        for idx, e, u, v, f_side, t_side in resolved_edges:
            p1, p2 = edge_endpoints[idx]
            offset = float(e.get("offset", auto_offsets.get(idx, 0.0)))
            pts = compute_orthogonal_waypoints(p1, p2, f_side, t_side, route_offset=offset)

            color = str(e.get("color", "#3a7df0"))
            thickness = float(e.get("stroke_width", 1.4))
            style = str(e.get("style", "solid")).lower()

            # Shorten final segment slightly so the line ends cleanly inside the arrowhead base
            arrow_len = 6.5
            arrow_half_w = 3.3
            draw_pts = list(pts)
            if len(draw_pts) >= 2:
                x_prev, y_prev = draw_pts[-2]
                x_end, y_end = draw_pts[-1]
                seg_len = math.hypot(x_end - x_prev, y_end - y_prev)
                if seg_len > arrow_len:
                    ux = (x_end - x_prev) / seg_len
                    uy = (y_end - y_prev) / seg_len
                    draw_pts[-1] = (x_end - ux * (arrow_len - 1.2), y_end - uy * (arrow_len - 1.2))
            if e.get("bidirectional") and len(draw_pts) >= 2:
                x_start, y_start = draw_pts[0]
                x_next, y_next = draw_pts[1]
                seg_len = math.hypot(x_next - x_start, y_next - y_start)
                if seg_len > arrow_len:
                    ux = (x_next - x_start) / seg_len
                    uy = (y_next - y_start) / seg_len
                    draw_pts[0] = (x_start + ux * (arrow_len - 1.2), y_start + uy * (arrow_len - 1.2))

            self._draw_orthogonal_segments(edges_group, draw_pts, color, thickness, style)

            # Explicit target arrowhead polygon
            if len(pts) >= 2:
                self._draw_arrowhead(edges_group, pts[-2], pts[-1], color, arrow_len, arrow_half_w)

            # Optional bidirectional source arrowhead
            if e.get("bidirectional") and len(pts) >= 2:
                self._draw_arrowhead(edges_group, pts[1], pts[0], color, arrow_len, arrow_half_w)

            labels_and_badges.append((e, pts, color))

        # Third pass: draw numbered step circles & edge labels on top of all lines with collision avoidance
        placed_pills: List[Dict[str, float]] = []

        for e, pts, color in labels_and_badges:
            step = e.get("step")
            label = e.get("label")
            if step is None and not label:
                continue

            if step is not None and label:
                lbl_str = str(label)
                pill_w = estimate_text_width(lbl_str, 8.8) + 28.0
                pill_h = 16.0
            elif step is not None:
                pill_w = 16.0
                pill_h = 16.0
            else:
                lbl_str = str(label)
                pill_w = estimate_text_width(lbl_str, 8.8) + 12.0
                pill_h = 15.0

            card_boxes_list = [b for b in boxes.values() if b["h"] <= 80.0]
            mid_x, mid_y = self._choose_non_overlapping_midpoint(pts, pill_w, pill_h, placed_pills, card_boxes_list)
            placed_pills.append({"x": mid_x - pill_w / 2.0, "y": mid_y - pill_h / 2.0, "w": pill_w, "h": pill_h})

            if step is not None and label:
                lbl_str = str(label)
                px = mid_x - pill_w / 2.0
                py = mid_y - pill_h / 2.0
                ET.SubElement(
                    edges_group,
                    "rect",
                    {
                        "x": f"{px - 0.9:.2f}",
                        "y": f"{py - 0.9:.2f}",
                        "width": f"{pill_w + 1.8:.2f}",
                        "height": f"{pill_h + 1.8:.2f}",
                        "rx": "8.8",
                        "ry": "8.8",
                        "fill": color,
                    },
                )
                ET.SubElement(
                    edges_group,
                    "rect",
                    {
                        "x": f"{px:.2f}",
                        "y": f"{py:.2f}",
                        "width": f"{pill_w:.2f}",
                        "height": f"{pill_h:.2f}",
                        "rx": "8",
                        "ry": "8",
                        "fill": "#ffffff",
                    },
                )
                cx = px + 8.5
                cy = mid_y
                ET.SubElement(
                    edges_group,
                    "circle",
                    {
                        "cx": f"{cx:.2f}",
                        "cy": f"{cy:.2f}",
                        "r": "6.8",
                        "fill": color,
                    },
                )
                st_txt = ET.SubElement(
                    edges_group,
                    "text",
                    {
                        "x": f"{cx:.2f}",
                        "y": f"{cy + 3.0:.2f}",
                        "fill": "#ffffff",
                        "font-size": "8.5",
                        "font-weight": "700",
                        "text-anchor": "middle",
                    },
                )
                st_txt.text = str(step)

                lbl_el = ET.SubElement(
                    edges_group,
                    "text",
                    {
                        "x": f"{px + 19.0:.2f}",
                        "y": f"{mid_y + 3.0:.2f}",
                        "fill": "#202124",
                        "font-size": "8.8",
                        "font-weight": "500",
                    },
                )
                lbl_el.text = lbl_str

            elif step is not None:
                ET.SubElement(
                    edges_group,
                    "circle",
                    {
                        "cx": f"{mid_x:.2f}",
                        "cy": f"{mid_y:.2f}",
                        "r": "8.7",
                        "fill": "#ffffff",
                    },
                )
                ET.SubElement(
                    edges_group,
                    "circle",
                    {
                        "cx": f"{mid_x:.2f}",
                        "cy": f"{mid_y:.2f}",
                        "r": "7.5",
                        "fill": color,
                    },
                )
                st_txt = ET.SubElement(
                    edges_group,
                    "text",
                    {
                        "x": f"{mid_x:.2f}",
                        "y": f"{mid_y + 3.0:.2f}",
                        "fill": "#ffffff",
                        "font-size": "8.8",
                        "font-weight": "700",
                        "text-anchor": "middle",
                    },
                )
                st_txt.text = str(step)

            elif label:
                lbl_str = str(label)
                px = mid_x - pill_w / 2.0
                py = mid_y - pill_h / 2.0
                ET.SubElement(
                    edges_group,
                    "rect",
                    {
                        "x": f"{px - 0.8:.2f}",
                        "y": f"{py - 0.8:.2f}",
                        "width": f"{pill_w + 1.6:.2f}",
                        "height": f"{pill_h + 1.6:.2f}",
                        "rx": "3.8",
                        "ry": "3.8",
                        "fill": "#90caf9",
                    },
                )
                ET.SubElement(
                    edges_group,
                    "rect",
                    {
                        "x": f"{px:.2f}",
                        "y": f"{py:.2f}",
                        "width": f"{pill_w:.2f}",
                        "height": f"{pill_h:.2f}",
                        "rx": "3",
                        "ry": "3",
                        "fill": "#ffffff",
                    },
                )
                lbl_el = ET.SubElement(
                    edges_group,
                    "text",
                    {
                        "x": f"{mid_x:.2f}",
                        "y": f"{mid_y + 3.0:.2f}",
                        "fill": "#3c4043",
                        "font-size": "8.8",
                        "font-weight": "500",
                        "text-anchor": "middle",
                    },
                )
                lbl_el.text = lbl_str

    @staticmethod
    def _draw_orthogonal_segments(
        group: ET.Element,
        pts: List[Tuple[float, float]],
        color: str,
        thickness: float,
        style: str,
    ) -> None:
        """Draws orthogonal segments using filled <rect> elements for 100% renderer fidelity."""
        half_t = thickness / 2.0
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            seg_len = math.hypot(dx, dy)
            if seg_len < 0.5:
                continue

            is_horiz = abs(dy) <= abs(dx)
            if style not in ("dashed", "dotted"):
                if is_horiz:
                    rx = min(x1, x2) - half_t
                    ry = (y1 + y2) / 2.0 - half_t
                    rw = abs(dx) + thickness
                    rh = thickness
                else:
                    rx = (x1 + x2) / 2.0 - half_t
                    ry = min(y1, y2) - half_t
                    rw = thickness
                    rh = abs(dy) + thickness
                ET.SubElement(
                    group,
                    "rect",
                    {
                        "x": f"{rx:.2f}",
                        "y": f"{ry:.2f}",
                        "width": f"{rw:.2f}",
                        "height": f"{rh:.2f}",
                        "fill": color,
                    },
                )
            else:
                dash_len, gap_len = (5.0, 3.5) if style == "dashed" else (2.2, 2.2)
                ux, uy = dx / seg_len, dy / seg_len
                pos = 0.0
                while pos < seg_len:
                    d_len = min(dash_len, seg_len - pos)
                    if d_len >= 0.8:
                        sx = x1 + ux * pos
                        sy = y1 + uy * pos
                        ex = x1 + ux * (pos + d_len)
                        ey = y1 + uy * (pos + d_len)
                        if is_horiz:
                            rx = min(sx, ex)
                            ry = (sy + ey) / 2.0 - half_t
                            rw = max(1.0, abs(ex - sx))
                            rh = thickness
                        else:
                            rx = (sx + ex) / 2.0 - half_t
                            ry = min(sy, ey)
                            rw = thickness
                            rh = max(1.0, abs(ey - sy))
                        ET.SubElement(
                            group,
                            "rect",
                            {
                                "x": f"{rx:.2f}",
                                "y": f"{ry:.2f}",
                                "width": f"{rw:.2f}",
                                "height": f"{rh:.2f}",
                                "fill": color,
                            },
                        )
                    pos += dash_len + gap_len

    @staticmethod
    def _draw_arrowhead(
        group: ET.Element,
        p_from: Tuple[float, float],
        p_tip: Tuple[float, float],
        color: str,
        length: float,
        half_w: float,
    ) -> None:
        dx = p_tip[0] - p_from[0]
        dy = p_tip[1] - p_from[1]
        seg_len = math.hypot(dx, dy)
        if seg_len < 1e-3:
            return
        ux, uy = dx / seg_len, dy / seg_len
        px, py = -uy, ux

        bx = p_tip[0] - ux * length
        by = p_tip[1] - uy * length
        c1x, c1y = bx + px * half_w, by + py * half_w
        c2x, c2y = bx - px * half_w, by - py * half_w

        ET.SubElement(
            group,
            "polygon",
            {
                "points": f"{p_tip[0]:.2f},{p_tip[1]:.2f} {c1x:.2f},{c1y:.2f} {c2x:.2f},{c2y:.2f}",
                "fill": color,
            },
        )

    @staticmethod
    def _choose_non_overlapping_midpoint(
        pts: List[Tuple[float, float]],
        pill_w: float,
        pill_h: float,
        placed_pills: List[Dict[str, float]],
        card_boxes: Optional[List[Dict[str, float]]] = None,
    ) -> Tuple[float, float]:
        """Finds a point along `pts` that avoids colliding with existing pills and card boxes."""
        segments = []
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            seg_len = math.hypot(x2 - x1, y2 - y1)
            segments.append((seg_len, (x1, y1), (x2, y2)))
        segments.sort(key=lambda s: s[0], reverse=True)

        def overlaps_pills(cx: float, cy: float) -> bool:
            bx = cx - pill_w / 2.0 - 4.0
            by = cy - pill_h / 2.0 - 2.0
            bw = pill_w + 8.0
            bh = pill_h + 4.0
            for p in placed_pills:
                if not (bx + bw < p["x"] or p["x"] + p["w"] < bx or by + bh < p["y"] or p["y"] + p["h"] < by):
                    return True
            return False

        def overlaps_cards(cx: float, cy: float) -> bool:
            if not card_boxes:
                return False
            bx = cx - pill_w / 2.0 - 2.0
            by = cy - pill_h / 2.0 - 2.0
            bw = pill_w + 4.0
            bh = pill_h + 4.0
            for c in card_boxes:
                if not (bx + bw < c["x"] or c["x"] + c["w"] < bx or by + bh < c["y"] or c["y"] + c["h"] < by):
                    return True
            return False

        candidates: List[Tuple[float, float]] = []

        # For 4-point horizontal doglegs between columns, prioritize the horizontal center of the channel
        if len(pts) == 4 and abs(pts[0][1] - pts[1][1]) < 1.0 and abs(pts[2][1] - pts[3][1]) < 1.0:
            ch_x = (pts[0][0] + pts[3][0]) / 2.0
            mid_y = (pts[1][1] + pts[2][1]) / 2.0
            candidates.extend([
                (ch_x, mid_y),
                (ch_x, pts[0][1]),
                (ch_x, pts[3][1]),
                (pts[1][0], mid_y),
            ])

        fracs = [0.5, 0.35, 0.65, 0.25, 0.75]
        for seg_len, (x1, y1), (x2, y2) in segments:
            if seg_len < 12.0:
                continue
            for f in fracs:
                candidates.append((x1 + (x2 - x1) * f, y1 + (y2 - y1) * f))

        # Pass 1: neither overlaps cards nor pills
        for cx, cy in candidates:
            if not overlaps_cards(cx, cy) and not overlaps_pills(cx, cy):
                return cx, cy

        # Pass 2: doesn't overlap pills
        for cx, cy in candidates:
            if not overlaps_pills(cx, cy):
                return cx, cy

        # Fallback: midpoint of longest segment nudged vertically
        _, (x1, y1), (x2, y2) = segments[0]
        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        for dy in (-16.0, 16.0, -28.0, 28.0):
            if not overlaps_pills(cx, cy + dy):
                return cx, cy + dy
        return cx, cy


# ---------------------------------------------------------------------------
# Mermaid Flowchart -> Declarative GCP Architecture Spec Translator
# ---------------------------------------------------------------------------

def parse_mermaid_to_spec(mermaid_text: str, icon_lib: IconLibrary) -> Dict[str, Any]:
    """Translates a Mermaid `flowchart` / `graph` into a GCP Architecture JSON spec."""
    lines = [ln.strip() for ln in mermaid_text.splitlines() if ln.strip() and not ln.strip().startswith("%%")]
    direction = "LR"
    if lines:
        m_dir = re.match(r"^(?:flowchart|graph)\s+(LR|RL|TB|TD|BT)\b", lines[0], re.I)
        if m_dir:
            direction = m_dir.group(1).upper()
            lines = lines[1:]

    root_zone: Dict[str, Any] = {
        "id": "_root",
        "zones": [],
        "cards": [],
        "layout": "horizontal" if direction in ("LR", "RL") else "vertical",
    }
    zone_stack: List[Dict[str, Any]] = [root_zone]
    cards_by_id: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, Any]] = []
    zone_palette_cycle = ["blue", "amber", "green", "purple", "coral"]
    zone_counter = 0

    def split_card_label(raw_label: str) -> Tuple[str, str, str]:
        cleaned = re.sub(r"<br\s*/?>|\\n", "\n", raw_label, flags=re.I)
        cleaned = re.sub(r"[*_`]", "", cleaned).strip().strip('"').strip("'")
        raw_parts = [re.sub(r"^[-•*]\s*", "", p.strip()) for p in cleaned.split("\n") if p.strip()]
        if len(raw_parts) >= 3:
            return raw_parts[0], raw_parts[1], raw_parts[2]
        if len(raw_parts) == 2:
            return raw_parts[0], raw_parts[1], ""
        single = raw_parts[0] if raw_parts else "Component"
        # Check for "Title (Subtitle)" pattern
        m_paren = re.match(r"^(.+?)\s*\(([^)]+)\)$", single)
        if m_paren:
            return m_paren.group(1).strip(), m_paren.group(2).strip(), ""
        # Check for "Title — Subtitle" or "Title: Subtitle"
        for sep in (" — ", " - ", ": "):
            if sep in single:
                a, b = single.split(sep, 1)
                return a.strip(), b.strip(), ""
        return single, "Google Cloud", ""

    def register_node_token(token: str, current_zone: Dict[str, Any]) -> str:
        token = token.strip()
        # Match id["label"], id("label"), id[("label")], id[["label"]], id[label]
        m = re.match(
            r'^([A-Za-z0-9_.-]+)\s*(?:\[\(|\(\[|\[\[|\{\{|\(\(|\(|\[|\{)(.+?)(?:\)\]|\]\)|\]\]|\}\}|\)\)|\)|\]|\})$',
            token,
        )
        if m:
            nid, raw_lbl = m.group(1), m.group(2)
            title, subtitle, badge = split_card_label(raw_lbl)
            icon = icon_lib.resolve_icon_slug(None, title=title, subtitle=subtitle)
            if nid not in cards_by_id:
                card_obj = {"id": nid, "title": title, "subtitle": subtitle, "icon": icon}
                if badge:
                    card_obj["badge"] = badge
                cards_by_id[nid] = card_obj
                current_zone.setdefault("cards", []).append(card_obj)
            return nid

        nid = re.sub(r"[^A-Za-z0-9_.-]", "", token)
        if nid and nid not in cards_by_id:
            card_obj = {
                "id": nid,
                "title": nid.replace("_", " "),
                "subtitle": "Component",
                "icon": icon_lib.resolve_icon_slug(nid, title=nid),
            }
            cards_by_id[nid] = card_obj
            current_zone.setdefault("cards", []).append(card_obj)
        return nid

    edge_pattern = re.compile(
        r"^(.+?)\s*(<-->|-->|-\.->|==>|---)\s*(?:\|([^|]*)\|\s*)?(.+)$"
    )

    for ln in lines:
        if ln.startswith(("classDef ", "class ", "style ", "linkStyle ", "direction ")):
            m_sub_dir = re.match(r"^direction\s+(LR|RL|TB|TD|BT)\b", ln, re.I)
            if m_sub_dir and len(zone_stack) > 1:
                d_val = m_sub_dir.group(1).upper()
                zone_stack[-1]["layout"] = "horizontal" if d_val in ("LR", "RL") else "vertical"
            continue

        # Subgraph start
        m_sg = re.match(r"^subgraph\s+([^\[\s]+)?\s*(?:\[(.+)\])?$", ln)
        if m_sg:
            raw_id = (m_sg.group(1) or f"zone_{zone_counter}").strip().strip('"')
            raw_lbl = (m_sg.group(2) or raw_id).strip().strip('"')
            raw_lbl = re.sub(r"<br\s*/?>|\\n", " — ", raw_lbl, flags=re.I)
            depth = len(zone_stack) - 1
            color = zone_palette_cycle[zone_counter % len(zone_palette_cycle)] if depth == 0 else "amber"
            zone_counter += 1
            new_zone: Dict[str, Any] = {
                "id": raw_id,
                "label": raw_lbl,
                "color": color,
                "layout": "horizontal" if depth > 0 else ("horizontal" if direction in ("TB", "TD") else "vertical"),
                "subzones": [],
                "cards": [],
            }
            zone_stack[-1].setdefault("subzones" if depth > 0 else "zones", []).append(new_zone)
            zone_stack.append(new_zone)
            continue

        if ln == "end":
            if len(zone_stack) > 1:
                zone_stack.pop()
            continue

        # Edge match
        m_edge = edge_pattern.match(ln)
        if m_edge:
            lhs, arrow, edge_lbl, rhs = m_edge.groups()
            u_id = register_node_token(lhs, zone_stack[-1])
            v_id = register_node_token(rhs, zone_stack[-1])
            edge_obj: Dict[str, Any] = {"from": u_id, "to": v_id}
            if arrow == "-.->":
                edge_obj["style"] = "dashed"
            elif arrow == "<-->":
                edge_obj["bidirectional"] = True
            if edge_lbl:
                lbl_parts = [p.strip() for p in re.split(r"<br\s*/?>|\\n", edge_lbl.strip().strip('"'), flags=re.I) if p.strip()]
                lbl_clean = lbl_parts[0] if lbl_parts else ""
                lbl_clean = re.sub(r"[*_`]", "", lbl_clean)
                m_step = re.match(r"^(?:\(?(\d+)\)?[.:)\s-]+)(.*)$", lbl_clean)
                if m_step:
                    edge_obj["step"] = int(m_step.group(1))
                    if m_step.group(2).strip():
                        edge_obj["label"] = truncate_text_to_width(m_step.group(2).strip(), 8.8, 130.0)
                elif lbl_clean.isdigit():
                    edge_obj["step"] = int(lbl_clean)
                elif lbl_clean:
                    edge_obj["label"] = truncate_text_to_width(lbl_clean, 8.8, 130.0)
            edges.append(edge_obj)
            continue

        # Standalone node declaration
        if re.match(r"^[A-Za-z0-9_.-]+\s*[\[\(\{]", ln):
            register_node_token(ln, zone_stack[-1])

    spec: Dict[str, Any] = {
        "theme": "classic",
        "layout": root_zone["layout"],
        "zones": root_zone.get("zones", []),
        "cards": root_zone.get("cards", []),
        "edges": edges,
    }
    return spec


def extract_mermaid_blocks_from_markdown(md_path: str) -> List[Dict[str, Any]]:
    """Extracts all fenced ```mermaid blocks from a Markdown file with heading context."""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    blocks = []
    in_mermaid = False
    start_line = 0
    curr_heading = "Document Root"
    buf: List[str] = []

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not in_mermaid and stripped.startswith("#"):
            curr_heading = re.sub(r"^#+\s*", "", stripped).strip("* ")
        if not in_mermaid and re.match(r"^`{3,}\s*mermaid\b", stripped, re.I):
            in_mermaid = True
            start_line = idx
            buf = []
        elif in_mermaid and re.match(r"^`{3,}\s*$", stripped):
            in_mermaid = False
            blocks.append(
                {
                    "index": len(blocks),
                    "heading": curr_heading,
                    "start_line": start_line,
                    "end_line": idx,
                    "code": "".join(buf),
                }
            )
        elif in_mermaid:
            buf.append(line)

    return blocks


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile JSON architecture specs or Mermaid flowcharts into Google Cloud Reference Architecture SVGs."
    )
    parser.add_argument("--input", "-i", help="Path to declarative JSON architecture spec file.")
    parser.add_argument("--from-mermaid", "-m", help="Path to a standalone .mmd Mermaid file to convert.")
    parser.add_argument("--markdown", "--md", help="Path to a Markdown (.md) file containing ```mermaid blocks.")
    parser.add_argument("--list-mermaid", action="store_true", help="List all ```mermaid blocks in --markdown.")
    parser.add_argument("--block-index", type=int, default=0, help="0-based index of the ```mermaid block in --markdown.")
    parser.add_argument("--dump-json", help="Write the translated declarative JSON spec to this file path.")
    parser.add_argument("--output", "-o", help="Output .svg file path.")
    parser.add_argument("--theme", choices=["classic", "modern"], help="Override visual theme ('classic' or 'modern').")
    parser.add_argument("--list-icons", action="store_true", help="List all bundled official GCP SVG icons and aliases.")
    parser.add_argument(
        "--png",
        nargs="?",
        const="AUTO",
        default="AUTO",
        help="Also rasterize a 2x HiDPI PNG alongside the SVG (default: <output>.png; pass custom path to override).",
    )
    parser.add_argument(
        "--no-png",
        action="store_true",
        help="Skip automatic 2x HiDPI PNG generation alongside --output.",
    )

    args = parser.parse_args()
    icon_lib = IconLibrary()

    if args.list_icons:
        print(f"Icons directory: {icon_lib.icons_dir}")
        print(f"Available SVG icons ({len(icon_lib.available_icons)}): {', '.join(icon_lib.available_icons)}")
        print(f"Registered aliases ({len(icon_lib.aliases)}):")
        for k, v in sorted(icon_lib.aliases.items()):
            print(f"  {k:24s} -> {v}.svg")
        return 0

    if args.markdown and args.list_mermaid:
        blocks = extract_mermaid_blocks_from_markdown(args.markdown)
        print(f"Found {len(blocks)} Mermaid block(s) in {args.markdown}:")
        for b in blocks:
            first_line = b["code"].strip().splitlines()[0] if b["code"].strip() else ""
            print(f"  [{b['index']}] Lines {b['start_line']}-{b['end_line']} | Heading: {b['heading']} | {first_line}")
        return 0

    spec: Optional[Dict[str, Any]] = None
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            spec = json.load(f)
    elif args.from_mermaid:
        with open(args.from_mermaid, "r", encoding="utf-8") as f:
            spec = parse_mermaid_to_spec(f.read(), icon_lib)
    elif args.markdown:
        blocks = extract_mermaid_blocks_from_markdown(args.markdown)
        if not blocks:
            print(f"Error: No ```mermaid blocks found in {args.markdown}", file=sys.stderr)
            return 1
        if args.block_index < 0 or args.block_index >= len(blocks):
            print(
                f"Error: --block-index {args.block_index} out of range (0..{len(blocks) - 1})",
                file=sys.stderr,
            )
            return 1
        spec = parse_mermaid_to_spec(blocks[args.block_index]["code"], icon_lib)
    else:
        parser.print_help()
        return 1

    if args.theme:
        spec["theme"] = args.theme

    if args.dump_json:
        os.makedirs(os.path.dirname(os.path.abspath(args.dump_json)), exist_ok=True)
        with open(args.dump_json, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2)
        print(f"Wrote JSON architecture spec to {args.dump_json}")

    if args.output:
        renderer = GCPDiagramRenderer(spec, icon_lib)
        svg_xml = renderer.render()
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(svg_xml)
        print(f"Rendered Google Cloud Reference Architecture SVG to {args.output}")

        if args.png and not args.no_png:
            import shutil
            import subprocess
            png_path = (
                os.path.splitext(args.output)[0] + ".png"
                if args.png == "AUTO"
                else args.png
            )
            os.makedirs(os.path.dirname(os.path.abspath(png_path)), exist_ok=True)
            magick_bin = shutil.which("magick") or shutil.which("convert")
            rsvg_bin = shutil.which("rsvg-convert")
            if magick_bin:
                subprocess.run(
                    [magick_bin, "-density", "144", "-background", "white", args.output, png_path],
                    check=True,
                )
            elif rsvg_bin:
                subprocess.run(
                    [rsvg_bin, "-z", "2", "-f", "png", "-o", png_path, args.output],
                    check=True,
                )
            else:
                raise RuntimeError("Neither ImageMagick ('magick'/'convert') nor 'rsvg-convert' found in PATH.")
            print(f"Rasterized 2x HiDPI PNG to {png_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
