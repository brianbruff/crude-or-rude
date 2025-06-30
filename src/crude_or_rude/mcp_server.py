"""
MCP Server implementation for the Crude or Rude application.

This module provides an MCP (Model Context Protocol) server that exposes
the crude oil sentiment analysis functionality as tools that can be used
by MCP clients like Claude Desktop.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.types import Tool, Resource, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP library not available. Installing dependencies...")

from crude_or_rude.workflow import CrudeOrRudeWorkflow
from crude_or_rude.models import AnalysisResult


class CrudeOrRudeMCPServer:
    """MCP Server for Crude or Rude sentiment analysis."""

    def __init__(self):
        """Initialize the MCP server."""
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP library not available. Please install with: pip install mcp"
            )
        
        self.server = Server("crude-or-rude")
        self.workflow = None
        self._setup_tools()
        self._setup_resources()

    def _setup_tools(self):
        """Setup MCP tools."""
        
        # Tool for analyzing individual headlines
        @self.server.tool("analyze_headline")
        async def analyze_headline(headline: str, source: Optional[str] = None) -> str:
            """
            Analyze a crude oil news headline for market sentiment.
            
            Args:
                headline: The news headline to analyze
                source: Optional source of the news
                
            Returns:
                JSON string with complete analysis including sentiment, tone, and market classification
            """
            if not self.workflow:
                self.workflow = CrudeOrRudeWorkflow()
            
            try:
                result = await self.workflow.analyze_headline(headline, source)
                return json.dumps({
                    "headline": result.headline,
                    "sentiment": {
                        "score": result.sentiment.sentiment_score,
                        "label": result.sentiment.sentiment_label,
                        "confidence": result.sentiment.confidence
                    },
                    "tone": {
                        "rudeness_score": result.rudeness.rudeness_score,
                        "tone": result.rudeness.tone,
                        "confidence": result.rudeness.confidence
                    },
                    "market_sentiment": {
                        "category": result.market_sentiment.category,
                        "reasoning": result.market_sentiment.reasoning,
                        "response": result.market_sentiment.response
                    }
                }, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": f"Analysis failed: {str(e)}",
                    "headline": headline
                }, indent=2)

        # Tool for analyzing multiple headlines
        @self.server.tool("analyze_headlines_batch")
        async def analyze_headlines_batch(headlines: List[str]) -> str:
            """
            Analyze multiple crude oil news headlines for market sentiment.
            
            Args:
                headlines: List of news headlines to analyze
                
            Returns:
                JSON string with analysis results for all headlines
            """
            if not self.workflow:
                self.workflow = CrudeOrRudeWorkflow()
            
            results = []
            for headline in headlines[:5]:  # Limit to 5 headlines to avoid timeout
                try:
                    result = await self.workflow.analyze_headline(headline)
                    results.append({
                        "headline": result.headline,
                        "sentiment": {
                            "score": result.sentiment.sentiment_score,
                            "label": result.sentiment.sentiment_label,
                            "confidence": result.sentiment.confidence
                        },
                        "tone": {
                            "rudeness_score": result.rudeness.rudeness_score,
                            "tone": result.rudeness.tone,
                            "confidence": result.rudeness.confidence
                        },
                        "market_sentiment": {
                            "category": result.market_sentiment.category,
                            "reasoning": result.market_sentiment.reasoning,
                            "response": result.market_sentiment.response
                        }
                    })
                except Exception as e:
                    results.append({
                        "headline": headline,
                        "error": f"Analysis failed: {str(e)}"
                    })
            
            return json.dumps({
                "results": results,
                "total_analyzed": len(results)
            }, indent=2)

        # Tool for getting sample analysis
        @self.server.tool("get_sample_analysis")
        async def get_sample_analysis() -> str:
            """
            Get sample crude oil headline analysis for demonstration.
            
            Returns:
                JSON string with sample headline analysis results
            """
            sample_headlines = [
                "OPEC cuts production again despite global surplus concerns",
                "Oil prices surge as geopolitical tensions escalate in Middle East",
                "Crude futures plummet amid recession fears and demand destruction",
            ]
            
            return await analyze_headlines_batch(sample_headlines)

    def _setup_resources(self):
        """Setup MCP resources."""
        
        # Resource for getting tool descriptions
        @self.server.resource("tools_description")
        async def get_tools_description() -> str:
            """Get description of available tools."""
            return """
            # Crude or Rude Market Sentiment Analyzer Tools

            ## Available Tools:

            ### 1. analyze_headline
            - **Purpose**: Analyze a single crude oil news headline for market sentiment
            - **Input**: headline (required), source (optional)
            - **Output**: Complete analysis with sentiment, tone, and market classification

            ### 2. analyze_headlines_batch
            - **Purpose**: Analyze multiple headlines at once (max 5)
            - **Input**: List of headlines
            - **Output**: Analysis results for all headlines

            ### 3. get_sample_analysis
            - **Purpose**: Get sample analysis for demonstration
            - **Input**: None
            - **Output**: Sample analysis results

            ## Analysis Categories:
            - **Professional**: Normal, measured market reporting
            - **Panic-stricken**: Markets in chaos, fear-driven reactions
            - **Passive-aggressive**: Markets sending mixed signals

            ## Usage Examples:
            - Use `analyze_headline` for single headline analysis
            - Use `analyze_headlines_batch` for comparing multiple headlines
            - Use `get_sample_analysis` to see example outputs
            """

    async def run(self, stdio: bool = True):
        """
        Run the MCP server.
        
        Args:
            stdio: Whether to use stdio transport (default for Claude Desktop)
        """
        if stdio:
            from mcp.server.stdio import stdio_server
            async with stdio_server() as streams:
                await self.server.run(*streams)
        else:
            # For other transports, would need additional setup
            raise NotImplementedError("Only stdio transport is currently supported")

    async def cleanup(self):
        """Clean up resources."""
        if self.workflow:
            await self.workflow.close()


async def run_mcp_server():
    """Main entry point for running the MCP server."""
    server = CrudeOrRudeMCPServer()
    
    try:
        await server.run(stdio=True)
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        return 1
    finally:
        await server.cleanup()
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run_mcp_server()))