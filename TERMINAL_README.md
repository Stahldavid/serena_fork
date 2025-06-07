# 🖥️ Serena Terminal System

## Overview

The Serena Terminal System adds powerful long-running command support to the Serena MCP Server, based on the proven architecture of Desktop Commander MCP Server. This system resolves MCP's limitations with long-running tools by implementing session management and background command execution.

## 🚀 Features

### Terminal Management
- **`execute_command`** - Execute commands with configurable timeout
- **`read_output`** - Read new output from running sessions  
- **`force_terminate`** - Force terminate running sessions
- **`list_sessions`** - List all active terminal sessions

### Process Management  
- **`list_processes`** - List all system processes
- **`kill_process`** - Terminate processes by PID

## 🛡️ Security Features

- **Command Validation** - Blocks dangerous commands automatically
- **Timeout Control** - Prevents runaway processes
- **Session Limits** - Controls resource usage
- **Safe Termination** - Graceful process cleanup

## 📋 Blocked Commands

The system automatically blocks dangerous commands including:
- Disk operations: `format`, `mkfs`, `dd`, `fdisk`
- System control: `sudo`, `shutdown`, `reboot`
- File destruction: `rm -rf`, `del /s`
- User management: `passwd`, `adduser`, `usermod`

## 🔧 Usage Examples

### Execute Long-Running Command
```python
# Start a command that might take time
result = execute_command("npm install", timeout_ms=10000)
# Returns: PID and initial output

# Check for more output later
output = read_output(pid=1234, timeout_ms=5000)
```

### Monitor System Processes
```python
# List all running processes
processes = list_processes()

# Terminate a specific process
result = kill_process(pid=5678)
```

### Manage Sessions
```python
# List active terminal sessions
sessions = list_sessions()

# Force terminate a session
result = force_terminate(pid=1234)
```

## 🏗️ Architecture

```
src/serena/terminal/
├── __init__.py              # Module exports
├── terminal_types.py        # Data structures
├── terminal_manager.py      # Core session management
├── command_manager.py       # Command validation
├── terminal_handlers.py     # Request handlers
└── process_tools.py         # System process tools
```

## 🔄 How It Works

1. **Command Execution**: Commands are started with a timeout
2. **Background Monitoring**: Long-running commands continue in background
3. **Session Tracking**: Each command gets a PID for tracking
4. **Output Buffering**: Output is collected and available on demand
5. **Resource Management**: Automatic cleanup of completed sessions

## 🧪 Testing

Run the test script to verify functionality:

```bash
cd /path/to/serena
python test_terminal.py
```

## 🔌 Integration

The terminal tools are automatically registered in Serena's tool system:
- `ExecuteCommandTool`
- `ReadOutputTool`  
- `ForceTerminateTool`
- `ListSessionsTool`
- `ListProcessesTool`
- `KillProcessTool`

## ⚙️ Configuration

No additional configuration required - the system uses sensible defaults:
- Default timeout: 5000ms
- Max sessions: 100
- Output buffer: 50KB per session

## 🎯 Benefits

1. **Solves MCP Limitations** - Long-running commands work seamlessly
2. **Enhanced Security** - Built-in command validation
3. **Resource Efficient** - Automatic cleanup and limits
4. **User Friendly** - Simple API with clear feedback
5. **Cross-Platform** - Works on Windows, macOS, and Linux

This implementation brings the power of Desktop Commander's terminal system to Serena, enabling sophisticated command-line workflows within the MCP framework.
