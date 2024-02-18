# implementation of each test
def toxicity_test(
    prompt, response, expected_response, context, parameter1, parameter2, threshold=0.5
):
    """
    documentation for the test
    """
    # implementation
    toxicity_score = calculate_toxicity_score(response, parameter1, parameter2)

    is_toxic = toxicity_score > threshold

    result = {
        "prompt": prompt,
        "response": response,
        "toxicity_score": toxicity_score,
        "is_toxic": is_toxic,
        "threshold": threshold,
        "evaluated_with": {"parameter1": parameter1, "parameter2": parameter2},
    }

    return result
