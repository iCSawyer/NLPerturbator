import random
from .my_util import *
from nltk.corpus import wordnet

# from wordhoard import Antonyms


def select_idx(token_list, prob):
    """"""
    idx = []
    for i, token in enumerate(token_list):
        if (
            judge_pos(token.pos_) == "word"
            and token.pos_
            in [
                "NOUN",
                "VERB",
                "ADJ",
                "ADV",
            ]
            and token.text.isalpha()
        ):
            idx.append(i)

    idx = list(set(idx))
    times = max(1, int(len(idx) * prob))
    idx = random.sample(idx, times) if len(idx) > 0 else []
    return idx


def get_synonyms(word):
    synonyms = []

    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())

    # antonym = Antonyms(search_string=word)
    # synonyms = antonym.find_antonyms()

    if word in synonyms:
        synonyms.remove(word)
    return synonyms if len(synonyms) > 0 else [word]


def perturbate(prompt, prob):
    new_prompt = ""

    token_list = pro_tokenize(prompt)
    perturbed_idx = select_idx(token_list, prob)

    for i, token in enumerate(token_list):
        if i in perturbed_idx:
            synonym = random.choice(get_synonyms(token.text))
            new_prompt += synonym
        else:
            new_prompt += token.text

    return new_prompt
