# Telegram Monitoring & Translation Bot 🛰
A Python-based Telegram bot that monitors selected channels for messages related to something of your choice -conflict for example- extracts key entities (like locations and times), and translates messages to English using a self-hosted LibreTranslate instance. It then posts structured alerts to a designated Telegram channel.

🚀 Features
📥 Real-time monitoring of specific Telegram channels/chats

🔍 Keyword-based filtering in multiple languages

📌 Named Entity Recognition (NER) for location and datetime extraction

🌍 Automatic translation via LibreTranslate (self-hosted)

📤 Forwards enriched and translated messages to a target Telegram channel

🛠 Setup & Configuration
### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/FilteredTeleScanner.git
cd telegram-translator-bot
```
---

### 2️⃣ ✅ Create a virtual environment (recommended):

```bash
python -m venv .venv
```

### 3️⃣ Install Python Dependencies
```bash
pip install -r requirements.txt
python -m spacy download xx_ent_wiki_sm
```

### 4️⃣ Set up LibreTranslate locally

This project requires you to **self-host LibreTranslate** for translation.

#### ➜ Install Docker

Download and install Docker Desktop from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/).

#### ➜ Run LibreTranslate

```bash
docker run -it -p 5555:5000 libretranslate/libretranslate
```

✅ This will:

* Download and run LibreTranslate, exposing it on `http://localhost:5555`.
* On first startup, download translation models (this takes a few minutes).

### 5️⃣ Configure the bot

Open main.py and configure the following:
```bash
api_id = '--'            # Telegram API ID from my.telegram.org
api_hash = '--'          # Telegram API Hash
phone_number = '--'      # Phone number with country code (e.g., +1234567890)
target_channel = '--'    # Target channel where results are posted
chat_ids = ['--']        # List of monitored chat/channel IDs
```

You can also customize:

    1. KEYWORDS in multiple languages

    2. BLACKLIST for non-location named entities

    3. LOCATION_SUFFIXES based on language/geography

    4. Regex patterns for datetime detection

### 6️⃣ Run the bot!

```bash
python main.py
```


📝 Sample Output

"
🌐 New Translated Message

Original Channel: such and such
Sender: so and so
Detected Location(s): Detected place 1, Detected place 2 
Detected Time: 2025-06-29 06:45

Detected Language: uk (confidence: 0.98)

Original Message:
В Одесі стався вибух близько 6:45 ранку.

Translated to English:
An explosion occurred in Odesa around 6:45 AM.
"

📓 Important notes
* 1. This bot, used correctly, is not a plug and play solution, it will not work without accurate input of localized prepositions in main.py
    
* 2. This bot is not infallible, it will make mistakes regarding location and time so always double check its output with the translated message


✅ The bot will:

* Connect to Telegram using Telethon
* Listen for new messages in your source chats
* Filter for keywords of your choosing
* Detect the source language and confidence
* Translate to English
* Forward the translated text (with detected language, time, location & confidence) to your target channel

---

## ⚡ Full Features

*✅ Listen to any number of Telegram channels
*✅ Automatically detect the source language and its confidence
*✅ Translate to English (LibreTranslate)
*✅ Filter for any keywords or topics
*✅ Detect location and time of incident
*✅ Forward everything to a target Telegram channel
*✅ Fully self-hosted translation (no external API costs!)
