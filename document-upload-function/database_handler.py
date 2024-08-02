"""
Database handler module for interacting with PostgreSQL for file translation logs.

This module provides functionality to connect to a PostgreSQL database,
insert file upload records, check for existing file names, and fetch logs
based on date or fetch all logs.
"""

import logging
import os
from datetime import datetime
import psycopg2
from psycopg2 import sql, DatabaseError, IntegrityError


# PostgreSQL connection details
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")

# Log environment variables to check if they exist
logging.debug("DB_HOST: %s", DB_HOST)
logging.debug("DB_PORT: %d", DB_PORT)
logging.debug("DB_NAME: %s", DB_NAME)
logging.debug("DB_USER: %s", DB_USER)
logging.debug("DB_PASSWORD: %s", '****' if DB_PASSWORD else None)
logging.debug("DB_SSLMODE: %s", DB_SSLMODE)


class DatabaseHandler:
    """
    A class to handle database operations for file translation logs.
    """

    def get_connection(self):
        """
        Establish a connection to the PostgreSQL database using the provided connection details.

        Returns:
            psycopg2.connection: A connection object to interact with the PostgreSQL database.

        Raises:
            psycopg2.OperationalError: If there is an error connecting to the database.
        """
        logging.info("Database password retrieved: %s", DB_PASSWORD is not None)
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

    def insert_file_record(
        self,
        file_name,
        landing_zone_path,
        file_type,
        upload_date,
        upload_datetime,
        upload_status,
        uploaded_by,
        from_lang,
        to_lang,
        exclusion_text,
        prompt_id
    ):
        """
        Insert a record of the uploaded file into the PostgreSQL database.

        Args:
            file_name (str): The name of the file.
            landing_zone_path (str): The path to the file in the landing zone.
            file_type (str): The type of the file (pdf/docx).
            upload_date (datetime.date): The date of the upload.
            upload_datetime (datetime.datetime): The date and time of the upload.
            upload_status (str): The status of the upload ('failed', 'in progress', 'done').
            uploaded_by (str): The identifier of the person who uploaded the file.
            from_lang (str): The source language of the file.
            to_lang (str): The target language of the file.
            exclusion_text (str): The text to exclude from translation.

        Raises:
            IntegrityError: If there is an integrity constraint violation.
            DatabaseError: If there is a general database error.
            Exception: If there is an unexpected error.
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                insert_query = sql.SQL(
                    """
                    INSERT INTO file_translation_logs (
                        file_name, landing_zone_path, file_type, upload_date, upload_datetime, 
                        upload_status, uploaded_by, fromLanguage, toLanguage, exclusion_text, prompt_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                )
                cursor.execute(
                    insert_query,
                    (
                        file_name,
                        landing_zone_path,
                        file_type,
                        upload_date,
                        upload_datetime,
                        upload_status,
                        uploaded_by,
                        from_lang,
                        to_lang,
                        exclusion_text,
                        prompt_id
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

    def check_file_name(self, file_name):
        """
        Check if a file with the same name already exists in the database.
        If it does, append a timestamp to the file name to make it unique.

        Args:
            file_name (str): The original file name.

        Returns:
            str: The unique file name (original or modified).

        Raises:
            DatabaseError: If there is a general database error.
            Exception: If there is an unexpected error.
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM file_translation_logs WHERE file_name = %s",
                    (file_name,),
                )
                count = cursor.fetchone()[0]

                if count > 0:
                    timestamp = datetime.now().strftime("_%Y%m%d%H%M%S")
                    new_file_name = f"{os.path.splitext(file_name)[0]}{timestamp}{os.path.splitext(file_name)[1]}"
                    logging.info("File name exists. New file name: %s", new_file_name)
                    file_name = new_file_name
        except DatabaseError as e:
            logging.error("Database error: %s", str(e))
            raise
        except Exception as e:
            logging.error("Unexpected error: %s", str(e))
            raise
        finally:
            if conn:
                conn.close()
        return file_name

    def fetch_logs_by_date(self, date):
        """
        Fetch logs from the file_translation_logs table filtered by the given date.

        Args:
            date (str): The date to filter logs by.

        Returns:
            list: A list of dictionaries representing the rows retrieved.

        Raises:
            DatabaseError: If there is a general database error.
            Exception: If there is an unexpected error.
        """
        conn = None
        logs = []
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                query = sql.SQL(
                    """
                    SELECT file_name, landing_zone_path, file_type, upload_date, upload_datetime, upload_status, 
                        translation_date, translation_datetime, translation_status, translated_zone_path, 
                        fromLanguage, toLanguage, watermark_date, watermark_datetime, watermark_status, 
                        watermark_zone_path, glossary_content, glossary_processing_status, glossary_zone_path, 
                        uploaded_by, statue, exclusion_text
                    FROM file_translation_logs 
                    WHERE upload_date = %s 
                    ORDER BY upload_datetime DESC
                    """
                )
                cursor.execute(query, (date,))
                rows = cursor.fetchall()
                for row in rows:
                    logs.append(
                        {
                            "file_name": row[0],
                            "landing_zone_path": row[1],
                            "file_type": row[2],
                            "upload_date": row[3].isoformat() if row[3] else None,
                            "upload_datetime": row[4].isoformat() if row[4] else None,
                            "upload_status": row[5],
                            "translation_date": row[6].isoformat() if row[6] else None,
                            "translation_datetime": row[7].isoformat() if row[7] else None,
                            "translation_status": row[8],
                            "translated_zone_path": row[9],
                            "fromLanguage": row[10],
                            "toLanguage": row[11],
                            "watermark_date": row[12].isoformat() if row[12] else None,
                            "watermark_datetime": row[13].isoformat() if row[13] else None,
                            "watermark_status": row[14],
                            "watermark_zone_path": row[15],
                            "glossary_content": row[16],
                            "glossary_processing_status": row[17],
                            "glossary_zone_path": row[18],
                            "uploaded_by": row[19],
                            "statue": row[20],
                            "exclusion_text": row[21],
                        }
                    )
        except DatabaseError as e:
            logging.error("Database error: %s", str(e))
            raise
        except Exception as e:
            logging.error("Unexpected error: %s", str(e))
            raise
        finally:
            if conn:
                conn.close()
        return logs

    def fetch_all_logs(self):
        """
        Fetch all logs from the file_translation_logs table.

        Returns:
            list: A list of dictionaries representing the rows retrieved.

        Raises:
            DatabaseError: If there is a general database error.
            Exception: If there is an unexpected error.
        """
        conn = None
        logs = []
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                query = sql.SQL(
                    """
                    SELECT file_name, landing_zone_path, file_type, upload_date, upload_datetime, upload_status, 
                        translation_date, translation_datetime, translation_status, translated_zone_path, 
                        fromLanguage, toLanguage, watermark_date, watermark_datetime, watermark_status, 
                        watermark_zone_path, glossary_content, glossary_processing_status, glossary_zone_path, 
                        uploaded_by, statue , exclusion_text
                    FROM file_translation_logs 
                    ORDER BY upload_datetime DESC
                    """
                )
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    logs.append(
                        {
                            "file_name": row[0],
                            "landing_zone_path": row[1],
                            "file_type": row[2],
                            "upload_date": row[3].isoformat() if row[3] else None,
                            "upload_datetime": row[4].isoformat() if row[4] else None,
                            "upload_status": row[5],
                            "translation_date": row[6].isoformat() if row[6] else None,
                            "translation_datetime": row[7].isoformat() if row[7] else None,
                            "translation_status": row[8],
                            "translated_zone_path": row[9],
                            "fromLanguage": row[10],
                            "toLanguage": row[11],
                            "watermark_date": row[12].isoformat() if row[12] else None,
                            "watermark_datetime": row[13].isoformat() if row[13] else None,
                            "watermark_status": row[14],
                            "watermark_zone_path": row[15],
                            "glossary_content": row[16],
                            "glossary_processing_status": row[17],
                            "glossary_zone_path": row[18],
                            "uploaded_by": row[19],
                            "statue": row[20],
                            "exclusion_text": row[21],
                        }
                    )
        except DatabaseError as e:
            logging.error("Database error: %s", str(e))
            raise
        except Exception as e:
            logging.error("Unexpected error: %s", str(e))
            raise
        finally:
            if conn:
                conn.close()
        return logs


    def fetch_all_prompts(self):
        """
        Fetch all prompts from the prompt_logs table.

        Returns:
            list: A prompts the rows retrieved.

        Raises:
            DatabaseError: If there is a general database error.
            Exception: If there is an unexpected error.
        """
        conn = None
        logs = []
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                query = sql.SQL(
                    """
                    SELECT id, prompt_name, prompt_text
                    FROM prompt_logs 
                    ORDER BY updated_at DESC
                    """
                )
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    logs.append(
                        {
                            "id": row[0],
                            "prompt_name": row[1],
                            "prompt_text": row[2]
                        }
                    )
        except DatabaseError as e:
            logging.error("Database error: %s", str(e))
            raise
        except Exception as e:
            logging.error("Unexpected error: %s", str(e))
            raise
        finally:
            if conn:
                conn.close()
        return logs
