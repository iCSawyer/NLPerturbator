# note: use a individual virtual environment and
import random
from .my_util import *
from nltk.corpus import wordnet
from parrot import Parrot
import torch
import warnings

warnings.filterwarnings("ignore")


def set_torch_seed(seed):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def judge(token):
    end_symbols = [
        ".",
        "!",
        "?",
        ";",
        ":",
    ]
    return token.text in end_symbols


def paraphrase(sentence: str, model):
    print("\nsentence:", sentence)
    parrot = model
    para_phrases = parrot.augment(input_phrase=sentence)
    try:
        if sentence[0].isupper():
            rtn = para_phrases[0][0][0].upper() + para_phrases[0][0][1:]
        else:
            rtn = para_phrases[0][0]
    except:
        rtn = sentence
    print("rtn:", rtn)
    return rtn


def perturbate(prompt, times, model, seed):
    """
    P1 - rephrasing_sentence

    Algorithm: DL model
    """
    token_list = pro_tokenize(prompt)
    perturbed_text = ""


    perturbed_idx = [
        i
        for i, token in enumerate(token_list)
        if judge(token) or i == len(token_list) - 1  
    ]
    perturbed_idx = random.sample(perturbed_idx, min(times, len(perturbed_idx)))

    last = 0
    for i, token in enumerate(token_list):
        if judge(token) or i == len(token_list) - 1:
            sentence = "".join([token.text for token in token_list[last : i + 1]])
            if i in perturbed_idx:
                sentence = paraphrase(sentence, model)
            last = i + 1
            perturbed_text += sentence
    return perturbed_text
