# 🎨 generate-social-preview-gif

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node-%3E%3D16.0.0-brightgreen.svg)](https://nodejs.org/)

An automated, high-fidelity GIF generator tailored for **GitHub Social Preview images** (`640x320px`, `< 1MB`, strictly padded).

The generator parses your repository's existing `assets/banner.svg` to extract text styling, color palettes, gradients, glowing orbs, grid patterns, and diagram nodes—faithfully replicating your project's visual identity into an animated social preview GIF.

---

## ✨ Features

- 📏 **Strict Specifications**: Outputs `640x320px` GIFs with 50px top/bottom safe padding, adhering directly to GitHub Social Preview requirements.
- 🎨 **SVG Theme Matching**: Automatically extracts titles, subtitles, badge tags, feature pills, gradient stops, accent colors, grid lines, and node diagrams from `assets/banner.svg`.
- ⚡ **Extremely Lightweight**: Generates optimized outputs (typically ~180 KB using 128-color quantization), well below GitHub's 1MB limit.
- 🐍 **Python & Node.js Support**: Includes both a pixel-perfect TrueType Python script ([`scripts/generate_gif.py`](./scripts/generate_gif.py)) and a lightweight Node.js fallback ([`scripts/generate_gif.js`](./scripts/generate_gif.js)).

---

## 🚀 Quick Start

### Python (Recommended)

Requires `Pillow`:

```bash
pip install pillow
```

Run from your project root:

```bash
python path/to/generate_gif.py
```

Or specify custom input/output paths:

```bash
python path/to/generate_gif.py assets/banner.svg assets/preview.gif
```

### Node.js

Requires `canvas` and `gifencoder`:

```bash
npm install canvas gifencoder
```

Run:

```bash
node path/to/generate_gif.js [path/to/banner.svg] [path/to/preview.gif]
```

---

## ⚙️ How It Works

The generator parses `assets/banner.svg` and extracts key design parameters:

| Element | Extracted Attributes |
|---|---|
| **Title & Subtitle** | `<text class="title">`, `<text class="subtitle">`, or `<text class="desc">` |
| **Tagline & Badges** | `<text class="tagline">` / `<text class="badge-text">` |
| **Feature Pills** | `<text class="node-text">` and short text elements |
| **Color Palettes** | Background & primary gradient stops (`<linearGradient id="bg-grad">`) |
| **Grid & Effects** | `.grid-line` patterns, glowing ambient orbs (`r >= 80`), and animated data waves |

*Note: If `assets/banner.svg` is missing, the generator falls back gracefully to formatting the project's root folder name.*

---

## 📄 License

[MIT](LICENSE)
