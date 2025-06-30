"""
Server entry point for crude-or-rude MCP server.
"""

import sys
from dotenv import load_dotenv

from crude_or_rude.server import server


def main():
    """Start the MCP server."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    transport = "stdio"  # Default MCP transport
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            print("Crude or Rude MCP Server")
            print("Usage: crude-or-rude-server [--transport TRANSPORT]")
            print("  --transport TRANSPORT    Transport to use: stdio, sse, streamable-http (default: stdio)")
            print("                          stdio: Standard input/output (for Claude Desktop)")
            print("                          sse: Server-Sent Events HTTP server")
            print("                          streamable-http: HTTP server with streaming")
            return 0
        
        # Simple argument parsing
        for i, arg in enumerate(sys.argv[1:], 1):
            if arg == "--transport" and i + 1 < len(sys.argv):
                transport = sys.argv[i + 1]
                if transport not in ["stdio", "sse", "streamable-http"]:
                    print(f"Error: Invalid transport '{transport}'. Use stdio, sse, or streamable-http")
                    return 1
    
    print(f"🛢️ Starting Crude or Rude MCP Server with {transport} transport")
    print("📖 Available tools:")
    print("  - analyze_headline: Complete headline analysis")
    print("  - analyze_sentiment: Sentiment analysis only")  
    print("  - detect_rudeness: Rudeness/tone detection only")
    print("  - decide_market_sentiment: Market sentiment decision")
    
    if transport == "stdio":
        print()
        print("💡 Add this server to Claude Desktop configuration:")
        print('   "crude-or-rude": {"command": "crude-or-rude-server"}')
        
    print()
    
    # Start the server with the specified transport
    server.app.run(transport=transport)
    return 0


if __name__ == "__main__":
    sys.exit(main())