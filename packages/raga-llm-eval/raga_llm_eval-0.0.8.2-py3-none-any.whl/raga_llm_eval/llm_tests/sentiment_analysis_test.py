"""
Detect Sentiment of the response. This test can be used to regulate the sentiment of the response from the model
depending on the requiremnts of the downstream application
"""

import logging
import os
import sys
import warnings

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# sys.stderr = open(os.devnull, "w", encoding="utf-8")
# warnings.filterwarnings("ignore")


def sentiment_analysis_test(response, threshold=0.5):
    """
    Provides a score for the sentiment of model response. The test can be used to regulate
    the sentiment of the model to keep it based on the application requirement.
    It return overall text sentiment higher score is positive sentiment

    Args:
    - response (str): The response from the model.
    - threshold (float): The threshold to define the sentiment

    Returns:
    - dict: A dictionary containing the response, sentimentscore, threshold and
    boolean if sentiment score is more than threshold

    """

    # Create a test case
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(response)

    score = sentiment_score["compound"]
    injection_prompt = "Passed" if sentiment_score["compound"] > threshold else "Failed"

    # Prepare and return the result
    result = {
        "response": response,
        "threshold": threshold,
        "sentiment": injection_prompt,
        "sentiment_score": score,
    }

    return result
