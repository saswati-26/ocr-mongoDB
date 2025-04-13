from deep_translator import GoogleTranslator

def translate_text(text, target_lang="en"):
    translation = GoogleTranslator(source="auto", target=target_lang).translate(text)
    return translation