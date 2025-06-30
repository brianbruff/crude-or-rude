"""
LangGraph workflow for the Crude or Rude market sentiment analyzer.
"""

import os
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from crude_or_rude.models import AnalysisResult, WorkflowState
from crude_or_rude.nodes import (
    ClaudeDecisionNode,
    rudeness_detector_node,
    sentiment_analysis_node,
)
from crude_or_rude.services import FastMCPClient


class CrudeOrRudeWorkflow:
    """Main workflow orchestrator using LangGraph."""

    def __init__(self, fastmcp_url: str = None, aws_region: str = None):
        """
        Initialize the workflow.

        Args:
            fastmcp_url: URL for FastMCP service
            aws_region: AWS region for Bedrock service (optional, uses CLI default)
        """
        self.fastmcp_url = fastmcp_url or os.getenv(
            "FASTMCP_URL", "http://localhost:8000"
        )
        self.fastmcp_client = FastMCPClient(self.fastmcp_url)
        
        # Initialize Claude node with error handling
        try:
            self.claude_node = ClaudeDecisionNode(aws_region)
            self.claude_available = True
        except Exception as e:
            print(f"Warning: Claude/AWS Bedrock not available: {e}")
            print("Using fallback logic for market sentiment decisions.")
            self.claude_node = None
            self.claude_available = False
            
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""

        # Create workflow graph
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("analyze_sentiment", self._sentiment_node)
        workflow.add_node("analyze_rudeness", self._rudeness_node)
        workflow.add_node("make_decision", self._claude_node)

        # Define edges
        workflow.set_entry_point("analyze_sentiment")
        workflow.add_edge("analyze_sentiment", "analyze_rudeness")
        workflow.add_edge("analyze_rudeness", "make_decision")
        workflow.add_edge("make_decision", END)

        return workflow.compile()

    async def _sentiment_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Wrapper for sentiment analysis node."""
        return await sentiment_analysis_node(state, self.fastmcp_client)

    async def _rudeness_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Wrapper for rudeness detector node."""
        return await rudeness_detector_node(state)

    async def _claude_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Wrapper for Claude decision node."""
        if self.claude_available:
            return await self.claude_node.decide_market_sentiment(state)
        else:
            # Use fallback logic when Claude is not available
            return await self._fallback_market_sentiment(state)

    async def analyze_headline(
        self, headline: str, source: str = None
    ) -> AnalysisResult:
        """
        Analyze a crude oil news headline.

        Args:
            headline: The news headline to analyze
            source: Optional source of the news

        Returns:
            Complete analysis result
        """
        # Initialize state
        initial_state = WorkflowState(headline=headline, source=source)

        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)

            # Check for errors
            if final_state.get("error"):
                raise RuntimeError(f"Workflow error: {final_state['error']}")

            # Build result
            result = AnalysisResult(
                headline=headline,
                sentiment=final_state["sentiment"],
                rudeness=final_state["rudeness"],
                market_sentiment=final_state["market_sentiment"],
            )

            return result

        except Exception as e:
            raise RuntimeError(f"Analysis failed: {str(e)}")

    async def close(self):
        """Clean up resources."""
        await self.fastmcp_client.close()
    
    async def _fallback_market_sentiment(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Fallback market sentiment decision when Claude is not available.
        
        Args:
            state: The workflow state with sentiment and rudeness analysis
            
        Returns:
            Market sentiment decision
        """
        from crude_or_rude.models import MarketSentiment
        
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
