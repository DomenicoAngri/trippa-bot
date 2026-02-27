"""
Bot Scheduler - Automated job scheduling
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


class BotScheduler:
    """
    Scheduler for automated booking tasks
    
    Manages periodic monitoring and scheduled release-day sniping
    """
    
    def __init__(self, bot, config: Dict):
        """
        Initialize scheduler
        
        Args:
            bot: BookingBot instance
            config: Configuration dictionary with scheduler settings
        """
        self.bot = bot
        self.config = config
        self.running = False
        
        logger.info("⚙️  BotScheduler initialized")
    
    def setup_monitor_job(
        self,
        target_dates: List[str],
        party_size: int,
        preferred_times: List[str],
        check_interval: int = 1800,
        auto_book: bool = False,
        user_data: Optional[Dict] = None
    ):
        """
        Setup periodic monitoring job
        
        Args:
            target_dates: Dates to monitor
            party_size: Number of guests
            preferred_times: Preferred time slots
            check_interval: Seconds between checks
            auto_book: Auto-book when slot found
            user_data: Guest info (required if auto_book=True)
        """
        interval_minutes = check_interval // 60
        
        def job():
            """Monitor job wrapper"""
            logger.info("🔍 Running scheduled monitoring check...")
            self.bot.quick_check(
                target_dates=target_dates,
                party_size=party_size,
                notify=True
            )
        
        schedule.every(interval_minutes).minutes.do(job)
        
        logger.info(
            f"✅ Monitor job scheduled: every {interval_minutes} minutes "
            f"for {len(target_dates)} dates"
        )
    
    def setup_sniper_job(
        self,
        day_of_month: int,
        hour: int,
        minute: int,
        target_date_offset_months: int,
        party_size: int,
        preferred_time: str,
        user_data: Dict,
        fallback_date: Optional[str] = None
    ):
        """
        Setup release-day sniper job
        
        Args:
            day_of_month: Day to trigger (e.g., 1 for first of month)
            hour: Hour to trigger (0-23)
            minute: Minute to trigger (0-59)
            target_date_offset_months: Months ahead to book
            party_size: Number of guests
            preferred_time: Preferred time slot
            user_data: Guest information
            fallback_date: Specific date to book (overrides offset calculation)
        """
        def job():
            """Sniper job wrapper"""
            logger.info("🎯 Running scheduled sniper job...")
            
            # Calculate release datetime and target date
            now = datetime.now()
            
            # Next occurrence of day_of_month at hour:minute
            if now.day >= day_of_month and (now.hour > hour or 
                (now.hour == hour and now.minute >= minute)):
                # Already passed this month, use next month
                if now.month == 12:
                    release_month = 1
                    release_year = now.year + 1
                else:
                    release_month = now.month + 1
                    release_year = now.year
            else:
                release_month = now.month
                release_year = now.year
            
            release_datetime = datetime(
                year=release_year,
                month=release_month,
                day=day_of_month,
                hour=hour,
                minute=minute
            )
            
            # Calculate target date
            if fallback_date:
                target_date = fallback_date
            else:
                target_month = release_month + target_date_offset_months
                target_year = release_year
                
                if target_month > 12:
                    target_month -= 12
                    target_year += 1
                
                # Use middle of month as default (15th)
                target_date = f"{target_year:04d}-{target_month:02d}-15"
            
            # Run sniper
            self.bot.run_sniper(
                release_datetime=release_datetime,
                target_date=target_date,
                party_size=party_size,
                preferred_time=preferred_time,
                user_data=user_data
            )
        
        # Schedule for the specific day and time
        schedule_time = f"{hour:02d}:{minute:02d}"
        schedule.every().day.at(schedule_time).do(job)
        
        logger.info(
            f"✅ Sniper job scheduled: Day {day_of_month} at {schedule_time} "
            f"(target: {target_date_offset_months} months ahead)"
        )
    
    def setup_from_config(self):
        """
        Setup all jobs from configuration
        
        Reads from self.config to setup both monitor and sniper jobs
        """
        logger.info("⚙️  Setting up jobs from configuration...")
        
        # Monitor job
        if self.config.get('monitor', {}).get('enabled', False):
            monitor_cfg = self.config['monitor']
            booking_prefs = self.config.get('booking_preferences', {})
            user_data = self.config.get('user_data', {})
            
            self.setup_monitor_job(
                target_dates=booking_prefs.get('target_dates', []),
                party_size=booking_prefs.get('party_size', 2),
                preferred_times=booking_prefs.get('preferred_times', []),
                check_interval=monitor_cfg.get('check_interval', 1800),
                auto_book=monitor_cfg.get('auto_book', False),
                user_data=user_data if monitor_cfg.get('auto_book') else None
            )
        
        # Sniper job
        if self.config.get('release', {}).get('enabled', False):
            release_cfg = self.config['release']
            booking_prefs = self.config.get('booking_preferences', {})
            user_data = self.config.get('user_data', {})
            
            # Get first target date if specified
            target_dates = booking_prefs.get('target_dates', [])
            fallback_date = target_dates[0] if target_dates else None
            
            self.setup_sniper_job(
                day_of_month=release_cfg.get('day_of_month', 1),
                hour=release_cfg.get('hour', 0),
                minute=release_cfg.get('minute', 0),
                target_date_offset_months=release_cfg.get('month_to_book', 1),
                party_size=booking_prefs.get('party_size', 2),
                preferred_time=booking_prefs.get('preferred_times', ['20:00'])[0],
                user_data=user_data,
                fallback_date=fallback_date
            )
        
        logger.info("✅ All jobs configured")
    
    def run_once(self):
        """Run all pending jobs once (useful for testing)"""
        logger.info("▶️  Running all pending jobs once...")
        schedule.run_all()
    
    def run_forever(self, initial_check: bool = True):
        """
        Start the scheduler loop
        
        Args:
            initial_check: Run an initial monitoring check before starting loop
        """
        logger.info("=" * 60)
        logger.info("🚀 SCHEDULER STARTED")
        logger.info("=" * 60)
        
        # List all jobs
        logger.info(f"Scheduled jobs: {len(schedule.jobs)}")
        for job in schedule.jobs:
            logger.info(f"  • {job}")
        
        # Initial check if requested
        if initial_check:
            logger.info("\n🧪 Running initial availability check...")
            booking_prefs = self.config.get('booking_preferences', {})
            self.bot.quick_check(
                target_dates=booking_prefs.get('target_dates', []),
                party_size=booking_prefs.get('party_size', 2),
                notify=True
            )
        
        # Main loop
        logger.info("\n♾️  Entering main scheduler loop...")
        logger.info("Press Ctrl+C to stop\n")
        
        self.running = True
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("\n⏹️  Scheduler stopped by user")
            self.running = False
        
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            self.running = False
            raise
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("⏹️  Stopping scheduler...")
        self.running = False
        schedule.clear()
