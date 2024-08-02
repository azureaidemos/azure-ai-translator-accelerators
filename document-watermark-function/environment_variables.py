"""
Module for handling environment variables and logging their values.
"""

import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Read environment variables from Azure Function App settings
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
SAS_TOKEN = os.getenv("SAS_TOKEN")
STORAGE_ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY")
WATERMARK_PREFIX = os.getenv("WATERMARK_PREFIX")
CONTAINER_NAME = "translation-service"
UPLOAD_PREFIX = "translated-zone"

# Log environment variables to check if they exist
logging.info("AZURE_STORAGE_ACCOUNT: %s", AZURE_STORAGE_ACCOUNT)
logging.info("SAS_TOKEN: %s", SAS_TOKEN)
logging.info("STORAGE_ACCOUNT_KEY: %s", STORAGE_ACCOUNT_KEY)
logging.info("WATERMARK_PREFIX: %s", WATERMARK_PREFIX)
logging.info("CONTAINER_NAME: %s", CONTAINER_NAME)
logging.info("UPLOAD_PREFIX: %s", UPLOAD_PREFIX)
