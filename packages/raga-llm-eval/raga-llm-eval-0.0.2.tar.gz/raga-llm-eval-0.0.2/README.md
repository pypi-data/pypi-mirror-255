# Welcome to Raga LLM Eval

Homepage: [RagaAI](https://www.raga.ai)

## Installation

* `python -m venv venv` - Create a new python environment.
* `source venv/bin/activate` - Activate the environment.
* `pip install raga-llm-eval` - Install the package

## Sample Code
```py
from raga_llm_eval import RagaLLMEval

evaluator = RagaLLMEval()

# Get the list of available tests
evaluator.list_available_tests()

# Perform Testing
evaluator.add_test(
    name="reliability_test",
    prompt="prompt1",
    response="response1",
    test_arguments={"parameter1": None, "parameter2": None},
).add_test(
    name="reliability_test",
    prompt="prompt2",
    response="response2",
    test_arguments={"parameter1": None, "parameter2": None},
).run().print_results()
```