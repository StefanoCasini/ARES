import json
from pathlib import Path
from module.base_parser import BaseParser
from module.dtos.HostDTO import HostDTO
from module.dtos.ParsedDataDTO import ParsedDataDTO
from module.dtos.PortDTO import PortDTO


class MasscanParser(BaseParser):
    """
    Parser for Masscan JSON output files.
    In this project the masscan launcher is built to wrap output in a standard format:
    {
        "command": "...",
        "data": [ {...}, {...}, ... ]
    }
    and the cli command is built to produce a json output.


    Another information about Masscan JSON output is that is full of duplicates row for same ip and port couple.
    This because masscan first finds open ports and then tries to grab banners on them, so you can have multiple entries

    So i need to manage it here in the parser.
    """
    @staticmethod
    def can_handle(file_path: Path) -> bool:
        if file_path.suffix != ".json":
            return False
        # 2. Content/Context Check
        # We can check filename conventions if you use them (e.g., "masscan_" in name)
        # Or peek at the content for Masscan specific structure
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
            # Return empty structure if file is corrupted or empty
            return ParsedDataDTO(tool_name="masscan", command="", data={})
        
        # 1. Extract Meta-Info
        command = content.get('command', 'unknown')
        tool_name = "masscan"
        raw_data_list = content.get('data', [])  # assuming data is under 'data' key or is the root

        data_dict = {}

        for entry in raw_data_list:
            ip = entry.get("ip")

            if not ip:
                continue
            if ip not in data_dict:
                data_dict[ip] = HostDTO(ip=ip, ports={}, hostnames=[], os=[], cpes=[])

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
                        reason = None
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