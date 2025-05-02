import time
from agentforge.core import Agent
from agentforge.tasks.contract_monitor import (
    ContractMonitorTask,
    TRANSFER_EVENT,
    APPROVAL_EVENT,
    SWAP_EVENT
)


def main():
    # Create a contract monitoring agent
    contract_agent = Agent("CONTRACT_MONITOR")
    
    # List of important contracts to monitor
    contracts = [
        # WETH
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        # Uniswap V2 Router
        "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        # Sushiswap Router
        "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    ]
    
    # Events to monitor for each contract
    events = [TRANSFER_EVENT, APPROVAL_EVENT, SWAP_EVENT]
    
    # Create monitoring tasks for each contract
    for contract in contracts:
        task = ContractMonitorTask(
            contract_address=contract,
            events_to_monitor=events,
            blocks_to_scan=100  # Scan last 100 blocks
        )
        contract_agent.assign_task(task)
    
    # Start the agent
    contract_agent.start()
    
    try:
        print("Contract monitor is running. Press Ctrl+C to stop...")
        print(f"Monitoring {len(contracts)} contracts for events...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        contract_agent.stop()
        print("\nAgent stopped.")


if __name__ == "__main__":
    main() 