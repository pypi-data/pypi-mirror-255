"""
Contextual Relevancy Test
"""

import logging
import os
import sys
import warnings

from deepeval.metrics import ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase

# sys.stderr = open(os.devnull, "w", encoding="utf-8")
# warnings.filterwarnings("ignore")
# logging.getLogger("deepeval").setLevel(logging.ERROR)




def contextual_relevancy_test(
    prompt, response, context, model, include_reason, threshold
):
    """
    The contextual relevancy metric measures the quality of your LLM model by evaluating the overall relevance of the information presented in your retrieval_context for a given input prompt

     Args:
     - prompt (str): The prompt given to the model.
     - response (str): The model's response to the prompt.
     - context (list): The context provided to the model for the prompt.
     - model (str): The name of the model being evaluated (default is "gpt-3.5-turbo").
     - include_reason (bool): Whether to include the reason for the evaluation (default is True).
     - threshold (float): The threshold for determining relevancy (default is 0.5).

     Returns:
     - dict: A dictionary containing the prompt, response, context, contextual relevancy score, whether the response is contextually relevant, contextual relevancy reason, threshold, and evaluation details.
    """

    # Create a test case
    test_case = LLMTestCase(
        input=prompt, actual_output=response, retrieval_context=context
    )

    # Create a relevancy metric
    metric = ContextualRelevancyMetric(
        threshold=threshold, model=model, include_reason=include_reason
    )

    # Measure the relevancy
    metric.measure(test_case)
    contextual_relevancy_score = metric.score
    contextual_relevancy_reason = metric.reason if include_reason else None

    is_contextually_relevant = (
        "Passed" if contextual_relevancy_score > threshold else "Failed"
    )

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "context": context,
        "score": contextual_relevancy_score,
        "is_passed": is_contextually_relevant,
        "reason": contextual_relevancy_reason,
        "threshold": threshold,
        "evaluated_with": {"model": model, "include_reason": include_reason},
    }

    return result
