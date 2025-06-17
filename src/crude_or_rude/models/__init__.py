"""
Pydantic models for the Crude or Rude application.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class HeadlineInput(BaseModel):
    """Input model for news headlines."""

    headline: str = Field(..., description="The news headline to analyze")
    source: Optional[str] = Field(None, description="The news source")


class SentimentAnalysis(BaseModel):
    """Sentiment analysis result."""

    sentiment_score: float = Field(
        ..., description="Sentiment score between -1.0 and 1.0"
    )
    sentiment_label: Literal["positive", "negative", "neutral"] = Field(
        ..., description="Categorical sentiment label"
    )
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")


class RudenessAnalysis(BaseModel):
    """Rudeness/aggressiveness analysis result."""

    rudeness_score: float = Field(..., description="Rudeness score between 0.0 and 1.0")
    tone: Literal["professional", "aggressive", "passive-aggressive"] = Field(
        ..., description="Tone classification"
    )
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")


class MarketSentiment(BaseModel):
    """Final market sentiment classification."""

    category: Literal["Professional", "Panic-stricken", "Passive-aggressive"] = Field(
        ..., description="Market sentiment category"
    )
    reasoning: str = Field(
        ..., description="Explanation of the sentiment classification"
    )
    response: str = Field(..., description="Witty response about the market sentiment")


class AnalysisResult(BaseModel):
    """Complete analysis result."""

    headline: str = Field(..., description="The original headline")
    sentiment: SentimentAnalysis = Field(..., description="Sentiment analysis results")
    rudeness: RudenessAnalysis = Field(..., description="Rudeness analysis results")
    market_sentiment: MarketSentiment = Field(..., description="Final market sentiment")


class WorkflowState(BaseModel):
    """State model for the LangGraph workflow."""

    headline: str
    source: Optional[str] = None
    sentiment: Optional[SentimentAnalysis] = None
    rudeness: Optional[RudenessAnalysis] = None
    market_sentiment: Optional[MarketSentiment] = None
    error: Optional[str] = None
