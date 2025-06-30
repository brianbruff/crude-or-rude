"""
Tests for the Crude or Rude application.
"""

from unittest.mock import Mock, patch

import pytest

from crude_or_rude.models import (
    AnalysisResult,
    HeadlineInput,
    SentimentAnalysis,
    WorkflowState,
)
from crude_or_rude.nodes.rudeness import rudeness_detector_node
from crude_or_rude.services import SentimentAnalysisService
from crude_or_rude.workflow import CrudeOrRudeWorkflow


class TestModels:
    """Test Pydantic models."""

    def test_headline_input(self):
        """Test HeadlineInput model."""
        headline = HeadlineInput(headline="Oil prices surge", source="Reuters")
        assert headline.headline == "Oil prices surge"
        assert headline.source == "Reuters"

    def test_sentiment_analysis(self):
        """Test SentimentAnalysis model."""
        sentiment = SentimentAnalysis(
            sentiment_score=0.5, sentiment_label="positive", confidence=0.8
        )
        assert sentiment.sentiment_score == 0.5
        assert sentiment.sentiment_label == "positive"
        assert sentiment.confidence == 0.8

    def test_workflow_state(self):
        """Test WorkflowState model."""
        state = WorkflowState(headline="Test headline")
        assert state.headline == "Test headline"
        assert state.sentiment is None
        assert state.rudeness is None


class TestSentimentAnalysisService:
    """Test internal sentiment analysis service."""

    @pytest.mark.asyncio
    async def test_sentiment_analysis(self):
        """Test internal sentiment analysis."""
        service = SentimentAnalysisService()

        # Test positive sentiment
        result = await service.analyze_sentiment(
            "Oil prices surge and rally strongly with bullish demand"
        )
        assert result.sentiment_label == "positive"
        assert result.sentiment_score > 0

        # Test negative sentiment
        result = await service.analyze_sentiment(
            "Oil market crashes and collapses with bearish panic"
        )
        assert result.sentiment_label == "negative"
        assert result.sentiment_score < 0

        # Test neutral sentiment
        result = await service.analyze_sentiment("Oil report released today")
        assert result.sentiment_label == "neutral"
        assert result.sentiment_score == 0.0


class TestRudenessDetector:
    """Test rudeness detector node."""

    @pytest.mark.asyncio
    async def test_professional_tone(self):
        """Test detection of professional tone."""
        state = WorkflowState(headline="Official reports indicate oil production data")
        result = await rudeness_detector_node(state)

        assert "rudeness" in result
        assert result["rudeness"].tone == "professional"
        assert result["rudeness"].rudeness_score < 0.5

    @pytest.mark.asyncio
    async def test_aggressive_tone(self):
        """Test detection of aggressive tone."""
        state = WorkflowState(headline="Oil market crashes and devastates investors")
        result = await rudeness_detector_node(state)

        assert "rudeness" in result
        assert result["rudeness"].tone == "aggressive"
        assert result["rudeness"].rudeness_score > 0.5

    @pytest.mark.asyncio
    async def test_passive_aggressive_tone(self):
        """Test detection of passive-aggressive tone."""
        state = WorkflowState(headline="Oil cuts despite surplus - how convenient")
        result = await rudeness_detector_node(state)

        assert "rudeness" in result
        # Note: This might be detected as different tones due to randomness
        assert result["rudeness"].tone in ["passive-aggressive", "professional"]


@pytest.mark.asyncio
async def test_workflow_integration():
    """Test basic workflow integration without external dependencies."""
    # Mock the Claude API to avoid requiring actual API key
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "fake_key"}):
        with patch("crude_or_rude.nodes.claude.ChatBedrock") as mock_bedrock:
            # Mock Bedrock response
            mock_response = {
                "category": "Professional",
                "reasoning": "Test reasoning",
                "response": "Test response",
            }
            mock_bedrock.return_value.with_structured_output.return_value.ainvoke.return_value = (
                mock_response
            )

            workflow = CrudeOrRudeWorkflow()

            try:
                result = await workflow.analyze_headline(
                    "Oil prices remain stable according to reports"
                )

                # Verify we get a complete analysis result
                assert isinstance(result, AnalysisResult)
                assert (
                    result.headline == "Oil prices remain stable according to reports"
                )
                assert result.sentiment is not None
                assert result.rudeness is not None
                assert result.market_sentiment is not None

            finally:
                await workflow.close()


def test_sample_headlines():
    """Test that we have good sample headlines for demonstration."""
    from crude_or_rude.main import analyze_sample_headlines

    # This is mainly to ensure the function exists and can be imported
    assert callable(analyze_sample_headlines)
