"""
Main Module for LLM Test Execution
"""

import requests

from .llm_tests.test_executor import TestExecutor
from .raga_llm_eval import RagaLLMEval

__all__ = ["RagaLLMEval", "TestExecutor"]

__version__ = "0.0.8.4"


def check_latest_version(package_name):
    """
    Check the latest version of the package on PyPI and inform the user if an update is available.
    """
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=3)
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]
        if __version__ != latest_version:
            print(
                f"Update available for {package_name} package. Your version: {__version__}. Latest version: {latest_version}."
            )
            print(
                "Run 'pip install --upgrade <package_name>' to update to the latest version."
            )
    except Exception as e:
        print("Failed to check the latest package version:", e)


# Check the latest version
check_latest_version("raga_llm_eval")
