"""
Tests for the MCP server functionality.
"""

import pytest
from crude_or_rude.server import CrudeOrRudeMCPServer


class TestMCPServer:
    """Test MCP server functionality."""

    def test_server_initialization(self):
        """Test server initializes correctly."""
        server = CrudeOrRudeMCPServer()
        assert server.app is not None
        assert server.app.name == "crude-or-rude"
        assert "Analyze" in server.app.instructions

    @pytest.mark.asyncio
    async def test_sentiment_analysis_internal(self):
        """Test internal sentiment analysis."""
        server = CrudeOrRudeMCPServer()
        
        # Test positive sentiment
        result = await server._analyze_sentiment_internal("Oil prices surge strongly")
        assert result.sentiment_label == "positive"
        assert result.sentiment_score > 0
        
        # Test negative sentiment
        result = await server._analyze_sentiment_internal("Oil market crashes dramatically")
        assert result.sentiment_label == "negative"
        assert result.sentiment_score < 0
        
        # Test neutral sentiment
        result = await server._analyze_sentiment_internal("Oil report released today")
        assert result.sentiment_label == "neutral"
        assert result.sentiment_score == 0.0

    @pytest.mark.asyncio
    async def test_fallback_market_sentiment(self):
        """Test fallback market sentiment logic."""
        from crude_or_rude.models import WorkflowState, SentimentAnalysis, RudenessAnalysis
        
        server = CrudeOrRudeMCPServer()
        
        # Test aggressive market sentiment
        state = WorkflowState(
            headline="Oil market crashes",
            sentiment=SentimentAnalysis(
                sentiment_score=-0.8,
                sentiment_label="negative",
                confidence=0.9
            ),
            rudeness=RudenessAnalysis(
                rudeness_score=0.8,
                tone="aggressive",
                confidence=0.9
            )
        )
        
        result = await server._fallback_market_sentiment(state)
        assert result["market_sentiment"].category == "Panic-stricken"
        assert "meltdown" in result["market_sentiment"].response.lower()

    def test_server_tools_registered(self):
        """Test that all expected tools are registered."""
        server = CrudeOrRudeMCPServer()
        
        # Check that tools are registered in the FastMCP app
        # This is a basic check that the server initializes without errors
        assert hasattr(server.app, "_tool_manager")
        assert server.app._tool_manager is not None