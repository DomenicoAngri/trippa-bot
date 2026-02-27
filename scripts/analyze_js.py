#!/usr/bin/env python3
"""
JavaScript Analysis Tool
Analyzes Trippa's website code to discover API endpoints
"""

import sys
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils import setup_logger

logger = setup_logger(level="INFO", console=True)


def analyze_page():
    """Download and analyze the booking page"""
    url = "https://www.trippamilano.it/book-a-table-2/"
    
    print("🔍 Downloading booking page...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to download page: {e}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all external scripts
    scripts = soup.find_all('script', src=True)
    
    print(f"\n📜 Found {len(scripts)} external scripts")
    
    endpoints = set()
    
    for script in scripts:
        script_url = script['src']
        
        # Skip non-relevant scripts
        if not any(x in script_url.lower() for x in ['resdiary', 'booking', 'reservation']):
            continue
        
        # Make URL absolute
        if script_url.startswith('//'):
            script_url = 'https:' + script_url
        elif script_url.startswith('/'):
            script_url = 'https://www.trippamilano.it' + script_url
        
        print(f"\n🔎 Analyzing: {script_url}")
        
        try:
            js_response = requests.get(script_url, timeout=10)
            js_code = js_response.text
            
            # Search for API patterns
            patterns = [
                r'["\']\/api\/[^"\']+["\']',                    # "/api/..."
                r'["\']https?://[^"\']*api[^"\']+["\']',        # "https://...api..."
                r'\.post\(["\']([^"\']+)["\']',                 # .post("url")
                r'\.get\(["\']([^"\']+)["\']',                  # .get("url")
                r'endpoint["\']?\s*[:=]\s*["\']([^"\']+)["\']', # endpoint: "..."
                r'url["\']?\s*[:=]\s*["\']([^"\']+)["\']',      # url: "..."
                r'\/Restaurant\/[^"\']+',                       # /Restaurant/...
                r'\/Booking[^"\']*',                            # /Booking...
                r'\/Reserve[^"\']*',                            # /Reserve...
                r'\/Availability[^"\']*',                       # /Availability...
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, js_code, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match else ''
                    
                    clean = match.strip('\'"')
                    
                    # Filter relevant endpoints
                    if any(kw in clean.lower() for kw in 
                           ['book', 'reserv', 'api', 'slot', 'availability', 'restaurant']):
                        endpoints.add(clean)
                        print(f"  ✓ Found: {clean}")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Analyze inline scripts
    print("\n📝 Checking inline scripts...")
    inline_scripts = soup.find_all('script', src=False)
    
    for script in inline_scripts:
        if script.string and ('resdiary' in script.string.lower() or 
                             'booking' in script.string.lower()):
            print("\n--- Found relevant inline script ---")
            print(script.string[:500])
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📋 DISCOVERED ENDPOINTS")
    print("=" * 60)
    
    if endpoints:
        for endpoint in sorted(endpoints):
            print(f"  • {endpoint}")
    else:
        print("  No endpoints discovered")
    
    print("\n💡 TIP: The booking endpoint is likely one of:")
    print("  • POST /api/Restaurant/TRATTORIATRIPPA/Booking")
    print("  • POST /api/Restaurant/TRATTORIATRIPPA/CreateBooking")
    print("  • POST /api/Restaurant/TRATTORIATRIPPA/Reserve")
    print("\nTo confirm, capture the request when actually booking!")


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║      🔍  JAVASCRIPT ENDPOINT ANALYZER  🔍                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    analyze_page()
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
