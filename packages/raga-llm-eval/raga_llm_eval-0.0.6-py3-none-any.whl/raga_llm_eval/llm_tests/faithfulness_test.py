"""
Faithfulness Test
"""

import logging
import os
import sys
import warnings

from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

# sys.stderr = open(os.devnull, "w", encoding="utf-8")
# warnings.filterwarnings("ignore")
# logging.getLogger("deepeval").setLevel(logging.ERROR)




def faithfulness_test(prompt, response, context, model, include_reason, threshold):
    """
    Test the faithfulness of whether the response genereted by LLM factually aligns with the contents of retrieval_context

    Args:
    - prompt (str): The prompt given to the model.
    - response (str): The model's response to the prompt.
    - context (str): The context provided to the model for the prompt.
    - model (str): The name of the model being evaluated (default is "gpt-3.5-turbo").
    - include_reason (bool): Whether to include the reason for the evaluation (default is True).
    - threshold (float): The threshold for determining faithfulness (default is 0.5).

    Returns:
    - dict: A dictionary containing the prompt, response, relevancy score, whether it's relevant, relevancy reason, threshold, and evaluation details.
    """

    # Create a test case
    test_case = LLMTestCase(
        input=prompt, actual_output=response, retrieval_context=context
    )

    # Create a relevancy metric
    metric = FaithfulnessMetric(
        threshold=threshold, model=model, include_reason=include_reason
    )

    # Measure the relevancy
    metric.measure(test_case)
    faithfulness_score = metric.score
    faithfulness_reason = metric.reason if include_reason else None

    is_faithful = "Passed" if faithfulness_score > threshold else "Failed"

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "context": context,
        "score": faithfulness_score,
        "is_passed": is_faithful,
        "reason": faithfulness_reason,
        "threshold": threshold,
        "evaluated_with": {"model": model, "include_reason": include_reason},
    }

    return result
