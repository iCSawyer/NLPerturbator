import random
from .my_util import *
from lemminflect import getInflection


def select_idx(token_list, prob):
    idx = []
    for i, token in enumerate(token_list):
        if judge_pos(token.pos_) == "word" and token.pos_ == "VERB":
            if token.tag_ == "VBN":
                _t = getInflection(token.lemma_, tag=token.tag_)[0]
                if _t != token.text:
                    idx.append(i)
            else:
                _t = getInflection(token.lemma_, tag="VBN")[0]
                if _t != token.text:
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
            if token.tag_ == "VBN":
                _t = getInflection(token.lemma_, tag=token.tag_)[0]
                if _t:
                    new_prompt += keep_case(token.text, _t)
                else:
                    new_prompt += token.text
            else:
                _t = getInflection(token.lemma_, tag="VBN")[0]
                if _t:
                    new_prompt += keep_case(token.text, _t)
                else:
                    new_prompt += token.text
        else:
            new_prompt += token.text

    return new_prompt


def _deprecated_perturbate(prompt, prob, times, seed):


    def _judge(token):
        return token.pos_ == "VERB" and token.tag_ != "MD" and token.lemma_ != "be"

    def _rfind(tokens, idx):
        for i in range(idx - 1, -1, -1):
            if judge_pos(tokens[i].pos_) == "word":
                return i
        return -1

    def _be(token):
        if token.tag_ == "PRP": 
            if token.text.lower() == "i":
                return "am"
            elif token.text.lower() == "you":
                return "are"
            else:
                return "is"
        elif token.tag_ == "PRP$": 
            return "is"
        elif token.tag_ == "NN" or token.tag_ == "NNS":
            if token.tag_ == "NNS" or token.text.lower() == "they":
                return "are"
            else:
                return "is"
        elif token.text == "to":
            return "be"
        return ""


    tokens = pro_tokenize(prompt)
    perturbed_text = ""


    idx = [i for i, token in enumerate(tokens) if _judge(token)]
    idx = random.sample(idx, min(times, len(idx)))

    flag = False  
    for i in range(len(tokens) - 1, -1, -1): 
        token = tokens[i]
        if i in idx:  
            if token.tag_ != "VBN": 
                if i == 0:  
                    t = getInflection(token.lemma_, tag="VBN")[0]
                    t = t[0].upper() + t[1:]
                else:
                    be_ = _be(tokens[_rfind(tokens, i)])
                    if be_ != "":
                        t = be_ + " " + getInflection(token.lemma_, tag="VBN")[0]
                    else:
                        t = getInflection(token.lemma_, tag="VBN")[0]
                perturbed_text = t + perturbed_text
            else:  
                last_word = tokens[_rfind(tokens, i)]
                if last_word.lemma_ == "be":  
                    t = getInflection(token.lemma_, tag=last_word.tag_)[0] 
                    flag = True  
                    perturbed_text = t + perturbed_text
                else:
                    perturbed_text = token.text + perturbed_text
        else:
            if flag and token.lemma_ == "be":  
                flag = False
                perturbed_text = perturbed_text[1:]
            else:
                perturbed_text = token.text + perturbed_text
    return perturbed_text
