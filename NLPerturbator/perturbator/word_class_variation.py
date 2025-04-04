import random
from .my_util import *
from nltk.corpus import wordnet as wn



WN_NOUN = "n"
WN_VERB = "v"
WN_ADJECTIVE = "a"
WN_ADJECTIVE_SATELLITE = "s"
WN_ADVERB = "r"


def convert(word, from_pos, to_pos):

    synsets = wn.synsets(word, pos=from_pos)

    # Word not found
    if not synsets:
        return []

    # Get all lemmas of the word (consider 'a'and 's' equivalent)
    lemmas = []
    for s in synsets:
        for l in s.lemmas():
            if (
                s.name().split(".")[1] == from_pos
                or from_pos in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)
                and s.name().split(".")[1] in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)
            ):
                lemmas += [l]

    # Get related forms
    derivationally_related_forms = [
        (l, l.derivationally_related_forms()) for l in lemmas
    ]

    # filter only the desired pos (consider 'a' and 's' equivalent)
    related_noun_lemmas = []

    for drf in derivationally_related_forms:
        for l in drf[1]:
            if (
                l.synset().name().split(".")[1] == to_pos
                or to_pos in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)
                and l.synset().name().split(".")[1]
                in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)
            ):
                related_noun_lemmas += [l]

    # Extract the words from the lemmas
    words = [l.name() for l in related_noun_lemmas]
    len_words = len(words)

    # Build the result in the form of a list containing tuples (word, probability)
    result = [(w, float(words.count(w)) / len_words) for w in set(words)]
    result.sort(key=lambda w: -w[1])

    # return all the possibilities sorted by probability
    return result


def my_inflect(token):
    rtn = [token.text, 0]
    if token.pos_ == "NOUN":
        rtn = convert(token.text, "n", "v")
    elif token.pos_ == "VERB":
        rtn = convert(token.text, "v", "n")
    elif token.pos_ == "ADJ":
        rtn = convert(token.text, "a", "r")
        if not rtn:
            rtn = convert(token.text, "s", "r")
    elif token.pos_ == "ADV":
        rtn = convert(token.text, "r", "a")
        if not rtn:
            rtn = convert(token.text, "r", "s")

    if rtn:
        return keep_case(token.text, rtn[0][0])
    else:
        return token.text


def select_idx(token_list, prob):
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
            and my_inflect(token) != token.text
            and token.text.isalpha()
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

    for i, token in enumerate(token_list):
        if i in perturbed_idx:
            new_prompt += my_inflect(token)
        else:
            new_prompt += token.text

    return new_prompt
