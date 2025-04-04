# reference: nlaugmenter/transformations/whitespace_perturbation/transformation.py

import random
from .my_util import *


def repeat(word):
    perturbed_word = ""

    pos = random.randint(0, len(word) - 1)
    perturbed_word += word[:pos] + word[pos] + word[pos:]

    return perturbed_word


def select_idx(token_list, prob):

    idx = []
    for i, token in enumerate(token_list):
        if judge_real_word(token.pos_) == "word":
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
            new_prompt += repeat(token.text)
        else:
            new_prompt += token.text

    return new_prompt
