from datetime import date

from matplotlib.figure import Figure

import dados
import graficos
import relatorios
from apoio import leituras_de_um_dia


def test_grafico_da_temperatura():
    figura = graficos.grafico_temperatura(leituras_de_um_dia())
    assert isinstance(figura, Figure)
    eixo = figura.axes[0]
    assert eixo.get_title() == "Temperatura da caixa"
    assert len(eixo.lines) == 2           # a temperatura e a linha dos 5 °C
    assert len(eixo.collections) == 1     # os pontos, coloridos pelo estado


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
