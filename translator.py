from deep_translator import GoogleTranslator

_translator_cache = {}


def translate(text, target_language="en"):
    try:
        key = target_language
        if key not in _translator_cache:
            _translator_cache[key] = GoogleTranslator(source="auto", target=target_language)
        return _translator_cache[key].translate(text)
    except Exception:
        return None
