#!/usr/bin/env python3
"""
Generate Social Preview GIF matching assets/banner.svg visual language.
Strict specifications:
- GIF format with dynamic animations mirroring assets/banner.svg
- Dimensions: exactly 640x320 px
- Size: strictly under 1 MB
- Vertical padding: strictly 50px on top and 50px on bottom (all content between y=50 and y=270)

The generator parses assets/banner.svg from the destination project to extract:
  - Title, subtitle/tagline, category pill, feature pills/badges
  - Background gradient colors, grid lines, glowing orbs
  - Accent/primary colors for waves, dots, diagrams
  - Right-side architectural diagram nodes
"""

import os
import sys
import math
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def hex_to_rgb(h):
    """Convert #rrggbb or #rgb to (r, g, b) tuple."""
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    if len(h) != 6:
        return None
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return None


def interpolate_color(c1, c2, factor):
    return tuple(int(a + (b - a) * factor) for a, b in zip(c1, c2))


def color_with_alpha(rgb, a):
    return (*rgb, a)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def strip_emoji(text):
    """Remove emoji and non-BMP unicode, keeping only printable ASCII/Latin."""
    return re.sub(
        r'[\U00002600-\U000027BF'   # Misc symbols
        r'\U0000FE00-\U0000FE0F'    # Variation selectors
        r'\U0001F000-\U0001FFFF'    # Emoticons, symbols, flags, etc.
        r'\U00002702-\U000027B0'    # Dingbats
        r'\U000024C2-\U0001F251'    # Enclosed chars
        r'\U0000200D'               # ZWJ
        r'\U0000FE0F'               # VS16
        r']+', '', text
    ).strip()


# ---------------------------------------------------------------------------
# SVG Parser — extracts ALL visual metadata from assets/banner.svg
# ---------------------------------------------------------------------------

def parse_banner_svg(svg_path):
    """
    Deep-parse assets/banner.svg and return a rich info dict used by the
    renderer to faithfully replicate the banner's visual language.
    """
    info = {
        # Text content
        "title": None,
        "subtitle": None,
        "tagline": None,           # small uppercase pill text (e.g. "COMPOSABLE COMMERCE")
        "feature_pills": [],       # list of feature pill strings
        # Colors extracted from gradients / fills
        "bg_colors": [],           # background gradient stop colors
        "primary_colors": [],      # primary/title gradient stop colors
        "accent_color": None,      # single dominant accent hex
        # Background elements
        "orbs": [],                # list of {"cx","cy","r","color","opacity"} dicts
        "has_grid": False,
        "grid_color": None,
        # Right-side diagram nodes
        "diagram_nodes": [],       # list of {"label", "sublabel"} dicts
        # Animation hints
        "has_flowing_beams": False,
        "has_dash_flow": False,
    }

    if not os.path.exists(svg_path):
        return info

    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except Exception as e:
        safe_print(f"Warning: could not parse {svg_path}: {e}")
        return info

    ns = ''
    if root.tag.startswith('{'):
        ns = root.tag.split('}')[0] + '}'

    # --- Collect all <text> elements with class/content ---
    texts = []
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]
        if tag == 'text':
            cls = elem.attrib.get('class', '')
            content = "".join(elem.itertext()).strip()
            content = content.replace('&amp;', '&')
            if content:
                texts.append((cls, content))

    # --- Title ---
    for cls, t in texts:
        if 'title' in cls and info["title"] is None:
            info["title"] = t
            break
    if not info["title"]:
        for cls, t in texts:
            if 'awesome' in t.lower():
                info["title"] = t
                break
    if not info["title"] and texts:
        # pick the longest text as likely title
        info["title"] = max(texts, key=lambda x: len(x[1]))[1]

    # --- Subtitle ---
    for cls, t in texts:
        if any(k in cls for k in ('subtitle', 'desc')):
            info["subtitle"] = t
            break
    if not info["subtitle"]:
        # second longest text after title
        remaining = [(c, t) for c, t in texts if t != info.get("title")]
        if remaining:
            info["subtitle"] = max(remaining, key=lambda x: len(x[1]))[1]

    # --- Tagline (small uppercase category pill) ---
    for cls, t in texts:
        if 'tagline' in cls or 'badge-text' in cls:
            info["tagline"] = t
            break
    if not info["tagline"]:
        for cls, t in texts:
            if t.isupper() and len(t) > 4 and t != info.get("title"):
                info["tagline"] = t
                break

    # --- Feature pills vs Diagram nodes ---
    # Both use class="node-text" but differ by parent <g> transform position.
    # Feature pills: inside translate(70,0) → translate(0,240) (left side)
    # Diagram nodes: inside translate(920,80) (right side, uppercase labels)
    known = {info.get("title"), info.get("subtitle"), info.get("tagline")}

    # Identify right-side diagram labels by scanning <g> transforms
    right_side_labels = set()
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]
        if tag == 'g':
            transform = elem.attrib.get('transform', '')
            m = re.search(r'translate\(\s*(\d+)', transform)
            if m and int(m.group(1)) >= 800:
                for child in elem.iter():
                    ctag = child.tag.split('}')[-1]
                    if ctag == 'text':
                        content = "".join(child.itertext()).strip()
                        content = content.replace('&amp;', '&')
                        if content and content not in known:
                            right_side_labels.add(content)
                            info["diagram_nodes"].append({"label": content, "sublabel": None})

    info["diagram_nodes"] = info["diagram_nodes"][:3]

    # Feature pills: node-text elements NOT in the right-side group
    for cls, t in texts:
        if t in known or t in right_side_labels:
            continue
        if any(k in cls for k in ('node-text', 'node_text')):
            clean = strip_emoji(t)
            if clean:
                info["feature_pills"].append(clean)
        elif len(t) < 30 and t not in known:
            clean = strip_emoji(t)
            if clean:
                info["feature_pills"].append(clean)
    # De-dup preserving order
    seen = set()
    deduped = []
    for p in info["feature_pills"]:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    info["feature_pills"] = deduped[:4]

    # --- Gradients & Colors ---
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]
        if tag == 'linearGradient':
            gid = elem.attrib.get('id', '')
            stops = []
            for child in elem:
                ctag = child.tag.split('}')[-1]
                if ctag == 'stop':
                    sc = child.attrib.get('stop-color', '')
                    rgb = hex_to_rgb(sc)
                    if rgb:
                        stops.append(rgb)
            if 'bg' in gid and stops:
                info["bg_colors"] = stops
            elif ('primary' in gid or 'title' in gid) and stops:
                info["primary_colors"] = stops
            elif stops and not info["primary_colors"]:
                info["primary_colors"] = stops

    # --- Accent color (first non-bg hex in the SVG) ---
    raw_svg = open(svg_path, 'r', encoding='utf-8').read()
    accent_candidates = re.findall(r'stroke=["\']?(#[0-9a-fA-F]{6})', raw_svg)
    for ac in accent_candidates:
        rgb = hex_to_rgb(ac)
        if rgb and sum(rgb) > 120:  # skip very dark colors
            info["accent_color"] = rgb
            break
    if not info["accent_color"] and info["primary_colors"]:
        info["accent_color"] = info["primary_colors"][0]

    # --- Glowing background orbs (circles with large r & low opacity) ---
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]
        if tag == 'circle':
            try:
                r = float(elem.attrib.get('r', 0))
            except ValueError:
                continue
            if r >= 80:
                fill = elem.attrib.get('fill', '')
                opacity_str = elem.attrib.get('opacity', '1')
                try:
                    opacity = float(opacity_str)
                except ValueError:
                    opacity = 0.15
                rgb = hex_to_rgb(fill)
                if rgb:
                    info["orbs"].append({
                        "cx": float(elem.attrib.get('cx', 200)),
                        "cy": float(elem.attrib.get('cy', 100)),
                        "r": r,
                        "color": rgb,
                        "opacity": opacity,
                    })

    # --- Grid ---
    if 'grid' in raw_svg.lower():
        info["has_grid"] = True
        grid_m = re.search(r'grid.*?stroke.*?(#[0-9a-fA-F]{6})', raw_svg, re.S)
        if grid_m:
            info["grid_color"] = hex_to_rgb(grid_m.group(1))

    # --- Flowing beams / dashed animated lines ---
    if 'flowing-beam' in raw_svg or 'dash-flow' in raw_svg or 'stroke-dasharray' in raw_svg:
        info["has_flowing_beams"] = True
    if 'dash' in raw_svg:
        info["has_dash_flow"] = True

    return info


# ---------------------------------------------------------------------------
# Fallback app name from CWD folder name
# ---------------------------------------------------------------------------

def get_fallback_app_name():
    """Derives appnamefull from the current working directory folder name."""
    cwd_name = os.path.basename(os.getcwd().strip('/\\'))
    if not cwd_name:
        return "Awesome Project"
    clean_name = cwd_name.replace('-', ' ').replace('_', ' ')
    words = clean_name.split()
    if words and words[0].lower() != "awesome":
        words.insert(0, "Awesome")
    return " ".join(w.capitalize() for w in words)


# ---------------------------------------------------------------------------
# Safe print (handles Unicode chars on Windows consoles)
# ---------------------------------------------------------------------------

def safe_print(*args, **kwargs):
    """Print with fallback for Unicode encoding errors on Windows."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        text = " ".join(str(a) for a in args)
        print(text.encode('ascii', errors='replace').decode('ascii'), **kwargs)


# ---------------------------------------------------------------------------
# Font loader
# ---------------------------------------------------------------------------

def load_fonts():
    """Return (bold_font_path, regular_font_path) or (None, None)."""
    candidates = [
        (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf"),
        (r"C:\Windows\Fonts\arialbd.ttf",  r"C:\Windows\Fonts\arial.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf"),
    ]
    for bold_p, reg_p in candidates:
        if os.path.exists(bold_p) and os.path.exists(reg_p):
            return bold_p, reg_p
    return None, None


# ---------------------------------------------------------------------------
# Coordinate scaling: SVG 1200x360 → GIF 640x320 with 50px padding
#
# The SVG viewBox is 0 0 1200 360.
# The GIF is 640x320 with a content zone from y=50 to y=270 (220px tall).
# Scale factors:
#   sx = 640 / 1200  ≈ 0.5333
#   sy = 220 / 360   ≈ 0.6111
# Y offset = 50 (padding top)
# ---------------------------------------------------------------------------

GIF_W = 640
GIF_H = 320
PAD_TOP = 50
PAD_BOT = 50
CONTENT_H = GIF_H - PAD_TOP - PAD_BOT  # 220

SVG_W = 1200
SVG_H = 360

SX = GIF_W / SVG_W      # 0.5333
SY = CONTENT_H / SVG_H  # 0.6111


def svg_x(x):
    """Scale an SVG x-coordinate to GIF x-coordinate."""
    return int(x * SX)


def svg_y(y):
    """Scale an SVG y-coordinate to GIF y-coordinate (with padding offset)."""
    return int(y * SY + PAD_TOP)


def svg_size(s):
    """Scale a size/font-size proportionally (average of SX and SY)."""
    return max(1, int(s * (SX + SY) / 2))


# ---------------------------------------------------------------------------
# Text measurement helper
# ---------------------------------------------------------------------------

def text_width(draw, text, font):
    """Measure text width using the draw object."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_height(draw, text, font):
    """Measure text height using the draw object."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def safe_rounded_rect(draw, coords, radius, **kwargs):
    """Draw a rounded rectangle, clamping radius to avoid Pillow 9.x crashes."""
    x1, y1, x2, y2 = coords
    w = x2 - x1
    h = y2 - y1
    if w <= 0 or h <= 0:
        return
    # Pillow 9.5.0 crashes when radius >= (min_dim / 2) due to internal rounding
    max_r = max(0, min(w, h) // 2 - 2)
    radius = min(radius, max_r)
    if radius <= 0:
        draw.rectangle(coords, **kwargs)
    else:
        draw.rounded_rectangle(coords, radius=radius, **kwargs)


# ---------------------------------------------------------------------------
# Frame renderer — faithfully mirrors banner.svg visual language
# ---------------------------------------------------------------------------

def render_frame(frame_idx, total_frames, svg_info, width=GIF_W, height=GIF_H):
    t = frame_idx / total_frames  # normalized time [0..1)

    # ---- Resolve colors from SVG info or use defaults ----
    bg_colors = svg_info.get("bg_colors") or [(15, 23, 42), (30, 27, 75), (15, 23, 42)]
    primary_colors = svg_info.get("primary_colors") or [(56, 189, 248), (129, 140, 248), (192, 132, 252)]
    accent = svg_info.get("accent_color") or (56, 189, 248)
    grid_color = svg_info.get("grid_color") or (51, 65, 85)

    # ---- 1. Background gradient fill ----
    img = Image.new("RGBA", (width, height), color_with_alpha(bg_colors[0], 255))
    draw = ImageDraw.Draw(img)

    # Diagonal gradient fill across entire canvas
    for y_px in range(height):
        frac = y_px / height
        c = interpolate_color(bg_colors[0], bg_colors[-1], frac)
        draw.line([(0, y_px), (width, y_px)], fill=color_with_alpha(c, 255))

    # ---- 2. Glowing background orbs (animated position) ----
    orbs = svg_info.get("orbs", [])
    if not orbs:
        # Default orbs matching banner.svg common pattern
        orbs = [
            {"cx": 150, "cy": 100, "r": 140, "color": primary_colors[0], "opacity": 0.18},
            {"cx": 1050, "cy": 240, "r": 160, "color": primary_colors[-1], "opacity": 0.15},
            {"cx": 600, "cy": 180, "r": 120, "color": (192, 132, 252), "opacity": 0.12},
        ]
    for i, orb in enumerate(orbs):
        ocx = svg_x(orb["cx"]) + int(10 * math.sin(t * 2 * math.pi + i * 1.5))
        ocy = svg_y(orb["cy"]) + int(6 * math.cos(t * 2 * math.pi + i * 2.0))
        orb_r = int(orb["r"] * SX * 0.5)
        alpha = max(8, min(45, int(orb["opacity"] * 255 * 0.6)))
        col = color_with_alpha(orb["color"], alpha)
        draw.ellipse([ocx - orb_r, ocy - orb_r, ocx + orb_r, ocy + orb_r], fill=col)

    # ---- 3. Grid lines (subtle, matching .grid-line in SVG) ----
    if svg_info.get("has_grid", True):
        gc = color_with_alpha(grid_color, 16)
        # SVG grid lines at x=100,300,500,700,900 and y=120,240
        for gx_svg in [100, 300, 500, 700, 900]:
            gx = svg_x(gx_svg)
            draw.line([(gx, PAD_TOP), (gx, height - PAD_BOT)], fill=gc, width=1)
        for gy_svg in [120, 240]:
            gy = svg_y(gy_svg)
            draw.line([(0, gy), (width, gy)], fill=gc, width=1)

    # ---- 4. Fonts (scaled proportionally from SVG font sizes) ----
    bold_path, reg_path = load_fonts()
    if bold_path:
        # SVG: title=52px, subtitle=20px, tagline=14px, node-text=13px
        font_title    = ImageFont.truetype(bold_path, svg_size(52))
        font_subtitle = ImageFont.truetype(reg_path,  svg_size(20))
        font_tagline  = ImageFont.truetype(bold_path, svg_size(14))
        font_node     = ImageFont.truetype(bold_path, svg_size(13))
        font_pill     = ImageFont.truetype(bold_path, svg_size(13))
    else:
        font_title = font_subtitle = font_tagline = font_node = font_pill = ImageFont.load_default()

    # ---- Content starts at SVG translate(70, 0) ----
    lx = svg_x(70)  # left margin for text content

    # ---- 5. Tagline pill (small uppercase category badge) ----
    # SVG: rect at (0,55) w=260 h=30 rx=15, text at y=75
    tagline = svg_info.get("tagline")
    if tagline:
        tag_x = lx
        tag_y = svg_y(55)
        tag_w = svg_x(260)
        tag_h = svg_size(30)
        pill_bg = interpolate_color(bg_colors[0], (30, 41, 59), 0.7)
        safe_rounded_rect(draw,
            [tag_x, tag_y, tag_x + tag_w, tag_y + tag_h],
            radius=svg_size(15),
            fill=color_with_alpha(pill_bg, 230),
            outline=color_with_alpha(accent, 180),
            width=1,
        )
        # Pulsing dot (animated opacity)
        dot_r = svg_size(5)
        dot_cx = tag_x + svg_size(16)
        dot_cy = tag_y + tag_h // 2
        dot_alpha = int(100 + 155 * (0.5 + 0.5 * math.sin(t * 2 * math.pi)))
        draw.ellipse(
            [dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r],
            fill=color_with_alpha(accent, dot_alpha),
        )
        # Tagline text
        draw.text(
            (tag_x + svg_size(30), tag_y + (tag_h - svg_size(14)) // 2),
            tagline.upper()[:30],
            font=font_tagline,
            fill=color_with_alpha(accent, 240),
        )

    # ---- 6. Title (SVG: text at y=145, class=title, gradient fill) ----
    title_text = svg_info.get("title") or "Awesome Project"
    title_y = svg_y(130)  # SVG y=145 is baseline; adjust up for ascent

    # Render title with gradient color simulation (left-to-right primary gradient)
    if len(primary_colors) >= 2:
        # Render character-by-character with gradient
        char_x = lx
        for ci, ch in enumerate(title_text):
            frac = ci / max(1, len(title_text) - 1)
            tc = interpolate_color(primary_colors[0], primary_colors[-1], frac)
            draw.text((char_x, title_y), ch, font=font_title, fill=color_with_alpha(tc, 255))
            char_x += text_width(draw, ch, font_title)
    else:
        draw.text((lx, title_y), title_text, font=font_title, fill=(255, 255, 255, 255))

    # ---- 7. Subtitle (SVG: text at y=195, class=subtitle, fill=#94a3b8) ----
    sub_text = svg_info.get("subtitle") or ""
    if sub_text:
        sub_y = svg_y(182)  # SVG y=195 baseline, adjust
        if len(sub_text) > 55:
            sub_text = sub_text[:52] + "..."
        draw.text((lx, sub_y), sub_text, font=font_subtitle, fill=(148, 163, 184, 255))

    # ---- 8. Feature pills (SVG: row of bordered rects at translate(0, 240)) ----
    # In the SVG these are at g transform translate(0,240) inside translate(70,0)
    pills = svg_info.get("feature_pills", [])[:4]
    if pills:
        pill_y = svg_y(240)
        pill_h = svg_size(38)
        pill_x = lx
        pill_border_colors = [accent, (71, 85, 105), (71, 85, 105), (71, 85, 105)]
        pill_bg_color = interpolate_color(bg_colors[0], (30, 41, 59), 0.7)

        for i, p_text in enumerate(pills):
            # Strip emoji prefix for width calculation but keep for display
            display_text = p_text
            if len(display_text) > 18:
                display_text = display_text[:16] + ".."
            pw = text_width(draw, display_text, font_pill) + svg_size(20)
            pw = max(pw, svg_size(80))

            if pill_x + pw > width - svg_size(20):
                break

            bc = pill_border_colors[i % len(pill_border_colors)]
            safe_rounded_rect(draw,
                [pill_x, pill_y, pill_x + pw, pill_y + pill_h],
                radius=svg_size(8),
                fill=color_with_alpha(pill_bg_color, 230),
                outline=color_with_alpha(bc, 180),
                width=1,
            )
            draw.text(
                (pill_x + svg_size(10), pill_y + (pill_h - svg_size(13)) // 2),
                display_text,
                font=font_pill,
                fill=(226, 232, 240, 255),
            )
            pill_x += pw + svg_size(15)

    # ---- 9. Right-side: diagram nodes with animated dashed connectors ----
    # SVG: g transform translate(920, 80)
    # Three nodes: SVG PARSER, FRAME RENDERER, GIF OUTPUT
    nodes = svg_info.get("diagram_nodes", [])[:3]
    if nodes:
        # Node box colors from SVG
        node_outline_colors = [accent, (168, 85, 247), (6, 182, 212)]
        node_bg_colors = [bg_colors[0], (30, 27, 75), bg_colors[0]]

        # SVG positions relative to translate(920, 80):
        #   Node 1: rect x=40 y=10 w=130 h=42 rx=10
        #   Path:   M 105 52 L 105 105
        #   Node 2: rect x=30 y=105 w=150 h=42 rx=10
        #   Path:   M 105 147 L 105 190
        #   Node 3: rect x=30 y=190 w=150 h=36 rx=8
        base_x = svg_x(920)
        base_y = svg_y(80)

        node_specs = [
            {"rx": 40, "ry": 10, "rw": 130, "rh": 42, "rad": 10},
            {"rx": 30, "ry": 105, "rw": 150, "rh": 42, "rad": 10},
            {"rx": 30, "ry": 190, "rw": 150, "rh": 36, "rad": 8},
        ]
        connector_paths = [
            (105, 52, 105, 105),
            (105, 147, 105, 190),
        ]

        for ni, node in enumerate(nodes):
            if ni >= len(node_specs):
                break
            spec = node_specs[ni]
            nx = base_x + svg_x(spec["rx"])
            ny = base_y + int(spec["ry"] * SY)
            nw = svg_x(spec["rw"])
            nh = int(spec["rh"] * SY)
            nc = node_outline_colors[ni % len(node_outline_colors)]
            nbg = node_bg_colors[ni % len(node_bg_colors)]

            safe_rounded_rect(draw,
                [nx, ny, nx + nw, ny + nh],
                radius=svg_size(spec["rad"]),
                fill=color_with_alpha(nbg, 230),
                outline=color_with_alpha(nc, 220),
                width=1,
            )
            label = node.get("label", "")[:18]
            tw = text_width(draw, label, font_node)
            # Center text in the node box
            draw.text(
                (nx + (nw - tw) // 2, ny + (nh - svg_size(13)) // 2),
                label,
                font=font_node,
                fill=(226, 232, 240, 255),
            )

            # Animated dashed connector to next node
            if ni < len(connector_paths):
                cp = connector_paths[ni]
                cx_line = base_x + svg_x(cp[0])
                cy_start = base_y + int(cp[1] * SY)
                cy_end = base_y + int(cp[3] * SY)
                dash_offset = int(t * 32) % 8
                for dy in range(cy_start, cy_end, 2):
                    if (dy + dash_offset) % 8 < 4:
                        draw.line(
                            [(cx_line, dy), (cx_line, dy + 1)],
                            fill=color_with_alpha(nc, 180),
                            width=1,
                        )

    # ---- 10. Animated flowing beam across the bottom (dashed gradient line) ----
    if svg_info.get("has_flowing_beams", True):
        beam_y = height - PAD_BOT - svg_size(10)
        # Keep beam within content zone
        if beam_y < height - PAD_BOT:
            dash_offset = int(t * 60) % 20
            for bx in range(svg_size(20), width - svg_size(20), 4):
                phase = (bx + dash_offset) % 20
                if phase < 10:
                    frac = bx / max(1, width)
                    bc = interpolate_color(
                        primary_colors[0] if primary_colors else (56, 189, 248),
                        primary_colors[-1] if primary_colors else (192, 132, 252),
                        frac,
                    )
                    draw.line(
                        [(bx, beam_y), (bx + 2, beam_y)],
                        fill=color_with_alpha(bc, 60),
                        width=1,
                    )

    # ---- 11. Enforce strict 50px padding (clear top and bottom) ----
    # Paint over the padding zones with the background gradient to ensure
    # absolutely no visual content leaks outside y=50..270
    for y_px in range(PAD_TOP):
        frac = y_px / height
        c = interpolate_color(bg_colors[0], bg_colors[-1], frac)
        draw.line([(0, y_px), (width, y_px)], fill=color_with_alpha(c, 255))
    for y_px in range(height - PAD_BOT, height):
        frac = y_px / height
        c = interpolate_color(bg_colors[0], bg_colors[-1], frac)
        draw.line([(0, y_px), (width, y_px)], fill=color_with_alpha(c, 255))

    # ---- 12. Convert RGBA -> RGB ----
    bg = Image.new("RGB", (width, height), bg_colors[0])
    bg.paste(img, mask=img.split()[3])
    return bg


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_social_preview(output_path, appnamefull=None, banner_svg_path=None,
                            num_frames=24, fps=12):
    if banner_svg_path is None:
        banner_svg_path = os.path.join(os.getcwd(), "assets", "banner.svg")

    svg_info = parse_banner_svg(banner_svg_path)

    # Title priority: 1) explicit arg  2) parsed from banner.svg  3) CWD folder name
    if not appnamefull:
        appnamefull = svg_info.get("title") or get_fallback_app_name()

    safe_print(f"Using App Name : '{appnamefull}'")
    safe_print(f"Subtitle       : '{svg_info.get('subtitle', '(none)')}'")
    safe_print(f"Tagline        : '{svg_info.get('tagline', '(none)')}'")
    safe_print(f"Feature pills  : {svg_info.get('feature_pills', [])}")
    safe_print(f"Primary colors : {svg_info.get('primary_colors', [])}")
    safe_print(f"Orbs           : {len(svg_info.get('orbs', []))} found")
    safe_print(f"Diagram nodes  : {len(svg_info.get('diagram_nodes', []))} found")
    safe_print()

    safe_print(f"Generating {num_frames} frames for Social Preview GIF...")
    frames = []
    for i in range(num_frames):
        frame = render_frame(i, num_frames, svg_info)
        paletted = frame.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        frames.append(paletted)

    duration_ms = int(1000 / fps)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
    )

    file_size = os.path.getsize(output_path)
    safe_print(f"Done! Saved GIF to: {output_path}")
    safe_print(f"Dimensions: {frames[0].size}")
    safe_print(f"File size: {file_size} bytes ({file_size / 1024:.2f} KB)")

    if file_size >= 1024 * 1024:
        raise ValueError(f"File size {file_size} exceeds 1MB limit!")
    if frames[0].size != (640, 320):
        raise ValueError(f"Dimensions {frames[0].size} do not match strictly 640x320!")


if __name__ == "__main__":
    banner_svg_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "assets", "banner.svg")
    out_gif = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "assets", "preview.gif")
    generate_social_preview(output_path=out_gif, banner_svg_path=banner_svg_path)
