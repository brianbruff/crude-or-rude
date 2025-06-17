"""
FastMCP service client for sentiment analysis.
"""

import httpx

from crude_or_rude.models import SentimentAnalysis


class FastMCPClient:
    """Client for FastMCP sentiment analysis service."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient()

    async def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """
        Analyze sentiment of text using FastMCP.

        Args:
            text: The text to analyze

        Returns:
            SentimentAnalysis object with results
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/analyze/sentiment", json={"text": text}
            )
            response.raise_for_status()
            data = response.json()

            return SentimentAnalysis(
                sentiment_score=data.get("sentiment_score", 0.0),
                sentiment_label=data.get("sentiment_label", "neutral"),
                confidence=data.get("confidence", 0.5),
            )
        except Exception:
            # Fallback to mock sentiment analysis if FastMCP is not available
            return await self._mock_sentiment_analysis(text)

    async def _mock_sentiment_analysis(self, text: str) -> SentimentAnalysis:
        """
        Mock sentiment analysis for when FastMCP is not available.

        This provides basic sentiment analysis based on keyword matching.
        """
        text_lower = text.lower()

        # Simple keyword-based sentiment analysis
        positive_keywords = [
            "surge",
            "bull",
            "rise",
            "gain",
            "up",
            "increase",
            "boost",
            "optimistic",
            "strong",
            "rally",
            "breakthrough",
        ]
        negative_keywords = [
            "crash",
            "bear",
            "fall",
            "drop",
            "down",
            "decline",
            "plunge",
            "crisis",
            "panic",
            "weak",
            "collapse",
            "disaster",
            "cut",
        ]

        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)

        if positive_count > negative_count:
            sentiment_score = min(0.8, 0.3 + (positive_count * 0.1))
            sentiment_label = "positive"
        elif negative_count > positive_count:
            sentiment_score = max(-0.8, -0.3 - (negative_count * 0.1))
            sentiment_label = "negative"
        else:
            sentiment_score = 0.0
            sentiment_label = "neutral"

        confidence = min(0.9, 0.5 + abs(sentiment_score) * 0.5)

        return SentimentAnalysis(
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            confidence=confidence,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
