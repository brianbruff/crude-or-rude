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
        Updated state with sentiment analysis
    """
    try:
        sentiment_analysis = await fastmcp_client.analyze_sentiment(state.headline)

        return {"sentiment": sentiment_analysis}

    except Exception as e:
        return {"error": f"Sentiment analysis failed: {str(e)}"}
