"""
Module for handling interactions with the GPT model using Azure OpenAI.
This module provides functions to send text to the GPT model and parse the responses.
"""

import logging
import json
from openai import AzureOpenAI
from environment_variables import (
    OPENAI_API_KEY, OPENAI_API_ENDPOINT
)

def get_gpt_response(prompt_text, SYSTEM_PROMPT, FEW_SHOT_EXAMPLES, CHAT_PARAMETERS):
    """
    Sends the extracted text to the GPT model and retrieves the response.

    Args:
        prompt_text (str): The text to send to the GPT model.
        SYSTEM_PROMPT (str): The system prompt to guide the GPT model.
        FEW_SHOT_EXAMPLES (list): Examples to help guide the GPT model.
        CHAT_PARAMETERS (dict): Parameters for the GPT model.

    Returns:
        str: The JSON response from the GPT model.
    """
    logging.info("Sending extracted text to the GPT model.")
    client = AzureOpenAI(
        api_key=OPENAI_API_KEY,
        azure_endpoint=OPENAI_API_ENDPOINT,
        api_version="2024-02-01",
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt_text},
    ]
    for example in FEW_SHOT_EXAMPLES:
        messages.append({"role": "assistant", "content": example["chatbotResponse"]})
        messages.append({"role": "user", "content": example["userInput"]})

    completion = client.chat.completions.create(
        model=CHAT_PARAMETERS["deploymentName"],
        messages=messages,
        max_tokens=CHAT_PARAMETERS.get("maxResponseLength", 800),
        temperature=CHAT_PARAMETERS.get("temperature", 0.7),
        top_p=CHAT_PARAMETERS.get("topProbabilities", 0.95),
        stop=CHAT_PARAMETERS.get("stopSequences"),
        frequency_penalty=CHAT_PARAMETERS.get("frequencyPenalty", 0),
        presence_penalty=CHAT_PARAMETERS.get("presencePenalty", 0),
    )

    logging.info("Response received from GPT model.")
    return completion.to_json()


def parse_response(json_data):
    """
    Parses the JSON response from the GPT model to extract relevant text.

    Args:
        json_data (str): The JSON response from the GPT model.

    Returns:
        list: A list of extracted text lines.
    """
    logging.info("Parsing response data to extract relevant text.")
    data = json.loads(json_data)
    if "choices" in data and data["choices"]:
        text = data["choices"][0]["message"]["content"]
        results = [line.strip() for line in text.strip().split("\n") if line.strip()]
        logging.info("Text parsed successfully.")
        return results
    logging.warning("No text found in the response data.")
    return []
