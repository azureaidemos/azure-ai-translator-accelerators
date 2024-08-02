"""
This module contains HTTP-triggered Azure Functions for handling file uploads and retrieving logs.

Functions:
- upload_file: 
    -> Handles file upload requests.
    -> Saves files temporarily.
    -> Uploads them to Azure Blob Storage
    -> Logs upload details in a PostgreSQL database.
- get_logs_by_date: Fetches logs from the PostgreSQL database based on a provided date.
- get_all_logs: Retrieves all logs from the PostgreSQL database.
"""

import logging
import json
import azure.functions as func
from database_handler import DatabaseHandler, DatabaseError, IntegrityError
from utils import (
    extract_request_data, 
    get_azure_storage_info, 
    save_file_temporarily, 
    upload_to_blob_storage, 
    generate_blob_url, 
    log_file_upload,
    clean_up_temporary_file
    )


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="upload_file", methods=["POST"])
def upload_file(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle the file upload request, save the file to a temporary location,
    upload it to Azure Blob Storage, and log the upload details in the database.

    Args:
        req (func.HttpRequest): The HTTP request object.

    Returns:
        func.HttpResponse: The HTTP response object with the status of the upload.
    """
    logging.info("Python HTTP trigger function to upload a file processed a request.")
    new_file_path = None
    try:

        file, from_lang, to_lang, exclusion_text, uploaded_by, prompt_id = extract_request_data(req)

        if not file:
            logging.error("No file provided in the request")
            return func.HttpResponse("No file provided in the request", status_code=400)

        if not from_lang or not to_lang:
            logging.error("Language information not provided in the request")
            return func.HttpResponse(
                "Language information not provided in the request", status_code=400
            )

        database_handler = DatabaseHandler()

        azure_storage_account, sas_token, container_name = get_azure_storage_info()

        new_file_name, new_file_path = save_file_temporarily(file, database_handler)
        
        upload_to_blob_storage(new_file_path, new_file_name, container_name)

        landing_zone_path = generate_blob_url(azure_storage_account, container_name, new_file_name, sas_token)

        logging.info("File %s uploaded successfully", new_file_name)

        log_file_upload(
            new_file_name,
            landing_zone_path,
            file,
            uploaded_by,
            from_lang,
            to_lang,
            exclusion_text,
            prompt_id
        )

        return func.HttpResponse(f"File {new_file_name} uploaded successfully", status_code=200)

    except (FileNotFoundError, PermissionError, DatabaseError, IntegrityError) as e:
        logging.error("Specific error: %s", str(e))
        return func.HttpResponse(f"Specific error: {str(e)}", status_code=500)
    except Exception as e:
        logging.error("Exception occurred during upload: %s", str(e))
        return func.HttpResponse(f"Exception occurred during upload: {str(e)}", status_code=500)
    finally:        
        clean_up_temporary_file(new_file_path)


@app.route(route="get_logs_by_date", methods=["GET"])
def get_logs_by_date(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle the GET request to fetch logs by date from the PostgreSQL database.

    Args:
        req (func.HttpRequest): The HTTP request object.

    Returns:
        func.HttpResponse: The HTTP response object with the logs data.
    """
    logging.info("Python HTTP trigger function processed a request.")

    date = req.params.get("date")
    if not date:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        date = req_body.get("date")

    if not date:
        return func.HttpResponse("Please pass a date on the query string or in the request body",status_code=400)

    database_handler = DatabaseHandler()
    try:
        logs = database_handler.fetch_logs_by_date(date)
        return func.HttpResponse(json.dumps(logs), status_code=200, mimetype="application/json")
    except Exception as e:
        logging.error("Exception occurred: %s", str(e))
        return func.HttpResponse(f"Error fetching logs: {str(e)}", status_code=500)


@app.route(route="get_all_logs", methods=["GET"])
def get_all_logs(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle the GET request to fetch logs by date from the PostgreSQL database.

    Args:
        req (func.HttpRequest): The HTTP request object.

    Returns:
        func.HttpResponse: The HTTP response object with the logs data.
    """
    logging.info("Python HTTP trigger function processed a request.")

    database_handler = DatabaseHandler()
    try:
        logs = database_handler.fetch_all_logs()
        return func.HttpResponse(json.dumps(logs), status_code=200, mimetype="application/json")    
    except Exception as e:
        logging.error("Exception occurred: %s", str(e))
        return func.HttpResponse(f"Error fetching logs: {str(e)}", status_code=500)


@app.route(route="get_all_prompts", methods=["GET"])
def get_all_prompts(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle the GET request to fetch logs by date from the PostgreSQL database.

    Args:
        req (func.HttpRequest): The HTTP request object.

    Returns:
        func.HttpResponse: The HTTP response object with the logs data.
    """
    logging.info("Python HTTP trigger function processed a request.")

    database_handler = DatabaseHandler()
    try:
        logs = database_handler.fetch_all_prompts()
        return func.HttpResponse(json.dumps(logs), status_code=200, mimetype="application/json")    
    except Exception as e:
        logging.error("Exception occurred: %s", str(e))
        return func.HttpResponse(f"Error fetching logs: {str(e)}", status_code=500)    
    
