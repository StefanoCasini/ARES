import time
from rich.table import Table
from rich import box

class TaskMonitor:
    def __init__(self):
        self.tasks = {}  # Stores task data: {task_id: {name, status, start_time, duration}}
        
    def add_task(self, task_id, command_name, target, raw_command):
        """Register a new task with a 'Ready' status"""
        self.tasks[task_id] = {
            "name": command_name,
            "target": target,
            "status": "[grey]Ready[/grey]", # Rich formatting
            "start": None,
            "duration": "...",
            "command": raw_command
        }

    def update_task(self, task_id, status="done"):
        """Update a task to Done or Error"""
        if status == "done":
            if task_id in self.tasks:
                elapsed = time.time() - self.tasks[task_id]["start"]
                self.tasks[task_id]["duration"] = f"{elapsed:.2f}s"
            color = "[green]"
        elif status == "running":
            color = "[yellow]"
            self.tasks[task_id]["start"] = time.time()
        else:
            if task_id in self.tasks:
                elapsed = time.time() - self.tasks[task_id]["start"]
                self.tasks[task_id]["duration"] = f"{elapsed:.2f}s"
            color = "[red]"

        self.tasks[task_id]["status"] = f"{color}{status.upper()}[/]"
            
    def generate_table(self):
        """Creates the table structure for the Live display"""
        table = Table(box=box.ROUNDED, title="ARESS Execution")
        
        table.add_column("Tool", style="cyan")
        table.add_column("Target", style="magenta")
        table.add_column("Status", justify="center")
        table.add_column("Duration", justify="right")
        table.add_column("Command", style="dim")

        for _, data in self.tasks.items():
            table.add_row(
                data["name"],
                data["target"],
                data["status"],
                data["duration"],
                data["command"]
            )
        return table