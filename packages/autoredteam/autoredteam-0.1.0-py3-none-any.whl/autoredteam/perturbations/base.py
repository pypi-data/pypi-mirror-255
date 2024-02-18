"""
Perturbations provide templates to modify prompts with.
They may be as simple as adding a prefix or suffix to a prompt, or changing the case,
or they may be more complex, such as generating a paraphrase or performing adversarial attacks.
"""

from typing import Optional

from garak.buffs.base import Buff


class Perturbation:
    """Base class for perturbations."""

    name: Optional[str]
    description: Optional[str]
    buff: Optional[Buff]

    def __init__(self, buff: Optional[Buff] = None):
        """Initialize a perturbation."""
        if buff:
            self.buff = buff
        pass

    def perturb_prompt(self, prompt: str):
        """Perturb a prompt."""
        return prompt

    # def perturb_probe(self, test: Test):
    #     """Perturb a probe."""
    #     return [self.perturb_prompt(p) for p in test.probe.prompts]
