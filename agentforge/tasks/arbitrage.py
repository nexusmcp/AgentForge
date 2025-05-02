from typing import List, Dict, Optional
from decimal import Decimal
import json

from web3 import Web3
from loguru import logger

from .base import Task
from ..utils.blockchain import BlockchainClient

# Sushiswap Router for price comparison
SUSHISWAP_ROUTER = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"

class ArbitrageTask(Task):
    """Task for monitoring price differences between DEXes for arbitrage opportunities."""
    
    name: str = "arbitrage_monitoring"
    token_address: str
    min_profit_threshold: Decimal  # Minimum profit percentage to trigger alert
    base_amount: Decimal  # Amount to simulate trade with
    rpc_url: str = "https://eth.llamarpc.com"
    chain_id: int = 1
    
    def __init__(self, **data):
        super().__init__(**data)
        self.blockchain = BlockchainClient(self.rpc_url, self.chain_id)
        
        # Initialize Sushiswap router contract
        self.sushiswap_router = self.blockchain.get_contract(
            SUSHISWAP_ROUTER,
            self.blockchain.UNISWAP_V2_ROUTER_ABI  # Same ABI as Uniswap V2
        )
    
    def execute(self) -> None:
        """Check for arbitrage opportunities between Uniswap and Sushiswap."""
        try:
            # Get prices from both DEXes
            uni_price = self._get_uniswap_price()
            sushi_price = self._get_sushiswap_price()
            
            # Calculate price difference percentage
            price_diff = abs(uni_price - sushi_price)
            avg_price = (uni_price + sushi_price) / 2
            diff_percentage = (price_diff / avg_price) * 100
            
            logger.info(
                f"Price Comparison for {self.token_address}:\n"
                f"Uniswap: ${uni_price:.2f}\n"
                f"Sushiswap: ${sushi_price:.2f}\n"
                f"Difference: {diff_percentage:.2f}%"
            )
            
            # Check if difference exceeds threshold
            if diff_percentage >= self.min_profit_threshold:
                buy_dex = "Sushiswap" if sushi_price < uni_price else "Uniswap"
                sell_dex = "Uniswap" if buy_dex == "Sushiswap" else "Sushiswap"
                
                logger.warning(
                    f"Arbitrage Opportunity Found!\n"
                    f"Token: {self.token_address}\n"
                    f"Strategy: Buy on {buy_dex}, Sell on {sell_dex}\n"
                    f"Potential Profit: {diff_percentage:.2f}%"
                )
                
        except Exception as e:
            logger.error(f"Error checking arbitrage for {self.token_address}: {e}")
    
    def _get_uniswap_price(self) -> Decimal:
        """Get token price from Uniswap."""
        return self.blockchain.get_token_price_usd(self.token_address)
    
    def _get_sushiswap_price(self) -> Decimal:
        """Get token price from Sushiswap using the same method as Uniswap."""
        token_address = self.blockchain.w3.to_checksum_address(self.token_address)
        
        # Use WETH as intermediate if token is not WETH
        if token_address.lower() != self.blockchain.WETH.lower():
            path = [token_address, self.blockchain.WETH, self.blockchain.USDC]
        else:
            path = [self.blockchain.WETH, self.blockchain.USDC]
        
        try:
            # Get decimals for the input token
            token_contract = self.blockchain.get_contract(token_address, self.blockchain.ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            
            # Calculate price through Sushiswap
            amount_in = 10 ** decimals
            amounts = self.sushiswap_router.functions.getAmountsOut(
                amount_in,
                path
            ).call()
            
            # Convert to USD price
            price = Decimal(amounts[-1]) / Decimal(10 ** 6)
            if len(path) == 3:
                price = price / (Decimal(amounts[1]) / Decimal(10 ** 18))
                
            return price
            
        except Exception as e:
            logger.error(f"Error getting Sushiswap price for {token_address}: {e}")
            raise 