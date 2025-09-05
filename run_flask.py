import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from server.app import create_app
from server.config.hashicorp import OpenBaoApiClient

FLASK_PORT = 5003
FLASK_HOST = '0.0.0.0'

DEFAULT_BAO_ADDRESS = 'http://127.0.0.1:8200'
DEFAULT_BAO_VAULT_TOKEN = 'dev-only-token'
SECRETS_PATH = 'test'

os.environ['BAO_ADDR'] = DEFAULT_BAO_ADDRESS
os.environ['OPENBAO_SECRETS_PATH'] = SECRETS_PATH
os.environ['VAULT_TOKEN'] = DEFAULT_BAO_VAULT_TOKEN
os.environ['SQLALCHEMY_INIT_TABLES'] = True
os.environ['SQLALCHEMY_DATABASE_URL'] = True

def main():
    """
    Main function to parse command line arguments and run the Flask application.
    """
    def _set_secrets():
        openbao = OpenBaoApiClient()
        openbao.add_secret_value(
            path='test',
            secret={
                'DB_HOST': 'localhost',
                'DB_PORT': '14333',
                'DB_USERNAME': 'root',
                'DB_PASSWORD': 'root'
            }
        )
        print('Done writing mock secrets!')
    _set_secrets()
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    # -h conflicts, so using -n for hostname flag instead of -h
    parser.add_argument('-n', dest='host', default=FLASK_HOST, help="Hostname")
    parser.add_argument('-p', dest='port', type=int, default=FLASK_PORT, help="Port")

    args, extras = parser.parse_known_args()

    app = create_app()

    app.run(host=args.host, port=args.port)

if __name__ == '__main__':
    main()
