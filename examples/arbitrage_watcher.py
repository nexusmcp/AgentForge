from decimal import Decimal
import time

from agentforge.core import Agent
from agentforge.tasks.arbitrage import ArbitrageTask


def main():
    # Create an arbitrage monitoring agent
    arb_agent = Agent("ARBITRAGE_WATCHER")
    
    # List of popular tokens to monitor
    tokens = [
        # WETH
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        # USDT
        "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        # LINK
        "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        # UNI
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
    ]
    
    # Create arbitrage tasks for each token
    for token in tokens:
        task = ArbitrageTask(
            token_address=token,
            min_profit_threshold=Decimal("0.5"),  # 0.5% minimum profit
            base_amount=Decimal("1.0")  # Simulate with 1 token
        )
        arb_agent.assign_task(task)
    
    # Start the agent
    arb_agent.start()
    
    try:
        print("Arbitrage watcher is running. Press Ctrl+C to stop...")
        print(f"Monitoring {len(tokens)} tokens for arbitrage opportunities...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        arb_agent.stop()
        print("\nAgent stopped.")


if __name__ == "__main__":
    main() 