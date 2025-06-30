"""
Main entry point for the Crude or Rude application.
"""

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


def main():
    """Main CLI entry point."""
    # Load environment variables
    load_dotenv()

    # Check for server mode
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        # Run MCP server mode
        print("🛢️ Starting Crude or Rude MCP Server...")
        try:
            from crude_or_rude.mcp_server import run_mcp_server
            return asyncio.run(run_mcp_server())
        except ImportError as e:
            print(f"❌ MCP server not available: {e}")
            print("💡 Install MCP dependencies: pip install mcp")
            return 1
    elif len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        # Show help
        print("🛢️ Crude or Rude? Market Sentiment Analyzer")
        print()
        print("Usage:")
        print("  crude-or-rude                    # Run sample analysis (CLI mode)")
        print("  crude-or-rude <headline>         # Analyze custom headline (CLI mode)")
        print("  crude-or-rude --server          # Run as MCP server for Claude Desktop")
        print("  crude-or-rude --help            # Show this help")
        print()
        print("Examples:")
        print('  crude-or-rude "Oil prices surge amid supply concerns"')
        print("  crude-or-rude --server")
        return 0
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        # Analyze custom headline from command line
        headline = " ".join(sys.argv[1:])
        return asyncio.run(analyze_custom_headline(headline))
    else:
        # Run sample analysis
        return asyncio.run(analyze_sample_headlines())


if __name__ == "__main__":
    sys.exit(main())
