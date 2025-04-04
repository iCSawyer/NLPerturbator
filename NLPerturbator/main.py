import csv
import argparse
import yaml
from tqdm import tqdm
import random
from parrot import Parrot
from perturbator import (
    extra_space_among_words,
    extra_space_inside_words,
    repeated_words,
    repeated_char,
    char_deletion,
    preposition_deletion,
    determiner_deletion,
    space_deletion,
    keyboard_typo,
    extra_capital_letter,
    grammatical_person_variation,
    active_and_passive_voice_variation,
    word_class_variation,
    synonym_substitution,
    swap_adjacent_chars,
    swap_adjacent_words,
    c1,
    c2,
    c3,
    # rephrasing_sentence, # individual virtualenv
     declarative_to_interrogative,
)


def read_yaml(path="./config.yaml"):
    return yaml.load(open(path, "r"), Loader=yaml.FullLoader)


def extract(row, dataset):
    """a helper function to extract the start and end of the natural language part of the prompt"""
    prompt = row["prompt"]
    start, end = 0, len(prompt)

    if dataset == "humaneval":
        task_id, entry_point = row["task_id"], row["entry_point"]

        # including a lot of special cases
        end_marker = [  # priority exists
            "For example",
            "for example",
            "for examble",
            "For Example",
            "Example",
            "example",
            "It must be implemented like this",
            "[input/output] samples",
            ">>>",
        ]
        end_marker.append(entry_point + "(")
        if task_id in [
            "HumanEval/119",
            "HumanEval/127",
            "HumanEval/130",
            "HumanEval/153",
            "HumanEval/99",
        ]:
            end_marker.remove("For example")
        if task_id in ["HumanEval/140", "HumanEval/127"]:
            end_marker.remove("Example")
        if task_id in ["HumanEval/127"]:
            end_marker.remove("example")

        # start
        start, end = None, None
        start = prompt.find(entry_point)
        if prompt.find(r'"""', start) != -1:
            start = prompt.find(r'"""', start)
            end_marker.append(r'"""')
        else:
            start = prompt.find(r"'''", start)
            assert start != -1
            end_marker.append(r"'''")
        start += 3
        for i, char in enumerate(prompt[start:]):
            # find the first non-space character
            if not char.isspace():
                start += i
                break

        # end
        for marker in end_marker:
            end = prompt.find(marker, start)
            if end != -1:
                break
        for i in range(len(prompt[start:end])):
            # find the last non-space character
            if not prompt[start:end][-i - 1].isspace():
                end -= i
                break

        assert start != -1 and end != -1
        assert (
            prompt[start:end] == prompt[start:end].strip()
        ), "space characters exist in the start or end"

    elif dataset == "mbpp":
        url_pos = prompt.find("https://")
        if url_pos != -1:
            end = url_pos
    return start, end


def pipeline(dataset, perturbator, seed, **perturbator_args):
    input_csv_path = f"./data/{dataset}.csv"
    output_csv_path = f"./output/auto2/{dataset}_{perturbator}.csv"

    with open(input_csv_path, "r", encoding="utf-8") as infile, open(
        output_csv_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        csv_reader = csv.DictReader(infile)
        fieldnames = csv_reader.fieldnames
        modified_fieldnames = list(fieldnames) + ["original_prompt"]
        csv_writer = csv.DictWriter(outfile, fieldnames=modified_fieldnames)
        csv_writer.writeheader()

        modification_func = eval(perturbator).perturbate
        random.seed(seed)  # change seed for each perturbator
        for row in tqdm(csv_reader):
            prompt = row["prompt"]
            st, ed = extract(row, dataset)
            row["prompt"] = (
                prompt[:st]
                + modification_func(
                    prompt[st:ed],
                    **perturbator_args,
                )
                + prompt[ed:]
            )
            row["original_prompt"] = prompt
            csv_writer.writerow(row)


if __name__ == "__main__":
    # config of datasets and perturbators
    yml = read_yaml()

    # args
    args = argparse.ArgumentParser()
    args.add_argument("--dataset", choices=list(yml["dataset"]), required=True)
    args.add_argument("--perturbator", choices=list(yml["perturbator"]), required=True)
    args = args.parse_args()

    # arguments for perturbator
    perturbator_args = yml["perturbator"][args.perturbator]
    if perturbator_args is None:
        perturbator_args = {}
    
    if args.perturbator == "rephrasing_sentence":
        perturbator_args["model"] = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5")

    # pipeline
    random.seed(yml['seed'])
    pipeline(dataset=args.dataset, perturbator=args.perturbator, seed=random.randint(0, 1e9), **perturbator_args)
