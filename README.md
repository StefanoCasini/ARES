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
    git clone [https://github.com/yourusername/ares-framework.git](https://github.com/yourusername/ares-framework.git)
    cd ares-framework
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
# config.yaml example

general:
  project_name: "Internal_Audit_01"
  output_directory: "./results"
  targets: 
    - "192.168.1.0/24"
    - "10.0.0.5"
  max_threads: 4

tools:
  # Define which tools to run and their arguments
  nmap:
    enabled: true
    arguments: "-sV -O --top-ports 100"
    output_format: "xml"  # Required for the parser
  
  masscan:
    enabled: true
    arguments: "--rate=1000 -p80,443,22"
```
## Usage

A.R.E.S. relies on a `config.yaml` file to define targets, tool behavior, and execution parameters. To run the tool, simply point to your configuration file using the CLI.

**Command to run:**
[INSERISCI QUI IL COMANDO BASH PER LANCIARE IL TOOL]

> **Note:** `sudo` privileges are often required because Masscan and Nmap (specifically for OS detection) utilize raw sockets to perform scans.

---

## Configuration Examples

Below are common configuration scenarios to be defined in `config.yaml`.

### Scenario A: Fast Discovery (Stealth & Speed)
In this scenario, **Masscan** is used for high-speed volumetric scanning to quickly identify open ports, while **Smap** provides passive intelligence without touching the target. **Nmap** is disabled to reduce the active footprint and scan duration.

[INSERISCI QUI L'ESEMPIO YAML SCENARIO A]

### Scenario B: Deep Enumeration
This profile focuses on detailed service versioning and script scanning. It uses **Nmap** with aggressive flags on specific targets found previously. Masscan is disabled to prioritize precision over speed.

[INSERISCI QUI L'ESEMPIO YAML SCENARIO B]

---

## Architecture & Extensibility

A.R.E.S. is built to be **modular and extensible**. The core logic is decoupled from specific tool implementations using the **Strategy Pattern**.

The system revolves around two main interfaces:
1.  **Command Generators:** Responsible for building the CLI command string for a specific tool (e.g., constructing the Nmap flags).
2.  **Parsers:** Responsible for reading the tool's raw output file (XML, JSON, etc.) and converting it into the internal standard structure.

### Directory Structure
The project follows a clean separation of concerns:

[INSERISCI QUI L'ALBERO DELLE DIRECTORY]

---

## How to Extend (Add a New Tool)

To add support for a new tool (e.g., `Nuclei`, `RustScan`, or a custom script), follow these three steps:

### 1. Create the Command Generator
Create a new class in `src/modules/generators/` implementing the base generator interface. This class defines how the command line string is constructed.

[INSERISCI QUI IL CODICE PYTHON DEL GENERATOR]

### 2. Create the Parser
Create a new class in `src/modules/parsers/` to handle the output file. This class must read the raw file produced by the tool and map it to the internal `Host` object list.

[INSERISCI QUI IL CODICE PYTHON DEL PARSER]

### 3. Register the Module
Finally, add your new classes to the `Registry` (typically found in `src/core/registry.py` or `main.py`). This tells the orchestrator that the new tool exists and maps the name used in the config file to the correct classes.

[INSERISCI QUI IL CODICE PYTHON DI REGISTRAZIONE]

Once registered, you can simply add the new tool name to your `config.yaml` tools section, and the orchestrator will handle the execution and parsing automatically.

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
