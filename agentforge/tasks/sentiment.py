from typing import Optional, Dict, Any
from decimal import Decimal

from loguru import logger

from .base import Task
from ..utils.twitter import TwitterClient


class SentimentAnalysisTask(Task):
    """Task for monitoring social media sentiment around crypto tokens."""
    
    name: str = "sentiment_analysis"
    token_symbol: str  # Token symbol (e.g., "ETH")
    timeframe_hours: int = 24  # How many hours of data to analyze
    sentiment_threshold: float = 0.5  # Threshold for sentiment alerts
    twitter_bearer_token: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        self.twitter = TwitterClient(self.twitter_bearer_token)
        self.last_sentiment: Optional[float] = None
    
    def execute(self) -> None:
        """Analyze current sentiment and generate alerts on significant changes."""
        try:
            # Get current sentiment metrics
            metrics = self.twitter.get_crypto_sentiment(
                symbol=self.token_symbol,
                timeframe_hours=self.timeframe_hours
            )
            
            current_sentiment = metrics["sentiment_score"]
            
            # Log basic metrics
            logger.info(
                f"Sentiment Analysis for {self.token_symbol}:\n"
                f"Tweet Count: {metrics['tweet_count']}\n"
                f"Total Engagement: {metrics['total_likes'] + metrics['total_retweets']}\n"
                f"Sentiment Score: {current_sentiment:.2f}"
            )
            
            # Check for significant sentiment changes
            if self.last_sentiment is not None:
                sentiment_change = current_sentiment - self.last_sentiment
                
                if abs(sentiment_change) >= self.sentiment_threshold:
                    direction = "positive" if sentiment_change > 0 else "negative"
                    logger.warning(
                        f"Significant {direction} sentiment shift for {self.token_symbol}!\n"
                        f"Change: {sentiment_change:+.2f}\n"
                        f"Previous Score: {self.last_sentiment:.2f}\n"
                        f"Current Score: {current_sentiment:.2f}"
                    )
            
            self.last_sentiment = current_sentiment
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {self.token_symbol}: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the current sentiment metrics.
        
        Returns:
            Dict containing the latest sentiment metrics
        """
        return self.twitter.get_crypto_sentiment(
            symbol=self.token_symbol,
            timeframe_hours=self.timeframe_hours
        ) 
