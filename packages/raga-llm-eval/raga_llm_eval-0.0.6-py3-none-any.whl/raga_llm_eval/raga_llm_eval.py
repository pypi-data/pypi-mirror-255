"""
Main Function for RagaLLMEval
"""

import json
import os
import warnings

from prettytable import ALL, PrettyTable

from .llm_tests.test_executor import TestExecutor
from .utils import load_supported_tests


class RagaLLMEval:
    """
    Class for managing the API keys and executing tests.
    """

    config_file = "raga_llm_eval/llm_tests/test_details.toml"

    def __init__(self, api_keys=None):
        """
        Constructor for the API key manager.

        Args:
            api_keys (dict, optional): A dictionary containing API keys for
                            OpenAI and Hugging Face Hub. Defaults to None.

        Attributes:
            __open_ai_api_key (str): The OpenAI API key.
            __hugging_face_hub_api_token (str): The Hugging Face Hub API token.
            supported_tests (dict): A dictionary containing descriptions and
                                    expected arguments for supported tests.
            _test_methods (dict): A dictionary mapping test names to their
                                  corresponding methods.
            _tests_to_execute (list): A list of test names to be executed.
            _results (list): A list to store the results of the executed tests.
        """
        self.__set_api_keys(api_keys=api_keys)

        self.test_executor = TestExecutor()

        self._results = []
        self._tests_to_execute = []
        self._output_format = "summary"
        self.supported_tests = load_supported_tests(config_file=self.config_file)

        self._test_methods = {
            "answer_relevancy_test": self.test_executor.run_answer_relevancy_test,
            "contextual_precision_test": self.test_executor.run_contextual_precision_test,
            "contextual_recall_test": self.test_executor.run_contextual_recall_test,
            "contextual_relevancy_test": self.test_executor.run_contextual_relevancy_test,
            "faithfulness_test": self.test_executor.run_faithfulness_test,
            "maliciousness_test": self.test_executor.run_maliciousness_test,
            "summarization_test": self.test_executor.run_summarization_test,
            "coherence_test": self.test_executor.run_coherence_test,
            "conciseness_test": self.test_executor.run_conciseness_test,
            "correctness_test": self.test_executor.run_correctness_test,
            "consistency_test": self.test_executor.run_consistency_test,
            "length_test": self.test_executor.run_length_test,
            "cover_test": self.test_executor.run_cover_test,
            "pos_test": self.test_executor.run_pos_test,
            "toxicity_test": self.test_executor.run_toxicity_test,
            "winner_test": self.test_executor.run_winner_test,
            "prompt_injection_test": self.test_executor.run_prompt_injection_test,
            "sentiment_analysis_test": self.test_executor.run_sentiment_analysis_test,
            "generic_evaluation_test": self.test_executor.run_generic_evaluation_test,
        }

        self.__welcome_message()

    def __welcome_message(self):
        print("🌟 Welcome to raga_llm_eval! 🌟")
        print(
            "The most comprehensive LLM (Large Language Models) testing library at your service."
        )
        print(
            "We're thrilled to have you on board and can't wait to help you test and evaluate your models. Let's achieve greatness together! ✨"
        )

    def __set_api_keys(self, api_keys):
        """
        Set the API keys for OpenAI and Hugging Face Hub.

        Parameters:
            api_keys (dict): A dictionary containing the API keys for OpenAI and Hugging Face Hub.

        Returns:
            None
        """
        open_ai_api_key = (
            api_keys.get("OPENAI_API_KEY")
            if api_keys and "OPENAI_API_KEY" in api_keys
            else os.getenv("OPENAI_API_KEY", None)
        )
        hugging_face_hub_api_token = (
            api_keys.get("HUGGINGFACEHUB_API_TOKEN")
            if api_keys and "HUGGINGFACEHUB_API_TOKEN" in api_keys
            else os.getenv("HUGGINGFACEHUB_API_TOKEN", None)
        )

        if open_ai_api_key:
            os.environ["OPENAI_API_KEY"] = open_ai_api_key

        if hugging_face_hub_api_token:
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = hugging_face_hub_api_token

    def list_available_tests(self):
        """
        List available tests and their details in a formatted table.
        """
        table = PrettyTable()
        table.field_names = [
            "SNo.",
            "Test Name",
            "Description",
            "Expected Arguments",
            "Expected Output",
            "Interpretation",
        ]
        table._max_width = {
            "SNo.": 5,
            "Test Name": 15,
            "Description": 25,
            "Expected Arguments": 20,
            "Expected Output": 20,
            "Interpretation": 20,
        }
        table.hrules = ALL

        for idx, (test_name, details) in enumerate(self.supported_tests.items()):
            table.add_row(
                [
                    idx,
                    test_name,
                    details["description"],
                    details["expected_arguments"],
                    details["expected_output"],
                    details["interpretation"],
                ]
            )

        print(table)

    def print_results(self):
        """
        A method to print the results in a pretty table format, creating a separate table for each test type,
        and mapping internal key names to user-friendly column names for display.
        """

        # Mapping of internal key names to display names
        key_name_mapping = {
            "test_name": "Test Name",
            "prompt": "Prompt",
            "response": "Response",
            "evaluated_with": "Parameters",
            "score": "Score",
            "is_passed": "Result",
            "threshold": "Threshold",
            "context": "Context",
            "concept_set": "Concept Set",
            "test_arguments": "Test Arguments",
            "expected_response": "Expected Response",
        }

        # Group data by test names
        test_groups = {}
        for test_data in self._results:
            test_name = test_data.get("test_name", "Unknown Test Name")
            if test_name not in test_groups:
                test_groups[test_name] = []
            test_groups[test_name].append(test_data)

        # Iterate over each test group and create a table
        for test_name, test_datas in test_groups.items():
            print(f"\nTest Name: {test_name}\n")

            # Dynamically determine all keys (field names) present across test datas in the group
            all_keys = set()
            for test_data in test_datas:
                all_keys.update(test_data.keys())

            # Use mapped names for base fields and dynamic keys for complete field names list
            field_names = [key_name_mapping.get(key, key) for key in all_keys]

            # Initialize table with the mapped field names
            table = PrettyTable()
            table.field_names = field_names

            # Set max width for each column. Adjust these values as needed.
            table._max_width = {
                name: 25 for name in field_names
            }  # Example: limit max width to 25 characters
            table.hrules = ALL

            # Fill the table with data specific to the current test group
            for test_data in test_datas:
                row = []
                for key in all_keys:
                    if key == "evaluated_with":
                        # Convert dict to string for 'evaluated_with'
                        value = ", ".join(
                            [f"{k}: {v}" for k, v in test_data.get(key, {}).items()]
                        )
                        row.append(value)
                    else:
                        # Use mapped name for the column if available
                        value = test_data.get(key, "")
                        row.append(value)

                # Add the row to the table
                table.add_row(row)

            # Print the table for the current test group
            print(table)

        return self

    def add_test(
        self,
        name,
        prompt,
        response,
        expected_response=None,
        context=None,
        concept_set=None,
        test_arguments=None,
    ):
        """
        A function to add a test or multiple tests to the test suite.

        Args:
            name (str or list): The name of the test or a list of test names.
            prompt (str or list): The prompt for the test or a list of prompts.
            response (str or list): The response for the test or a list of responses.
            expected_response (str or list, optional): The expected response for the test or a list of expected responses. Defaults to None.
            context (str, optional): The context for the test. Defaults to None.
            test_arguments (list, optional): Additional arguments for the test. Defaults to None.

        Returns:
            self: The instance of the test suite with the added test(s).
        """
        # Ensure 'name' is a list for consistent processing
        if isinstance(name, str):
            name = [name]

        # Validate all test names are supported
        unsupported_tests = [test for test in name if test not in self.supported_tests]
        if unsupported_tests:
            raise ValueError(
                f"Test(s) {unsupported_tests} is/are not supported. Supported tests are {list(self.supported_tests.keys())}"
            )

        # convert single inputs to lists to handle them uniformly
        if isinstance(prompt, str):
            prompt = [prompt]
        if isinstance(response, str):
            response = [response]
        if expected_response is None:
            expected_response = [None] * len(prompt)
        elif isinstance(expected_response, str):
            expected_response = [expected_response]
        if isinstance(context, str):
            context = [context]
        if not isinstance(concept_set, list) and concept_set is not None:
            raise ValueError("Concept set must be a list of concepts")

        # Ensure prompt, response, and expected_response have the same length
        if not len(prompt) == len(response) == len(expected_response):
            raise ValueError(
                "Prompt, response, and expected response lists must have the same length."
            )

        # Iterate over inputs to add each test
        for cur_prompt, cur_response, cur_expected_response in zip(
            prompt, response, expected_response
        ):

            for test_name in name:
                self._tests_to_execute.append(
                    {
                        "test_name": test_name,
                        "prompt": cur_prompt,
                        "response": cur_response,
                        "expected_response": cur_expected_response,
                        "context": context,
                        "concept_set": concept_set,
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

        self._output_format = output_format

        return self

    def run(self):
        """
        Run the tests in the test suite.
        """
        if not self._tests_to_execute:
            raise ValueError("🚫 No tests to execute.")

        for test_details in self._tests_to_execute:
            test_name = test_details["test_name"]
            if isinstance(test_name, str):
                test_name = [test_name]

            for each_test in test_name:
                if each_test in self._test_methods:
                    print(f"🚀 Starting test: {each_test}...")
                    method = self._test_methods[each_test]
                    result = method(test_details)
                    result["test_name"] = each_test
                    self._results.append(result)
                    print(f"✅ Test completed: {each_test}.")
                else:
                    warnings.warn(
                        f"⚠️ Warning: Test method for {each_test} not implemented."
                    )
        return self

    def print_results(self):
        """
        A method to print the results in a pretty table format, creating a separate table for each test type,
        and mapping internal key names to user-friendly column names for display.
        """

        # Mapping of internal key names to display names
        key_name_mapping = {
            "test_name": "Test Name",
            "prompt": "Prompt",
            "response": "Response",
            "evaluated_with": "Parameters",
            "score": "Score",
            "is_passed": "Result",
            "threshold": "Threshold",
            "context": "Context",
            "concept_set": "Concept Set",
            "test_arguments": "Test Arguments",
            "expected_response": "Expected Response",
        }

        # Group data by test names
        test_groups = {}
        for test_data in self._results:
            test_name = test_data.get("test_name", "Unknown Test Name")
            if test_name not in test_groups:
                test_groups[test_name] = []
            test_groups[test_name].append(test_data)

        # Iterate over each test group and create a table
        for test_name, test_datas in test_groups.items():
            print(f"\nTest Name: {test_name}\n")

            # Dynamically determine all keys (field names) present across test datas in the group
            all_keys = set()
            for test_data in test_datas:
                all_keys.update(test_data.keys())

            # Use mapped names for base fields and dynamic keys for complete field names list
            field_names = [key_name_mapping.get(key, key) for key in all_keys]

            # Initialize table with the mapped field names
            table = PrettyTable()
            table.field_names = field_names

            # Set max width for each column. Adjust these values as needed.
            table._max_width = {name: 25 for name in field_names}
            table.hrules = ALL

            # Fill the table with data specific to the current test group
            for test_data in test_datas:
                row = []
                for key in all_keys:
                    if key == "evaluated_with":
                        # Convert dict to string for 'evaluated_with'
                        value = ", ".join(
                            [f"{k}: {v}" for k, v in test_data.get(key, {}).items()]
                        )
                        row.append(value)
                    else:
                        # Use mapped name for the column if available
                        value = test_data.get(key, "")
                        row.append(value)

                # Add the row to the table
                table.add_row(row)

            # Print the table for the current test group
            print(table)

        return self

    def get_results(self):
        """
        Get the results of the tests.

        Returns:
            The results of the tests.
        """
        return self._results

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
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(results_json)

        print(f"Results saved to {file_path}")
