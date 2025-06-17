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

    def __init__(self, fastmcp_url: str = None, anthropic_api_key: str = None):
        """
        Initialize the workflow.

        Args:
            fastmcp_url: URL for FastMCP service
            anthropic_api_key: Anthropic API key for Claude
        """
        self.fastmcp_url = fastmcp_url or os.getenv(
            "FASTMCP_URL", "http://localhost:8000"
        )
        self.fastmcp_client = FastMCPClient(self.fastmcp_url)
        self.claude_node = ClaudeDecisionNode(anthropic_api_key)
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
        return await self.claude_node.decide_market_sentiment(state)

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
