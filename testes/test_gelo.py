from datetime import date

import pytest

import dados
import gelo

EXEMPLO = dados.dados_de_exemplo(date(2026, 11, 9))


def test_modelo_do_gelo():
    assert gelo.minutos_de_gelo(5.0, 31.0, 2500.0) == pytest.approx(403.2, abs=0.1)
    assert gelo.constante_da_feira(5.0, 403, 31.0) == pytest.approx(2498.6)
    assert gelo.minutos_de_gelo(5.0, 4.0, 2500.0) == pytest.approx(1250.0)    # abaixo de 10 °C conta 10 °C
    assert gelo.perda_por_grau(5.0, 32.0, 2500.0) == pytest.approx(12.2, abs=0.01)


def test_gelo_necessario_sobe_de_meio_em_meio_quilo():
    assert gelo.minutos_que_a_feira_precisa() == 540
    assert gelo.gelo_necessario(540, 32.0, 2500.0) == 7.0     # precisa de 6,9 kg
    assert gelo.gelo_necessario(540, 22.0, 2500.0) == 5.0     # 4,75 kg
    assert gelo.gelo_necessario(540, 5.0, 2500.0) == 2.5      # dia frio: conta 10 °C


def test_duracao_do_gelo_numa_feira():
    assert gelo.duracao_do_gelo({"gelo_acabou": "12:13"}) == 403
    assert gelo.duracao_do_gelo({"gelo_acabou": None}) == 510    # durou a feira toda: conta até 14h


def test_constante_estimada_pelo_historico():
    assert gelo.estimar_constante(EXEMPLO["feiras"], "caixa-1") == pytest.approx(2446.0, abs=0.1)
    assert gelo.estimar_constante(EXEMPLO["feiras"], "caixa-4") == pytest.approx(1896.9, abs=0.1)
    assert gelo.estimar_constante([], "caixa-1") == 2500.0


def test_recomendacao_para_um_dia_de_32_graus():
    recomendacao = gelo.recomendar_gelo(EXEMPLO["caixas"], EXEMPLO["feiras"], 32.0)
    quilos = []
    for item in recomendacao:
        quilos.append(item["gelo_kg"])
    assert quilos == [7.5, 7.5, 7.0, 9.5]
    tilapia = recomendacao[0]
    assert (tilapia["acaba_as"], tilapia["perda_por_grau"]) == ("11:52", 12)
    assert tilapia["mensagem"] == "Leve 7,5 kg de gelo (2,5 kg a mais que o normal). Com 5 kg, o gelo acaba perto das 11h52."
    assert gelo.total_de_gelo(recomendacao) == 31.5


def test_recomendacao_para_um_dia_fresco():
    recomendacao = gelo.recomendar_gelo(EXEMPLO["caixas"], EXEMPLO["feiras"], 18.0)
    assert recomendacao[0]["mensagem"] == "Dia mais fresco: 4 kg de gelo bastam (1 kg a menos que o normal)."
    assert recomendacao[1]["mensagem"] == "Os 4 kg de sempre bastam. O gelo deve durar a feira toda."


def test_caixa_com_defeito():
    avisos = gelo.caixas_com_defeito(EXEMPLO["caixas"], EXEMPLO["feiras"])
    assert len(avisos) == 1
    assert (avisos[0]["caixa_id"], avisos[0]["vezes"], avisos[0]["analisadas"]) == ("caixa-4", 4, 4)
    assert avisos[0]["mensagem"] == ("A caixa Pescada perde o gelo mais rápido que as outras "
                                     "(4 das últimas 4 feiras). Confira a tampa e a borracha.")
    assert gelo.caixas_com_defeito(EXEMPLO["caixas"], []) == []
