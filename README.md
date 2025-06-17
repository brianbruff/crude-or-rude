# 🛢️ Crude or Rude? Market Sentiment Analyzer

A witty market sentiment analyzer for crude oil news using LangGraph and FastMCP.

> "Is the market bullish, bearish, or just being a jerk?"

## 🧠 Concept

This application analyzes crude oil news headlines and determines whether the market sentiment is:
- **Professional** - Normal, measured market reporting
- **Panic-stricken** - Markets are in chaos, fear-driven reactions  
- **Passive-aggressive** - Markets are being manipulative or sending mixed signals

## 🏗️ Architecture

The application uses a LangGraph workflow that orchestrates multiple analysis nodes:

1. **Sentiment Analysis Node** - Uses FastMCP for sentiment scoring
2. **Rudeness Detector Node** - Mock NLP node for tone analysis
3. **Claude Decision Node** - LLM-powered composite sentiment classification

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Anthropic API key (for Claude integration)
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

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
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
    workflow = CrudeOrRudeWorkflow()
    try:
        result = await workflow.analyze_headline(
            "Oil prices surge as tensions escalate"
        )
        print(f"Market says: {result.market_sentiment.response}")
    finally:
        await workflow.close()
```

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

The application can be configured via environment variables:

- `ANTHROPIC_API_KEY` - Required for Claude integration
- `FASTMCP_URL` - URL for FastMCP service (defaults to http://localhost:8000)

## 🧪 Testing

The application includes mock implementations that work without external dependencies:
- Mock sentiment analysis when FastMCP is unavailable
- Fallback decision logic when Claude API is unavailable

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
