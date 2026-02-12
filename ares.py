import argparse
import datetime
import json
from pathlib import Path
import sys

# Modules
from module.launcher import run_scanners
from module.parser import parse_all_files
from utils.helpers import load_config
from module.merger import merge_all
from utils.permission import fix_ownership

# --------------------------------------------
# MAIN EXECUTION
# --------------------------------------------
def main():
    # 1. Parse ONLY the config file path
    parser = argparse.ArgumentParser(description="Aress - Automated Recon and Scanning Tool")
    parser.add_argument("target", nargs="?", help="Target IP/CIDR (Overrides config.yml)")
    parser.add_argument("--config", default="config.yml", help="Path to configuration file")
    args = parser.parse_args()

    # 2. Load Configuration
    print(f"[-] Loading configuration from {args.config}...")
    config_data = load_config(args.config)

    if args.target:
        if "mode" not in config_data:
            config_data["mode"] = {}
        
        config_data["mode"]["target"] = args.target
    
    target = config_data["mode"].get("target", "unknown")
    if target == "unknown":
        print("[!] Critical: No target specified in config.yml or command line.")
        sys.exit(1)

    # 3. Run Scanners (Launcher) And/Or Import Files
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d_%H%M")
    file_to_read = []
    if config_data.get("mode", {}).get("enable_scan", True):
        file_to_read = run_scanners(config_data, timestamp)

    # Add imported files from config.yml
    file_from_import = config_data.get("import_files", []) or []
    if file_from_import is not []:
        file_to_read.extend(file_from_import)

    #4. Parse all files 
    all_results = parse_all_files(file_to_read)

    # 5. Merge Results
    report = merge_all(all_results)

    # 6. Save Merged Report
    base_output_dir = Path(config_data.get("output_report_path", "output"))
    
    base_output_dir.mkdir(parents=True, exist_ok=True) 

    target_clean = config_data["mode"]["target"].replace("/", "_")

    output_file_name = f"{timestamp}_{target_clean}.json"
    output_file_name = base_output_dir / output_file_name
    
    try:
        with open(output_file_name, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        print(f"[+] Summary saved to: {output_file_name}")
    except Exception as e:
        print(f"[!] Error saving report: {e}")


if __name__ == "__main__":
    main()