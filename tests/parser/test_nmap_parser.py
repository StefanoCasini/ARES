import json
import os

from module.nmap.nmap_utils import deep_merge_nmap_data
import module.nmap.nmap_parser 

def test_nmap_parser():
    n_threads = 2
    output_path = "nmap_parser_result" 
    input_dir = "module/nmap/scans"

    thread_option = [
        ("-sn -Pn", os.path.join(input_dir, "host_discovery.xml")),
        ("--top-ports 100 -sS", os.path.join(input_dir, "top_100_tcp_ports_sys.xml")),
        ("--top-ports 100 -sU", os.path.join(input_dir, "top_100_udp_ports.xml")),
        #aggressive altro tread
    ]
    
    # Merge results
    print("[+] Merging XML results...")
    nmap_scan_data = []
    for i in range(n_threads):
        nmap_scan_file = thread_option[i][1]
        NmapParser = module.nmap.nmap_parser.NmapParser()
        data = NmapParser.parse(nmap_scan_file)
        nmap_scan_data.append(data)  # xml_output paths
        

    # nmap_merged_data = unify_nmap_list(nmap_scan_data)
    nmap_merged_data = deep_merge_nmap_data(nmap_scan_data)
    with open(output_path, 'w') as output_file:
            json.dump(nmap_merged_data, output_file, indent=4)
    print(f"[+] Merged data contains {len(nmap_merged_data)} unique hosts and save results in {output_path}")

    return nmap_merged_data

if __name__ == "__main__":
    test_nmap_parser()
