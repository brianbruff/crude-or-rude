"""
Claude node for composite sentiment decision making.
"""

import os
from typing import Any, Dict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from crude_or_rude.models import MarketSentiment, WorkflowState


class ClaudeDecisionNode:
    """Claude-powered node for making composite sentiment decisions."""

    def __init__(self, api_key: str = None):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key, defaults to environment variable
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307", anthropic_api_key=api_key, temperature=0.7
        )
        self.parser = PydanticOutputParser(pydantic_object=MarketSentiment)

    async def decide_market_sentiment(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Use Claude to make a composite sentiment decision based on sentiment and rudeness analysis.

        Args:
            state: The current workflow state with sentiment and rudeness analysis

        Returns:
            Updated state with market sentiment decision
        """
        if not state.sentiment or not state.rudeness:
            return {"error": "Missing sentiment or rudeness analysis"}

        system_prompt = """You are a witty financial market analyst who 
        specializes in crude oil markets. 
        Your job is to analyze news headlines and classify the market 
        sentiment into one of three categories:

        1. "Professional" - Normal, measured market reporting
        2. "Panic-stricken" - Markets are in chaos, fear-driven reactions
        3. "Passive-aggressive" - Markets are being manipulative or 
           sending mixed signals

        Based on the sentiment analysis and tone analysis provided, 
        make your classification and provide:
        1. A brief reasoning for your choice
        2. A witty, entertaining response about what the market is doing 
           (like "This market is gaslighting you")

        Be creative and humorous with your responses while staying 
        professional."""

        human_prompt = f"""
        Analyze this crude oil news headline: "{state.headline}"

        Sentiment Analysis Results:
        - Sentiment Score: {state.sentiment.sentiment_score} 
          (range: -1.0 to 1.0)
        - Sentiment Label: {state.sentiment.sentiment_label}
        - Confidence: {state.sentiment.confidence}

        Rudeness/Tone Analysis Results:
        - Rudeness Score: {state.rudeness.rudeness_score} 
          (range: 0.0 to 1.0)
        - Tone: {state.rudeness.tone}
        - Confidence: {state.rudeness.confidence}

        {self.parser.get_format_instructions()}
        """

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ]

            response = await self.llm.ainvoke(messages)
            market_sentiment = self.parser.parse(response.content)

            return {"market_sentiment": market_sentiment}

        except Exception:
            # Fallback logic if Claude API fails
            return await self._fallback_decision(state)

    async def _fallback_decision(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Fallback decision logic when Claude API is not available.

        Args:
            state: The current workflow state

        Returns:
            Market sentiment decision based on simple rules
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
