"""
Harnesses for each dimension of trust in the Vijil framework.
"""


from .tagwise import TagHarness

all_dimensions = [
    "Security",
    "Toxicity",
    "Ethics",
    "Hallucination",
    "Stereotype",
    "Fairness",
]


# for dimension in all_dimensions:
#     def init_func(self, agent, **kwargs):
#         super(self.__class__, self).__init__(agent, tags=[f"vijil:{dimension}"], **kwargs)

#     setattr(
#         sys.modules[__name__],
#         f"{dimension}Harness",
#         type(
#             f"{dimension}Harness",
#             (TagHarness,),
#             {
#                 '__init__': init_func,
#                 '__doc__': f'Create a harness on all {dimension.lower()} specific tests.'
#             }
#         )
#     )


class SecurityHarness(TagHarness):
    def __init__(self, agent, *args):
        super().__init__(agent=agent, tags=["vijil:Security"], *args)


class ToxicityHarness(TagHarness):
    def __init__(self, agent, *args):
        super().__init__(agent=agent, tags=["vijil:Toxicity"], *args)


class EthicsHarness(TagHarness):
    def __init__(self, agent, *args):
        super().__init__(agent=agent, tags=["vijil:Ethics"], *args)


class HallucinationHarness(TagHarness):
    def __init__(self, agent, *args):
        super().__init__(agent=agent, tags=["vijil:Hallucination"], *args)


class StereotypeHarness(TagHarness):
    def __init__(self, agent, *args):
        super().__init__(agent=agent, tags=["vijil:Stereotype"], *args)


class PrivacyHarness(TagHarness):
    def __init__(self, agent, *args):
        super().__init__(agent=agent, tags=["vijil:Privacy"], *args)


class FairnessHarness(TagHarness):
    def __init__(self, agent, *args):
        super().__init__(agent=agent, tags=["vijil:Fairness"], *args)


class RobustnessHarness(TagHarness):
    def __init__(self, agent, *args):
        super().__init__(agent=agent, tags=["vijil:Robustness"], *args)
