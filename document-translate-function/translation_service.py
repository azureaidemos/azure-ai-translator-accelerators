"""
Module for handling translation services.

This module provides functions to start a translation job and check the status
of the translation job using the Azure Translator service.
"""

import logging
import json
import time
import requests
from environment_variables import ENDPOINT, SUBSCRIPTION_KEY

def start_translation(
    source_url, target_url, glossary_url, source_language, target_language
):
    """
    Starts the translation job.

    Args:
        source_url (str): URL of the source document.
        target_url (str): URL where the translated document will be stored.
        glossary_url (str): URL of the glossary file.
        source_language (str): The source language of the document.
        target_language (str): The target language for the translation.

    Returns:
        str: Operation location URL if successful, None otherwise.
    """
    logging.info("Starting translation job")
    logging.info("Source URL: %s", source_url)
    logging.info("Target URL: %s", target_url)
    logging.info("Glossary URL: %s", glossary_url)
    logging.info("Source language: %s", source_language)
    logging.info("Target language: %s", target_language)

    url = f"{ENDPOINT}/translator/document/batches?api-version=2024-05-01"
    body = {
        "inputs": [
            {
                "source": {
                    "sourceUrl": source_url,
                    "language": source_language,
                    "storageSource": "AzureBlob",
                },
                "targets": [
                    {
                        "targetUrl": target_url,
                        "category": "general",
                        "language": target_language,
                        "storageSource": "AzureBlob",
                        "glossaries": [{"glossaryUrl": glossary_url, "format": "csv"}],
                    }
                ],
                "storageType": "File",
            }
        ],
        "options": {"experimental": True},
    }

    logging.info("Request body: %s", json.dumps(body, indent=2))
    response = requests.post(
        url,
        headers={
            "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
            "Content-Type": "application/json",
        },
        json=body,
        timeout=30
    )
    logging.info("Response status code: %s", response.status_code)
    logging.info("Response headers: %s", response.headers)
    logging.info("Response text: %s", response.text)

    if response.status_code == 202:
        operation_location = response.headers.get("Operation-Location")
        logging.info(
            "Translation job started successfully. Operation location: %s", operation_location
        )
        return operation_location
    logging.error(
        "Error starting translation job: %s, %s", response.status_code, response.text
    )
    return None


def check_translation_status(
    operation_location, target_file_name, max_retries=20, delay=10
):
    """
    Checks the status of the translation job and retrieves the translated document if successful.

    Args:
        operation_location (str): URL to check the status of the translation job.
        target_file_name (str): Name of the target file.
        max_retries (int): Maximum number of retries for checking status.
        delay (int): Delay between retries in seconds.

    Returns:
        str: Translated document content if successful, None otherwise.
    """
    logging.info("Checking translation status")
    logging.info("Operation location: %s", operation_location)
    logging.info("Target file name: %s", target_file_name)

    retries = 0
    while retries < max_retries:
        time.sleep(delay)
        retries += 1
        logging.info("Polling translation status... Attempt %d/%d", retries, max_retries)
        response = requests.get(
            operation_location, headers={"Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY},
            timeout=30
        )
        logging.info("Response status code: %s", response.status_code)
        logging.info("Response text: %s", response.text)

        if response.status_code == 200:
            status = response.json()
            logging.info("Translation status response: %s", json.dumps(status, indent=2))
            return json.dumps(status, indent=2)
        logging.error(
            "Error checking translation status: %s, %s", response.status_code, response.text
        )
        return None

    logging.error("Max retries reached. Translation status check failed.")
    return None
