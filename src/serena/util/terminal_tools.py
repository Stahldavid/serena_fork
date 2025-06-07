"""
Fixed terminal tools with timeout handling.
"""

import asyncio
from typing import Optional
from ..terminal import (
    handle_execute_command,
    handle_read_output,
    handle_force_terminate,
    handle_list_sessions,
    handle_list_processes,
    handle_kill_process
)
from .async_utils import run_coroutine_with_timeout

class TerminalExecutorLogic:
    """Execute terminal commands with timeout."""

    def execute(self, command: str, timeout_ms: int = 30000, shell: Optional[str] = None, cwd: Optional[str] = None) -> str:
        """Execute a terminal command with timeout."""
        try:
            coro = handle_execute_command({
                "command": command,
                "timeout_ms": timeout_ms,
                "shell": shell,
                "cwd": cwd
            })
            
            sync_timeout_seconds = (timeout_ms / 1000.0) + 10
            
            result = run_coroutine_with_timeout(
                coro,
                timeout_seconds=sync_timeout_seconds,
                default_result={
                    "content": [{"type": "text", "text": f"Command timed out."}],
                    "isError": True
                }
            )
            
            if result.get("isError"):
                return f"Error: {result['content'][0]['text']}"
            
            return result["content"][0]["text"]
            
        except Exception as e:
            return f"Error executing command: {str(e)}"


class TerminalReaderLogic:
    """Read output from terminal sessions."""

    def read(self, pid: int, timeout_ms: int = 5000) -> str:
        """Read new output from a running terminal session."""
        try:
            coro = handle_read_output({
                "pid": pid,
                "timeout_ms": timeout_ms
            })
            
            sync_timeout_seconds = (timeout_ms / 1000.0) + 5
            
            result = run_coroutine_with_timeout(
                coro,
                timeout_seconds=sync_timeout_seconds,
                default_result={
                    "content": [{"type": "text", "text": f"Read output timed out for PID {pid}"}],
                    "isError": True
                }
            )
            
            if result.get("isError"):
                return f"Error: {result['content'][0]['text']}"
            
            return result["content"][0]["text"]
            
        except Exception as e:
            return f"Error reading output: {str(e)}"


class TerminalTerminatorLogic:
    """Terminate terminal sessions."""

    def terminate(self, pid: int) -> str:
        """Force terminate a running terminal session."""
        try:
            coro = handle_force_terminate({
                "pid": pid
            })
            
            result = run_coroutine_with_timeout(
                coro,
                timeout_seconds=10.0,
                default_result={
                    "content": [{"type": "text", "text": f"Termination request timed out for PID {pid}"}],
                    "isError": True
                }
            )
            
            if result.get("isError"):
                return f"Error: {result['content'][0]['text']}"
            
            return result["content"][0]["text"]
            
        except Exception as e:
            return f"Error terminating session: {str(e)}"


class TerminalSessionListerLogic:
    """List terminal sessions."""

    def list_sessions(self) -> str:
        """List all active terminal sessions."""
        try:
            coro = handle_list_sessions({})
            
            result = run_coroutine_with_timeout(
                coro,
                timeout_seconds=5.0,
                default_result={
                    "content": [{"type": "text", "text": "List sessions timed out"}],
                    "isError": True
                }
            )
            
            if result.get("isError"):
                return f"Error: {result['content'][0]['text']}"
            
            return result["content"][0]["text"]
            
        except Exception as e:
            return f"Error listing sessions: {str(e)}"


class ProcessListerLogic:
    """List system processes."""

    def list_processes(self) -> str:
        """List all running processes."""
        try:
            coro = handle_list_processes()
            
            result = run_coroutine_with_timeout(
                coro,
                timeout_seconds=10.0,
                default_result={
                    "content": [{"type": "text", "text": "List processes timed out"}],
                    "isError": True
                }
            )
            
            if result.get("isError"):
                return f"Error: {result['content'][0]['text']}"
            
            return result["content"][0]["text"]
            
        except Exception as e:
            return f"Error listing processes: {str(e)}"


class ProcessKillerLogic:
    """Kill system processes."""

    def kill(self, pid: int) -> str:
        """Terminate a running process by PID."""
        try:
            coro = handle_kill_process({
                "pid": pid
            })
            
            result = run_coroutine_with_timeout(
                coro,
                timeout_seconds=10.0,
                default_result={
                    "content": [{"type": "text", "text": f"Kill process timed out for PID {pid}"}],
                    "isError": True
                }
            )
            
            if result.get("isError"):
                return f"Error: {result['content'][0]['text']}"
            
            return result["content"][0]["text"]
            
        except Exception as e:
            return f"Error killing process: {str(e)}"
