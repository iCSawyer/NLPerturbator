import random
from .my_util import *
import copy
import re

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

# to avoid char deletion to delete a keyboard typo
key_board_typo_selected_indices = []


# ----------------Functions for Keyboard typo----------------
def get_alphabet_indices(input_string):
    alphabet_indices = [
        i for i, char in enumerate(input_string) if char in adjacent_letters
    ]
    return alphabet_indices


def get_random_indices(indices_list, prob):
    x = max(1, int(len(indices_list) * prob))
    selected_indices = random.sample(indices_list, x)
    selected_indices.sort()
    key_board_typo_selected_indices = copy.deepcopy(selected_indices)
    return selected_indices


def keyboard_typo(prompt, random_indices):
    prompt_list = list(prompt)
    for index in random_indices:
        prompt_list[index] = random.choice(adjacent_letters[prompt[index]])
    new_prompt = "".join(prompt_list)
    return new_prompt

def keyboard_typo_perturbate(prompt, keyboard_typo_prob):
    alphabet_list = get_alphabet_indices(prompt)
    random_indices = get_random_indices(alphabet_list, keyboard_typo_prob)
    new_prompt = keyboard_typo(prompt, random_indices)
    # print(new_prompt)
    return new_prompt


# ----------------Functions for char deletion----------------

def is_lower_alphabet(char):
    return "a" <= char <= "z"


# Given a string, return the indices of chars that satisfy the following conditions:
# 1. reside in a word >= 3 chars
# 2. not at the start and end of a word
# 3. are lower case alphabets
def indices_in_long_words(input_string):
    words = re.finditer(r"\b\w{3,}\b", input_string)
    alphabet_indices = []
    for match in words:
        word_start = match.start()
        word_end = match.end()
        word = match.group()
        for i, char in enumerate(word):
            if i == 0 or i == (len(word) - 1):
                continue
            if is_lower_alphabet(char) and (word_start + i) not in key_board_typo_selected_indices:
                alphabet_indices.append(word_start + i)
    return alphabet_indices


def get_random_indices_char_deletion(indices_list, prob):
    x = max(1, int(len(indices_list) * prob))
    selected_indices = random.sample(indices_list, x)
    selected_indices.sort()
    return selected_indices


def char_deletion(prompt, random_indices):
    new_prompt_list = []
    for i, char in enumerate(prompt):
        if i not in random_indices:
            new_prompt_list.append(char)
    new_prompt = "".join(new_prompt_list)
    return new_prompt


def char_deletion_perturbate(prompt, char_deletion_prob):
    alphabet_list = indices_in_long_words(prompt)
    random_indices = get_random_indices_char_deletion(alphabet_list, char_deletion_prob)
    new_prompt = char_deletion(prompt, random_indices)
    # print(new_prompt)
    return new_prompt


def perturbate(prompt, keyboard_typo_prob, char_deletion_prob):
    new_prompt_first = keyboard_typo_perturbate(prompt, keyboard_typo_prob)
    new_prompt_final = char_deletion_perturbate(new_prompt_first, char_deletion_prob)
    return new_prompt_final


