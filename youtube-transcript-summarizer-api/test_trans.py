try:
    from googletrans import Translator
    translator = Translator()
    result = translator.translate("Hello world", dest='hi')
    print(f"Translation successful: {result.text}")
except Exception as e:
    print(f"Translation failed: {e}")
