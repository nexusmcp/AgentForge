from typing import Optional, Literal
from decimal import Decimal

from web3 import Web3
from loguru import logger

from .base import Task
from ..utils.blockchain import BlockchainClient


class PriceTrackingTask(Task):
    """Task for tracking token prices and generating alerts based on thresholds."""
    
    name: str = "price_tracking"
    token_address: str
    threshold_price: Decimal
    alert_on: Literal["above", "below"] = "above"
    chain_id: int = 1  # Default to Ethereum mainnet
    rpc_url: str = "https://eth.llamarpc.com"  # Default RPC URL
    
    def __init__(self, **data):
        super().__init__(**data)
        self.blockchain = BlockchainClient(self.rpc_url, self.chain_id)
        self.last_price: Optional[Decimal] = None
    
    def execute(self) -> None:
        """Check the current price against the threshold and generate alerts."""
        try:
            current_price = self._get_token_price()
            
            # Log price change if significant
            if self.last_price is not None:
                pct_change = abs(current_price - self.last_price) / self.last_price * 100
                if pct_change > 1.0:  # Log if price changed by more than 1%
                    logger.info(
                        f"Price Change: {self.token_address} "
                        f"from {self.last_price:.2f} to {current_price:.2f} "
                        f"({pct_change:+.2f}%)"
                    )
            
            self.last_price = current_price
            
            alert_condition = (
                current_price > self.threshold_price
                if self.alert_on == "above"
                else current_price < self.threshold_price
            )
            
            if alert_condition:
                logger.warning(
                    f"Price Alert: {self.token_address} is {self.alert_on} "
                    f"threshold {self.threshold_price} (Current: {current_price})"
                )
                
        except Exception as e:
            logger.error(f"Error tracking price for {self.token_address}: {e}")
    
    def _get_token_price(self) -> Decimal:
        """Get the current price of the token using blockchain data."""
        return self.blockchain.get_token_price_usd(self.token_address) 