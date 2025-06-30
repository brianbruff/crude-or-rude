# 🛢️ Crude or Rude? Market Sentiment Analyzer

A witty market sentiment analyzer for crude oil news using LangGraph and AWS Bedrock.

> "Is the market bullish, bearish, or just being a jerk?"

## 🧠 Concept

This application analyzes crude oil news headlines and determines whether the market sentiment is:
- **Professional** - Normal, measured market reporting
- **Panic-stricken** - Markets are in chaos, fear-driven reactions  
- **Passive-aggressive** - Markets are being manipulative or sending mixed signals

## 🏗️ Architecture

The application can run in two modes:

### 1. **MCP Server Mode** (Recommended)
Acts as a Model Context Protocol (MCP) server that can be integrated with Claude Desktop or other MCP clients. This mode exposes sentiment analysis capabilities as MCP tools.

### 2. **CLI Mode** 
Traditional command-line interface for direct headline analysis.

The application uses a LangGraph workflow that orchestrates multiple analysis nodes:

1. **Sentiment Analysis** - Internal crude oil market sentiment analysis
2. **Rudeness Detection** - Tone analysis for market language 
3. **Claude Decision Node** - AWS Bedrock-powered composite sentiment classification using Claude 3.7 Sonnet

## 🚀 Quick Start

### Prerequisites 

- Python 3.11+
- Poetry (for dependency management)
- AWS CLI configured with Bedrock access (for Claude 3.7 Sonnet integration)
- Optional: FastMCP service running (falls back to mock analysis)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/brianbruff/crude-or-rude.git
cd crude-or-rude
```

2. Install dependencies:
```bash
poetry install
```

3. Configure AWS CLI (if not already done):
```bash
aws configure
# Or use AWS SSO, IAM roles, or other AWS authentication methods
```

4. Verify AWS Bedrock access:
```bash
aws bedrock list-foundation-models --region us-east-1
```

### Usage

#### Run with sample headlines:
```bash
poetry run crude-or-rude
```

#### Analyze a custom headline:
```bash
poetry run crude-or-rude "OPEC cuts production again despite surplus"
```

#### Programmatic usage:
```python
from crude_or_rude.workflow import CrudeOrRudeWorkflow

async def analyze():
    # Uses your existing AWS CLI configuration automatically
    workflow = CrudeOrRudeWorkflow()
    try:
        result = await workflow.analyze_headline(
            "Oil prices surge as tensions escalate"
        )
        print(f"Market says: {result.market_sentiment.response}")
    finally:
        await workflow.close()
```

## 🖥️ MCP Server Mode

### Overview
The application can run as an MCP (Model Context Protocol) server, allowing integration with Claude Desktop and other MCP clients. This is the recommended way to use crude-or-rude for interactive analysis.

### Starting the Server

#### Using dedicated command:
```bash
poetry run crude-or-rude-server
```

#### Using CLI flag:
```bash
poetry run crude-or-rude --server
```

### Claude Desktop Integration

1. **Locate Claude Desktop configuration file**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add crude-or-rude server configuration**:
   ```json
   {
     "mcpServers": {
       "crude-or-rude": {
         "command": "poetry",
         "args": ["run", "crude-or-rude-server"],
         "cwd": "/path/to/your/crude-or-rude/directory"
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### Available MCP Tools

The server exposes three main tools:

#### `analyze_headline`
Complete analysis of crude oil news headlines
- **Input**: `headline` (required), `source` (optional)
- **Output**: Full sentiment analysis with market categorization

#### `analyze_sentiment`  
Sentiment analysis only
- **Input**: `text` (required)
- **Output**: Sentiment score, label, and confidence

#### `detect_rudeness`
Tone and rudeness detection
- **Input**: `text` (required)  
- **Output**: Tone classification and rudeness score

### Testing MCP Integration

Once configured in Claude Desktop, you can test with prompts like:

```
"Can you analyze this oil headline using crude-or-rude: 'OPEC cuts production amid market volatility'"

"Use the crude-or-rude sentiment analyzer to check: 'Oil prices crash to yearly lows'"

"What does crude-or-rude say about the tone of: 'Energy markets show concerning weakness'"
```

The tools will provide comprehensive analysis including:
- Sentiment scores and labels
- Tone analysis (professional/aggressive/passive-aggressive)
- Market sentiment classification
- Witty market commentary

## ☁️ GitHub Codespaces

The easiest way to get started is using GitHub Codespaces, which provides a pre-configured development environment.

### 🚀 Launch in Codespace

1. **Create a Codespace**: Click the "Code" button on the GitHub repository and select "Create codespace on main"

2. **Configure AWS credentials**: The Codespace will automatically install dependencies. You need to configure your AWS credentials:
   ```bash
   # Configure AWS CLI
   aws configure
   # Or set environment variables:
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **Ensure Bedrock access**: Make sure your AWS credentials have access to Amazon Bedrock:
   - Required permissions: `bedrock:InvokeModel` for Claude models
   - Supported regions: us-east-1, us-west-2, eu-central-1, ap-southeast-1, ap-northeast-1

4. **Run the application**:
   ```bash
   poetry run crude-or-rude
   ```

### 🔐 AWS Authentication

The application supports multiple AWS authentication methods:

**Option 1: AWS CLI (Recommended)**
```bash
aws configure
# Follow prompts to enter your AWS credentials
```

**Option 2: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Option 3: IAM Roles (for EC2/ECS/Lambda)**
- Attach appropriate IAM role with Bedrock permissions
- No additional configuration needed

**Option 4: AWS SSO**
```bash
aws configure sso
# Follow prompts to configure SSO
```

### 📋 Required AWS Permissions

Your AWS credentials need the following permissions for Amazon Bedrock:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-7-sonnet-*"
            ]
        }
    ]
}
```

### 🌍 Supported AWS Regions

Claude 3.7 Sonnet is available in these AWS regions:
- `us-east-1` (Virginia) 
- `us-west-2` (Oregon)
- `eu-central-1` (Frankfurt)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)

### 🌍 Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | ❌ Optional* | AWS access key (if not using CLI/IAM) | From AWS CLI |
| `AWS_SECRET_ACCESS_KEY` | ❌ Optional* | AWS secret key (if not using CLI/IAM) | From AWS CLI |
| `AWS_DEFAULT_REGION` | ❌ Optional | AWS region for Bedrock | From AWS CLI |

*Not required if using AWS CLI, IAM roles, or SSO

Note: The application uses internal sentiment analysis and will work without external dependencies.

## 📊 Example Output

```
📰 Sample: OPEC cuts production again despite global surplus concerns
--------------------------------------------------
💭 Sentiment: negative (score: -0.60, confidence: 0.75)
🗣️ Tone: passive-aggressive (rudeness: 0.65, confidence: 0.80)  
🎯 Market Sentiment: Passive-aggressive
💡 Reasoning: Mixed signals with OPEC cuts despite surplus indicate market manipulation
🤡 Market Says: "This market is gaslighting you with convenient timing."
```

## 🚀 Why AWS Bedrock?

This application uses **AWS Bedrock** instead of direct API calls for several advantages:

### 🔒 **Enhanced Security**
- Uses AWS IAM for access control
- No API keys to manage or rotate
- Leverages existing AWS security policies

### 💰 **Cost Management** 
- Unified billing through AWS
- AWS cost management and monitoring tools
- Pay-per-use pricing model

### 🌐 **Enterprise Ready**
- VPC integration for private deployments
- AWS compliance certifications (SOC, HIPAA, etc.)
- Better integration with other AWS services

### 🤖 **Latest Models**
- **Claude 3.7 Sonnet**: More capable than previous versions
- Higher context window (200K tokens)
- Better reasoning and analysis capabilities
- Faster response times

### 🔄 **Reliability**
- AWS's global infrastructure
- Built-in retry mechanisms
- Service availability guarantees

## 🛠️ Development

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black src/ tests/
poetry run isort src/ tests/
```

### Linting
```bash
poetry run flake8 src/ tests/
```

## 🔧 Configuration

The application can be configured via environment variables or AWS CLI:

### Claude 3.7 Sonnet via AWS Bedrock
- **Model**: `us.anthropic.claude-3-7-sonnet-20250219-v1:0`
- **Temperature**: 0.7
- **Max Tokens**: 4000
- **Authentication**: Uses your AWS CLI configuration automatically
- **Region**: Configurable via `AWS_DEFAULT_REGION` or AWS CLI

### Internal Services
- **Sentiment Analysis**: Built-in crude oil market sentiment analysis
- **Tone Detection**: Internal rudeness/tone classification
- **MCP Server**: Model Context Protocol server for external integration

## 🧪 Testing

### Quick Bedrock Test
```bash
# Test AWS Bedrock integration
poetry run python test_bedrock.py
```

### Full Test Suite
The application uses internal services and includes comprehensive testing:
- Internal sentiment analysis with crude oil market keywords
- Fallback decision logic when Claude API is unavailable
- MCP server functionality tests

```bash
poetry run pytest
```

## 🔧 Troubleshooting

### Common Issues

**"Import langchain_aws could not be resolved"**
```bash
poetry install
# or
poetry add langchain-aws boto3
```

**"No module named 'langchain_aws'"**
```bash
poetry run python your_script.py
# instead of
python your_script.py
```

**"Unable to locate credentials"**
```bash
aws configure
# or check your AWS credentials
aws sts get-caller-identity
```

**"Access denied to Bedrock"**
- Ensure your AWS user/role has `bedrock:InvokeModel` permission
- Check if Claude is available in your selected region
- Verify model access in AWS Bedrock console

**"Region not supported"**
- Use one of the supported regions: us-east-1, us-west-2, eu-central-1, ap-southeast-1, ap-northeast-1
- Set region via `AWS_DEFAULT_REGION` environment variable or AWS CLI

### Debug Mode
```bash
# Test Bedrock connectivity
poetry run python test_bedrock.py

# Check AWS configuration
aws bedrock list-foundation-models --region us-east-1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
