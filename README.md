<p align="center">
  <a href="https://github.com/ishandutta2007/generate-social-preview-gif">
    <img src="./assets/banner.svg" alt="Social Preview GIF Generator Banner" width="100%">
  </a>
</p>

# 🎨 Animated GitHub Social Preview GIF Generator & Creative Automation Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node-%3E%3D16.0.0-brightgreen.svg)](https://nodejs.org/)

An automated, high-fidelity **GitHub Social Preview GIF Generator** (`640x320px`, `< 1MB`, strictly padded). This developer tool parses repository banner files (`assets/banner.svg`) to extract design parameters—typography, color palettes, gradients, glowing orbs, grid patterns, and diagram nodes—replicating your project's brand identity into an animated Open Graph preview GIF.

---

## ✨ Key Features & Capabilities

- 📏 **GitHub Open Graph Spec Compliance**: Produces `640x320px` GIFs with 50px top/bottom safe padding to ensure perfect framing on GitHub, Twitter, and LinkedIn.
- 🎨 **Automated SVG Theme Extraction**: Parses SVG elements like `<text class="title">`, `<linearGradient id="bg-grad">`, glowing `<circle>` orbs, and node labels.
- ⚡ **Ultra-Optimized File Size**: Generates quantized 128-color GIFs (typically ~180 KB), far below GitHub's strict 1 MB file size limit.
- 🐍 **Dual Engine Support**: Includes both a pixel-perfect TrueType Python generator ([`scripts/generate_gif.py`](./scripts/generate_gif.py)) and a lightweight Node.js fallback ([`scripts/generate_gif.js`](./scripts/generate_gif.js)).

---

## 🚀 Quick Start Guide

### Python Engine (Recommended)

Install dependencies:

```bash
pip install pillow
```

Generate preview GIF from repository root:

```bash
python scripts/generate_gif.py assets/banner.svg assets/preview.gif
```

### Node.js Engine

Install dependencies:

```bash
npm install canvas gifencoder
```

Run generator:

```bash
node scripts/generate_gif.js assets/banner.svg assets/preview.gif
```

---

## 📊 Market Overview & SaaS Landscape

> **Market Analysis**: The global Banner & Social Preview Creative Automation market is estimated at **~$450 Million (2026)** and projected to exceed **$1.2 Billion by 2030**. The sector is currently **moderately fragmented**, balancing massive design platforms with specialized API automation services.

### SaaS Product Comparison (Sorted by Company Size / Valuation)

| Product / Platform | Company Size (Valuation / Revenue) | Starting Price Tier | Free Tier / Trial Limits |
| :--- | :--- | :--- | :--- |
| **Canva** | $32.0 Billion Valuation / $2.5B ARR | $18.00 / month | **Free Forever Plan**: 5GB Cloud Storage, 1M+ free templates & design assets |
| **Screen Studio** | ~$15.0 Million Valuation (Estimated) | $29.00 / month ($9/mo billed annually) | **Free Trial**: Watermarked Video/GIF Export, full editor access |
| **Bannerbear** | ~$10.0 Million Valuation / $1.2M ARR | $49.00 / month | **Free Trial**: 30 API Credits total (No credit card required) |
| **Placid App** | Bootstrapped / Business Tier | $19.00 / month | **Free Trial**: Unlimited watermarked preview generation |
| **Bannerify** | Bootstrapped / Figma Plugin Ecosystem | $39.00 / month | **Free Trial**: 10 Free Exports via Figma Plugin |
| **PlayPlay** | $32.0 Million Total Funding | $160.00 / month | **Free Trial**: 7 Days full feature access (Enterprise template trial) |

---

## 💻 Top Open-Source Image & GIF Processing Libraries

Below are the leading open-source projects for programmatic GIF animation and media processing, ranked by GitHub star popularity:

| Open-Source Tool | GitHub Star Count | Primary Use Case & Language |
| :--- | :--- | :--- |
| [**FFmpeg**](https://github.com/FFmpeg/FFmpeg) | [![FFmpeg Stars](https://img.shields.io/github/stars/FFmpeg/FFmpeg?style=social&color=white)](https://github.com/FFmpeg/FFmpeg/stargazers) | Universal multimedia encoder, GIF palette generation & video conversion (C) |
| [**ImageMagick**](https://github.com/ImageMagick/ImageMagick) | [![ImageMagick Stars](https://img.shields.io/github/stars/ImageMagick/ImageMagick?style=social&color=white)](https://github.com/ImageMagick/ImageMagick/stargazers) | Command-line image manipulation & animated GIF assembly (C) |
| [**Pillow**](https://github.com/python-pillow/Pillow) | [![Pillow Stars](https://img.shields.io/github/stars/python-pillow/Pillow?style=social&color=white)](https://github.com/python-pillow/Pillow/stargazers) | Python Imaging Library for pixel-perfect TrueType font rendering & frame quantization (Python) |
| [**node-canvas**](https://github.com/Automattic/node-canvas) | [![node-canvas Stars](https://img.shields.io/github/stars/Automattic/node-canvas?style=social&color=white)](https://github.com/Automattic/node-canvas/stargazers) | Cairo-backed HTML5 Canvas implementation for Node.js graphics generation (JavaScript/C++) |
| [**Gifsicle**](https://github.com/kohler/gifsicle) | [![Gifsicle Stars](https://img.shields.io/github/stars/kohler/gifsicle?style=social&color=white)](https://github.com/kohler/gifsicle/stargazers) | Command-line GIF animation editing, color reduction & frame optimization (C) |
| [**libcaca**](https://github.com/cacalabs/libcaca) | [![libcaca Stars](https://img.shields.io/github/stars/cacalabs/libcaca?style=social&color=white)](https://github.com/cacalabs/libcaca/stargazers) | Color ASCII graphics renderer and terminal GIF/image preview tool (C) |

---

## ⚙️ SVG Parsing Specification

The generator extracts design tokens from SVG files based on the following mapping:

| Target Element | SVG Selector / Class | Extracted Design Attribute |
| :--- | :--- | :--- |
| **Title Text** | `<text class="title">` or `"Awesome..."` text | Headline font style & positioning |
| **Subtitle** | `<text class="subtitle">` or `<text class="desc">` | Secondary description styling |
| **Badge / Tag** | `<text class="tagline">` / `<text class="badge-text">` | Top highlight pill label |
| **Diagram Nodes** | `<text class="node-text">` | Feature tags and technology pills |
| **Background Colors**| `<linearGradient id="bg-grad">` | Start & end gradient stop colors |
| **Primary Theme** | `<linearGradient id="primary-grad">` | Accent highlight gradient stop colors |
| **Orbs & Grid** | `<circle r=">=80">`, `.grid-line` | Ambient background glow & grid line patterns |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
