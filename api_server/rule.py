import random
from api_server.chatgpt_interface import request_system_response


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
        self.synonyms_percentage = 0.8

    def preprocessing(self, message):
        print(self.name + ": Starting Preprocessing")

        system_instruction = "Your goal is to replace some of the words in the message with its synonyms."
        messages = [{"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}]
        message = request_system_response(messages)

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + message)
        return message


class EmojiRule(Rule):
    name = "EmojiRule"
    description = "Inserts emojis to make responses more expressive and engaging"  # sentimental analysis, place some emojis, resond with alot emojis

    def preprocessing(self, message):
        print(self.name + ": Starting Preprocessing")

        system_instruction = "Your goal is to take the user's message and insert a lot of emojis. Do not respond to the message, only the modified user message. Then append in the users language 'Use a lot of emojis'"
        messages = [{"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}]
        message = request_system_response(messages)

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
