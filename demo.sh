#!/bin/bash

# Demo script to test the MCP server functionality
# This shows how to test the server in different modes

echo "🛢️ Crude or Rude MCP Server Demo"
echo "================================="
echo

echo "📋 Testing CLI Mode (Legacy):"
echo "poetry run crude-or-rude \"OPEC announces surprise production cuts\""
echo

echo "📋 Testing MCP Server Help:"
echo "poetry run crude-or-rude-server --help"
echo

echo "📋 Starting MCP Server (STDIO for Claude Desktop):"
echo "poetry run crude-or-rude-server"
echo "# This starts the server in STDIO mode for Claude Desktop integration"
echo

echo "📋 Starting MCP Server (SSE for web testing):"
echo "poetry run crude-or-rude-server --transport sse"
echo "# This starts an HTTP server on port 8000 for testing"
echo

echo "📋 Claude Desktop Configuration:"
echo "Add this to your claude_desktop_config.json:"
echo
cat << EOF
{
  "mcpServers": {
    "crude-or-rude": {
      "command": "poetry",
      "args": ["run", "crude-or-rude-server"],
      "cwd": "$(pwd)"
    }
  }
}
EOF
echo

echo "📋 Testing with Claude Desktop:"
echo "After configuring Claude Desktop, you can ask:"
echo "\"Using the crude-or-rude server, analyze this headline: 'Oil prices crash amid recession fears'\""
echo

echo "✅ Available MCP Tools:"
echo "  - analyze_headline: Complete analysis"
echo "  - analyze_sentiment: Sentiment only"
echo "  - detect_rudeness: Tone analysis only"
echo "  - decide_market_sentiment: Final classification"
echo

echo "🔧 Technical Notes:"
echo "  - Server works without AWS credentials (uses fallback logic)"
echo "  - CLI mode still available for backward compatibility"
echo "  - Built-in sentiment analysis (no external dependencies)"
echo "  - Supports stdio, sse, and streamable-http transports"