import random
from .my_util import *

adjacent_letters = {
    "a": ["q", "w", "s", "z"],
    "b": ["v", "g", "h", "n"],
    "c": ["x", "d", "f", "v"],
    "d": ["s", "e", "r", "f", "c", "x"],
    "e": ["w", "s", "d", "r"],
    "f": ["d", "r", "t", "g", "v", "c"],
    "g": ["f", "t", "y", "h", "b", "v"],
    "h": ["g", "y", "u", "j", "n", "b"],
    "i": ["u", "j", "k", "o"],
    "j": ["h", "u", "i", "k", "m", "n"],
    "k": ["j", "i", "o", "l"],
    "l": ["k", "o", "p"],
    "m": ["n", "j", "k"],
    "n": ["b", "h", "j", "m"],
    "o": ["i", "k", "l", "p"],
    "p": ["o", "l"],
    "q": ["a", "s", "w"],
    "r": ["e", "d", "f", "t"],
    "s": ["a", "w", "e", "d", "x", "z"],
    "t": ["r", "f", "g", "y"],
    "u": ["y", "h", "j", "i"],
    "v": ["c", "f", "g", "b"],
    "w": ["q", "a", "s", "e"],
    "x": ["z", "s", "d", "c"],
    "y": ["t", "g", "h", "u"],
    "z": ["a", "s", "x"],
}


def get_alphabet_indices(input_string):
    alphabet_indices = [
        i for i, char in enumerate(input_string) if char in adjacent_letters
    ]
    return alphabet_indices


def get_random_indices(indices_list, prob):
    x = max(1, int(len(indices_list) * prob))
    selected_indices = random.sample(indices_list, x)
    selected_indices.sort()
    return selected_indices


def keyboard_typo(prompt, random_indices):
    prompt_list = list(prompt)
    for index in random_indices:
        prompt_list[index] = random.choice(adjacent_letters[prompt[index]])
        # new_prompt = prompt[:index] + random.choice(adjacent_letters[prompt[index]]) + prompt[index:]
        # prompt = new_prompt
    new_prompt = "".join(prompt_list)
    return new_prompt

def keyboard_typo_perturbate(prompt, keyboard_typo_prob):
    alphabet_list = get_alphabet_indices(prompt)
    random_indices = get_random_indices(alphabet_list, keyboard_typo_prob)
    new_prompt = keyboard_typo(prompt, random_indices)
    # print(new_prompt)
    return new_prompt


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


def extra_space_outside_words_perturbate(prompt, extra_space_outside_words_prob):
    new_prompt = ""
    token_list = pro_tokenize(prompt)
    perturbed_idx = select_idx(token_list, extra_space_outside_words_prob)
    for i, token in enumerate(token_list):
        if i in perturbed_idx:
            new_prompt += " "
        new_prompt += token.text

    if -1 in perturbed_idx:
        new_prompt = " " + new_prompt
    if -2 in perturbed_idx:
        new_prompt += " "

    return new_prompt

def perturbate(prompt, keyboard_typo_prob, extra_space_outside_words_prob):
    new_prompt_first = keyboard_typo_perturbate(prompt, keyboard_typo_prob)
    new_prompt_final = extra_space_outside_words_perturbate(new_prompt_first, extra_space_outside_words_prob)
    return new_prompt_final


