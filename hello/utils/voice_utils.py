# utils/voice_utils.py
def get_flag_emoji(locale):
    country_code = locale.split('-')[-1].upper()
    return ''.join(chr(127397 + ord(c)) for c in country_code)


def get_language_display(locale):
    lang_map = {
        'en-US': 'English (US)',
        'en-GB': 'English (UK)',
        'en-IN': 'English (India)',
        'ml-IN': 'Malayalam',
        'fr-FR': 'French',
        'de-DE': 'German',
        'hi-IN': 'Hindi',
        'ar-AE': 'Arabic',
        # Add more as needed
    }
    return lang_map.get(locale, locale)
