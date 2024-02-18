"""
Utility function for the package
"""

import toml


def load_supported_tests(config_file):
    """
    Load the supported tests from the given config file.

    Parameters:
    config_file (str): The path to the configuration file.

    Returns:
    dict: The loaded test configuration.
    """
    with open(config_file, "r", encoding="utf-8") as file:
        test_config = toml.load(file)
    return test_config
