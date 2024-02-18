import json
import openai
import warnings
from prettytable import PrettyTable

from .llm_tests import reliability_test, biasness_test, toxicity_test


class RagaLLMEval:
    def __init__(self, api_keys=None):
        """
        Constructor for the API key manager.

        Args:
            api_keys (dict, optional): A dictionary containing API keys for OpenAI and Hugging Face Hub. Defaults to None.

        Attributes:
            __open_ai_api_key (str): The OpenAI API key.
            __hugging_face_hub_api_token (str): The Hugging Face Hub API token.
            supported_tests (dict): A dictionary containing descriptions and expected arguments for supported tests.
            _test_methods (dict): A dictionary mapping test names to their corresponding methods.
            _tests_to_execute (list): A list of test names to be executed.
            _results (list): A list to store the results of the executed tests.
        """
        self.__open_ai_api_key = api_keys.get("OPENAI_API_KEY") if api_keys else None
        self.__hugging_face_hub_api_token = (
            api_keys.get("HUGGINGFACEHUB_API_TOKEN") if api_keys else None
        )

        self.supported_tests = {
            "reliability_test": {
                "description": "Tests for the reliability of the response.",
                "expected arguments": "prompt, response",
                "expected output": "A score indicating reliability.",
                "interpretation": "A higher score indicates higher reliability.",
            },
            "biasness_test": {
                "description": "Evaluates the response for any bias.",
                "expected arguments": "prompt, response",
                "expected output": "A score indicating level of bias.",
                "interpretation": "A lower score indicates lesser bias.",
            },
            "toxicity_test": {
                "description": "Assesses the response for toxicity levels.",
                "expected arguments": "prompt, response",
                "expected output": "A score indicating toxicity levels.",
                "interpretation": "A lower score indicates lesser toxicity.",
            },
        }
        self._test_methods = {
            "reliability_test": self._run_reliability_test,
            "biasness_test": self._run_biasness_test,
            "toxicity_test": self._run_toxicity_test,
        }
        self._tests_to_execute = []
        self._results = []

    def list_available_tests(self):
        """
        List available tests and their details in a formatted table.
        """
        table = PrettyTable()
        table.field_names = [
            "Test Name",
            "Description",
            "Expected Arguments",
            "Expected Output",
            "Interpretation",
        ]

        for test_name, details in self.supported_tests.items():
            table.add_row(
                [
                    test_name,
                    details["description"],
                    details["expected arguments"],
                    details["expected output"],
                    details["interpretation"],
                ]
            )

        print(table)

    def add_test(
        self,
        name,
        prompt,
        response,
        expected_response=None,
        context=None,
        test_arguments=None,
    ):
        """
        A function to add a test to the test suite.

        Args:
            name (str): The name of the test.
            prompt (str): The prompt for the test.
            response (str): The response for the test.
            expected_response (str, optional): The expected response for the test. Defaults to None.
            context (str, optional): The context for the test. Defaults to None.
            test_arguments (list, optional): Additional arguments for the test. Defaults to None.

        Returns:
            self: The instance of the test suite with the added test.
        """
        if name not in self.supported_tests:
            raise ValueError(
                f"Test {name} is not supported. Supported tests are \
                    {list(self.supported_tests.keys())}"
            )

        self._tests_to_execute.append(
            {
                "test_name": name,
                "prompt": prompt,
                "response": response,
                "expected_response": expected_response,
                "context": context,
                "test_arguments": test_arguments,
            }
        )

        return self

    def set_output_format(self, output_format):
        """
        Set the output format for the object.

        Parameters:
            output_format (str): The desired output format, can be 'detailed' or 'summary'.

        Returns:
            self: The updated object with the new output format.
        """
        # check if output format is one of detailed or summary, share warning with the user and use output_format="summary"
        if output_format not in ["detailed", "summary"]:
            warnings.warn(
                f"Output format {output_format} is not supported. Supported output formats are 'detailed' and 'summary'"
            )
            output_format = "summary"  # default to summary

        self._output_format = output_format

        return self

    def run(self):
        """
        Run the tests in the test suite.
        """
        if not self._tests_to_execute:
            raise ValueError("No tests to execute.")
        for test_details in self._tests_to_execute:
            test_name = test_details["test_name"]
            if test_name in self._test_methods:
                method = self._test_methods[test_name]
                result = method(test_details)
                result["test_name"] = test_name
                self._results.append(result)
            else:
                warnings.warn(f"Warning: Test method for {test_name} not implemented.")
        return self

    def print_results(self):
        """
        A method to print the results in a pretty table format.
        """

        table = PrettyTable()
        table.field_names = ["Test Name", "Parameters", "Score", "Result", "Threshold"]

        # Fill the table with data from _results
        for test_data in self._results:
            test_name = test_data["test_name"]
            parameters = test_data["evaluated_with"]
            score = test_data["score"]
            result = test_data["is_passed"]
            threshold = test_data["threshold"]

            # Formatting parameters and result for display
            parameters_str = ", ".join([f"{k}: {v}" for k, v in parameters.items()])

            score = test_data["score"]

            table.add_row([test_name, parameters_str, score, result, threshold])

        # Print the table in a pretty format
        print(table)

        return self

    def save_results(self, file_path):
        """
        Save the results to a specified file in JSON format.

        Args:
            file_path (str): The path to the file where the results will be saved.

        Returns:
            None
        """
        # Convert the results dictionary to a JSON string
        results_json = json.dumps(self._results, indent=4)

        # Write the JSON string to the specified file
        with open(file_path, "w") as file:
            file.write(results_json)

        print(f"Results saved to {file_path}")

    def _run_reliability_test(self, test_data):
        """
        A reliability test function that takes test data as input and returns the result.
        """
        # TODO: Check of the parameters are valid
        res = reliability_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            parameter1=test_data["test_arguments"]["parameter1"],
            parameter2=test_data["test_arguments"]["parameter2"],
            threshold=test_data.get("threshold", 0.5),
        )
        # TODO: Check if the results are in the desired form
        return res

    def _run_biasness_test(self, test_data):
        """
        A function to run biasness test on the provided test data.

        Parameters:
            self: the object instance
            test_data: a dictionary containing the prompt, response, and test arguments

        Returns:
            The result of the biasness test.
        """
        # TODO: Check of the parameters are valid
        res = biasness_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            parameter1=test_data["test_arguments"]["parameter1"],
            parameter2=test_data["test_arguments"]["parameter2"],
            threshold=test_data.get("threshold", 0.5),
        )
        # TODO: Check if the results are in the desired form
        return res

    def _run_toxicity_test(self, test_data):
        """
        A function to run a toxicity test on the provided test data.

        Parameters:
            self: the object itself
            test_data: a dictionary containing the prompt, response, test arguments, and threshold

        Returns:
            The result of the toxicity test
        """
        # TODO: Check of the parameters are valid
        res = toxicity_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            parameter1=test_data["test_arguments"]["parameter1"],
            parameter2=test_data["test_arguments"]["parameter2"],
            threshold=test_data.get("threshold", 0.5),
        )
        # TODO: Check if the results are in the desired form
        return res
