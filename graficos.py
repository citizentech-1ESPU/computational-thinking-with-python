"""Gráficos do painel (matplotlib): a temperatura da caixa e a mercadoria da semana."""
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure

import config
import regras
from config import CORES


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
    eixo.plot(horarios, temperaturas, color=CORES["texto"], linewidth=1.5)
    eixo.axhline(config.LIMITE_FRIO_C, linestyle="--", color=CORES["perigo"], linewidth=1)
    eixo.scatter(horarios, temperaturas, c=cores, s=24, zorder=3)
    eixo.set_ylabel("°C")
    eixo.xaxis.set_major_formatter(DateFormatter("%Hh%M", tz=config.FUSO_SAO_PAULO))
    figura.tight_layout()
    return figura
