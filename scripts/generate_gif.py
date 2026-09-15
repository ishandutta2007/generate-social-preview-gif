#!/usr/bin/env python3
"""
Generate Social Preview GIF for Awesome-My-App
Strict specifications:
- GIF format with dynamic animations mirroring assets/banner.svg
- Dimensions: exactly 640x320 px
- Size: strictly under 1 MB
- Vertical padding: strictly 50px on top and 50px on bottom (all content between y=50 and y=270)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def interpolate_color(c1, c2, factor):
    return tuple(int(a + (b - a) * factor) for a, b in zip(c1, c2))

def get_accent_color(t):
    # Gradient: #ff5e62 (255, 94, 98) -> #ff9966 (255, 153, 102) -> #4facfe (79, 172, 254)
    c1 = (255, 94, 98)
    c2 = (255, 153, 102)
    c3 = (79, 172, 254)
    if t < 0.5:
        return interpolate_color(c1, c2, t / 0.5)
    else:
        return interpolate_color(c2, c3, (t - 0.5) / 0.5)

def render_frame(frame_idx, total_frames, appname1, appname2, svg_info=None, width=640, height=320):
    t = frame_idx / total_frames
    if svg_info is None:
        svg_info = {}
    
    # 1. Base Image - Dark GitHub background #0d1117
    img = Image.new("RGBA", (width, height), (13, 17, 23, 255))
    draw = ImageDraw.Draw(img)
    
    # Content Area: y from 50 to 270 (Strict 50px top and bottom padding)
    card_x1, card_y1, card_x2, card_y2 = 18, 50, width - 18, 270
    
    # Draw Inner Card with subtle gradient / rounded rectangle
    card_bg = (22, 27, 34, 255) # #161b22
    border_color = (48, 54, 61, 255) # #30363d
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=10, fill=card_bg, outline=border_color, width=2)
    
    # 2. Shield Icon (Matches assets/banner.svg)
    shield_cx = 58
    shield_cy = 100
    
    # Shield polygon points scaled & translated
    # Banner: M40 10 L75 25 V60 C75 90 40 110 40 110 C40 110 5 90 5 60 V25 Z
    # Local coords approx: top (0, -25), top-right (20, -16), mid-right (20, 5), bottom (0, 28), mid-left (-20, 5), top-left (-20, -16)
    pts = [
        (shield_cx, shield_cy - 24),
        (shield_cx + 18, shield_cy - 15),
        (shield_cx + 18, shield_cy + 6),
        (shield_cx, shield_cy + 25),
        (shield_cx - 18, shield_cy + 6),
        (shield_cx - 18, shield_cy - 15)
    ]
    # Draw shield gradient outline
    draw.polygon(pts, outline=(255, 120, 90, 255), fill=(28, 33, 40, 255), width=3)
    # Shield cross: vertical and horizontal lines
    draw.line([(shield_cx, shield_cy - 12), (shield_cx, shield_cy + 13)], fill=(255, 153, 102, 255), width=3)
    draw.line([(shield_cx - 10, shield_cy - 1), (shield_cx + 10, shield_cy - 1)], fill=(255, 153, 102, 255), width=3)
    
    # 3. Typography
    font_title = None
    font_subtitle = None
    font_desc = None
    font_badge = None
    
    # Try finding system fonts (Segoe UI, Arial, etc.)
    font_paths = [
        (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf"),
        (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf"),
        ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf")
    ]
    for bold_p, reg_p in font_paths:
        if os.path.exists(bold_p) and os.path.exists(reg_p):
            try:
                font_title = ImageFont.truetype(bold_p, 23)
                font_subtitle = ImageFont.truetype(bold_p, 14)
                font_desc = ImageFont.truetype(reg_p, 11)
                font_badge = ImageFont.truetype(bold_p, 10)
                break
            except Exception:
                pass
                
    if font_title is None:
        font_title = font_subtitle = font_desc = font_badge = ImageFont.load_default()
    
    text_x = 95
    # Title (first line)
    draw.text((text_x, 72), appname1, font=font_title, fill=(255, 255, 255, 255))
    
    # Title (second line)
    draw.text((text_x, 104), appname2, font=font_subtitle, fill=(88, 166, 255, 255))
    
    # Subtitle / Description extracted from banner.svg if available
    subtitle_text = svg_info.get("subtitle") or "Curated SaaS Platforms, Risk Analysis Frameworks & Open-Source Tools"
    draw.text((text_x, 128), subtitle_text, font=font_desc, fill=(139, 148, 158, 255))
    
    # 4. Badges (y = 152 to 174)
    parsed_badges = svg_info.get("badges", [])
    if parsed_badges:
        badge_colors = [(126, 231, 135), (121, 192, 255), (255, 166, 87)]
        badges = [(b, badge_colors[idx % len(badge_colors)]) for idx, b in enumerate(parsed_badges[:3])]
    else:
        badges = [
            ("OSHA PSM 1910.119", (126, 231, 135)), # Green
            ("HAZOP / PHA / QRA", (121, 192, 255)),  # Blue
            ("EHS & Seveso III", (255, 166, 87)),   # Orange
        ]
        
    bx = text_x
    by = 152
    for label, col in badges:
        bw = len(label) * 6 + 18
        draw.rounded_rectangle([bx, by, bx + bw, by + 18], radius=9, fill=(33, 38, 45, 255), outline=col, width=1)
        draw.text((bx + 8, by + 3), label, font=font_badge, fill=col)
        bx += bw + 10
        
    # 5. Dynamic Wave with oscillation (y around 212)
    wave_start_x = 35
    wave_end_x = width - 35
    wave_base_y = 212
    amp = 11
    if svg_info.get("wave_values"):
        amp = 15 # Adjust amplitude slightly if custom animated wave detected
    
    wave_pts = []
    num_steps = 120
    for i in range(num_steps + 1):
        frac = i / num_steps
        wx = wave_start_x + frac * (wave_end_x - wave_start_x)
        wy = wave_base_y + amp * math.sin(frac * 3.5 * math.pi + t * 2 * math.pi)
        wave_pts.append((wx, wy))
        
    # Draw wave segments with gradient colors
    for i in range(len(wave_pts) - 1):
        frac = i / (len(wave_pts) - 1)
        col = get_accent_color(frac)
        draw.line([wave_pts[i], wave_pts[i + 1]], fill=col, width=3)
        
    # 6. Pulsing dynamic dot traveling across the wave
    dot_frac = 0.5 * (1.0 - math.cos(t * 2 * math.pi))
    dot_x = wave_start_x + dot_frac * (wave_end_x - wave_start_x)
    dot_y = wave_base_y + amp * math.sin(dot_frac * 3.5 * math.pi + t * 2 * math.pi)
    
    # Glow circle
    dot_color = (255, 94, 98, 255) # #ff5e62
    glow_radius = 7
    draw.ellipse([dot_x - glow_radius, dot_y - glow_radius, dot_x + glow_radius, dot_y + glow_radius], 
                 fill=(255, 120, 100, 100))
    draw.ellipse([dot_x - 4, dot_y - 4, dot_x + 4, dot_y + 4], fill=dot_color)
    
    # 7. Verification: Strict padding bounds
    # Ensure y=0..49 and y=271..319 remain clean background
    draw.rectangle([0, 0, width, 49], fill=(13, 17, 23, 255))
    draw.rectangle([0, 271, width, height], fill=(13, 17, 23, 255))
    
    # Convert RGBA to RGB with dark background
    bg = Image.new("RGB", (width, height), (13, 17, 23))
    bg.paste(img, mask=img.split()[3])
    
    return bg

def parse_banner_svg(svg_path):
    """
    Parses assets/banner.svg to extract appnamefull, description/subtitle,
    badges/tags, and animation details if present.
    """
    info = {
        "appnamefull": None,
        "subtitle": None,
        "badges": [],
        "wave_values": None
    }
    if not os.path.exists(svg_path):
        return info

    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Helper to recursively extract text elements and classes/styles
        texts = []
        for elem in root.iter():
            tag = elem.tag.split('}')[-1]
            if tag == 'text':
                cls = elem.attrib.get('class', '')
                t_content = "".join(elem.itertext()).strip()
                if t_content:
                    texts.append((cls, t_content))
            elif tag == 'animate':
                attr = elem.attrib.get('attributeName', '')
                vals = elem.attrib.get('values', '')
                if attr == 'd' and 'Q' in vals:
                    info['wave_values'] = vals

        # Extract appnamefull from title text element or first main header text element
        title_texts = [t for cls, t in texts if 'title' in cls]
        if title_texts:
            info['appnamefull'] = title_texts[0]
        else:
            # Fallback: largest or first prominent text in SVG
            if texts:
                info['appnamefull'] = texts[0][1]

        # Subtitle / description extraction
        sub_texts = [t for cls, t in texts if 'subtitle' in cls or 'desc' in cls or 'tagline' in cls]
        if sub_texts:
            info['subtitle'] = sub_texts[0]

        # Badges / feature pills extraction
        badge_texts = [t for cls, t in texts if 'badge' in cls or 'node' in cls or 'pill' in cls]
        if badge_texts:
            info['badges'] = badge_texts
    except Exception as e:
        print(f"Warning: Failed to parse SVG metadata from {svg_path}: {e}")

    return info

def split_sentence_balanced(sentence):
    words = sentence.split()
    if not words:
        return "", ""
    
    mid = (len(words) + 1) // 2
    first_half = " ".join(words[:mid])
    second_half = " ".join(words[mid:])
    
    return first_half, second_half

def generate_social_preview(output_path, appnamefull=None, banner_svg_path=None, num_frames=24, fps=12):
    if banner_svg_path is None:
        # Default destination banner path: root of destination repo / working directory
        banner_svg_path = os.path.join(os.getcwd(), "assets", "banner.svg")

    svg_info = parse_banner_svg(banner_svg_path)
    
    # Priority: explicit argument -> parsed from banner.svg -> fallback default
    if not appnamefull:
        if svg_info["appnamefull"]:
            appnamefull = svg_info["appnamefull"]
        else:
            appnamefull = "Awesome Project"

    print(f"Using App Name: '{appnamefull}'")
    print(f"Generating {num_frames} frames for Social Preview GIF...")
    appname1, appname2 = split_sentence_balanced(appnamefull)
    frames = []
    for i in range(num_frames):
        frame = render_frame(i, num_frames, appname1, appname2, svg_info=svg_info)
        # Quantize to 128 colors for high quality, small file size
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
        optimize=True
    )
    
    file_size = os.path.getsize(output_path)
    print(f"Done! Saved GIF to: {output_path}")
    print(f"Dimensions: {frames[0].size}")
    print(f"File size: {file_size} bytes ({file_size / 1024:.2f} KB)")
    
    if file_size >= 1024 * 1024:
        raise ValueError(f"File size {file_size} exceeds 1MB limit!")
    if frames[0].size != (640, 320):
        raise ValueError(f"Dimensions {frames[0].size} do not match strictly 640x320!")

if __name__ == "__main__":
    import sys
    
    # Allow optional CLI arguments: python generate_gif.py [banner_svg_path] [output_gif_path]
    banner_svg_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "assets", "banner.svg")
    out_gif = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "assets", "preview.gif")
    
    generate_social_preview(output_path=out_gif, banner_svg_path=banner_svg_path)

