import importlib
import os

from garak.probes.atkgen import Tox
from garak import _config
from .base import Test

# Instantiate the probe
_config.system.verbose = 1
_config.system.parallel_requests = False
probe_instance = Tox()

# instantiate the detectors
probe_detectors = []
for detector in probe_instance.recommended_detector:
    det_module_name, detector_name = detector.split(".")
    detector_module = importlib.import_module(f"garak.detectors.{det_module_name}")
    probe_detectors.append(getattr(detector_module, detector_name)())


class ToxicityAttack(Test):
    probe = probe_instance
    __doc__ = probe_instance.__doc__
    name = "atkgen.ToxicityAttack"
    description = probe_instance.description
    goal = probe_instance.goal
    uri = probe_instance.uri
    detectors = probe_detectors
    tags = ["vijil:Toxicity", "source:garak"] + probe_instance.tags

    def generate(self, agent, logged=False):
        """
        Generate attempts by calling an agent.
        """
        if not logged:  # save atkgen logs in a temporary file
            _config.transient.reportfile = open(
                "temp.jsonl", "w", buffering=1, encoding="utf-8"
            )
        self.attempt_results = self.probe.probe(agent)
        if not logged:  # delete temp file after generation is done
            os.remove("temp.jsonl")


__all__ = ["ToxicityAttack"]
