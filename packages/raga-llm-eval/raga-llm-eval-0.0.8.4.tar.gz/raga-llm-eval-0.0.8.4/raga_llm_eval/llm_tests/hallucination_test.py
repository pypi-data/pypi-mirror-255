"""
Hallucination Test
"""

from deepeval.metrics import HallucinationMetric
from deepeval.test_case import LLMTestCase


def hallucination_test(
    prompt, response, context, model = "gpt-3.5-turbo", include_reason=True, threshold=0.5
):
    """
    Measures the hallucination score of the model's response compared to the context.

    Args:
        - prompt (str) : The prompt given to the model.
        - response (str) : The model's response to the prompt.
        - context (list) : The context provided to the model for the prompt.
        - model (str) : a string specifying which the model to be used (default is "gpt-3.5-turbo").
        - include_reason (bool) : a boolean which when set to True, will include a reason for its evaluation score (default is True).
        - threshold (float) : The threshold for the hallucination score (default is 0.5).
    Returns:
        - dict: A dictionary containing the prompt, response, score, threshold, and evaluation details.

    """

    # Create a test case
    test_case = LLMTestCase(
        input=prompt, actual_output=response, retrieval_context=context
    )

    # Create a Hallucination metric
    metric = HallucinationMetric(
        threshold=threshold, model=model, include_reason=include_reason
    )

    # Measure the Hallucination score
    metric.measure(test_case)
    hallucination_score = metric.score
    hallucination_reason = metric.reason if include_reason else None

    is_hallucinating = (
        "Passed" if hallucination_score > threshold else "Failed"
    )

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "context": context,
        "score": hallucination_score,
        "is_passed": is_hallucinating,
        "reason": hallucination_reason,
        "threshold": threshold,
        "evaluated_with": {"model": model, "include_reason": include_reason},
    }

    return result
