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

    def __init__(self, synonyms):
        self.synonyms = synonyms

    def preprocessing(self, message):
        for word, synonym in self.synonyms.items():
            message = message.replace(word, synonym)
        return message

    def postprocessing(self, response):
        for word, synonym in self.synonyms.items():
            response = response.replace(word, synonym)
        return response
