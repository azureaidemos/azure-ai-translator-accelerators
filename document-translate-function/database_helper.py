"""
Module for handling database operations.

This module provides functions to interact with a PostgreSQL database, including
updating file records and fetching metadata and exclusion texts.
"""

import logging
import os
import json
import re
import psycopg2
from psycopg2 import sql, DatabaseError, IntegrityError

# PostgreSQL connection details
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")

# Log environment variables to check if they exist
logging.debug("DB_HOST: %s", DB_HOST)
logging.debug("DB_PORT: %s", DB_PORT)
logging.debug("DB_NAME: %s", DB_NAME)
logging.debug("DB_USER: %s", DB_USER)
logging.debug("DB_PASSWORD: %s", '****' if DB_PASSWORD else None)
logging.debug("DB_SSLMODE: %s", DB_SSLMODE)


class DatabaseHandler:
    """
    A class to handle database operations.
    """

    def get_connection(self):
        """
        Establish a connection to the PostgreSQL database using the provided connection details.

        Returns:
            psycopg2.connection: A connection object to interact with the PostgreSQL database.

        Raises:
            psycopg2.OperationalError: If there is an error connecting to the database.
        """
        try:
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                sslmode=DB_SSLMODE,
            )
        except psycopg2.OperationalError as e:
            logging.error("Error connecting to the database: %s", str(e))
            raise

    def update_file_record(
        self,
        file_name,
        translation_date,
        translation_datetime,
        translation_status,
        translated_zone_path,
        glossary_zone_path,
        glossary_processing_status,
        glossary_content,
    ):
        """
        Update the record of the file in the PostgreSQL database.

        Args:
            file_name (str): The name of the file.
            translation_date (datetime.date): The date of the translation.
            translation_datetime (datetime.datetime): The date and time of the translation.
            translation_status (str): The status of the translation ('failed', 'in progress', 'done').
            glossary_zone_path (str): The path to the glossary file.
            glossary_processing_status (str): The status of the glossary processing ('failed', 'in progress', 'done').
            glossary_content (list): The content of the glossary.
            translated_zone_path (str): The path to the translated file in the translated zone.

        Raises:
            IntegrityError: If there is an integrity constraint violation.
            DatabaseError: If there is a general database error.
            Exception: If there is an unexpected error.
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                update_query = sql.SQL(
                    """
                    UPDATE file_translation_logs
                    SET translation_date = %s,
                        translation_datetime = %s,
                        translation_status = %s,
                        translated_zone_path = %s,
                        glossary_zone_path = %s,
                        glossary_processing_status = %s,
                        glossary_content = %s                    
                    WHERE file_name = %s
                    """
                )
                cursor.execute(
                    update_query,
                    (
                        translation_date,
                        translation_datetime,
                        translation_status,
                        translated_zone_path,
                        glossary_zone_path,
                        glossary_processing_status,
                        json.dumps(glossary_content) if glossary_content else None,
                        file_name,
                    ),
                )
                conn.commit()
        except IntegrityError as e:
            logging.error("Integrity error: %s", str(e))
            if conn:
                conn.rollback()
        except DatabaseError as e:
            logging.error("Database error: %s", str(e))
            if conn:
                conn.rollback()
        except Exception as e:
            logging.error("Unexpected error: %s", str(e))
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    def fetch_metadata_text(self, file_name):
        """
        Fetch metadata and exclusion texts from the file_translation_logs table.

        Args:
            file_name (str): The name of the file to fetch exclusion texts and metadata for.

        Returns:
            dict: A dictionary containing metadata (fromLang, toLang, exclusionTexts, additionalGlossaryContentUrl)
                and exclusion texts for the given file name.

        Raises:
            DatabaseError: If there is a general database error.
            Exception: If there is an unexpected error.
        """
        conn = None
        result = {
            "fromLang": None,
            "toLang": None,
            "exclusionTexts": [],
            "additionalGlossaryContentUrl": None,
        }

        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                query = sql.SQL(
                    """
                    SELECT fromLanguage, toLanguage, exclusion_text, additional_glossary_content_url
                    FROM file_translation_logs 
                    WHERE file_name = %s
                    """
                )
                cursor.execute(query, (file_name,))
                rows = cursor.fetchall()
                if rows:
                    row = rows[0]
                    result["fromLang"] = row[0]
                    result["toLang"] = row[1]
                    result["additionalGlossaryContentUrl"] = row[3]
                    exclusion_texts = row[2]
                    exclusion_texts = row[2] if row[2] is not None else ""
                    result["exclusionTexts"] = [
                        text.strip() for text in re.split(r"\r\n|\n", exclusion_texts)
                    ]
        except DatabaseError as e:
            logging.error("Database error: %s", str(e))
            raise
        except Exception as e:
            logging.error("Unexpected error: %s", str(e))
            raise
        finally:
            if conn:
                conn.close()

        return result
