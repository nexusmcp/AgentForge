from typing import List, Dict, Any, Optional
import os
import time
from datetime import datetime, timedelta

import requests
from loguru import logger


class TwitterClient:
    """Client for interacting with Twitter/X API v2."""
    
    BASE_URL = "https://api.twitter.com/2"
    
    def __init__(self, bearer_token: Optional[str] = None):
        """Initialize Twitter client.
        
        Args:
            bearer_token: Twitter API bearer token. If None, will try to get from env.
        """
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError(
                "Twitter bearer token not provided. Set TWITTER_BEARER_TOKEN env variable."
            )
    
    def search_recent_tweets(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Search recent tweets matching a query.
        
        Args:
            query: Search query string
            max_results: Maximum number of tweets to return (default: 100)
            start_time: Only return tweets after this time
            
        Returns:
            List of tweet objects
        """
        url = f"{self.BASE_URL}/tweets/search/recent"
        
        params = {
            "query": query,
            "max_results": min(max_results, 100),  # API limit
            "tweet.fields": "created_at,public_metrics,lang"
        }
        
        if start_time:
            params["start_time"] = start_time.isoformat() + "Z"
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            return data.get("data", [])
            
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return []
    
    def get_crypto_sentiment(
        self,
        symbol: str,
        timeframe_hours: int = 24
    ) -> Dict[str, Any]:
        """Get sentiment analysis for a crypto token from recent tweets.
        
        Args:
            symbol: Token symbol (e.g., "ETH")
            timeframe_hours: How many hours of tweets to analyze
            
        Returns:
            Dict containing sentiment metrics
        """
        # Create search query
        query = f"#{symbol} OR ${symbol} lang:en -is:retweet"
        start_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
        
        # Get tweets
        tweets = self.search_recent_tweets(
            query=query,
            max_results=100,
            start_time=start_time
        )
        
        if not tweets:
            return {
                "tweet_count": 0,
                "total_likes": 0,
                "total_retweets": 0,
                "avg_engagement": 0,
                "sentiment_score": 0
            }
        
        # Calculate metrics
        total_likes = sum(t["public_metrics"]["like_count"] for t in tweets)
        total_retweets = sum(t["public_metrics"]["retweet_count"] for t in tweets)
        avg_engagement = (total_likes + total_retweets) / len(tweets)
        
        # Simple sentiment scoring based on engagement
        # TODO: Add actual NLP-based sentiment analysis
        sentiment_score = avg_engagement / 100  # Normalize to roughly -1 to 1 range
        
        return {
            "tweet_count": len(tweets),
            "total_likes": total_likes,
            "total_retweets": total_retweets,
            "avg_engagement": avg_engagement,
            "sentiment_score": sentiment_score
        } 
