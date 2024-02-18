"""
Maliciousness Test
"""

import logging
import os
import sys
import warnings

from datasets import Dataset
from ragas import evaluate
from ragas.metrics.critique import maliciousness

# sys.stderr = open(os.devnull, "w", encoding="utf-8")
# warnings.filterwarnings("ignore")
# logging.getLogger("deepeval").setLevel(logging.ERROR)



def maliciousness_test(prompt, response, expected_output, context, model, threshold):
    """
    This metric checks maliciousness of LLM.

    Args:
        prompt (str): The prompt given to the model.
        response (str): The model's response to the prompt.
        expected_output (str): The expected output for comparison.
        context (str): The context or background information.
        model (str): The model to be used for evaluation (default is "gpt-3.5-turbo").
        threshold (float): The threshold for correctness score (default is 0.5).
    """

    data = {
        "ground_truths": [[expected_output]],
        "contexts": [[context]],
        "question": [prompt],
        "answer": [response],
    }

    dataset = Dataset.from_dict(data)
    scores = evaluate(dataset, [maliciousness])
    maliciousness_score = scores["maliciousness"]
    is_malicious = "Passed" if maliciousness_score > threshold else "Failed"

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "expected_output": expected_output,
        "context": context,
        "score": maliciousness_score,
        "is_passed": is_malicious,
        "threshold": threshold,
        "evaluated_with": {
            "expected_output": expected_output,
            "context": context,
            "model": model,
        },
    }

    return result
