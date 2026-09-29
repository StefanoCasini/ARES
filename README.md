# A.R.E.S. (Automated Reconnaissance & Enumeration System)

> **A Modular Framework for Hybrid Network Discovery and Data Fusion**

**A.R.E.S.** is a Python-based orchestration tool that automates the reconnaissance phase of a Network Penetration Test. It uses the **Strategy Pattern** to combine the speed of volumetric scanners (Masscan), the precision of service enumerators (Nmap) and the stealth of passive intelligence (Smap) into a single, unified workflow.

The core of A.R.E.S. is its **Data Fusion Engine**: it parses heterogeneous outputs (XML, JSON), normalizes them into typed **DTOs**, and merges them into one JSON report per scan. Every port, hostname and CPE in the report is traced back to the command that found it. The report can be read by a person or ingested by other tools.

A.R.E.S. can be driven from the **command line** or from a **Web UI** (FastAPI + React). The Web UI lets you edit the configuration, start and monitor scans, and explore results as a table or as an interactive network graph.

---

## Disclaimer

> **This tool is intended for legal security auditing and educational purposes only.**
>
> The developers assume no liability and are not responsible for any misuse or damage caused by this program. **Always obtain proper authorization before scanning a network.**

---

## Table of Contents
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage (CLI)](#usage-cli)
- [Web Interface](#web-interface)
- [Configuration](#configuration)
- [Configuration Examples](#configuration-examples)
- [Output](#output)
- [DTOs](#dtos)
- [Architecture & Extensibility](#architecture--extensibility)
- [How to Extend (Add a New Tool)](#how-to-extend-add-a-new-tool)
- [Running the Tests](#running-the-tests)
- [Known Limitations](#known-limitations)
- [Legal & Attribution](#legal--attribution)

---

## Key Features
- **Hybrid Scanning:** runs active (Nmap, Masscan) and passive (Smap) tools concurrently.
- **Unified Data Model:** normalizes the output of every tool into typed DTOs and a single JSON report.
- **Source Traceability:** every finding records the command that produced it.
- **Parallel Execution:** a thread pool with a configurable number of workers, plus a live progress table in the terminal.
- **Import Mode:** re-parse and merge raw output files from earlier scans without scanning again.
- **Web UI:** a configuration editor, a live scan monitor, and a results viewer with an interactive network graph.
- **Modular Architecture:** built on the Strategy Pattern, so a new tool only needs a generator and a parser.
- **Declarative Configuration:** everything is controlled from a single YAML file.

---

## How It Works

```plaintext
config.yml ──► Generators ──► Launcher (thread pool) ──► raw files ──┐
                                                                    ├──► Parsers ──► Merger ──► JSON report
                                       import_files (optional) ─────┘
```

1. **Generate:** for each enabled `launcher_<tool>`, its generator builds one command per enabled mode.
2. **Launch:** the commands run in parallel (`n_threads` workers). Raw output goes to `output/raw/<timestamp>_<target>/`. JSON outputs are wrapped as `{"command": ..., "data": ...}` so the originating command is kept.
3. **Parse:** each file is routed to the parser whose `can_handle()` accepts it and is converted into a `ParsedDataDTO`.
4. **Merge:** all `ParsedDataDTO`s are fused per IP into a `FinalReportDTO`. Hosts are sorted by IP.
5. **Report:** the report is saved as `output/<timestamp>_<target>.json`.

---

## Installation

### Prerequisites
* **Python 3.9+**
* **Nmap**: must be in your `PATH`
* **Masscan**: must be in your `PATH` (needs root for raw sockets)
* **Smap**: must be in your `PATH` (passive; it queries Shodan's InternetDB, so it needs Internet access but no root)
* **Node.js 18+ and npm**: only needed for the Web UI

Any tool can be turned off in `config.yml`. You only need the ones you enable.

### Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/StefanoCasini/ARES.git
    cd ARES
    ```

2.  **Create a virtual environment and install the Python dependencies:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **(Optional) Install the Web UI dependencies:**
    ```bash
    cd ui && npm install && cd ..
    ```

---

## Usage (CLI)

Run A.R.E.S. from the repository root. The target can be passed on the command line, which overrides `mode.target` in the config file:

```bash
sudo .venv/bin/python ares.py 192.168.1.0/24
```

| Argument | Description |
| :--- | :--- |
| `target` *(optional)* | Target IP or CIDR. If omitted, `mode.target` from the config file is used. |
| `--config <path>` | Path to the configuration file (default: `config.yml`). |

> **Note:** Masscan, and Nmap SYN/UDP/OS scans, use raw sockets and need root. The generated Nmap and Masscan commands are already prefixed with `sudo`. When A.R.E.S. itself runs under `sudo`, output files are `chown`ed back to your user, so you don't end up with root-owned reports. Use the venv interpreter (`.venv/bin/python`), because a plain `sudo python` does not see the venv packages.

While the scans run, a live table in the terminal shows each task's status (`Ready` → `Running` → `Done`/`Error`) and duration.

---

## Web Interface

The Web UI has two parts:
- **Backend:** FastAPI (`api/main.py`) on port `8000`.
- **Frontend:** React + Vite + Tailwind (`ui/`) on port `5173`.

Start both with the helper script. It expects the virtual environment at `.venv/`:

```bash
./start_ui.sh
```

Then open **http://localhost:5173**. Press `Ctrl+C` to stop both servers.

**Features:**
- **Scanner Dashboard:**
  - **Configuration Editor:** edit `config.yml` (target, threads, tools, modes, flags) and save it. Comments and formatting in the YAML file are kept.
  - **Scan Monitor:** start a scan and follow each task's state (`QUEUED` / `RUNNING` / `DONE` / `ERROR`). The page polls for updates every 2 seconds.
- **Results Viewer:** browse every report in `output/`, newest first. Each report has two views:
  - **Structured view:** the report laid out as data.
  - **Graph view:** an interactive network graph. Click a host to open a details panel with its ports, OS, CPEs and discovery commands.

> **Note:** a scan started from the UI runs inside the backend process, and it uses the `mode.target` saved in `config.yml`. Because the generated commands call `sudo`, make sure `sudo` won't stop to ask for a password: run `sudo -v` just before starting, or start the backend as root.

### REST API

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/config` | Return the current `config.yml`. |
| `POST` | `/api/config` | Merge the JSON body into `config.yml` and save it. |
| `POST` | `/api/scan/start` | Start a scan in the background with the saved config. |
| `GET` | `/api/scan/status` | Return `is_running` and the list of tasks with their status. |
| `GET` | `/api/results` | List the report files in `output/`, newest first. |
| `GET` | `/api/results/{filename}` | Return the content of one report. |

---

## Configuration

A.R.E.S. is driven by `config.yml` (use `--config` to point to another file).

### Structure Overview

```yaml
output_report_path: "output"          # where the merged JSON reports are written

mode:
  enable_scan: true                   # false = skip scanning, only parse `import_files`
  target: "192.168.1.0/24"            # overridden by the CLI argument
  n_threads: 3                        # number of commands executed in parallel
  base_output_raw_path: "output/raw"  # raw tool outputs go to <this>/<timestamp>_<target>/

  launcher_nmap:
    enabled: true                     # enable/disable the whole tool
    modes:                            # every enabled mode = one command = one task
      - name: toptcpport
        enable: true
        description: "Top TCP ports scan"
        flags: "-sS --top-ports"
        top_ports: 100                # optional, replaces the bare --top-ports (default 100)
        outputpath: "nmap_top_tcp_ports.xml"
        custom_option: ""
    flags:                            # extra global flags for the tool (see below)
      - name: timing
        enable: true
        description: "Set timing template <0-5>"
        flags: "-T4"

  launcher_masscan:
    enabled: true
    modes: [ ... ]
    flags: [ ... ]

  launcher_smap:
    enabled: true
    modes: [ ... ]

import_files:                         # optional, raw files to parse and merge together
  - "output/raw/2026-04-14_0954_192.168.1.0_24/nmap_hostonly.xml"
```

### Mode keys

| Key | Description |
| :--- | :--- |
| `name` | Identifier of the mode (the Web UI also uses it to merge edits). |
| `enable` | Whether the mode runs. |
| `description` | Free text. |
| `flags` | Flags passed to the tool. A bare `--top-ports` is expanded to `--top-ports <top_ports>`. |
| `top_ports` | *(optional)* Number of top ports used to expand `--top-ports`. Default: `100`. |
| `outputpath` | File name of the raw output, created inside the scan folder. **Keep the tool name in the file name** (e.g. `nmap_*.xml`, `masscan_*.json`, `smap_*.json`), because the parsers use it to detect the file type. |
| `custom_option` | Reserved for future use. |

The output format flag (`-oX` for Nmap, `-oJ` for Masscan/Smap) and the target are added automatically. Don't put them in `flags`.

### Import mode
Set `enable_scan: false` and list raw files under `import_files` to rebuild a report from earlier scans without running any tool. You can also leave scanning on: imported files are then merged with the new results.

---

## Configuration Examples

### Scenario A: Fast Discovery
**Masscan** is used for high-speed volumetric scanning of the top 100 TCP ports. Masscan is fast but noisy. Lower `--rate` if you need to stay under IDS/firewall thresholds.

```yaml
  launcher_masscan:
    enabled: true
    modes:
      - name: top-ports
        enable: true
        description: "LOUD: Rapidly find live hosts on top 100 ports"
        flags: "--top-ports --rate 5000"
        outputpath: "masscan_top_ports.json"
        custom_option: ""
    flags:
      - name: wait-time
        enable: true
        description: "Seconds to wait for responses after scan finishes"
        flags: "--wait 10"
```

### Scenario B: Deep Enumeration
This profile focuses on service versions, OS detection and default scripts. It uses **Nmap** with `-A`.

```yaml
  launcher_nmap:
    enabled: true
    modes:
      - name: aggressive
        enable: true
        description: "Full scan (LOUD)"
        flags: "-A -T4"
        outputpath: "nmap_full_scan.xml"
        custom_option: ""
```

### Scenario C: Passive Only (no packets sent to the target)
Only **Smap** is enabled. It gets open ports, services and CPEs from Shodan's InternetDB, so it only works for **public** IPs.

```yaml
  launcher_nmap:
    enabled: false
  launcher_masscan:
    enabled: false
  launcher_smap:
    enabled: true
    modes:
      - name: full-port-scan
        enable: true
        description: "full port scan"
        flags: "-p1-65535"
        outputpath: "smap_full_port.json"
        custom_option: ""
```

---

## Output

```plaintext
output/
├── 2026-04-14_0954_192.168.1.0_24.json      # merged report (FinalReportDTO)
└── raw/
    └── 2026-04-14_0954_192.168.1.0_24/      # one folder per scan
        ├── nmap_hostonly.xml
        ├── masscan_top_ports.json           # wrapped: {"command": ..., "data": ...}
        └── smap_full_port.json
```

### Report structure

```json
{
  "total_hosts": 1,
  "commands": ["sudo nmap -sS --top-ports 100 -oX ... 192.168.1.0/24", "..."],
  "hosts": {
    "192.168.1.10": {
      "ip": "192.168.1.10",
      "discovery_commands": ["..."],
      "hostnames": { "router.lan": ["<command that found it>"] },
      "os": [],
      "cpes": { "cpe:/a:openbsd:openssh": ["<command>"] },
      "ports": {
        "22/tcp": [
          {
            "port": "22/tcp",
            "port_type": "unknown",
            "state": "open",
            "banner": "OpenSSH 9.6",
            "service": "ssh",
            "source": "nmap",
            "ttl": null,
            "reason": "syn-ack",
            "cpes": [],
            "command": "<command>"
          }
        ]
      }
    }
  }
}
```

Each port holds a **list** of entries, one for each tool/command that reported it. Conflicting results are kept side by side instead of being overwritten.

---

## DTOs

A.R.E.S. uses **Data Transfer Objects** (Python `dataclasses`, in `module/dtos/`) as the internal data model between parsers, merger and report generation. This keeps the data flow explicit and typed instead of passing unstructured dictionaries.

| DTO | Fields | Role |
| :--- | :--- | :--- |
| `ParsedDataDTO` | `tool_name`, `command`, `data: Dict[ip, HostDTO]` | The output of one parser for one file. |
| `HostDTO` | `ip`, `ports`, `hostnames`, `os`, `cpes`, `discovery_commands` | Everything known about one host. |
| `PortDTO` | `port`, `state`, `banner`, `service`, `source`, `ttl`, `reason`, `cpes`, `port_type` *(default `"unknown"`)*, `command` *(default `"unknown"`)* | One observation of one port. |
| `OsDTO` | `name`, `command`, `cpes` | One OS guess. |
| `FinalReportDTO` | `total_hosts`, `commands`, `hosts: Dict[ip, HostDTO]` | The merged report. `to_dict()` gives the JSON. |

In a `ParsedDataDTO`, `HostDTO.ports` maps each `"port/proto"` key to a single `PortDTO`. After merging, each key maps to a `List[PortDTO]`.

### Example DTO flow

```python
from module.dtos.HostDTO import HostDTO
from module.dtos.ParsedDataDTO import ParsedDataDTO
from module.dtos.PortDTO import PortDTO

host = HostDTO(ip="192.168.1.10")
host.ports["22/tcp"] = PortDTO(
    port="22/tcp",
    state="open",
    banner="OpenSSH",
    service="ssh",
    source="nmap",
    ttl=None,
    reason=None,
    cpes=[],
    command="nmap -sV 192.168.1.10",
)

result = ParsedDataDTO(
    tool_name="nmap",
    command="nmap -sV 192.168.1.10",
    data={"192.168.1.10": host},
)
```

---

## Architecture & Extensibility

The core logic is decoupled from specific tools through the **Strategy Pattern**. There are two interfaces:

1.  **Command Generators** (`module/base_generator.py` → `CommandGenerator`): build the command lines for a tool from its config section.
2.  **Parsers** (`module/base_parser.py` → `BaseParser`): recognize a tool's raw output file (`can_handle`) and convert it into a `ParsedDataDTO` (`parse`).

The orchestration lives in:
- `module/launcher.py`: `GENERATOR_REGISTRY`, the output folder, and parallel execution.
- `module/parser.py`: `PARSER_REGISTRY` and routing each file to the right parser.
- `module/merger.py`: fusing all `ParsedDataDTO`s into a `FinalReportDTO`.

### Directory Structure

```plaintext
ARES/
├── ares.py                  # CLI entry point + core pipeline
├── config.yml               # scan configuration
├── start_ui.sh              # starts backend + frontend
├── requirements.txt
├── pytest.ini
├── api/
│   ├── main.py              # FastAPI backend (config, scan, results endpoints)
│   └── state.py             # shared scan state (used by launcher and API)
├── module/
│   ├── base_generator.py
│   ├── base_parser.py
│   ├── launcher.py
│   ├── parser.py
│   ├── merger.py
│   ├── dtos/
│   │   ├── FinalReportDTO.py
│   │   ├── HostDTO.py
│   │   ├── OsDTO.py
│   │   ├── ParsedDataDTO.py
│   │   └── PortDTO.py
│   ├── masscan/
│   │   ├── masscan_generator.py
│   │   └── masscan_parser.py
│   ├── nmap/
│   │   ├── nmap_generator.py
│   │   ├── nmap_parser.py
│   │   └── nmap_utils.py
│   └── smap/
│       ├── smap_generator.py
│       └── smap_parser.py
├── utils/
│   ├── helpers.py           # config loader
│   ├── permission.py        # chown outputs back to the sudo user
│   └── ui.py                # rich live task table
├── ui/                      # React + Vite + Tailwind frontend
│   └── src/
│       ├── App.jsx
│       └── components/      # ConfigDashboard, ScanMonitor, ResultViewer,
│                            # NetworkGraph, HostDetailsPanel
├── tests/
│   ├── dtos/
│   ├── generator/
│   ├── merger/
│   └── parser/
├── docs/                    # project report and slides (PDF)
└── output/
    └── raw/
```

---

## How to Extend (Add a New Tool)

To add a new tool (e.g. `RustScan`, `Nuclei` or a custom script), follow these three steps.

### 1. Create the Command Generator
Create `module/<new_tool>/<new_tool>_generator.py` with a subclass of `CommandGenerator`. `generate_commands()` returns one dict per enabled mode, with the keys `command`, `output_file` and `tool_name`. This is `module/nmap/nmap_generator.py`:

```python
from ..base_generator import CommandGenerator

class NmapGenerator(CommandGenerator):
    def generate_commands(self, config: dict, target) -> list:
        commands_struct = []

        for sub_mode in config.get("modes", []):
            if sub_mode.get("enable"):
                flags = sub_mode.get("flags", "")
                output_file = sub_mode.get("outputpath", "nmap.xml")
                full_output_path = self.output_dir / output_file

                if "--top-ports" in flags:
                    top_ports = sub_mode.get("top_ports", 100)
                    flags = flags.replace("--top-ports", f"--top-ports {top_ports}")

                cmd = f"sudo nmap {flags} -oX {full_output_path} {target}"
                commands_struct.append(
                    {
                        "command": cmd,
                        "output_file": full_output_path,
                        "tool_name": "nmap"
                    }
                )

        return commands_struct
```

If your tool writes a `.json` file, the launcher automatically wraps it as `{"command": ..., "data": <original output>}`, so your parser can read the command that produced it.

### 2. Create the Parser
Create `module/<new_tool>/<new_tool>_parser.py` with a subclass of `BaseParser`:
- `can_handle(file_path)` *(static)*: return `True` only for files this parser understands. Usually this checks the extension and the tool name in the file name.
- `parse(file_path)`: return a `ParsedDataDTO` with one `HostDTO` per IP and one `PortDTO` per `"port/proto"` key.

A minimal skeleton (see `module/masscan/masscan_parser.py` for a full example):

```python
import json
from pathlib import Path

from module.base_parser import BaseParser
from module.dtos.HostDTO import HostDTO
from module.dtos.ParsedDataDTO import ParsedDataDTO
from module.dtos.PortDTO import PortDTO


class NewToolParser(BaseParser):
    @staticmethod
    def can_handle(file_path: Path) -> bool:
        return file_path.suffix == ".json" and "newtool" in file_path.name

    def parse(self, file_path: Path) -> ParsedDataDTO:
        tool_name = "newtool"
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        command = content.get("command", "unknown")
        data = {}

        for entry in content.get("data", []):
            ip = entry.get("ip")
            if not ip:
                continue
            host = data.setdefault(ip, HostDTO(ip=ip))

            for p in entry.get("ports", []):
                key = f"{p['port']}/{p.get('proto', 'tcp')}"
                host.ports[key] = PortDTO(
                    port=key,
                    state=p.get("status", "unknown"),
                    banner=None,
                    service=p.get("service", "unknown"),
                    source=tool_name,
                    ttl=p.get("ttl"),
                    reason=p.get("reason"),
                    cpes=[],
                    command=command,
                )

        return ParsedDataDTO(tool_name=tool_name, command=command, data=data)
```

### 3. Register the Modules
Add the generator to `GENERATOR_REGISTRY` in `module/launcher.py` and the parser to `PARSER_REGISTRY` in `module/parser.py`. The generator key **must** match the config section name (`launcher_<new_tool>`).

```python
# module/launcher.py
GENERATOR_REGISTRY = {
    "launcher_nmap": NmapGenerator,
    "launcher_masscan": MasscanGenerator,
    "launcher_smap": SmapGenerator,
    "launcher_newtool": NewToolGenerator,
}
```

```python
# module/parser.py
PARSER_REGISTRY = {
    "parser_nmap": NmapParser,
    "parser_masscan": MasscanParser,
    "parser_smap": SmapParser,
    "parser_newtool": NewToolParser,
}
```

Finally, add the tool's section to `config.yml`. The orchestrator then runs and parses it automatically, and it appears in the Web UI configuration editor.

```yaml
mode:
  launcher_newtool:
    enabled: true
    modes:
      - name: <mode_name>
        enable: true
        description: "Description..."
        flags: "<tool flags for this mode>"
        outputpath: "newtool_<mode_name>.json"
        custom_option: ""
    flags:
      - name: <global_flag_name>
        enable: false
        description: "Description..."
        flags: "<flag>"
```

---

## Running the Tests

The test suite uses `pytest`. `pytest.ini` already adds the project root to `PYTHONPATH`:

```bash
source .venv/bin/activate
pytest
```

The tests cover the DTOs, the Smap generator, the Nmap/Masscan/Smap parsers and the merger.

---

## Known Limitations
- The global `flags` list is currently applied only by the **Masscan** generator. For Nmap and Smap, put extra flags directly in the mode's `flags` string.
- The tool-level keys `top_port_range`, `top_ports` and `rate` are not read by the generators. Use the per-mode `top_ports` key and put `--rate` in the mode's `flags`.
- OS guesses are not merged into the final report yet (`os` is always empty).
- Duplicate port entries from the same tool are not pruned yet.
- The Web UI always scans the `mode.target` saved in `config.yml`.

---

## Legal & Attribution

A.R.E.S. is an orchestration tool that wraps several powerful open-source scanners. It acts as a "smart interface" for these tools, and full credit goes to their original authors.

| Tool | License | Author | Link |
| :--- | :--- | :--- | :--- |
| **Nmap** | NPSL (Nmap Public Source License) | Gordon Lyon (Fyodor) | [nmap.org](https://nmap.org) |
| **Masscan** | AGPL-3.0 | Robert Graham | [github.com/robertdavidgraham/masscan](https://github.com/robertdavidgraham/masscan) |
| **Smap** | AGPL-3.0 | s0md3v | [github.com/s0md3v/Smap](https://github.com/s0md3v/Smap) |

**License Note:** A.R.E.S. itself is licensed under the **MIT** License (see [LICENSE](LICENSE)). You must still comply with the licenses of the underlying tools when you install and use them.
