from collections import defaultdict
import copy
import json
from datetime import datetime
from tqdm import tqdm
import logging
from typing import Optional
from itertools import islice

from garak.generators.base import Generator
from garak.probes.base import Probe
from garak.detectors.base import Detector
from garak import _config


class Test:
    """This is a base test class that can be extended to create new tests."""

    active = True
    logged = False
    name = "base.Test"
    probe = Probe()
    detectors: Optional[list[Detector]] = None

    def __init__(self, name=None, prompts=None, detectors=None):
        if name is not None:
            self.name = name
        if prompts is not None:
            self.prompts = prompts
            self.probe.prompts = prompts
        if detectors:
            self.detectors = detectors
        pass

    def _execute_attempt(self, this_attempt, logged: bool = False):
        """
        Executes a single attempt, generating outputs and running detectors

        Attributes:
            this_attempt (Attempt): the attempt to execute
        """
        this_attempt.outputs = self.agent.generate(this_attempt.prompt)
        if logged:
            _config.transient.reportfile.write(
                json.dumps(this_attempt.as_dict()) + "\n"
            )
        return copy.deepcopy(this_attempt)

    def generate(self, agent: Generator, logged: bool = False):
        """
        Generates outputs for a given agent

        Attributes:
            agent (Agent): the agent to generate outputs
        """
        self.agent = agent

        # build list of attempts
        attempts_todo = []
        for seq, prompt in enumerate(self.prompts):
            attempts_todo.append(
                self.probe._mint_attempt(prompt, seq)
            )

        # iterate through attempts
        attempts_completed = []

        attempt_iterator = tqdm(attempts_todo, position=0, leave=False)
        attempt_iterator.set_description("Test " + self.name)
        for this_attempt in attempt_iterator:
            attempts_completed.append(self._execute_attempt(this_attempt, logged))

        logging.debug(
            "probe return: %s with %s attempts", self, len(attempts_completed)
        )

        self.attempt_results = attempts_completed

    def evaluate(self, logged: bool = False):
        """
        Runs detectors on the generated outputs
        """
        eval_outputs, eval_results = [], defaultdict(list)
        first_detector = True
        for d in self.detectors:
            detname = ".".join(d.detectorname.split(".")[-2:])
            logging.debug("harness: run detector %s", detname)
            attempt_iterator = tqdm(self.attempt_results, position=0, leave=False)
            for attempt in attempt_iterator:
                attempt.detector_results[detname] = d.detect(attempt)

                if first_detector:
                    eval_outputs += attempt.outputs
                eval_results[detname] += attempt.detector_results[detname]
            first_detector = False

        for attempt in self.attempt_results:
            attempt.status = 2
            if logged:
                _config.transient.reportfile.write(json.dumps(attempt.as_dict()) + "\n")

        if len(self.attempt_results) == 0:
            logging.warning("Zero attempt results! Nothing to report.")

        self.eval_outputs = eval_outputs
        self.eval_results = eval_results

    def summarize(self, threshold: float = 0.5, logged: bool = False):
        """
        Summarizes the results of the test

        Attributes:
            threshold (float): the threshold for a detector to pass
        """
        eval_summary = defaultdict(dict)
        for detectorname, detector_results in self.eval_results.items():
            eval_summary[detectorname]["passed"] = sum(
                [1 for x in detector_results if x < threshold]
            )
            eval_summary[detectorname]["total"] = len(detector_results)
            eval_summary[detectorname]["pass_rate"] = round(
                eval_summary[detectorname]["passed"]
                / eval_summary[detectorname]["total"]
                * 100,
                1,
            )
        self.eval_summary = eval_summary

        for k, v in self.eval_summary.items():
            if logged:
                _config.transient.reportfile.write(
                    json.dumps(
                        {
                            "entry_type": "eval",
                            "test": self.name,
                            "detector": k,
                            "passed": v["passed"],
                            "total": v["total"],
                        }
                    )
                    + "\n"
                )
            print(
                f"{self.name:<50} {k:>50}: {v['passed']:>4}/{v['total']:>4} ({v['pass_rate']:>6}%) passed"
            )

        # record the hits if logging is enabled
        if logged:
            for d in self.detectors:
                detname = ".".join(d.detectorname.split(".")[-2:])
                for attempt in self.attempt_results:
                    for idx, score in enumerate(attempt.detector_results[detname]):
                        if score > threshold:  # if we don't pass
                            if not _config.transient.hitlogfile:
                                hitlog_filename = f"{_config.reporting.report_dir}/autoredteam.{_config.transient.run_id}.hitlog.jsonl"
                                logging.info("hit log in %s", hitlog_filename)
                                _config.transient.hitlogfile = open(
                                    hitlog_filename,
                                    "w",
                                    buffering=1,
                                    encoding="utf-8",
                                )

                            trigger = None
                            if "trigger" in attempt.notes:
                                trigger = attempt.notes["trigger"]
                            _config.transient.hitlogfile.write(
                                json.dumps(
                                    {
                                        "goal": attempt.goal,
                                        "prompt": attempt.prompt,
                                        "output": attempt.outputs[idx],
                                        "trigger": trigger,
                                        "score": score,
                                        "run_id": str(_config.transient.run_id),
                                        "attempt_id": str(attempt.uuid),
                                        "attempt_seq": attempt.seq,
                                        "attempt_idx": idx,
                                        "test": self.name,
                                        "detector": detname,
                                        "generations_per_prompt": len(
                                            attempt.detector_results[detname]
                                        ),
                                    }
                                )
                                + "\n"
                            )

    def run(
        self, agent: Generator, detection_threshold: float = 0.5, logged: bool = False
    ):
        """
        Runs the test

        Attributes:
            agent (Agent): the agent to run the test on
            detection_threshold (float): the threshold for a detector to pass
        """
        # for dan prompts, use generator name
        if "dan." in self.name:
            self.prompts = [prompt.format(generator=agent) for prompt in self.probe.prompts]
        
        self.generate(agent, logged=logged)
        self.evaluate(logged=logged)
        self.summarize(threshold=detection_threshold, logged=logged)

    def export(self, path=None, subset=None, threshold=0.5, mode="a"):
        """
        Exports the results of the test

        Attributes:
            path (str): the path to export the results to, defaults to an auto-assigned filename
            subset (str): the subset of results to export, defaults to all
            threshold (float): the threshold for a detector to pass, defaults to 0.5
        """
        if path is None:
            if subset == "hits":
                level = "hitlog"
            else:
                level = "report"
            path = f"{type(self).__name__}_{int(datetime.utcnow().timestamp())}.{level}.jsonl"

        if subset == "hits":
            for d in self.detectors:
                detname = ".".join(d.detectorname.split(".")[-2:])
                for attempt in self.attempt_results:
                    for idx, score in enumerate(attempt.detector_results[detname]):
                        if score > threshold:  # if we don't pass
                            f = open(path, mode, buffering=1, encoding="utf-8")

                            trigger = None
                            if "triggers" in attempt.notes:
                                trigger = attempt.notes["triggers"]
                            f.write(
                                json.dumps(
                                    {
                                        "goal": attempt.goal,
                                        "prompt": attempt.prompt,
                                        "output": attempt.outputs[idx],
                                        "trigger": trigger,
                                        "score": score,
                                        "run_id": str(_config.transient.run_id),
                                        "attempt_id": str(attempt.uuid),
                                        "attempt_seq": attempt.seq,
                                        "attempt_idx": idx,
                                        "test": self.name,
                                        "detector": detname,
                                        "generations_per_prompt": len(
                                            attempt.detector_results[detname]
                                        ),
                                    }
                                )
                                + "\n"
                            )
        else:
            with open(path, mode) as f:
                # export attempt results
                for attempt in self.attempt_results:
                    f.write(json.dumps(attempt.as_dict()) + "\n")

                # export eval summary
                for det in self.eval_summary.keys():
                    f.write(
                        json.dumps(
                            {
                                "entry_type": "eval",
                                "test": type(self).__name__,
                                "detector": det,
                                "passed": self.eval_summary[det]["passed"],
                                "total": self.eval_summary[det]["total"],
                            }
                        )
                        + "\n"
                    )
            logging.info("exported results to %s", path)


class PairwiseTest(Test):
    """
    Generic test class that compares responses pairwise.
    """

    def __init__(self, step=200, probe=None, detectors=None):
        """
        Args:
            step (int): the step size for pairwise comparison, i.e. compare attempts (0, step), (1, step+1), etc.
            probe (Probe): the probe to use
            detectors (list[Detector]): the detectors to use
        """
        self.step = step
        super().__init__(probe, detectors)

    def evaluate(self, logged: bool = False):
        """
        Runs detectors on the generated outputs pairwise
        """
        eval_outputs, eval_results = [], defaultdict(list)
        first_detector = True
        for d in self.detectors:
            detname = ".".join(d.detectorname.split(".")[-2:])
            logging.debug("harness: run detector %s", detname)
            attempt_iterator = iter(self.attempt_results)
            first_half = tqdm(islice(attempt_iterator, 0, self.step), leave=False)
            first_half.set_description("Detector " + detname)

            # only score attempts in first half
            for attempt1 in first_half:
                attempt1.detector_results[detname] = d.detect(
                    attempt1, self.attempt_results[attempt1.seq + self.step]
                )
                # placeholder for second half samples
                self.attempt_results[attempt1.seq + self.step].detector_results[
                    detname
                ] = [0 for _ in attempt1.detector_results[detname]]

                if first_detector:
                    eval_outputs += attempt1.outputs
                eval_results[detname] += attempt1.detector_results[detname]

            first_detector = False

        for attempt in self.attempt_results:
            attempt.status = 2
            if logged:
                _config.transient.reportfile.write(json.dumps(attempt.as_dict()) + "\n")

        if len(self.attempt_results) == 0:
            logging.warning("Zero attempt results! Nothing to report.")

        self.eval_outputs = eval_outputs
        self.eval_results = eval_results


class TriggerTest(Test):
    def evaluate(self, logged: bool = False):
        # append triggers
        for i, attempt in enumerate(self.attempt_results):
            attempt.notes["triggers"] = [self.probe.triggers[i]]

        super().evaluate(logged=logged)
