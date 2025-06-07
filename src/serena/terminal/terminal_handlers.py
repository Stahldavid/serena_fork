"""
Terminal command handlers - SIMPLIFIED VERSION
Based on Desktop Commander MCP pattern that works reliably
"""

from typing import Dict, Any, List
from .terminal_manager import ImprovedTerminalManager
from .command_manager import CommandManager
from .terminal_types import TerminalError
import asyncio
import time
import logging

log = logging.getLogger(__name__)

# Global instances
terminal_manager = ImprovedTerminalManager()
command_manager = CommandManager()


async def handle_execute_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handler for execute_command tool - Desktop Commander style"""
    try:
        command = args.get("command", "").strip()
        timeout_ms = args.get("timeout_ms", 30000)  # Default 30 seconds
        shell = args.get("shell")
        cwd = args.get("cwd")  # Working directory for command execution
        
        if not command:
            return {
                "content": [{"type": "text", "text": "Error: Command cannot be empty"}],
                "isError": True
            }
        
        # Simple validation (no complex parsing)
        try:
            validation_result = command_manager.validate_command(command)
            if not validation_result.is_valid:
                return {
                    "content": [{"type": "text", "text": f"Error: {validation_result.reason}"}],
                    "isError": True
                }
        except Exception:
            # If validation fails, continue (fail-safe approach)
            pass
        
        # Execute command using simplified approach
        try:
            result = await terminal_manager.execute_command(command, timeout_ms, shell, cwd)
        except Exception as e:
            log.error(f"Error executing command: {e}")
            return {
                "content": [{"type": "text", "text": f"Error executing command: {str(e)}"}],
                "isError": True
            }
        
        if result.pid == -1:
            return {
                "content": [{"type": "text", "text": result.initial_output}],
                "isError": True
            }
        
        # Build response - Desktop Commander style
        if not result.is_blocked:
            # Command completed - return direct output
            output_text = result.initial_output.strip() if result.initial_output.strip() else "(no output)"
            return {
                "content": [{"type": "text", "text": output_text}]
            }
        else:
            # Command still running - return PID format
            output_text = f"Command started with PID {result.pid}"
            
            if result.initial_output.strip():
                output_text += f"\nInitial output:\n{result.initial_output}"
            
            output_text += "\nCommand is still running. Use read_output to get more output."
            
            return {
                "content": [{"type": "text", "text": output_text}]
            }
        
    except Exception as e:
        log.error(f"Unexpected error in handle_execute_command: {e}")
        return {
            "content": [{"type": "text", "text": f"Unexpected error: {str(e)}"}],
            "isError": True
        }


async def handle_read_output(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handler for read_output tool - Desktop Commander style"""
    try:
        pid = args.get("pid")
        timeout_ms = args.get("timeout_ms", 5000)
        
        if not isinstance(pid, int):
            return {
                "content": [{"type": "text", "text": "Error: PID must be an integer"}],
                "isError": True
            }
        
        # Check if the process exists first
        session = terminal_manager.get_session(pid)
        if not session:
            # Check completed sessions too
            completed_output = terminal_manager.get_new_output(pid)
            if completed_output:
                return {
                    "content": [{"type": "text", "text": completed_output}]
                }
            else:
                return {
                    "content": [{"type": "text", "text": f"No session found for PID {pid}"}],
                    "isError": True
                }
        
        # Desktop Commander style output polling with timeout
        timeout_seconds = timeout_ms / 1000.0
        start_time = time.time()
        
        while (time.time() - start_time) < timeout_seconds:
            output = terminal_manager.get_new_output(pid)
            if output and output.strip():
                return {
                    "content": [{"type": "text", "text": output}]
                }
            await asyncio.sleep(0.3)  # Poll every 300ms like Desktop Commander
        
        # After timeout, check one more time for any output
        final_output = terminal_manager.get_new_output(pid)
        if final_output and final_output.strip():
            return {
                "content": [{"type": "text", "text": final_output}]
            }
        else:
            return {
                "content": [{"type": "text", "text": "No new output available (timeout reached)"}]
            }
        
    except Exception as e:
        log.error(f"Error in handle_read_output: {e}")
        return {
            "content": [{"type": "text", "text": f"Error reading output: {str(e)}"}],
            "isError": True
        }


async def handle_force_terminate(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handler for force_terminate tool - Desktop Commander style"""
    try:
        pid = args.get("pid")
        
        if not isinstance(pid, int):
            return {
                "content": [{"type": "text", "text": "Error: PID must be an integer"}],
                "isError": True
            }
        
        success = terminal_manager.force_terminate(pid)
        
        if success:
            return {
                "content": [{"type": "text", "text": f"Successfully initiated termination of session {pid}"}]
            }
        else:
            return {
                "content": [{"type": "text", "text": f"No active session found for PID {pid}"}]
            }
            
    except Exception as e:
        log.error(f"Error in handle_force_terminate: {e}")
        return {
            "content": [{"type": "text", "text": f"Error terminating session: {str(e)}"}],
            "isError": True
        }


async def handle_list_sessions(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handler for list_sessions tool - Desktop Commander style"""
    try:
        sessions = terminal_manager.list_active_sessions()
        
        if not sessions:
            return {
                "content": [{"type": "text", "text": "No active sessions"}]
            }
        
        session_info = []
        for session in sessions:
            session_info.append(
                f"PID: {session.pid}, "
                f"Blocked: {session.is_blocked}, "
                f"Runtime: {session.runtime_seconds:.1f}s"
            )
        
        return {
            "content": [{"type": "text", "text": "\n".join(session_info)}]
        }
        
    except Exception as e:
        log.error(f"Error in handle_list_sessions: {e}")
        return {
            "content": [{"type": "text", "text": f"Error listing sessions: {str(e)}"}],
            "isError": True
        }
