import os
import re
from collections import defaultdict
import sys

import yaml

# --------------------------------------------
# CONFIG LOADER
# --------------------------------------------
def load_config(path):
    if not os.path.isfile(path):
        print(f"[!] Critical: Config file '{path}' not found.")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}