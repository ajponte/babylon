import datetime
from datetime import timezone

def date_to_epoch(date_obj: datetime.date) -> int:
    """
    Converts a datetime.date object to an integer.

    :param date_obj: The datetime.date object to convert.

    :return: An integer representing the epoch timestamp in seconds.
    """
    # Convert the date object to a datetime object at midnight UTC
    # We use combine to set the time to 00:00:00 and then attach the UTC timezone.
    dt_utc = datetime.datetime.combine(date_obj, datetime.time(0, 0, 0), tzinfo=timezone.utc)

    # Return the epoch timestamp as an integer
    return int(dt_utc.timestamp())

def epoch_to_date_utc(timestamp: int) -> datetime.date:
    """
    Converts an integer epoch timestamp to a datetime.date object in UTC.

    :param timestamp: An integer representing the epoch timestamp in seconds.

    :return: A datetime.date object corresponding to the timestamp in UTC.
    """
    # Convert the epoch timestamp to a datetime object in UTC.
    # The fromtimestamp method automatically handles the conversion based on the timezone.
    dt_utc = datetime.datetime.fromtimestamp(timestamp, tz=timezone.utc)

    # Return just the date part of the datetime object.
    return dt_utc.date()
