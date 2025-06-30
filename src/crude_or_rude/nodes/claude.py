"""
Claude node for composite sentiment decision making via AWS Bedrock.
"""

import os
from typing import Any, Dict

from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from crude_or_rude.models import MarketSentiment, WorkflowState
from pydantic import BaseModel


class ClaudeDecisionNode:
    """Claude-powered node for making composite sentiment decisions via AWS Bedrock."""

    def __init__(self, region_name: str | None = None):
        """
        Initialize Claude client via AWS Bedrock using existing AWS CLI configuration.

        Args:
            region_name: AWS region name, defaults to environment variable or CLI default
        """
        # Use the region from environment or AWS CLI default
        region = region_name or os.getenv("AWS_DEFAULT_REGION")
        
        # ChatBedrock will automatically use your AWS CLI configuration
        self.llm = ChatBedrock(
            model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Claude 3.7 Sonnet cross-region inference profile
            region_name=region,  # Will use CLI default if None
            model_kwargs={
                "temperature": 0.7,
                "max_tokens": 4000,
            }
        )
        # Instead of PydanticOutputParser, bind the schema directly
        self.llm_with_structured_output = self.llm.with_structured_output(MarketSentiment)

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
        """

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ]

            response = await self.llm_with_structured_output.ainvoke(messages)
            
            return {"market_sentiment": response}

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
