import random
import re


def is_lower_alphabet(char):
    return "a" <= char <= "z"


# Given a string, return the indices of chars that are lower case alphabets
def get_alphabet_indices(input_string):
    alphabet_indices = [
        i for i, char in enumerate(input_string) if is_lower_alphabet(char)
    ]
    return alphabet_indices


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
            if is_lower_alphabet(char):
                alphabet_indices.append(word_start + i)
    return alphabet_indices


def get_random_indices(indices_list, prob):
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


def perturbate(prompt, prob):
    alphabet_list = indices_in_long_words(prompt)
    random_indices = get_random_indices(alphabet_list, prob)
    new_prompt = char_deletion(prompt, random_indices)
    # print(new_prompt)
    return new_prompt


# test = "Write a function to output each item in a list"
# for i in range(50):
#    output = perturbate(test, 0.10, 1, 42+i)
#    print(i, output)
