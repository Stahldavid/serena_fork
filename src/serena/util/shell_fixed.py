import os
import platform
import subprocess

from pydantic import BaseModel


class ShellCommandResult(BaseModel):
    stdout: str
    return_code: int
    cwd: str
    stderr: str | None = None


def execute_shell_command(command: str, cwd: str | None = None, capture_stderr: bool = False) -> ShellCommandResult:
    """
    Execute a shell command and return the output.

    :param command: The command to execute.
    :param cwd: The working directory to execute the command in. If None, the current working directory will be used.
    :param capture_stderr: Whether to capture the stderr output.
    :return: The output of the command.
    """
    if cwd is None:
        cwd = os.getcwd()

    # Comprehensive Windows fix with multiple fallback approaches
    is_windows = platform.system() == "Windows"
    
    if is_windows:
        # Windows-specific handling with fallbacks
        approaches = [
            # Approach 1: Use shell=True with original command
            lambda: subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE if capture_stderr else None,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=cwd,
            ),
            # Approach 2: Use cmd.exe explicitly
            lambda: subprocess.Popen(
                f"cmd /c {command}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE if capture_stderr else None,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=cwd,
            ),
            # Approach 3: Use cmd.exe as list
            lambda: subprocess.Popen(
                ["cmd", "/c", command],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE if capture_stderr else None,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=cwd,
            ),
        ]
        
        # Try each approach until one works
        for i, approach in enumerate(approaches):
            try:
                process = approach()
                break
            except (FileNotFoundError, OSError) as e:
                if i == len(approaches) - 1:  # Last approach failed
                    raise FileNotFoundError(f"All Windows command execution approaches failed. Last error: {e}")
                continue
    else:
        # Unix-like systems - use shell=False for better security
        try:
            # Try as list first (safer)
            process = subprocess.Popen(
                command.split() if isinstance(command, str) else command,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE if capture_stderr else None,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=cwd,
            )
        except (FileNotFoundError, OSError):
            # Fallback to shell=True for complex commands
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE if capture_stderr else None,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=cwd,
            )

    stdout, stderr = process.communicate()
    return ShellCommandResult(stdout=stdout, stderr=stderr, return_code=process.returncode, cwd=cwd)
