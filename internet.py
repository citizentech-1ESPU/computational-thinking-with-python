"""Busca na internet com tempo limite e mensagens no tom da feira (as mesmas do site)."""
import requests

import config

NAO_ENCONTRADO = "Endereço não encontrado."


def baixar_json(url, parametros):
    """Busca um JSON na internet. Devolve (valor, erro) e nunca deixa a exceção chegar na janela."""
    try:
        resposta = requests.get(url, params=parametros, timeout=config.TEMPO_LIMITE_S)
    except requests.exceptions.Timeout:
        # vem primeiro porque a conexão que demora para abrir conta como as duas coisas
        return None, "A conexão está lenta. Tente de novo."
    except requests.exceptions.ConnectionError:
        return None, "Sem conexão com o servidor. Tente de novo."
    except requests.exceptions.RequestException:
        return None, "O servidor não respondeu. Tente de novo."
    if resposta.status_code == 404:
        return None, NAO_ENCONTRADO
    try:
        resposta.raise_for_status()
        return resposta.json(), None
    except (requests.exceptions.HTTPError, ValueError):
        return None, "O servidor não respondeu. Tente de novo."
