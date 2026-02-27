"""
Bot Configuration Settings

IMPORTANT: Update these values with your personal information!

For sensitive data (bot tokens, emails), consider using environment variables
or a .env file instead of hardcoding them here.
"""

import os
from pathlib import Path

# =============================================================================
# USER DATA - Your personal information for bookings
# =============================================================================

USER_DATA = {
    "first_name": os.getenv("USER_FIRST_NAME", "Mario"),
    "last_name": os.getenv("USER_LAST_NAME", "Rossi"),
    "email": os.getenv("USER_EMAIL", "mario.rossi@example.com"),
    "phone": os.getenv("USER_PHONE", "+393201234567"),
}

# =============================================================================
# BOOKING PREFERENCES - What you want to book
# =============================================================================

BOOKING_PREFERENCES = {
    # Number of guests
    "party_size": int(os.getenv("PARTY_SIZE", "2")),
    
    # Preferred time slots (in order of preference)
    "preferred_times": [
        "20:00",
        "20:15",
        "20:30",
        "21:00"
    ],
    
    # Preferred area (None = any, 263371 = TAVOLO, 263372 = BANCONE)
    "preferred_area": None,
    
    # Target dates you want to book
    "target_dates": [
        "2026-04-15",
        "2026-04-22",
        "2026-04-29"
    ]
}

# =============================================================================
# RELEASE DAY CONFIGURATION - For the 1st of month booking rush
# =============================================================================

RELEASE_CONFIG = {
    # Enable/disable sniper mode
    "enabled": os.getenv("RELEASE_ENABLED", "true").lower() == "true",
    
    # Day of month when bookings open (typically 1)
    "day_of_month": int(os.getenv("RELEASE_DAY_OF_MONTH", "1")),
    
    # Time when bookings open
    "hour": int(os.getenv("RELEASE_HOUR", "0")),      # 0 = midnight
    "minute": int(os.getenv("RELEASE_MINUTE", "0")),
    
    # How many months ahead to book (1 = next month, 2 = month after next)
    "month_to_book": int(os.getenv("RELEASE_MONTH_TO_BOOK", "1")),
    
    # Auto-book when slot found (True) or just notify (False)
    "auto_book": os.getenv("RELEASE_AUTO_BOOK", "false").lower() == "true",
}

# =============================================================================
# MONITOR CONFIGURATION - Continuous availability checking
# =============================================================================

MONITOR_CONFIG = {
    # Enable/disable monitoring
    "enabled": os.getenv("MONITOR_ENABLED", "true").lower() == "true",
    
    # Check interval in seconds (1800 = 30 minutes)
    "check_interval": int(os.getenv("MONITOR_CHECK_INTERVAL", "1800")),
    
    # Intensify checks in last 24 hours before reservation
    # (when confirmation is required and many cancel)
    "intensify_24h_before": True,
    "intensified_interval": 300,  # 5 minutes
    
    # Auto-book when slot found (True) or just notify (False)
    "auto_book": os.getenv("MONITOR_AUTO_BOOK", "false").lower() == "true",
    
    # Auto-open browser when slot found (macOS/Linux/Windows)
    "auto_open_browser": os.getenv("AUTO_OPEN_BROWSER", "false").lower() == "true",
}

# =============================================================================
# TELEGRAM CONFIGURATION - Notification settings
# =============================================================================

TELEGRAM_CONFIG = {
    # Enable/disable Telegram notifications
    "enabled": os.getenv("TELEGRAM_ENABLED", "true").lower() == "true",
    
    # Bot token from @BotFather
    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE"),
    
    # Your chat ID from @userinfobot
    "chat_id": os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE"),
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent

LOGGING_CONFIG = {
    # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    "level": os.getenv("LOG_LEVEL", "INFO"),
    
    # Log file path
    "file": str(PROJECT_ROOT / "logs" / "trippa_bot.log"),
    
    # Also log to console
    "console": True,
}

# =============================================================================
# HELPER FUNCTION - Get full configuration as dict
# =============================================================================

def get_config() -> dict:
    """
    Get complete configuration as a dictionary
    
    Returns:
        Dictionary containing all configuration sections
    
    Example:
        >>> config = get_config()
        >>> print(config['user_data']['email'])
    """
    return {
        "user_data": USER_DATA,
        "booking_preferences": BOOKING_PREFERENCES,
        "release": RELEASE_CONFIG,
        "monitor": MONITOR_CONFIG,
        "telegram": TELEGRAM_CONFIG,
        "logging": LOGGING_CONFIG,
    }


# =============================================================================
# VALIDATION - Warn if using default values
# =============================================================================

def validate_config():
    """
    Validate configuration and warn about default values
    """
    warnings = []
    
    # Check user data
    if USER_DATA["email"] == "mario.rossi@example.com":
        warnings.append("⚠️  Using default email - update USER_DATA in config/settings.py")
    
    if USER_DATA["phone"] == "+393201234567":
        warnings.append("⚠️  Using default phone - update USER_DATA in config/settings.py")
    
    # Check Telegram
    if TELEGRAM_CONFIG["enabled"]:
        if TELEGRAM_CONFIG["bot_token"] == "YOUR_BOT_TOKEN_HERE":
            warnings.append("⚠️  Telegram enabled but using default bot_token")
        
        if TELEGRAM_CONFIG["chat_id"] == "YOUR_CHAT_ID_HERE":
            warnings.append("⚠️  Telegram enabled but using default chat_id")
    
    # Check target dates
    if not BOOKING_PREFERENCES["target_dates"]:
        warnings.append("⚠️  No target dates specified in BOOKING_PREFERENCES")
    
    return warnings


# Auto-validate on import (in development)
if __name__ != "__main__":
    _warnings = validate_config()
    if _warnings:
        import logging
        logger = logging.getLogger(__name__)
        for warning in _warnings:
            logger.warning(warning)
