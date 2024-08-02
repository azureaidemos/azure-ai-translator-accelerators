"""
Module for Azure Function to translate documents using various services.

This module defines a blob-triggered Azure Function to process and translate documents.
It handles the following steps:
1. Validates the file type and source URL.
2. Extracts text content from the document.
3. Processes the extracted content to merge with metadata.
4. Uploads the processed data to a storage location.
5. Initiates a translation job using the processed data.
6. Checks the status of the translation job and retrieves the translated document.
7. Updates the database with the results of the translation job.
"""

import json
import logging
import urllib.parse
from datetime import datetime
import azure.functions as func
from environment_variables import *
from blob_handler import validate_source_url
from document_processing import process_file, process_and_upload_data
from translation_service import start_translation, check_translation_status
from database_helper import DatabaseHandler
from gpt_handler import parse_response

app = func.FunctionApp()
database_handler = DatabaseHandler()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@app.blob_trigger(
    arg_name="myblob",
    path="documents/landing-zone/{name}",
    connection="BlobStorageConnectionString",
)
def az_ai_translate_document(myblob: func.InputStream):
    """
    Function to handle blob trigger and translate document.

    Steps:
    1. Validates the file type and source URL.
    2. Extracts text content from the document.
    3. Processes the extracted content to merge with metadata.
    4. Uploads the processed data to a storage location.
    5. Initiates a translation job using the processed data.
    6. Checks the status of the translation job and retrieves the translated document.
    7. Updates the database with the results of the translation job.

    Args:
        myblob (func.InputStream): Input stream triggered by the blob event.
    """
    logging.info("Blob trigger function processing blob: %s", myblob.name)    

    file_name = myblob.name.split("/")[-1]
    logging.info("Extracted file name: %s", file_name)
    logging.info("Full path: %s", myblob.name)

    # Filter out unwanted file types
    if not (file_name.endswith(".docx") or file_name.endswith(".pdf")):
        logging.info("File type not supported for translation: %s", file_name)
        return

    try:
        process_document(file_name)

    except (ValueError, KeyError, RuntimeError) as e:
        handle_exception(file_name, str(e))


def process_document(file_name):
    """
    Process the document for translation.

    Args:
        file_name (str): The name of the file.
    """
    encoded_file_name = urllib.parse.quote(file_name)
    source_url = (
        f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/"
        f"{CONTAINER_NAME}/{UPLOAD_PREFIX}/{encoded_file_name}?{SAS_TOKEN}"
    )
    logging.info("Source URL: %s", source_url)
    logging.info("Encoded file name: %s", encoded_file_name)

    # Validate the existence of the source URL
    if not validate_source_url(source_url):
        logging.error("Source file does not exist: %s", source_url)
        return

    target_urls = get_target_urls(file_name)
    target_url = target_urls['docx'] if file_name.endswith(".docx") else target_urls['pdf']
    logging.info("Target URL: %s", target_url)

    response = process_file(file_name, source_url, SYSTEM_PROMPT, FEW_SHOT_EXAMPLES, CHAT_PARAMETERS)

    parsed_response = parse_response(response)
    logging.info("Text extracted from file: %s", parsed_response)

    logging.info("File processing completed for: %s", file_name)

    metadata_results = database_handler.fetch_metadata_text(file_name)
    logging.info("Metadata results: %s", metadata_results)

    exclusion_text = metadata_results["exclusionTexts"]
    logging.info("Exclusion text: %s", exclusion_text)

    merged_response = parsed_response + exclusion_text
    logging.info("Merged response: %s", merged_response)

    glossary_url = process_and_upload_data(
        file_name,
        merged_response,
        AZURE_STORAGE_ACCOUNT,
        SAS_TOKEN,
        CONTAINER_NAME,
        GLOSSARY_PREFIX,
    )

    logging.info("Glossary URL: %s", glossary_url)

    json_list = [{"items": item} for item in merged_response]

    # Convert the list of objects to a JSON string
    glossary_content = json.dumps(json_list, ensure_ascii=False, indent=2)
    logging.info("Glossary content: %s", glossary_content)

    start_translation_job(file_name, source_url, target_url, glossary_url, metadata_results, glossary_content)


def get_target_urls(file_name):
    """
    Get the target URLs for the document.

    Args:
        file_name (str): The name of the file.

    Returns:
        dict: A dictionary containing the target URLs for DOCX and PDF formats.
    """
    target_file_name_base = file_name.split(".")[0]
    logging.info("Target file name base: %s", target_file_name_base)

    target_file_name_docx = f"{target_file_name_base}.docx"
    logging.info("Target file name (docx): %s", target_file_name_docx)

    target_file_name_pdf = f"{target_file_name_base}.pdf"
    logging.info("Target file name (pdf): %s", target_file_name_pdf)

    encoded_target_file_name_docx = urllib.parse.quote(target_file_name_docx)
    encoded_target_file_name_pdf = urllib.parse.quote(target_file_name_pdf)

    target_url_docx = (
        f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/"
        f"{CONTAINER_NAME}/{TRANSLATION_OUTPUT_PREFIX}/{encoded_target_file_name_docx}?{SAS_TOKEN}"
    )
    target_url_pdf = (
        f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/"
        f"{CONTAINER_NAME}/{TRANSLATION_OUTPUT_PREFIX}/{encoded_target_file_name_pdf}?{SAS_TOKEN}"
    )

    return {'docx': target_url_docx, 'pdf': target_url_pdf}


def start_translation_job(file_name, source_url, target_url, glossary_url, metadata_results, glossary_content):
    """
    Start the translation job for the document.

    Args:
        file_name (str): The name of the file.
        source_url (str): The source URL of the file.
        target_url (str): The target URL for the translated file.
        glossary_url (str): The URL of the glossary.
        metadata_results (dict): The metadata results.
        glossary_content (str): The content of the glossary.
    """
    operation_location = start_translation(
        source_url,
        target_url,
        glossary_url,
        metadata_results["fromLang"],
        metadata_results["toLang"],
    )

    translation_status = "in progress"
    glossary_processing_status = "done"
    translation_date = datetime.now().date()
    translation_datetime = datetime.now()
    translated_zone_path = target_url

    if not operation_location:
        logging.error("Failed to start translation job")
        translation_status = "failed"
        update_file_record(
            file_name, translation_date, translation_datetime, translation_status,
            translated_zone_path, glossary_url, glossary_processing_status, glossary_content
        )
        return

    logging.info("Translation job started successfully")

    translated_document = check_translation_status(
        operation_location,
        get_target_file_name(file_name)
    )

    if not translated_document:
        logging.error("Translation job failed")
        translation_status = "failed"
    else:
        logging.info("Translated document URL: %s", target_url)
        translation_status = "done"

    update_file_record(
        file_name, translation_date, translation_datetime, translation_status,
        translated_zone_path, glossary_url, glossary_processing_status, glossary_content
    )


def get_target_file_name(file_name):
    """
    Get the target file name based on the file extension.

    Args:
        file_name (str): The name of the file.

    Returns:
        str: The target file name.
    """
    target_file_name_base = file_name.split(".")[0]
    return f"{target_file_name_base}.docx" if file_name.endswith(".docx") else f"{target_file_name_base}.pdf"


def update_file_record(file_name, translation_date, translation_datetime, translation_status,
                       translated_zone_path, glossary_url, glossary_processing_status, glossary_content):
    """
    Update the file record in the database.

    Args:
        file_name (str): The name of the file.
        translation_date (date): The date of the translation.
        translation_datetime (datetime): The datetime of the translation.
        translation_status (str): The status of the translation.
        translated_zone_path (str): The path to the translated zone.
        glossary_url (str): The URL of the glossary.
        glossary_processing_status (str): The status of the glossary processing.
        glossary_content (str): The content of the glossary.
    """
    database_handler.update_file_record(
        file_name,
        translation_date,
        translation_datetime,
        translation_status,
        translated_zone_path,
        glossary_url,
        glossary_processing_status,
        glossary_content,
    )


def handle_exception(file_name, error_message):
    """
    Handle exceptions during the translation process.

    Args:
        file_name (str): The name of the file.
        error_message (str): The error message.
    """
    logging.error("Error in Translate Function: %s", error_message)
    translation_status = "failed"
    translation_date = datetime.now().date()
    translation_datetime = datetime.now()
    glossary_processing_status = "failed"

    update_file_record(
        file_name,
        translation_date,
        translation_datetime,
        translation_status,
        None,
        None,
        glossary_processing_status,
        None,
    )
