from garak.attempt import Attempt
import garak.detectors.base as garak_base_detectors


class Detector(garak_base_detectors.Detector):
    """Base Detector class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HFDetector(garak_base_detectors.HFDetector):
    """Base Detector class that works off of Hugging Face models."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StringDetector(garak_base_detectors.StringDetector):
    """Base Detector class that detects substring matches."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # case sensitive detection of string match
    def detect(self, attempt: Attempt, case_sensitive=True):
        return super().detect(attempt, case_sensitive=case_sensitive)


class StringAbsenceDetector(garak_base_detectors.StringDetector):
    """Base Detector class that detects absence of substrings."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # case sensitive detection of string match
    def detect(self, attempt: Attempt, case_sensitive=True):
        return [1 - n for n in super().detect(attempt, case_sensitive=case_sensitive)]


class TriggerListDetector(garak_base_detectors.TriggerListDetector):
    """Base Detector class that detects presence of trigger words."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TriggerListAbsenceDetector(garak_base_detectors.TriggerListDetector):
    """Base Detector class that detects absence of trigger words."""

    def detect(self, attempt: Attempt):
        return [1 - n for n in super().detect(attempt)]
