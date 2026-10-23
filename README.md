# Hermes Agent Local Setup & Custom Extensions

A specialized configuration, custom skills, and MCP server setup for [Hermes Agent](https://github.com/NousResearch/hermes-agent) running 100% locally on Linux.

---

## 💻 Hardware & Inference Context

* **Machine**: ASUS ROG Zephyrus G14 (AMD Ryzen 9 7940HS, 8C/16T, AVX-512)
* **Memory**: 32 GB DDR5 RAM
* **GPU**: NVIDIA GeForce RTX 4060 Mobile (6 GB VRAM)
* **OS**: Arch Linux
* **Inference Backend**: [Ollama](https://ollama.com) (listening on `http://127.0.0.1:11434`)

### Configured Models
* **Primary (Deep Reasoning & Complex Extraction)**: `qwen3.8:latest` (17 GB, 27B class)
* **Secondary (Fast Agent Execution Layer)**: `nemotron-3.5-lightning:latest` (25 GB, 30B MoE with 3B active parameters per token)

---

## 📂 Repository Structure

```
Hermes_setup/
├── skills/
│   ├── laptop-manager/          # Arch Linux & ASUS G14 hardware / package management
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── health_check.sh
│   └── pdf-reader/              # Text/table extraction and Matplotlib chart generation
│       ├── SKILL.md
│       └── scripts/
│           ├── parse_pdf.py
│           └── plot_chart.py
├── mcp/
│   └── news-reader/             # Zero-dependency Hacker News, Reddit, and RSS MCP server
│       ├── README.md
│       └── server.py
└── README.md
```

---

## 🛠️ Extensions Overview

### 1. `laptop-manager` (Hermes Skill)
Tailored specifically for Arch Linux on ASUS ROG laptops.
* **Instant Health Snapshot**: Runs `scripts/health_check.sh` to report CPU/GPU temps (`sensors`), memory/swap, disk usage, pending updates, and failed services in milliseconds.
* **Package Management**: Safe checking via `checkupdates` and `yay -Qua` before executing upgrades. Alerts on pending kernel/NVIDIA dkms upgrades.
* **Hardware Profiles**: Adjusts power profiles and battery longevity limits via `asusctl`.

### 2. `news-reader` (MCP Server)
A standalone Python Model Context Protocol (MCP) server running via stdio with zero external runtime dependencies.
* `get_hacker_news`: Fetches top, best, or new discussions with scores, authors, and comment links.
* `get_reddit_posts`: Fetches trending discussions from any subreddit (e.g. `r/archlinux`, `r/localllama`, `r/technology`) without API keys.
* `read_rss_feed`: Parses and summarizes any custom RSS or Atom feed URL into structured markdown.

### 3. `pdf-reader` (Hermes Skill)
Full multimodal extraction and graph visualization pipeline.
* **Text & Table Extraction**: Uses `pymupdf` to extract clean Markdown text and tables.
* **Embedded Graphics**: Extracts all embedded figures and images to `/tmp/pdf_extracted/images/`.
* **Chart Generation**: Uses `matplotlib` (`scripts/plot_chart.py`) to render bar charts, line trends, or pie plots from extracted numerical data.
* **Structural Flowcharts**: Prompts the agent to generate native Mermaid diagrams for architectural workflows.

---

## 🚀 Installation & Setup

### Prerequisites
In your Python environment or Hermes venv, install the required packages:
```bash
pip install mcp pymupdf matplotlib
```

### Install the Skills
Copy the skills to your local Hermes configuration directory:
```bash
cp -r skills/laptop-manager ~/.hermes/skills/
cp -r skills/pdf-reader ~/.hermes/skills/
chmod +x ~/.hermes/skills/laptop-manager/scripts/health_check.sh
chmod +x ~/.hermes/skills/pdf-reader/scripts/*.py
```

### Register the MCP Server
Add the `news-reader` MCP server to Hermes:
```bash
hermes mcp add news-reader --command python3 --args $(pwd)/mcp/news-reader/server.py
```
Or add to `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  news-reader:
    command: python3
    args:
    - /path/to/Hermes_setup/mcp/news-reader/server.py
    enabled: true
```

---

## 📝 Example Commands

* **Laptop Status**:
  ```bash
  hermes "Check my laptop temperatures, battery level, and see if there are any pending updates."
  ```

* **News & Social Digest**:
  ```bash
  hermes "What are the top 5 discussions on Hacker News and r/archlinux today?"
  ```

* **PDF & Graph Visualization**:
  ```bash
  hermes "Extract text and tables from document.pdf, summarize it, and generate a comparison chart of the results."
  ```

---

## License
MIT
