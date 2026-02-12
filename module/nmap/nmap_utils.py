def unify_nmap_list(nmap_scan_data):
    """
    Normalize and unify the merged Nmap scan structure.

    Input example:
    {
        "192.168.1.10": {
            "ports": {
                "80": {"state": "open", "service": "http"},
                "22": {"state": "open", "service": "ssh"},
            },
            "hostnames": ["example.com"],
            "os": None
        }
    }

    Returns a normalized structure:
    {
        "192.168.1.10": {
            "ports": [...],
            "hostnames": [...],
            "os": ...
        }
    }
    """
    final = {}

    for ip, data in nmap_scan_data.items():

        # Ensure structure correctness
        ports = data.get("ports", {})
        hostnames = data.get("hostnames", [])
        osinfo = data.get("os")

        # Normalize ports into list of objects
        normalized_ports = []
        for port, pdata in ports.items():
            normalized_ports.append({
                "port": int(port),
                "state": pdata.get("state", "unknown"),
                "service": pdata.get("service", None),
                "protocol": pdata.get("protocol", "tcp"),
            })

        # Sort ports numerically
        normalized_ports = sorted(normalized_ports, key=lambda x: x["port"])

        # Remove duplicates from hostnames while preserving order
        seen = set()
        normalized_hostnames = []
        for hn in hostnames:
            if hn not in seen:
                normalized_hostnames.append(hn)
                seen.add(hn)

        # Build final structure
        final[ip] = {
            "ports": normalized_ports,
            "hostnames": normalized_hostnames,
            "os": osinfo,
        }

    return final

def deep_merge_nmap_data(nmap_scan_data):
    """
    Merges a list of Nmap dictionaries (e.g., Discovery Scan + Port Scan)
    into a single master dictionary keyed by IP.
    """
    merged = {}

    for partial_dict in nmap_scan_data:
        if not partial_dict: continue

        for ip, data in partial_dict.items():
            # Ensure structure correctness
            hostnames = data.get("hostnames") or []
            ports = data.get("ports") or []
            osinfo = data.get("os") or []
            cpes = data.get("cpes") or []

            if ip not in merged:
                merged[ip]=data
            else:
                #check if hostnames could be update
                for host in hostnames:
                    if host not in merged[ip].get("hostnames", []):
                        merged[ip]["hostnames"].append(host)
                #check if cpes could be update
                for cpe in cpes:
                    if cpe not in merged[ip].get("cpes", []):
                        merged[ip]["cpes"].append(cpe)
                #check if osinfo could be update
                for oi in osinfo:
                    if oi not in merged[ip].get("os", []):
                        merged[ip]["os"].append(oi)
                #check if ports could be update
                for port in ports:
                    if port not in merged[ip].get("ports", []):
                        merged[ip]["ports"].update({port:ports[port]})

    return merged