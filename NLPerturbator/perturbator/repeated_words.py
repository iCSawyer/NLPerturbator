# reference: nlaugmenter/transformations/whitespace_perturbation/transformation.py

import random
from .my_util import *


def select_idx(token_list, prob):

    idx = []
    for i, token in enumerate(token_list):
        if (
            judge_pos(token.pos_) == "word"
            and len(token.text) <= 3
            and token.text.isalpha()
        ):
            idx.append(i)

    idx = list(set(idx))
    times = max(1, int(len(idx) * prob))
    idx = random.sample(idx, times)
    return idx


def perturbate(prompt, prob):

    new_prompt = ""

    token_list = pro_tokenize(prompt)
    perturbed_idx = select_idx(token_list, prob)

    for i, token in enumerate(token_list):
        if i in perturbed_idx:
            new_prompt += token.text + " " + token.text
        else:
            new_prompt += token.text

    return new_prompt
