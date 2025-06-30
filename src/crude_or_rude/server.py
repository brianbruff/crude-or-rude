"""
MCP Server implementation for Crude or Rude market sentiment analyzer.
"""

import asyncio
import os
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP
from crude_or_rude.models import (
    AnalysisResult, 
    HeadlineInput, 
    SentimentAnalysis,
    RudenessAnalysis,
    MarketSentiment,
    WorkflowState
)
from crude_or_rude.nodes import (
    rudeness_detector_node,
    ClaudeDecisionNode
)
from crude_or_rude.services import FastMCPClient


class CrudeOrRudeMCPServer:
    """MCP Server for Crude or Rude sentiment analysis."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.app = FastMCP(
            name="crude-or-rude",
            instructions="Analyze crude oil market sentiment from news headlines. "
                        "Provides sentiment analysis, rudeness detection, and market sentiment classification."
        )
        
        # Initialize components with error handling
        try:
            self.claude_node = ClaudeDecisionNode()
            self.claude_available = True
        except Exception as e:
            print(f"Warning: Claude/AWS Bedrock not available: {e}")
            print("Server will use fallback logic for market sentiment decisions.")
            self.claude_node = None
            self.claude_available = False
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools."""
        
        @self.app.tool(
            name="analyze_headline",
            description="Analyze a crude oil news headline for sentiment, rudeness, and market sentiment classification",
        )
        async def analyze_headline(headline: str, source: str = None) -> Dict[str, Any]:
            """
            Analyze a crude oil news headline comprehensively.
            
            Args:
                headline: The news headline to analyze
                source: Optional source of the news
                
            Returns:
                Complete analysis including sentiment, rudeness, and market sentiment
            """
            try:
                # Create workflow state
                state = WorkflowState(headline=headline, source=source)
                
                # Step 1: Sentiment analysis (using mock since we're now the server)
                sentiment = await self._analyze_sentiment_internal(headline)
                state.sentiment = sentiment
                
                # Step 2: Rudeness detection
                rudeness_result = await rudeness_detector_node(state)
                state.rudeness = rudeness_result["rudeness"]
                
                # Step 3: Market sentiment decision
                if self.claude_available:
                    market_result = await self.claude_node.decide_market_sentiment(state)
                    state.market_sentiment = market_result["market_sentiment"]
                else:
                    # Use fallback logic
                    market_result = await self._fallback_market_sentiment(state)
                    state.market_sentiment = market_result["market_sentiment"]
                
                # Build result
                result = AnalysisResult(
                    headline=headline,
                    sentiment=state.sentiment,
                    rudeness=state.rudeness,
                    market_sentiment=state.market_sentiment
                )
                
                return result.model_dump()
                
            except Exception as e:
                return {
                    "error": f"Analysis failed: {str(e)}",
                    "headline": headline
                }
        
        @self.app.tool(
            name="analyze_sentiment",
            description="Analyze sentiment of a crude oil news headline",
        )
        async def analyze_sentiment(text: str) -> Dict[str, Any]:
            """
            Analyze sentiment of text.
            
            Args:
                text: The text to analyze
                
            Returns:
                Sentiment analysis results
            """
            try:
                sentiment = await self._analyze_sentiment_internal(text)
                return sentiment.model_dump()
            except Exception as e:
                return {"error": f"Sentiment analysis failed: {str(e)}"}
        
        @self.app.tool(
            name="detect_rudeness",
            description="Detect rudeness and tone in a crude oil news headline",
        )
        async def detect_rudeness(headline: str) -> Dict[str, Any]:
            """
            Detect rudeness and tone in a headline.
            
            Args:
                headline: The headline to analyze
                
            Returns:
                Rudeness analysis results
            """
            try:
                state = WorkflowState(headline=headline)
                result = await rudeness_detector_node(state)
                return result["rudeness"].model_dump()
            except Exception as e:
                return {"error": f"Rudeness detection failed: {str(e)}"}
        
        @self.app.tool(
            name="decide_market_sentiment",
            description="Make final market sentiment decision based on sentiment and rudeness analysis",
        )
        async def decide_market_sentiment(
            headline: str,
            sentiment_score: float,
            sentiment_label: str,
            confidence: float,
            rudeness_score: float,
            tone: str,
            rudeness_confidence: float
        ) -> Dict[str, Any]:
            """
            Make market sentiment decision.
            
            Args:
                headline: The original headline
                sentiment_score: Sentiment score (-1.0 to 1.0)
                sentiment_label: Sentiment label (positive/negative/neutral)
                confidence: Sentiment confidence (0.0 to 1.0)
                rudeness_score: Rudeness score (0.0 to 1.0)
                tone: Tone classification (professional/aggressive/passive-aggressive)
                rudeness_confidence: Rudeness confidence (0.0 to 1.0)
                
            Returns:
                Market sentiment decision
            """
            try:
                # Create state with provided analysis
                state = WorkflowState(
                    headline=headline,
                    sentiment=SentimentAnalysis(
                        sentiment_score=sentiment_score,
                        sentiment_label=sentiment_label,
                        confidence=confidence
                    ),
                    rudeness=RudenessAnalysis(
                        rudeness_score=rudeness_score,
                        tone=tone,
                        confidence=rudeness_confidence
                    )
                )
                
                if self.claude_available:
                    result = await self.claude_node.decide_market_sentiment(state)
                else:
                    result = await self._fallback_market_sentiment(state)
                return result["market_sentiment"].model_dump()
            except Exception as e:
                return {"error": f"Market sentiment decision failed: {str(e)}"}
    
    async def _analyze_sentiment_internal(self, text: str) -> SentimentAnalysis:
        """
        Internal sentiment analysis using the mock implementation.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis result
        """
        # Use the mock sentiment analysis from FastMCPClient
        # This is the same logic but without external dependency
        text_lower = text.lower()

        # Simple keyword-based sentiment analysis
        positive_keywords = [
            "surge", "bull", "rise", "gain", "up", "increase", "boost",
            "optimistic", "strong", "rally", "breakthrough",
        ]
        negative_keywords = [
            "crash", "bear", "fall", "drop", "down", "decline", "plunge",
            "crisis", "panic", "weak", "collapse", "disaster", "cut",
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
    
    async def _fallback_market_sentiment(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Fallback market sentiment decision when Claude is not available.
        
        Args:
            state: The workflow state with sentiment and rudeness analysis
            
        Returns:
            Market sentiment decision
        """
        sentiment_score = state.sentiment.sentiment_score
        rudeness_score = state.rudeness.rudeness_score
        tone = state.rudeness.tone

        # Simple rule-based classification
        if tone == "aggressive" or rudeness_score > 0.7:
            category = "Panic-stricken"
            reasoning = f"High rudeness score ({rudeness_score:.2f}) and aggressive tone indicate market panic"
            response = "This market is having a complete meltdown!"
        elif tone == "passive-aggressive" or (
            rudeness_score > 0.4 and abs(sentiment_score) < 0.3
        ):
            category = "Passive-aggressive"
            reasoning = (
                f"Passive-aggressive tone with mixed signals "
                f"(sentiment: {sentiment_score:.2f})"
            )
            response = "This market is gaslighting you with mixed signals."
        else:
            category = "Professional"
            reasoning = (
                f"Low rudeness score ({rudeness_score:.2f}) and professional tone"
            )
            response = "The market is being surprisingly reasonable today."

        market_sentiment = MarketSentiment(
            category=category, reasoning=reasoning, response=response
        )

        return {"market_sentiment": market_sentiment}
    
    def get_fastmcp_app(self):
        """Get the FastMCP app for running the server."""
        return self.app.sse_app


# Global server instance
server = CrudeOrRudeMCPServer()