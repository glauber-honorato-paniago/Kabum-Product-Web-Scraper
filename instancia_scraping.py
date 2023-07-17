import os

import requests


def nova_instancia_requests():
    try:
        sessao = requests.Session()
    except Exception as erro:
        raise ConnectionError(f'proxie_connection_error: {erro}')
    return sessao
