# sample implementation
def biasness_test(prompt, response, parameter1, parameter2, threshold):
    """
    documentation for the test
    """
    # implementation
    biasness_score = 0.6543

    is_biased = "Passed" if biasness_score > threshold else "Failed"

    result = {
        "prompt": prompt,
        "response": response,
        "score": biasness_score,
        "is_passed": is_biased,
        "threshold": threshold,
        "evaluated_with": {"parameter1": parameter1, "parameter2": parameter2},
    }

    return result
