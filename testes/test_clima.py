from datetime import date

import clima
import internet

HORARIOS = {
    "time": ["2026-11-15T05:00", "2026-11-15T06:00", "2026-11-15T07:00", "2026-11-15T08:00",
             "2026-11-15T09:00", "2026-11-15T10:00", "2026-11-15T11:00", "2026-11-15T12:00",
             "2026-11-15T13:00", "2026-11-15T14:00"],
    "temperature_2m": [20.0, 24.0, 26.0, 28.0, 30.0, 31.0, 32.0, 33.0, None, 30.0],
}


def test_media_das_6h_as_14h():
    assert clima.media_na_feira(HORARIOS, date(2026, 11, 15)) == 29.1   # 6h a 13h, sem o valor que faltou
    assert clima.media_na_feira(HORARIOS, date(2026, 11, 16)) is None


def test_pede_a_previsao_certa(monkeypatch):
    pedidos = []
    def baixar_falso(url, parametros):
        pedidos.append((url, parametros))
        return {"hourly": HORARIOS}, None
    monkeypatch.setattr(internet, "baixar_json", baixar_falso)
    assert clima.temperatura_da_feira(date(2026, 11, 15)) == (29.1, None)
    assert pedidos == [("https://api.open-meteo.com/v1/forecast", {
        "latitude": -23.5, "longitude": -46.66, "hourly": "temperature_2m",
        "timezone": "America/Sao_Paulo", "past_days": 7, "forecast_days": 16})]


def test_sem_previsao_pede_para_digitar(monkeypatch):
    def baixar_sem_conexao(url, parametros):
        return None, "Sem conexão com o servidor. Tente de novo."
    monkeypatch.setattr(internet, "baixar_json", baixar_sem_conexao)
    assert clima.temperatura_da_feira(date(2026, 11, 15)) == (
        None, "Sem conexão com o servidor. Tente de novo. Digite a temperatura esperada.")

    def baixar_incompleto(url, parametros):
        return {"erro": True}, None
    monkeypatch.setattr(internet, "baixar_json", baixar_incompleto)
    assert clima.temperatura_da_feira(date(2026, 11, 15)) == (
        None, "A previsão do tempo veio incompleta. Digite a temperatura esperada.")

    def baixar_outra_semana(url, parametros):
        return {"hourly": HORARIOS}, None
    monkeypatch.setattr(internet, "baixar_json", baixar_outra_semana)
    assert clima.temperatura_da_feira(date(2026, 12, 25)) == (
        None, "A previsão não chega até 25/12/2026. Digite a temperatura esperada.")
