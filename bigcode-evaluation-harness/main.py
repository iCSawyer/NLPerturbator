import fnmatch
import json
import warnings

import datasets
import torch
import transformers
from accelerate import Accelerator
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer, HfArgumentParser

from lm_eval.arguments import EvalArguments
from lm_eval.evaluator import Evaluator
from lm_eval.tasks import ALL_TASKS

import os
os.environ['TIKTOKEN_CACHE_DIR'] = ""

class MultiChoice:
    def __init__(self, choices):
        self.choices = choices

    # Simple wildcard support (linux filename patterns)
    def __contains__(self, values):
        for value in values.split(","):
            if len(fnmatch.filter(self.choices, value)) == 0:
                return False

        return True

    def __iter__(self):
        for choice in self.choices:
            yield choice


def parse_args():
    parser = HfArgumentParser(EvalArguments)
    
    parser.add_argument(
        "--api",
        action="store_true",
        help="If set true, enter a temperorary mode of API, only support one model"        
    )
    
    parser.add_argument(
        "--model",
        default="codeparrot/codeparrot-small",
        help="Model to evaluate, provide a repo name in Hugging Face hub or a local path",
    )
    
    parser.add_argument(
        "--modeltype",
        default="causal",
        help="AutoModel to use, it can be causal or seq2seq",
    )
    parser.add_argument(    
        "--peft_model",
        type=str,
        default=None,
        help="Adapter to the PEFT base model. Can be utilized for loading PEFT adapters such as a LoRA trained model. The --model parameter needs to be the base model.",
    )
    parser.add_argument(
        "--revision",
        default=None,
        help="Model revision to use",
    )
    parser.add_argument(
        "--use_auth_token",
        action="store_true",
        help="Use the token generated when running `huggingface-cli login` (necessary for private model).",
    )
    parser.add_argument(
        "--trust_remote_code",
        action="store_true",
        help="Use a model with custom code, this requires executing code by the author of the model.",
    )
    parser.add_argument(
        "--tasks",
        default=None,
        choices=MultiChoice(ALL_TASKS),
        help=f"Evaluation tasks from {ALL_TASKS}",
    )
    parser.add_argument(
        "--instruction_tokens",
        default=None,
        help="A series of instruction tokens used for instruction-tuning benchamrks separated by comma e.g. <user_message>,<end_user_message>,<assistant_message>",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Batch size for evaluation on each worker, can be larger for HumanEval",
    )
    parser.add_argument(
        "--max_length_generation",
        type=int,
        default=512,
        help="Maximum length of generated sequence (prompt+generation)",
    )
    parser.add_argument(
        "--precision",
        type=str,
        default="fp32",
        help="Model precision, from: fp32, fp16 or bf16",
    )
    parser.add_argument(
        "--load_in_8bit",
        action="store_true",
        help="Load model in 8bit",
    )
    parser.add_argument(
        "--load_in_4bit",
        action="store_true",
        help="Load model in 4bit",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of samples to solve and evaluate from the benchmark",
    )
    parser.add_argument(
        "--limit_start",
        type=int,
        default=0,
        help="Optional offset to start from when limiting the number of samples",
    )    
    parser.add_argument(
        "--postprocess",
        action="store_false",
        help="Postprocess model outputs before execution, always on except during generation tests",
    )
    parser.add_argument(
        "--allow_code_execution",
        action="store_true",
        help="Allow code evaluation to execute external/untrusted Python code on your machine",
    )
    parser.add_argument(
        "--generation_only",
        action="store_true",
        help="Do code generation but no evaluation",
    )
    parser.add_argument(
        "--load_generations_path",
        type=str,
        default=None,
        help="Path of file with previously generated solutions, if provided generation is skipped and only evaluation is done",
    )
    parser.add_argument(
        "--load_data_path",
        type=str,
        default=None,
        help="Path of additional data to load for the tasks",
    )    
    parser.add_argument(
        "--metric_output_path",
        type=str,
        default="evaluation_results.json",
        help="Path to save the results",
    )
    parser.add_argument(
        "--save_generations",
        action="store_true",
        help="Whether to save code generations",
    )
    parser.add_argument(
        "--save_generations_path",
        type=str,
        default="generations.json",
        help="Path for saving the code generations",
    )
    parser.add_argument(
        "--save_references",
        action="store_true",
        help="Whether to save reference solutions/tests",
    )
    parser.add_argument(
        "--save_references_path",
        type=str,
        default="generations.json",
        help="Path for saving the code generations",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="prompt",
        help="Prompt type to use for generation in HumanEvalPack tasks",
    )
    parser.add_argument("--max_memory_per_gpu", type=str, default=None)
    parser.add_argument(
        "--check_references",
        action="store_true",
        help="Don't run generation but benchmark groundtruth (useful for debugging)",
    )
    parser.add_argument("--local_dataset", type=str)    
    return parser.parse_args()


def pattern_match(patterns, source_list):
    """Returns a list containing all values of the source_list that
    match at least one of the patterns"""
    task_names = set()
    for pattern in patterns:
        for matching in fnmatch.filter(source_list, pattern):
            task_names.add(matching)
    return list(task_names)

def get_gpus_max_memory(max_memory, num_gpus):
    max_memory = {i: max_memory for i in range(num_gpus)}
    print("Loading model via these GPUs & max memories: ", max_memory)
    return max_memory

def main():
    args = parse_args()
    transformers.logging.set_verbosity_error()
    datasets.logging.set_verbosity_error()

    if args.tasks is None:
        task_names = ALL_TASKS
    else:
        task_names = pattern_match(args.tasks.split(","), ALL_TASKS)

    accelerator = Accelerator()
    if accelerator.is_main_process:
        print(f"Selected Tasks: {task_names}")

    results = {}
    if args.load_generations_path:
        # here we don't generate code but only evaluate previously computed generations
        if accelerator.is_main_process:
            print("evaluation only mode")
        evaluator = Evaluator(accelerator, None, None, args)
        for task in task_names:
            results[task] = evaluator.evaluate(task)
    elif args.api:
        evaluator = Evaluator(accelerator, args.model, None, args)
        for task in task_names:
            if args.generation_only:
                if accelerator.is_main_process:
                    print("generation mode only")
                generations, references = evaluator.generate_text(task)
                if accelerator.is_main_process:
                    with open(args.save_generations_path, "w") as fp:
                        json.dump(generations, fp)
                        print(f"generations were saved at {args.save_generations_path}")
                    if args.save_references:
                        with open(args.save_references_path, "w") as fp:
                            json.dump(references, fp)
                            print("references were saved")
            else:
                results[task] = evaluator.evaluate(task)
    else:
        # here we generate code and save it (evaluation is optional but True by default)
        dict_precisions = {
            "fp32": torch.float32,
            "fp16": torch.float16,
            "bf16": torch.bfloat16,
        }
        if args.precision not in dict_precisions:
            raise ValueError(
                f"Non valid precision {args.precision}, choose from: fp16, fp32, bf16"
            )

        model_kwargs = {
            "revision": args.revision,
            "trust_remote_code": args.trust_remote_code,
            "use_auth_token": args.use_auth_token,
        }
        if args.load_in_8bit:
            print("Loading model in 8bit")
            model_kwargs["load_in_8bit"] = args.load_in_8bit
            model_kwargs["device_map"] = {"": accelerator.process_index}
        elif args.load_in_4bit:
            print("Loading model in 4bit")
            model_kwargs["load_in_4bit"] = args.load_in_4bit
            model_kwargs["device_map"] = {"": accelerator.process_index}
        else:
            print(f"Loading model in {args.precision}")
            model_kwargs["torch_dtype"] = dict_precisions[args.precision]

            if args.max_memory_per_gpu:
                model_kwargs["max_memory"] = get_gpus_max_memory(args.max_memory_per_gpu, accelerator.num_processes)
                model_kwargs["offload_folder"] = "offload"
                model_kwargs["device_map"] = "auto"

        assert args.modeltype == "causal"
        assert not args.peft_model
        model_name = args.model.lower()
        
        # model
        if "wizard" in model_name:
            # TODO prompt 差异 暂时忽略 
            # https://github.com/nlpxucan/WizardLM/blob/main/WizardCoder/src/inference_wizardcoder.py
            model = AutoModelForCausalLM.from_pretrained(
                args.model,
                **model_kwargs,
            )
            tokenizer = AutoTokenizer.from_pretrained(
                args.model,
                revision=args.revision,
                trust_remote_code=args.trust_remote_code,
                use_auth_token=args.use_auth_token,
                truncation_side="left",
                padding_side="right",
            )
            model.tie_weights()
            model.config.pad_token_id = tokenizer.pad_token_id
            model = model.bfloat16()
            model.eval()
            model = torch.compile(model)
        elif "incoder" in model_name:
            model_kwargs['revision'] = args.revision = "float16"
            model_kwargs['low_cpu_mem_usage'] = True
            
            model = AutoModelForCausalLM.from_pretrained(
                args.model,
                **model_kwargs,
            )   
            
            tokenizer = AutoTokenizer.from_pretrained(
                args.model,
                revision=args.revision,
                trust_remote_code=args.trust_remote_code,
                use_auth_token=args.use_auth_token,
                truncation_side="left",
                padding_side="right", # padding on the right is needed to cut off padding in `complete_code`
            )
        elif "star" in model_name:
            model_kwargs["device_map"] = "auto"
            args.max_memory_per_gpu = "0" # if this argument is None, the program will move the model to GPU again
            model = AutoModelForCausalLM.from_pretrained(
                args.model,
                **model_kwargs,
            )   
            
            tokenizer = AutoTokenizer.from_pretrained(
                args.model,
                revision=args.revision,
                trust_remote_code=args.trust_remote_code,
                use_auth_token=args.use_auth_token,
                truncation_side="left",
                padding_side="right", # padding on the right is needed to cut off padding in `complete_code`
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                args.model,
                **model_kwargs,
            )   
            
            tokenizer = AutoTokenizer.from_pretrained(
                args.model,
                revision=args.revision,
                trust_remote_code=args.trust_remote_code,
                use_auth_token=args.use_auth_token,
                truncation_side="left",
                padding_side="right", # padding on the right is needed to cut off padding in `complete_code`
            )
        
        
        if not tokenizer.eos_token:
            if tokenizer.bos_token:
                tokenizer.eos_token = tokenizer.bos_token
                print("bos_token used as eos_token")
            else:
                raise ValueError("No eos_token or bos_token found")
        try:
            tokenizer.pad_token = tokenizer.eos_token
        # Some models like CodeGeeX2 have pad_token as a read-only property
        except AttributeError:
            print("Not setting pad_token to eos_token")
            pass
        evaluator = Evaluator(accelerator, model, tokenizer, args)

        for task in task_names:
            if args.generation_only:
                if accelerator.is_main_process:
                    print("generation mode only")
                generations, references = evaluator.generate_text(task)
                if accelerator.is_main_process:
                    with open(args.save_generations_path, "w") as fp:
                        json.dump(generations, fp)
                        print(f"generations were saved at {args.save_generations_path}")
                    if args.save_references:
                        with open(args.save_references_path, "w") as fp:
                            json.dump(references, fp)
                            print("references were saved")
            else:
                results[task] = evaluator.evaluate(task)

    # Save all args to config
    results["config"] = vars(args)
    if not args.generation_only:
        dumped = json.dumps(results, indent=2)
        if accelerator.is_main_process:
            print(results[args.tasks][0])
        with open(args.metric_output_path, "w") as f:
            f.write(dumped)


if __name__ == "__main__":
    main()
