"""
Detect Prompt injection
"""

import logging
import os
import sys
import warnings

from langkit import extract, injections

# sys.stderr = open(os.devnull, "w", encoding="utf-8")
# warnings.filterwarnings("ignore")



def prompt_injection_test(prompt, threshold=0.5):
    """
    Provides a score for the prompt being a jailbreak or injection prompt.
    Prompt injection is used to get output from model against which guardrails are put

    Args:
    - prompt (str): The prompt given to the model.
    - threshold(float): The threshold score above this the prompt will be flagged as injection prompt.

    Returns:
    - dict: A dictionary containing the prompt, injection_score, threshold and
    boolean if prompt score was more than threshold

    """

    # Create a test case
    schema = injections.init()
    result = extract({"prompt": prompt}, schema=schema)

    injection_score = result["prompt.injection"]
    is_breakable = "Passed" if result["prompt.injection"] > threshold else "Failed"

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "threshold": threshold,
        "is_passed": is_breakable,
        "score": injection_score,
    }

    return result
