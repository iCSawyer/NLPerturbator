# reference: nlaugmenter/transformations/whitespace_perturbation/transformation.py

import random
from .my_util import *


def add_whitespace(word):
    assert len(word) >= 4

    perturbed_word = ""
    pos = random.randint(1, len(word) - 1)
    perturbed_word += word[:pos] + " " + word[pos:]

    return perturbed_word


def select_idx(token_list, prob):
    idx = []
    for i, token in enumerate(token_list):
        if judge_pos(token.pos_) == "word" and len(token.text) >= 4:
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
            new_prompt += add_whitespace(token.text)
        else:
            new_prompt += token.text

    return new_prompt
