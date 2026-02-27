"""
Base Notifier Interface
Defines the contract that all notifiers must implement
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class BaseNotifier(ABC):
    """
    Abstract base class for all notifiers
    
    Subclasses must implement all abstract methods to ensure
    consistent interface across different notification channels
    """
    
    @abstractmethod
    def send_message(self, text: str) -> bool:
        """
        Send a generic message
        
        Args:
            text: Message text
        
        Returns:
            True if sent successfully
        """
        pass
    
    @abstractmethod
    def send_availability_alert(
        self,
        date: str,
        time_slots: List[str],
        party_size: int
    ) -> bool:
        """
        Send alert when availability is found
        
        Args:
            date: Available date
            time_slots: List of available time slots
            party_size: Number of guests
        
        Returns:
            True if sent successfully
        """
        pass
    
    @abstractmethod
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
            confirmation_code: Booking confirmation code
        
        Returns:
            True if sent successfully
        """
        pass
    
    @abstractmethod
    def send_booking_failed(self, reason: str) -> bool:
        """
        Send notification of failed booking
        
        Args:
            reason: Failure reason
        
        Returns:
            True if sent successfully
        """
        pass
    
    @abstractmethod
    def send_error(self, error_message: str) -> bool:
        """
        Send error notification
        
        Args:
            error_message: Error description
        
        Returns:
            True if sent successfully
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the notification connection
        
        Returns:
            True if connection is working
        """
        pass
