"""Module: rule_based_processing

This module contains classes representing different rules for preprocessing user messages before
passing them to a ChatGPT-based response system.
Each rule defines specific behaviors such as replacing words with synonyms,
adding emojis, summarizing, introducing humor, storytelling, and introducing mistakes.

Classes:
    Rule: Base class for all rule types.
    SynonymRule: Rule that replaces words with synonyms.
    EmojiRule: Rule that inserts emojis into messages.
    SummarizeRule: Rule that summarizes the user message.
    HumorRule: Rule that adds humor to responses.
    StorytellingRule: Rule that responds in a storytelling format.
    MakeMistakesRule: Rule that introduces mistakes into messages.

Usage:
    Instantiate rule classes and use their `preprocessing` method to process user messages before
    sending to a ChatGPT-based response system.

Example:
    synonym_rule = SynonymRule()
    preprocessed_msg = synonym_rule.preprocessing(user_msg)
    # Send preprocessed_msg to the response system

Author: Marlon Beck
Date: 17/08/2023
"""

import random

from api_server.chatgpt_interface import request_system_response


class Rule:
    """Base class for all rule types."""
    name = "Rule"
    description = "Base Rule"

    def preprocessing(self, message):
        """
        Preprocesses the user message according to the rule.

        Args:
            message (str): The user's message.

        Returns:
            str: The preprocessed message.
        """
        return message

    def postprocessing(self, response):
        """
        Performs postprocessing on the generated response.

        Args:
            response (str): The generated response.

        Returns:
            str: The postprocessed response.
        """
        return response


class SynonymRule(Rule):
    """Rule that replaces words with synonyms."""
    name = "SynonymRule"
    description = "Replaces words with words"

    def __init__(self):
        self.synonyms_percentage = 0.8

    def preprocessing(self, message):
        """
        Preprocesses the user message by replacing words with synonyms.

        Args:
            message (str): The user's message.

        Returns:
            str: The preprocessed message.
        """
        print(self.name + ": Starting Preprocessing")

        system_instruction = ("Your goal is to replace some of the words in the message with its "
                              "synonyms.")
        messages = [{"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}]
        message = request_system_response(messages)

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + message)
        return message


class EmojiRule(Rule):
    """Rule that inserts emojis into messages."""
    name = "EmojiRule"
    description = "Inserts emojis to make responses more expressive and engaging"

    def preprocessing(self, message):
        """
        Preprocesses the user message by inserting emojis.

        Args:
            message (str): The user's message.

        Returns:
            str: The preprocessed message.
        """
        print(self.name + ": Starting Preprocessing")

        system_instruction = ("Your goal is to insert a lot of emojis into the user's message. Do "
                              "not respond to the message, only modify the user message. Then "
                              "append in the users language 'Use a lot of emojis'")
        messages = [{"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}]
        message = request_system_response(messages)

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + message)
        return message


class SummarizeRule(Rule):
    """Rule that summarizes the user message."""
    name = "SummarizeRule"
    description = "Summarizes the user message and sends it to ChatGPT"

    def preprocessing(self, message):
        """
        Preprocesses the user message by summarizing it.

        Args:
            message (str): The user's message.

        Returns:
            str: The summarized message.
        """
        print(self.name + ": Starting Preprocessing")

        system_instruction = ("Your goal is to summarize the text the user provides. Do not send "
                              "any other response, only the summarized text.")
        messages = [{"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}]
        # completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        # summary = completion.choices[0].message.content
        summary = request_system_response(messages)
        print(self.name + ": Finished Preprocessing. Preprocessed message: " + summary)
        return summary


class HumorRule(Rule):
    """Rule that adds humor to responses."""
    name = "HumorRule"
    description = "Randomly makes the response contain a joke about the discussed topic"

    def preprocessing(self, message):
        """
        Preprocesses the user message by potentially adding a joke.

        Args:
            message (str): The user's message.

        Returns:
            str: The preprocessed message.
        """
        print(self.name + ": Starting Preprocessing")

        if random.random() < 0.8:
            message = message + "\n" + "Append a joke about this topic at the end of your response."

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + message)
        return message


class StorytellingRule(Rule):
    """Rule that responds in a storytelling format."""
    name = "StorytellingRule"
    description = ("Responds in a storytelling format to engage the user with narrative driven "
                   "responses")

    def preprocessing(self, message):
        """
        Preprocesses the user message by framing it in a storytelling format.

        Args:
            message (str): The user's message.

        Returns:
            str: The preprocessed message.
        """
        print(self.name + ": Starting Preprocessing")

        message = (
                "Once upon a time, this topic was to be discussed: " + "\n" + message + "\n"
                + "What happened next? Tell me about it in a story telling style, like a folk "
                  "tale.")

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + message)
        return message


class MakeMistakesRule(Rule):
    """Rule that introduces mistakes into messages."""
    name = "MakeMistakesRule"
    description = "Asks another instance of ChatGPT to input mistakes into the message."

    def preprocessing(self, message):
        """
        Preprocesses the user message by adding mistakes.

        Args:
            message (str): The user's message.

        Returns:
            str: The preprocessed message with mistakes.
        """
        print(self.name + ": Starting Preprocessing")

        system_instruction = ("You will put mistakes into the given user message and return that "
                              "mistake ridden message.")
        messages = [{"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}]
        response = request_system_response(messages)

        print(self.name + ": Finished Preprocessing. Preprocessed message: " + response)
        return response
