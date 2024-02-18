"""Library defining the interface for the schedule API."""
from __future__ import annotations

import logging

from google.protobuf.field_mask_pb2 import FieldMask

from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.swagger.swagger_client import ScheduleSchedule as ScheduleSchema
from rime_sdk.swagger.swagger_client import (
    ScheduleServiceApi,
    SchedulesScheduleScheduleIdUuidBody,
)

logger = logging.getLogger(__name__)


class Schedule:
    """An interface for the schedule API.

    This interface provides methods to interact with the schedule API which allows
    you to manage schedules with various methods.

    Args:
        api_client: The API client.
        schedule_id: The schedule ID.
    """

    def __init__(self, api_client: ApiClient, schedule_id: str) -> None:
        """Initialize the schedule interface.

        Args:
            api_client: The API client.
            schedule_id: The schedule ID to interface with.
        """
        self._api_client = api_client
        self._schedule_id = schedule_id

    def __repr__(self) -> str:
        """Get the string representation of the schedule."""
        return f"{self.__class__.__name__}({self._schedule_id})"

    def __str__(self) -> str:
        """Get the string form of the schedule."""
        return f"Schedule  (ID: {self._schedule_id})"

    def __eq__(self, other: object) -> bool:
        """Check if the schedule is equal to another schedule."""
        if not isinstance(other, Schedule):
            return False

        return self._schedule_id == other._schedule_id

    @property
    def schedule_id(self) -> str:
        """Get the schedule ID.

        Returns:
            str: The schedule ID.
        """
        return self._schedule_id

    @property
    def info(self) -> dict:
        """Get the schedule information.

        Returns:
            dict: The schedule information.
        """
        return self._get()

    def _get(self) -> dict:
        """Get the schedule information.

        Returns:
            Schedule: The schedule information.
        """
        raise NotImplementedError

    def update(
        self,
        frequency_cron_expr: str,
    ) -> ScheduleSchema:
        """Update the schedule.

        Args:
            frequency_cron_expr: The frequency cron expression.

        Returns:
            str: The updated schedule id.
        """
        if not self._schedule_id:
            raise ValueError(
                "No schedule ID has been attached to the object.  Please add a schedule ID to the object or create a new schedule."
            )
        api = ScheduleServiceApi(self._api_client)
        with RESTErrorHandler():
            mask = FieldMask()
            mask.paths.append("frequency_cron_expr")
            body = SchedulesScheduleScheduleIdUuidBody(
                frequency_cron_expr=frequency_cron_expr,
            )

            response = api.schedule_service_update_schedule(
                body=body,
                schedule_schedule_id_uuid=self._schedule_id,
                update_mask="frequency_cron_expr",
            )

            return response.schedule

    def delete(self) -> None:
        """Delete the schedule."""
        raise NotImplementedError
