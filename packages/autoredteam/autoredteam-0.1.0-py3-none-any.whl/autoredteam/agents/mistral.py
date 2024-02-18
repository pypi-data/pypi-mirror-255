import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from garak import _config
from .base import Agent


class MistralAPI(Agent):
    """
    A generator that uses Mistral APIs to generate text.
    """

    # stream = True
    generator_family_name = "Mistral"

    def __init__(self, name, generations: int = 10):
        # def __init__(self, name, config: AgentConfig=None):

        if hasattr(_config.run, "seed"):
            self.seed = _config.run.seed

        self.family = "Mistral"
        super().__init__(name, generations)
        # super().__init__(name, config)

        mistral_token = os.getenv("MISTRAL_API_TOKEN", default=None)
        if mistral_token is None:
            raise ValueError(
                'Put the Mistral API token in the MISTRAL_API_TOKEN environment variable\n \
                e.g.: export MISTRAL_API_TOKEN="esecret_1234567890abcdefg"'
            )
        self.agent = MistralClient(api_key=mistral_token)

    def _call_model(self, prompt):
        response = self.agent.chat(
            model=self.name,
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content=prompt),
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            # stream=self.stream
        )

        # TODO: add streaming: https://docs.mistral.ai/platform/client/
        return response.choices[0].message.content


default_class = "MistralAPI"
