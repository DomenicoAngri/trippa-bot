"""
Helper Utilities
Common utility functions used throughout the application
"""

import re
from datetime import datetime
from typing import Optional


def validate_date(date_str: str) -> bool:
    """
    Validate date string format (YYYY-MM-DD)
    
    Args:
        date_str: Date string to validate
    
    Returns:
        True if valid date format
    
    Example:
        >>> validate_date("2026-04-15")
        True
        >>> validate_date("04/15/2026")
        False
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_time(time_str: str) -> bool:
    """
    Validate time string format (HH:MM)
    
    Args:
        time_str: Time string to validate
    
    Returns:
        True if valid time format
    
    Example:
        >>> validate_time("20:30")
        True
        >>> validate_time("8:30pm")
        False
    """
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


def format_phone(phone: str, country_code: str = "+39") -> str:
    """
    Format phone number to international format
    
    Args:
        phone: Phone number (with or without country code)
        country_code: Default country code if not present
    
    Returns:
        Formatted phone number with country code
    
    Example:
        >>> format_phone("3201234567")
        "+393201234567"
        >>> format_phone("+393201234567")
        "+393201234567"
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # If already has country code (starts with country_code digits)
    country_digits = re.sub(r'\D', '', country_code)
    if digits.startswith(country_digits):
        return f"+{digits}"
    
    # Add country code
    return f"{country_code}{digits}"


def parse_time_slot(slot: dict) -> Optional[str]:
    """
    Extract time string from time slot dictionary
    
    Args:
        slot: Time slot dictionary from API
    
    Returns:
        Time string (HH:MM) or None if not found
    """
    return slot.get('Time', slot.get('time', None))


def calculate_date_offset(base_date: str, months: int) -> str:
    """
    Calculate date offset by months
    
    Args:
        base_date: Base date in YYYY-MM-DD format
        months: Number of months to offset
    
    Returns:
        New date in YYYY-MM-DD format
    
    Example:
        >>> calculate_date_offset("2026-01-15", 2)
        "2026-03-15"
    """
    base = datetime.strptime(base_date, "%Y-%m-%d")
    
    # Calculate new month and year
    new_month = base.month + months
    new_year = base.year
    
    while new_month > 12:
        new_month -= 12
        new_year += 1
    
    while new_month < 1:
        new_month += 12
        new_year -= 1
    
    # Handle day overflow (e.g., Jan 31 + 1 month = Feb 28/29)
    max_day = 31
    if new_month in [4, 6, 9, 11]:
        max_day = 30
    elif new_month == 2:
        # Leap year check
        is_leap = (new_year % 4 == 0 and new_year % 100 != 0) or (new_year % 400 == 0)
        max_day = 29 if is_leap else 28
    
    new_day = min(base.day, max_day)
    
    return f"{new_year:04d}-{new_month:02d}-{new_day:02d}"


def is_past_date(date_str: str) -> bool:
    """
    Check if date is in the past
    
    Args:
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        True if date is in the past
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.date() < datetime.now().date()


def sanitize_input(text: str, max_length: int = 100) -> str:
    """
    Sanitize user input text
    
    Args:
        text: Input text
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potentially dangerous characters
    # Keep only alphanumeric, spaces, and common punctuation
    text = re.sub(r'[^\w\s\-@.,+()]', '', text)
    
    return text
