import random
from .my_util import *


def select_idx(token_list, prob):
    idx = []
    for i, token in enumerate(token_list):
        if judge_pos(token.pos_) == "word":
            idx.append(i)
    idx.append(-1)  # start
    idx.append(-2)  # end
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
            new_prompt += " "
        new_prompt += token.text

    if -1 in perturbed_idx:
        new_prompt = " " + new_prompt
    if -2 in perturbed_idx:
        new_prompt += " "

    return new_prompt
