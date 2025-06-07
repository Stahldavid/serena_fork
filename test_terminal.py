#!/usr/bin/env python3
"""
Test script for terminal functionality in Serena MCP Server.
This script tests the basic terminal management system.
"""

import sys
import os
import asyncio

# Add the src directory to the path so we can import serena modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from serena.terminal.terminal_manager import TerminalManager
from serena.terminal.command_manager import CommandManager
from serena.terminal.terminal_handlers import (
    handle_execute_command,
    handle_read_output,
    handle_list_sessions,
    handle_force_terminate
)
from serena.terminal.process_tools import handle_list_processes, handle_kill_process


async def test_terminal_system():
    """Test the terminal system components"""
    print("🚀 Testing Serena Terminal System")
    print("="*50)
    
    # Test 1: Command Manager
    print("\n1. Testing Command Manager...")
    cmd_manager = CommandManager()
    
    # Test valid command
    result = cmd_manager.validate_command("echo 'Hello World'")
    print(f"   Valid command test: {'✅ PASS' if result.is_valid else '❌ FAIL'}")
    
    # Test blocked command
    result = cmd_manager.validate_command("sudo rm -rf /")
    print(f"   Blocked command test: {'✅ PASS' if not result.is_valid else '❌ FAIL'}")
    
    # Test 2: Terminal Manager
    print("\n2. Testing Terminal Manager...")
    terminal_manager = TerminalManager()
    
    # Test command execution
    try:
        if sys.platform == "win32":
            test_cmd = "echo Hello from Windows"
        else:
            test_cmd = "echo 'Hello from Unix'"
            
        result = await terminal_manager.execute_command(test_cmd, timeout_ms=3000)
        print(f"   Command execution: {'✅ PASS' if result.pid > 0 else '❌ FAIL'}")
        print(f"   Output: {result.output[:50]}...")
        
        # Test session listing
        sessions = terminal_manager.list_active_sessions()
        print(f"   Active sessions: {len(sessions)} found")
        
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
    
    # Test 3: Handlers
    print("\n3. Testing Terminal Handlers...")
    
    try:
        # Test execute command handler
        result = await handle_execute_command({
            "command": "echo 'Handler Test'",
            "timeout_ms": 2000
        })
        print(f"   Execute handler: {'✅ PASS' if not result.get('isError') else '❌ FAIL'}")
        
        # Test list sessions handler
        result = await handle_list_sessions({})
        print(f"   List sessions handler: {'✅ PASS' if not result.get('isError') else '❌ FAIL'}")
        
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
    
    # Test 4: Process Tools
    print("\n4. Testing Process Tools...")
    
    try:
        result = await handle_list_processes()
        print(f"   List processes: {'✅ PASS' if not result.get('isError') else '❌ FAIL'}")
        
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
    
    print("\n" + "="*50)
    print("🎉 Terminal System Test Complete!")
    print("\n💡 Next Steps:")
    print("   1. Start Serena MCP Server: serena-mcp-server")
    print("   2. Test terminal tools in Claude Desktop")
    print("   3. Try commands like: execute_command, read_output, list_sessions")


if __name__ == "__main__":
    print("Serena Terminal System Test")
    print("===========================")
    
    try:
        asyncio.run(test_terminal_system())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
