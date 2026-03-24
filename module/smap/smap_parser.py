import json
from pathlib import Path
from module.base_parser import BaseParser
from module.dtos.HostDTO import HostDTO
from module.dtos.OsDTO import OsDTO
from module.dtos.ParsedDataDTO import ParsedDataDTO
from module.dtos.PortDTO import PortDTO


class SmapParser(BaseParser):
    def can_handle(file_path: Path) -> bool:
        if file_path.suffix != ".json":
            return False
        # 2. Content/Context Check
        # We can check filename conventions if you use them (e.g., "masscan_" in name)
        # Or peek at the content for Masscan specific structure
        try:
            if "smap" in file_path.name:
                return True
            # Fallback: Peek content
            with open(file_path, 'r') as f:
                content_start = f.read(50)
            # Masscan raw output is usually a list [...]
            # Your wrapped output starts with { "command": ... }
            if "smap" in content_start: 
                return True
        except Exception:
            return False
        return False

        pass

    def parse(self, file_path: Path) -> ParsedDataDTO:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except Exception:
            # Return empty structure if file is corrupted or empty
            return ParsedDataDTO(tool_name="smap", command="", data={})
        
        # 1. Extract Meta-Info
        command = content.get('command', 'unknown')
        tool_name = "smap"
        raw_data_list = content.get('data', [])  # assuming data is under 'data' key or is the root

        data_dict = {}

        for entry in raw_data_list:
            ip = entry.get("ip")
            if not ip:
                continue
            if ip not in data_dict:
                data_dict[ip] = HostDTO(ip=ip)

            host_record = data_dict[ip]
            # --- Extract Hostnames ---
            # Smap provides a list of hostnames
            raw_hostnames = entry.get("hostnames", {})
            for hn in raw_hostnames:
                if hn not in host_record.hostnames:
                    host_record.hostnames[hn] = command

            # --- Extract OS/CPE/Vulns (Smap bonuses) ---
            if "os" in entry and entry["os"]:
                raw_os = entry["os"]
                os_entry = None
                if isinstance(raw_os, dict):
                    os_name = raw_os.get("name", "")
                    os_accuracy = raw_os.get("accuracy")
                    if os_name:
                        if os_accuracy:
                            os_entry = f"{os_name} ({os_accuracy}%)"
                        else:
                            os_entry = os_name
                elif isinstance(raw_os, str):
                    os_entry = raw_os
                # Append ONLY if we have a valid string (Prevents 'dict' crash)
                if os_entry and isinstance(os_entry, str):
                    if os_entry not in host_record.os:

                        host_record.os.append(OsDTO(name = os_entry, command = command))
            # TODO: undestand if smap provides vulns in a way we can extract and merge here. If so, we can add a "vulns" field to HostDTO and merge similarly to ports.
            # if "vulns" in entry:
            #     host_record.vulns.extend(entry["vulns"])

            # --- C. Extract Ports ---
            raw_ports = entry.get("ports", {})

            for port_data in raw_ports:
                port_id = str(port_data.get("port"))
                protocol = port_data.get("protocol", "tcp")
                key = f"{port_id}/{protocol}"

                if key not in host_record.ports:
                    host_record.ports[key] = PortDTO(
                        port = key,
                        state="closed",
                        service="unknown",
                        banner=None,
                        source=tool_name,
                        ttl = None,
                        reason = "shodan-api",
                        command=command,
                    )

                existing_port_data = host_record.ports[key]
                # Extract new data
                new_service = port_data.get("service", None)
                new_banner = port_data.get("product", None)
                port_cpes = port_data.get("cpes", [])
                if port_cpes:
                    existing_port_data.cpes.extend(port_cpes)
                # Merge logic
                if new_banner:
                    existing_port_data.banner = new_banner
                if new_service and new_service != "unknown":
                    existing_port_data.service = new_service

                if tool_name not in existing_port_data.source:
                    existing_port_data.source += f", {tool_name}"

        parsed_data_dto = ParsedDataDTO(tool_name=tool_name, command=command, data=data_dict)
        return parsed_data_dto