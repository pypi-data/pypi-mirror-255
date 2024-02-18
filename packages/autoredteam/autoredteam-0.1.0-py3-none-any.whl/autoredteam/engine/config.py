from pydantic import BaseModel
from typing import Optional


class AgentConfig(BaseModel):
    family: str
    name: str
    endpoint: Optional[str]
    max_tokens: int = 150
    temperature: Optional[float]
    top_k: Optional[float]
    seed: Optional[int]
    presence_penalty: Optional[float]
    supports_multiple_generations: Optional[bool]


def _get_default_agent_config(family, name):
    return AgentConfig(
        family=family,
        name=name,
        endpoint=name,
        max_tokens=150,
        temperature=1,
        top_k=5,
        seed=9,
        presence_penalty=0,
        supports_multiple_generations=False,
    )


# class TestParams(TypedDict, total=False):
#     name: Optional[str]
#     params: Optional[dict]

# class TestConfig(BaseModel, total=False):
#     spec: Optional[str]
#     params: Optional[List[TestParams]]

# # class BuffParams(TypedDict): # TODO: add buffs
# #     name: str
# #     params: dict

# # class BuffConfig(BaseModel):
# #     spec: str
# #     params: List[BuffParams] = None

# class SystemConfig(BaseModel, total=False):
#     generations: Optional[int]
#     prompt_parallelism: Optional[bool]
#     Test_parallelism: bool
#     ncores: Optional[int]

# class EvalConfig:
#     generator: AgentConfig
#     tests: Optional[TestConfig]
#     # buffs: Optional[List[BuffConfig]]
#     system: Optional[SystemConfig]

#     def __init__(self, config_file=None):

#         # load config file and exit function if no config file is provided
#         if config_file:
#             self.config_file = config_file
#             self.config = self.load(config_file)
#         # if no config file is provided, use default config
#         else:
#             self.system = SystemConfig(generations=1, prompt_parallelism=False, Test_parallelism=False, ncores=1)
#             self.Tests = TestConfig(spec='all')

#     def load(self):
#         with open(self.config_file, 'r') as f:
#             self.config = yaml.safe_load(f)
#         return self
