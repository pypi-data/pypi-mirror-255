"""
Answer Relevancy Test
"""

import logging
import os
import sys
import warnings

from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

# sys.stderr = open(os.devnull, "w", encoding="utf-8")
# warnings.filterwarnings("ignore")
# logging.getLogger("deepeval").setLevel(logging.ERROR)



def answer_relevancy_test(prompt, response, context, model, include_reason, threshold):
    """
    The answer relevancy metric measures the quality of your LLM by evaluating how relevant the response of your LLM application is compared to the provided input prompt

    Args:
        prompt (str): The input prompt for the LLM.
        response (str): The actual output of the LLM.
        context (str): The retrieval context for the LLM.
        model (str, optional): The name of the language model. Defaults to "gpt-3.5-turbo".
        include_reason (bool, optional): Flag to include the reason for relevancy measurement. Defaults to True.
        threshold (float, optional): The threshold for relevancy score. Defaults to 0.5.

    Returns:
        dict: A dictionary containing the evaluation results.
    """

    # Create a test case
    test_case = LLMTestCase(
        input=prompt, actual_output=response, retrieval_context=context
    )

    # Create a relevancy metric
    metric = AnswerRelevancyMetric(
        threshold=threshold, model=model, include_reason=include_reason
    )

    # Measure the relevancy
    metric.measure(test_case)
    relevancy_score = metric.score
    relevancy_reason = metric.reason if include_reason else None

    is_relevant = "Passed" if relevancy_score > threshold else "Failed"

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "context": context,
        "score": relevancy_score,
        "is_passed": is_relevant,
        "reason": relevancy_reason,
        "threshold": threshold,
        "evaluated_with": {"model": model, "include_reason": include_reason},
    }

    return result
