'''
Bias Test
'''

from deepeval.metrics import BiasMetric
from deepeval.test_case import LLMTestCase

def bias_test(
    prompt, response, threshold = 0.5
):
    """
    Measures the bias score of the model's response compared to the context.

    Args:
        - prompt (str) : The prompt given to the model.
        - response (str) : The model's response to the prompt.
        - threshold (float) : The threshold for the bias score (default is 0.5).
    Returns:
        - dict: A dictionary containing the prompt, response, score, and threshold.

    """

    # Create a test case
    test_case = LLMTestCase(
        input=prompt, actual_output=response
    )

    # Create a Bias metric
    metric = BiasMetric(
        threshold=threshold
    )

    # Measure the Bias score
    metric.measure(test_case)
    bias_score = metric.score

    is_biased = (
        "Passed" if bias_score > threshold else "Failed"
    )

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "score": bias_score,
        "is_passed": is_biased,
        "threshold": threshold,
    }

    return result