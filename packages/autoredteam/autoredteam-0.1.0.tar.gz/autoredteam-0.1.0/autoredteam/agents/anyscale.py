import backoff
import os
import openai

# from .base import AgentAPI
from .base import Agent

# from ..engine.config import AgentConfig
from garak import _config


# class AnyscaleAPI(AgentAPI):
#     generator_family_name = "Anyscale"

#     def __init__(self, name, generations: int = 10):
#         anyscale_token = os.getenv("ANYSCALE_API_TOKEN", default=None)
#         if anyscale_token is None:
#             raise ValueError(
#                 'Put the Anyscale API token in the ANYSCALE_API_TOKEN environment variable\n \
#                 e.g.: export ANYSCALE_API_TOKEN="esecret_1234567890abcdefg"'
#             )

#         super().__init__(
#             base_url='https://api.endpoints.anyscale.com/v1/',
#             name=name,
#             token=anyscale_token,
#             family="Anyscale",
#             generations=generations
#         )


class AnyscaleAPI(Agent):
    """
    A generator that uses Anyscale APIs to generate text.
    """

    stream = True
    generator_family_name = "Anyscale"

    def __init__(self, name, generations: int = 10):
        # def __init__(self, name, config: AgentConfig=None):

        if hasattr(_config.run, "seed"):
            self.seed = _config.run.seed

        self.family = "Anyscale"
        super().__init__(name, generations)
        # super().__init__(name, config)

        self.token = os.getenv("ANYSCALE_API_TOKEN", default=None)
        if self.token is None:
            raise ValueError(
                'Put the Anyscale API token in the ANYSCALE_API_TOKEN environment variable\n \
                e.g.: export ANYSCALE_API_TOKEN="esecret_1234567890abcdefg"'
            )
        # openai.api_key = anyscale_token
        # openai.api_base = "https://api.endpoints.anyscale.com/v1"
        self.agent = openai.ChatCompletion

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
        response = self.agent.create(
            api_key=self.token,
            api_base="https://api.endpoints.anyscale.com/v1",
            model=self.name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_k=self.top_k,
            presence_penalty=self.presence_penalty,
            # stream=self.stream
        )
        return response.choices[0].message.content


default_class = "AnyscaleAPI"
