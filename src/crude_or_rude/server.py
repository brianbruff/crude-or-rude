"""
MCP Server for Crude or Rude sentiment analysis.

This module implements an MCP server that exposes crude oil market sentiment 
analysis capabilities to MCP clients like Claude Desktop.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Sequence

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolRequest, ListToolsResult, TextContent, Tool

from crude_or_rude.models import (
    AnalysisResult,
    HeadlineInput,
    MarketSentiment,
    RudenessAnalysis,
    SentimentAnalysis,
)
from crude_or_rude.workflow import CrudeOrRudeWorkflow


class CrudeOrRudeMCPServer:
    """MCP Server for crude oil market sentiment analysis."""

    def __init__(self):
        """Initialize the MCP server."""
        load_dotenv()
        self.server = Server("crude-or-rude")
        self.workflow = None
        self._setup_tools()

    def _setup_tools(self):
        """Set up the MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="analyze_headline",
                        description="Analyze a crude oil news headline for market sentiment",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "headline": {
                                    "type": "string",
                                    "description": "The crude oil news headline to analyze",
                                },
                                "source": {
                                    "type": "string",
                                    "description": "Optional news source (default: unknown)",
                                },
                            },
                            "required": ["headline"],
                        },
                    ),
                    Tool(
                        name="analyze_sentiment",
                        description="Analyze only the sentiment of a text",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "The text to analyze for sentiment",
                                }
                            },
                            "required": ["text"],
                        },
                    ),
                    Tool(
                        name="detect_rudeness",
                        description="Detect rudeness/aggressiveness in text",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "The text to analyze for rudeness",
                                }
                            },
                            "required": ["text"],
                        },
                    ),
                ]
            )

        @self.server.call_tool()
        async def call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> Sequence[TextContent]:
            """Handle tool calls."""
            if name == "analyze_headline":
                return await self._analyze_headline(arguments)
            elif name == "analyze_sentiment":
                return await self._analyze_sentiment(arguments)
            elif name == "detect_rudeness":
                return await self._detect_rudeness(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _analyze_headline(
        self, arguments: Dict[str, Any]
    ) -> Sequence[TextContent]:
        """Analyze a headline for complete market sentiment."""
        headline = arguments.get("headline")
        source = arguments.get("source")

        if not headline:
            raise ValueError("headline is required")

        # Initialize workflow if not already done
        if not self.workflow:
            self.workflow = CrudeOrRudeWorkflow()

        try:
            result = await self.workflow.analyze_headline(headline, source)

            # Format the result as a comprehensive analysis
            analysis_text = f"""# Crude Oil Market Sentiment Analysis

## 📰 Headline
{result.headline}

## 💭 Sentiment Analysis
- **Label**: {result.sentiment.sentiment_label}
- **Score**: {result.sentiment.sentiment_score:.3f} (range: -1.0 to 1.0)
- **Confidence**: {result.sentiment.confidence:.3f}

## 🗣️ Tone Analysis
- **Tone**: {result.rudeness.tone}
- **Rudeness Score**: {result.rudeness.rudeness_score:.3f} (range: 0.0 to 1.0)
- **Confidence**: {result.rudeness.confidence:.3f}

## 🎯 Market Sentiment Classification
- **Category**: {result.market_sentiment.category}
- **Reasoning**: {result.market_sentiment.reasoning}
- **Market Response**: "{result.market_sentiment.response}"

## 🔍 Summary
The market sentiment for this headline is classified as **{result.market_sentiment.category}** based on:
- Sentiment score of {result.sentiment.sentiment_score:.3f} ({result.sentiment.sentiment_label})
- Tone analysis showing {result.rudeness.tone} characteristics
- Overall market behavior: {result.market_sentiment.response}
"""

            return [TextContent(type="text", text=analysis_text)]

        except Exception as e:
            error_text = f"Error analyzing headline: {str(e)}"
            return [TextContent(type="text", text=error_text)]

    async def _analyze_sentiment(
        self, arguments: Dict[str, Any]
    ) -> Sequence[TextContent]:
        """Analyze text for sentiment only."""
        text = arguments.get("text")

        if not text:
            raise ValueError("text is required")

        # Initialize workflow if not already done
        if not self.workflow:
            self.workflow = CrudeOrRudeWorkflow()

        try:
            # Use the internal sentiment analysis
            sentiment = await self.workflow.sentiment_client.analyze_sentiment(text)

            result_text = f"""# Sentiment Analysis

## 📊 Results
- **Sentiment**: {sentiment.sentiment_label}  
- **Score**: {sentiment.sentiment_score:.3f} (range: -1.0 to 1.0)
- **Confidence**: {sentiment.confidence:.3f}

## 📝 Interpretation
Score interpretation:
- Positive: {sentiment.sentiment_score:.3f} > 0 (bullish market sentiment)
- Negative: {sentiment.sentiment_score:.3f} < 0 (bearish market sentiment)  
- Neutral: {sentiment.sentiment_score:.3f} ≈ 0 (balanced market sentiment)

Confidence level: {sentiment.confidence:.1%}
"""

            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            error_text = f"Error analyzing sentiment: {str(e)}"
            return [TextContent(type="text", text=error_text)]

    async def _detect_rudeness(
        self, arguments: Dict[str, Any]
    ) -> Sequence[TextContent]:
        """Detect rudeness/aggressiveness in text."""
        text = arguments.get("text")

        if not text:
            raise ValueError("text is required")

        try:
            # Import here to avoid circular imports
            from crude_or_rude.models import WorkflowState
            from crude_or_rude.nodes.rudeness import rudeness_detector_node

            # Create a workflow state for rudeness detection
            state = WorkflowState(headline=text)
            result = await rudeness_detector_node(state)
            rudeness = result.get("rudeness")

            if not rudeness:
                raise ValueError("Rudeness detection failed")

            result_text = f"""# Rudeness/Tone Analysis

## 🗣️ Results
- **Tone**: {rudeness.tone}
- **Rudeness Score**: {rudeness.rudeness_score:.3f} (range: 0.0 to 1.0)
- **Confidence**: {rudeness.confidence:.3f}

## 📝 Interpretation
Tone categories:
- **Professional**: Measured, neutral market language
- **Aggressive**: Hostile, panic-driven language
- **Passive-aggressive**: Subtle, manipulative language

Current tone: **{rudeness.tone}**
Rudeness level: {rudeness.rudeness_score:.1%}
Confidence: {rudeness.confidence:.1%}
"""

            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            error_text = f"Error detecting rudeness: {str(e)}"
            return [TextContent(type="text", text=error_text)]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as streams:
            await self.server.run(
                streams[0], streams[1], self.server.create_initialization_options()
            )

    async def cleanup(self):
        """Clean up resources."""
        if self.workflow:
            await self.workflow.close()


def main():
    """Main entry point for the MCP server."""
    asyncio.run(main_async())


async def main_async():
    """Async main entry point for the MCP server."""
    server = CrudeOrRudeMCPServer()
    try:
        await server.run()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        await server.cleanup()


if __name__ == "__main__":
    main()
