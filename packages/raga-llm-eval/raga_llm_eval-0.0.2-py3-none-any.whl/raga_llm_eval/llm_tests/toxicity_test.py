# sample implementation
def toxicity_test(prompt, response, parameter1, parameter2, threshold):
    """
    documentation for the test
    """
    # implementation
    toxicity_score = 0.6543

    is_toxic = "Passed" if toxicity_score > threshold else "Failed"

    result = {
        "prompt": prompt,
        "response": response,
        "score": toxicity_score,
        "is_passed": is_toxic,
        "threshold": threshold,
        "evaluated_with": {"parameter1": parameter1, "parameter2": parameter2},
    }

    return result
