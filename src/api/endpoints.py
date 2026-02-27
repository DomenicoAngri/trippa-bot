"""
API Endpoints Configuration
Centralized definition of all ResDiary API endpoints
"""

# Base configuration
BASE_URL = "https://booking.resdiary.com/api/Restaurant/TRATTORIATRIPPA"
CHANNEL_CODE = "INGLESE"

# API Endpoints
ENDPOINTS = {
    # Get restaurant configuration and settings
    "setup": {
        "path": "/Setup",
        "method": "GET",
        "description": "Fetch restaurant configuration (hours, limits, rules)"
    },
    
    # Check availability for a date range
    "availability_range": {
        "path": "/AvailabilityForDateRange",
        "method": "POST",
        "description": "Get available dates within a date range"
    },
    
    # Get specific time slots for a date
    "availability_search": {
        "path": "/AvailabilitySearch",
        "method": "GET",
        "description": "Get available time slots for a specific date"
    },
    
    # Create a booking (ENDPOINT TO BE VERIFIED)
    "booking": {
        "path": "/Booking",  # May need to be updated after discovery
        "method": "POST",
        "description": "Create a new reservation",
        "verified": False  # Flag to indicate this endpoint needs verification
    },
    
    # Alternative booking endpoints to test
    "booking_alternatives": [
        "/CreateBooking",
        "/Reserve",
        "/MakeReservation",
        "/Book",
        "/CreateReservation"
    ]
}

# Request headers template
DEFAULT_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,it;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://www.trippamilano.it',
    'referer': 'https://www.trippamilano.it/book-a-table-2/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

# Area IDs (from API discovery)
AREAS = {
    "bancone": 263372,
    "tavolo": 263371,
    "any": 0  # 0 means any area
}

# Service configuration (from API response)
SERVICE = {
    "name": "Cena",
    "time_from": "19:15:00",
    "last_booking_time": "22:00:00",
    "time_slot_interval": 15  # minutes
}

# Booking constraints (from API response)
CONSTRAINTS = {
    "max_party_size": 6,
    "min_party_size": 1,
    "default_party_size": 6,
    "accept_bookings_days_in_advance": 62
}
