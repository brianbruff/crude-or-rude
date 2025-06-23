# GitHub Copilot Instructions for Crude or Rude Project

## Project Overview
This is a **crude oil market sentiment analyzer** called "Crude or Rude" that uses LangGraph workflows and AWS Bedrock with Claude 3.7 Sonnet to analyze news headlines and classify market sentiment with witty commentary.

## Key Architecture Components

### 1. **LangGraph Workflow System**
- Uses `langgraph` for orchestrating multi-node analysis pipeline
- State management through `WorkflowState` Pydantic model
- Sequential processing: Sentiment → Rudeness → Claude Decision

### 2. **AWS Bedrock Integration**
- **Current Model**: Claude 3.7 Sonnet (`us.anthropic.claude-3-7-sonnet-20250219-v1:0`)
- **Authentication**: AWS CLI configuration (no API keys needed)
- **Cross-region inference profile** for improved availability
- **Temperature**: 0.7, **Max Tokens**: 4000

### 3. **Node Structure**
- **Sentiment Analysis Node**: Uses FastMCP service (with mock fallback)
- **Rudeness Detector Node**: Mock NLP for tone analysis
- **Claude Decision Node**: AWS Bedrock-powered final classification

## Code Style & Patterns

### **Pydantic Models**
All data structures use Pydantic BaseModel with proper Field descriptions:
```python
class MarketSentiment(BaseModel):
    category: Literal["Professional", "Panic-stricken", "Passive-aggressive"]
    reasoning: str = Field(..., description="Explanation of classification")
    response: str = Field(..., description="Witty market commentary")
```

### **Async/Await Pattern**
All analysis functions are async:
```python
async def decide_market_sentiment(self, state: WorkflowState) -> Dict[str, Any]:
    # Implementation with try/except and fallback logic
```

### **Error Handling**
- Always include fallback logic for external service failures
- Return error states in workflow dictionaries
- Use try/except blocks around AWS Bedrock calls

### **File Organization**
```
src/crude_or_rude/
├── __init__.py
├── main.py              # CLI entry point
├── workflow.py          # LangGraph workflow orchestration
├── models/
│   └── __init__.py      # Pydantic models
├── nodes/
│   ├── __init__.py
│   ├── claude.py        # AWS Bedrock Claude node
│   ├── sentiment.py     # FastMCP sentiment analysis
│   └── rudeness.py      # Mock rudeness detection
└── services/
    └── __init__.py      # FastMCP client
```

## Specific Guidelines

### **When Working with Claude Node**
- Always use the cross-region inference profile model ID
- Include proper error handling with fallback decision logic
- Use Pydantic output parser for structured responses
- System prompt should emphasize witty, professional market analysis

### **When Adding New Analysis Nodes**
- Follow the async function signature pattern
- Return Dict[str, Any] with state updates
- Include comprehensive error handling
- Add proper type hints and docstrings

### **When Working with AWS Bedrock**
- Use `ChatBedrock` from `langchain_aws`  
- Model configuration goes in `model_kwargs`
- Region defaults to AWS CLI configuration
- Always handle `ValidationException` for model access issues

### **Mock Services**
- FastMCP has mock implementations when service unavailable
- Rudeness detector is entirely mock-based
- Mock data should be realistic for testing

## Key Dependencies
- **langgraph**: Workflow orchestration
- **langchain-aws**: AWS Bedrock integration  
- **langchain-core**: Core LangChain functionality
- **pydantic**: Data validation and parsing
- **boto3**: AWS SDK
- **fastapi**: Web framework (for potential API)
- **poetry**: Dependency management

## Environment & Configuration
- **AWS Authentication**: Via AWS CLI (`aws configure`)
- **No API Keys Required**: Uses AWS IAM/CLI credentials
- **Regions**: us-east-1, us-west-2, eu-central-1, ap-southeast-1, ap-northeast-1
- **Optional ENV**: `AWS_DEFAULT_REGION`, `FASTMCP_URL`

## Testing Patterns
- Use `test_bedrock.py` for AWS Bedrock connectivity testing
- Include both unit tests and integration tests
- Mock external services for unit testing
- Use `poetry run` for all command execution

## Market Sentiment Categories
1. **"Professional"** - Normal, measured market reporting
2. **"Panic-stricken"** - Markets in chaos, fear-driven reactions  
3. **"Passive-aggressive"** - Markets being manipulative or sending mixed signals

## Witty Response Style
Claude generates humorous market commentary with analogies like:
- "This market is like that friend who says 'Do whatever you want' but means the opposite"
- "This market is gaslighting you with mixed signals"
- Professional but entertaining tone

## Common Commands
```bash
# Install dependencies
poetry install

# Run application
poetry run crude-or-rude

# Test Bedrock connection
poetry run python test_bedrock.py

# Run tests
poetry run pytest

# Format code
poetry run black src/ tests/
poetry run isort src/ tests/
```

## When Suggesting Changes
- Always maintain the witty, entertaining tone
- Preserve AWS Bedrock integration patterns
- Keep fallback logic for external service failures  
- Follow the established Pydantic model patterns
- Maintain async/await consistency
- Include proper error handling and logging
