import subprocess
import threading
import time
import sys
from datetime import datetime
from typing import Dict, Optional, List
import logging
from .terminal_types import (TerminalSession, CommandExecutionResult, ActiveSessionInfo, CompletedSession)

log = logging.getLogger(__name__)

class ImprovedTerminalManager:
    """Simple, reliable terminal manager based on Desktop Commander pattern"""
    
    def __init__(self, max_completed_sessions: int = 100):
        self.sessions: Dict[int, TerminalSession] = {}
        self.completed_sessions: Dict[int, CompletedSession] = {}
        self.max_completed_sessions = max_completed_sessions
        self._lock = threading.Lock()

    async def execute_command(self, command: str, timeout_ms: int = 30000, shell: Optional[str] = None, cwd: Optional[str] = None) -> CommandExecutionResult:
        """Execute command with proper timeout handling - Desktop Commander style"""
        try:
            # Start process
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                cwd=cwd  # Set working directory if provided
            )
            
            if process.pid is None:
                return CommandExecutionResult(
                    pid=-1,
                    initial_output="Error: Failed to get process ID. The command could not be executed.",
                    is_blocked=False
                )

            # Create session
            session = TerminalSession(
                pid=process.pid,
                process=process,
                command=command,
                start_time=datetime.now(),
                output_lines=[],
                last_read_offset=0,
                is_blocked_flag=False
            )
            
            with self._lock:
                self.sessions[process.pid] = session

            # Start background thread for continuous output collection
            threading.Thread(
                target=self._handle_process_lifecycle, 
                args=(session,), 
                daemon=True
            ).start()
            
            # Wait for timeout or completion - Desktop Commander style
            timeout_seconds = timeout_ms / 1000.0
            initial_output = ""
            start_time = time.time()
            
            # Collect output during timeout period
            while (time.time() - start_time) < timeout_seconds:
                # Check if process completed
                if process.poll() is not None:
                    # Process finished - collect all output and return it directly
                    time.sleep(0.1)  # Give time for output collection
                    with self._lock:
                        initial_output = ''.join(session.output_lines)
                    
                    return CommandExecutionResult(
                        pid=process.pid,
                        initial_output=initial_output,
                        is_blocked=False  # Command completed
                    )
                
                # Process still running - collect partial output
                with self._lock:
                    current_output = ''.join(session.output_lines)
                    if current_output != initial_output:
                        initial_output = current_output
                
                time.sleep(0.1)  # Small sleep to prevent busy waiting
            
            # Timeout reached and process still running
            with self._lock:
                session.is_blocked_flag = True
                initial_output = ''.join(session.output_lines)
            
            return CommandExecutionResult(
                pid=process.pid,
                initial_output=initial_output,
                is_blocked=True  # Command still running after timeout
            )
            
        except Exception as e:
            log.error(f"Error executing command: {e}")
            return CommandExecutionResult(
                pid=-1, 
                initial_output=f"Error executing command: {str(e)}", 
                is_blocked=False
            )

    def _handle_process_lifecycle(self, session: TerminalSession) -> None:
        """Handle process completion - Desktop Commander style"""
        try:
            # Continue reading output until process completes
            while session.process.poll() is None:
                try:
                    line = session.process.stdout.readline()
                    if line:
                        with self._lock:
                            session.output_lines.append(line)
                    else:
                        time.sleep(0.1)
                except Exception:
                    break
            
            # Read any remaining output
            try:
                remaining = session.process.stdout.read()
                if remaining:
                    with self._lock:
                        session.output_lines.append(remaining)
            except Exception:
                pass
            
            # Store completed session
            exit_code = session.process.returncode
            end_time = datetime.now()
            final_output = ''.join(session.output_lines)
            
            completed = CompletedSession(
                pid=session.pid,
                command=session.command,
                final_output=final_output,
                exit_code=exit_code,
                start_time=session.start_time,
                end_time=end_time
            )
            
            with self._lock:
                self.completed_sessions[session.pid] = completed
                if session.pid in self.sessions:
                    del self.sessions[session.pid]
                
                # Keep only last N completed sessions
                if len(self.completed_sessions) > self.max_completed_sessions:
                    oldest_pid = min(self.completed_sessions.keys())
                    del self.completed_sessions[oldest_pid]
                    
        except Exception as e:
            log.error(f"Error handling process lifecycle: {e}")

    def get_new_output(self, pid: int) -> Optional[str]:
        """Get new output since last read - Desktop Commander style"""
        with self._lock:
            # Check active sessions first
            session = self.sessions.get(pid)
            if session:
                new_lines = session.output_lines[session.last_read_offset:]
                session.last_read_offset = len(session.output_lines)
                return ''.join(new_lines)
            
            # Check completed sessions
            completed_session = self.completed_sessions.get(pid)
            if completed_session:
                runtime = completed_session.runtime_seconds
                return f"Process completed with exit code {completed_session.exit_code}\nRuntime: {runtime:.2f}s\nFinal output:\n{completed_session.final_output}"
            
            return None

    def force_terminate(self, pid: int) -> bool:
        """Terminate process - Desktop Commander style"""
        with self._lock:
            session = self.sessions.get(pid)
            if not session:
                return False
            
        try:
            import signal
            
            if sys.platform == "win32":
                session.process.terminate()
                # Set timer for force kill if needed
                threading.Timer(1.0, lambda: self._force_kill_if_needed(session)).start()
            else:
                try:
                    session.process.send_signal(signal.SIGINT)
                    threading.Timer(1.0, lambda: self._force_kill_if_needed(session)).start()
                except Exception:
                    session.process.terminate()
            
            return True
            
        except Exception as e:
            log.error(f"Failed to terminate process {pid}: {e}")
            return False

    def _force_kill_if_needed(self, session: TerminalSession) -> None:
        """Force kill if process hasn't terminated"""
        try:
            if session.process.poll() is None:
                session.process.kill()
        except Exception:
            pass

    def get_session(self, pid: int) -> Optional[TerminalSession]:
        """Get session by PID"""
        with self._lock:
            return self.sessions.get(pid)

    def list_active_sessions(self) -> List[ActiveSessionInfo]:
        """List all active sessions"""
        now = datetime.now()
        with self._lock:
            return [
                ActiveSessionInfo(
                    pid=session.pid,
                    command=session.command,
                    is_blocked=session.is_blocked_flag,
                    runtime_seconds=(now - session.start_time).total_seconds(),
                    start_time=session.start_time
                )
                for session in self.sessions.values()
            ]

    def list_completed_sessions(self) -> List[CompletedSession]:
        """List all completed sessions"""
        with self._lock:
            return list(self.completed_sessions.values())
