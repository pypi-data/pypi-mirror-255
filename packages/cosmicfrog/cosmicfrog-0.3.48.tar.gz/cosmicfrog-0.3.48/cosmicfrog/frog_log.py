"""
    Easy logging wrapper for cosmicfrog library, supports Insights logging if available
"""

import logging
import os
import sys
from logging import Logger
from opencensus.ext.azure.log_exporter import AzureLogHandler

app_logger = {}


def get_logger(console_only: bool = False) -> Logger:
    """
    Gets a appropriate Logger instance (configured, connected to Insights as appropriate)
    """

    current_pid = str(os.getpid())

    if current_pid in app_logger:
        return app_logger[current_pid]
    else:
        log_level = os.getenv("FROG_LOG_LEVEL") or logging.DEBUG
        log_level = int(log_level)

        logger = logging.getLogger(current_pid)
        app_logger[current_pid] = logger

        # Add log to Insights (OL internal only)
        if not console_only:
            insights_connection = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

            if insights_connection:
                logger.addHandler(
                    AzureLogHandler(connection_string=insights_connection)
                )

        # Add log to console
        stdhandler = logging.StreamHandler(sys.stdout)
        stdhandler.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        stdhandler.setFormatter(formatter)
        logger.addHandler(stdhandler)

        logger.setLevel(log_level)

    return logger
