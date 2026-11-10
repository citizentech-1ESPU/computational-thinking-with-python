import pytest

import internet


@pytest.fixture
def sem_internet(monkeypatch):
    """Faz toda busca na internet falhar, como se o Wi-Fi estivesse desligado."""
    def baixar_sem_conexao(url, parametros):
        return None, "Sem conexão com o servidor. Tente de novo."
    monkeypatch.setattr(internet, "baixar_json", baixar_sem_conexao)
