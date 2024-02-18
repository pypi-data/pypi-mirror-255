"""
This module defines a harness that runs all tests from a given module.
"""
import importlib
from ..utils import list_all_tests
from .base import Harness


class ModuleHarness(Harness):
    """
    Create a harness on all tests from one module.
    """

    def __init__(self, agent, module, *args):
        """
        Args:
            agent (Agent): The agent to run the tests on.
            module (str): The module to run tests from.
        """

        # grab all tests from the module
        test_module = importlib.import_module(f"autoredteam.tests.{module}")
        all_tests = list_all_tests(modules=[module])
        self.test_instances = [
            getattr(test_module, test)() for test in all_tests[module]
        ]

        super().__init__(agent=agent, *args)

    def run(self, logged: bool = False):
        print(
            f"Running test harness for module {self.test_instances[0].__class__.__module__.split('.')[-1]}"
        )
        return super().run(logged=logged)
