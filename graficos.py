"""Gráficos do painel (matplotlib): a temperatura da caixa e a mercadoria da semana."""
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure

import config
import formatos
import regras
import relatorios
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
