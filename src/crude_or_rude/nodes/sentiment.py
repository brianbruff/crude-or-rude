"""
Sentiment analysis node using internal sentiment analysis service.
"""

from typing import Any, Dict

from crude_or_rude.models import WorkflowState
from crude_or_rude.services import SentimentAnalysisService


async def sentiment_analysis_node(
    state: WorkflowState, sentiment_service: SentimentAnalysisService
) -> Dict[str, Any]:
    """
    Analyze sentiment of the headline using internal sentiment analysis.

    Args:
        state: The current workflow state
        sentiment_service: Internal sentiment analysis service

    Returns:
        Updated state with sentiment analysis
    """
    try:
        sentiment_analysis = await sentiment_service.analyze_sentiment(state.headline)
        return {"sentiment": sentiment_analysis}

    except Exception as e:
        # This should rarely fail since it's internal logic
        return {"error": f"Sentiment analysis failed: {str(e)}"}
