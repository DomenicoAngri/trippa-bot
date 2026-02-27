"""
Booking Strategies
Different approaches for securing a table reservation
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


class BookingStrategy:
    """
    Base class for booking strategies
    
    Defines the interface that all strategies must implement
    """
    
    def __init__(self, api_client, notifier=None):
        """
        Args:
            api_client: ResDiaryClient instance
            notifier: Optional notifier instance (e.g., TelegramNotifier)
        """
        self.api = api_client
        self.notifier = notifier
    
    def execute(self, **kwargs) -> bool:
        """
        Execute the booking strategy
        
        Returns:
            True if booking was successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def _notify(self, method_name: str, *args, **kwargs):
        """Helper to send notifications if notifier is available"""
        if self.notifier and hasattr(self.notifier, method_name):
            method = getattr(self.notifier, method_name)
            method(*args, **kwargs)


class SniperStrategy(BookingStrategy):
    """
    Sniper Strategy - High-speed booking on release day
    
    This strategy synchronizes precisely with the moment bookings open
    (typically 1st of the month at 12pm) and attempts to book
    at maximum speed with multiple rapid-fire attempts.
    """
    
    def execute(
        self,
        release_datetime: datetime,
        target_date: str,
        party_size: int,
        preferred_time: str,
        user_data: Dict,
        max_attempts: int = 50,
        attempt_interval: float = 0.1
    ) -> bool:
        """
        Execute sniper strategy
        
        Args:
            release_datetime: Exact moment bookings open
            target_date: Date to book (YYYY-MM-DD)
            party_size: Number of guests
            preferred_time: Preferred time slot (e.g., "20:00")
            user_data: Dict with guest info (first_name, last_name, email, phone)
            max_attempts: Maximum number of booking attempts
            attempt_interval: Seconds between attempts
        
        Returns:
            True if booking succeeded
        """
        logger.info("🎯 SNIPER MODE ACTIVATED")
        logger.info(f"   Release: {release_datetime}")
        logger.info(f"   Target: {target_date} at {preferred_time}")
        logger.info(f"   Party size: {party_size}")
        
        # Notify user that sniper is starting
        self._notify(
            'send_sniper_starting',
            target_datetime=release_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            target_date=target_date
        )
        
        # Wait until release time
        self._wait_for_release(release_datetime)
        
        logger.info("🔥 FIRE! Starting booking attempts...")
        
        # Rapid-fire booking attempts
        for attempt in range(max_attempts):
            try:
                # 1. Check available slots
                slots = self.api.get_time_slots(target_date, party_size)
                
                if not slots:
                    logger.debug(f"Attempt {attempt + 1}/{max_attempts}: No slots available")
                    time.sleep(attempt_interval)
                    continue
                
                # 2. Find preferred slot or take first available
                target_slot = self._find_best_slot(slots, preferred_time)
                
                if not target_slot:
                    logger.debug(f"Attempt {attempt + 1}/{max_attempts}: No matching slots")
                    time.sleep(attempt_interval)
                    continue
                
                slot_time = target_slot.get('Time', preferred_time)
                logger.info(f"✅ SLOT FOUND: {slot_time} (attempt {attempt + 1})")
                
                # Build direct booking URL
                from ..utils import BookingURLBuilder, BrowserOpener
                
                booking_url = BookingURLBuilder.build_direct_link(
                    date=target_date,
                    time=slot_time,
                    party_size=party_size
                )
                
                logger.info(f"📎 Direct booking URL: {booking_url}")
                
                # Send urgent notification with link
                if self.notifier:
                    self.notifier.send_message(f"""
🔥 <b>SLOT FOUND - SNIPER MODE!</b>

📅 Date: <b>{target_date}</b>
🕐 Time: <b>{slot_time}</b>
👥 Party: <b>{party_size}</b>

⚡ <b>BOOK NOW:</b>
<a href="{booking_url}">🚀 CLICK HERE TO BOOK</a>

⏱️ <b>URGENT!</b> Complete booking in next 30 seconds!
""")
                
                # Auto-open browser (optional - can be enabled in config)
                # BrowserOpener.open_booking_page(booking_url, auto_open=True)
                
                # Phase 2: Auto-booking (not implemented yet)
                logger.warning("⚠️ Auto-booking not implemented - complete manually via link")
                
                # Placeholder for Phase 2
                # result = self.api.book_table(
                #     date=target_date,
                #     time=slot_time,
                #     covers=party_size,
                #     **user_data
                # )
                
                # For now, consider it a success if we found and notified
                return True
            
            except Exception as e:
                logger.error(f"Error in attempt {attempt + 1}: {e}")
            
            time.sleep(attempt_interval)
        
        # All attempts exhausted
        logger.error(f"😞 Failed to book after {max_attempts} attempts")
        self._notify(
            'send_booking_failed',
            reason=f"No slots found after {max_attempts} attempts"
        )
        
        return False
    
    def _wait_for_release(self, release_datetime: datetime):
        """Wait with precise synchronization until release time"""
        now = datetime.now()
        wait_seconds = (release_datetime - now).total_seconds()
        
        if wait_seconds <= 0:
            logger.warning("Release time already passed!")
            return
        
        logger.info(f"⏳ Waiting {wait_seconds:.1f} seconds until release...")
        
        # Coarse wait (if more than 5 seconds away)
        if wait_seconds > 5:
            time.sleep(wait_seconds - 5)
        
        # Fine-grained synchronization (last 5 seconds)
        while datetime.now() < release_datetime:
            time.sleep(0.001)  # 1ms precision
        
        logger.info("⏰ Release time reached!")
    
    def _find_best_slot(self, slots: List[Dict], preferred_time: str) -> Optional[Dict]:
        """
        Find the best available slot
        
        Args:
            slots: List of available time slots
            preferred_time: Preferred time
        
        Returns:
            Best matching slot or first available
        """
        # Try to find exact match for preferred time
        for slot in slots:
            if slot.get('Time') == preferred_time:
                return slot
        
        # Return first available if preferred not found
        if slots:
            logger.warning(
                f"Preferred time {preferred_time} not found, "
                f"using {slots[0].get('Time')}"
            )
            return slots[0]
        
        return None


class MonitorStrategy(BookingStrategy):
    """
    Monitor Strategy - Continuous availability monitoring
    
    Periodically checks for cancellations and newly available slots.
    Particularly effective:
    - 24 hours before reservation (when confirmation required)
    - During the day (random cancellations)
    """
    
    def execute(
        self,
        target_dates: List[str],
        party_size: int,
        preferred_times: List[str],
        check_interval: int = 1800,
        auto_book: bool = False,
        user_data: Optional[Dict] = None,
        stop_callback: Optional[Callable] = None
    ) -> bool:
        """
        Execute monitoring strategy
        
        Args:
            target_dates: List of dates to monitor
            party_size: Number of guests
            preferred_times: List of preferred times (in order of preference)
            check_interval: Seconds between checks (default: 30 min)
            auto_book: If True, automatically book when slot found
            user_data: Guest info (required if auto_book=True)
            stop_callback: Optional callback that returns True to stop monitoring
        
        Returns:
            True if a booking was made (only relevant if auto_book=True)
        """
        logger.info("🔍 MONITOR MODE ACTIVATED")
        logger.info(f"   Monitoring dates: {target_dates}")
        logger.info(f"   Party size: {party_size}")
        logger.info(f"   Preferred times: {preferred_times}")
        logger.info(f"   Check interval: {check_interval}s ({check_interval/60:.0f} min)")
        logger.info(f"   Auto-book: {auto_book}")
        
        attempt = 0
        
        while True:
            attempt += 1
            
            # Check if we should stop
            if stop_callback and stop_callback():
                logger.info("Stop callback triggered, ending monitoring")
                break
            
            logger.info(f"--- Check #{attempt} ---")
            
            # Check each target date
            for target_date in target_dates:
                found_slots = self._check_date(
                    target_date,
                    party_size,
                    preferred_times,
                    auto_book,
                    user_data
                )
                
                # If auto-booking succeeded, we're done
                if auto_book and found_slots:
                    return True
            
            # Wait before next check
            logger.info(f"Next check in {check_interval}s...")
            time.sleep(check_interval)
        
        return False
    
    def _check_date(
        self,
        date: str,
        party_size: int,
        preferred_times: List[str],
        auto_book: bool,
        user_data: Optional[Dict]
    ) -> bool:
        """
        Check a specific date for availability
        
        Returns:
            True if booking was made (only when auto_book=True)
        """
        try:
            slots = self.api.get_time_slots(date, party_size)
            
            if not slots:
                logger.debug(f"{date}: No slots available")
                return False
            
            logger.info(f"🎉 {date}: Found {len(slots)} available slots!")
            
            # Extract time slots
            time_slots = [s.get('Time', 'N/A') for s in slots]
            
            # Filter by preferred times if specified
            matching_slots = []
            if preferred_times:
                for pref_time in preferred_times:
                    for slot in slots:
                        if slot.get('Time') == pref_time:
                            matching_slots.append(slot)
                            break  # Take first match for this preferred time
                
                if matching_slots:
                    slots = matching_slots
                    time_slots = [s.get('Time') for s in matching_slots]
                    logger.info(f"   Filtered to {len(matching_slots)} preferred slots")
            
            # Build direct booking URL for the best slot
            from ..utils import BookingURLBuilder, BrowserOpener
            
            best_slot = slots[0]
            best_time = best_slot.get('Time', time_slots[0])
            
            booking_url = BookingURLBuilder.build_direct_link(
                date=date,
                time=best_time,
                party_size=party_size
            )
            
            logger.info(f"📎 Direct booking URL: {booking_url}")
            
            # Send notification with clickable link
            self._notify(
                'send_availability_alert',
                date=date,
                time_slots=time_slots,
                party_size=party_size,
                booking_url=booking_url
            )
            
            # Optional: Auto-open browser
            # BrowserOpener.open_booking_page(booking_url, auto_open=True)
            
            # Auto-book if enabled (Phase 2 - not implemented yet)
            if auto_book and user_data:
                logger.warning("⚠️ Auto-booking not yet implemented (Phase 2)")
                # return self._attempt_booking(date, best_slot, party_size, user_data)
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking {date}: {e}")
            return False
    
    def _attempt_booking(
        self,
        date: str,
        slot: Dict,
        party_size: int,
        user_data: Dict
    ) -> bool:
        """
        Attempt to book a specific slot
        
        Returns:
            True if booking succeeded
        """
        time_str = slot.get('Time', '00:00')
        
        logger.info(f"🎯 Auto-booking: {date} {time_str}")
        
        try:
            result = self.api.book_table(
                date=date,
                time=time_str,
                covers=party_size,
                **user_data
            )
            
            if result.get('success'):
                logger.info("✅ Auto-booking successful!")
                
                self._notify(
                    'send_booking_success',
                    date=date,
                    time=time_str,
                    party_size=party_size,
                    confirmation_code=result.get('confirmation_code')
                )
                
                return True
            else:
                logger.warning(f"Auto-booking failed: {result.get('message')}")
                
                self._notify(
                    'send_booking_failed',
                    reason=result.get('message', 'Unknown error')
                )
        
        except Exception as e:
            logger.error(f"Booking error: {e}")
            self._notify('send_error', error_message=str(e))
        
        return False
