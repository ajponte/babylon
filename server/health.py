"""Health route."""


def health():
    """
    A simple health route.
    :return: Tuple of OK message and HTTP 200 status.
    """
    # Simple health check for now.
    return "OK", 200
