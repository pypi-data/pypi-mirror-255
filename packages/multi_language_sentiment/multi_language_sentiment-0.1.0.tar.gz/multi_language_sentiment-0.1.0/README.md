# multi-language-sentiment

A pipeline for sentiment analysis for texts with unknown language.

We use the lingua-language-detector to detect the language and run the text
samples through an sentiment analysis appropriate pipeline for that language.

## Usage

Basic usage for analysing a list of sentences:

``` python
import multi_language_sentiment

texts = ["This is a positive sentence", "Tämä on ikävä juttu"]
sentiments = multi_language_sentiment.sentiment(texts)
print(sentiments)
```

This should print
```
[{'label': 'positive', 'score': 0.89024418592453}, {'label': 'negative', 'score': 0.8899219632148743}]
```

### Supported language

The module currently supports the following langauges by default: English, Japanese, Arabic, German, Spanish, French, Chinese, Indonesian, Hindi, Italian, Malay, Portuguese, Swedish, and Finnish.

For other languages, you must supply a path for a HuggingFace sentiment analysis pipeline. To supply
a pipelien for a new language, use the models parameter:

``` python
import multi_language_sentiment
from lingua import Language

texts = ["This is a positive sentence", "Tämä on ikävä juttu"]
models = {Language.FINNISH: "fergusq/finbert-finnsentiment"}
sentiments = multi_language_sentiment.sentiment(texts, models = models)
```


## Technical details

Note that the pipeline will split each text sample to a maximum length of 512 characters. The
sentiments are aggregated by adding up the scores and taking the largest value.
