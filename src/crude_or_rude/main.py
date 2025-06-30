"""
Main entry point for the Crude or Rude application.
"""

import argparse
import asyncio
import sys

from dotenv import load_dotenv

from crude_or_rude.workflow import CrudeOrRudeWorkflow


async def analyze_sample_headlines():
    """Analyze some sample headlines to demonstrate the system."""

    # Sample crude oil headlines for testing
    sample_headlines = [
        "OPEC cuts production again despite global surplus concerns",
        "Oil prices surge as geopolitical tensions escalate in Middle East",
        "Crude futures plummet amid recession fears and demand destruction",
        "Energy analysts report steady growth in shale oil production",
        "Breaking: Major pipeline explosion sends oil markets into chaos",
    ]

    print("🛢️ Crude or Rude? Market Sentiment Analyzer")
    print("=" * 50)

    # Initialize workflow
    workflow = CrudeOrRudeWorkflow()

    try:
        for i, headline in enumerate(sample_headlines, 1):
            print(f"\n📰 Sample {i}: {headline}")
            print("-" * 50)

            try:
                result = await workflow.analyze_headline(headline)

                print(
                    f"💭 Sentiment: {result.sentiment.sentiment_label} "
                    f"(score: {result.sentiment.sentiment_score:.2f}, "
                    f"confidence: {result.sentiment.confidence:.2f})"
                )

                print(
                    f"🗣️  Tone: {result.rudeness.tone} "
                    f"(rudeness: {result.rudeness.rudeness_score:.2f}, "
                    f"confidence: {result.rudeness.confidence:.2f})"
                )

                print(f"🎯 Market Sentiment: {result.market_sentiment.category}")
                print(f"💡 Reasoning: {result.market_sentiment.reasoning}")
                print(f'🤡 Market Says: "{result.market_sentiment.response}"')

            except Exception as e:
                print(f"❌ Error analyzing headline: {e}")

    finally:
        await workflow.close()


async def analyze_custom_headline(headline: str):
    """Analyze a custom headline provided by the user."""

    print("🛢️ Crude or Rude? Market Sentiment Analyzer")
    print("=" * 50)
    print(f"\n📰 Analyzing: {headline}")
    print("-" * 50)

    workflow = CrudeOrRudeWorkflow()

    try:
        result = await workflow.analyze_headline(headline)

        print(
            f"💭 Sentiment: {result.sentiment.sentiment_label} "
            f"(score: {result.sentiment.sentiment_score:.2f}, "
            f"confidence: {result.sentiment.confidence:.2f})"
        )

        print(
            f"🗣️  Tone: {result.rudeness.tone} "
            f"(rudeness: {result.rudeness.rudeness_score:.2f}, "
            f"confidence: {result.rudeness.confidence:.2f})"
        )

        print(f"🎯 Market Sentiment: {result.market_sentiment.category}")
        print(f"💡 Reasoning: {result.market_sentiment.reasoning}")
        print(f'🤡 Market Says: "{result.market_sentiment.response}"')

    except Exception as e:
        print(f"❌ Error analyzing headline: {e}")
        return 1

    finally:
        await workflow.close()

    return 0


async def run_mcp_server():
    """Run the application in MCP server mode."""
    from crude_or_rude.mcp_server import create_mcp_server
    
    # Create the MCP server
    server = create_mcp_server()
    
    print("🛢️ Crude or Rude MCP Server starting...")
    print("Listening for MCP connections via stdio...")
    
    try:
        # Run the server via stdio (standard communication for MCP servers)
        await server.run_stdio_async()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1
    finally:
        # Clean up resources
        from crude_or_rude.mcp_server import cleanup_workflow
        await cleanup_workflow()
    
    return 0


def main():
    """Main CLI entry point."""
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Crude or Rude: Market Sentiment Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  crude-or-rude                                    # Run sample analysis
  crude-or-rude "Oil prices surge dramatically"   # Analyze custom headline
  crude-or-rude --server                          # Run as MCP server
        """,
    )
    parser.add_argument(
        "--server", 
        action="store_true", 
        help="Run as MCP server for Claude Desktop integration"
    )
    parser.add_argument(
        "headline", 
        nargs="*", 
        help="Custom headline to analyze (if not provided, runs sample analysis)"
    )
    
    args = parser.parse_args()
    
    if args.server:
        # Run in MCP server mode
        return asyncio.run(run_mcp_server())
    elif args.headline:
        # Analyze custom headline from command line
        headline = " ".join(args.headline)
        return asyncio.run(analyze_custom_headline(headline))
    else:
        # Run sample analysis
        return asyncio.run(analyze_sample_headlines())


if __name__ == "__main__":
    sys.exit(main())
