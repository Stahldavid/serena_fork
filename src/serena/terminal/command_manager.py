"""
Command validation and management system.
Based on Desktop Commander MCP Server command management.
"""

from typing import List, Set, Optional
import re
import shlex
from .terminal_types import CommandValidationResult


class CommandManager:
    """Manages command validation and security"""
    
    def __init__(self, blocked_commands: Optional[List[str]] = None):
        """Initialize with blocked commands list"""
        self.blocked_commands: Set[str] = set(blocked_commands or self._get_default_blocked_commands())
    
    def _get_default_blocked_commands(self) -> List[str]:
        """Get default list of blocked dangerous commands"""
        return [
            # Disk and partition management
            "mkfs", "format", "mount", "umount", "fdisk", "dd", "parted", 
            "diskpart", "fsck", "e2fsck", "gparted",
            
            # System administration and user management
            "sudo", "su", "passwd", "adduser", "useradd", "usermod", 
            "groupadd", "chsh", "visudo", "deluser", "userdel",
            
            # System control
            "shutdown", "reboot", "halt", "poweroff", "init", "systemctl",
            "service", "chkconfig",
            
            # Dangerous file operations
            "chmod 777", "chown", "rm -rf", "del /s", "deltree", 
            "format c:", "rd /s",
            
            # Network and security
            "iptables", "firewall", "netsh", "ufw", "fail2ban",
            
            # Windows system commands
            "sfc", "bcdedit", "reg delete", "net user", "sc delete", 
            "runas", "cipher", "takeown", "icacls"
        ]
    
    def get_base_command(self, command: str) -> str:
        """Extract base command from command string"""
        try:
            # Remove leading/trailing whitespace
            command = command.strip()
            
            # Handle empty command
            if not command:
                return ""
            
            # Split command and get first token
            tokens = shlex.split(command)
            if not tokens:
                return ""
                
            return tokens[0].lower()
        except (ValueError, Exception):
            # If shlex fails, fall back to simple split
            return command.split()[0].lower() if command.split() else ""
    
    def extract_commands(self, command_string: str) -> List[str]:
        """Extract all commands from a complex command string"""
        try:
            commands = []
            
            # Split by common command separators
            separators = [';', '&&', '||', '|', '&']
            
            # Simple splitting approach for now
            parts = [command_string]
            for separator in separators:
                new_parts = []
                for part in parts:
                    new_parts.extend(part.split(separator))
                parts = new_parts
            
            # Extract base command from each part
            for part in parts:
                base_cmd = self.get_base_command(part.strip())
                if base_cmd:
                    commands.append(base_cmd)
            
            return list(set(commands))  # Remove duplicates
            
        except Exception:
            # If extraction fails, return just the base command
            return [self.get_base_command(command_string)]
    
    def validate_command(self, command: str) -> CommandValidationResult:
        """Validate if command is allowed to execute"""
        try:
            if not command or not command.strip():
                return CommandValidationResult(False, "Empty command not allowed")
            
            # Extract all commands from the command string
            commands = self.extract_commands(command)
            
            # Check each extracted command
            for cmd in commands:
                if cmd in self.blocked_commands:
                    return CommandValidationResult(False, f"Blocked command: {cmd}")
                
                # Check for dangerous patterns
                if self._check_dangerous_patterns(command):
                    return CommandValidationResult(False, "Dangerous command pattern detected")
            
            return CommandValidationResult(True)
            
        except Exception as e:
            # If validation fails, err on the side of caution
            return CommandValidationResult(False, f"Validation error: {str(e)}")
    
    def _check_dangerous_patterns(self, command: str) -> bool:
        """Check for dangerous command patterns"""
        dangerous_patterns = [
            r'rm\s+-rf\s+/',     # rm -rf /
            r'del\s+/s\s+c:',    # del /s c:
            r'format\s+c:',      # format c:
            r'dd\s+if=.*of=/dev', # dd if=... of=/dev...
            r'>\s*/dev/',        # redirect to /dev/
            r'sudo\s+rm',        # sudo rm
        ]
        
        cmd_lower = command.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, cmd_lower):
                return True
        
        return False
    
    def add_blocked_command(self, command: str) -> None:
        """Add a command to the blocked list"""
        self.blocked_commands.add(command.lower())
    
    def remove_blocked_command(self, command: str) -> None:
        """Remove a command from the blocked list"""
        self.blocked_commands.discard(command.lower())
    
    def get_blocked_commands(self) -> List[str]:
        """Get list of blocked commands"""
        return sorted(list(self.blocked_commands))
