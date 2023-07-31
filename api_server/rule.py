import random
from textblob import TextBlob

import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize

nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
from nltk.corpus import wordnet


class Rule:
    name = "Rule"
    description = "Base Rule"

    def preprocessing(self, message):
        return message

    def postprocessing(self, response):
        return response


def get_unique_synonyms(word):
    # Get synsets for the word
    synsets = wordnet.synsets(word)

    # Get lemmas for each synset and extract unique synonyms
    synonyms = set(
        lemma.replace("_", " ") for synset in synsets for lemma in synset.lemma_names())

    # Remove the original word from the set of synonyms
    synonyms.discard(word)

    return list(synonyms)


def find_adjectives_and_nouns(message):
    # Tokenize the message into words
    words = word_tokenize(message)

    # Use nltk's part-of-speech tagging to tag each word with its POS
    tagged_words = pos_tag(words)

    # Initialize lists to store adjectives and nouns
    adjectives = []
    nouns = []

    # Iterate over each tagged word
    for word, pos in tagged_words:
        # Check if the word is an adjective or a noun
        if pos.startswith("JJ"):
            adjectives.append(word)
        elif pos.startswith("NN"):
            nouns.append(word)

    return adjectives, nouns


class SynonymRule(Rule):
    name = "SynonymRule"
    description = "Replaces words with words"

    def __init__(self):
        self.synonyms_percentage = 1

    def preprocessing(self, message):
        adjectives, nouns = find_adjectives_and_nouns(message)

        # Get x% of adjectives and nouns (rounded to the nearest integer)
        num_adjectives_to_replace = int(len(adjectives) * self.synonyms_percentage)
        num_nouns_to_replace = int(len(nouns) * self.synonyms_percentage)

        synonyms = {}
        while num_adjectives_to_replace > 0:
            adj = random.choice(adjectives)
            adjectives.remove(adj)
            synonym = random.choice(get_unique_synonyms(adj))
            synonyms[adj] = synonym
            num_adjectives_to_replace -= 1

        while num_nouns_to_replace > 0:
            noun = random.choice(nouns)
            nouns.remove(noun)
            synonym = random.choice(get_unique_synonyms(noun))
            synonyms[noun] = synonym
            num_nouns_to_replace -= 1

        for word, synonym in synonyms.items():
            print(word, synonym)
            message = message.replace(word, synonym)
        return message


class EmojiRule(Rule):
    name = "EmojiRule"
    description = "Inserts emojis to make responses more expressive and engaging"  # sentimental analysis, place some emojis, resond with alot emojis

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
        message = message + "\n" + "This is a " + sentiment + " message. Please use a lot of " + sentiment + " emojis in your response!!"
        return message


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
