<div align="center">
  <img src="ARES_icon.png" alt="A.R.E.S. Logo" width="250">
</div>

# A.R.E.S. (Automated Reconnaissance & Enumeration System)

> **A Modular Framework for Hybrid Network Discovery and Data Fusion**

**A.R.E.S.** is a Python-based orchestration tool designed to automate the reconnaissance phase of Network Penetration Testing. It leverages the **Strategy Pattern** to combine the speed of volumetric scanners (Masscan), the precision of service enumerators (Nmap), and the stealth of passive intelligence (Smap) into a single, unified workflow.

The core strength of A.R.E.S. lies in its **Data Fusion Engine**, which parses heterogeneous outputs (XML, JSON, Raw) and merges them into a standardized, conflict-free JSON report, ready for human analysis or automated ingestion.

---

## Disclaimer

> **This tool is intended for legal security auditing and educational purposes only.**
>
> The developers assume no liability and are not responsible for any misuse or damage caused by this program. **Always obtain proper authorization before scanning a network.**

---

## Table of Contents
- [Key Features](#key-features)
- [Installation](#installation)
- [Configuration (How to Start)](#configuration-how-to-start)
- [Configuration Examples](#configuration-examples)
- [DTOs](#dtos)
- [Architecture & Extensibility](#architecture--extensibility)
- [How to Extend](#how-to-extend-add-a-new-tool)

---

## Key Features
- **Hybrid Scanning:** Orchestrates Active (Nmap, Masscan) and Passive (Smap) tools concurrently.
- **Unified Data Model:** Normalizes disparate tool outputs into a single JSON structure.
- **High Performance:** Multi-threaded launcher with configurable concurrency logic.
- **Modular Architecture:** Built on the Strategy Pattern for easy extension (new tools/parsers).
- **Declarative Configuration:** Fully controllable via YAML config files.

---

## Installation

### Prerequisites
Ensure the following tools are installed and available in your system `PATH`:
* **Python 3.8+**
* **Nmap**
* **Masscan** (Requires root/sudo privileges for raw sockets)
* **Smap** (Optional, for passive scanning)

### Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/StefanoCasini/ARES.git
    cd ARES
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Configuration (How to Start)

A.R.E.S. relies on a `config.yaml` file to define targets, tool behavior, and execution parameters.

### Structure Overview
The configuration is divided into `general` settings and `tools` definitions.

```yaml
# ================================
# ARES CONFIGURATION FILE
# ================================

output_report_path: "output"
# --------------------------------
# SCAN MODE
# --------------------------------
mode:
  enable_scan: true          # enable or disable the scanning phase
  n_threads: 3 # to choose the number of parallel scans
  base_output_raw_path: "output/raw" # base path to store raw scan outputs

  # NMAP
  launcher_nmap:
    enabled: true                 # enable or disable Nmap module
    top_port_range: 100
    modes:                        # each mode maps to a thread
      .
      .
      .

  # MASSCAN
  launcher_masscan:
    enabled: true                 # enable or disable Masscan module
    top_ports: 100
    rate: 1000
    modes:
      .
      .
      .

  # SMAP
  launcher_smap:
    enabled: true                 # enable or disable Nmap module
    top_port_range: 100
    modes:                        # each mode maps to a thread
      .
      .
      .

# --------------------------------
# IMPORT FILE
# --------------------------------
import_files:
  - "output/raw/<timestamp>_<target>/nmap_top_tcp_ports.xml"  how to import example
```
## Usage

A.R.E.S. relies on a `config.yaml` file to define targets, tool behavior, and execution parameters. To run the tool, simply point to your configuration file using the CLI.

**Command to run:**
```bash
sudo ares.py <target>
```

> **Note:** `sudo` privileges are often required because Masscan and Nmap (specifically for OS detection) utilize raw sockets to perform scans.

---

## Configuration Examples

Below are common configuration scenarios to be defined in `config.yaml`.

### Scenario A: Fast Discovery (Stealth & Speed)
In this scenario, **Masscan** is used for high-speed volumetric scanning to quickly identify open ports from the top 100 most used tcp ports.

```yaml
launcher_masscan:
    enabled: true                 # enable or disable Masscan module
    top_ports: 100
    rate: 1000
    modes:
      # --- LOUD / FAST MODES (Discovery) ---
      - name: top-ports
        enable: true
        description: "LOUD: Rapidly find live hosts on top 100 ports"
        flags: "--top-ports --rate 5000" 
        outputpath: "masscan_top_ports.json"
        custom_option: ""
```

### Scenario B: Deep Enumeration
This profile focuses on detailed service versioning and script scanning. It uses **Nmap** with aggressive flags.

```yaml
 # NMAP
  launcher_nmap:
    enabled: true                 # enable or disable Nmap module
    top_port_range: 100
    modes:
    .
    .
    .
    - name: aggressive
        enable: false
        description: "Full scan (LOWD)"
        flags: "-A"
        output_path: "nmap_full_scan.xml"
        custom_option: ""
    flags:
      - name: no-ping
        enable: false
        description: "Treat all hosts as online -- skip host discovery"
        flags: "-Pn"
      - name: timing
        enable: true
        description: "Set timing template <0-5> (higher is faster)"
        flags: "-T4"
```

---

## DTOs

A.R.E.S. now uses **Data Transfer Objects (DTOs)** as the internal data model between parsers, merger, and report generation.  
This keeps the data flow explicit and type-safe instead of passing unstructured dictionaries.

### DTOs currently used

- `ParsedDataDTO`: top-level parser output (`tool_name`, `command`, and parsed `data`).
- `HostDTO`: host container (`ip`, `ports`, `hostnames`, `os`, `cpes`, `discovery_commands`).
- `PortDTO`: port/service details (`port`, `state`, `service`, `banner`, `source`, `reason`, `ttl`, `cpes`, `command`).
- `OsDTO`: OS guess metadata (`name`, `cpes`, `command`).
- `FinalReportDTO`: final merged output (`total_hosts`, `commands`, `hosts`).

### Example DTO flow

```python
from module.dtos.HostDTO import HostDTO
from module.dtos.ParsedDataDTO import ParsedDataDTO
from module.dtos.PortDTO import PortDTO

host = HostDTO(ip="192.168.1.10")
host.ports["22/tcp"] = PortDTO(
    port="22/tcp",
    state="open",
    service="ssh",
    banner="OpenSSH",
    source="nmap",
    ttl=None,
    reason=None,
    cpes=[],
    command="nmap -sV 192.168.1.10"
)

result = ParsedDataDTO(
    tool_name="nmap",
    command="nmap -sV 192.168.1.10",
    data={"192.168.1.10": host}
)
```

---

## Architecture & Extensibility

A.R.E.S. is built to be **modular and extensible**. The core logic is decoupled from specific tool implementations using the **Strategy Pattern**.

The system revolves around two main interfaces:
1.  **Command Generators:** Responsible for building the CLI command string for a specific tool (e.g., constructing the Nmap flags).
2.  **Parsers:** Responsible for reading the tool's raw output file (XML, JSON, etc.) and converting it into the internal standard structure.

### Directory Structure
The project follows a clean separation of concerns:

```plaintext

├── ares.py
├── config.yml
├── __init__.py
├── LICENSE
├── module
│   ├── base_generator.py
│   ├── base_parser.py
│   ├── __init__.py
│   ├── launcher.py
│   ├── masscan
│   │   ├── __init__.py
│   │   ├── masscan_generator.py
│   │   └── masscan_parser.py
│   ├── merger.py
│   ├── nmap
│   │   ├── __init__.py
│   │   ├── nmap_generator.py
│   │   ├── nmap_parser.py
│   │   └── nmap_utils.py
│   ├── parser.py
│   └── smap
│       ├── __init__.py
│       ├── smap_generator.py
│       └── smap_parser.py
├── output
│   └── raw
├── README.md
├── test
│   ├── __init__.py
│   ├── nmap_parser_result
│   ├── test_masscan_parser.py
│   ├── test_merger_duplicates.py
│   ├── test_nmap_parser.py
│   ├── test_smap_generator.py
│   └── test_smap_parser.py
└── utils
    ├── helpers.py
    ├── __init__.py
    ├── permission.py
    └── ui.py

```

---

## How to Extend (Add a New Tool)

To add support for a new tool (e.g., `Nuclei`, `RustScan`, or a custom script), follow these three steps:

### 1. Create the Command Generator
Create a new folder in `src/modules/<new tools>/<new_generator.py>` implementing the base generator interface. This class defines how the command line string is constructed. Here's an example of nmap_generator.py

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

### 2. Create the Parser
Create a new class in `src/modules/<new tools>/<new_generator.py>` to handle the output file. This class must read the raw file produced by the tool and map it to the internal `Host` object list. Here's an example of masscan_parser.py

```python
class MasscanParser(BaseParser):
    @staticmethod
    def can_handle(file_path: Path) -> bool:
        if file_path.suffix != ".json":
            return False
        try:
            if "masscan" in file_path.name:
                return True
            # Fallback: Peek content
            with open(file_path, 'r') as f:
                content_start = f.read(50)
            # Masscan raw output is usually a list [...]
            # Your wrapped output starts with { "command": ... }
            if "masscan" in content_start: 
                return True
        except Exception:
            return False
        return False

    def parse(self, file_path: Path) -> ParsedDataDTO:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except Exception:
            return ParsedDataDTO(tool_name="masscan", command="", data={})

        command = content.get("command", "unknown")
        tool_name = "masscan"
        raw_data_list = content.get('data', [])  # assuming data is under 'data' key or is the root

        data_dict = {}

        for entry in raw_data_list:
            ip = entry.get("ip")
            if not ip:
                continue
            if ip not in data_dict:
                data_dict[ip] = HostDTO(ip=ip)

            host_record = data_dict[ip]
            raw_ports = entry.get("ports", [])

            for port_data in raw_ports:
                port_id = str(port_data.get("port"))
                protocol = port_data.get("proto", "tcp")
                key = f"{port_id}/{protocol}"

                if key not in host_record.ports:
                    host_record.ports[key] = PortDTO(
                        port = key,
                        state="closed",
                        service="unknown",
                        banner=None,
                        source=tool_name,
                        ttl = None,
                        reason = None,
                        cpes = None,
                        command = command
                    )

                existing_port_data = host_record.ports[key]

                # Extract new data
                new_status = port_data.get("status", None)
                new_ttl = port_data.get("ttl", None)
                new_reason = port_data.get("reason", None)
                new_service_obj = port_data.get("service", {})
                new_banner = None
                new_service_name = None

                if isinstance(new_service_obj, dict):
                    new_banner = new_service_obj.get("banner", None)
                    new_service_name = new_service_obj.get("name", "unknown")
                elif isinstance(new_service_obj, str):
                    new_service_name = new_service_obj

                # Merge logic
                if new_status and new_status == "open":
                    existing_port_data.state = new_status
                if new_ttl is not None:
                    existing_port_data.ttl = new_ttl
                if new_reason is not None:
                    existing_port_data.reason = new_reason
                if new_banner:
                    existing_port_data.banner = new_banner
                if new_service_name and new_service_name != "unknown":
                    existing_port_data.service = new_service_name
                
                if tool_name not in existing_port_data.source:
                    existing_port_data.source += f", {tool_name}"

        parsed_data_dto = ParsedDataDTO(tool_name=tool_name, command=command, data=data_dict)
        return parsed_data_dto

```

### 3. Register the Modules
Finally, add your new generator classes to the `GENERATOR_REGISTRY` (found in `src/module/launcher.py`) and your parser class to the `PARSER_REGISTRY` (found in `src/module/parser.py`). This tells the orchestrator that the new tool exists and maps the name used in the config file to the correct classes.

```python 
# Registry of available generator classes
GENERATOR_REGISTRY = {
    "launcher_nmap": NmapGenerator,
    "launcher_masscan": MasscanGenerator,
    "launcher_smap": SmapGenerator
}
```

```python
PARSER_REGISTRY = {
    "parser_nmap": NmapParser,
    "parser_masscan": MasscanParser,
    "parser_smap": SmapParser
}
```
Once registered, you can simply add the new tool name to your `config.yaml` tools section, and the orchestrator will handle the execution and parsing automatically.

```yaml
launcher_<new_tool>:
    enabled: true                 # enable or disable Nmap module
    top_port_range: 100  #if needed, i use that to set the range for the command that need port range
    modes:
    .
    .
    .
    - name: <mode1>
        enable: false
        description: "Description..."
        flags: "<tool flag related to this mode>"
        output_path: "<mode_output_file_name>"
        custom_option: ""
    flags:
      - name: <custom_option name>
        enable: false
        description: "Description..."
        flags: "<flag related to this mode>"
```

##  Legal & Attribution

ARES is an orchestration tool that wraps several powerful open-source scanners. 
We essentially act as a "smart interface" for these tools. 
Full credit goes to the original authors.

| Tool | License | Author | Link |
| :--- | :--- | :--- | :--- |
| **Nmap** | NPSL (GPL-compatible) | Gordon Lyon (Fyodor) | [nmap.org](https://nmap.org) |
| **Masscan** | AGPL-3.0 | Robert Graham | [github.com/robertdavidgraham/masscan](https://github.com/robertdavidgraham/masscan) |
| **Smap** | AGPL-3.0 | s0md3v | [github.com/s0md3v/Smap](https://github.com/s0md3v/Smap) |

**License Note:** ARES itself is licensed under **MIT**. However, users must comply with the licenses of the underlying tools (Nmap, Masscan, etc.) when installing and using them.
