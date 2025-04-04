import openai
import os
import time
from .my_util import *


os.environ["HTTP_PROXY"] = "http://127.0.0.1:X"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:X"
os.environ["http_proxy"] = "http://127.0.0.1:X"
os.environ["https_proxy"] = "http://127.0.0.1:X"
# Replace to your openai API key
openai.api_key = "XXX"


def convert_to_question(text):
    prompt = f"""You task is to change the imperative sentence in the docstring to an interrogative sentence. \
You should only change one sentence in the docstring and keep the rest such as restrictions and conditions unchanged. \
Do not change the format such as line breaks ans whitespaces.

For example:
[original docstring]
For a given list of input numbers, calculate Mean Absolute Deviation
    around the mean of this dataset.
    Mean Absolute Deviation is the average absolute difference between each
    element and a centerpoint (mean in this case):
    MAD = average | x - x_mean |

[modified prompt]
For a given list of input numbers, can you calculate Mean Absolute Deviation
    around the mean of this dataset?
    Mean Absolute Deviation is the average absolute difference between each
    element and a centerpoint (mean in this case):
    MAD = average | x - x_mean |

Now it's your turn:
[original docstring]
{text}

[modified prompt]
"""
    messages = [
        {"role": "system", "content": ""},
        {"role": "user", "content": f"{prompt}"},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8,
        top_p=0.95,
        max_tokens=200,
    )
    return (
        response["choices"][0]["message"]["content"]
        .strip()
        .rstrip("[Modified prompt]\n")
    )


def perturbate(prompt: str, seed):
    """
    P2 - declarative_to_interrogative

    Algorithm: LLM
    """
    retry_limit = 3
    while retry_limit > 0:
        try:
            response = convert_to_question(prompt)
            print(response)
            time.sleep(3)
            return response
        except Exception as e:
            print(e)
            retry_limit -= 1
            time.sleep(10)
    return prompt
