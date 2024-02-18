import openai
import os
import backoff
import contextlib

from garak.generators.base import Generator
from garak import _config
from ..engine.config import _get_default_agent_config


class Agent(Generator):
    """
    Generic Agent class, takes after the Generator class in garak
    """

    family = ""

    def __init__(self, name, generations: int = 10):
        # def __init__(self, name, config: AgentConfig=None):
        """
        Initializes the Agent class, given a `name`.
        """
        print(f"Loading {self.family} Agent: {name}")
        with contextlib.redirect_stdout(None):
            super().__init__(name, generations)

        # if config is None:
        config = _get_default_agent_config(family="", name=self.name)
        for field in [
            "endpoint",
            "max_tokens",
            "presence_penalty",
            "temperature",
            "top_k",
            "seed",
            "presence_penalty",
            "supports_multiple_generations",
        ]:
            if hasattr(config, field):
                setattr(self, field, getattr(config, field))


# TODO: make this work
class AgentAPI(Agent):
    """
    Generic class for creating an Agent based on OpenAI style base URL, name, and API token.
    """

    stream = True

    def __init__(self, base_url, name, token=None, family=None, generations: int = 10):
        # def __init__(self, name, config: AgentConfig=None):

        if hasattr(_config.run, "seed"):
            self.seed = _config.run.seed

        # block_print()
        super().__init__(name, generations)
        # enable_print()
        # super().__init__(name, config)
        if family is not None:
            self.family = family
        else:
            self.family = "APIAgent"

        if token is None:
            rest_token = os.getenv("REST_API_TOKEN", default=None)
            if rest_token is None:
                raise ValueError(
                    'Supply an API token as REST_API_TOKEN, e.g.: export REST_API_TOKEN="abc123xyz".\n \
                        Alternatively, supply the API token as argument `token`'
                )
        else:
            rest_token = token
        openai.api_key = rest_token
        openai.api_base = base_url
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
