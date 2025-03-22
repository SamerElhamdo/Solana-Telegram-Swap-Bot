import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from tokenInfo import TokenInfo

logger = logging.getLogger(__name__)

class PriceAlert:
    def __init__(self):
        self.alerts = {}  # user_id -> list of alerts
        self.last_checked_prices = {}  # token_address -> price
        
    async def add_price_alert(self, user_id: int, token_address: str, target_price: float, 
                              is_above: bool, name: Optional[str] = None) -> bool:
        """
        Add a price alert for a user
        :param user_id: Telegram user ID
        :param token_address: Token contract address
        :param target_price: Target price to trigger alert
        :param is_above: If True, alert when price goes above target, else when below
        :param name: Optional name for the alert
        :return: Success status
        """
        try:
            # Get current token info to validate the token address
            token_info = await TokenInfo.get_token_info(token_address)
            if not token_info:
                logger.error(f"Invalid token address for price alert: {token_address}")
                return False
                
            # Create alert structure
            alert = {
                "token_address": token_address,
                "token_symbol": token_info.get("symbol", "Unknown"),
                "target_price": target_price,
                "is_above": is_above,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "name": name or token_info.get("symbol", "Alert"),
                "triggered": False,
                "current_price": token_info.get("price_in_usd", 0)
            }
            
            # Add to user's alerts
            if user_id not in self.alerts:
                self.alerts[user_id] = []
                
            self.alerts[user_id].append(alert)
            self.last_checked_prices[token_address] = token_info.get("price_in_usd", 0)
            
            logger.info(f"Added price alert for user {user_id}: {alert['name']} at ${target_price}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding price alert: {e}", exc_info=True)
            return False
    
    async def remove_price_alert(self, user_id: int, alert_index: int) -> bool:
        """
        Remove a price alert for a user by its index
        :param user_id: Telegram user ID
        :param alert_index: Index of the alert to remove
        :return: Success status
        """
        try:
            if user_id not in self.alerts or alert_index >= len(self.alerts[user_id]):
                return False
                
            removed = self.alerts[user_id].pop(alert_index)
            logger.info(f"Removed price alert for user {user_id}: {removed['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing price alert: {e}", exc_info=True)
            return False
    
    async def get_user_alerts(self, user_id: int) -> List[Dict]:
        """
        Get all alerts for a user
        :param user_id: Telegram user ID
        :return: List of alert dictionaries
        """
        return self.alerts.get(user_id, [])
    
    async def check_alerts(self) -> List[Tuple[int, Dict]]:
        """
        Check all alerts against current prices
        :return: List of (user_id, alert) tuples that have been triggered
        """
        triggered_alerts = []
        
        try:
            # Group alerts by token address to minimize API calls
            tokens_to_check = set()
            for user_alerts in self.alerts.values():
                for alert in user_alerts:
                    if not alert["triggered"]:
                        tokens_to_check.add(alert["token_address"])
            
            # Get current prices for all tokens to check
            token_prices = {}
            for token_address in tokens_to_check:
                token_info = await TokenInfo.get_token_info(token_address)
                if token_info:
                    price = token_info.get("price_in_usd", 0)
                    token_prices[token_address] = price
                    self.last_checked_prices[token_address] = price
            
            # Check all alerts
            for user_id, user_alerts in self.alerts.items():
                for i, alert in enumerate(user_alerts):
                    if alert["triggered"]:
                        continue
                        
                    token_address = alert["token_address"]
                    if token_address not in token_prices:
                        continue
                        
                    current_price = token_prices[token_address]
                    target_price = alert["target_price"]
                    is_above = alert["is_above"]
                    
                    # Update current price in alert
                    self.alerts[user_id][i]["current_price"] = current_price
                    
                    # Check if alert should trigger
                    if (is_above and current_price >= target_price) or (not is_above and current_price <= target_price):
                        self.alerts[user_id][i]["triggered"] = True
                        triggered_alerts.append((user_id, self.alerts[user_id][i]))
                        logger.info(f"Price alert triggered for user {user_id}: {alert['name']} at ${current_price}")
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking price alerts: {e}", exc_info=True)
            return []
    
    def reset_triggered_alert(self, user_id: int, alert_index: int) -> bool:
        """
        Reset a triggered alert so it can trigger again
        :param user_id: Telegram user ID
        :param alert_index: Index of the alert to reset
        :return: Success status
        """
        try:
            if user_id not in self.alerts or alert_index >= len(self.alerts[user_id]):
                return False
                
            self.alerts[user_id][alert_index]["triggered"] = False
            return True
            
        except Exception as e:
            logger.error(f"Error resetting triggered alert: {e}", exc_info=True)
            return False
    
    def save_alerts_to_file(self, filename: str = "price_alerts.json") -> bool:
        """
        Save all alerts to a JSON file
        :param filename: Path to the JSON file
        :return: Success status
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.alerts, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving alerts to file: {e}", exc_info=True)
            return False
    
    def load_alerts_from_file(self, filename: str = "price_alerts.json") -> bool:
        """
        Load alerts from a JSON file
        :param filename: Path to the JSON file
        :return: Success status
        """
        try:
            with open(filename, 'r') as f:
                self.alerts = json.load(f)
            return True
        except FileNotFoundError:
            logger.warning(f"Alerts file not found: {filename}")
            return False
        except Exception as e:
            logger.error(f"Error loading alerts from file: {e}", exc_info=True)
            return False

# Create global instance
price_alert_manager = PriceAlert() 