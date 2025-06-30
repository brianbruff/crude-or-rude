"""
MCP server implementation for the Crude or Rude application.

This module provides an MCP (Model Context Protocol) server that exposes
the crude oil market sentiment analysis functionality as tools that can be
used by MCP clients like Claude Desktop.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from crude_or_rude.workflow import CrudeOrRudeWorkflow


# Initialize the MCP server
mcp = FastMCP(
    name="crude-or-rude",
    instructions=(
        "Crude or Rude is a market sentiment analyzer for crude oil news headlines. "
        "It uses LangGraph workflows and AWS Bedrock with Claude 3.7 Sonnet to analyze "
        "news headlines and classify market sentiment with witty commentary. "
        "The analyzer provides sentiment analysis, rudeness/tone detection, and "
        "final market sentiment classification in categories: Professional, "
        "Panic-stricken, or Passive-aggressive."
    ),
)

# Global workflow instance (will be initialized when server starts)
workflow: CrudeOrRudeWorkflow | None = None


async def get_workflow() -> CrudeOrRudeWorkflow:
    """Get or create the workflow instance."""
    global workflow
    if workflow is None:
        workflow = CrudeOrRudeWorkflow()
    return workflow


@mcp.tool()
async def analyze_crude_headline(headline: str, source: str = None) -> dict[str, Any]:
    """
    Analyze a crude oil news headline for market sentiment.

    This tool performs comprehensive analysis of crude oil market news headlines,
    including sentiment analysis, tone detection, and market sentiment classification
    with witty commentary.

    Args:
        headline: The crude oil news headline to analyze
        source: Optional source of the news (e.g., "Reuters", "Bloomberg")

    Returns:
        Complete analysis result containing:
        - headline: The original headline
        - sentiment: Sentiment analysis (score, label, confidence)
        - rudeness: Tone analysis (score, tone, confidence)  
        - market_sentiment: Final classification with reasoning and witty response
    """
    try:
        # Get the workflow instance
        workflow_instance = await get_workflow()
        
        # Perform the analysis
        result = await workflow_instance.analyze_headline(headline, source)
        
        # Convert the result to a dictionary for JSON serialization
        return {
            "headline": result.headline,
            "sentiment": {
                "sentiment_score": result.sentiment.sentiment_score,
                "sentiment_label": result.sentiment.sentiment_label,
                "confidence": result.sentiment.confidence,
            },
            "rudeness": {
                "rudeness_score": result.rudeness.rudeness_score,
                "tone": result.rudeness.tone,
                "confidence": result.rudeness.confidence,
            },
            "market_sentiment": {
                "category": result.market_sentiment.category,
                "reasoning": result.market_sentiment.reasoning,
                "response": result.market_sentiment.response,
            },
            "source": source,
        }
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "headline": headline,
            "source": source,
        }


@mcp.tool()
async def get_sample_headlines() -> list[str]:
    """
    Get a list of sample crude oil headlines for testing the analyzer.

    Returns:
        List of sample crude oil news headlines that can be used to test
        the analyze_crude_headline tool.
    """
    return [
        "OPEC cuts production again despite global surplus concerns",
        "Oil prices surge as geopolitical tensions escalate in Middle East",
        "Crude futures plummet amid recession fears and demand destruction",
        "Energy analysts report steady growth in shale oil production",
        "Breaking: Major pipeline explosion sends oil markets into chaos",
        "Oil inventories show unexpected drawdown in latest weekly report",
        "IEA warns of potential supply disruption in key producing region",
        "Crude oil trades sideways as markets await OPEC+ decision",
        "WTI crude hits new monthly high on supply concerns",
        "Oil markets stabilize after volatile trading session",
    ]


@mcp.tool()
async def analyze_multiple_headlines(headlines: list[str]) -> list[dict[str, Any]]:
    """
    Analyze multiple crude oil headlines in batch.

    Args:
        headlines: List of crude oil news headlines to analyze

    Returns:
        List of analysis results, one for each headline.
    """
    results = []
    workflow_instance = await get_workflow()
    
    for headline in headlines:
        try:
            result = await workflow_instance.analyze_headline(headline)
            results.append({
                "headline": result.headline,
                "sentiment": {
                    "sentiment_score": result.sentiment.sentiment_score,
                    "sentiment_label": result.sentiment.sentiment_label,
                    "confidence": result.sentiment.confidence,
                },
                "rudeness": {
                    "rudeness_score": result.rudeness.rudeness_score,
                    "tone": result.rudeness.tone,
                    "confidence": result.rudeness.confidence,
                },
                "market_sentiment": {
                    "category": result.market_sentiment.category,
                    "reasoning": result.market_sentiment.reasoning,
                    "response": result.market_sentiment.response,
                },
            })
        except Exception as e:
            results.append({
                "headline": headline,
                "error": f"Analysis failed: {str(e)}",
            })
    
    return results


async def cleanup_workflow():
    """Clean up the workflow resources."""
    global workflow
    if workflow is not None:
        await workflow.close()
        workflow = None


def create_mcp_server() -> FastMCP:
    """Create and return the MCP server instance."""
    return mcp