from deep_translator import GoogleTranslator


def translate(text, target_language="en"):
    try:
        result = GoogleTranslator(source="auto", target=target_language).translate(text)
        return result
    except Exception:
        return None
