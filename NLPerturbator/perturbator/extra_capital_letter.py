import random
from .my_util import *


def select_idx(token_list, prob):
    idx = []
    cur_idx = 0
    
    for i, token in enumerate(token_list):
        token = token.text
        for offset, c in enumerate(token):
            if c.isalpha() and c.isupper():
                idx.append(cur_idx + offset + 1)
        
        if token.isalpha() and token[0].islower():
            idx.append(cur_idx)
        
        cur_idx += len(token)
        

    idx = list(set(idx))
    times = max(1, int(len(idx) * prob))
    idx = random.sample(idx, times) if len(idx) > 0 else []
    return idx


def perturbate(prompt, prob):
    new_prompt = ""
    token_list = pro_tokenize(prompt)
    
    perturbed_idx = select_idx(token_list, prob)

    for i, char in enumerate(prompt):
        if i in perturbed_idx:
            new_prompt += char.upper()
        else:
            new_prompt += char
    return new_prompt
