import yaml
import sys
from pathlib import Path

from utils.helpers import load_config

# --- Setup Python Path ---
# Allows importing 'module' from the project root
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from module.smap.smap_generator import SmapGenerator

def test_config_generation():
    print("\n--- 🧪 Testing Smap Generator with REAL Config ---")

    target = "testtarget.com"
    
    # 1. Load the actual config.yml
    config_path = project_root / "config.yml"

        # 2. Load Configuration
    print(f"[-] Loading configuration from {config_path}...")
    config_data = load_config(config_path)
    mode_config = config_data.get("mode", {})
    
    generator = SmapGenerator(output_dir=project_root / "test_outputs")
    commands = generator.generate_commands(mode_config.get("launcher_smap", {}), target)

    print("[-] Generated Commands:")
    for cmd_struct in commands:
        print(cmd_struct["command"])

    print("\n--- ✅ Smap Generator Test Completed ---\n")

if __name__ == "__main__":
    test_config_generation()