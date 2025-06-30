"""
Integration test for running the MCP server.
"""

import asyncio
import signal
import subprocess
import sys
import time
from pathlib import Path


def test_mcp_server_startup():
    """Test that the MCP server can start up without crashing."""
    
    # Get the path to the crude-or-rude script
    project_root = Path(__file__).parent
    
    # Start the server process
    process = subprocess.Popen(
        ["poetry", "run", "crude-or-rude", "--server"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Give the server 5 seconds to start up
        time.sleep(5)
        
        # Check if the process is still running (not crashed)
        return_code = process.poll()
        
        if return_code is None:
            # Process is still running, which is good
            print("✅ MCP server started successfully")
            success = True
        else:
            # Process exited, check output
            stdout, stderr = process.communicate()
            print(f"❌ MCP server exited with code {return_code}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            success = False
            
    finally:
        # Clean up: terminate the process if it's still running
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    
    return success


def test_cli_help():
    """Test that the CLI help works."""
    project_root = Path(__file__).parent
    
    result = subprocess.run(
        ["poetry", "run", "crude-or-rude", "--help"],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0 and "--server" in result.stdout:
        print("✅ CLI help shows server option")
        return True
    else:
        print(f"❌ CLI help failed: {result.stderr}")
        return False


if __name__ == "__main__":
    print("🧪 Testing MCP server integration...")
    
    # Test CLI help first (faster and doesn't require AWS)
    cli_success = test_cli_help()
    
    # Test server startup
    server_success = test_mcp_server_startup()
    
    if cli_success and server_success:
        print("\n✅ All integration tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)