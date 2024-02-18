from .base import Perturbation

"""This module contains perturbations that change the case of a prompt or prompts in a test."""


class LowerCase(Perturbation):
    name = "casechange.LowerCase"
    description = "Change the case of the string to lowercase"

    def __init__(self):
        super().__init__()

    def perturb_prompt(self, prompt: str):
        return prompt.lower()


class UpperCase(Perturbation):
    name = "casechange.UpperCase"
    description = "Change the case of the string to UPPERCASE"

    def perturb_prompt(self, prompt: str):
        return prompt.upper()


class CaseSwitch(Perturbation):
    name = "casechange.CaseSwitch"
    description = "Randomly switch cases inside the string"

    def __init__(self, p=0.1, seed=42):
        self.case_switch_prob = p
        self.seed = seed
        super().__init__()

    def perturb_prompt(self, prompt: str):
        import random

        random.seed(self.seed)
        return "".join(
            [
                c.upper() if random.random() < self.case_switch_prob else c.lower()
                for c in prompt
            ]
        )
