"""
    Helper for implementing model activity updates
"""

import os
import traceback
from typing import Optional
from logging import Logger
from enum import Enum
from httpx import AsyncClient
from .sync_wrapper import sync_wrapper

CF_ACTIVITY_URL = os.getenv("CF_ACTIVITY_URL")


class ActivityStatus(Enum):
    """
    Model activity statuses.
    PENDING -> STARTED -> Terminal(COMPLETED or FAILED)
    """

    PENDING = "pending"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class ModelActivity:
    """
    Wraps model activity related Rest API
    """

    def __init__(
        self,
        logger: Logger,
        correlation_id: str,
        model_name: str,
        description: str,
        tags: str,
        app_key: str,
    ) -> None:
        # Fail fast if misconfigured
        assert CF_ACTIVITY_URL, "CF_ACTIVITY_URL is not configured"

        self.activity_id = None
        self.done = False
        self.logger = logger
        self.correlation_id = correlation_id
        self.model_name = model_name
        self.description = description
        self.tags = tags
        self.app_key = app_key

    def _get_api_header(self):
        return {"x-app-key": self.app_key, "correlation-id": self.correlation_id}

    async def create_activity_async(self) -> None:
        """
        Create a new activity
        """
        try:
            assert (
                self.activity_id is None
            ), "It is not possible to recreate an existing activity"

            self.logger.info(
                f"{self.correlation_id} Creating activity for model: {self.model_name}"
            )

            params = {
                "frogmodel_name": self.model_name,
                "description": self.description,
                "tags": self.tags,
            }

            async with AsyncClient() as client:
                response = await client.post(
                    f"{CF_ACTIVITY_URL}/activity",
                    headers=self._get_api_header(),
                    params=params,
                )

            if response.status_code != 200:
                raise ConnectionError(
                    f"{self.correlation_id} Unable to create activity: {response.status_code}"
                )

            result = response.json()

            self.activity_id = result["ActivityId"]

            self.logger.info(
                f"{self.correlation_id} Activity ID created: {self.activity_id}"
            )

            return self.activity_id

        except Exception as e:
            # Ensure that an activity related failure does not stop the calling process
            trace_back = traceback.format_exc()
            self.logger.error(
                "%s Ignoring exception while creating activity: %s",
                self.correlation_id,
                e,
            )
            self.logger.debug(f"{self.correlation_id} {trace_back}")

    create_activity = sync_wrapper(create_activity_async)

    async def update_activity_async(
        self,
        activity_status: ActivityStatus,
        last_message: Optional[str] = None,
        progress: Optional[int] = None,
    ):
        """
        Update an existing activity
        """

        try:
            assert (
                self.activity_id
            ), "No activity_id. Check create_activity has been called"
            assert len(self.activity_id) == 36

            self.logger.info(f"activity_status: {activity_status}")
            self.logger.info(f"last_message: {last_message}")
            self.logger.info(f"progress: {progress}")

            if self.done:
                raise ValueError("Cannot update a closed activity")

            if activity_status in [ActivityStatus.COMPLETED, ActivityStatus.FAILED]:
                self.done = True

            params = {
                "frogmodel_name": self.model_name,
                "activity_id": self.activity_id,
                "activity_status": activity_status.value,
            }

            if progress:
                params["progress"] = progress

            if last_message:
                # Also, automatically log messages on the sender side also
                self.logger.info(f"{self.correlation_id} {last_message}")
                params["last_message"] = last_message

            async with AsyncClient() as client:
                response = await client.put(
                    f"{CF_ACTIVITY_URL}/activity",
                    headers=self._get_api_header(),
                    params=params,
                )

            if response.status_code != 200:
                raise ConnectionError(
                    f"{self.correlation_id} Unable to update activity: {response.status_code} {response.text}"
                )

            self.logger.info(
                f"{self.correlation_id} Activity ID updated: {self.activity_id}"
            )
        except Exception as e:
            # Ensure that an activity related failure does not stop the calling process
            trace_back = traceback.format_exc()
            self.logger.error(
                "%s Ignoring exception while updating activity: %s",
                self.correlation_id,
                e,
            )
            self.logger.debug(f"{self.correlation_id} {trace_back}")

    update_activity = sync_wrapper(update_activity_async)


class AsyncFrogActivityHandler:
    """
    Async wrapper for Frog Model Activity notifications service

    Supports context manager style usage

    Can be used to create and update activities
    """

    # A new activity has:
    #
    # model_name: str =
    # Query(..., max_length=1024, description="The model the activity relates to"),
    #
    # description: str =
    # Query(..., max_length=1024, description="A short description of the activity"),
    #
    # tags: str = Query(..., max_length=1024, description="CSV tags for the activity"),

    def __init__(
        self,
        logger: Logger,
        correlation_id: str,
        model_name: str,
        description: str,
        tags: str,
        app_key: str,
    ) -> None:
        self.activity_id = None
        self.activity = ModelActivity(
            logger, correlation_id, model_name, description, tags, app_key
        )

        self.logger = logger

    async def __aenter__(self):
        try:
            activity_id = await self.activity.create_activity_async()
            self.activity_id = activity_id
        except Exception as e:
            self.logger.debug(
                f"{self.activity.correlation_id} Failed to create activity due to exception"
            )
            raise e

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            # If this activity has already been closed, then close automatically
            if not self.activity.done:
                if exc_type is None and exc_val is None and exc_tb is None:
                    await self.activity.update_activity_async(ActivityStatus.COMPLETED)
                else:
                    await self.activity.update_activity_async(ActivityStatus.FAILED)
                    raise exc_val

                self.activity.done = True

        except Exception as e:
            self.logger.debug(
                f"{self.activity.correlation_id} Failed to close activity due to exception"
            )
            self.logger.error(traceback.format_exc())
            raise e

        return self

    async def update_activity_async(
        self,
        activity_status: ActivityStatus,
        last_message: Optional[str] = None,
        progress: Optional[int] = None,
    ):
        """
        Update activity while in context
        """
        await self.activity.update_activity_async(
            activity_status, last_message, progress
        )
