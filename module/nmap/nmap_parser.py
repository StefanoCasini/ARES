import xml.etree.ElementTree as ET
from pathlib import Path
from module.base_parser import BaseParser
from module.dtos.HostDTO import HostDTO
from module.dtos.OsDTO import OsDTO
from module.dtos.ParsedDataDTO import ParsedDataDTO
from module.dtos.PortDTO import PortDTO 


class NmapParser(BaseParser):

    """
    Parser for NMAP XML output files.
    The cli command is built to produce a XML output.
    """
    @staticmethod
    def can_handle(file_path: Path) -> bool:
        if file_path.suffix != ".xml":
            return False
        # 2. Content/Context Check
        # We can check filename conventions if you use them (e.g., "nmap_" in name)
        # Or peek at the content for Nmap specific structure
        try:
            if "nmap" in file_path.name:
                return True
            # Fallback: Peek content
            with open(file_path, 'r') as f:
                content_start = f.read(50)
            # Nmap raw output is usually a list [...]
            # Your wrapped output starts with { "command": ... }
            if "nmap" in content_start: 
                return True
        except Exception:
            return False
        return False

    def parse(self, file_path: Path) -> ParsedDataDTO:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except Exception:
            # Return empty structure if file is corrupted or empty
            return ParsedDataDTO(tool_name="nmap", command="", data={})
        # 1. Extract Meta-Info
        command = root.get('args', 'unknown')
        tool_name = "nmap"
        
        data_dict = {}
        
        for host in root.findall("host"):
            # Some struct to get information about the host, we will convert to HostDTO at the end of this loop

            status = host.find("status")
            if status is None or status.get("state") != "up":
                continue

            # Extract IP Address
            for addr in host.findall("address"):
                if addr.get("addrtype") == "ipv4":
                    ip = addr.get("addr")
                    break
            
            host_info = HostDTO(ip=ip)

            if not ip: continue

            # --- Extract Ports & Service CPEs ---
            ports_elem = host.find("ports")
            if ports_elem:
                for port in ports_elem.findall("port"):
                    port_id = port.get("portid")
                    protocol = port.get("protocol")
                    key = f"{port_id}/{protocol}"
                    port_cpes = []
                    state = port.find("state")
                    if state is not None and state.get("state") == "open":
                        service = port.find("service")
                        service_name = service.get("name") if service is not None else "unknown"
                        banner = service.get("product") if service is not None else ""

                        # Grab CPE from the Service (e.g. cpe:/a:apache:http_server)
                        if service is not None:
                            for cpe in service.findall("cpe"):
                                if cpe.text and cpe.text not in port_cpes:
                                    port_cpes.append(cpe.text)

                        host_info.ports[key] = PortDTO(
                            port=key,
                            state="open",
                            service=service_name,
                            banner=banner,
                            source=tool_name,
                            cpes = port_cpes,
                            ttl=None,
                            reason=None,
                            command=command
                        )
            # --- Extract Hostnames ---
            hostnames_elem = host.find("hostnames")
            if hostnames_elem:
                for hn in hostnames_elem.findall("hostname"):
                    name = hn.get("name")
                    if name:
                        host_info.hostnames[name] = [command]
            os_elem = host.find("os")
            if os_elem:
                for os_match in os_elem.findall("osmatch"):                    
                    # Get OS CPEs (e.g. cpe:/o:linux:linux_kernel)
                    os_cpes = []
                    for os_class in os_match.findall("osclass"):
                        for cpe in os_class.findall("cpe"):
                            if cpe.text and cpe.text not in os_cpes:
                                os_cpes.append(cpe.text)

                # Get OS Name
                    if os_match.get("name"):
                        host_info.os.append(OsDTO(name=os_match.get("name"), command=command, cpes=os_cpes))
            data_dict[ip] = host_info
            
        parsed_data_dto = ParsedDataDTO(tool_name=tool_name, command=command, data=data_dict)
        return parsed_data_dto