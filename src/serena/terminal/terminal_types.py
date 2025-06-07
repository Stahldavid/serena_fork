"""
Types and data structures for terminal management system.
Based on Desktop Commander MCP Server terminal functionality.
"""

from dataclasses import dataclass, field
from subprocess import Popen
from datetime import datetime
from typing import Optional, Dict, Any, List, Deque
from enum import Enum
import asyncio # For asyncio.subprocess.Process and asyncio.Task


@dataclass
class TerminalSession:
    """Represents an active terminal session being managed."""
    pid: int
    process: any  # subprocess.Popen process
    command: str
    start_time: datetime
    output_lines: List[str] = field(default_factory=list)
    # Tracks how much of output_lines has been sent by get_new_output
    last_read_offset: int = 0
    # True if execute_command returned while this session was still running
    is_blocked_flag: bool = False
    # Store the exit code once known, even before moving to CompletedSession
    exit_code: Optional[int] = None


@dataclass
class CommandExecutionResult:
    """Result of a command execution, returned by the manager's execute_command."""
    pid: Optional[int] = None
    initial_output: str = ""
    is_blocked: bool = False  # True if command is still running after initial timeout
    error_message: Optional[str] = None # For errors like failing to start the process


@dataclass
class ActiveSessionInfo:
    """Brief information about an active session, for listing."""
    pid: int
    command: str
    is_blocked: bool # Reflects the is_blocked_flag from TerminalSession
    runtime_seconds: float
    start_time: datetime


@dataclass
class CompletedSession:
    """Represents a terminal session that has finished."""
    pid: int
    command: str
    final_output: str
    exit_code: Optional[int]
    start_time: datetime
    end_time: datetime

    @property
    def runtime_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


@dataclass
class ProcessInfo:
    """System process information"""
    pid: int
    command: str
    cpu: str
    memory: str


class CommandValidationResult:
    """Result of command validation"""
    def __init__(self, is_valid: bool, reason: str = ""):
        self.is_valid = is_valid
        self.reason = reason


class TerminalError(Exception):
    """Custom exception for terminal operations"""
    pass


class ServerSentEvent(Enum):
    TEXT = "text"
    ERROR = "error"
    SYSTEM = "system"
    TERMINAL_OUTPUT = "terminal_output"


@dataclass
class ServerSentEventData:
    type: ServerSentEvent
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type.value, "text": self.text}


@dataclass
class ServerResultContent:
    type: str # Should be "text" for now, mirroring client expectations
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "text": self.text}

@dataclass
class ServerResultDict:
    content: List[ServerResultContent] = field(default_factory=list)
    isError: bool = False
    # Serena specific, not in MCP spec directly
    # but useful for our internal handling
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": [c.to_dict() for c in self.content],
            "isError": self.isError,
            # "tool_name": self.tool_name, # Not sending to client
            # "tool_input": self.tool_input # Not sending to client
        }

    @classmethod
    def from_text(cls, text: str, is_error: bool = False) -> "ServerResultDict":
        return cls(content=[ServerResultContent(type="text", text=text)], isError=is_error)

    @classmethod
    def from_error(cls, error_message: str) -> "ServerResultDict":
        return cls(content=[ServerResultContent(type="text", text=error_message)], isError=True)


class ShellType(Enum):
    POWERSHELL = "powershell"
    CMD = "cmd"
    BASH = "bash"
    ZSH = "zsh"
    PYTHON = "python"
    UNKNOWN = "unknown"
