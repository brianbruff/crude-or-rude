# MCP Server Setup for Claude Desktop

This guide explains how to set up and use the Crude or Rude application as an MCP (Model Context Protocol) server with Claude Desktop.

## What is MCP?

MCP (Model Context Protocol) allows AI applications like Claude Desktop to connect to external tools and services. By running Crude or Rude as an MCP server, you can analyze crude oil headlines directly within Claude Desktop conversations.

## Prerequisites

1. **Claude Desktop**: Download and install Claude Desktop from Anthropic
2. **Python 3.11+**: Required for running the application
3. **Poetry**: For dependency management (or pip)
4. **AWS CLI** (Optional): For full AWS Bedrock integration, otherwise uses mock analysis

## Installation

### 1. Install Dependencies

```bash
# Install the application with MCP dependencies
cd crude-or-rude
poetry install

# Or with pip
pip install .
```

### 2. Install MCP Library

```bash
# Add MCP support
poetry add mcp
# Or with pip
pip install mcp
```

## Configuration

### 1. AWS Setup (Optional)

For full functionality with AWS Bedrock:

```bash
# Configure AWS CLI (optional - will use fallback if not configured)
aws configure
```

Set environment variables if needed:
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

**Note**: The application includes fallback mechanisms and will work with mock analysis if AWS is not configured.

### 2. Claude Desktop Configuration

Add the MCP server to your Claude Desktop configuration:

#### On macOS:
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

#### On Windows:
Edit `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "crude-or-rude": {
      "command": "poetry",
      "args": ["run", "crude-or-rude", "--server"],
      "cwd": "/path/to/your/crude-or-rude"
    }
  }
}
```

Or if installed globally:

```json
{
  "mcpServers": {
    "crude-or-rude": {
      "command": "crude-or-rude-server"
    }
  }
}
```

## Usage

### 1. Start the MCP Server

You can test the server manually:

```bash
# Using poetry
poetry run crude-or-rude --server

# Or using the dedicated server command
poetry run crude-or-rude-server

# Or if installed globally
crude-or-rude --server
```

### 2. Use in Claude Desktop

Once configured and Claude Desktop is restarted, you can use these tools in your conversations:

#### Analyze a Single Headline
```
Can you analyze this crude oil headline using the crude-or-rude tool: "Oil prices surge amid OPEC production cuts"
```

#### Analyze Multiple Headlines
```
Please analyze these oil market headlines:
- "OPEC extends production cuts through 2024"
- "U.S. crude inventories fall more than expected"
- "Oil prices plummet on recession fears"
```

#### Get Sample Analysis
```
Show me some sample crude oil market sentiment analysis
```

## Available MCP Tools

### 1. `analyze_headline`
- **Purpose**: Analyze a single crude oil news headline
- **Input**: headline (required), source (optional)
- **Output**: Complete sentiment, tone, and market classification analysis

### 2. `analyze_headlines_batch`
- **Purpose**: Analyze multiple headlines at once (max 5)
- **Input**: Array of headlines
- **Output**: Analysis results for all headlines

### 3. `get_sample_analysis`
- **Purpose**: Get sample analysis for demonstration
- **Input**: None
- **Output**: Sample analysis results with different headline types

## Analysis Categories

The tool classifies headlines into three market sentiment categories:

- **Professional**: Normal, measured market reporting
- **Panic-stricken**: Markets in chaos, fear-driven reactions  
- **Passive-aggressive**: Markets sending mixed signals

## Troubleshooting

### Server Won't Start
1. Check that MCP dependencies are installed: `pip install mcp`
2. Verify the path in Claude Desktop configuration is correct
3. Test manually: `crude-or-rude --server`

### AWS Bedrock Errors
- The application includes fallback mechanisms
- It will use mock analysis if AWS Bedrock is unavailable
- No AWS configuration is required for basic functionality

### Claude Desktop Not Detecting Server
1. Restart Claude Desktop after configuration changes
2. Check the configuration file syntax (valid JSON)
3. Verify the command path and arguments are correct

### Testing the Server
```bash
# Test MCP functionality without full MCP installation
python test_mcp_functionality.py

# Test CLI functionality
crude-or-rude "Oil prices rise today"

# Test server mode (requires MCP library)
crude-or-rude --server
```

## Example Output

```json
{
  "headline": "Oil prices surge amid OPEC production cuts",
  "sentiment": {
    "score": 0.6,
    "label": "positive",
    "confidence": 0.8
  },
  "tone": {
    "rudeness_score": 0.3,
    "tone": "professional",
    "confidence": 0.7
  },
  "market_sentiment": {
    "category": "Professional",
    "reasoning": "Measured market response to supply-side fundamentals",
    "response": "The market is being surprisingly reasonable about supply dynamics"
  }
}
```

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Test the CLI functionality first: `crude-or-rude "test headline"`
3. Verify MCP configuration in Claude Desktop
4. Check application logs for detailed error messages

The application is designed to be resilient and will provide analysis even if external services (AWS Bedrock, FastMCP) are unavailable.