import json
import os
from pathlib import Path
from module.masscan.masscan_parser import MasscanParser

# --- YOUR SAMPLE DATA ---
command = "masscan test"
sample_json_input = [
    { "ip": "10.10.10.1", "timestamp": "1768474998", "ports": [ {"port": 445, "proto": "tcp", "status": "open", "reason": "syn-ack", "ttl": 64} ] },
    { "ip": "10.10.10.1", "timestamp": "1768475000", "ports": [ {"port": 445, "proto": "tcp", "service": {"name": "smb", "banner": "SMBv2 guid=00..."} } ] },
]

file_data = {
    "tool_name": "masscan",
    "command": command,
    "data": sample_json_input
}

# --- 1. SETUP: Create a temporary file ---
test_file_path = Path("temp_test_masscan.json")
with open(test_file_path, "w") as f:
    json.dump(file_data, f)

try:
    # --- 2. EXECUTION: Pass the FILE PATH, not the list ---
    parser = MasscanParser()
    result = parser.parse(test_file_path)

    # --- 3. VERIFICATION ---
    print("--- TEST RESULTS ---\n")

    # CHECK 1: IP 10.10.10.1 Port 445
    if '10.10.10.1' in result['data']:
        p445 = result['data']['10.10.10.1']['ports']['445/tcp']
        print(f"IP: 10.10.10.1 | Port: 445")
        print(f"  > TTL (Expect 64): {p445.get('ttl')}")
        print(f"  > Banner (Expect SMBv2...): {p445.get('banner')}")
    else:
        print("ERROR: IP 10.10.10.1 not found in result!")

    print("-" * 30)

    # CHECK 2: IP 10.10.10.1 Port 80
    if '10.10.10.1' in result['data']:
        p177 = result['data']['10.10.10.1']['ports']
        print(f"IP: 10.10.10.1")
        print(f"  > Total entries for Port 80 (Expect 1): {len(p177)}")
        print(f"  > State: {p177['80/tcp']['state']}")
    else:
        print("ERROR: IP 10.10.10.1 not found in result!")

finally:
    # --- 4. CLEANUP: Remove the temp file ---
    if test_file_path.exists():
        os.remove(test_file_path)