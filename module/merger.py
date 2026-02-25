import ipaddress

from module.dtos.ParsedDataDTO import ParsedDataDTO

def merge_tools(shodan_map=None, nmap_map=None, mass_map=None, smap_map=None, command=None):
    """
    Merge scan maps from nmap/smap, masscan, and networksherlock.
    Output structure:
    {
        "total host": N,
        "hosts": { "IP": { "os":..., "ports":[...] } }
    }
    """          
    nmap_map = nmap_map or {}
    mass_map = mass_map or {}
    shodan_map = shodan_map or {}
    # smap_map = smap_map or {}
    smap_map = {}
    command = command or {}  
        
    tool_maps = [shodan_map, nmap_map, mass_map, smap_map]
    tools = ["shodan", "nmap", "masscan", "smap"]
    
    all_ips = set(nmap_map.keys()) | set(mass_map.keys()) | set(shodan_map.keys()) | set(smap_map.keys())
    result = {"hosts": {}}
    result["total_hosts"] = len(all_ips)

    for ip in sorted(all_ips):
        host_record = {"ip": ip,"command":command ,"os_info": {}, "hostnames": {}, "ports": {}, "cpes":{}}

        hostnames = {}
        os_info = {}
        ports = {}
        cpes = {}
        
        for tool_name, tool_map in zip(tools, tool_maps):
            if ip in tool_map:
                # if tool_name == "shodan":
                    # print(f"Hostmanes:{tool_map[ip]}")
                    # print(f"ToolName:{tool_name}")
                for hn in tool_map[ip].get("hostnames") or []:
                    if hn not in hostnames:
                        hostnames[hn] = []
                    hostnames[hn].append(tool_name)          
                for os_info_i in tool_map[ip].get("os") or []:
                    if os_info_i not in os_info:
                        os_info[os_info_i] = []
                    os_info[os_info_i].append(tool_name)
                    
                for cpe in tool_map[ip].get("cpes") or []:
                    if cpe not in cpes:
                        cpes[cpe] = []
                    cpes[cpe].append(tool_name)
                
                for port, port_info in (tool_map[ip].get("ports") or []).items():
                    if port not in ports:
                        ports[port] = []
                    ports[port].append(port_info)
        
        host_record["hostnames"] = hostnames
        host_record["os_info"] = os_info
        host_record["cpes"] = cpes
        host_record["ports"] = ports
                    
                    
        result["hosts"][ip] = host_record
        
    sorted_hosts = dict(sorted(result["hosts"].items(), key=lambda x: ipaddress.ip_address(x[0])))
    result["hosts"] = sorted_hosts
    
    
    return result


def _merge_traked_field(target_dict, incoming_list, tool_name):
    for item in incoming_list:
        if item not in target_dict:
            target_dict[item] = []
        if tool_name not in target_dict[item]:
            target_dict[item].append(tool_name)

def _same_entry(entry1, entry2):
    if entry1.get("service") != entry2.get("service"):
        return False
    if entry1.get("banner") != entry2.get("banner"):
        return False
    return True

def _prune_weak_siblings(existing_entries, new_entry):
    for entry in existing_entries:
        if entry.get("source") != new_entry.get("source"):
            continue
        entry_service = entry.get("service", "unknown")
        entry_banner = entry.get("banner")
        new_entry_service = new_entry.get("service", "unknown")
        new_entry_banner = new_entry.get("banner")

        if (entry_service == "unknown" and entry_banner is None) or \
            (_same_entry(entry, new_entry)):
            existing_entries.remove(entry)

def merge_all(parser_results_list: list[ParsedDataDTO]):
    print(f"\n--- Merging {len(parser_results_list)} scan files ---")

    merged_db = {}
    command_set = set()
    for scan_file_result in parser_results_list:
        tool_name = scan_file_result.tool_name
        command = scan_file_result.command
        scan_data = scan_file_result.data

        command_set.add(command)

        for ip, host_info in scan_data.items():
            if ip not in merged_db:
                merged_db[ip] = {
                    "ip": ip,
                    "commands": set(),
                    "hostnames": {},
                    "os_info": {},
                    "cpes": {},
                    "ports": {}
                }

            entry = merged_db[ip]

            if command:
                entry["commands"].add(command)

            _merge_traked_field(entry["hostnames"], host_info.get("hostnames", {}), tool_name)
            _merge_traked_field(entry["os_info"], host_info.get("os", []), tool_name)
            _merge_traked_field(entry["cpes"], host_info.get("cpes", []), tool_name)

            # TODO: Avoid port info duplication on the same tool
            new_ports = host_info.get("ports", {}) 
            for port_key, port_info in new_ports.items():
                if port_key not in entry["ports"]:
                    entry["ports"][port_key] = []
                
                if "source" not in port_info:
                    port_info["source"] = []
                
                _prune_weak_siblings(entry["ports"][port_key], port_info)

                entry["ports"][port_key].append(port_info)

    final_output = {
        "total_hosts": len(merged_db),
        "commands": list(command_set),
        "hosts": {}
    }

    sorted_ips = sorted(merged_db.keys(), key=lambda ip: ipaddress.ip_address(ip))
    for ip in sorted_ips:
        host_obj = merged_db[ip]
        host_obj["commands"] = list(host_obj["commands"])
        final_output["hosts"][ip] = host_obj

    print(f"--- Merging Completed: {final_output['total_hosts']} unique hosts found ---")
    return final_output