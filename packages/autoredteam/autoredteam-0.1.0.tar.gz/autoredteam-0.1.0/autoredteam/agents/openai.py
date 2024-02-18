import contextlib
import os
from garak.generators.openai import OpenAIGenerator
from ..engine.config import _get_default_agent_config


class OpenaiAgent(OpenAIGenerator):
    def __init__(self, name, generations: int = 10):
        # def __init__(self, name, generations: int = 10, config: AgentConfig=None):

        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_TOKEN")

        self.family = "OpenAI"
        print(f"Loading {self.family} Agent: {name}")
        with contextlib.redirect_stdout(None):
            super().__init__(name, generations)
        # if config is None:
        config = _get_default_agent_config(family="", name=self.name)
        for field in [
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


default_class = "OpenaiAgent"
