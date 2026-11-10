from datetime import date

import dados
import fechamento
from apoio import leituras_de_um_dia

EXEMPLO = dados.dados_de_exemplo(date(2026, 11, 9))
TILAPIA = EXEMPLO["produtos"][0]
CAIXA_1 = EXEMPLO["caixas"][0]


def test_linha_de_produto_certa():
    textos = {"trouxe": "12", "vendido": "9", "xepa": "1,5", "preco_xepa": "29,90", "doado": "0,5", "descartado": ""}
    linha, erros = fechamento.validar_linha_produto(TILAPIA, textos, 0)
    assert erros == {}
    assert linha == {"produto_id": "produto-1", "nome": "Tilápia (filé)", "preco_kg": 39.9, "preco_xepa_kg": 29.9,
                     "trouxe_kg": 12.0, "vendido_kg": 9.0, "xepa_kg": 1.5, "doado_kg": 0.5, "descartado_kg": 0.0}
    assert fechamento.sobra_guardada(linha) == 1.0


def test_soma_maior_que_o_que_trouxe():
    textos = {"trouxe": "10", "vendido": "9", "xepa": "1,5", "preco_xepa": "29,90", "doado": "", "descartado": ""}
    linha, erros = fechamento.validar_linha_produto(TILAPIA, textos, 0)
    assert erros == {"soma": "A soma passou do que você trouxe (10 kg)."}


def test_preco_da_xepa_precisa_ser_menor():
    textos = {"trouxe": "10", "vendido": "5", "xepa": "1", "preco_xepa": "39,90", "doado": "", "descartado": ""}
    linha, erros = fechamento.validar_linha_produto(TILAPIA, textos, 0)
    assert erros == {"preco_xepa": "O preço da xepa precisa ser menor que o normal."}


def test_caixa_na_xepa_ou_no_descarte_nao_guarda_sobra():
    textos = {"trouxe": "10", "vendido": "5", "xepa": "2", "preco_xepa": "29,90", "doado": "1", "descartado": ""}
    linha, erros = fechamento.validar_linha_produto(TILAPIA, textos, 2)
    assert erros == {"soma": "A caixa terminou em Hora da xepa: o que sobrou não volta para a geladeira. "
                             "Lance como xepa, doação ou descarte."}
    linha, erros = fechamento.validar_linha_produto(TILAPIA, textos, 3)
    assert erros == {"soma": "A caixa terminou em Descarte: o que sobrou vai para o descarte."}
    linha, erros = fechamento.validar_linha_produto(TILAPIA, textos, None)     # produto fora de caixa
    assert erros == {}


def test_linha_de_caixa():
    linha, erros = fechamento.validar_linha_caixa(CAIXA_1, {"gelo": "5", "acabou": "11h40", "estado": "Venda normal"}, None)
    assert erros == {}
    assert linha == {"caixa_id": "caixa-1", "nome": "Tilápia", "gelo_kg": 5.0, "gelo_acabou": "11:40",
                     "estado_final": 0, "max_c": None, "minutos_fora": None, "fonte": "manual"}
    do_sensor = {"acabou": "11h40", "estado": "Complete o gelo", "max_c": 6.1, "minutos_fora": 25}
    linha, erros = fechamento.validar_linha_caixa(CAIXA_1, {"gelo": "5", "acabou": "", "estado": "Venda normal"}, do_sensor)
    assert (linha["gelo_acabou"], linha["max_c"], linha["minutos_fora"], linha["fonte"]) == (None, 6.1, 25, "sensor")
    linha, erros = fechamento.validar_linha_caixa(CAIXA_1, {"gelo": "0", "acabou": "05h00", "estado": ""}, None)
    assert erros == {"gelo": "Use um número entre 0,5 e 30.",
                     "acabou": "O gelo não pode acabar antes de encher a caixa (05h30).",
                     "estado": "Escolha como a caixa terminou."}


def test_dados_do_sensor_no_dia():
    assert fechamento.dados_do_sensor(leituras_de_um_dia(), date(2026, 11, 15)) == {
        "acabou": "12h00", "estado": "Descarte", "max_c": 7.8, "minutos_fora": 250}
    assert fechamento.dados_do_sensor(leituras_de_um_dia(), date(2026, 11, 16)) is None


def test_gravar_fechamento():
    feiras = EXEMPLO["feiras"]
    nova = fechamento.montar_feira(date(2026, 11, 1), 30.0, [], [])
    assert nova == {"data": "2026-11-01", "temperatura_ar_c": 30.0, "caixas": [], "produtos": []}
    resultado = fechamento.gravar_fechamento(feiras, nova)
    assert len(resultado) == 8 and resultado[5] == nova        # substitui a feira de 01/11
    resultado = fechamento.gravar_fechamento(feiras, fechamento.montar_feira(date(2026, 11, 12), 29.0, [], []))
    assert len(resultado) == 9 and resultado[-1]["data"] == "2026-11-12"
    assert len(feiras) == 8                                     # a lista original não muda
    assert fechamento.ja_fechada(feiras, date(2026, 11, 8)) is True
    assert fechamento.ja_fechada(feiras, date(2026, 11, 12)) is False
