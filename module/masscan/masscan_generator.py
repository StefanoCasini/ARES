import argparse
import ipaddress
import subprocess
import shlex
from concurrent.futures import ThreadPoolExecutor
import os

from ..base_generator import CommandGenerator


class MasscanGenerator(CommandGenerator):
    def generate_commands(self, config: dict, target) -> list:
        commands_struct = []

        global_flags = []

        global_flags = []
        for flag in config.get("flags", []):
            if flag.get("enable"):
                global_flags.append(flag.get("flags", ""))
        global_flags_str = " ".join(global_flags)
        
        for sub_mode in config.get("modes", []):
            if sub_mode.get("enable"):
                flags = sub_mode.get("flags", "")
                output_file = sub_mode.get("outputpath", "masscan.json")
                full_output_path = self.output_dir / output_file

                if "--top-ports" in flags:
                    top_ports = sub_mode.get("top_ports", 100)
                    flags = flags.replace("--top-ports", f"--top-ports {top_ports}")
                    
                cmd = f"sudo masscan {global_flags_str} {flags} -oJ {full_output_path} {target}"
                commands_struct.append(
                    {
                        "command": cmd,
                        "output_file": full_output_path,
                        "tool_name": "masscan"
                    }
                )

        return commands_struct