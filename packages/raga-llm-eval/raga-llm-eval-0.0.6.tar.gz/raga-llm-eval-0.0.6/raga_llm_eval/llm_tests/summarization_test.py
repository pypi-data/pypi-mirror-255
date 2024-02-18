"""
Summmarisation Test
"""

from deepeval.metrics import SummarizationMetric
from deepeval.test_case import LLMTestCase


def summarization_test(prompt, response, model, threshold):
    """
    The summarization metric determines whether your LLM is generating factually correct summaries while including the neccessary details from the original text

    Args:
        prompt (str): The prompt for the summary.
        response (str): The summary response to be evaluated.
        model (str): The LLM model to be used (default is 'gpt-3.5-turbo').
        threshold (float): The threshold for determining if the summary is good (default is 0.5).

    Returns:
        dict: A dictionary containing the prompt, response, summarization score,
              a boolean indicating if the summary is good, the threshold used,
              and the model evaluated with.
    """

    # Create a test case with the prompt and response
    test_case = LLMTestCase(input=prompt, actual_output=response)

    # Initialize the summarization metric with the given threshold and model
    metric = SummarizationMetric(
        threshold=threshold,
        model=model,
    )

    # Measure the summarization metric for the test case
    metric.measure(test_case)
    summarization_score = metric.score

    # Determine if the summary is good based on the threshold
    is_good_summary = "Passed" if summarization_score > threshold else "Failed"

    # Create a result dictionary with the prompt, response, summarization score,
    # boolean indicating if the summary is good, threshold, and model evaluated with
    result = {
        "prompt": prompt,
        "response": response,
        "score": summarization_score,
        "is_passed": is_good_summary,
        "threshold": threshold,
        "evaluated_with": {"model": model},
    }

    return result
