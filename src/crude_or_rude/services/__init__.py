"""
Internal sentiment analysis service for the Crude or Rude application.
"""

from crude_or_rude.models import SentimentAnalysis


class SentimentAnalysisService:
    """Internal sentiment analysis service."""

    def __init__(self):
        """Initialize the service."""
        pass

    async def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """
        Analyze sentiment of text using internal logic.

        Args:
            text: The text to analyze

        Returns:
            SentimentAnalysis object with results
        """
        return await self._sentiment_analysis(text)

    async def _sentiment_analysis(self, text: str) -> SentimentAnalysis:
        """
        Internal sentiment analysis based on keyword matching.

        This provides basic sentiment analysis based on crude oil market keywords.
        """
        text_lower = text.lower()

        # Crude oil market specific keywords
        positive_keywords = [
            "surge",
            "bull",
            "bullish",
            "rise",
            "rising",
            "gain",
            "gains",
            "up",
            "upward",
            "increase",
            "increased",
            "boost",
            "boosted",
            "optimistic",
            "strong",
            "stronger",
            "rally",
            "rallied",
            "breakthrough",
            "recovery",
            "demand",
            "growth",
            "stable",
            "stability",
            "support",
            "supported",
        ]
        negative_keywords = [
            "crash",
            "crashed",
            "bear",
            "bearish",
            "fall",
            "falling",
            "fell",
            "drop",
            "dropped",
            "dropping",
            "down",
            "downward",
            "decline",
            "declined",
            "declining",
            "plunge",
            "plunged",
            "crisis",
            "panic",
            "panicked",
            "weak",
            "weaker",
            "weakness",
            "collapse",
            "collapsed",
            "disaster",
            "cut",
            "cuts",
            "cutting",
            "recession",
            "fears",
            "concerns",
            "pressure",
            "oversupply",
            "glut",
        ]

        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)

        # Calculate sentiment score with enhanced weighting
        if positive_count > negative_count:
            base_score = 0.3 + (positive_count * 0.15)
            sentiment_score = min(0.9, base_score)
            sentiment_label = "positive"
        elif negative_count > positive_count:
            base_score = -0.3 - (negative_count * 0.15)
            sentiment_score = max(-0.9, base_score)
            sentiment_label = "negative"
        else:
            sentiment_score = 0.0
            sentiment_label = "neutral"

        # Calculate confidence based on keyword matches and text length
        match_strength = (positive_count + negative_count) / max(len(text.split()), 1)
        confidence = min(0.95, 0.6 + match_strength * 0.3)

        return SentimentAnalysis(
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            confidence=confidence,
        )
