# NLPerturbator: Studying the Robustness of Code LLMs to Natural Language Variations

This is our replication package of the paper "NLPerturbator: Studying the Robustness of Code LLMs to Natural Language Variations". In this repository, we introduce the information of our tool NLPerturbator, the evaluation process, and our survey.


## List of Materials:

- [x] README.md
- [x] NLPerturbator: Code of NLPerturbator
- [x] Dataset: Manually verified datasets: HumanEval-R and MBPP-R
- [x] bigcode-evaluation-harness: The mirror of the evaluation tool we used
- [x] Results_RQ3: Complete results of RQ3
- [x] Survey: Questionnaire template and stats results
- [x] Others: Including the literature review (list of collected papers and initial categories) and the appendix (implementation details and case studies)


## Framework for Natural Language Perturbations: NLPerturbator

### Environments

We use Ubuntu 20.04.1 LTS and Python 3.10.12 to run this project. Use the following command to install the required packages:

```bash
pip install -r requirements.txt
```


### Original Datasets

We use two datasets in our study: 
- [mbpp](https://huggingface.co/datasets/mbpp): The mbpp dataset consists of around 1,000 crowd-sourced Python programming problems, designed to be solvable by entry level programmers. Note that we use the sanitized subset of this dataset.
- [HumanEval](https://huggingface.co/datasets/openai_humaneval): The HumanEval dataset includes 164 programming problems with a function signature, docstring, body, and several unit tests.


### Generate Data Perturbed by Specific Perturbators

Use the following command to generate data perturbed by specific perturbators:

```bash
python main.py --dataset $DATASET --perturbator $PERTURBATOR
```

`DATASET` should be `mbpp` or `humaneval` and `PERTURBATOR` should be in the `perturbator/` directory. The output file will be saved in `output/$DATASET_$PERTURBATOR.csv`.


### Add a New Perturbator

You can design your own perturbator and add it to our framework. To do this, you need to follow the following steps:
1. Create a Python file `new_perturbator.py` in `perturbator/` and implement the function `perturbate()`. Function `perturbate` function accepts arguments including the NL description of the prompt and some personal arguments. 

2. Add arguments except for `prompt` in the dictionary `perturbator` of `config.yaml`. That is to say, if you add `prob` argument in YAML file, the `perturbator()` function in `perturbator/new_perturbator.py` accepts two arguments: `prompt` and `prob`.


## Datasets

We share the datasets under the directory `\Dataset`, including:

* `\HumanEval-R` and `\MBPP-R`: manually verified perturbation datasets with default frequency

_Note: In a few cases, there is no available element in the prompt to perform the perturbation, therefore the perturbed prompt and original prompt are the same in such cases._


## Evaluation Process with *bigcode-evaluation-harness*

### Models

In our paper, we use [*bigcode-evaluation-harness*](https://github.com/bigcode-project/bigcode-evaluation-harness) to run the experiments of code generation. We use seven code LLMs to run the experiments. Here are 🤗Hugging Face links of these models: [StarCoder](https://huggingface.co/bigcode/starcoder), [WizardCoder](https://huggingface.co/WizardLM/WizardCoder-Python-7B-V1.0), [InCoder](https://huggingface.co/facebook/incoder-6B), [CodeGeeX2](https://huggingface.co/facebook/incoder-6B), [CodeLlama](https://huggingface.co/TheBloke/CodeLlama-7B-fp16), and [CodeGen2](https://huggingface.co/Salesforce/codegen25-7b-mono). For GPT-3.5-Turbo, we invoke the official API from OpenAI.


### *bigcode-evaluation-harness*

Compared to the original version of [*bigcode-evaluation-harness*](https://github.com/bigcode-project/bigcode-evaluation-harness), we mainly make these modifications to implement our experiments:

1. Add additional statements that are used in the usage examples of the models (e.g., `model.config.pad_token_id = tokenizer.pad_token_id)` used in the WizardCoder repository).
2. Replace the official(original) datasets with our perturbed datasets.
3. Output the details of test.
4. Add simple supports for OpenAI API.

This is our example bash script, you can modify it to meet your requirements:

```bash
accelerate launch --config_file <your_conf.yaml> main.py \
  --model <your_model_path> \
  --max_length_generation 512 \
  --tasks <humaneval/mbpp> \
  --temperature 0.2 \
  --n_samples 15 \
  --batch_size 15 \
  --precision <fp16/bf16> \
  --allow_code_execution \
  --trust_remote_code \
  --save_generations \
  --save_generations_path <your_path.json> \
  --save_references \
  --save_references_path <your_path.json> \
  --metric_output_path <your_path.json> \
  --local_dataset <your_dataset.csv>
```

We use two NVIDIA RTX 3090 to run the experiments. Note that for WizardCoder, we use the bf16 precision (as we cannot run it normally with fp16 due to its bug); for the other 5 models, we use fp16 precision.

