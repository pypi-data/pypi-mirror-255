"""
Module with helper functions for working with sqlalchemy
"""

import os
import time
import sqlalchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

CFLIB_STATEMENT_TIMEOUT = (
    os.getenv("CFLIB_STATEMENT_TIMEOUT") or 1800000
)  # Statement timeout in milliseconds = 30 minutes
CFLIB_IDLE_TRANSACTION_TIMEOUT = os.getenv("CFLIB_IDLE_TRANSACTION_TIMEOUT") or 1800
CFLIB_CONNECT_TIMEOUT = os.getenv("CFLIB_CONNECT_TIMEOUT") or 15  # Connection timeout in seconds
CFLIB_DEFAULT_MAX_RETRIES = os.getenv("CFLIB_DEFAULT_MAX_RETRIES") or 5
CFLIB_DEFAULT_RETRY_DELAY = os.getenv("CFLIB_DEFAULT_RETRY_DELAY") or 5


def create_engine_with_retry(
    logger,
    connection_string: str,
    application_name: str,
    max_retries: int = CFLIB_DEFAULT_MAX_RETRIES,
    retry_delay: int = CFLIB_DEFAULT_RETRY_DELAY,
) -> sqlalchemy.Engine:
    """
    Wrapper for sqlalchemy.create_engine - adds ping with retries, to ensure connection is valid for use
    """

    connection_string = f"{connection_string}&application_name={application_name}"

    engine = sqlalchemy.create_engine(
        connection_string,
        connect_args={"connect_timeout": CFLIB_CONNECT_TIMEOUT},
        execution_options={"statement_timeout": CFLIB_STATEMENT_TIMEOUT},
    )

    for attempt in range(max_retries):
        try:
            # Attempt to establish a connection and successful ping
            with engine.connect() as connection:
                connection.execute(text("SELECT 1;"))
                return engine

        except OperationalError:
            logger.warning("create_engine_with_retry: Database not ready, retrying")
            if attempt < max_retries - 1:
                # TODO: Async
                time.sleep(retry_delay)
            else:
                raise  # Re-raise the exception if all retries fail
