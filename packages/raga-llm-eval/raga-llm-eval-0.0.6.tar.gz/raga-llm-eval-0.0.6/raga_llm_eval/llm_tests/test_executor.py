"""
Container code for all the test runners
"""

from . import (answer_correctness_test, answer_relevancy_test, coherence_test,
               conciseness_test, consistency_test, contextual_precision_test,
               contextual_recall_test, contextual_relevancy_test,
               correctness_test, cover_test, faithfulness_test,
               generic_evaluation_test, length_test, maliciousness_test,
               pos_test, prompt_injection_test, sentiment_analysis_test,
               summarization_test, toxicity_test, winner_test)


class TestExecutor:
    """
    Container class for the all the tests supported.
    """

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

    def run_maliciousness_test(self, test_data):
        """
        Run a summarization test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing prompt, response, model, and threshold.

        Returns:
            The result of the summarization test.
        """
        # TODO: Check of the parameters are valid

        res = maliciousness_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            expected_output=test_data["expected_output"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
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

    def run_prompt_injection_test(self, test_data):
        """
        Run prompt injection test using the given test data.

        Parameters:
            self: the object itself
            test_data (dict): a dictionary containing the prompt and threshold

        Returns:
            The result of the prompt injection test.
        """
        # TODO: Check of the parameters are valid

        res = prompt_injection_test(
            prompt=test_data["prompt"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_sentiment_analysis_test(self, test_data):
        """
        Run sentiment analysis test using the given test data.

        Parameters:
            self: the object itself
            test_data (dict): a dictionary containing the response and threshold

        Returns:
            The result of the response sentiment test.
        """
        # TODO: Check of the parameters are valid

        res = sentiment_analysis_test(
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_toxicity_test(self, test_data):
        """
        Run toxicity test using the given test data.

        Parameters:
            self: the object itself
            test_data (dict): a dictionary containing the response and threshold

        Returns:
            The result of the response toxicity test.
        """
        # TODO: Check of the parameters are valid

        res = toxicity_test(
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_conciseness_test(self, test_data):
        """
        A function to run conciseness test.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing test data with the following keys:
                - prompt (str): The prompt text.
                - response (str): The response text.
                - expected_response (str): The expected response text.
                - context (str): The context for the test.
                - model (str, optional): The model to use for the test. Defaults to "gpt-3.5-turbo".
                - threshold (float, optional): The threshold for the test. Defaults to 0.5.

        Returns:
            The result of the conciseness test.
        """
        # TODO: Check of the parameters are valid

        res = conciseness_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            expected_response=test_data["expected_response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_coherence_test(self, test_data):
        """
        A function to run coherence test.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing test data with the following keys:
                - prompt (str): The prompt text.
                - response (str): The response text.
                - expected_response (str): The expected response text.
                - context (str): The context for the test.
                - model (str, optional): The model to use for the test. Defaults to "gpt-3.5-turbo".
                - threshold (float, optional): The threshold for the test. Defaults to 0.5.

        Returns:
            The result of the coherence test.
        """
        # TODO: Check of the parameters are valid

        res = coherence_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            expected_response=test_data["expected_response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_correctness_test(self, test_data):
        """
        A function to run correctness test.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing test data with the following keys:
                - prompt (str): The prompt text.
                - response (str): The response text.
                - expected_response (str): The expected response text.
                - context (str): The context for the test.
                - model (str, optional): The model to use for the test. Defaults to "gpt-3.5-turbo".
                - threshold (float, optional): The threshold for the test. Defaults to 0.5.

        Returns:
            The result of the correctness test.
        """
        # TODO: Check of the parameters are valid

        res = correctness_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            expected_response=test_data["expected_response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_consistency_test(self, test_data):
        """
        A function to run a consistency test on the given test data.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing the test data with the following keys:
                - prompt (str): The prompt given to the model.
                - response (str): The model's response to the prompt.
                - model (str): The name of the model being evaluated (default is "gpt-3.5-turbo").
                - threshold(float): The threshold score above this the prompt will be flagged as injection prompt.

        Returns:
            The result of the consistency test.
        """
        # TODO: Check of the parameters are valid

        res = consistency_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_cover_test(self, test_data):
        """
        Run a cover_test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response, concept set.

        Returns:
            The result of the cover test.
        """
        # TODO: Check of the parameters are valid
        res = cover_test(
            response=test_data["response"],
            concept_set=test_data["concept_set"],
        )
        # TODO: Check if the results are in the desired form
        return res

    def run_pos_test(self, test_data):
        """
        Run a pos_test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response, concept set.

        Returns:
            The result of the pos test.
        """
        # TODO: Check of the parameters are valid
        res = pos_test(
            response=test_data["response"],
            concept_set=test_data["concept_set"],
        )
        # TODO: Check if the results are in the desired form
        return res

    def run_length_test(self, test_data):
        """
        Run a length_test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response.

        Returns:
            The result of the length test.
        """
        # TODO: Check of the parameters are valid
        res = length_test(
            response=test_data["response"],
        )
        # TODO: Check if the results are in the desired form
        return res

    def run_winner_test(self, test_data):
        """
        Run a winner_test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response, ground_truth, concept_set, model, temperature, max_tokens.


        Returns:
            The result of the winner test.
        """
        # TODO: Check of the parameters are valid
        res = winner_test(
            response=test_data["response"],
            expected_response=test_data["expected_response"],
            concept_set=test_data["concept_set"],
            model=test_data["test_arguments"]["model"],
            temperature=test_data["test_arguments"]["temperature"],
            max_tokens=test_data["test_arguments"]["max_tokens"],
        )
        # TODO: Check if the results are in the desired form
        return res

    def run_answer_correctness_test(self, test_data):
        """
        Run an answer correctness test using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the test data with keys "prompt", "response", "expected_response", "context", "model", and "threshold".
        Returns:
            The result of the answer correctness test.
        """

        res = answer_correctness_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            expected_response=test_data["expected_response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        return res

    def run_generic_evaluation_test(self, test_data):
        """
        Run a generic test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing prompt, response, model name to use for evaluation,
            evalutaion_name, evaluation criteria, reason to include and threshold to apply


        Returns:
            The result of the evaluation test.
        """
        # TODO: Check of the parameters are valid
        res = generic_evaluation_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            context=test_data["context"],
            model=test_data["model"],
            evaluation_name=test_data["evaluation_name"],
            evaluation_criteria=test_data["evaluation_criteria"],
            include_reason=test_data["reason"],
            threshold=test_data["threshold"],
        )
        # TODO: Check if the results are in the desired form
        return res
