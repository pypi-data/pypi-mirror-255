from string import Template
from lmoe.api.base_expert import BaseExpert

import ollama

_PROMPT_TEMPLATE = Template(
    """
===user-context===
$user_context
===user-context===
===user-query===
$user_query
===user-query===
-response-
"""
)


class Code(BaseExpert):

    @classmethod
    def name(cls):
        return "CODE"

    @classmethod
    def has_modelfile(cls):
        return True

    def description(self):
        return "A model specifically for generating code. It is expected that this is an instruction-tuned model rather than a 'fill in the middle' model, meaning that a user will describe a coding task or coding question in natural language rather than supplying code and expecting the following code to be generated."

    def examples(self):
        return [
            "write a python script which determines the largest directory in my home environment",
        ]

    def generate(self, user_context, user_query):
        stream = ollama.generate(
            model="lmoe_code",
            prompt=_PROMPT_TEMPLATE.substitute(
                user_context=user_context, user_query=user_query
            ),
            stream=True,
        )
        for chunk in stream:
            if chunk["response"] or not chunk["done"]:
                print(chunk["response"], end="", flush=True)
        print("")
