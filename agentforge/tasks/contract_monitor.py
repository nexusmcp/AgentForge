from typing import List, Dict, Any, Optional, Set
from decimal import Decimal

from web3 import Web3
from web3.contract import Contract
from eth_typing import Address
from loguru import logger

from .base import Task
from ..utils.blockchain import BlockchainClient

# Common event signatures to monitor
TRANSFER_EVENT = "Transfer(address,address,uint256)"
APPROVAL_EVENT = "Approval(address,address,uint256)"
SWAP_EVENT = "Swap(address,uint256,uint256,uint256,uint256,address)"

class ContractMonitorTask(Task):
    """Task for monitoring smart contract events and state changes."""
    
    name: str = "contract_monitor"
    contract_address: str
    events_to_monitor: List[str]  # List of event signatures to monitor
    rpc_url: str = "https://eth.llamarpc.com"
    chain_id: int = 1
    blocks_to_scan: int = 100  # How many recent blocks to scan
    
    def __init__(self, **data):
        super().__init__(**data)
        self.blockchain = BlockchainClient(self.rpc_url, self.chain_id)
        self.last_processed_block = 0
        self.processed_txs: Set[str] = set()
        
        # Get contract ABI - for this example, we'll use ERC20 events
        self.monitored_events = {
            TRANSFER_EVENT,
            APPROVAL_EVENT,
            SWAP_EVENT
        }.intersection(set(self.events_to_monitor))
    
    def execute(self) -> None:
        """Monitor contract events and state changes."""
        try:
            # Get current block
            current_block = self.blockchain.w3.eth.block_number
            
            # If this is the first run, start from current block
            if self.last_processed_block == 0:
                self.last_processed_block = current_block - 1
            
            # Calculate block range to scan
            start_block = max(
                self.last_processed_block + 1,
                current_block - self.blocks_to_scan
            )
            
            if start_block >= current_block:
                return  # No new blocks to process
            
            logger.info(
                f"Scanning blocks {start_block} to {current_block} "
                f"for contract {self.contract_address}"
            )
            
            # Get contract events
            self._process_events(start_block, current_block)
            
            # Update last processed block
            self.last_processed_block = current_block
            
        except Exception as e:
            logger.error(f"Error monitoring contract {self.contract_address}: {e}")
    
    def _process_events(self, start_block: int, end_block: int) -> None:
        """Process contract events in the given block range."""
        # Get event logs
        try:
            # Create event filter
            event_filter = self.blockchain.w3.eth.filter({
                'fromBlock': start_block,
                'toBlock': end_block,
                'address': Web3.to_checksum_address(self.contract_address)
            })
            
            # Get all matching events
            events = event_filter.get_all_entries()
            
            for event in events:
                tx_hash = event['transactionHash'].hex()
                
                # Skip if we've already processed this transaction
                if tx_hash in self.processed_txs:
                    continue
                
                # Get transaction receipt for more details
                receipt = self.blockchain.w3.eth.get_transaction_receipt(tx_hash)
                
                # Process the event
                self._handle_event(event, receipt)
                
                # Mark transaction as processed
                self.processed_txs.add(tx_hash)
                
                # Keep processed tx set from growing too large
                if len(self.processed_txs) > 1000:
                    self.processed_txs = set(list(self.processed_txs)[-1000:])
                
        except Exception as e:
            logger.error(f"Error processing events: {e}")
    
    def _handle_event(self, event: Dict[str, Any], receipt: Dict[str, Any]) -> None:
        """Handle a specific contract event."""
        try:
            # Get basic event info
            tx_hash = event['transactionHash'].hex()
            block_number = event['blockNumber']
            
            # Log the event
            logger.info(
                f"Contract Event Detected:\n"
                f"Block: {block_number}\n"
                f"Transaction: {tx_hash}\n"
                f"Gas Used: {receipt['gasUsed']}\n"
                f"Status: {'Success' if receipt['status'] == 1 else 'Failed'}"
            )
            
            # TODO: Add specific handling for different event types
            # For now, we just log them
            
        except Exception as e:
            logger.error(f"Error handling event: {e}") 