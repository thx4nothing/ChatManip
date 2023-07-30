import random
from textblob import TextBlob


class Rule:
    name = "Rule"
    description = "Base Rule"

    def preprocessing(self, message):
        return message

    def postprocessing(self, response):
        return response


class SynonymRule(Rule):
    name = "SynonymRule"
    description = "Replaces words with words"

    def __init__(self):
        self.synonyms = {"hello": "hi", "world": "earth"}

    def preprocessing(self, message):
        for word, synonym in self.synonyms.items():
            message = message.replace(word, synonym)
        return message

    def postprocessing(self, response):
        for word, synonym in self.synonyms.items():
            response = response.replace(word, synonym)
        print(response)
        print(self.synonyms)
        return response


class EmojiRule(Rule):
    name = "EmojiRule"
    description = "Inserts emojis to make responses more expressive and engaging"  # sentimental analysis, place some emojis, resond with alot emojis

    def __init__(self):
        self.emojis = ["😀", "😂"]

    def preprocessing(self, message):
        blob = TextBlob(message)
        sentiment_polarity = blob.sentiment.polarity
        if sentiment_polarity > 0:
            sentiment = "positive"
        elif sentiment_polarity == 0:
            sentiment = "neutral"
        else:
            sentiment = "negative"
        print(sentiment_polarity)
        message = message + "\n" + "This is a " + sentiment + " message. Please use a lot of emojis in your response!!"
        return message

    def postprocessing(self, response):
        response = response + "\n" + random.choice(self.emojis)
        return response


class ShortRule(Rule):
    name = "ShortRule"
    description = "Attempts to generate a really short answer"

    def preprocessing(self, message):
        message = (message + "\n" +
                   "Please make your answer as short as possible. I mean really REALLY short!")
        return message


class LongRule(Rule):
    name = "LongRule"
    description = "Attempts to generate a really long and detailed answer"

    def preprocessing(self, message):
        message = (message + "\n" +
                   "Please make your answer as long and detailed as possible. I mean really REALLY long!")
        return message


class HumorRule(Rule):
    name = "HumorRule"
    description = "Randomly makes the response contain a joke about the discussed topic"

    def preprocessing(self, message):
        if random.random() < 0.8:
            message = message + "\n" + "Append a joke about this topic at the end of your response."
        return message


class StorytellingRule(Rule):
    name = "StorytellingRule"
    description = "Responds in a storytelling format to engage the user with narrative driven respones"

    def preprocessing(self, message):
        message = "Once upon a time, this topic was to be discussed: " + "\n" + message + "\n" "What happened next? Tell me about it in a story telling style. like a folk tale."
        return message


class DetectMistakesRule(Rule):
    name = "DetectMistakesRule"
    description = "Detects Mistakes"


class SarcasmRule(Rule):
    name = "SarcasmRule"
    description = "Makes the response contain sarcasm"

    def preprocessing(self, message):
        message = message + "\n" + "Make your response as sarcastic as possible."
        return message
