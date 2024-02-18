"""
Consistency Check
"""

import logging
import os
import sys
import warnings

from langkit import response_hallucination
from langkit.openai import OpenAIDefault

# sys.stderr = open(os.devnull, "w", encoding="utf-8")
# warnings.filterwarnings("ignore")
# logging.getLogger("deepeval").setLevel(logging.ERROR)



def consistency_test(prompt, response="", model="gpt-3.5-turbo", threshold=0.5):
    """
    Provides a score for the consistency.
    Args:
    - prompt (str): The prompt given to the model.
    - response (str): The model's response to the prompt.
    - model (str): The name of the model being evaluated (default is "gpt-3.5-turbo").
    - threshold(float): The threshold score above this the prompt will be flagged as injection prompt.

    Returns:
    - dict: A dictionary containing the prompt, response, consistency_score, is_passed and threshold
    """
    response_hallucination.init(llm=OpenAIDefault(model=model))
    consistency_result = response_hallucination.consistency_check(
        prompt=prompt,
        response=response,
    )

    is_consistent = (
        "Passed" if consistency_result["final_score"] > threshold else "Failed"
    )

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "is_passed": is_consistent,
        "score": consistency_result["final_score"],
        "threshold": threshold,
    }

    return result
