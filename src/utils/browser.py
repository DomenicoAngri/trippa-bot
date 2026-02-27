"""
Browser Automation - Opens URLs in default browser
"""

import webbrowser
import logging
import platform

logger = logging.getLogger(__name__)


class BrowserOpener:
    """
    Opens URLs in the system's default browser
    
    Useful for automatically opening the booking page
    when a slot is found
    """
    
    @staticmethod
    def open_url(url: str, new_window: bool = True) -> bool:
        """
        Open URL in default browser
        
        Args:
            url: URL to open
            new_window: If True, open in new window/tab
        
        Returns:
            True if successfully opened
        
        Example:
            >>> BrowserOpener.open_url("https://example.com")
            True
        """
        try:
            if new_window:
                webbrowser.open_new_tab(url)
            else:
                webbrowser.open(url)
            
            logger.info(f"Opened URL in browser: {url[:50]}...")
            return True
        
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            return False
    
    @staticmethod
    def open_booking_page(url: str, auto_open: bool = False) -> bool:
        """
        Open booking page with optional auto-open
        
        Args:
            url: Booking URL
            auto_open: If True, automatically open browser
        
        Returns:
            True if opened (or auto_open is False)
        """
        if not auto_open:
            logger.info(f"Auto-open disabled. URL: {url}")
            return True
        
        logger.info("Auto-opening booking page in browser...")
        return BrowserOpener.open_url(url)
    
    @staticmethod
    def get_browser_info() -> dict:
        """
        Get information about the system and browser
        
        Returns:
            Dictionary with system info
        """
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'default_browser': webbrowser.get().__class__.__name__
        }


# Standalone test
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Opening: {url}")
        BrowserOpener.open_url(url)
    else:
        print("Usage: python browser.py <url>")
        print("\nSystem info:")
        info = BrowserOpener.get_browser_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
