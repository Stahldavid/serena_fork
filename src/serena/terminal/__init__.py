"""
Terminal management module for Serena MCP Server.
Based on Desktop Commander MCP Server terminal functionality.
"""

# In serena/terminal/__init__.py
from .terminal_manager import ImprovedTerminalManager as TerminalManager
from .command_manager import CommandManager
from .terminal_handlers import (
    handle_execute_command,
    handle_read_output,
    handle_force_terminate,
    handle_list_sessions
)
from .process_tools import handle_list_processes, handle_kill_process
from .terminal_types import (
    TerminalSession,
    CommandExecutionResult,
    ActiveSessionInfo,
    CompletedSession,
    ProcessInfo,
    CommandValidationResult,
    TerminalError
)

__all__ = [
    "TerminalManager",
    "CommandManager",
    "handle_execute_command",
    "handle_read_output", 
    "handle_force_terminate",
    "handle_list_sessions",
    "handle_list_processes",
    "handle_kill_process",
    "TerminalSession",
    "CommandExecutionResult",
    "ActiveSessionInfo",
    "CompletedSession",
    "ProcessInfo",
    "CommandValidationResult",
    "TerminalError"
]
