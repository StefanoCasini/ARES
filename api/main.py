from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ruamel.yaml import YAML
from api.state import GLOBAL_SCAN_STATE
from ares import run_core_pipeline
import os
from datetime import datetime
import json

app = FastAPI()

# --- (REMOVED Antigravity's fake mock thread entirely) ---

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.yml')

@app.get("/api/config")
def get_config():
    yaml = YAML()
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.load(f)
    return config

def update_dict(target, source):
    for k, v in source.items():
        if k in target and isinstance(target[k], dict) and isinstance(v, dict):
            update_dict(target[k], v)
        elif k in target and isinstance(target[k], list) and isinstance(v, list):
            if target[k] and isinstance(target[k][0], dict) and 'name' in target[k][0]:
                target_by_name = {item['name']: item for item in target[k]}
                for s_item in v:
                    if isinstance(s_item, dict) and 'name' in s_item and s_item['name'] in target_by_name:
                        update_dict(target_by_name[s_item['name']], s_item)
            else:
                target[k] = v
        else:
            target[k] = v

@app.post("/api/config")
async def update_config(request: Request):
    new_config = await request.json()
    yaml = YAML()
    yaml.preserve_quotes = True
    
    with open(CONFIG_PATH, 'r') as f:
        existing_config = yaml.load(f)
        
    update_dict(existing_config, new_config)
    
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(existing_config, f)
        
    return {"status": "success"}

def execute_scan_task(config_data, timestamp):
    try:
        GLOBAL_SCAN_STATE["is_running"] = True
        run_core_pipeline(config_data, timestamp)
    finally:
        GLOBAL_SCAN_STATE["is_running"] = False

@app.post("/api/scan/start")
def start_scan(background_tasks: BackgroundTasks):
    if GLOBAL_SCAN_STATE["is_running"]:
        return {"message": "Scan already running!"}
    
    # 1. Read the ACTUAL config file
    yaml = YAML()
    with open(CONFIG_PATH, 'r') as f:
        real_config = yaml.load(f)
        
    # 2. Generate a REAL timestamp
    real_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")

    # 3. Pass the real data to your core engine
    background_tasks.add_task(execute_scan_task, real_config, real_timestamp)
    
    return {"message": "Scan initiated", "target": real_config.get("mode", {}).get("target", "Unknown")}

@app.get("/api/scan/status")
def get_scan_status():
    tasks_list = list(GLOBAL_SCAN_STATE["tasks"].values())
    return {
        "is_running": GLOBAL_SCAN_STATE["is_running"],
        "tasks": tasks_list
    }

@app.get("/api/results")
def list_results():
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    if not os.path.exists(output_dir):
        return []
        
    json_files = []
    for f in os.listdir(output_dir):
        file_path = os.path.join(output_dir, f)
        if os.path.isfile(file_path) and f.endswith('.json'):
            json_files.append(f)
            
    json_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
    return json_files

@app.get("/api/results/{filename}")
def get_result(filename: str):
    if "/" in filename or "\\" in filename or not filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    file_path = os.path.join(output_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return {"filename": filename, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))