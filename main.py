#!/usr/bin/env python3
"""
Trippa Milano Booking Bot - Main Entry Point

Automated booking system for securing tables at Trattoria Trippa
when reservations are sold out in seconds.

Usage:
    python main.py              # Run with scheduler (continuous)
    python main.py --test       # Run connection tests only
    python main.py --check      # Run single availability check
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api import ResDiaryClient
from src.bot import BookingBot, BotScheduler
from src.notifiers import TelegramNotifier
from src.utils import setup_logger
from config import get_config, validate_config


def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║         🍝  TRIPPA MILANO BOOKING BOT  🍝                ║
    ║                                                          ║
    ║     Automated reservation system for Trippa Milano      ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_tests(bot):
    """
    Run connection and API tests
    
    Args:
        bot: BookingBot instance
    """
    print("\n" + "=" * 60)
    print("🧪 RUNNING TESTS")
    print("=" * 60)
    
    success = bot.test_connection()
    
    if success:
        print("\n✅ All tests passed!")
        print("You're ready to run the bot.")
        return 0
    else:
        print("\n❌ Some tests failed")
        print("Please check the configuration and try again.")
        return 1


def run_quick_check(bot, config):
    """
    Run a single availability check
    
    Args:
        bot: BookingBot instance
        config: Configuration dictionary
    """
    print("\n" + "=" * 60)
    print("🔎 QUICK AVAILABILITY CHECK")
    print("=" * 60)
    
    prefs = config['booking_preferences']
    
    results = bot.quick_check(
        target_dates=prefs['target_dates'],
        party_size=prefs['party_size'],
        notify=True
    )
    
    print("\n📊 Results:")
    print("-" * 60)
    
    total_slots = 0
    for date, slots in results.items():
        if slots:
            print(f"✓ {date}: {len(slots)} slots available")
            for slot in slots:
                print(f"    • {slot}")
            total_slots += len(slots)
        else:
            print(f"✗ {date}: No availability")
    
    print("-" * 60)
    print(f"Total: {total_slots} slots found across {len(results)} dates")
    
    return 0


def run_scheduler(bot, config):
    """
    Run the bot with scheduler (continuous operation)
    
    Args:
        bot: BookingBot instance
        config: Configuration dictionary
    """
    print("\n" + "=" * 60)
    print("⚙️  INITIALIZING SCHEDULER")
    print("=" * 60)
    
    # Create and configure scheduler
    scheduler = BotScheduler(bot, config)
    scheduler.setup_from_config()
    
    # Run forever
    scheduler.run_forever(initial_check=True)
    
    return 0


def main():
    """Main application entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Trippa Milano Booking Bot"
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run connection tests and exit'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Run single availability check and exit'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Load configuration
    print("📋 Loading configuration...")
    config = get_config()
    
    # Validate configuration
    warnings = validate_config()
    if warnings:
        print("\n⚠️  Configuration warnings:")
        for warning in warnings:
            print(f"  {warning}")
        print()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else config['logging']['level']
    logger = setup_logger(
        level=log_level,
        log_file=config['logging']['file'],
        console=config['logging']['console']
    )
    
    logger.info("=" * 60)
    logger.info("Trippa Bot starting...")
    logger.info("=" * 60)
    
    # Initialize components
    print("🔧 Initializing components...")
    
    # API Client
    api_client = ResDiaryClient()
    
    # Notifier (if enabled)
    notifier = None
    if config['telegram']['enabled']:
        notifier = TelegramNotifier(
            bot_token=config['telegram']['bot_token'],
            chat_id=config['telegram']['chat_id'],
            enabled=True
        )
        logger.info("✓ Telegram notifier enabled")
    else:
        logger.info("✗ Telegram notifier disabled")
    
    # Bot
    bot = BookingBot(api_client, notifier)
    
    print("✅ Initialization complete\n")
    
    # Run appropriate mode
    try:
        if args.test:
            return run_tests(bot)
        elif args.check:
            return run_quick_check(bot, config)
        else:
            return run_scheduler(bot, config)
    
    except KeyboardInterrupt:
        logger.info("\n⏹️  Bot stopped by user")
        return 0
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        if notifier:
            notifier.send_error(f"Bot crashed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
