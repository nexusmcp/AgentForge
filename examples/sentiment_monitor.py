import time
from agentforge.core import Agent
from agentforge.tasks.sentiment import SentimentAnalysisTask


def main():
    # Create a sentiment monitoring agent
    sentiment_agent = Agent("SENTIMENT_MONITOR")
    
    # List of tokens to monitor sentiment for
    tokens = ["ETH", "BTC", "LINK", "UNI"]
    
    # Create sentiment tasks for each token
    for token in tokens:
        task = SentimentAnalysisTask(
            token_symbol=token,
            timeframe_hours=24,
            sentiment_threshold=0.3  # Alert on 30% sentiment change
        )
        sentiment_agent.assign_task(task)
    
    # Start the agent
    sentiment_agent.start()
    
    try:
        print("Sentiment monitor is running. Press Ctrl+C to stop...")
        print(f"Monitoring sentiment for tokens: {', '.join(tokens)}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sentiment_agent.stop()
        print("\nAgent stopped.")


if __name__ == "__main__":
    main() 