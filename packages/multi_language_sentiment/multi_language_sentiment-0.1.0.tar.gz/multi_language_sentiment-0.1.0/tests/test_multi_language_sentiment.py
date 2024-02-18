import multi_language_sentiment

def test_sentiment():
    messages = [
        "I'm happy to write in English. This should not be hard to detect.",
        "I'm sad to write in English. This is long enough to be detected.",
        "Does this get detected?",
        "Olen iloinen",
        "Harmillinen juttu",
        "Allt går fint",
        "Detta är inte bra",
        "Jag skall gå till supermarket",
        ""
    ]
    sentiments = multi_language_sentiment.sentiment(messages)

    assert sentiments[0]["label"] == "positive"
    assert sentiments[1]["label"] == "negative"
    assert sentiments[3]["label"] == "positive"
    assert sentiments[4]["label"] == "negative"
    assert sentiments[5]["label"] == "positive"
    assert sentiments[6]["label"] == "negative"
    assert sentiments[7]["label"] == "neutral"
    assert sentiments[8]["label"] == "none"
