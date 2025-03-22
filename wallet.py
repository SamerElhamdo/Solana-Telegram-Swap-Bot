import json
import base58
import base64
import logging
from datetime import datetime
from solders import message
from solders.keypair import Keypair # type: ignore
from solders.transaction import VersionedTransaction # type: ignore
from solders.signature import Signature # type: ignore
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed, Finalized
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey # type: ignore
from spl.token.instructions import get_associated_token_address
from solders.pubkey import Pubkey # type: ignore

# Setup logging configuration
logger = logging.getLogger(__name__)

class Wallet():
    
    def __init__(self, rpc_url: str, private_key: str):
        self.wallet = Keypair.from_bytes(base58.b58decode(private_key))
        self.client = AsyncClient(endpoint=rpc_url,commitment=Finalized)
        self.balance_history = {}


    async def get_token_balance(self, token_mint_account: str) -> dict:
        """Get the wallet token balance"""
        if token_mint_account == self.wallet.pubkey().__str__(): #If it is SoL
            get_token_balance = await self.client.get_balance(pubkey=self.wallet.pubkey())
            token_balance = {
                'decimals': 9,
                'balance': {
                    'int': get_token_balance.value,
                    'float': float(get_token_balance.value / 10 ** 9)
                }
            }
        else: #If it is a token
            token_mint_account = get_associated_token_address(owner=self.wallet.pubkey(), mint=Pubkey.from_string(token_mint_account))
            get_token_balance = await self.client.get_token_account_balance(pubkey=token_mint_account)
            try:
                token_balance = {
                    'decimals': int(get_token_balance.value.decimals),
                    'balance': {
                        'int': get_token_balance.value.amount,
                        'float': float(get_token_balance.value.amount) / 10 ** int(get_token_balance.value.decimals)
                    }
                }
            except AttributeError: #If the token account does not exist
                token_balance = {
                    'decimals': 0,
                    'balance': {
                        'int': 0,
                        'float':0
                    }
                }
        
        return token_balance
    
    
    async def sign_send_transaction(self, transaction_data: str, signatures_list: list=None, print_link: bool=True):
        try:
            """Sign and send transaction, return transaction hash"""
            signatures = []
            raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
            signature = self.wallet.sign_message(message.to_bytes_versioned(raw_transaction.message))
            signatures.append(signature)
            if signatures_list:
                for signature in signatures_list:
                    signatures.append(signature)
            signed_txn = VersionedTransaction.populate(raw_transaction.message, signatures)
            opts = TxOpts(skip_preflight=True, preflight_commitment=Processed)
            result = await self.client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
            transaction_hash = json.loads(result.to_json())['result']
            if print_link is True:
                print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_hash}")
            return transaction_hash
        except Exception as e:
            print(e)
            return False

    async def get_status_transaction(self, transaction_hash: str):
        """Get the transaction status"""
        try:
            get_transaction_details = await self.client.confirm_transaction(
                tx_sig=Signature.from_string(transaction_hash),
                sleep_seconds=3,
                last_valid_block_height=json.loads((await self.client.get_latest_blockhash()).to_json())["result"]["value"]["lastValidBlockHeight"],
                commitment=Processed
            )
            transaction_status = get_transaction_details.value[0].err
            
            if transaction_status is None:
                print("Transaction Status SUCCESS!")
                return (True,transaction_status)
            else:
                print(f"!!! Check Transaction Status FAILED!")
                return (False,transaction_status)
        except Exception as e:
            print(e)
            print("Check Transaction Status FAILED!")
            return (False,str(e))

    async def track_balance_changes(self, token_mint_account: str = None):
        """
        Track changes in wallet balance for SOL or a specific token
        Returns a tuple (current_balance, change_percentage, is_increase) if there was a previous balance
        Returns just the current balance if this is the first check
        """
        try:
            if token_mint_account is None or token_mint_account == self.wallet.pubkey().__str__():
                # Track SOL balance
                token_key = "SOL"
                balance_data = await self.get_token_balance(self.wallet.pubkey().__str__())
            else:
                # Track token balance
                token_key = token_mint_account
                balance_data = await self.get_token_balance(token_mint_account)
            
            current_balance = balance_data['balance']['float']
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Store the current balance with timestamp
            if token_key not in self.balance_history:
                self.balance_history[token_key] = []
            
            self.balance_history[token_key].append({
                "timestamp": current_time,
                "balance": current_balance
            })
            
            # Keep only last 20 records to avoid memory bloat
            if len(self.balance_history[token_key]) > 20:
                self.balance_history[token_key].pop(0)
            
            # Calculate change if we have previous data
            if len(self.balance_history[token_key]) > 1:
                previous_balance = self.balance_history[token_key][-2]["balance"]
                if previous_balance > 0:
                    change_percentage = ((current_balance - previous_balance) / previous_balance) * 100
                    is_increase = current_balance > previous_balance
                    return (current_balance, change_percentage, is_increase)
            
            return (current_balance, 0, False)
        
        except Exception as e:
            logger.error(f"Error tracking balance: {e}", exc_info=True)
            return (0, 0, False)