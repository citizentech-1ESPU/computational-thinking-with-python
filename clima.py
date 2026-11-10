"""Temperatura do ar no horário da feira, pela previsão pública da Open-Meteo (sem chave)."""
import config
import formatos
import internet


def buscar_previsao():
    """Busca a temperatura de hora em hora (7 dias para trás e 16 para a frente). Devolve (horarios, erro)."""
    parametros = {"latitude": config.LATITUDE, "longitude": config.LONGITUDE, "hourly": "temperature_2m",
                  "timezone": "America/Sao_Paulo", "past_days": 7, "forecast_days": 16}
    resposta, erro = internet.baixar_json(config.URL_OPEN_METEO, parametros)
    if erro is not None:
        return None, f"{erro} Digite a temperatura esperada."
    incompleta = "A previsão do tempo veio incompleta. Digite a temperatura esperada."
    if not isinstance(resposta, dict) or not isinstance(resposta.get("hourly"), dict):
        return None, incompleta
    horarios = resposta["hourly"]
    if not isinstance(horarios.get("time"), list) or not isinstance(horarios.get("temperature_2m"), list):
        return None, incompleta
    return horarios, None


def media_na_feira(horarios, data):
    """Calcula a média da temperatura das 6h às 14h do dia (None se a previsão não tiver o dia)."""
    prefixo = data.isoformat()
    tempos = horarios["time"]
    temperaturas = horarios["temperature_2m"]
    soma = 0.0
    quantidade = 0
    for indice in range(min(len(tempos), len(temperaturas))):
        texto = str(tempos[indice])
        if texto.startswith(prefixo) and texto[11:13].isdigit() and temperaturas[indice] is not None:
            hora = int(texto[11:13])
            # o valor das 13h vale para a hora das 13h às 14h, que é a última da feira
            if 6 <= hora <= 13:
                soma = soma + temperaturas[indice]
                quantidade = quantidade + 1
    if quantidade == 0:
        return None
    return round(soma / quantidade, 1)


def temperatura_da_feira(data):
    """Busca a temperatura média esperada no horário da feira. Devolve (temperatura, erro)."""
    horarios, erro = buscar_previsao()
    if erro is not None:
        return None, erro
    media = media_na_feira(horarios, data)
    if media is None:
        return None, f"A previsão não chega até {formatos.formatar_data(data)}. Digite a temperatura esperada."
    return media, None
