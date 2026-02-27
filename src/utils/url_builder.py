"""
URL Builder - Generates direct booking links
"""

from typing import Optional
from urllib.parse import urlencode


class BookingURLBuilder:
    """
    Builds direct URLs to ResDiary booking pages
    
    This allows users to jump directly to the booking form
    with pre-filled date/time/party size
    """
    
    BASE_URL = "https://www.trippamilano.it/book-a-table-2/"
    WIDGET_URL = "https://booking.resdiary.com/widget/Standard/TRATTORIATRIPPA"
    
    @staticmethod
    def build_direct_link(
        date: str,
        time: str,
        party_size: int,
        area_id: Optional[int] = None
    ) -> str:
        """
        Build direct link to booking page with pre-selected slot
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            party_size: Number of guests
            area_id: Optional area ID
        
        Returns:
            Direct URL to booking page
        
        Example:
            >>> build_direct_link("2026-04-15", "20:30", 2)
            "https://booking.resdiary.com/widget/..."
        """
        # Convert date format: 2026-04-15 -> 15/04/2026
        parts = date.split("-")
        formatted_date = f"{parts[2]}/{parts[1]}/{parts[0]}"
        
        params = {
            'date': formatted_date,
            'time': time,
            'covers': party_size,
            'channelCode': 'INGLESE',
        }
        
        if area_id:
            params['areaId'] = area_id
        
        query_string = urlencode(params)
        return f"{BookingURLBuilder.WIDGET_URL}?{query_string}"
    
    @staticmethod
    def build_trippa_link() -> str:
        """
        Build link to Trippa booking page (general)
        
        Returns:
            URL to Trippa booking page
        """
        return BookingURLBuilder.BASE_URL
    
    @staticmethod
    def build_deep_link(
        date: str,
        time: str, 
        party_size: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> str:
        """
        Build deep link with pre-filled user data (if supported)
        
        Note: ResDiary may not support all these parameters,
        but we try to pre-fill what we can
        
        Args:
            date: Date in YYYY-MM-DD
            time: Time in HH:MM
            party_size: Number of guests
            first_name: Guest first name
            last_name: Guest last name
            email: Guest email
            phone: Guest phone
        
        Returns:
            Deep link URL
        """
        url = BookingURLBuilder.build_direct_link(date, time, party_size)
        
        # Add user data if provided (may or may not work)
        additional_params = {}
        
        if first_name:
            additional_params['firstName'] = first_name
        if last_name:
            additional_params['lastName'] = last_name
        if email:
            additional_params['email'] = email
        if phone:
            additional_params['phone'] = phone
        
        if additional_params:
            query_string = urlencode(additional_params)
            url = f"{url}&{query_string}"
        
        return url
