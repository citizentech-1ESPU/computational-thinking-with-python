"""Gráficos do painel (matplotlib): a temperatura da caixa e a mercadoria da semana."""
import math
from datetime import datetime, time, timedelta

from matplotlib.dates import DateFormatter, HourLocator
from matplotlib.figure import Figure

import config
import formatos
import regras
import relatorios
from config import CORES

# O gráfico da temperatura mostra o dia das 3h às 22h: da caixa sendo enchida (5h30) até depois da feira (14h).
PRIMEIRA_HORA = 3
ULTIMA_HORA = 22


def horario_do_grafico(quando):
    """Devolve o começo e o fim do eixo do gráfico (das 3h às 22h) no dia do momento, no fuso de São Paulo."""
    dia = quando.astimezone(config.FUSO_SAO_PAULO).date()
    inicio = datetime.combine(dia, time(PRIMEIRA_HORA), tzinfo=config.FUSO_SAO_PAULO)
    fim = datetime.combine(dia, time(ULTIMA_HORA), tzinfo=config.FUSO_SAO_PAULO)
    return inicio, fim


def pontos_da_linha(horarios, temperaturas):
    """Monta os pontos da linha do gráfico, cortando a linha onde a caixa ficou desligada.

    Mais de 5 minutos entre duas leituras é caixa desligada; um valor vazio (nan) entre elas faz o
    matplotlib parar a linha ali, para o gráfico não inventar a temperatura de quando não houve leitura.
    """
    linha_horarios = []
    linha_temperaturas = []
    for indice in range(len(horarios)):
        if indice > 0 and horarios[indice] - horarios[indice - 1] > timedelta(minutes=config.CAIXA_DESLIGADA_MIN):
            linha_horarios.append(horarios[indice - 1])
            linha_temperaturas.append(math.nan)
        linha_horarios.append(horarios[indice])
        linha_temperaturas.append(temperaturas[indice])
    return linha_horarios, linha_temperaturas


def grafico_temperatura(leituras):
    """Desenha a temperatura da caixa ao longo do tempo, com a linha dos 5 °C e a cor de cada estado."""
    figura = Figure(figsize=(7.5, 3.2))
    eixo = figura.add_subplot()
    eixo.set_title("Temperatura da caixa")
    horarios = []
    temperaturas = []
    cores = []
    for leitura in leituras:
        if leitura["valida"]:
            horarios.append(leitura["quando"])
            temperaturas.append(leitura["temperatura"])
            cores.append(regras.info_do_estado(regras.estado_da_leitura(leitura))[3])
    if len(horarios) == 0:
        eixo.text(0.5, 0.5, "Sem leituras para mostrar.", ha="center", va="center",
                  transform=eixo.transAxes, color=CORES["apagado"])
        eixo.set_xticks([])
        eixo.set_yticks([])
        return figura
    linha_horarios, linha_temperaturas = pontos_da_linha(horarios, temperaturas)
    eixo.plot(linha_horarios, linha_temperaturas, color=CORES["texto"], linewidth=1.5)
    eixo.axhline(config.LIMITE_FRIO_C, linestyle="--", color=CORES["perigo"], linewidth=1)
    eixo.scatter(horarios, temperaturas, c=cores, s=24, zorder=3)
    eixo.set_ylabel("°C")
    # vale o dia da última leitura (em "Últimas leituras", as de dias anteriores ficam fora)
    inicio, fim = horario_do_grafico(horarios[-1])
    eixo.set_xlim(inicio, fim)
    eixo.xaxis.set_major_locator(HourLocator(byhour=range(PRIMEIRA_HORA, ULTIMA_HORA + 1),
                                             tz=config.FUSO_SAO_PAULO))
    eixo.xaxis.set_major_formatter(DateFormatter("%Hh", tz=config.FUSO_SAO_PAULO))
    eixo.tick_params(axis="x", labelsize=8)
    figura.tight_layout()
    return figura


def grafico_da_semana(resumo_semana):
    """Desenha barras empilhadas com o destino da mercadoria em cada feira da semana."""
    figura = Figure(figsize=(7.5, 3.2))
    eixo = figura.add_subplot()
    eixo.set_title("Mercadoria da semana")
    rotulos = []
    partes = {"vendido_kg": [], "xepa_kg": [], "doado_kg": [], "descartado_kg": []}
    for feira in resumo_semana["feiras"]:
        data = relatorios.data_da_feira(feira)
        rotulos.append(f"{formatos.dia_da_semana(data)[:3]} {data.day:02d}/{data.month:02d}")
        resumo = relatorios.resumo_da_feira(feira)
        for chave in partes:
            partes[chave].append(resumo[chave])
    series = (("vendido_kg", "Vendido", CORES["ok"]), ("xepa_kg", "Xepa", CORES["aviso_forte"]),
              ("doado_kg", "Doado", CORES["gelo"]), ("descartado_kg", "Descartado", CORES["perigo"]))
    base = []
    for rotulo in rotulos:
        base.append(0)
    for chave, nome, cor in series:
        eixo.bar(rotulos, partes[chave], bottom=base, label=nome, color=cor)
        for indice in range(len(base)):
            base[indice] = base[indice] + partes[chave][indice]
    eixo.set_ylabel("kg")
    eixo.legend()
    figura.tight_layout()
    return figura
