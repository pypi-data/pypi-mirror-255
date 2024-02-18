"""
Generic Evaluation Test
"""

import logging
import os
import sys
import warnings

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

# sys.stderr = open(os.devnull, "w", encoding="utf-8")
# warnings.filterwarnings("ignore")
# logging.getLogger("deepeval").setLevel(logging.ERROR)


def generic_evaluation_test(
    prompt,
    response,
    context,
    model,
    evaluation_name,
    evaluation_criteria,
    include_reason=False,
    threshold=0.5,
):
    """
    Create custom test to check if the response is based on the criteria mentioned in the evaluation criteria

    Args:
    - prompt (str): The prompt given to the model.
    - response (str): The model's response to the prompt.
    - context (str): The context provided to the model for the prompt.
    - model (str): The name of the model being evaluated (default is "gpt-3.5-turbo").
    - evaluation_name (str): A name to be provided to the evaluation metric
    - evaluation_criteria(str): A task based on which the response from model would be judged by the model
    - include_reason (bool): Whether to include the reason for the evaluation (default is True).
    - threshold (float): The threshold for determining faithfulness (default is 0.5).

    Returns:
    - dict: A dictionary containing the prompt, response, metric score, evaluation_name, evaluation_criteria,
        reason, threshold, and evaluation details.
    """

    # Create a test case
    test_case = LLMTestCase(input=prompt, actual_output=response, context=context)

    # Create the metric
    evaluation_metric = GEval(
        name=evaluation_name,
        criteria=evaluation_criteria,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )

    # Measure the relevancy
    evaluation_metric.measure(test_case)

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "context": context,
        "name": evaluation_metric.name,
        "score": evaluation_metric.score,
        "is_passed": evaluation_metric.score > threshold,
        "reason": evaluation_metric.reason if include_reason else None,
        "threshold": threshold,
        "evaluated_with": {"model": model, "include_reason": include_reason},
    }

    return result
