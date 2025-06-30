"""
Test the MCP server functionality.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from crude_or_rude.mcp_server import create_mcp_server
from crude_or_rude.models import AnalysisResult, SentimentAnalysis, RudenessAnalysis, MarketSentiment


@pytest.mark.asyncio
async def test_mcp_server_creation():
    """Test that the MCP server can be created."""
    server = create_mcp_server()
    assert server is not None
    assert server.name == "crude-or-rude"


@pytest.mark.asyncio
async def test_get_sample_headlines_tool():
    """Test the get_sample_headlines tool."""
    server = create_mcp_server()
    
    # Get the tool function directly
    result = await server.call_tool("get_sample_headlines", {})
    
    # The result appears to be a tuple with text content and structured data
    # Extract the structured data
    if isinstance(result, tuple) and len(result) > 1:
        structured_result = result[1].get('result', result[1])
    else:
        structured_result = result
    
    # Check that we get a list of sample headlines
    assert isinstance(structured_result, list)
    assert len(structured_result) > 0
    assert all(isinstance(headline, str) for headline in structured_result)
    assert "OPEC" in str(structured_result)  # Should contain OPEC-related headlines


@pytest.mark.asyncio
async def test_analyze_crude_headline_tool_with_mock():
    """Test the analyze_crude_headline tool with mocked workflow."""
    server = create_mcp_server()
    
    # Mock the workflow result
    mock_sentiment = SentimentAnalysis(
        sentiment_score=0.5,
        sentiment_label="positive",
        confidence=0.8
    )
    mock_rudeness = RudenessAnalysis(
        rudeness_score=0.2,
        tone="professional",
        confidence=0.9
    )
    mock_market_sentiment = MarketSentiment(
        category="Professional",
        reasoning="Test reasoning",
        response="Test response"
    )
    mock_result = AnalysisResult(
        headline="Test headline",
        sentiment=mock_sentiment,
        rudeness=mock_rudeness,
        market_sentiment=mock_market_sentiment
    )
    
    # Mock the workflow
    with patch('crude_or_rude.mcp_server.get_workflow') as mock_get_workflow:
        mock_workflow = AsyncMock()
        mock_workflow.analyze_headline.return_value = mock_result
        mock_get_workflow.return_value = mock_workflow
        
        # Call the tool
        result = await server.call_tool("analyze_crude_headline", {
            "headline": "Test headline"
        })
        
        # Extract structured data from the result
        if isinstance(result, tuple) and len(result) > 1:
            structured_result = result[1]
        else:
            structured_result = result
        
        # Verify the result structure
        assert isinstance(structured_result, dict)
        assert structured_result["headline"] == "Test headline"
        assert "sentiment" in structured_result
        assert "rudeness" in structured_result
        assert "market_sentiment" in structured_result
        
        # Check sentiment structure
        assert structured_result["sentiment"]["sentiment_score"] == 0.5
        assert structured_result["sentiment"]["sentiment_label"] == "positive"
        assert structured_result["sentiment"]["confidence"] == 0.8
        
        # Check rudeness structure
        assert structured_result["rudeness"]["rudeness_score"] == 0.2
        assert structured_result["rudeness"]["tone"] == "professional"
        assert structured_result["rudeness"]["confidence"] == 0.9
        
        # Check market sentiment structure
        assert structured_result["market_sentiment"]["category"] == "Professional"
        assert structured_result["market_sentiment"]["reasoning"] == "Test reasoning"
        assert structured_result["market_sentiment"]["response"] == "Test response"


@pytest.mark.asyncio
async def test_analyze_crude_headline_tool_with_error():
    """Test the analyze_crude_headline tool error handling."""
    server = create_mcp_server()
    
    # Mock the workflow to raise an exception
    with patch('crude_or_rude.mcp_server.get_workflow') as mock_get_workflow:
        mock_workflow = AsyncMock()
        mock_workflow.analyze_headline.side_effect = Exception("Test error")
        mock_get_workflow.return_value = mock_workflow
        
        # Call the tool
        result = await server.call_tool("analyze_crude_headline", {
            "headline": "Test headline"
        })
        
        # Extract structured data from the result
        if isinstance(result, tuple) and len(result) > 1:
            structured_result = result[1]
        else:
            structured_result = result
        
        # Verify error handling
        assert isinstance(structured_result, dict)
        assert "error" in structured_result
        assert "Test error" in structured_result["error"]
        assert structured_result["headline"] == "Test headline"


@pytest.mark.asyncio
async def test_analyze_multiple_headlines_tool():
    """Test the analyze_multiple_headlines tool."""
    server = create_mcp_server()
    
    # Mock the workflow
    mock_sentiment = SentimentAnalysis(
        sentiment_score=0.3,
        sentiment_label="neutral",
        confidence=0.7
    )
    mock_rudeness = RudenessAnalysis(
        rudeness_score=0.1,
        tone="professional",
        confidence=0.8
    )
    mock_market_sentiment = MarketSentiment(
        category="Professional",
        reasoning="Test reasoning",
        response="Test response"
    )
    
    def mock_analyze_headline(headline):
        return AnalysisResult(
            headline=headline,
            sentiment=mock_sentiment,
            rudeness=mock_rudeness,
            market_sentiment=mock_market_sentiment
        )
    
    with patch('crude_or_rude.mcp_server.get_workflow') as mock_get_workflow:
        mock_workflow = AsyncMock()
        mock_workflow.analyze_headline.side_effect = mock_analyze_headline
        mock_get_workflow.return_value = mock_workflow
        
        # Call the tool with multiple headlines
        headlines = ["Headline 1", "Headline 2"]
        result = await server.call_tool("analyze_multiple_headlines", {
            "headlines": headlines
        })
        
        # Extract structured data from the result
        if isinstance(result, tuple) and len(result) > 1:
            structured_result = result[1].get('result', result[1])
        else:
            structured_result = result
        
        # Verify the result
        assert isinstance(structured_result, list)
        assert len(structured_result) == 2
        
        for i, analysis in enumerate(structured_result):
            assert analysis["headline"] == headlines[i]
            assert "sentiment" in analysis
            assert "rudeness" in analysis
            assert "market_sentiment" in analysis


@pytest.mark.asyncio
async def test_list_tools():
    """Test that the server exposes the expected tools."""
    server = create_mcp_server()
    
    tools = await server.list_tools()
    tool_names = [tool.name for tool in tools]
    
    expected_tools = [
        "analyze_crude_headline",
        "get_sample_headlines", 
        "analyze_multiple_headlines"
    ]
    
    for expected_tool in expected_tools:
        assert expected_tool in tool_names