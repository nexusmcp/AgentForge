from typing import Optional, Dict, Any
from decimal import Decimal
import json

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_typing import Address
from loguru import logger

# Standard Uniswap V2 Router ABI for price queries
UNISWAP_V2_ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# ERC20 ABI for basic token interactions
ERC20_ABI = [
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class BlockchainClient:
    """Utility class for blockchain interactions."""
    
    # Common token addresses
    WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    
    # DEX router addresses
    UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    
    def __init__(self, rpc_url: str, chain_id: int = 1):
        """Initialize the blockchain client.
        
        Args:
            rpc_url: The RPC endpoint URL
            chain_id: The chain ID (default: 1 for Ethereum mainnet)
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.chain_id = chain_id
        
        # Initialize common contracts
        self.uniswap_router = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.UNISWAP_V2_ROUTER),
            abi=UNISWAP_V2_ROUTER_ABI
        )
    
    def get_token_price_usd(self, token_address: str) -> Decimal:
        """Get the USD price of a token using Uniswap V2.
        
        Args:
            token_address: The token contract address
            
        Returns:
            Decimal: The token price in USD
        """
        token_address = self.w3.to_checksum_address(token_address)
        
        # Use WETH as intermediate if token is not WETH
        if token_address.lower() != self.WETH.lower():
            path = [token_address, self.WETH, self.USDC]
        else:
            path = [self.WETH, self.USDC]
        
        try:
            # Get decimals for the input token
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=ERC20_ABI
            )
            decimals = token_contract.functions.decimals().call()
            
            # Calculate price through Uniswap
            amount_in = 10 ** decimals  # Use 1 token as input
            amounts = self.uniswap_router.functions.getAmountsOut(
                amount_in,
                path
            ).call()
            
            # Convert to USD price (USDC has 6 decimals)
            price = Decimal(amounts[-1]) / Decimal(10 ** 6)
            if len(path) == 3:  # If going through WETH
                price = price / (Decimal(amounts[1]) / Decimal(10 ** 18))
                
            return price
            
        except Exception as e:
            logger.error(f"Error getting price for {token_address}: {e}")
            raise
    
    def get_contract(self, address: str, abi: list) -> Any:
        """Get a contract instance.
        
        Args:
            address: The contract address
            abi: The contract ABI
            
        Returns:
            Contract: A Web3.py contract instance
        """
        return self.w3.eth.contract(
            address=self.w3.to_checksum_address(address),
            abi=abi
        ) 