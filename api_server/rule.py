import random
from textblob import TextBlob
from api_server.chatgpt_interface import request_system_response

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
        self.synonyms_percentage = 0.8

    def preprocessing(self, message):
        print(self.name + ": Starting Preprocessing")

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

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + message)
        return message


class EmojiRule(Rule):
    name = "EmojiRule"
    description = "Inserts emojis to make responses more expressive and engaging"  # sentimental analysis, place some emojis, resond with alot emojis

    def preprocessing(self, message):
        print(self.name + ": Starting Preprocessing")

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

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + message)
        return message


class SummarizeRule(Rule):
    name = "SummarizeRule"
    description = "Summarizes the user message and sends it to ChatGPT"

    def preprocessing(self, message):
        print(self.name + ": Starting Preprocessing")

        system_instruction = "Your goal is to summarize the text the user provides. Do not send any other response, only the summarized text."
        messages = [{"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}]
        # completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        # summary = completion.choices[0].message.content
        summary = request_system_response(messages)
        print(self.name + ": Finished Preprocessing. Preprocessed message: " + summary)
        return summary


class HumorRule(Rule):
    name = "HumorRule"
    description = "Randomly makes the response contain a joke about the discussed topic"

    def preprocessing(self, message):
        print(self.name + ": Starting Preprocessing")

        if random.random() < 0.8:
            message = message + "\n" + "Append a joke about this topic at the end of your response."

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + message)
        return message


class StorytellingRule(Rule):
    name = "StorytellingRule"
    description = "Responds in a storytelling format to engage the user with narrative driven respones"

    def preprocessing(self, message):
        print(self.name + ": Starting Preprocessing")

        message = ("Once upon a time, this topic was to be discussed: " + "\n" + message +
                   "\n" + "What happened next? Tell me about it in a story telling style, like a folk tale.")

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + message)
        return message


class MakeMistakesRule(Rule):
    name = "MakeMistakesRule"
    description = "Asks another instance of ChatGPT to input mistakes into the message."

    def preprocessing(self, message):
        print(self.name + ": Starting Preprocessing")

        system_instruction = "You will put mistakes into the given user message and return that mistake ridden message."
        messages = [{"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}]
        response = request_system_response(messages)

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + response)
        return response
