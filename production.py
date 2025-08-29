"""
Production WSGI hook.
"""
from server.app import create_app

from dotenv import load_dotenv

# This is a temporary solution until config management
# (ideally through a helm-like mechanism) is set up.
# Load environment variables from the .env file.
# This must be done before the app is created.
load_dotenv()

# The application object that Gunicorn will find.
application = create_app()
