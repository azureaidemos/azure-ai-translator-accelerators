"""
Azure Function App to handle the retrieval of a file from Azure Blob Storage,
convert it to PDF if necessary, add a watermark, upload it back to Azure Blob Storage,
and log the upload details in the database.
"""

import logging
import os
import tempfile
import subprocess
import urllib.parse
import io
import azure.functions as func
from azure.storage.blob import BlobClient
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from database_helper import update_watermark_file_record
from blob_handler import validate_blob_url, upload_to_blob
from azure.functions import HttpRequest, HttpResponse
import json
from environment_variables import (
    AZURE_STORAGE_ACCOUNT, 
    CONTAINER_NAME, 
    SAS_TOKEN, 
    UPLOAD_PREFIX, 
    WATERMARK_PREFIX
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="add_water_mark", methods=["POST"])
def add_water_mark(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle the file upload request, save the file to a temporary location,
    upload it to Azure Blob Storage, and log the upload details in the database.

    Args:
        req (func.HttpRequest): The HTTP request object.

    Returns:
        func.HttpResponse: The HTTP response object with the status of the upload.
    """
    logging.info("Python HTTP trigger function to upload a file processed a request.")
    input_file_path = None
    try:
        req_body = req.get_json()        
        logging.info("Request body: %s", req_body)

        # Check if the event is a subscription validation event
        for event in req_body:
            if event.get('eventType') == 'Microsoft.EventGrid.SubscriptionValidationEvent':
                validation_code = event['data']['validationCode']
                validation_response = {
                    "validationResponse": validation_code
                }
                return func.HttpResponse(
                    body=json.dumps(validation_response),
                    status_code=200,
                    mimetype="application/json"
                )

        # Handle BlobCreated events
        for event in req_body:
            if event.get('eventType') == 'Microsoft.Storage.BlobCreated':
                blob_url = event['data']['url']
                file_name = blob_url.split('/')[-1]
                logging.info("File name extracted: %s", file_name)
                
                input_file_path = file_name

                # Define the source URL
                encoded_file_name = urllib.parse.quote(file_name)
                source_url = (
                    f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/"
                    f"{CONTAINER_NAME}/{UPLOAD_PREFIX}/{encoded_file_name}?{SAS_TOKEN}"
                )
                logging.info("Source URL: %s", source_url)

                # Validate the existence of the source URL
                if not validate_blob_url(source_url):
                    logging.error("Source file does not exist: %s", source_url)
                    return func.HttpResponse("Source file does not exist.", status_code=404)

                # Read the file content from the source URL
                blob_client = BlobClient.from_blob_url(source_url)
                downloader = blob_client.download_blob()
                file_content = downloader.readall()

                logging.info("File content read successfully.")
                new_file_name = file_content

                if file_name.endswith(".docx"):
                    pdf_content = convert_docx_to_pdf(file_content)
                    pdf_content = add_pdf_watermark(pdf_content)
                    new_file_name = file_name.replace(".docx", ".pdf")
                elif file_name.endswith(".pdf"):
                    pdf_content = file_content
                    pdf_content = add_pdf_watermark(file_content)
                else:
                    return func.HttpResponse("Unsupported file type.", status_code=400)

                file_url = upload_to_blob(
                    WATERMARK_PREFIX,
                    new_file_name,
                    pdf_content,
                )
                logging.info("File URL: %s", file_url)
                watermark_zone_path = file_url
                watermark_status = "done"

                logging.info("Updating the watermark record in the database.")
                update_watermark_file_record(
                    input_file_path,
                    watermark_status,
                    watermark_zone_path,
                )
                logging.info("Watermark record updated successfully.")

                return func.HttpResponse(f"File {new_file_name} uploaded successfully", status_code=200)

        return func.HttpResponse("Event received but not handled.", status_code=200)

    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return func.HttpResponse(
            "Invalid request",
            status_code=400
        )
    except Exception as e:
        logging.error("Error processing the request: %s", str(e), exc_info=True)
        if input_file_path:
            update_watermark_file_record(input_file_path)
        return func.HttpResponse("Internal Server Error", status_code=500)



def convert_docx_to_pdf(docx_content):
    """
    Converts a .docx file content to .pdf using LibreOffice.

    Input:
    - docx_content: The content of the .docx file.

    Output:
    - The content of the converted .pdf file.
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            docx_path = os.path.join(tmpdirname, "temp.docx")
            pdf_path = os.path.join(tmpdirname, "temp.pdf")

            with open(docx_path, "wb") as f:
                f.write(docx_content)
            logging.debug("Wrote .docx content to %s", docx_path)

            # Convert .docx to .pdf using LibreOffice
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    docx_path,
                    "--outdir",
                    tmpdirname,
                ],
                check=True,
            )
            logging.debug("Converted .docx to .pdf using LibreOffice, output path: %s", pdf_path)

            # Read the .pdf file content
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()
            logging.debug("Read .pdf content from %s", pdf_path)

        return pdf_content
    except Exception as e:
        logging.error("Error converting .docx to .pdf: %s", str(e), exc_info=True)
        raise


def add_pdf_watermark(pdf_content, watermark_text="AI Translated"):
    """
    Adds a watermark to a PDF document.

    Input:
    - pdf_content: The content of the PDF to be watermarked.
    - watermark_text: The text to be used as the watermark.

    Output:
    - Watermarked PDF content.
    """
    try:
        with io.BytesIO(pdf_content) as input_pdf_stream, io.BytesIO() as output_pdf_stream:
            input_pdf = PdfReader(input_pdf_stream)
            output_pdf = PdfWriter()

            # Create a watermark
            watermark_stream = io.BytesIO()
            c = canvas.Canvas(watermark_stream, pagesize=letter)
            c.setFont("Helvetica", 100)
            c.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)

            # Get the dimensions of the page to center the watermark
            page_width, page_height = letter
            x = page_width / 2
            y = page_height / 2

            c.saveState()
            c.translate(x, y)
            c.rotate(45)
            c.drawCentredString(0, 0, watermark_text)
            c.restoreState()
            c.save()
            watermark_stream.seek(0)
            watermark = PdfReader(watermark_stream).pages[0]

            # Add watermark to each page
            for page in input_pdf.pages:
                page.merge_page(watermark)
                output_pdf.add_page(page)

            output_pdf.write(output_pdf_stream)
            logging.debug("Watermark added to PDF.")
            return output_pdf_stream.getvalue()

    except Exception as e:
        logging.error("Error adding watermark: %s", str(e), exc_info=True)
        raise
