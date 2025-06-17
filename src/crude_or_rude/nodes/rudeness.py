"""
Mock rudeness detector NLP node.
"""

import random
from typing import Any, Dict

from crude_or_rude.models import RudenessAnalysis, WorkflowState


async def rudeness_detector_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Mock NLP node for detecting rudeness/aggressiveness in headlines.

    This simulates an NLP model that analyzes the tone and aggressiveness
    of news headlines about crude oil markets.

    Args:
        state: The current workflow state

    Returns:
        Updated state with rudeness analysis
    """
    headline = state.headline.lower()

    # Keywords for different tone categories
    professional_keywords = [
        "reports",
        "announces",
        "states",
        "according",
        "official",
        "data",
        "statistics",
        "analysis",
        "forecast",
        "projection",
    ]

    aggressive_keywords = [
        "slams",
        "blasts",
        "crashes",
        "plummets",
        "devastates",
        "destroys",
        "annihilates",
        "obliterates",
        "disaster",
        "chaos",
    ]

    passive_aggressive_keywords = [
        "despite",
        "however",
        "surprisingly",
        "unexpectedly",
        "ironically",
        "curiously",
        "interesting",
        "convenient",
        "timely",
        "coincidentally",
    ]

    # Count keyword matches
    professional_score = sum(1 for word in professional_keywords if word in headline)
    aggressive_score = sum(1 for word in aggressive_keywords if word in headline)
    passive_aggressive_score = sum(
        1 for word in passive_aggressive_keywords if word in headline
    )

    # Determine tone based on keyword counts and some randomness for variety
    total_keywords = professional_score + aggressive_score + passive_aggressive_score

    if total_keywords == 0:
        # No clear indicators, use some heuristics
        if any(word in headline for word in ["cut", "drop", "fall", "decline"]):
            tone = "passive-aggressive"
            rudeness_score = 0.4 + random.uniform(0.0, 0.2)
        elif any(word in headline for word in ["surge", "soar", "rocket", "explode"]):
            tone = "aggressive"
            rudeness_score = 0.6 + random.uniform(0.0, 0.3)
        else:
            tone = "professional"
            rudeness_score = 0.1 + random.uniform(0.0, 0.2)
    else:
        if aggressive_score > max(professional_score, passive_aggressive_score):
            tone = "aggressive"
            rudeness_score = 0.7 + (aggressive_score * 0.1) + random.uniform(0.0, 0.2)
        elif passive_aggressive_score > professional_score:
            tone = "passive-aggressive"
            rudeness_score = (
                0.5 + (passive_aggressive_score * 0.1) + random.uniform(0.0, 0.2)
            )
        else:
            tone = "professional"
            rudeness_score = (
                0.1 + (professional_score * 0.05) + random.uniform(0.0, 0.1)
            )

    # Ensure rudeness_score is within bounds
    rudeness_score = min(1.0, max(0.0, rudeness_score))

    # Calculate confidence based on keyword strength
    confidence = min(0.95, 0.6 + (total_keywords * 0.1) + random.uniform(0.0, 0.1))

    rudeness_analysis = RudenessAnalysis(
        rudeness_score=rudeness_score, tone=tone, confidence=confidence
    )

    # Update state
    new_state = state.model_copy()
    new_state.rudeness = rudeness_analysis

    return {"rudeness": rudeness_analysis}
