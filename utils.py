import requests

def translate_with_libretranslate(text, target_lang='en'):
    """
    Detect the language and translate the text to English using local LibreTranslate.
    Returns a dict with detected language, confidence, and translated text.
    """
    url_translate = "http://localhost:5555/translate"
    url_detect = "http://localhost:5555/detect"
    headers = {"Content-Type": "application/json"}

    try:
        # Detect the source language
        detect_resp = requests.post(url_detect, json={"q": text}, headers=headers, timeout=10)
        detect_resp.raise_for_status()
        detection = detect_resp.json()[0]  # top detection
        detected_lang = detection["language"]
        confidence = detection["confidence"]

        # Translate
        data = {
            "q": text,
            "source": detected_lang,
            "target": target_lang,
            "format": "text"
        }
        translate_resp = requests.post(url_translate, json=data, headers=headers, timeout=10)
        translate_resp.raise_for_status()
        translated_text = translate_resp.json()["translatedText"]

        return {
            "detected_language": detected_lang,
            "confidence": confidence,
            "translation": translated_text
        }

    except requests.RequestException as e:
        print(f"Translation error: {e}")
        return None