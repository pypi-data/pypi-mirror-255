from raga_llm_eval import RagaLLMEval

evaluator = RagaLLMEval()

print("Available Tests")
evaluator.list_available_tests()

print("Results")
evaluator.add_test(
    name="reliability_test",
    prompt="dsdsdsd",
    response="dfdfdfd",
    test_arguments={"parameter1": None, "parameter2": None},
).add_test(
    name="reliability_test",
    prompt="dsdsdsd",
    response="dfdfdfd",
    test_arguments={"parameter1": None, "parameter2": None},
).add_test(
    name="reliability_test",
    prompt="dsdsdsd",
    response="dfdfdfd",
    test_arguments={"parameter1": None, "parameter2": None},
).run().print_results()
