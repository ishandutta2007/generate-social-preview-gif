---
name: generate-social-preview-gif
description: >-
  Generates an animated GIF tailored for GitHub Social Preview images (640x320px, strictly under 1MB, with 50px top and bottom padding).
  The generator parses the destination project's assets/banner.svg to extract title, subtitle, tagline, feature pills,
  colors, gradients, glowing orbs, grid patterns, and diagram nodes — then faithfully replicates them as an animated GIF.
  Use this skill whenever generating or updating a social preview GIF banner for a repository.
---

# Generate Social Preview GIF Skill

This skill provides an automated generator to create lightweight, high-fidelity animated GIFs formatted for GitHub repository Social Previews. The GIF **mirrors the visual language** of the destination project's `assets/banner.svg`.

## How It Works

The generator deeply parses `assets/banner.svg` from the destination project to extract:

| Element               | What is extracted                                           |
|-----------------------|-------------------------------------------------------------|
| **Title**             | `<text class="title">` or text containing "Awesome"        |
| **Subtitle**          | `<text class="subtitle">` or `<text class="desc">`         |
| **Tagline**           | `<text class="tagline">` / `<text class="badge-text">`     |
| **Feature pills**     | `<text class="node-text">` and short text elements          |
| **Background colors** | `<linearGradient id="bg-grad">` stop colors                |
| **Primary colors**    | `<linearGradient id="primary-grad">` stop colors            |
| **Accent color**      | First non-dark stroke hex color found                       |
| **Grid lines**        | Presence of `.grid-line` class or `<pattern id="grid">`     |
| **Glowing orbs**      | `<circle>` with `r >= 80` and low opacity                   |
| **Diagram nodes**     | Uppercase text elements as node labels                      |
| **Animated elements** | `stroke-dasharray`, flowing beams, animated `<animate>` tags |

If `assets/banner.svg` is missing, the title falls back to the **folder name** of the current working directory (e.g. `awesome-my-project` → `Awesome My Project`).

## Specifications

- **Dimensions**: Exactly 640px (width) × 320px (height).
- **Padding**: Strictly 50px top and bottom padding (all visual content contained between `y = 50` and `y = 270`).
- **File Size**: Guaranteed strictly < 1 MB (typically ~180 KB using optimized 128-color quantization).
- **Dynamic Behavior**: Animated glowing orbs, flowing data wave, pulsing dot, dashed beam line, and bar chart visualization.
- **Output Location**: `assets/preview.gif`

## Generator Scripts

- **Python (Recommended for pixel-perfect TrueType typography & anti-aliased rendering)**:
  [generate_gif.py](./scripts/generate_gif.py)
- **Node.js (Alternative lightweight fallback)**:
  [generate_gif.js](./scripts/generate_gif.js)

## Usage

The generator automatically reads `assets/banner.svg` from the current working directory.

```bash
# From the destination project root:
python path/to/generate_gif.py

# Or with explicit paths:
python path/to/generate_gif.py [path/to/assets/banner.svg] [path/to/assets/preview.gif]
```
