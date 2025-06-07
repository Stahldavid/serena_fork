"""
Process management tools.
Based on Desktop Commander MCP Server process management.
"""

import os
import signal
import subprocess
import sys
from typing import List, Dict, Any
from .terminal_types import ProcessInfo


async def handle_list_processes() -> Dict[str, Any]:
    """List all running processes on the system"""
    try:
        processes = []
        
        if sys.platform == "win32":
            # Windows: use tasklist
            result = subprocess.run(
                ["tasklist", "/fo", "csv"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines[:50]:  # Limit to 50 processes
                    try:
                        parts = line.strip().split('","')
                        if len(parts) >= 5:
                            name = parts[0].strip('"')
                            pid = parts[1].strip('"')
                            memory = parts[4].strip('"')
                            
                            processes.append(ProcessInfo(
                                pid=int(pid),
                                command=name,
                                cpu="N/A",  # Windows tasklist doesn't provide CPU%
                                memory=memory
                            ))
                    except (ValueError, IndexError):
                        continue
        else:
            # Unix/Linux: use ps
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines[:50]:  # Limit to 50 processes
                    try:
                        parts = line.split()
                        if len(parts) >= 11:
                            processes.append(ProcessInfo(
                                pid=int(parts[1]),
                                command=parts[10],
                                cpu=parts[2],
                                memory=parts[3]
                            ))
                    except (ValueError, IndexError):
                        continue
        
        if not processes:
            return {
                "content": [{"type": "text", "text": "No processes found or unable to list processes"}]
            }
        
        # Format output
        process_list = []
        for p in processes:
            process_list.append(
                f"PID: {p.pid}, Command: {p.command}, CPU: {p.cpu}, Memory: {p.memory}"
            )
        
        return {
            "content": [{"type": "text", "text": "\n".join(process_list)}]
        }
        
    except subprocess.TimeoutExpired:
        return {
            "content": [{"type": "text", "text": "Error: Process listing timed out"}],
            "isError": True
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error listing processes: {str(e)}"}],
            "isError": True
        }


async def handle_kill_process(args: Dict[str, Any]) -> Dict[str, Any]:
    """Terminate a process by PID"""
    try:
        pid = args.get("pid")
        
        if not isinstance(pid, int):
            return {
                "content": [{"type": "text", "text": "Error: PID must be an integer"}],
                "isError": True
            }
        
        if pid <= 0:
            return {
                "content": [{"type": "text", "text": "Error: Invalid PID"}],
                "isError": True
            }
        
        # Safety check: don't allow killing system critical processes
        critical_pids = [0, 1, 2, 4]  # Common system process PIDs
        if pid in critical_pids:
            return {
                "content": [{"type": "text", "text": f"Error: Cannot kill system critical process {pid}"}],
                "isError": True
            }
        
        try:
            if sys.platform == "win32":
                # Windows: use taskkill
                result = subprocess.run(
                    ["taskkill", "/F", "/PID", str(pid)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        "content": [{"type": "text", "text": f"Successfully terminated process {pid}"}]
                    }
                else:
                    return {
                        "content": [{"type": "text", "text": f"Failed to terminate process {pid}: {result.stderr}"}],
                        "isError": True
                    }
            else:
                # Unix/Linux: use os.kill
                os.kill(pid, signal.SIGTERM)
                return {
                    "content": [{"type": "text", "text": f"Successfully sent SIGTERM to process {pid}"}]
                }
                
        except ProcessLookupError:
            return {
                "content": [{"type": "text", "text": f"Process {pid} not found"}],
                "isError": True
            }
        except PermissionError:
            return {
                "content": [{"type": "text", "text": f"Permission denied: cannot kill process {pid}"}],
                "isError": True
            }
        except subprocess.TimeoutExpired:
            return {
                "content": [{"type": "text", "text": f"Timeout while trying to kill process {pid}"}],
                "isError": True
            }
            
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error killing process: {str(e)}"}],
            "isError": True
        }
