import backoff
import os
import together
import openai

from garak import _config
from .base import Agent


# class TogetherAPI(Agent):
#     """
#     A generator that uses Together APIs to generate text.
#     """
#     # stream = True
#     generator_family_name = "Together"

#     def __init__(self, name, generations: int = 10):
#     # def __init__(self, name, config: AgentConfig=None):

#         if hasattr(_config.run, "seed"):
#             self.seed = _config.run.seed

#         # block_print()
#         super().__init__(name, generations)
#         # enable_print()
#         # super().__init__(name, config)
#         self.family = "Together"

#         together_token = os.getenv("TOGETHER_API_TOKEN", default=None)
#         if together_token is None:
#             raise ValueError(
#                 'Put the Together API token in the TOGETHER_API_TOKEN environment variable\n \
#                 e.g.: export TOGETHER_API_TOKEN="esecret_1234567890abcdefg"'
#             )
#         openai.api_key = together_token
#         openai.api_base = 'https://api.together.xyz'
#         self.agent = openai.ChatCompletion

#     @backoff.on_exception(
#         backoff.fibo,
#         (
#             openai.error.RateLimitError,
#             openai.error.ServiceUnavailableError,
#             openai.error.APIError,
#             openai.error.Timeout,
#             openai.error.APIConnectionError,
#         ),
#         max_value=70,
#     )
#     def _call_model(self, prompt):
#         response = self.agent.create(
#             model=self.name,
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=self.max_tokens,
#             temperature=self.temperature,
#             top_k=self.top_k,
#             presence_penalty=self.presence_penalty,
#             # stream=self.stream
#         )
#         return response.choices[0].message.content


class TogetherAPI(Agent):
    """
    A generator that uses Together APIs to generate text.
    """

    # stream = True
    generator_family_name = "Together"

    def __init__(self, name, generations: int = 10):
        # def __init__(self, name, config: AgentConfig=None):

        if hasattr(_config.run, "seed"):
            self.seed = _config.run.seed

        self.family = "Together"
        super().__init__(name, generations)

        together_token = os.getenv("TOGETHER_API_TOKEN", default=None)
        if together_token is None:
            raise ValueError(
                'Put the Together API token in the TOGETHER_API_TOKEN environment variable\n \
                e.g.: export TOGETHER_API_TOKEN="esecret_1234567890abcdefg"'
            )
        together.api_key = together_token
        self.agent = together.Complete

    @backoff.on_exception(
        backoff.fibo,
        (
            openai.error.RateLimitError,
            openai.error.ServiceUnavailableError,
            openai.error.APIError,
            openai.error.Timeout,
            openai.error.APIConnectionError,
        ),
        max_value=70,
    )
    def _call_model(self, prompt):
        try:
            response = self.agent.create(
                model=self.name,
                prompt=prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_k=self.top_k,
                # stream=self.stream
            )["output"]["choices"][0]["text"]
        except:
            response = ""
        return response


default_class = "TogetherAPI"
