from datasets import Dataset
from ragas import evaluate
from ragas.metrics.critique import correctness


def correctness_test(
    prompt,
    response,
    expected_response,
    context,
    model="gpt-3.5-turbo",
    threshold=0.5,
):
    """
    This metric checks the correctness of your LLM response

    Args:
    prompt (str): The prompt for the response.
    response (str): The actual response to be evaluated.
    expected_response (str): The expected response for comparison.
    context (str): The context or background information.
    model (str): The model to be used for evaluation (default is "gpt-3.5-turbo").
    threshold (float): The threshold for correctness score (default is 0.5).

    Returns:
    dict: Result of the evaluation including correctness score, and other relevant information.
    """

    data = {
        "ground_truths": [[expected_response]],
        "contexts": [[context]],
        "question": [prompt],
        "answer": [response],
    }
    dataset = Dataset.from_dict(data)
    scores = evaluate(dataset, [correctness])
    correctness_score = scores["correctness"]

    is_correct = "Passed" if correctness_score > threshold else "Failed"

    # Prepare and return the result
    result = {
        "prompt": prompt,
        "response": response,
        "expected_response": expected_response,
        "context": context,
        "score": correctness_score,
        "is_passed": is_correct,
        "threshold": threshold,
        "evaluated_with": {"model": model},
    }

    return result


if __name__ == "__main__":
    prompt = "What is the capital of France?"
    response = "paris"
    expected_response = "Paris"
    context = "Paris is the capital of France."

    results = correctness_test(prompt, response, expected_response, context)
    print(results)
