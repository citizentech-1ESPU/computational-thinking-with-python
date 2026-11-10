import requests

import internet


def resposta(codigo, corpo):
    """Monta uma resposta do requests sem ir à internet."""
    falsa = requests.models.Response()
    falsa.status_code = codigo
    falsa._content = corpo.encode("utf-8")
    return falsa


def test_devolve_o_json(monkeypatch):
    def get_ok(url, params, timeout):
        assert timeout == 8
        return resposta(200, '{"ok": 1}')
    monkeypatch.setattr(internet.requests, "get", get_ok)
    assert internet.baixar_json("https://exemplo", {"a": 1}) == ({"ok": 1}, None)


def test_sem_conexao(monkeypatch):
    def get_sem_conexao(url, params, timeout):
        raise requests.exceptions.ConnectionError()
    monkeypatch.setattr(internet.requests, "get", get_sem_conexao)
    assert internet.baixar_json("https://exemplo", {}) == (None, "Sem conexão com o servidor. Tente de novo.")


def test_conexao_lenta(monkeypatch):
    def get_lento(url, params, timeout):
        raise requests.exceptions.ConnectTimeout()
    monkeypatch.setattr(internet.requests, "get", get_lento)
    assert internet.baixar_json("https://exemplo", {}) == (None, "A conexão está lenta. Tente de novo.")


def test_endereco_nao_encontrado_e_servidor_com_problema(monkeypatch):
    def get_404(url, params, timeout):
        return resposta(404, '{"status": "404", "error": "Not Found"}')
    monkeypatch.setattr(internet.requests, "get", get_404)
    assert internet.baixar_json("https://exemplo", {}) == (None, internet.NAO_ENCONTRADO)

    def get_500(url, params, timeout):
        return resposta(500, "erro")
    monkeypatch.setattr(internet.requests, "get", get_500)
    assert internet.baixar_json("https://exemplo", {}) == (None, "O servidor não respondeu. Tente de novo.")

    def get_texto(url, params, timeout):
        return resposta(200, "isto não é json")
    monkeypatch.setattr(internet.requests, "get", get_texto)
    assert internet.baixar_json("https://exemplo", {}) == (None, "O servidor não respondeu. Tente de novo.")
