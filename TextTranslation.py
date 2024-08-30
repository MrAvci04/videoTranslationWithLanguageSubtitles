from googletrans import Translator
from google.cloud import translate_v2 as translate

# Initialize the translator
translator = Translator()


def googletrans_translate_text(text_to_translate: str, target_language: str):

    text_to_translate = "Hello, how are you?"

    # Translate from English to target language
    translation = translator.translate(text_to_translate, src='en', dest='ar')

    # Print the translated text
    print(f"Original Text: {text_to_translate}")
    print(f"Translated Text: {translation.text}")


# Need google credentials json file and enabling the google translate service in Google cloud console
def google_cloud_translate_text(text_to_translate: str, target_language: str):

    # Initialize the Google Cloud client
    client = translate.Client()

    # Translate from English to target language
    result = client.translate(text_to_translate, target_language=target_language)

    # Print the translated text
    print(f"Translated Text: {result['translatedText']}")


def translate_segments(segments, target_language='ar'):
    """
    Translate each subtitle segment to the target language.

    Args:
    segments (list of dict): List of subtitle segments with text.
    target_language (str): Language code for the target translation language (e.g., 'es' for Spanish).

    Returns:
    list of dict: Translated subtitle segments.
    """
    translated_segments = []

    for segment in segments:
        translated_text = translator.translate(segment.text, dest=target_language).text
        translated_segments.append({
            'start': segment.start,
            'end': segment.end,
            'text': translated_text
        })

    return translated_segments

