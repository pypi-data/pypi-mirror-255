"""
Harness for the OWASP Top 10 LLM Vulnerabilities.
"""

from .tagwise import TagHarness


class LLMTop10Harness(TagHarness):
    def __init__(self, agent, *args):
        super().__init__(agent, tags=["owasp"], *args)
