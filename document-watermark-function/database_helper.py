"""
Module for handling database operations related to watermark file records.
"""

import logging
import os
from datetime import datetime
import psycopg2
from psycopg2 import sql, DatabaseError, IntegrityError, OperationalError

# PostgreSQL connection details
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")  # Ensure the default is a string
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")

# Log environment variables to check if they exist
logging.debug("DB_HOST: %s", DB_HOST)
logging.debug("DB_PORT: %s", DB_PORT)
logging.debug("DB_NAME: %s", DB_NAME)
logging.debug("DB_USER: %s", DB_USER)
logging.debug("DB_PASSWORD: %s", "****" if DB_PASSWORD else None)
logging.debug("DB_SSLMODE: %s", DB_SSLMODE)


def get_connection():
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
    except OperationalError as e:
        logging.error("Error connecting to the database: %s", str(e))
        raise    


def update_watermark_file_record(file_name, watermark_status="failed", watermark_zone_path=""):
    """
    Update the record of the file in the PostgreSQL database.
    Args:
        file_name (str): The name of the file.
        watermark_status (str): The status of the watermark ('failed', 'in progress', 'done').
        watermark_zone_path (str): The path to the translated file in the translated zone.
    Raises:
        IntegrityError: If there is an integrity constraint violation.
        DatabaseError: If there is a general database error.
        OperationalError: If there is an error connecting to the database.
    """
    conn = None
    watermark_date = datetime.now().date()
    watermark_datetime = datetime.now()
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            update_query = sql.SQL(
                """
                UPDATE file_translation_logs
                SET watermark_date = %s,
                    watermark_datetime = %s,
                    watermark_status = %s,
                    watermark_zone_path = %s               
                WHERE file_name = %s
                """
            )
            cursor.execute(
                update_query,
                (
                    watermark_date,
                    watermark_datetime,
                    watermark_status,
                    watermark_zone_path,
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
    except psycopg2.Error as e:
        logging.error("Psycopg2 error: %s", str(e))
        if conn:
            conn.rollback()
    except Exception as e:
        logging.error("Unexpected error: %s", str(e))
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
