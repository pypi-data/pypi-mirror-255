"""
Contextual Recall Test
"""

import logging
import os
import sys
import warnings

from deepeval.metrics import ContextualRecallMetric
from deepeval.test_case import LLMTestCase

# sys.stderr = open(os.devnull, "w", encoding="utf-8")
# warnings.filterwarnings("ignore")
# logging.getLogger("deepeval").setLevel(logging.ERROR)




def contextual_recall_test(
    prompt,
    response,
    expected_response,
    context,
    model,
    include_reason,
    threshold,
):
    """
    The contextual recall metric measures the quality of your LLM model by evaluating the extent of which the retrieval_context aligns with the expected_response

    Args:
    prompt (str): The prompt for the response.
    response (str): The actual response to be evaluated.
    expected_response (str): The expected response for comparison.
    context (str): The context or background information.
    model (str): The model to be used for evaluation (default is "gpt-3.5-turbo").
    include_reason (bool): Whether to include the reason for evaluation (default is True).
    threshold (float): The threshold for relevancy score (default is 0.5).

    Returns:
    dict: Result of the evaluation including contextual recall score, reason, and other relevant information.
    """
    # Create a test case
    test_case = LLMTestCase(
        input=prompt,
        actual_output=response,
        expected_output=expected_response,
        retrieval_context=context,
    )

    # Create a relevancy metric
    metric = ContextualRecallMetric(
        threshold=threshold, model=model, include_reason=include_reason
    )

    # Measure the relevancy
    metric.measure(test_case)
    contextual_recall_score = metric.score
    contextual_recall_reason = metric.reason if include_reason else None

    have_contextual_recall = (
        "Passed" if contextual_recall_score > threshold else "Failed"
    )

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "expected_response": expected_response,
        "context": context,
        "score": contextual_recall_score,
        "recall": have_contextual_recall,
        "reason": contextual_recall_reason,
        "threshold": threshold,
        "evaluated_with": {"model": model, "include_reason": include_reason},
    }

    return result
