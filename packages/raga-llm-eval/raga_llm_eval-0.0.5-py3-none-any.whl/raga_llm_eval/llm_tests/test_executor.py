""""""

from . import (
    answer_relevancy_test,
    contextual_precision_test,
    contextual_recall_test,
    contextual_relevancy_test,
    faithfulness_test,
    summarization_test,
)


class TestExecutor:
    """
    Container class for the all the tests supported.
    """

    def __init__(self):
        """ """
        pass

    def run_answer_relevancy_test(self, test_data):
        """
        Run an answer relevancy test using the given test data.

        Parameters:
            self: the object itself
            test_data (dict): a dictionary containing the prompt, response, context, model, include_reason, and threshold

        Returns:
            The result of the answer relevancy test.
        """
        # TODO: Check of the parameters are valid

        res = answer_relevancy_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_contextual_precision_test(self, test_data):
        """
        A function to run a contextual precision test.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing the test data with keys:
                - "prompt": The prompt for the test.
                - "response": The response for the test.
                - "expected_response": The expected response for the test.
                - "context": The context for the test.
                - "model" (optional): The model for the test (default is "gpt-3.5-turbo").
                - "include_reason" (optional): Whether to include the reason for the result (default is True).
                - "threshold" (optional): The threshold for the test (default is 0.5).

        Returns:
            The result of the contextual precision test.
        """
        # TODO: Check of the parameters are valid

        res = contextual_precision_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            expected_response=test_data["expected_response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_contextual_recall_test(self, test_data):
        """
        A function to run contextual recall test.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing test data with the following keys:
                - prompt (str): The prompt text.
                - response (str): The response text.
                - expected_response (str): The expected response text.
                - context (str): The context for the test.
                - model (str, optional): The model to use for the test. Defaults to "gpt-3.5-turbo".
                - include_reason (bool, optional): Whether to include reason in the test. Defaults to True.
                - threshold (float, optional): The threshold for the test. Defaults to 0.5.

        Returns:
            The result of the contextual recall test.
        """
        # TODO: Check of the parameters are valid

        res = contextual_recall_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            expected_response=test_data["expected_response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_contextual_relevancy_test(self, test_data):
        """
        A function to run a contextual relevancy test using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the test data with keys "prompt", "response", "context", "model", "include_reason", and "threshold"

        Returns:
            The result of the contextual relevancy test
        """
        # TODO: Check of the parameters are valid

        res = contextual_relevancy_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_faithfulness_test(self, test_data):
        """
        A function to run a faithfulness test on the given test data.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing the test data with the following keys:
                - "prompt": The prompt for the test.
                - "response": The response for the test.
                - "context": The context for the test.
                - "model" (optional): The model for the test. Defaults to "gpt-3.5-turbo".
                - "include_reason" (optional): Whether to include reason in the test. Defaults to True.
                - "threshold" (optional): The threshold for the test. Defaults to 0.5.

        Returns:
            The result of the faithfulness test.
        """
        # TODO: Check of the parameters are valid

        res = faithfulness_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_summarization_test(self, test_data):
        """
        Run a summarization test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing prompt, response, model, and threshold.

        Returns:
            The result of the summarization test.
        """
        # TODO: Check of the parameters are valid

        res = summarization_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res
