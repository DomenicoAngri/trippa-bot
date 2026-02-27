# 🍝 Trippa Milano Booking Bot

Bot automatico per prenotare alla Trattoria Trippa quando i tavoli sono sold-out.

## 🎯 Funzionalità

- **Release Day Sniper**: Si attiva automaticamente il 1° del mese e prenota alla velocità della luce
- **Monitor Cancellazioni**: Controlla periodicamente se si liberano posti da cancellazioni
- **Notifiche Telegram**: Ti avvisa immediatamente quando trova disponibilità
- **Auto-booking** (opzionale): Prenota automaticamente senza intervento manuale

## 📋 Prerequisiti

- Python 3.8 o superiore
- Connessione internet stabile
- Account Telegram (per le notifiche)

## 🚀 Installazione

### 1. Clona o scarica il progetto

```bash
cd /path/to/your/folder
```

### 2. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 3. Configura il bot Telegram

#### 3.1 Crea un bot Telegram

1. Apri Telegram e cerca `@BotFather`
2. Invia `/newbot`
3. Segui le istruzioni (scegli un nome e un username)
4. **Copia il token** che ti viene fornito (es. `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 3.2 Ottieni il tuo Chat ID

1. Apri Telegram e cerca `@userinfobot`
2. Invia `/start`
3. **Copia il tuo ID** (es. `987654321`)

### 4. Configura il bot

Modifica il file `config.py`:

```python
# Inserisci i TUOI dati
USER_DATA = {
    "first_name": "Mario",                    # ← TUO NOME
    "last_name": "Rossi",                     # ← TUO COGNOME
    "email": "mario.rossi@example.com",       # ← TUA EMAIL
    "phone": "+393201234567",                 # ← TUO TELEFONO
}

# Configura Telegram
TELEGRAM_CONFIG = {
    "enabled": True,
    "bot_token": "123456789:ABCdefGHI...",    # ← TOKEN BOT
    "chat_id": "987654321",                   # ← TUO CHAT ID
}

# Scegli le date che ti interessano
BOOKING_PREFERENCES = {
    "party_size": 2,                          # ← NUMERO PERSONE
    "preferred_times": [                      # ← ORARI PREFERITI
        "20:00",
        "20:15",
        "20:30"
    ],
    "target_dates": [                         # ← DATE DESIDERATE
        "2026-04-15",
        "2026-04-22"
    ]
}
```

## 🎮 Utilizzo

### Modalità Automatica (Raccomandata)

Avvia il bot e lascialo girare:

```bash
python main.py
```

Il bot farà tutto automaticamente:
- Monitora le cancellazioni ogni 30 minuti
- Si attiva il 1° del mese per il "release day"
- Ti notifica su Telegram quando trova posti

### Test Manuale

Per testare le API senza far partire lo scheduler:

```bash
python trippa_bot.py
```

### Test Telegram

Per verificare che le notifiche funzionino:

```bash
python telegram_notifier.py YOUR_BOT_TOKEN YOUR_CHAT_ID
```

## ⚙️ Configurazione Avanzata

### Release Day Sniper

```python
RELEASE_CONFIG = {
    "enabled": True,
    "day_of_month": 1,        # Giorno di apertura prenotazioni
    "hour": 0,                # Ora (0 = mezzanotte)
    "minute": 0,
    "auto_book": False,       # True = prenota automaticamente
}
```

### Monitor Cancellazioni

```python
MONITOR_CONFIG = {
    "enabled": True,
    "check_interval": 1800,   # Ogni 30 minuti (in secondi)
    "auto_book": False,       # True = prenota automaticamente
}
```

## 🖥️ Esecuzione su Mac (Sempre Attivo)

### Opzione 1: Usa launchd (Raccomandato)

Crea il file `~/Library/LaunchAgents/com.trippabot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.trippabot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/trippa-bot/main.py</string>
    </array>
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

Poi:

```bash
# Carica il servizio
launchctl load ~/Library/LaunchAgents/com.trippabot.plist

# Verifica che sia attivo
launchctl list | grep trippabot
```

### Opzione 2: Screen/Tmux

```bash
# Installa screen
brew install screen

# Avvia sessione
screen -S trippabot

# Esegui il bot
python main.py

# Detach con Ctrl+A poi D
# Riattacca con: screen -r trippabot
```

## 🔍 Cosa Manca (TODO)

**IMPORTANTE**: Il bot è quasi completo, ma manca l'endpoint finale di prenotazione!

### Come completare:

1. **Aspetta che ci siano posti disponibili** (es. 1° aprile)
2. Apri Chrome DevTools → Network
3. Seleziona una data/ora disponibile
4. **Clicca "Next"** per procedere alla prenotazione
5. Copia la cURL della chiamata POST che viene fatta
6. Inviamela e completo il metodo `book_table()` in `trippa_bot.py`

### Endpoint probabili da testare:

```
POST https://booking.resdiary.com/api/Restaurant/TRATTORIATRIPPA/Booking
POST https://booking.resdiary.com/api/Restaurant/TRATTORIATRIPPA/Reserve
POST https://booking.resdiary.com/api/Restaurant/TRATTORIATRIPPA/CreateBooking
```

Puoi anche provare a scoprirlo con:

```bash
python analyze_js.py
```

## 📊 Monitoraggio

### Log File

Il bot scrive tutto in `trippa_bot.log`:

```bash
# Segui il log in tempo reale
tail -f trippa_bot.log
```

### Notifiche Telegram

Riceverai:
- 🎉 Alert quando trova disponibilità
- ✅ Conferma prenotazione riuscita
- ❌ Errori o problemi
- 🎯 Avvio modalità sniper

## ⚠️ Note Legali

- Questo bot è per **uso personale** e non commerciale
- Non sovraccaricare il server (il bot ha rate limiting integrato)
- Rispetta le policy di ResDiary e del ristorante
- L'autore non è responsabile per eventuali ban o problemi

## 🐛 Troubleshooting

### Il bot non trova mai posti

- È normale! Trippa è sold-out in secondi
- Assicurati che `release_day_sniper` sia abilitato
- Verifica che il tuo Mac sia acceso il 1° del mese

### Le notifiche Telegram non arrivano

```bash
# Test connessione
python telegram_notifier.py YOUR_TOKEN YOUR_CHAT_ID
```

Verifica:
- Token corretto da @BotFather
- Chat ID corretto da @userinfobot
- Hai avviato una conversazione con il bot

### Errori di connessione

- Verifica la tua connessione internet
- Il sito potrebbe essere temporaneamente down
- Controlla i log per dettagli

## 🤝 Contributi

Per miglioramenti o bug, apri una issue!

## 📝 License

MIT - Fai quello che vuoi, ma a tuo rischio e pericolo 😄

---

**Buona caccia al tavolo! 🍝**
