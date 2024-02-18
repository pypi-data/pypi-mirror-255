"""
Answer Correctness Test
"""

import os

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_correctness


def answer_correctness_test(
    prompt, response, expected_response, context, model, threshold
):
    """
    Measures answer correctness compared to ground truth as a combination of
    factuality and semantic similarity.

    Args:
        - prompt list[str]: These are the questions your RAG pipeline will be evaluated on.
        - response list[str]: The answer generated from the RAG pipeline and given to the user.
        - expected_response list[list[str]]: The ground truth answer to the questions. (only required if you are using context_recall)
        - context list[list[str]]: The contexts which were passed into the LLM to answer the question.
        - model str: The name of the language model. (default is "gpt-3.5-turbo")
        - threshold float: The threshold for the answer correctness score. (default is 0.5)

    Returns:
        - dict: A dictionary containing the prompt, response, score, threshold, and evaluation details.

    """

    # Create a dictionary of the user inputs
    data = {
        "question": prompt,
        "answer": response,
        "contexts": context,
        "ground_truth": expected_response,
    }

    # Convert dict to dataset
    dataset = Dataset.from_dict(data)

    # Evaluate the prompts and responses for answer correctness
    result_dict = evaluate(
        dataset=dataset,
        metrics=[
            answer_correctness,
        ],
    )
    # df = result_dict.to_pandas()
    is_correct = "Passed" if result_dict["answer_correctness"] > threshold else "Failed"

    result = {
        "prompt": prompt,
        "response": response,
        "score": result_dict["answer_correctness"],
        "is_passed": is_correct,
        "threshold": threshold,
        "evaluated_with": {"model": model},
    }

    return result
