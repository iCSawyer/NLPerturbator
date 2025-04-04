
# How Are Code LLMs Robust to Natural Language Perturbations in Real-world Scenarios? A Case Study on Code Generation

This is our replication package of the paper "How Are Code LLMs Robust to Natural Language Perturbations in Real-world Scenarios? A Case Study on Code Generation". In this repository, we introduce the information of our tool NLPerturbator, the evaluation process, and our survey.





## List of Collected Papers

In this section, we share the 43 papers we collected in our study about the robustness of language models (which is related to Section 3.1 of our paper):

| Idx | Title |
| --- | --- |
| 1 | ReCode: Robustness Evaluation of Code Generation Models |
| 2 | Adversarial GLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models |
| 3 | On the Robustness of Code Generation Techniques: An Empirical Study on GitHub Copilot |
| 4 | Generating Adversarial Examples for Holding Robustness of Source Code Processing Models |
| 5 | On the Robustness of ChatGPT: An Adversarial and Out-of-distribution Perspective |
| 6 | Competition-level code generation with alphacode |
| 7 | Improving neural machine translation robustness via data augmentation: Beyond back-translation |
| 8 | Adversarial attacks on deep-learning models in natural language processing: A survey |
| 9 | Codeattack: Code-based adversarial attacks for pre-trained programming language models |
| 10 | Adversarial Robustness of Deep Code Comment Generation |
| 11 | Synthetic and natural noise both break neural machine translation |
| 12 | Comparing attention-based convolutional and recurrent neural networks: Success and limitations in machine reading comprehension |
| 13 | In chatgpt we trust? measuring and characterizing the reliability of chatgpt |
| 14 | PromptBench: Towards Evaluating the Robustness of Large Language Models on Adversarial Prompts|
| 15 | On robustness of prompt-based semantic parsing with large pre-trained language model: An empirical study on codex |
| 16 | Stress test evaluation for natural language inference |
| 17 | Assessing Hidden Risks of LLMs: An Empirical Study on Robustness, Consistency, and Credibility |
| 18 | Improving Robustness of Language Models from a Geometry-aware Perspective |
| 19 | How Should Pre-Trained Language Models Be Fine-Tuned Towards Adversarial Robustness? |
| 20 | A Causal Framework to Quantify the Robustness of Mathematical Reasoning with Language Models |
| 21 | Exploring the Robustness of Large Language Models for Solving Programming Problems|
| 22 | How Important are Good Method Names in Neural Code Generation? A Model Robustness Perspective|
| 23 | On Adversarial Robustness of Synthetic Code Generation |
| 24 | A Study on Robustness and Reliability of Large Language Model Code Generation|
| 25 | Adversarial Robustness for Code|
| 26 | Towards robustness of deep program processing models—detection, estimation, and enhancement|
| 27 | CLAWSAT: Towards Both Robust and Accurate Code Models|
| 28 | Methods for Estimating and Improving Robustness of Language Models|
| 29 | An empirical study on robustness to spurious correlations using pre-trained language models|
| 30 | What do compressed large language models forget? robustness challenges in model compression|
| 31 | Latent jailbreak: A benchmark for evaluating text safety and output robustness of large language models|
| 32 | On evaluating adversarial robustness of large vision-language models|
| 33 | Robustness Over Time: Understanding Adversarial Examples' Effectiveness on Longitudinal Versions of Large Language Models|
| 34 | Certified Robustness for Large Language Models with Self-Denoising|
| 35 | Chain-of-Note: Enhancing Robustness in Retrieval-Augmented Language Models|
| 36 | A survey on evaluation of large language models|
| 37 | Towards robustness of large language models on text-to-sql task: An adversarial and cross-domain investigation|
| 38 | Do you really follow me? adversarial instructions for evaluating the robustness of large language models|
| 39 | Are Large Language Models Really Robust to Word-Level Perturbations?|
| 40 | Adversarial attacks and defenses in large language models: Old and new threats|
| 41 | An LLM can Fool Itself: A Prompt-Based Adversarial Attack|
| 42 | Simple LLM Prompting is State-of-the-Art for Robust and Multilingual Dialogue Evaluation|
| 43 | Graph Meets LLM: A Novel Approach to Collaborative Filtering for Robust Conversational Understanding|




## Initial Categories of Perturbations

In this section, we share the initial 25 categories of perturbation in natural language we summarized (which is related to Section 3.1 of our paper):

| Category | Example |
| --- | --- |
| `Category A1: Extra Space outside Words` | Example: "Write a function to replace ..." -> "Write a function to  replace ..." |
| `Category A2: Extra Space inside Words` | Example: "Write a function to replace ..." -> "Write a func tion to  replace ..." |
| `Category A3: Repeated Words` | Example: "Write a function to replace ..." -> "Write a function to to replace ..." |
| `Category A4: Repeated Chars` | Example: "Write a function to replace ..." -> "Write a funnction to replace ..." |
| `Category A5: Synonym Insertion` | Example: "Write a function to find ..." -> "Write a function to find discover ..." |
| `Category A6: Attaching URL` | Example: "Write a function to replace ..." -> "Write a function to replace ... https://google.com" |
| `Category A7: Attaching Interrogation Statements` | Example: "Write a function to replace ..." -> "Write a function to replace ... what is what who is who where is where" |
| `Category D1: Char Deletion` | Example: "Write a function to find ..." -> "Write a funtion to find ..." |
| `Category D2: Preposition Deletion` | Example: "Write a function to find ..." -> "Write a function find ..." |
| `Category D3: Determiner Deletion` | Example: "Write a function to reverse the string and ..." -> "Write a function to reverse string and ..." |
| `Category D4: Space Deletion` | Example: "Write a function to find ..." -> "Write afunction to find ..." |
| `Category E1: Keyboard Typo` | Example: "Write a function to replace ..." -> "Writr a function to replace ... " |
| `Category E2: Random Char Replacement` | Example: "Write a function to replace ..." -> "Wr!te a function to replace ... " |
| `Category E3: Extra Capital Letter` | Example: "Write a function to replace ..." -> "WRite a function to replace ... " |
| `Category E4: Grammatical Person Variation` | Example: "Write a function that replaces the ..." -> "Write a function that replace the ..." |
| `Category E5: Active and Passive Voice Variation` | Example: "Given a list of numbers, return whether or not they are sorted in ascending order." -> "Given a list of numbers, return whether or not they sort in ascending order." |
| `Category E6: Word Class Variation` | Example: "Write a function to check for the number of attempts required of ..." -> "Write a function to check for the number of jumps requirement of ..." |
| `Category E7: Synonym Substitution` | Example: "Write a function to find the index of ..." -> "Write a function to locate the index of ..." |
| `Category S1: Swap Ajacent Chars` | Example: "Write a function to reverse the string and ..." -> "Write a function to revesre the string and ..." |
| `Category S2: Swap Chars Randomly` | Example: "Write a function to reverse the string and ..." -> "Write a function to rrveese the string and ..." |
| `Category S3: Middle Random` | Example: "Write a function to reverse the string and ..." -> "Write a function to rsrveee the string and ..." |
| `Category S4: Fully Random` | Example: "Write a function to reverse the string and ..." -> "Write a function to esrveer the string and ..." |
| `Category S5: Swap Adjacent Words` | Example: "Write a function to reverse the string and ..." -> "Write a function reverse to the string and ..." |
| `Category P1: Rephrasing Sentence` | Example: "Write a python function to print even numbers from a list of numbers." -> "Generate a python function that can print even numbers from a list of numbers." |
| `Category P2: Declarative to Interrogative` | Example: "Write a python function to print even numbers from a list of numbers." -> "Can you write a function to print even numbers from a list of numbers?" |



