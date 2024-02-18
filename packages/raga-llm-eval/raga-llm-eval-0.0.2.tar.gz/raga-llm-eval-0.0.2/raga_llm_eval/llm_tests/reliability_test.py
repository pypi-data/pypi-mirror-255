# sample implementation
def reliability_test(prompt, response, parameter1, parameter2, threshold):
    """
    documentation for the test
    """
    # implementation
    reliability_score = 0.6543

    is_reliable = "Passed" if reliability_score > threshold else "Failed"

    result = {
        "prompt": prompt,
        "response": response,
        "score": reliability_score,
        "is_passed": is_reliable,
        "threshold": threshold,
        "evaluated_with": {"parameter1": parameter1, "parameter2": parameter2},
    }

    return result
