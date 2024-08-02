"""
Module for reading and logging environment variables for the Azure Function App.

This module sets up configuration parameters, logs environment variables, and sets up parameters for the GPT model.
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Read environment variables from Azure Function App settings
SUBSCRIPTION_KEY = os.getenv("TRANSLATE_SUBSCRIPTION_KEY")
ENDPOINT = os.getenv("TRANSLATE_ENDPOINT")
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
SAS_TOKEN = os.getenv("SAS_TOKEN")
OPENAI_API_KEY = os.getenv("OPEN_AI_API_KEY")
OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT_NAME = os.getenv("CHAT_COMPLETIONS_DEPLOYMENT_NAME")

# Log environment variables to check if they exist
logging.info("TRANSLATE_SUBSCRIPTION_KEY: %s", SUBSCRIPTION_KEY)
logging.info("TRANSLATE_ENDPOINT: %s", ENDPOINT)
logging.info("AZURE_STORAGE_ACCOUNT: %s", AZURE_STORAGE_ACCOUNT)
logging.info("SAS_TOKEN: %s", SAS_TOKEN)
logging.info("OPEN_AI_API_KEY: %s", OPENAI_API_KEY)
logging.info("AZURE_OPENAI_ENDPOINT: %s", OPENAI_API_ENDPOINT)
logging.info("CHAT_COMPLETIONS_DEPLOYMENT_NAME: %s", OPENAI_DEPLOYMENT_NAME)

# Set up parameters for the GPT model
SYSTEM_PROMPT = (
    "- Extract all location addresses from the provided text. \n"
    "- Maintain the original address format. If the address spans multiple lines, keep it multiline. \n"
    "- Do not translate or modify the content. \n"
    "- Extract each line of the address in a separate line. \n"
    "- Provide only the extracted addresses without adding any additional text.\n"
)
FEW_SHOT_EXAMPLES = []  # Define examples if necessary
CHAT_PARAMETERS = {
    "deploymentName": OPENAI_DEPLOYMENT_NAME,
    "maxResponseLength": 800,
    "temperature": 0.7,
    "topProbabilities": 0.95,
    "stopSequences": None,
    "pastMessagesToInclude": 10,
    "frequencyPenalty": 0,
    "presencePenalty": 0,
}

CONTAINER_NAME = "documents"
UPLOAD_PREFIX = "landing-zone"
GLOSSARY_PREFIX = "glossaries"
TRANSLATION_OUTPUT_PREFIX = "translated-zone"
