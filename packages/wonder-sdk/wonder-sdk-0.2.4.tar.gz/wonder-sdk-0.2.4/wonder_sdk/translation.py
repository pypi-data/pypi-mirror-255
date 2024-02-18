from logging import Logger
from google.cloud import translate_v2

def translate(client, text, target_language, logger):
    """
    Translates text into a specified target language using Google Cloud Translation.

    This function takes a string of text and translates it into the specified target language.
    It uses the Google Cloud Translation client for the translation process.

    Args:
        client (Translate Client): The Google Cloud Translation client used to perform translations.
        text (str): The text to be translated.
        target_language (str): The language code of the target language (e.g., 'en' for English).
        logger (Logger): The logger to use for logging.

    Returns:
        str: The translated text.

    Raises:
        ValueError: If any of the input parameters are invalid.
        Exception: If the translation process fails.
    """
    if not isinstance(logger, Logger):
        raise ValueError("Logger must be a Logger object.")
    if not isinstance(client, translate_v2.Client):
        logger.error("Invalid translate client type provided.")
        raise ValueError("Client must be a Google Cloud Translate Client.")
    if not isinstance(text, str) or not text:
        logger.error("Invalid text provided for translation.")
        raise ValueError("Text must be a non-empty string.")
    if not isinstance(target_language, str) or not target_language:
        logger.error("Invalid target language provided.")
        raise ValueError("Target language must be a non-empty string.")

    logger.info(f"Translating text to '{target_language}' language.")

    try:
        translation = client.translate(text, target_language=target_language)
        translated_text = translation['translatedText']
        logger.info("Text translated successfully.")
        return translated_text
    except Exception as e:
        logger.exception("Exception occurred during the translation process.")
        raise e