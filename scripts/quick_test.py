#!/usr/bin/env python3
"""
Quick Test Script
Fast way to test API and notifications without running full bot
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
#sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.api import ResDiaryClient
from src.notifiers import TelegramNotifier
from src.utils import setup_logger
from datetime import datetime, timedelta


def test_api():
    """Test ResDiary API"""
    print("\n" + "=" * 60)
    print("🧪 TESTING RESDIARY API")
    print("=" * 60)
    
    api = ResDiaryClient()
    
    # Test 1: Setup
    print("\n1️⃣  Testing Setup endpoint...")
    try:
        setup = api.get_setup()
        print(f"   ✅ Setup OK")
        print(f"   Restaurant: {setup.get('Name')}")
        print(f"   Max party size: {setup.get('MaxOnlinePartySize')}")
        print(f"   Booking days ahead: {setup.get('AcceptBookingsDaysInAdvance')}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    # Test 2: Availability Range
    print("\n2️⃣  Testing Availability Range...")
    try:
        today = datetime.now()
        date_from = today.strftime("%Y-%m-%d")
        date_to = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        
        available = api.check_availability_range(
            date_from=date_from,
            date_to=date_to,
            party_size=2
        )
        
        print(f"   ✅ Range check OK")
        if available:
            print(f"   Found {len(available)} available dates:")
            for date in available[:5]:
                print(f"     • {date}")
        else:
            print(f"   ⚠️  No dates available (normal if sold out)")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    # Test 3: Time Slots
    print("\n3️⃣  Testing Time Slots...")
    try:
        test_date = (today + timedelta(days=15)).strftime("%Y-%m-%d")
        
        slots = api.get_time_slots(test_date, covers=2)
        
        print(f"   ✅ Time slots check OK")
        if slots:
            print(f"   Found {len(slots)} slots for {test_date}:")
            for slot in slots[:5]:
                print(f"     • {slot.get('Time', 'N/A')}")
        else:
            print(f"   ⚠️  No slots available for {test_date}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    print("\n✅ API tests completed successfully!")
    return True


def test_telegram():
    """Test Telegram notifications"""
    print("\n" + "=" * 60)
    print("📱 TESTING TELEGRAM NOTIFICATIONS")
    print("=" * 60)
    
    print("\nTo test Telegram, you need:")
    print("1. Bot Token from @BotFather")
    print("2. Chat ID from @userinfobot\n")
    
    token = input("Bot Token (or 'skip'): ").strip()
    
    if token.lower() == 'skip':
        print("⏭️  Telegram test skipped")
        return True
    
    chat_id = input("Chat ID: ").strip()
    
    notifier = TelegramNotifier(
        bot_token=token,
        chat_id=chat_id,
        enabled=True
    )
    
    print("\n🔌 Testing connection...")
    if not notifier.test_connection():
        print("❌ Connection failed!")
        print("Check your bot token and chat ID")
        return False
    
    print("✅ Connection OK!\n")
    
    # Send test notifications
    print("📬 Sending test notifications...")
    
    notifier.send_availability_alert(
        date="2026-04-15",
        time_slots=["20:00", "20:30"],
        party_size=2
    )
    print("  • Availability alert sent")
    
    notifier.send_booking_success(
        date="2026-04-15",
        time="20:30",
        party_size=2,
        confirmation_code="TEST123"
    )
    print("  • Booking success sent")
    
    print("\n✅ Check your Telegram for messages!")
    return True


def main():
    """Main test runner"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║         🧪  TRIPPA BOT - QUICK TEST  🧪                  ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Setup minimal logging
    setup_logger(level="INFO", console=True)
    
    results = []
    
    # Test API
    results.append(("ResDiary API", test_api()))
    
    # Test Telegram
    results.append(("Telegram", test_telegram()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True

    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Update config/settings.py with your data")
        print("2. Run: python main.py")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Fix the issues and try again")
        return 1


if __name__ == "__main__":
    sys.exit(main())
