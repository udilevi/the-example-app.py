import json
import os
import glob


TRANSLATIONS = {}


def initialize_translations():
    if TRANSLATIONS:
        return

    locales_path = os.path.join(os.path.dirname(__file__), 'locales')

    try:
        for file_name in glob.glob(os.path.join(locales_path, '*.json')):
            locale_name = file_name.split('/')[-1].replace('.json', '')

            with open(file_name, 'r') as f:
                TRANSLATIONS[locale_name] = json.loads(f.read())
    except Exception as e:
        print('Error loading localization files.')
        print(e)


def translate(symbol, locale='en-US'):
    locale_dict = TRANSLATIONS.get(locale, None)
    if locale_dict is None:
        return 'Localization file for {0} is not available'.format(locale)

    translated_value = locale_dict.get(symbol, None)
    if translated_value is None:
        return 'Translation not found for {0} in {1}'.format(symbol, locale)

    return translated_value


def is_translation_available(symbol, locale='en-US'):
    bool(TRANSLATIONS.get(locale, {}).get(symbol, False))