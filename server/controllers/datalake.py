"""Datalake controller methods."""
from typing import Any
from http import HTTPStatus


def sync_status_get() -> tuple[dict[str, Any], int]:
    """
    Fetch the most recent sync status record.

    :return: The most recent known record.
    """
    return {
        "records": [
            {
                "collection": "source-2025-01-30",
                "lastSyncTimestamp": "2025-09-21T03:39:07.757+00:00",
                "lastSyncRecordsUploaded": 20
            }
        ]
    }, HTTPStatus.OK
