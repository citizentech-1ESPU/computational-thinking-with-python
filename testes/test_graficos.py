from matplotlib.figure import Figure

import graficos
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
