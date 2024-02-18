from raga_llm_eval import RagaLLMEval

# Initialize the evaluator with necessary configurations
evaluator = RagaLLMEval(
    api_keys={  # add the ones required
        "OPENAI_API_KEY": "API_KEY",
        "HUGGINGFACEHUB_API_TOKEN": "API_TOKEN",
    }
)

# List available tests
evaluator.list_available_tests()

prompts = ["Describe a happy person", "Describe an unhappy person"]
responses = ["A person who is happy", "A person who is unhappy"]

# Configure and run a series of tests on the LLM, print, and save results
(
    evaluator.add_test(name="BiasnessTest", prompt=prompts, response=responses)
    .add_test(
        name="ToxicityTest",
        prompt=prompts,
        response=responses,
        expected_response=None,  # Assuming this field is optional for certain tests
        context=None,  # Context is optional
    )
    .set_output_format("detailed")  # Options: 'summary', 'detailed'
    .run()
    .print_results()
    .save_results("test_results.json")
)

# if the results need to be further processed, use get_results()
results = evaluator.get_results()
