# makes all the functions in the module available to the autoredteam.generators package

import contextlib
from garak.generators.octo import OctoGenerator, InferenceEndpoint
from ..engine.config import _get_default_agent_config

# from ..engine.config import AgentConfig, _get_default_agent_config


class OctoAPI(OctoGenerator):
    def __init__(self, name, generations: int = 10):
        # def __init__(self, name, generations: int = 10, config: AgentConfig=None):

        self.family = "OctoAI"
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


class OctoEndpoint(InferenceEndpoint):
    def __init__(self, name, generations: int = 10):
        # def __init__(self, name, generations: int = 10, config: AgentConfig=None):

        self.family = "OctoAI"
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


# more stable option is enabled by default
default_class = "OctoAPI"
