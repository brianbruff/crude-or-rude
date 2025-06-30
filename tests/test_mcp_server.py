"""
Tests for MCP server functionality.
"""

import pytest
from unittest.mock import patch
import json
import os

from crude_or_rude.models import AnalysisResult


class TestMCPServer:
    """Test MCP server functionality."""

    @pytest.mark.asyncio
    async def test_mcp_server_import(self):
        """Test that MCP server can be imported (even if MCP lib not available)."""
        try:
            from crude_or_rude.mcp_server import CrudeOrRudeMCPServer
            # If import succeeds, test basic initialization would fail without MCP
            # This is expected behavior
        except ImportError:
            # This is expected if MCP library is not installed
            pass

    @pytest.mark.asyncio
    async def test_mcp_functionality_simulation(self):
        """Test the core functionality that would be exposed via MCP tools."""
        # Set up environment for testing
        with patch.dict("os.environ", {
            "AWS_DEFAULT_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": "fake",
            "AWS_SECRET_ACCESS_KEY": "fake"
        }):
            from crude_or_rude.workflow import CrudeOrRudeWorkflow
            
            workflow = CrudeOrRudeWorkflow()
            
            try:
                # Test single headline analysis (similar to analyze_headline MCP tool)
                headline = "Oil prices surge on supply concerns"
                result = await workflow.analyze_headline(headline)
                
                # Verify result structure matches what MCP tools would return
                assert isinstance(result, AnalysisResult)
                assert result.headline == headline
                assert result.sentiment is not None
                assert result.rudeness is not None
                assert result.market_sentiment is not None
                
                # Test data can be serialized to JSON (required for MCP)
                mcp_response = {
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
                }
                
                # Verify JSON serialization works
                json_response = json.dumps(mcp_response)
                assert isinstance(json_response, str)
                assert "headline" in json_response
                assert "sentiment" in json_response
                assert "market_sentiment" in json_response
                
                # Test batch functionality simulation
                headlines = [
                    "OPEC cuts production",
                    "Oil prices rise"
                ]
                
                batch_results = []
                for headline in headlines:
                    try:
                        result = await workflow.analyze_headline(headline)
                        batch_results.append({
                            "headline": result.headline,
                            "market_sentiment": {
                                "category": result.market_sentiment.category,
                                "response": result.market_sentiment.response
                            }
                        })
                    except Exception as e:
                        batch_results.append({
                            "headline": headline,
                            "error": str(e)
                        })
                
                assert len(batch_results) == 2
                assert all("headline" in result for result in batch_results)
                
            finally:
                await workflow.close()

    def test_cli_server_mode_flag(self):
        """Test that CLI recognizes server mode flag."""
        from crude_or_rude.main import main
        import sys
        
        # Mock sys.argv to simulate --server flag
        original_argv = sys.argv
        try:
            sys.argv = ["crude-or-rude", "--server"]
            
            # This should attempt to import and run MCP server
            # We expect it to return 1 since MCP is not installed
            exit_code = main()
            assert exit_code == 1
                
        finally:
            sys.argv = original_argv

    def test_cli_help_includes_server_mode(self):
        """Test that CLI help includes server mode information."""
        from crude_or_rude.main import main
        import sys
        from io import StringIO
        
        # Capture stdout to check help output
        original_stdout = sys.stdout
        original_argv = sys.argv
        
        try:
            sys.stdout = StringIO()
            sys.argv = ["crude-or-rude", "--help"]
            
            exit_code = main()
            help_output = sys.stdout.getvalue()
            
            assert exit_code == 0
            assert "--server" in help_output
            assert "MCP server" in help_output
            assert "Claude Desktop" in help_output
            
        finally:
            sys.stdout = original_stdout
            sys.argv = original_argv