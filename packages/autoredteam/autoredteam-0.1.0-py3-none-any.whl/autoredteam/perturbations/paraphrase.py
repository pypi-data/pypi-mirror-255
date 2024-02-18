import contextlib

from .base import Perturbation
import garak.buffs.paraphrase as pp_buff

"""This module contains perturbations that generate paraphrases of a prompt or prompts in a test."""

# this = sys.modules[__name__]


class PegasusT5(Perturbation):
    """Perturbations that generate paraphrases of a prompt or prompts in a test."""

    name = "paraphrase.PegasusT5"
    description = "Paraphrase perturbation using PegasusT5"

    def __init__(self, num_paraphrases=6):
        self.num_paraphrases = num_paraphrases
        with contextlib.redirect_stdout(None):
            self.buff = pp_buff.PegasusT5()
        self.buff.num_return_sequences = self.num_paraphrases
        self.buff.num_beams = self.num_paraphrases
        self.uri = self.buff.uri
        self.__doc__ = self.buff.__doc__

        super().__init__()

    def perturb_prompt(self, prompt: str):
        return self.buff._get_response(prompt)


# # TODO: make Fast work
# buff_list = ["PegasusT5", "Fast"]
# for buff_name in buff_list:
#     buff_instance = getattr(buff_module, buff_name)()

#     setattr(
#         this,
#         buff_name,
#         type(
#             buff_name,
#             (Perturbation,),
#             {
#                 "__init__": local_constructor,
#                 "__doc__": buff_instance.__doc__,
#                 "buff": buff_instance,
#                 "uri": buff_instance.uri,
#                 "num_return_sequences": buff_instance.num_return_sequences,
#                 "num_beams": buff_instance.num_beams,
#                 "perturb_prompt": perturb_prompt
#             },
#         ),
#     )
