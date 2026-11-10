"""Regras da caixa térmica (as mesmas da caixa do Wokwi e do site), preço da xepa e dias de feira."""
import math
from datetime import timedelta

import config
import formatos
from config import CORES


def leitura_valida(temperatura):
    """Diz se a temperatura veio e está na faixa que o sensor consegue medir."""
    if temperatura is None:
        return False
    return config.TEMP_MIN_VALIDA_C <= temperatura <= config.TEMP_MAX_VALIDA_C


def minutos_ate_5c(temperatura, taxa):
    """Diz em quantos minutos a caixa passa de 5 °C na velocidade atual (None quando não vai passar)."""
    if taxa is None or taxa <= 0 or temperatura >= config.LIMITE_FRIO_C:
        return None
    return int((config.LIMITE_FRIO_C - temperatura) / taxa * 60)


def vai_esquentar_logo(temperatura, taxa):
    """Diz se a caixa passa de 5 °C em até 15 minutos, que é a hora de avisar para completar o gelo."""
    minutos = minutos_ate_5c(temperatura, taxa)
    return minutos is not None and minutos <= config.AVISO_GELO_MIN


def decidir_estado(temperatura, acumulado, taxa):
    """Decide o estado da caixa (0 a 4) na prioridade da caixa: sem leitura, descarte, xepa, gelo, normal."""
    if not leitura_valida(temperatura):
        return 4
    elif acumulado >= config.DESCARTE_APOS_MIN:
        return 3
    elif acumulado >= config.XEPA_APOS_MIN:
        return 2
    elif temperatura > config.LIMITE_FRIO_C or vai_esquentar_logo(temperatura, taxa):
        return 1
    else:
        return 0


def estado_da_leitura(leitura):
    """Diz o estado de uma leitura: quem decide é a caixa; o painel só calcula quando o código não vem."""
    if not leitura["valida"]:
        return 4
    if leitura["estado"] is not None:
        return leitura["estado"]
    return decidir_estado(leitura["temperatura"], leitura["acumulado"], leitura["taxa"])


def info_do_estado(codigo):
    """Devolve (nome, texto curto, texto de apoio, cor do texto, cor do fundo) de um estado."""
    match codigo:
        case 0:
            return ("normal", "Venda normal", "Pode vender tranquilo.", CORES["ok"], CORES["ok_fundo"])
        case 1:
            return ("gelo", "Complete o gelo", "A caixa está esquentando.", CORES["gelo"], CORES["gelo_fundo"])
        case 2:
            return ("xepa", "Hora da xepa", "Venda ou doe hoje. Não volta para a geladeira.",
                    CORES["aviso"], CORES["aviso_fundo"])
        case 3:
            return ("descarte", "Descarte", "Não venda nem doe.", CORES["perigo"], CORES["perigo_fundo"])
        case _:
            # 4 (sem leitura) ou um código que a caixa não manda
            return ("sensor", "Sem leitura", "Confira o sensor da caixa.", CORES["apagado"], CORES["linha"])


def codigo_do_texto(texto):
    """Acha o código do estado pelo texto curto, como Hora da xepa (None se não achar)."""
    for codigo in range(5):
        if info_do_estado(codigo)[1] == texto:
            return codigo
    return None


def preco_xepa_sugerido(preco):
    """Sugere o preço da xepa: 25% menos, arredondado para baixo em 10 centavos (igual ao site)."""
    if preco is None or preco <= 0:
        return None
    # a conta em centavos inteiros evita o erro de vírgula do computador (é o que faz 2,80 dar 2,10)
    return math.floor(round(preco * 100) * (1 - config.DESCONTO_XEPA) / 10) / 10


def proxima_feira(agora):
    """Acha a data da próxima feira (quinta ou domingo); depois das 14h, a de hoje já passou."""
    local = agora.astimezone(config.FUSO_SAO_PAULO)
    data = local.date()
    if local.hour * 60 + local.minute >= formatos.minutos_do_dia(config.FIM_DA_FEIRA):
        data = data + timedelta(days=1)
    while data.weekday() not in config.DIAS_DE_FEIRA:
        data = data + timedelta(days=1)
    return data
