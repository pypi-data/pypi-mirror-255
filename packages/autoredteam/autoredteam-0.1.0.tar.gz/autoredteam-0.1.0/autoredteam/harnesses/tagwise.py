"""
This module defines a harness that runs all tests that contain a given tag.
"""
import importlib
from ..utils import list_all_tests
from .base import Harness


class TagHarness(Harness):
    """
    Create a harness on all tests that contains the given tag(s).
    """

    def __init__(self, agent, tags, *args):
        """
        Args:
            agent (Agent): The agent to run the tests on.
            tags (list): The tags to filter tests by.
        """

        # grab all tests from the module
        self.tags = tags
        self.test_instances = []

        for module, module_tests in list_all_tests().items():
            module_instance = importlib.import_module(f"autoredteam.tests.{module}")
            for test in module_tests:
                test_instance = getattr(module_instance, test)()
                if any(
                    tag in ti_tags for tag in tags for ti_tags in test_instance.tags
                ):
                    self.test_instances.append(test_instance)
        super().__init__(agent=agent, *args)

    def run(self, logged: bool = False):
        print(f"Running harness for tags {self.tags}")
        return super().run(logged=logged)
