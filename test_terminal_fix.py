#!/usr/bin/env python3
"""
Test script to verify the terminal fix is working correctly.
Tests both quick commands (should return direct output) and long commands (should return PID format).
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from serena.terminal.terminal_handlers import handle_execute_command

async def test_quick_command():
    """Test a quick command that should return direct output"""
    print("🔍 Testing quick command: echo 'Test quick command'")
    result = await handle_execute_command({
        "command": "echo 'Test quick command'",
        "timeout_ms": 3000
    })
    
    print(f"✅ Quick Command Result:")
    print(f"   Text: {result['content'][0]['text']}")
    print(f"   Is Error: {result.get('isError', False)}")
    
    # Check if result contains direct output (not PID format)
    output_text = result['content'][0]['text']
    if "Test quick command" in output_text and "Command started with PID" not in output_text:
        print("✅ PASS: Quick command returns direct output")
        return True
    else:
        print("❌ FAIL: Quick command should return direct output, not PID format")
        return False

async def test_long_command():
    """Test a long command that should return PID format"""
    print("\n🔍 Testing long command: ping -n 3 127.0.0.1")
    result = await handle_execute_command({
        "command": "ping -n 3 127.0.0.1" if sys.platform == "win32" else "ping -c 3 127.0.0.1",
        "timeout_ms": 500  # Short timeout to ensure it's still running
    })
    
    print(f"✅ Long Command Result:")
    print(f"   Text: {result['content'][0]['text']}")
    print(f"   Is Error: {result.get('isError', False)}")
    
    # Check if result contains PID format
    output_text = result['content'][0]['text']
    if "Command started with PID" in output_text:
        print("✅ PASS: Long command returns PID format")
        return True
    else:
        print("❌ FAIL: Long command should return PID format")
        return False

async def test_invalid_command():
    """Test an invalid command"""
    print("\n🔍 Testing invalid command: nonexistentcommand123")
    result = await handle_execute_command({
        "command": "nonexistentcommand123",
        "timeout_ms": 3000
    })
    
    print(f"✅ Invalid Command Result:")
    print(f"   Text: {result['content'][0]['text']}")
    print(f"   Is Error: {result.get('isError', False)}")
    
    # Should handle gracefully
    output_text = result['content'][0]['text']
    if "nonexistentcommand123" in output_text or "not found" in output_text.lower() or "not recognized" in output_text.lower():
        print("✅ PASS: Invalid command handled gracefully")
        return True
    else:
        print("❌ FAIL: Invalid command not handled properly")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing Serena Terminal Fix")
    print("="*50)
    
    tests = [
        test_quick_command,
        test_long_command,
        test_invalid_command
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The terminal fix is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
