"""
Sentiment analysis node using FastMCP.
"""

from typing import Any, Dict

from crude_or_rude.models import WorkflowState
from crude_or_rude.services import FastMCPClient


async def sentiment_analysis_node(
    state: WorkflowState, fastmcp_client: FastMCPClient
) -> Dict[str, Any]:
    """
    Analyze sentiment of the headline using FastMCP.

    Args:
        state: The current workflow state
        fastmcp_client: FastMCP client for sentiment analysis

    Returns:
        Updated state with sentiment analysis or fallback mock data
    """
    try:
        sentiment_analysis = await fastmcp_client.analyze_sentiment(state.headline)
        return {"sentiment": sentiment_analysis}

    except Exception as e:
        # Fallback to mock sentiment analysis as per project patterns
        mock_sentiment = {
            "score": 0.1,
            "label": "neutral", 
            "confidence": 0.8,
            "source": "mock_fallback"
        }
        return {
            "sentiment": mock_sentiment,
            "sentiment_warning": f"Using mock data due to FastMCP failure: {str(e)}"
        }
