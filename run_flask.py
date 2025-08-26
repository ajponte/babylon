import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from server.app import create_app
from server.config.hashicorp import OpenBaoApiClient

DEFAULT_BAO_ADDRESS = 'http://127.0.0.1:8200'
DEFAULT_BAO_VAULT_TOKEN = 'dev-only-token'
SECRETS_PATH = 'test'


def main():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    # -h conflicts, so using -n for hostname flag instead of -h
    parser.add_argument('-n', dest='host', default='0.0.0.0', help="Hostname")
    parser.add_argument('-p', dest='port', type=int, default=8080, help="Port")
    parser.add_argument('-d', dest='debug', type=bool, default=True, help="Debug True/False")

    args, extras = parser.parse_known_args()

    app = create_app()

    app.run(host=args.host, port=args.port, debug=args.debug)

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
    print('Done writing secrets')

if __name__ == '__main__':
    os.environ['BAO_ADDR'] = DEFAULT_BAO_ADDRESS
    os.environ['OPENBAO_SECRETS_PATH'] = SECRETS_PATH
    os.environ['VAULT_TOKEN'] = DEFAULT_BAO_VAULT_TOKEN
    _set_secrets()
    main()
