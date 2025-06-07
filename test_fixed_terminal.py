#!/usr/bin/env python3
"""
Test script to verify the fixed terminal implementation works correctly.
"""

import asyncio
import sys
import os

# Add the serena src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from serena.terminal import ImprovedTerminalManager as TerminalManager

async def test_terminal_execution():
    """Test the terminal execution with the Desktop Commander pattern"""
    print("Testing Serena Terminal Manager with Desktop Commander pattern...")
    
    manager = TerminalManager()
    
    # Test 1: Quick command that should complete immediately
    print("\n1. Testing quick command (echo)...")
    result = await manager.execute_command("echo 'Hello from Serena!'", timeout_ms=5000)
    print(f"   PID: {result.pid}")
    print(f"   Initial output: {repr(result.initial_output)}")
    print(f"   Is blocked: {result.is_blocked}")
    
    # Test 2: Long-running command that should return PID immediately
    print("\n2. Testing long-running command...")
    if sys.platform == "win32":
        cmd = "ping -n 10 127.0.0.1"  # Windows: ping 10 times
    else:
        cmd = "sleep 5 && echo 'Done sleeping'"  # Unix: sleep then echo
    
    result = await manager.execute_command(cmd, timeout_ms=2000)  # 2 second timeout
    print(f"   PID: {result.pid}")
    print(f"   Initial output: {repr(result.initial_output)}")
    print(f"   Is blocked: {result.is_blocked}")
    
    if result.is_blocked and result.pid != -1:
        print(f"   ✓ SUCCESS: Command returned PID {result.pid} immediately while still running!")
        
        # Wait a bit and read more output
        await asyncio.sleep(3)
        new_output = manager.get_new_output(result.pid)
        if new_output:
            print(f"   New output after 3 seconds: {repr(new_output[:100])}...")
        
        # List active sessions
        active_sessions = manager.list_active_sessions()
        print(f"   Active sessions: {len(active_sessions)}")
        for session in active_sessions:
            print(f"     - PID {session.pid}: {session.command[:30]}... (running {session.runtime_seconds:.1f}s)")
    
    # Test 3: Command that fails
    print("\n3. Testing command that fails...")
    result = await manager.execute_command("this-command-does-not-exist-12345", timeout_ms=3000)
    print(f"   PID: {result.pid}")
    print(f"   Error output: {repr(result.initial_output)}")
    print(f"   Is blocked: {result.is_blocked}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_terminal_execution())
