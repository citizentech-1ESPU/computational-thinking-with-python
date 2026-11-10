import math
from datetime import date, datetime

import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import date2num
from matplotlib.figure import Figure

import config
import dados
import graficos
import relatorios
import thingspeak
from apoio import leituras_de_um_dia


def test_grafico_da_temperatura():
    figura = graficos.grafico_temperatura(leituras_de_um_dia())
    assert isinstance(figura, Figure)
    eixo = figura.axes[0]
    assert eixo.get_title() == "Temperatura da caixa"
    assert len(eixo.lines) == 2           # a temperatura e a linha dos 5 °C
    assert len(eixo.collections) == 1     # os pontos, coloridos pelo estado


def test_grafico_da_temperatura_vai_das_3h_as_22h_do_dia():
    # Uma leitura da véspera não muda o dia do gráfico: vale o dia da última leitura (15/11).
    vespera = thingspeak.interpretar_feed({"created_at": "2026-11-14T20:00:00Z", "field1": "3.0", "field2": "0",
                                           "field3": "0", "field4": "0", "field5": "240"})
    figura = graficos.grafico_temperatura([vespera] + leituras_de_um_dia())
    eixo = figura.axes[0]
    inicio = datetime(2026, 11, 15, 3, 0, tzinfo=config.FUSO_SAO_PAULO)
    fim = datetime(2026, 11, 15, 22, 0, tzinfo=config.FUSO_SAO_PAULO)
    um_segundo = 1 / (24 * 60 * 60)
    assert eixo.get_xlim() == pytest.approx((date2num(inicio), date2num(fim)), abs=um_segundo)
    FigureCanvasAgg(figura).draw()
    horas = []
    for rotulo in eixo.get_xticklabels():
        horas.append(rotulo.get_text())
    assert horas[0] == "03h" and horas[-1] == "22h" and len(horas) == 20


def test_linha_para_quando_a_caixa_fica_desligada():
    # De 15h01 a 15h20 não chegou leitura (mais de 5 minutos): a linha não liga os dois pontos.
    depois = thingspeak.interpretar_feed({"created_at": "2026-11-15T15:20:00Z", "field1": "3.0", "field2": "250",
                                          "field3": "3", "field4": "0", "field5": "0"})
    figura = graficos.grafico_temperatura(leituras_de_um_dia() + [depois])
    temperaturas = figura.axes[0].lines[0].get_ydata()
    vazios = 0
    for temperatura in temperaturas:
        if math.isnan(temperatura):
            vazios = vazios + 1
    assert vazios == 1
    assert len(figura.axes[0].collections[0].get_offsets()) == 6   # os pontos continuam todos lá


def test_grafico_sem_leituras_nao_quebra():
    figura = graficos.grafico_temperatura([])
    assert figura.axes[0].texts[0].get_text() == "Sem leituras para mostrar."


def test_grafico_da_semana():
    exemplo = dados.dados_de_exemplo(date(2026, 11, 9))
    figura = graficos.grafico_da_semana(relatorios.resumo_da_semana(exemplo["feiras"], date(2026, 11, 8)))
    eixo = figura.axes[0]
    assert len(eixo.containers) == 4
    legenda = []
    for texto in eixo.get_legend().get_texts():
        legenda.append(texto.get_text())
    assert legenda == ["Vendido", "Xepa", "Doado", "Descartado"]
