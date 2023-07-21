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
