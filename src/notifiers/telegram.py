"""
Telegram Notifier
Sends notifications via Telegram Bot API
"""

import requests
import logging
from typing import List, Optional

from .base import BaseNotifier

logger = logging.getLogger(__name__)


class TelegramNotifier(BaseNotifier):
    """
    Telegram notification implementation
    
    Sends formatted messages to a Telegram chat via Bot API
    
    Setup:
        1. Create bot with @BotFather on Telegram
        2. Get bot token from @BotFather
        3. Get your chat_id from @userinfobot
        4. Initialize with token and chat_id
    """
    
    def __init__(self, bot_token: str, chat_id: str, enabled: bool = True):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Your Telegram chat ID from @userinfobot
            enabled: If False, messages are only logged (useful for testing)
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = enabled
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        if not enabled:
            logger.warning("Telegram notifier is DISABLED - messages will only be logged")
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to Telegram
        
        Args:
            text: Message text (supports HTML formatting if parse_mode='HTML')
            parse_mode: 'HTML' or 'Markdown'
        
        Returns:
            True if sent successfully
        
        HTML Formatting:
            <b>bold</b>
            <i>italic</i>
            <code>code</code>
            <a href="URL">link</a>
        """
        if not self.enabled:
            logger.info(f"[TELEGRAM DISABLED] {text}")
            return False
        
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.debug(f"Telegram message sent: {text[:50]}...")
            return True
        
        except requests.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_availability_alert(
        self,
        date: str,
        time_slots: List[str],
        party_size: int,
        booking_url: Optional[str] = None
    ) -> bool:
        """
        Send alert when table availability is found
        
        Args:
            date: Available date (YYYY-MM-DD)
            time_slots: List of available time slots
            party_size: Number of guests
            booking_url: Optional direct booking URL
        
        Returns:
            True if sent successfully
        """
        # Format time slots as list
        slots_text = "\n".join([f"  • {slot}" for slot in time_slots])
        
        # Build booking link
        if booking_url:
            book_link = f'<a href="{booking_url}">🚀 BOOK NOW - CLICK HERE</a>'
        else:
            book_link = "https://www.trippamilano.it/book-a-table-2/"
        
        message = f"""
🎉 <b>AVAILABILITY FOUND!</b>

📅 Date: <b>{date}</b>
👥 Party size: <b>{party_size}</b>

🕐 <b>Available times:</b>
{slots_text}

⚡ <b>ACTION REQUIRED:</b>
{book_link}

⏱️ <b>ACT FAST!</b> Slots fill in seconds!
"""
        
        return self.send_message(message)
    
    def send_booking_success(
        self,
        date: str,
        time: str,
        party_size: int,
        confirmation_code: Optional[str] = None
    ) -> bool:
        """
        Send notification of successful booking
        
        Args:
            date: Booked date
            time: Booked time
            party_size: Number of guests
            confirmation_code: Booking confirmation code (if available)
        
        Returns:
            True if sent successfully
        """
        message = f"""
✅ <b>BOOKING CONFIRMED!</b>

📅 Date: <b>{date}</b>
🕐 Time: <b>{time}</b>
👥 Party size: <b>{party_size}</b>
"""
        
        if confirmation_code:
            message += f"\n🎫 Confirmation: <code>{confirmation_code}</code>"
        
        message += "\n\n🎊 See you at Trippa!"
        
        return self.send_message(message)
    
    def send_booking_failed(self, reason: str) -> bool:
        """
        Send notification of failed booking attempt
        
        Args:
            reason: Failure reason
        
        Returns:
            True if sent successfully
        """
        message = f"""
❌ <b>BOOKING FAILED</b>

😞 {reason}

Try again or book manually:
https://www.trippamilano.it/book-a-table-2/
"""
        
        return self.send_message(message)
    
    def send_sniper_starting(self, target_datetime: str, target_date: str) -> bool:
        """
        Send notification that sniper mode is starting
        
        Args:
            target_datetime: When sniper will activate
            target_date: Date being targeted for booking
        
        Returns:
            True if sent successfully
        """
        message = f"""
🎯 <b>SNIPER MODE ACTIVATED</b>

⏰ Activation: {target_datetime}
📅 Target date: {target_date}

🔥 The bot will start booking attempts automatically!
"""
        
        return self.send_message(message)
    
    def send_error(self, error_message: str) -> bool:
        """
        Send error notification
        
        Args:
            error_message: Error description
        
        Returns:
            True if sent successfully
        """
        message = f"""
⚠️ <b>BOT ERROR</b>

{error_message}

Check the logs for more details.
"""
        
        return self.send_message(message)
    
    def test_connection(self) -> bool:
        """
        Test Telegram connection
        
        Sends a test message to verify bot token and chat_id are correct
        
        Returns:
            True if connection is working
        """
        if not self.enabled:
            logger.warning("Telegram notifier is disabled")
            return False
        
        test_message = "🤖 Trippa Bot connection test - all systems OK!"
        
        result = self.send_message(test_message)
        
        if result:
            logger.info("✅ Telegram connection OK")
        else:
            logger.error("❌ Telegram connection FAILED")
        
        return result


# Standalone testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python telegram.py <bot_token> <chat_id>")
        sys.exit(1)
    
    bot_token = sys.argv[1]
    chat_id = sys.argv[2]
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    notifier = TelegramNotifier(bot_token, chat_id)
    
    print("🧪 Testing Telegram notifier...")
    
    # Test 1: Connection
    print("\n1. Testing connection...")
    notifier.test_connection()
    
    # Test 2: Availability alert
    print("\n2. Testing availability alert...")
    notifier.send_availability_alert(
        date="2026-04-15",
        time_slots=["20:00", "20:15", "21:00"],
        party_size=2
    )
    
    # Test 3: Booking success
    print("\n3. Testing booking success...")
    notifier.send_booking_success(
        date="2026-04-15",
        time="20:30",
        party_size=2,
        confirmation_code="ABC123"
    )
    
    # Test 4: Booking failed
    print("\n4. Testing booking failed...")
    notifier.send_booking_failed(
        reason="No slots available after 50 attempts"
    )
    
    # Test 5: Error
    print("\n5. Testing error notification...")
    notifier.send_error(
        error_message="API connection timeout"
    )
    
    print("\n✅ All tests sent! Check your Telegram.")
