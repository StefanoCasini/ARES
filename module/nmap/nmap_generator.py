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