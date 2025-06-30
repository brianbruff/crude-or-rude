#!/usr/bin/env python3
"""
Manual test script for the MCP server tools.
This tests the tools directly without requiring AWS credentials.
"""

import asyncio
import sys
from unittest.mock import AsyncMock, patch

# Import the MCP server components
from crude_or_rude.mcp_server import create_mcp_server
from crude_or_rude.models import AnalysisResult, SentimentAnalysis, RudenessAnalysis, MarketSentiment


async def test_sample_headlines():
    """Test the sample headlines tool."""
    print("🧪 Testing get_sample_headlines tool...")
    
    server = create_mcp_server()
    result = await server.call_tool("get_sample_headlines", {})
    
    # Extract the actual data
    if isinstance(result, tuple) and len(result) > 1:
        headlines = result[1].get('result', result[1])
    else:
        headlines = result
    
    print(f"✅ Got {len(headlines)} sample headlines")
    for i, headline in enumerate(headlines[:3], 1):
        print(f"  {i}. {headline}")
    
    if len(headlines) > 3:
        print(f"  ... and {len(headlines) - 3} more")
    
    return True


async def test_analysis_with_mock():
    """Test the analysis tool with mocked workflow."""
    print("\n🧪 Testing analyze_crude_headline tool with mock data...")
    
    # Create mock analysis result
    mock_sentiment = SentimentAnalysis(
        sentiment_score=0.6,
        sentiment_label="positive",
        confidence=0.85
    )
    mock_rudeness = RudenessAnalysis(
        rudeness_score=0.1,
        tone="professional",
        confidence=0.90
    )
    mock_market_sentiment = MarketSentiment(
        category="Professional",
        reasoning="Market shows genuine optimism with clear positive indicators",
        response="This market is actually being reasonable for once - how refreshing!"
    )
    mock_result = AnalysisResult(
        headline="Oil prices rise on strong demand outlook",
        sentiment=mock_sentiment,
        rudeness=mock_rudeness,
        market_sentiment=mock_market_sentiment
    )
    
    server = create_mcp_server()
    
    # Mock the workflow to avoid AWS dependencies
    with patch('crude_or_rude.mcp_server.get_workflow') as mock_get_workflow:
        mock_workflow = AsyncMock()
        mock_workflow.analyze_headline.return_value = mock_result
        mock_get_workflow.return_value = mock_workflow
        
        # Test the tool
        result = await server.call_tool("analyze_crude_headline", {
            "headline": "Oil prices rise on strong demand outlook",
            "source": "Reuters"
        })
        
        # Extract the actual data
        if isinstance(result, tuple) and len(result) > 1:
            analysis = result[1]
        else:
            analysis = result
        
        print("✅ Analysis completed successfully!")
        print(f"📰 Headline: {analysis['headline']}")
        print(f"💭 Sentiment: {analysis['sentiment']['sentiment_label']} ({analysis['sentiment']['sentiment_score']:.2f})")
        print(f"🗣️  Tone: {analysis['rudeness']['tone']} (rudeness: {analysis['rudeness']['rudeness_score']:.2f})")
        print(f"🎯 Market Sentiment: {analysis['market_sentiment']['category']}")
        print(f"🤡 Market Says: \"{analysis['market_sentiment']['response']}\"")
        
        return True


async def test_batch_analysis():
    """Test batch analysis tool."""
    print("\n🧪 Testing analyze_multiple_headlines tool...")
    
    # Mock data for multiple headlines
    mock_sentiment = SentimentAnalysis(sentiment_score=0.3, sentiment_label="neutral", confidence=0.7)
    mock_rudeness = RudenessAnalysis(rudeness_score=0.2, tone="professional", confidence=0.8)
    mock_market_sentiment = MarketSentiment(
        category="Professional",
        reasoning="Neutral market conditions",
        response="Markets are playing it cool today"
    )
    
    def create_mock_result(headline):
        return AnalysisResult(
            headline=headline,
            sentiment=mock_sentiment,
            rudeness=mock_rudeness,
            market_sentiment=mock_market_sentiment
        )
    
    server = create_mcp_server()
    
    with patch('crude_or_rude.mcp_server.get_workflow') as mock_get_workflow:
        mock_workflow = AsyncMock()
        mock_workflow.analyze_headline.side_effect = create_mock_result
        mock_get_workflow.return_value = mock_workflow
        
        test_headlines = [
            "Oil inventories show weekly decline",
            "OPEC maintains production targets",
            "Crude futures trade sideways in quiet session"
        ]
        
        result = await server.call_tool("analyze_multiple_headlines", {
            "headlines": test_headlines
        })
        
        # Extract the actual data
        if isinstance(result, tuple) and len(result) > 1:
            analyses = result[1].get('result', result[1])
        else:
            analyses = result
        
        print(f"✅ Analyzed {len(analyses)} headlines in batch")
        for i, analysis in enumerate(analyses, 1):
            print(f"  {i}. {analysis['headline']} → {analysis['market_sentiment']['category']}")
        
        return True


async def test_error_handling():
    """Test error handling."""
    print("\n🧪 Testing error handling...")
    
    server = create_mcp_server()
    
    with patch('crude_or_rude.mcp_server.get_workflow') as mock_get_workflow:
        mock_workflow = AsyncMock()
        mock_workflow.analyze_headline.side_effect = Exception("Mock AWS error")
        mock_get_workflow.return_value = mock_workflow
        
        result = await server.call_tool("analyze_crude_headline", {
            "headline": "Test headline that will fail"
        })
        
        # Extract the actual data
        if isinstance(result, tuple) and len(result) > 1:
            analysis = result[1]
        else:
            analysis = result
        
        if "error" in analysis:
            print("✅ Error handling works correctly")
            print(f"   Error message: {analysis['error']}")
            return True
        else:
            print("❌ Error handling failed")
            return False


async def main():
    """Run all tests."""
    print("🛢️ Crude or Rude MCP Server - Manual Testing")
    print("=" * 50)
    
    tests = [
        test_sample_headlines,
        test_analysis_with_mock,
        test_batch_analysis,
        test_error_handling
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} tests passed!")
        print("\n🎉 MCP server is ready for Claude Desktop integration!")
        print("\n📖 Next steps:")
        print("   1. Configure Claude Desktop using CLAUDE_DESKTOP_SETUP.md")
        print("   2. Start server with: poetry run crude-or-rude --server")
        print("   3. Connect from Claude Desktop and test with real headlines")
        return 0
    else:
        print(f"❌ {passed}/{total} tests passed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))