from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest
from utils import translate_with_libretranslate
import asyncio
import spacy
import dateparser
from datetime import datetime
import re
import unicodedata

# === CONFIGURATION ===
api_id = '--' # Telegram API ID
api_hash = '--' # Telegram API Hash
phone_number = '--'  # Your phone number with country code (e.g., +1234567890)
target_channel = "--"
chat_ids =   ['--']
                    
             # List of chat IDs to monitor for new messages

nlp = spacy.load("xx_ent_wiki_sm")

#\/ list of keywords the bot will look for, ensure that the keywords are in the original language 
KEYWORDS = [
    # English
    "strike", "attack", "explosion", "blast", "missile", "rocket", "drone",
    "injured", "injuries", "wounded", "killed", "fatalities", "dead",
    
    # Language 2 (add more as needed) - example used Russian
    "удар", "взрыв", "обстрел", "ракета", "дрон", "погиб", "ранен", "жертва",
    
    # Language 3 (add more as needed) - example used Ukrainian
    "удар", "вибух", "обстріл", "ракета", "дрон", "загиблий", "поранений", "жертва"
]

# Example regex to detect times like "16:10", "6, 30", "24, June"
time_patterns = [
    r'\b\d{1,2}[:.,]\d{2}\b',          # matches 16:10, 6.30, 5,15
    r'\b\d{1,2}\s?(?:годин[а-и]?|h|hours?)\b',  # matches "16 годин", "6 h"
]

# Words indicating time of day (add equivalents of target language)
time_words = [
    "morning", "afternoon", "evening", "night",
    "ранок", "день", "вечір", "ніч",
]

def contains_keywords(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

BLACKLIST = [
    "--",
]
# Specific words that the bot should NOT count as a location, have to use trial and error, helpful with messages from formulaic sources

# Typical target language location suffixes including locative forms
LOCATION_SUFFIXES = ['ськ', 'ська', 'ську', 'ське', 'ка', 'ів', 'ця', 'город', 'область', 'район', 'місто']

def normalize_text(text):
    # Normalize apostrophes and Unicode forms
    text = text.replace("ʼ", "'")  # Replace similar apostrophe chars with ASCII '
    text = unicodedata.normalize('NFC', text)
    return text

def is_likely_location(name):
    name = normalize_text(name).lower()
    # Check suffix
    return any(name.endswith(suffix) for suffix in LOCATION_SUFFIXES)

def extract_location(text):
    text = normalize_text(text)
    doc = nlp(text)
    locations = []

    # 1. Filter spaCy entities for LOC and GPE, exclude blacklist, check suffix
    for ent in doc.ents:
        ent_norm = normalize_text(ent.text)
        if ent.label_ in ("LOC", "GPE") and ent_norm not in BLACKLIST:
            if is_likely_location(ent_norm):
                locations.append(ent.text)

    # 2. Regex: Look for words after prepositions "по", "в", or "у" < Replace with prepositions from target language
    # Capture word with letters, apostrophes, hyphens, allowing Ukrainian letters
    pattern = r'(?:по|в|у)\s+([А-ЯҐЄІЇа-яґєії\'ʼ\-]+)'
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    for match in matches:
        match_norm = normalize_text(match)
        if match_norm not in BLACKLIST:
            # Accept if suffix looks like location OR is capitalized (fallback)
            if is_likely_location(match_norm) or match[0].isupper():
                locations.append(match)

    # Remove duplicates and return
    locations = list(set(locations))
    return locations


#Extract entities with allowed labels and exclude legal codes
    locations = [
        ent.text for ent in doc.ents
        if ent.label_ in candidate_labels and not legal_code_pattern.match(ent.text)
    ]

    # If no locations found, try heuristic: entity immediately after "in", "у", "в", or "на"
    if not locations:
        words = [token.text.lower() for token in doc]
        prepositions = ("in", "у", "в", "на")
        for i, token in enumerate(words[:-1]):
            if token in prepositions:
                next_token_index = i + 1
                # Check if next token is the start of an entity with allowed label and not legal code
                for ent in doc.ents:
                    if ent.start == next_token_index and ent.label_ in candidate_labels and not legal_code_pattern.match(ent.text):
                        locations.append(ent.text)
                        break  # stop after first match

    return locations


def extract_datetime(text):
    # First try to find date and time-like substrings manually via regex
    # This regex looks for things like "24 червня близько 16:10" or "24 June 16:10"
    datetime_pattern = re.compile(
        r'(\d{1,2}\s*(?:червня|липня|серпня|вересня|жовтня|листопада|грудня|січня|лютого|березня|квітня|травня|червня|June|July|August|September|October|November|December|January|February|March|April|May)\s*(?:близько)?\s*\d{1,2}[:.:,]\d{2})',
        re.IGNORECASE
    )
    match = datetime_pattern.search(text)
    if match:
        date_str = match.group(1)
        # Use dateparser to parse this date/time string with current year and relative base
        dt = dateparser.parse(date_str, settings={'RELATIVE_BASE': datetime.now()})
        if dt:
            return dt

    # If no explicit datetime pattern matched, fallback to general parsing if time keywords present
    time_words = ["morning", "afternoon", "evening", "night", "ранок", "день", "вечір", "ніч"]
    if any(word in text.lower() for word in time_words):
        dt = dateparser.parse(text, settings={'RELATIVE_BASE': datetime.now()})
        if dt:
            return dt

    return None

# === END OF CONFIGURATION ===

# Initialize the client
client = TelegramClient('session_name', api_id, api_hash)

async def get_channel_name(chat_id):
    # Get full channel info
    full_channel = await client(GetFullChannelRequest(channel=chat_id))
    
    # The channel object is in .chats[0]
    channel = full_channel.chats[0]
    
    # The title is the name of the channel
    return channel.title

async def main():
    # Connect and authorize if needed
    await client.start(phone_number)
    print("Client created and connected!")

    @client.on(events.NewMessage(chats=chat_ids))
    async def handler(event):
        message_text = event.text
        doc = nlp(message_text)
    
        print("=== Named Entities detected in message ===")
        for ent in doc.ents:
            print(f"Text: '{ent.text}', Label: {ent.label_}")
            
        sender = await event.get_sender()

        if sender is None:
            sender_name = 'Unknown'
        elif hasattr(sender, 'username') and sender.username:
            sender_name = sender.username
        elif hasattr(sender, 'first_name') and sender.first_name:
            sender_name = sender.first_name
        elif hasattr(sender, 'title') and sender.title:
            sender_name = sender.title
        else:
            sender_name = 'Unknown'

        channel_name = await get_channel_name(event.chat_id)

        if not contains_keywords(message_text):
            print(f"⛔ Ignored message from {channel_name} — no relevant keywords found.")
            return

        locations = extract_location(message_text)
        dt = extract_datetime(message_text)

        location_text = ", ".join(locations) if locations else "Unknown"
        datetime_text = dt.strftime("%Y-%m-%d %H:%M") if dt else "Unknown"

        print(f"🔔 Relevant message detected from {sender_name} in {channel_name}")

        # Translate
        print(f"New message from {sender_name} in chat {channel_name}")
        result = translate_with_libretranslate(message_text)
        if result:
            detected_lang = result["detected_language"]
            confidence = result["confidence"]
            translation = result["translation"]

            # Final message to send to target channel
            final_message = (
                f"🌐 **New Translated Message**\n\n"
                f"**Original Channel:** {channel_name}\n"
                f"**Sender:** {sender_name}\n"
                f"**Detected Location(s):** {location_text}\n"
                f"**Detected Time:** {datetime_text}\n\n"
                f"**Detected Language:** {detected_lang} (confidence: {confidence:.2f})\n\n"
                f"**Original Message:**\n{message_text}\n\n"
                f"**Translated to English:**\n{translation}"
            )

            print("✅ Translation successful!")
            print(f"Detected language: {detected_lang} (confidence: {confidence:.2f})")
            await client.send_message(target_channel, final_message, parse_mode="markdown")
            print(f"✅ Sent translated message to {target_channel}.")
        else:
            print("❌ Failed to translate or detect language. Sending original message.")
            final_message = (
                f"🌐 **New Translated Message**\n\n"
                f"**Original Channel:** {channel_name}\n"
                f"**Sender:** {sender_name}\n\n"
                f"**Original Message:**\n{message_text}\n\n"
            )
            await client.send_message(target_channel, final_message, parse_mode="markdown")
            print(f"✅ Sent message to {target_channel}.")

    print("Listening for new messages...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())