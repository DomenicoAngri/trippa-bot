# 🍝 Trippa Milano Booking Bot

Professional automated booking system for securing tables at Trattoria Trippa when reservations sell out in seconds.

## 🎯 Features

### Release Day Sniper
- Synchronizes precisely with booking opening (1st of month)
- 50 attempts in ~5 seconds vs human's 1-2 attempts
- ~100ms API latency vs 3-5 seconds for browser
- Millisecond-precision timing

### Continuous Monitor
- Periodic availability checking for cancellations
- Smart intensification 24h before reservation
- Multi-date tracking
- Configurable check intervals

### Notifications
- Real-time Telegram alerts
- Availability notifications
- Booking confirmations
- Error reports

### Architecture
- Clean, modular codebase
- Separation of concerns (API / Bot / Notifiers)
- Comprehensive logging
- Easily testable components
- Well-documented code

## 📋 Prerequisites

- Python 3.8 or higher
- Stable internet connection
- Telegram account (for notifications)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd trippa-booking-bot

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Telegram Bot

#### Create Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow instructions (choose name and username)
4. **Copy the token** (e.g., `123456789:ABCdefGHI...`)

#### Get Chat ID
1. Search for `@userinfobot`
2. Send `/start`
3. **Copy your ID** (e.g., `987654321`)

### 3. Configuration

Edit `config/settings.py`:

```python
# Your personal information
USER_DATA = {
    "first_name": "Your Name",          # ← UPDATE
    "last_name": "Your Surname",        # ← UPDATE
    "email": "your@email.com",          # ← UPDATE
    "phone": "+393201234567",           # ← UPDATE
}

# Telegram settings
TELEGRAM_CONFIG = {
    "enabled": True,
    "bot_token": "YOUR_BOT_TOKEN",      # ← UPDATE
    "chat_id": "YOUR_CHAT_ID",          # ← UPDATE
}

# Booking preferences
BOOKING_PREFERENCES = {
    "party_size": 2,                    # ← UPDATE
    "preferred_times": [                # ← UPDATE
        "20:00",
        "20:15",
        "20:30"
    ],
    "target_dates": [                   # ← UPDATE
        "2026-04-15",
        "2026-04-22"
    ]
}
```

### 4. Test Setup

```bash
# Quick test
python scripts/quick_test.py

# Or use main.py
python main.py --test
```

### 5. Run the Bot

```bash
# Start with scheduler (continuous operation)
python main.py

# Single availability check
python main.py --check

# Enable debug logging
python main.py --debug
```

## 📁 Project Structure

```
trippa-booking-bot/
├── src/                        # Source code
│   ├── api/                    # ResDiary API client
│   │   ├── resdiary_client.py  # Main API client
│   │   └── endpoints.py        # Endpoint definitions
│   ├── bot/                    # Bot logic
│   │   ├── booking_bot.py      # Main bot orchestrator
│   │   ├── strategies.py       # Sniper & Monitor strategies
│   │   └── scheduler.py        # Job scheduling
│   ├── notifiers/              # Notification systems
│   │   ├── base.py             # Notifier interface
│   │   └── telegram.py         # Telegram implementation
│   └── utils/                  # Utilities
│       ├── logger.py           # Logging setup
│       └── helpers.py          # Helper functions
├── config/                     # Configuration
│   └── settings.py             # Main settings file
├── scripts/                    # Utility scripts
│   ├── quick_test.py           # Quick testing
│   └── analyze_js.py           # Endpoint discovery
├── logs/                       # Log files
├── main.py                     # Application entry point
└── requirements.txt            # Python dependencies
```

## ⚙️ Configuration Options

### Release Day Sniper

```python
RELEASE_CONFIG = {
    "enabled": True,
    "day_of_month": 1,        # When bookings open
    "hour": 0,                # Opening hour (0 = midnight)
    "minute": 0,
    "month_to_book": 1,       # 1 = next month, 2 = month after
    "auto_book": False,       # True = auto-book, False = notify only
}
```

### Continuous Monitor

```python
MONITOR_CONFIG = {
    "enabled": True,
    "check_interval": 1800,   # 30 minutes (in seconds)
    "auto_book": False,       # True = auto-book, False = notify only
}
```

## 🖥️ Running on Mac (Always Active)

### Option 1: Using launchd (Recommended)

Create `~/Library/LaunchAgents/com.trippabot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.trippabot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/FULL/PATH/TO/trippa-booking-bot/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/FULL/PATH/TO/trippa-booking-bot</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/trippabot.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/trippabot.out</string>
</dict>
</plist>
```

Then:

```bash
# Load the service
launchctl load ~/Library/LaunchAgents/com.trippabot.plist

# Check status
launchctl list | grep trippabot

# Stop the service
launchctl unload ~/Library/LaunchAgents/com.trippabot.plist
```

### Option 2: Using screen/tmux

```bash
# Install screen
brew install screen

# Start a session
screen -S trippabot

# Run the bot
python main.py

# Detach: Ctrl+A then D
# Reattach: screen -r trippabot
```

## 🔧 Advanced Usage

### Environment Variables

Instead of editing `config/settings.py`, you can use environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export USER_FIRST_NAME="Mario"
export USER_LAST_NAME="Rossi"
export USER_EMAIL="mario@example.com"
export USER_PHONE="+393201234567"
export PARTY_SIZE="2"

python main.py
```

### Using .env File

Create a `.env` file (automatically loaded):

```bash
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
USER_FIRST_NAME=Mario
USER_LAST_NAME=Rossi
USER_EMAIL=mario@example.com
USER_PHONE=+393201234567
```

### Custom Scripts

```python
from src.api import ResDiaryClient
from src.bot import BookingBot
from src.notifiers import TelegramNotifier

# Create components
api = ResDiaryClient()
notifier = TelegramNotifier(token="...", chat_id="...")
bot = BookingBot(api, notifier)

# Quick check
results = bot.quick_check(
    target_dates=["2026-04-15", "2026-04-22"],
    party_size=2
)
print(results)
```

## 🔍 What's Missing

The bot is 95% complete. The only missing piece is the **final booking endpoint**.

### How to Complete

When bookings are available:

1. Open Chrome DevTools → Network tab
2. Select a time slot on the booking page
3. Click "Next" to proceed
4. Find the POST request in Network tab
5. Right-click → Copy → Copy as cURL
6. Update `src/api/resdiary_client.py` → `book_table()` method

### Likely Endpoints

```
POST https://booking.resdiary.com/api/Restaurant/TRATTORIATRIPPA/Booking
POST https://booking.resdiary.com/api/Restaurant/TRATTORIATRIPPA/CreateBooking
POST https://booking.resdiary.com/api/Restaurant/TRATTORIATRIPPA/Reserve
```

## 📊 Monitoring

### Logs

```bash
# Follow logs in real-time
tail -f logs/trippa_bot.log

# Search for errors
grep ERROR logs/trippa_bot.log

# Last 50 lines
tail -50 logs/trippa_bot.log
```

### Telegram Notifications

You'll receive:
- 🎉 Availability alerts
- ✅ Booking confirmations
- ❌ Error notifications
- 🎯 Sniper activation alerts

## 🐛 Troubleshooting

### Bot doesn't find availability

This is normal! Trippa sells out in seconds. Make sure:
- Release day sniper is enabled
- Your Mac is on and connected on the 1st
- Telegram notifications are working

### Telegram not working

```bash
# Test manually
python -c "
from src.notifiers import TelegramNotifier
n = TelegramNotifier('YOUR_TOKEN', 'YOUR_CHAT_ID')
n.test_connection()
"
```

Verify:
- Token is correct (from @BotFather)
- Chat ID is correct (from @userinfobot)
- You've started a conversation with your bot

### API errors

- Check internet connection
- Verify ResDiary website is up
- Check logs for specific errors

### Import errors

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## ⚖️ Legal & Ethics

- ✅ For **personal use only** (non-commercial)
- ✅ Respects rate limits (built-in delays)
- ⚠️ May violate ResDiary Terms of Service
- ⚠️ Could result in IP ban if abused
- ❌ Do not use for scalping/reselling reservations

**Use responsibly.** The bot has rate limiting to avoid overwhelming the server.

## 📝 License

MIT License - Use at your own risk

## 🤝 Contributing

Found an issue or want to improve the bot?
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 💡 Tips

- **Be patient**: Even with the bot, Trippa is extremely competitive
- **Set multiple target dates**: Increases your chances
- **Enable auto-booking** only when you're sure about the dates
- **Test first**: Always run `--test` before going live
- **Monitor logs**: Keep an eye on the bot's activity

## 🙏 Credits

Built with:
- Python 3
- Requests library
- Schedule library
- Telegram Bot API
- Love for good food 🍝

---

**Buona fortuna!** 🍀

May the bot be with you in your quest for a Trippa table!
