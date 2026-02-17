try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False

def g_translate(text, lang):
    """
    Translates text to the target language using deep-translator (Google Translator).
    Returns original text if translation service is unavailable.
    """
    if not HAS_TRANSLATOR:
        return "Translation unavailable (dependency error)."

    try:
        translator = GoogleTranslator(source='en', target=lang)
        
        # deep-translator handles long text better, but we'll still do a basic check
        if len(text) > 4500:
             # Split and translate if very long
             parts = [text[i:i+4500] for i in range(0, len(text), 4500)]
             translated_parts = [translator.translate(p) for p in parts]
             return ' '.join(translated_parts)
        
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return "Translation unavailable."
