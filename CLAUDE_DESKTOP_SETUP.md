# MCP Server Configuration for Claude Desktop

This guide explains how to set up and use the Crude or Rude MCP server with Claude Desktop.

## Prerequisites

1. **Python 3.11+** and **Poetry** installed
2. **AWS CLI configured** with appropriate credentials and region
3. **Claude Desktop** application installed

## Installation

1. Clone and set up the project:
```bash
git clone https://github.com/brianbruff/crude-or-rude.git
cd crude-or-rude
poetry install
```

2. Configure AWS credentials (required for Claude 3.7 Sonnet via Bedrock):
```bash
aws configure
# Enter your AWS Access Key ID, Secret Key, Region, and output format
```

## Starting the MCP Server

Run the crude-or-rude application in server mode:

```bash
poetry run crude-or-rude --server
```

You should see:
```
🛢️ Crude or Rude MCP Server starting...
Listening for MCP connections via stdio...
```

The server will remain running and listen for MCP protocol messages via stdin/stdout.

## Claude Desktop Configuration

### macOS Configuration

Add the following to your Claude Desktop configuration file at:
`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crude-or-rude": {
      "command": "poetry",
      "args": ["run", "crude-or-rude", "--server"],
      "cwd": "/path/to/your/crude-or-rude",
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### Windows Configuration

Add the following to:
`%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crude-or-rude": {
      "command": "poetry.exe",
      "args": ["run", "crude-or-rude", "--server"],
      "cwd": "C:\\path\\to\\your\\crude-or-rude",
      "env": {
        "PATH": "C:\\Python311;C:\\Python311\\Scripts;%PATH%"
      }
    }
  }
}
```

### Linux Configuration

Add the following to:
`~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crude-or-rude": {
      "command": "poetry",
      "args": ["run", "crude-or-rude", "--server"],
      "cwd": "/path/to/your/crude-or-rude",
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

**Important**: Replace `/path/to/your/crude-or-rude` with the actual absolute path to your crude-or-rude directory.

## Restarting Claude Desktop

After modifying the configuration:

1. **Completely quit Claude Desktop** (not just close the window)
2. **Restart Claude Desktop**
3. **Verify the connection** by looking for the MCP server indicator in Claude Desktop

## Testing the Integration

Once Claude Desktop is connected to the MCP server, you can test the functionality:

### 1. Get Sample Headlines
Ask Claude:
```
Can you get some sample crude oil headlines for me to analyze?
```

Claude should use the `get_sample_headlines` tool to retrieve a list of sample headlines.

### 2. Analyze a Single Headline
Ask Claude:
```
Can you analyze this crude oil headline: "OPEC cuts production again despite global surplus concerns"
```

Claude should use the `analyze_crude_headline` tool and provide a comprehensive analysis including:
- Sentiment analysis (score, label, confidence)
- Tone analysis (rudeness score, tone, confidence)
- Market sentiment classification with witty commentary

### 3. Batch Analysis
Ask Claude:
```
Can you analyze multiple headlines about oil markets and compare their sentiment?
```

Then provide a list of headlines. Claude should use the `analyze_multiple_headlines` tool.

## Available Tools

The MCP server exposes three tools:

### `analyze_crude_headline`
- **Purpose**: Analyze a single crude oil news headline
- **Parameters**: 
  - `headline` (required): The headline to analyze
  - `source` (optional): News source
- **Returns**: Complete analysis with sentiment, tone, and market classification

### `get_sample_headlines`
- **Purpose**: Get sample headlines for testing
- **Parameters**: None
- **Returns**: List of sample crude oil headlines

### `analyze_multiple_headlines`
- **Purpose**: Analyze multiple headlines in batch
- **Parameters**:
  - `headlines` (required): Array of headlines to analyze
- **Returns**: Array of analysis results

## Troubleshooting

### Server Won't Start
- Check that AWS credentials are configured: `aws sts get-caller-identity`
- Verify poetry environment: `poetry run python --version`
- Check for Python/dependency issues: `poetry install`

### Claude Desktop Connection Issues
- Verify the configuration file path is correct
- Ensure absolute paths are used in the configuration
- Check that the `cwd` path exists and contains the project
- Restart Claude Desktop completely after configuration changes

### Analysis Errors
- **AWS/Bedrock Issues**: The application will fall back to rule-based analysis if AWS Bedrock is unavailable
- **Network Issues**: Check internet connectivity for AWS Bedrock access
- **Region Issues**: Ensure your AWS region supports Claude 3.7 Sonnet

### Viewing Server Logs
The server outputs logs to stdout. If running from Claude Desktop, you may not see these logs directly. For debugging, run the server manually:

```bash
poetry run crude-or-rude --server
```

Then test with a separate MCP client or by sending JSON-RPC messages manually.

## Environment Variables

Optional environment variables:

- `AWS_DEFAULT_REGION`: Override the default AWS region
- `FASTMCP_URL`: URL for external sentiment service (fallback available)

## Security Considerations

- The server runs locally and communicates with Claude Desktop via stdio
- AWS credentials are handled securely through the AWS CLI/SDK
- No external network services are exposed
- All analysis is performed locally or via AWS Bedrock