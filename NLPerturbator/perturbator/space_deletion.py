import random
from .my_util import *


def select_idx(token_list, prob):

    idx = []
    for i, token in enumerate(token_list):
        if judge_pos(token.pos_) != "word" and not token.text.isalpha():
            idx.append(i)

    idx = list(set(idx))
    times = max(1, int(len(idx) * prob))
    idx = random.sample(idx, times) if len(idx) > 0 else []
    return idx


def perturbate(prompt, prob):

    new_prompt = ""

    token_list = pro_tokenize(prompt)
    perturbed_idx = select_idx(token_list, prob)

    for i, token in enumerate(token_list):
        if i not in perturbed_idx:
            new_prompt += token.text

    return new_prompt
