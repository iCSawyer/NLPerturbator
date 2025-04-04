import spacy
import yaml
from typing import List, Tuple

nlp = spacy.load("en_core_web_sm")


def pro_tokenize(text: str) -> List[spacy.tokens.token.Token]:
    """
    A word-level tokenizer for English which makes sure that "".join(tokens) == text

    Return:
    - list of spacy token, which has attributes like token.pos_, token.tag_
    - attributes list of spacy token: https://spacy.io/api/token#attributes (attributes related to position should not be used)

    Note:
    - token.pos_: coarse-grained part-of-speech
        - list: https://universaldependencies.org/u/pos/ + CONJ, EOL, SPACE
        - source code: https://github.com/explosion/spaCy/blob/master/spacy/glossary.py
    - token.tag_: fine-grained part-of-speech
        - list: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html (not compared with the source code yet)
        - source code: https://github.com/explosion/spaCy/blob/master/spacy/glossary.py
    """
    tokens = nlp(text)

    char_index = 0
    new_tokens = []

    # compare tokens with original text and add ignored characters to the token list
    for token in tokens:
        new_char_index = text.find(token.text, char_index)

        if new_char_index - char_index > 0:
            special_chars = text[char_index:new_char_index]

            sdoc = nlp(special_chars)
            assert len(sdoc) == 1

            new_tokens.append(sdoc[0])
            char_index += len(special_chars)

        new_tokens.append(token)
        char_index += len(token.text)

    # add the remaining character
    if char_index < len(text):
        special_chars = text[char_index:]

        sdoc = nlp(special_chars)
        assert len(sdoc) == 1

        new_tokens.append(sdoc[0])

    # make sure that "".join(tokens) == text
    assert "".join([t.text for t in new_tokens]) == text

    return new_tokens


def judge_pos(pos: str, level: str = "coarse") -> str:
    """
    Judge if is a word (not whitespace etc.)

    >>> judge_pos("NOUN") == "word"
    >>> judge_pos("SPACE") == "other"
    """
    # assert level in ["coarse", "fine"]
    assert level in ["coarse"]

    if level == "coarse":
        mapping = {
            "word": [
                "ADJ",  # "adjective"
                "ADP",  # "adposition"
                "ADV",  # "adverb"
                "AUX",  # "auxiliary"
                "CONJ",  # "conjunction"
                "CCONJ",  # "coordinating conjunction"
                "DET",  # "determiner"
                "INTJ",  # "interjection"
                "NOUN",  # "noun"
                "PRON",  # "pronoun"
                "PROPN",  # "proper noun"
                "PART",  # "particle"
                "SCONJ",  # "subordinating conjunction"
                "NUM",  # "numeral"
                "VERB",  # "verb"
                "PUNCT",  # "punctuation"
                "SYM",  # "symbol"
            ],
            "other": [
                "X",  # "other"
                "EOL",  # "end of line"
                "SPACE",  # "space"
            ],
        }
        return "word" if pos in mapping["word"] else "other"
    else:
        pass


def judge_real_word(pos: str, level: str = "coarse") -> str:
    """
    Judge if is a real word (not whitespace, number, punctuations, etc.)

    >>> judge_pos("NOUN") == "word"
    >>> judge_pos("SPACE") == "other"
    """
    # assert level in ["coarse", "fine"]
    assert level in ["coarse"]

    if level == "coarse":
        mapping = {
            "word": [
                "ADJ",  # "adjective"
                "ADP",  # "adposition"
                "ADV",  # "adverb"
                "AUX",  # "auxiliary"
                "CONJ",  # "conjunction"
                "CCONJ",  # "coordinating conjunction"
                "DET",  # "determiner"
                "INTJ",  # "interjection"
                "NOUN",  # "noun"
                "PRON",  # "pronoun"
                "PROPN",  # "proper noun"
                "PART",  # "particle"
                "SCONJ",  # "subordinating conjunction"
                "VERB",  # "verb"
            ],
            "other": [
                "X",  # "other"
                "EOL",  # "end of line"
                "SPACE",  # "space"
            ],
        }
        return "word" if pos in mapping["word"] else "other"
    else:
        pass



def keep_case(ref, str):

    if ref[0].isupper() and all([c.islower() for c in ref[1:]]):
        return "".join([c.upper() if i == 0 else c for i, c in enumerate(str)])

    if all([c.isupper() for c in ref]):
        return str.upper()

    if all([c.islower() for c in ref]):
        return str.lower()
    return str


if __name__ == "__main__":
    text = """you should there exist an integer index i
    such that lst_A < lst_B and for any j we have
lst_A = lst_B.
    
    It is guaranteed that the answer is unique.
Return an ordered list of the values on the cells that the minimum path go through.
"""
    tokens = pro_tokenize(text)

    print([(t.text, t.pos_) for t in tokens])
    # print([(t.text, t.tag_) for t in tokens])

    print(" ".join([t.text for t in tokens if judge_pos(t.pos_, "coarse") == "word"]))
