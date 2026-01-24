"""Datalake controller handlers."""
from http import HTTPStatus
import logging
from datetime import datetime, timezone

_LOGGER = logging.getLogger(__name__)

async def sync_status_get() -> tuple:
    """Get the status of the datalake sync."""
    _LOGGER.info("Getting datalake sync status")
    mock_data = {
        "status": "SUCCESS",
        "last_successful_sync": datetime.now(timezone.utc).isoformat(),
        "records_processed": 12345,
    }
    return mock_data, HTTPStatus.OK
