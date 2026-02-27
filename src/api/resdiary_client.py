"""
ResDiary API Client
Handles all HTTP communication with the ResDiary booking system
"""

import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .endpoints import (
    BASE_URL, 
    CHANNEL_CODE, 
    ENDPOINTS, 
    DEFAULT_HEADERS,
    AREAS
)

logger = logging.getLogger(__name__)


class ResDiaryClient:
    """
    Client for ResDiary API (Trippa's booking system)
    
    This client handles all communication with the ResDiary platform,
    including checking availability and creating bookings.
    """
    
    def __init__(self):
        """Initialize the API client with session and headers"""
        self.base_url = BASE_URL
        self.channel_code = CHANNEL_CODE
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.setup_data = None
    
    def get_setup(self, date: Optional[str] = None) -> Dict:
        """
        Fetch restaurant configuration
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            Dictionary containing restaurant setup data:
            - Hours and service times
            - Party size limits
            - Booking rules
            - Available areas
        
        Raises:
            requests.RequestException: If API call fails
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        endpoint = ENDPOINTS["setup"]
        url = f"{self.base_url}{endpoint['path']}"
        
        params = {
            'date': date,
            'channelCode': self.channel_code
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            self.setup_data = response.json()
            logger.info(f"Setup fetched successfully for date {date}")
            logger.debug(f"Setup data: {self.setup_data}")
            
            return self.setup_data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch setup: {e}")
            raise
    
    def check_availability_range(
        self, 
        date_from: str, 
        date_to: str, 
        party_size: int = 2,
        area_id: Optional[int] = None,
        promotion_id: Optional[str] = None
    ) -> List[str]:
        """
        Check availability across a date range
        
        Args:
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            party_size: Number of guests
            area_id: Specific area ID (None = any area)
            promotion_id: Optional promotion ID
        
        Returns:
            List of available dates as strings
        
        Example:
            >>> client.check_availability_range("2026-04-01", "2026-04-30", 2)
            ["2026-04-15", "2026-04-22"]
        """
        endpoint = ENDPOINTS["availability_range"]
        url = f"{self.base_url}{endpoint['path']}"
        
        payload = {
            "DateFrom": f"{date_from}T00:00:00",
            "DateTo": f"{date_to}T00:00:00",
            "PartySize": party_size,
            "ChannelCode": self.channel_code,
            "PromotionId": promotion_id,
            "AreaId": area_id,
            "AvailabilityType": "Reservation"
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            available_dates = data.get('AvailableDates', [])
            
            logger.info(
                f"Availability check: {date_from} to {date_to} | "
                f"{len(available_dates)} dates available"
            )
            
            return available_dates
            
        except requests.RequestException as e:
            logger.error(f"Failed to check availability range: {e}")
            return []
    
    def get_time_slots(
        self,
        date: str,
        covers: int = 2,
        area_id: int = 0,
        promotion_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get available time slots for a specific date
        
        Args:
            date: Date in YYYY-MM-DD format
            covers: Number of guests
            area_id: Area ID (0 = any area, see AREAS constant)
            promotion_id: Optional promotion ID
        
        Returns:
            List of time slot dictionaries containing:
            - Time: Time slot (e.g., "20:00")
            - Additional slot information
        
        Example:
            >>> client.get_time_slots("2026-04-15", covers=2)
            [
                {"Time": "20:00", ...},
                {"Time": "20:15", ...}
            ]
        """
        endpoint = ENDPOINTS["availability_search"]
        url = f"{self.base_url}{endpoint['path']}"
        
        params = {
            'date': date,
            'covers': covers,
            'channelCode': self.channel_code,
            'areaId': area_id,
            'availabilityType': 'Reservation'
        }
        
        if promotion_id:
            params['promotionId'] = promotion_id
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            time_slots = data.get('TimeSlots', [])
            
            logger.info(f"Time slots for {date}: {len(time_slots)} available")
            logger.debug(f"Slots: {time_slots}")
            
            return time_slots
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch time slots: {e}")
            return []
    
    def book_table(
        self,
        date: str,
        time: str,
        covers: int,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        area_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Create a table reservation
        
        WARNING: This endpoint has not been fully verified yet.
        The exact payload structure needs to be confirmed by capturing
        an actual booking request from the browser.
        
        Args:
            date: Reservation date in YYYY-MM-DD format
            time: Reservation time (e.g., "20:00")
            covers: Number of guests
            first_name: Guest first name
            last_name: Guest last name
            email: Guest email
            phone: Guest phone (international format recommended)
            area_id: Preferred area ID (optional)
            notes: Special requests (optional)
        
        Returns:
            Dictionary with booking result:
            - success: Boolean indicating if booking was successful
            - confirmation_code: Booking confirmation code (if successful)
            - message: Result message or error description
        
        Raises:
            NotImplementedError: Until endpoint is verified
        
        TODO:
            - Verify exact endpoint path
            - Confirm required payload fields
            - Test with actual booking
        """
        # IMPORTANT: This endpoint needs verification!
        # Once we capture the actual booking request, update this method
        
        endpoint = ENDPOINTS["booking"]
        
        if not endpoint.get('verified', False):
            logger.warning(
                "⚠️  Booking endpoint NOT yet verified! "
                "This is a placeholder implementation."
            )
        
        url = f"{self.base_url}{endpoint['path']}"
        
        # Expected payload structure (to be confirmed)
        payload = {
            "Date": date,
            "Time": time,
            "Covers": covers,
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
            "Phone": phone,
            "ChannelCode": self.channel_code,
            "AvailabilityType": "Reservation"
        }
        
        # Optional fields
        if area_id is not None:
            payload["AreaId"] = area_id
        
        if notes:
            payload["Notes"] = notes
        
        logger.info(
            f"Attempting booking: {date} {time} for {covers} guests | "
            f"Guest: {first_name} {last_name}"
        )
        
        # UNCOMMENT when endpoint is verified
        # try:
        #     response = self.session.post(url, json=payload)
        #     response.raise_for_status()
        #     
        #     result = response.json()
        #     logger.info(f"Booking successful: {result}")
        #     
        #     return {
        #         'success': True,
        #         'confirmation_code': result.get('ConfirmationCode'),
        #         'message': 'Booking created successfully',
        #         'data': result
        #     }
        # 
        # except requests.RequestException as e:
        #     logger.error(f"Booking failed: {e}")
        #     
        #     return {
        #         'success': False,
        #         'confirmation_code': None,
        #         'message': str(e),
        #         'data': None
        #     }
        
        # Placeholder response until endpoint is verified
        return {
            'success': False,
            'confirmation_code': None,
            'message': 'Booking endpoint not yet implemented - needs verification',
            'data': None
        }
    
    def discover_booking_endpoint(self) -> List[str]:
        """
        Attempt to discover the correct booking endpoint
        
        Tries common endpoint variations to find the working one.
        This is a helper method for development/testing.
        
        Returns:
            List of endpoints that returned non-404 responses
        """
        logger.info("🔍 Discovering booking endpoint...")
        
        working_endpoints = []
        alternatives = ENDPOINTS["booking_alternatives"]
        
        for endpoint_path in alternatives:
            url = f"{self.base_url}{endpoint_path}"
            logger.info(f"Testing: {url}")
            
            try:
                # Try GET first
                response = self.session.get(url)
                if response.status_code != 404:
                    logger.info(f"  ✓ GET {endpoint_path}: {response.status_code}")
                    working_endpoints.append(endpoint_path)
                
                # Try POST with minimal payload
                test_payload = {
                    "Date": "2026-04-01",
                    "Time": "20:00",
                    "Covers": 2,
                    "ChannelCode": self.channel_code
                }
                
                response = self.session.post(url, json=test_payload)
                if response.status_code != 404:
                    logger.info(
                        f"  ✓ POST {endpoint_path}: {response.status_code} | "
                        f"Response: {response.text[:100]}"
                    )
                    if endpoint_path not in working_endpoints:
                        working_endpoints.append(endpoint_path)
            
            except Exception as e:
                logger.debug(f"  ✗ {endpoint_path}: {e}")
        
        logger.info(f"Discovery complete. Found {len(working_endpoints)} potential endpoints")
        return working_endpoints
