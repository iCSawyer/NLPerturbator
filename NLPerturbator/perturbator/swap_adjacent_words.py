import random
from .my_util import *
from nltk.corpus import wordnet


def select_idx(token_list, prob):
    idx = []
    for i in range(len(token_list) - 2):
        token1 = token_list[i]
        token2 = token_list[i + 2]
        if (
            token1.text.isalpha()
            and token2.text.isalpha()
            and token1.text.islower()
            and token2.text.islower()
            and judge_pos(token1.pos_) == judge_pos(token2.pos_) == "word"
        ):
            idx.append(i)

    idx = list(set(idx))
    times = max(1, int(len(idx) * prob))
    idx = random.sample(idx, times) if len(idx) > 0 else []
    return idx


def perturbate(prompt, prob):

    new_prompt = ""

    token_list = pro_tokenize(prompt)
    perturbed_idx = select_idx(token_list, prob)

    tokens = [token.text for token in token_list]
    for i in range(len(tokens)):
        if i in perturbed_idx:
            t = tokens[i]
            tokens[i] = tokens[i + 2]
            tokens[i + 2] = t
    new_prompt = "".join(tokens)

    return new_prompt
