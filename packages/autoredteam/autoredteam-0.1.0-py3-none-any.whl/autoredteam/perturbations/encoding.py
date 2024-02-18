from base64 import b64encode
from .base import Perturbation


class Base64(Perturbation):
    def __init__(self):
        super().__init__()
        self.name = "encoding.Base64"
        self.description = "Base64 perturbation"

    def perturb_prompt(self, prompt: str):
        b64_attempt = b64encode(prompt.encode())
        b64_attempt_string = str(b64_attempt, encoding="utf-8")
        return b64_attempt_string


class CharCode(Perturbation):
    def __init__(self):
        super().__init__()
        self.name = "encoding.CharCode"
        self.description = "CharCode perturbation"

    def perturb_prompt(self, prompt: str):
        cc_prompt = " ".join(list(map(str, map(ord, prompt))))
        return cc_prompt
