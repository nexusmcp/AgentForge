from decimal import Decimal
import time

from agentforge.core import Agent
from agentforge.tasks.price_tracking import PriceTrackingTask


def main():
    # Create a price tracking agent for ETH
    eth_agent = Agent("ETH_PRICE_TRACKER")
    
    # Create a task to track ETH price
    eth_task = PriceTrackingTask(
        token_address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH contract
        threshold_price=Decimal("2000.00"),
        alert_on="above"
    )
    
    # Assign the task to the agent
    eth_agent.assign_task(eth_task)
    
    # Start the agent
    eth_agent.start()
    
    try:
        print("Price tracking agent is running. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        eth_agent.stop()
        print("\nAgent stopped.")


if __name__ == "__main__":
    main() 
