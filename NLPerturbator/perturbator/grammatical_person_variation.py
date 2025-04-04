import random
from .my_util import *
from lemminflect import getInflection


def select_idx(token_list, prob):
    idx = []
    for i, token in enumerate(token_list):
        if judge_pos(token.pos_) == "word" and (token.tag_ == "VB" or token.tag_ == "VBZ") and token.lemma_ != "be":
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
        if i in perturbed_idx:
            if token.tag_ != "VBZ":  
                new_prompt += keep_case(
                    token.text, getInflection(token.lemma_, tag="VBZ")[0]
                )
            elif token.tag_ == "VBZ": 
                new_prompt += keep_case(token.text, token.lemma_)
        else:
            new_prompt += token.text

    return new_prompt
