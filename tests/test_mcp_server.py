"""
Test the MCP server functionality.
"""

import pytest
from unittest.mock import patch, Mock

from crude_or_rude.server import CrudeOrRudeMCPServer


class TestMCPServer:
    """Test MCP server functionality."""

    def test_server_creation(self):
        """Test that the server can be created."""
        server = CrudeOrRudeMCPServer()
        assert server is not None
        assert server.server.name == "crude-or-rude"

    @pytest.mark.asyncio 
    async def test_analyze_sentiment_tool(self):
        """Test the analyze_sentiment tool."""
        with patch.dict("os.environ", {"AWS_DEFAULT_REGION": "us-east-1"}):
            with patch("crude_or_rude.nodes.claude.ChatBedrock"):
                server = CrudeOrRudeMCPServer()
                
                # Test sentiment analysis
                arguments = {"text": "Oil prices surge with strong bullish demand"}
                result = await server._analyze_sentiment(arguments)
                
                assert len(result) == 1
                assert "positive" in result[0].text.lower()
                assert "sentiment" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_detect_rudeness_tool(self):
        """Test the detect_rudeness tool."""
        with patch.dict("os.environ", {"AWS_DEFAULT_REGION": "us-east-1"}):
            with patch("crude_or_rude.nodes.claude.ChatBedrock"):
                server = CrudeOrRudeMCPServer()
                
                # Test rudeness detection
                arguments = {"text": "Oil markets are in complete chaos and panic"}
                result = await server._detect_rudeness(arguments)
                
                assert len(result) == 1
                assert "tone" in result[0].text.lower()
        
    @pytest.mark.asyncio
    async def test_analyze_headline_tool_mock(self):
        """Test the analyze_headline tool with mocked workflow."""
        with patch.dict("os.environ", {"AWS_DEFAULT_REGION": "us-east-1"}):
            with patch("crude_or_rude.nodes.claude.ChatBedrock"):
                server = CrudeOrRudeMCPServer()
                
                # Mock the workflow to avoid AWS dependencies
                with patch('crude_or_rude.workflow.CrudeOrRudeWorkflow') as mock_workflow_class:
                    # Create a mock workflow instance
                    mock_workflow = Mock()
                    mock_workflow_class.return_value = mock_workflow
                    
                    # Mock the analysis result
                    from crude_or_rude.models import AnalysisResult, SentimentAnalysis, RudenessAnalysis, MarketSentiment
                    
                    mock_result = AnalysisResult(
                        headline="Test headline",
                        sentiment=SentimentAnalysis(
                            sentiment_score=0.5,
                            sentiment_label="positive", 
                            confidence=0.8
                        ),
                        rudeness=RudenessAnalysis(
                            rudeness_score=0.3,
                            tone="professional",
                            confidence=0.7
                        ),
                        market_sentiment=MarketSentiment(
                            category="Professional",
                            reasoning="Test reasoning",
                            response="Test response"
                        )
                    )
                    
                    mock_workflow.analyze_headline.return_value = mock_result
                    
                    # Test headline analysis
                    arguments = {"headline": "Test headline"}
                    result = await server._analyze_headline(arguments)
                    
                    assert len(result) == 1
                    assert "Professional" in result[0].text
                    assert "Test headline" in result[0].text

    def test_error_handling(self):
        """Test error handling for missing arguments."""
        server = CrudeOrRudeMCPServer()
        
        # Test missing text argument
        import asyncio
        
        async def test_missing_text():
            try:
                await server._analyze_sentiment({})
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "text is required" in str(e)
        
        asyncio.run(test_missing_text())