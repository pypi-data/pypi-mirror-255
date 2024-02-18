"""
Contextual Precision Test
"""

import logging
import os
import sys
import warnings

from deepeval.metrics import ContextualPrecisionMetric
from deepeval.test_case import LLMTestCase

# sys.stderr = open(os.devnull, "w", encoding="utf-8")
# warnings.filterwarnings("ignore")
# logging.getLogger("deepeval").setLevel(logging.ERROR)




def contextual_precision_test(
    prompt,
    response,
    expected_response,
    context,
    model,
    include_reason,
    threshold,
):
    """
    The contextual precision metric measures your LLM model by evaluating whether nodes in your retrieval_context that are relevant to the given input prompt are ranked higher than irrelevant ones

    Args:
    prompt (str): The prompt given to the model.
    response (str): The model's response to the prompt.
    expected_response (str): The expected response to the prompt.
    context (str): The context in which the prompt and response are given.
    model (str, optional): The model to evaluate the response. Defaults to "gpt-3.5-turbo".
    include_reason (bool, optional): Whether to include the reason for the evaluation. Defaults to True.
    threshold (float, optional): The threshold for the contextual precision score. Defaults to 0.5.

    Returns:
    dict: A dictionary containing the evaluation result.
    """
    # Create a test case
    test_case = LLMTestCase(
        input=prompt,
        actual_output=response,
        expected_output=expected_response,
        retrieval_context=context,
    )

    # Create a relevancy metric
    metric = ContextualPrecisionMetric(
        threshold=threshold, model=model, include_reason=include_reason
    )

    # Measure the relevancy
    metric.measure(test_case)
    contextual_precision_score = metric.score
    contextual_precision_reason = metric.reason if include_reason else None

    is_contextually_precise = (
        "Passed" if contextual_precision_score > threshold else "Failed"
    )

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "expected_response": expected_response,
        "context": context,
        "score": contextual_precision_score,
        "is_passed": is_contextually_precise,
        "reason": contextual_precision_reason,
        "threshold": threshold,
        "evaluated_with": {"model": model, "include_reason": include_reason},
    }

    return result
