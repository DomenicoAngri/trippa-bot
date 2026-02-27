"""
Booking Bot - Main orchestration logic
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from .strategies import SniperStrategy, MonitorStrategy

logger = logging.getLogger(__name__)


class BookingBot:
    """
    Main booking bot orchestrator
    
    Coordinates between API client, strategies, and notifiers
    to automate the booking process.
    """
    
    def __init__(self, api_client, notifier=None):
        """
        Initialize the booking bot
        
        Args:
            api_client: ResDiaryClient instance
            notifier: Optional notifier instance for alerts
        """
        self.api = api_client
        self.notifier = notifier
        
        # Initialize strategies
        self.sniper = SniperStrategy(api_client, notifier)
        self.monitor = MonitorStrategy(api_client, notifier)
        
        logger.info("🤖 BookingBot initialized")
    
    def run_sniper(
        self,
        release_datetime: datetime,
        target_date: str,
        party_size: int,
        preferred_time: str,
        user_data: Dict,
        **kwargs
    ) -> bool:
        """
        Run sniper strategy for release day
        
        Args:
            release_datetime: When bookings open
            target_date: Date to book
            party_size: Number of guests
            preferred_time: Preferred time slot
            user_data: Guest information
            **kwargs: Additional strategy parameters
        
        Returns:
            True if booking succeeded
        """
        logger.info("🎯 Starting sniper strategy...")
        
        return self.sniper.execute(
            release_datetime=release_datetime,
            target_date=target_date,
            party_size=party_size,
            preferred_time=preferred_time,
            user_data=user_data,
            **kwargs
        )
    
    def run_monitor(
        self,
        target_dates: List[str],
        party_size: int,
        preferred_times: List[str],
        auto_book: bool = False,
        user_data: Optional[Dict] = None,
        **kwargs
    ) -> bool:
        """
        Run monitor strategy for continuous checking
        
        Args:
            target_dates: List of dates to monitor
            party_size: Number of guests
            preferred_times: List of preferred times
            auto_book: Whether to auto-book when slot found
            user_data: Guest information (required if auto_book=True)
            **kwargs: Additional strategy parameters
        
        Returns:
            True if booking was made (only relevant if auto_book=True)
        """
        logger.info("🔍 Starting monitor strategy...")
        
        if auto_book and not user_data:
            logger.error("auto_book=True requires user_data!")
            return False
        
        return self.monitor.execute(
            target_dates=target_dates,
            party_size=party_size,
            preferred_times=preferred_times,
            auto_book=auto_book,
            user_data=user_data,
            **kwargs
        )
    
    def quick_check(
        self,
        target_dates: List[str],
        party_size: int,
        notify: bool = True
    ) -> Dict[str, List[str]]:
        """
        Quick availability check across multiple dates
        
        Args:
            target_dates: Dates to check
            party_size: Number of guests
            notify: Whether to send notification if slots found
        
        Returns:
            Dictionary mapping dates to available time slots
            Example: {"2026-04-15": ["20:00", "20:30"], "2026-04-22": []}
        """
        logger.info(f"🔎 Quick check for {len(target_dates)} dates...")
        
        results = {}
        
        for date in target_dates:
            try:
                slots = self.api.get_time_slots(date, party_size)
                time_slots = [s.get('Time', 'N/A') for s in slots]
                results[date] = time_slots
                
                if time_slots:
                    logger.info(f"✓ {date}: {len(time_slots)} slots")
                    
                    if notify and self.notifier:
                        self.notifier.send_availability_alert(
                            date=date,
                            time_slots=time_slots,
                            party_size=party_size
                        )
                else:
                    logger.info(f"✗ {date}: No slots")
            
            except Exception as e:
                logger.error(f"Error checking {date}: {e}")
                results[date] = []
        
        return results
    
    def test_connection(self) -> bool:
        """
        Test API and notification connections
        
        Returns:
            True if all connections working
        """
        logger.info("🧪 Testing connections...")
        
        # Test API
        try:
            self.api.get_setup()
            logger.info("✅ API connection OK")
            api_ok = True
        except Exception as e:
            logger.error(f"❌ API connection failed: {e}")
            api_ok = False
        
        # Test notifier
        notifier_ok = True
        if self.notifier:
            try:
                notifier_ok = self.notifier.test_connection()
            except Exception as e:
                logger.error(f"❌ Notifier test failed: {e}")
                notifier_ok = False
        
        return api_ok and notifier_ok
