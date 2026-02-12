from concurrent.futures import ThreadPoolExecutor, as_completed
from module.masscan.masscan_generator import MasscanGenerator
from module.nmap.nmap_generator import NmapGenerator
from module.smap.smap_generator import SmapGenerator
from utils.permission import fix_ownership
from utils.ui import TaskMonitor
from pathlib import Path
from rich.live import Live
import xml.etree.ElementTree as ET
import json
import shlex
import subprocess
import time


# Registry of available generator classes
GENERATOR_REGISTRY = {
    "launcher_nmap": NmapGenerator,
    "launcher_masscan": MasscanGenerator,
    "launcher_smap": SmapGenerator
} # TODO: move generator_registry in a separate file

def create_output_directory(target, base_path, timestamp):
    # create a folder inside output/raw called iptarget_timestamp to store all scan outputs
    target_clean = target.replace("/", "_")
    folder_name = timestamp+"_"+target_clean
    folder_path = Path(base_path) / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)

    fix_ownership(folder_path)
    print(f"[-] Created Output Directory: {folder_path.absolute()}")
    return folder_path

def get_tasks(mode, target, folder_path):
    possible_tasks = []

    for key, tool_config in mode.items():
        if key.startswith("launcher_") and tool_config.get("enabled", False):
            if key in GENERATOR_REGISTRY:
                generator_class = GENERATOR_REGISTRY[key]
                generator = generator_class(output_dir=folder_path)
            else:
                #fall back option with generic generator (not implemented yet)
                tool_name = key.replace("launcher_", "")
                #generator = GenericGenerator(output_dir=folder_path, tool_name=tool_name)

            tasks = generator.generate_commands(tool_config, target)
            possible_tasks.extend(tasks)
            print(f"[-] {key} generated {len(tasks)} tasks")
    # print("\n--- Command Queue (possible_tasks) ---")
    # for i, task in enumerate(possible_tasks):
    #     print(f"[{i+1}] {task}")
    return possible_tasks

def wrapper_output_json(command: str, output_file: Path):
    try:
        with open(output_file, "r") as f:
            try:
                raw_data = json.load(f)
            except json.JSONDecodeError:
                f.seek(0)
                raw_data = f.read().strip()
        
        wrapped_data = {
            "command":command,
            "data":raw_data
        }

        with open(output_file, "w") as f:
            json.dump(wrapped_data, f, indent=4)
        
        # print(f"[WRAP] Wrapped output in {output_file.name}")

    except Exception as e:
        print(f"[ERROR] Failed to wrap output for {command}: {str(e)}")

def run_command_task(command: str, output_file: Path, tool_name: str):
    # print(f"[START] {command}")
    start_time = time.time()
    
    try:
        # shlex.split is crucial: it correctly handles spaces inside quotes
        # e.g., 'nmap -o "my file.xml"' -> ['nmap', '-o', 'my file.xml']
        args = shlex.split(command)
        # Run the command and capture output
        # check=True raises CalledProcessError if return code != 0
        result = subprocess.run(
            args, 
            capture_output=True, 
            text=True, 
            check=True
        )
        elapsed = time.time() - start_time
        # print(f"[DONE] {command} ({elapsed:.2f}s)")

        # Wrap ANY tool output if it is a JSON file (Smap, Masscan, etc.)
        if output_file and output_file.exists() and output_file.suffix == ".json":
            wrapper_output_json(command, output_file)

        return {"cmd": command, "status": "success", "output": result.stdout}

    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"[FAIL] {command} (Exit Code: {e.returncode})")
        return {"cmd": command, "status": "error", "error": e.stderr}
        
    except Exception as e:
        print(f"[CRASH] {command}: {str(e)}")
        return {"cmd": command, "status": "crash", "error": str(e)}

def execute_tasks(possible_tasks, nthreads):
    # print(f"\n--- Starting Execution (Threads: {nthreads}) ---")
    monitor = TaskMonitor()
    results = []

    # 1. Define the Wrapper Function
    # This runs INSIDE the thread. It updates the UI, then runs the command.
    def task_wrapper(task_id, cmd, output_file, tool_name):
        # A. Signal that we have left the queue and entered the CPU
        monitor.update_task(task_id, status="running")
        
        # B. Run the ACTUAL heavy lifting
        return run_command_task(cmd, output_file, tool_name)

    with Live(monitor.generate_table(), refresh_per_second=4) as live:
        with ThreadPoolExecutor(max_workers=nthreads) as executor:
            # 1. Submit all tasks to the pool
            # future_to_cmd maps the "future" object back to the command string
            #future_to_cmd = {executor.submit(run_command_task, cmd): cmd for cmd in possible_tasks}
            future_to_task = {}
            for i, task_struct in enumerate(possible_tasks):
                task_id = i

                cmd = task_struct.get("command")
                output_file = task_struct.get("output_file")
                tool_name = task_struct.get("tool_name", "unknown")

                try:
                    target_display = cmd[-1] if isinstance(cmd, list) else cmd.split()[-1]
                except:
                    target_display = "Unknown"

                # 1. Add row to UI as "Ready" (Grey) -> Register with Monitor (Status: Grey "Ready...")
                monitor.add_task(task_id, tool_name, target_display, cmd)

                # Submit to thread pool
                future = executor.submit(task_wrapper, task_id, cmd, output_file, tool_name) 
                # task_wrapper contains UI updates for the status of the command and the specific command to run

                # Register with Monitor (Status: Grey "Ready...")
                # We use the 'future' object as the unique ID

                future_to_task[future] = {
                    "task_id": task_id,
                    "cmd": cmd,
                    "output_file": output_file
                }

            # Force an initial update of the table so user sees all tasks "Running"
            live.update(monitor.generate_table())

            # 2. Process results as they finish (in order of completion, not submission)
            for future in as_completed(future_to_task):
                task_context = future_to_task[future]
                cmd = task_context["cmd"]
                output_file = task_context["output_file"]
                try:
                    data = future.result()
                    results.append(data)

                    # Update Monitor: Success (Green "DONE")
                    monitor.update_task(task_id=task_context["task_id"], status="done")

                    # Fix ownership after each task (if running with sudo)
                    if output_file:
                        fix_ownership(Path(output_file))
                except Exception as exc:
                    # Update Monitor: Failure (Red "ERROR")
                    monitor.update_task(task_id=task_context["task_id"], status="error")
                    # print(f"Task {cmd} generated an exception: {exc}") #TODO: ideally, log the actual exception to a file, not stdout
                
                # Refresh table immediately after a task finishes
                live.update(monitor.generate_table())
        # print("--- All Tasks Completed ---")
    return results

# ---------------------------------------------------------
# MAIN LAUNCHER LOGIC
# ---------------------------------------------------------
def run_scanners(config, timestamp):
    mode = config.get("mode", {})
    target = mode.get("target")
    base_path = mode.get("base_output_raw_path", "output/raw")

    if not target:
        print("[!] Error: No 'target' found in config.")
        return

    print(f"[-] Target: {target}")
    print("[-] Starting parallel scans...")

    folder_path = create_output_directory(target, base_path, timestamp)
    
    possible_tasks = get_tasks(mode, target, folder_path)
    
    nthreads = mode.get("n_threads", 1)
    execute_tasks(possible_tasks, nthreads)
    
    files = [item for item in folder_path.iterdir() if item.is_file()]
    return files