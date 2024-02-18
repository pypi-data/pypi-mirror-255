# Welcome to Raga LLM Eval

Homepage: [RagaAI](https://www.raga.ai)

## Installation

* `python -m venv venv` - Create a new python environment.
* `source venv/bin/activate` - Activate the environment.
* `pip install raga-llm-eval` - Install the package

## Sample Code
```py
from raga_llm_eval import RagaLLMEval

evaluator = RagaLLMEval(
    api_keys={"OPENAI_API_KEY": "xxx"}
)

# Get the list of available tests
evaluator.list_available_tests()

evaluator.add_test(
    name=["answer_relevancy_test", "summarization_test"],
    prompt=["How are you?", "How do you do?"],
    context=["You are a student, answering your teacher."],
    response=["I am fine. Thank you", "Doooo do do do doooo..."],
    test_arguments={"model": "gpt-3.5-turbo-1106", "threshold": 0.6},
).run().print_results()
```
