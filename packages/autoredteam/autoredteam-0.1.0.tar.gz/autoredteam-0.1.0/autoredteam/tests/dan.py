"""
A model provider typically prepends a system prompt that stipulates organizational policies (safety guardrails, content moderation filters, etc.) to every user prompt. A Do-Anything-Now (DAN[^1]) attack is a user prompt designed to get the model to ignore these guardrails. Falcon-40B-Instruct exhibits high susceptibility to DAN attacks.

Vijil covers 15 DAN attack scenarios through its tests.

* AntiDAN
* AutoDAN
* ChatGPT Developer Mode + RANTI
* ChatGPT Developer Mode v2
* ChatGPT Markdown Image Unlocker
* DAN Jailbreak
* DUDE
* DAN 6.0
* DAN 6.2
* DAN 7.0
* DAN 8.0
* DAN 9.0
* DAN 10.0
* DAN 11.0
* STAN

[^1]: [ChatGPT is easily abused, or let's talk about DAN](https://adguard.com/en/blog/chatgpt-dan-prompt-abuse.html)
"""

import importlib
import sys
from .base import Test
from ..utils import local_constructor, GARAK_PROBE_MODULES

# TODO: make it work by adding prompts to dan probe inits in base garak
# import probe and instantiate
module_name = "dan"
probe_module = importlib.import_module(f"garak.probes.{module_name}")

# get all probes under probe module
all_probes = GARAK_PROBE_MODULES[module_name]

# create Test classes for all probes
this = sys.modules[__name__]

for probe_name in all_probes:
    # import probe and instantiate
    probe_instance = getattr(probe_module, probe_name)()

    # import detectors and instantiate
    probe_detectors = []
    for detector in probe_instance.recommended_detector:
        det_module_name, detector_name = detector.split(".")
        detector_module = importlib.import_module(f"garak.detectors.{det_module_name}")
        probe_detectors.append(getattr(detector_module, detector_name)())

    # define test class based on probe
    classname = probe_name
    setattr(
        this,
        classname,
        type(
            classname,
            (Test,),
            {
                "__init__": local_constructor,
                "__doc__": probe_instance.__doc__,
                "probe": probe_instance,
                "prompts": probe_instance.prompts,
                "detectors": probe_detectors,
                "uri": probe_instance.uri,
                "name": f"{module_name}.{probe_name}",
                "description": probe_instance.description,
                "tags": ["vijil:Security", "source:garak"] + probe_instance.tags,
                "goal": probe_instance.goal,
            },
        ),
    )
