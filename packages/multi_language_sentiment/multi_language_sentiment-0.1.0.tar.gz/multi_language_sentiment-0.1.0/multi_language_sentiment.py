"""
Sentiment analysis pipeline for texts in multiple languages.
"""

import gc
from collections import defaultdict

from transformers import pipeline
import torch
from lingua import Language, LanguageDetectorBuilder


__version__ = "0.1.0"

if torch.cuda.is_available():
    device_tag = 0 # first gpu
else:
    device_tag = -1 # cpu


default_models = {
    Language.ENGLISH: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.JAPANESE: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.ARABIC: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.GERMAN: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.SPANISH: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.FRENCH: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.CHINESE: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.INDONESIAN: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.HINDI: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.ITALIAN: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.MALAY: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.PORTUGUESE: "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    Language.SWEDISH: "KBLab/robust-swedish-sentiment-multiclass",
    Language.FINNISH: "fergusq/finbert-finnsentiment",
}

language_detector = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()


# Processing a batch:
# Detect languages into a list and map to models
# For each model, make a pipeline, make a list and process
# inject int a list in the original order

def split_message(message, max_length):
    """ Split a message into a list of chunks of given maximum size. """
    return [message[i: i+max_length] for i in range(0, len(message), max_length)]


def process_messages_in_batches(
        messages_with_languages,
        models = None,
        max_length = 512
    ):
    """
    Process messages in batches, creating only one pipeline at a time, and maintain the original order.
    
    Params:
    messages_with_languages: list of tuples, each containing a message and its detected language
    models: dict, model paths indexed by Language
    
    Returns:
    OrderedDict: containing the index as keys and tuple of (message, sentiment result) as values
    """

    if models is None:
        models = default_models
    else:
        models = default_models.copy().update(models)

    results = {}

    # Group messages by model, preserving original order.
    # If language is no detected or a model for that language is not
    # provided, add None to results
    messages_by_model = defaultdict(list)
    for index, (message, language) in enumerate(messages_with_languages):
        model_name = models.get(language)
        if model_name:
            messages_by_model[model_name].append((index, message))
        else:
            results[index] = {"label": "none", "score": 0}
    
    # Process messages and maintain original order
    for model_name, batch in messages_by_model.items():
        sentiment_pipeline = pipeline(model=model_name, device=device_tag)

        chunks = []
        message_map = {}
        for idx, message in batch:
            message_chunks = split_message(message, max_length)
            for chunk in message_chunks:
                chunks.append(chunk)
                if idx in message_map:
                    message_map[idx].append(len(chunks) - 1)
                else:
                    message_map[idx] = [len(chunks) - 1]
        
        chunk_sentiments = sentiment_pipeline(chunks)

        for idx, chunk_indices in message_map.items():
            sum_scores = {"neutral": 0}
            for chunk_idx in chunk_indices:
                label = chunk_sentiments[chunk_idx]["label"]
                score = chunk_sentiments[chunk_idx]["score"]
                if label in sum_scores:
                    sum_scores[label] += score
                else:
                    sum_scores[label] = score
            best_sentiment = max(sum_scores, key=sum_scores.get)
            score = sum_scores[best_sentiment] / len(chunk_indices)
            results[idx] = {"label": best_sentiment, "score": score}

        # Force garbage collections to remove the model from memory
        del sentiment_pipeline
        gc.collect()
    
    # Unify common spellings of the labels
    for i in range(len(results)):
        results[i]["label"] = results[i]["label"].lower()

    results = [results[i] for i in range(len(results))]

    return results


def sentiment(messages, models=None):
    """
    Estimate the sentiment of a list of messages (strings of text). The
    sentences may be in different languages from each other.

    We maintain a list of default models for some languages. In addition,
    the user can provide a model for a given language in the models
    dictionary. The keys for this dictionary are lingua.Language objects
    and items HuggingFace model paths.
    
    Params:
    messages: list of message strings
    models: dict, huggingface model paths indexed by lingua.Language
    
    Returns:
    OrderedDict: containing the index as keys and tuple of (message, sentiment result) as values
    """
    messages_with_languages = [
        (message, language_detector.detect_language_of(message)) for message in messages
    ]

    results = process_messages_in_batches(messages_with_languages, models)
    return  results

