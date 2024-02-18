# Main Table
{
    'id': unique_id (primary_key),
    'prompt': user_prompt,
    'response': llm_response,
    'gt_response': expected_response,
    'context': prompt_context(if_available),
    'prompt_embedding': prompt_embedding(if_available),
    'response_embedding': response_embedding(if_available),
    'gt_response_embedding': gt_response_embedding(if_available),
    'tests': { # TODO: Should this be a separate file?
        'response_relevance': test_response_relevance_id,
        'response_accuracy': test_response_accuracy_id,
        'response_correctness': test_response_correctness_id,
        'response_bias': test_response_bias_id,
        'response_coverage': test_response_coverage_id,
        ...
    }
}

# Test Tables
# TODO: Table 2 for response relevance
{
    'id': test_response_relevance_id,
    'test_parameter_1': test_parameter1,
    'test_parameter_2': test_parameter2,
    'test_parameter_3': test_parameter3,
    'test_output': test_output 
}

...
