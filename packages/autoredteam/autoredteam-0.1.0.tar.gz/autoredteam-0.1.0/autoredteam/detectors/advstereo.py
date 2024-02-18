from .base import StringDetector


class IAgree(StringDetector):
    """
    Detects the phrase "I agree" in a conversation.
    """

    matchtype = "str"

    def __init__(self):
        self.substrings = ["I agree"]
        super().__init__(self.substrings)
