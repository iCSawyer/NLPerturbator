import json
from math import ceil

from accelerate.utils import set_seed
from torch.utils.data.dataloader import DataLoader
from transformers import StoppingCriteria, StoppingCriteriaList

from lm_eval.utils import TokenizedDataset, complete_code


class EndOfFunctionCriteria(StoppingCriteria):
    """Custom `StoppingCriteria` which checks if all generated functions in the batch are completed."""
    def __init__(self, start_length, eof_strings, tokenizer, check_fn=None):
        self.start_length = start_length
        self.eof_strings = eof_strings
        self.tokenizer = tokenizer
        if check_fn is None:
            check_fn = lambda decoded_generation: any(
                [stop_string in decoded_generation for stop_string in self.eof_strings]
            )
        self.check_fn = check_fn

    def __call__(self, input_ids, scores, **kwargs):
        """Returns true if all generated sequences contain any of the end-of-function strings."""
        decoded_generations = self.tokenizer.batch_decode(input_ids[:, self.start_length :])
        return all([self.check_fn(decoded_generation) for decoded_generation in decoded_generations])

class TooLongFunctionCriteria(StoppingCriteria):
    """Custom `StoppingCriteria` which checks if the generated function is too long by a certain multiplier based on input length."""

    def __init__(self, input_length, multiplier):
        self.input_length = input_length
        self.multiplier = multiplier

    def __call__(self, input_ids, scores, **kwargs):
        """Returns true if generated sequence is too long."""
        return input_ids.shape[1] > int(self.input_length * self.multiplier)
        

def parallel_generations(task, dataset, accelerator, model, tokenizer, n_tasks, args):
    if args.load_generations_path:
        # load generated code
        with open(args.load_generations_path) as fp:
            generations = json.load(fp)
            if accelerator.is_main_process:
                print(
                    f"generations loaded, {n_tasks} selected from {len(generations)} with {len(generations[0])} candidates"
                )
        return generations[:n_tasks]
    
    #####################
    ###### OPEN AI ######
    #####################
    if args.api == True:
        import asyncio
        import os
        from openai import AsyncOpenAI
        from tqdm.asyncio import tqdm
        import re

        api_key = "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"
        client = AsyncOpenAI(api_key=api_key)
        
        # prompts = [task.get_prompt(doc) for doc in dataset]
        # print(task)
        if args.tasks == "humaneval":        
            prompts = [
                "Please provide a self-contained Python script that solves the following problem in a markdown code block:\n" +
                f"```\n{task.get_prompt(doc).strip()}\n```"
                for doc in dataset
            ]
            stop_list = ["\n#", "\n```", "if __name__", "\nprint"]
            # print(prompts[0])
        elif args.tasks == "mbpp":
            prompts = [
                "Please provide a self-contained Python script that solves the following problem in a markdown code block:\n" +
                f"```\n{task.get_prompt(doc).strip()}\n```"
                for doc in dataset
            ]
            stop_list = ["\nassert", "\nprint", "\nif", "\n```"]
            # print(prompts[0])
        else:
            assert False

        
        def extract_python_code(text: str) -> str:
            _st = text.find("```")
            if "_st" == -1:
                print(text)
                print("warning")
            st = text.find("\n", _st)           
            return text[st:].strip()
            
        
        awaitables = [client.chat.completions.create(
            model=args.model,
            messages=[{"role": "user", "content": prompt}],
            n=args.batch_size,
            max_tokens=args.max_length_generation,
            temperature=args.temperature,
            top_p=args.top_p,
            stop=stop_list
        ) for prompt in prompts]
        responses = asyncio.run(tqdm.gather(*awaitables))
        
        generations = []
        for i, (prompt, response) in enumerate(zip(prompts, responses)):
            # texts = [prompt + choice.text for choice in response.choices]
            texts = [extract_python_code(choice.message.content) for choice in response.choices]
            generations.append([task.postprocess_generation(text, i, args.api) for text in texts])
        return generations
    #####################
    ###### OPEN AI ######
    #####################

    set_seed(args.seed, device_specific=True)

    # Setup generation settings
    gen_kwargs = {
        "do_sample": args.do_sample,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "top_k": args.top_k,
        "max_length": args.max_length_generation,
    }
    stopping_criteria = []
    # The input_length / start_length set to 0 for now will be adjusted later
    # Check if the task has a custom check_fn method for the stopping criteria
    if task.stop_words and tokenizer.eos_token:
        task.stop_words.append(tokenizer.eos_token)    
    if hasattr(task, "check_fn"):
        stopping_criteria.append(
            EndOfFunctionCriteria(0, task.stop_words, tokenizer, task.check_fn)
        )
    elif task.stop_words:
        stopping_criteria.append(
            EndOfFunctionCriteria(0, task.stop_words, tokenizer)
        )
    if hasattr(task, "max_length_multiplier") and task.max_length_multiplier:
        stopping_criteria.append(
            TooLongFunctionCriteria(0, task.max_length_multiplier)
        )
    
    if stopping_criteria:
        gen_kwargs["stopping_criteria"] = StoppingCriteriaList(stopping_criteria)

    if args.instruction_tokens:
        instruction_tokens = args.instruction_tokens.split(",")
        if len(instruction_tokens) != 3:
            raise ValueError(
                "Instruction tokens should contain exactly 3 tokens separated by a comma. If a token is empty, represent it as ''"
            )
        for token in instruction_tokens:
            if token.strip() != "":
                task.stop_words.append(token)
    else:
        instruction_tokens = None
    if accelerator.is_main_process:
        print(f"number of problems for this task is {n_tasks}")
    n_copies = ceil(args.n_samples / args.batch_size)

    ds_tokenized = TokenizedDataset(
        task,
        dataset,
        tokenizer,
        num_devices=accelerator.state.num_processes,
        max_length=args.max_length_generation,
        limit_start=args.limit_start,
        n_tasks=n_tasks,
        n_copies=n_copies,
        prefix=args.prefix,
        has_encoder=args.modeltype == "seq2seq",
        instruction_tokens=instruction_tokens,
    )

    # do not confuse args.batch_size, which is actually the num_return_sequences
    ds_loader = DataLoader(ds_tokenized, batch_size=1)

    is_loaded_in_8bit = getattr(model, "is_loaded_in_8bit", False)
    is_loaded_in_4bit = getattr(model, "is_loaded_in_4bit", False)
    if args.max_memory_per_gpu is not None:
        # The model is already sharded across multiple GPUs
        ds_loader = accelerator.prepare(ds_loader)
    elif not is_loaded_in_8bit and not is_loaded_in_4bit:
        # we only wrap data loader to avoid extra memory occupation
        model = model.to(accelerator.device)
        ds_loader = accelerator.prepare(ds_loader)
    else:
        # model.to() is not supported for 8bit and 4bit models
        model, ds_loader = accelerator.prepare(model, ds_loader)

    generations = complete_code(
        task,
        accelerator,
        model,
        tokenizer,
        ds_loader,
        n_tasks=n_tasks,
        limit_start=args.limit_start,
        batch_size=args.batch_size,
        prefix=args.prefix,
        instruction_tokens=instruction_tokens,
        postprocess=args.postprocess,
        is_wrapped=is_loaded_in_8bit or is_loaded_in_4bit,
        **gen_kwargs,
    )
    return generations
