from pathlib import Path
from module.nmap.nmap_parser import NmapParser
from module.masscan.masscan_parser import MasscanParser
from module.smap.smap_parser import SmapParser
from module.dtos.ParsedDataDTO import ParsedDataDTO

# PARSER_REGISTRY = {
#     "parser_nmap": NmapParser,
#     "parser_masscan": MasscanParser
# }

PARSER_REGISTRY = {
    "parser_nmap": NmapParser,
    "parser_masscan": MasscanParser,
    "parser_smap": SmapParser
} # TODO: move parser_registry in a separate file

def get_parser(file_path: Path):
    """
    Iterates through the registry to find a parser that accepts this file.
    """
    for parser_cls in PARSER_REGISTRY.values():
        try:
            if parser_cls.can_handle(file_path):
                return parser_cls() # Return an instance
        except Exception as e:
            # If a check crashes, log it safely and move to next
            print(f"[DEBUG] Check failed for {parser_cls.__name__}: {e}")
            continue
    return None

def parse_all_files(file_path_list: list) -> list[ParsedDataDTO]:
    print(f"\n--- 🔍 Parsing files ---")
    
    # Dictionary to store all parsed data
    # Structure: { "nmap_scan.xml": { ...data... }, "masscan.json": { ...data... } }
    aggregated_results = []

    # Sort files to keep order consistent
    # iterdir() gets all files in the timestamp folder
    for entry in file_path_list:
        file_path = Path(entry)

        if not file_path.is_file():
            continue

        parser = get_parser(file_path)

        if parser:
            print(f"   Parsing {file_path.name} using {parser.__class__.__name__}...")
            try:
                # 2. Run the parse method
                # This assumes every Parser class has a .parse(file_path) method
                parsed_data = parser.parse(file_path)
                
                # 3. Store result
                if parsed_data:
                    aggregated_results.append(parsed_data)
                    host_count = len(parsed_data.data) 
                    tool = parsed_data.tool_name
                    print(f"   Parsed {host_count} hosts from {file_path.name} [{tool}] ")
                
            except ValueError as e:
                # This happens for files we don't recognize (like logs)
                print(f"   Skip {file_path.name}: {e}")
            except Exception as e:
                print(f"   Error parsing {file_path.name}: {e}")

    print(f"--- Parsing Completed. Processed {len(aggregated_results)} files. ---")
    return aggregated_results