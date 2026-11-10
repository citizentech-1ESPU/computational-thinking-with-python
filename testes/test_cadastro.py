from datetime import date

import cadastro
import dados

EXEMPLO = dados.dados_de_exemplo(date(2026, 11, 9))
CAIXAS = EXEMPLO["caixas"]
PRODUTOS = EXEMPLO["produtos"]


def test_novo_id_pega_o_primeiro_numero_livre():
    assert cadastro.novo_id("caixa", ["caixa-1", "caixa-2", "caixa-4"]) == "caixa-3"
    assert cadastro.novo_id("produto", []) == "produto-1"


def test_id_de_caixa_apagada_nao_volta_porque_tem_historico():
    estado = dados.dados_de_exemplo(date(2026, 11, 9))
    estado["caixas"] = estado["caixas"][:3]          # a Pescada saiu do cadastro
    usados = cadastro.ids_em_uso(estado, "caixa")
    assert "caixa-4" in usados
    assert cadastro.novo_id("caixa", usados) == "caixa-5"


def test_valida_caixa():
    campos, erros = cadastro.validar_caixa({"nome": " Tainha ", "gelo": "5,5", "canal": ""}, CAIXAS, None)
    assert erros == {}
    assert campos == {"nome": "Tainha", "gelo_padrao_kg": 5.5, "canal": ""}
    campos, erros = cadastro.validar_caixa({"nome": "tilápia", "gelo": "50", "canal": "12a"}, CAIXAS, None)
    assert erros == {"nome": "Já existe uma caixa com esse nome.",
                     "gelo": "Use um número entre 0,5 e 30.",
                     "canal": "O canal tem só números, como 2345678."}
    campos, erros = cadastro.validar_caixa({"nome": "Tilápia", "gelo": "5", "canal": ""}, CAIXAS, "caixa-1")
    assert erros == {}                               # a própria caixa pode manter o nome
    campos, erros = cadastro.validar_caixa({"nome": "T", "gelo": "5", "canal": ""}, CAIXAS, None)
    assert erros == {"nome": "Use de 2 a 30 letras."}


def test_valida_produto():
    textos = {"nome": "Tainha", "categoria": "peixe", "preco": "29,90", "caixa": "Sem caixa"}
    campos, erros = cadastro.validar_produto(textos, PRODUTOS, CAIXAS, None)
    assert erros == {}
    assert campos == {"nome": "Tainha", "categoria": "peixe", "preco_kg": 29.9, "caixa_id": ""}
    textos = {"nome": "Tainha", "categoria": "carne", "preco": "0", "caixa": "Geladeira"}
    campos, erros = cadastro.validar_produto(textos, PRODUTOS, CAIXAS, None)
    assert erros == {"categoria": "Escolha uma categoria da lista.",
                     "preco": "Use um número entre 0,01 e 1000.",
                     "caixa": "Escolha uma caixa da lista."}
    textos = {"nome": "Sardinha", "categoria": "peixe", "preco": "18", "caixa": "Sardinha"}
    campos, erros = cadastro.validar_produto(textos, PRODUTOS, CAIXAS, None)
    assert erros == {"nome": "Já existe um produto com esse nome."}


def test_salvar_e_excluir():
    usados = ["caixa-1", "caixa-2", "caixa-3", "caixa-4"]
    caixas, nova = cadastro.salvar_caixa(CAIXAS, {"nome": "Tainha", "gelo_padrao_kg": 5.5, "canal": ""}, None, usados)
    assert nova == {"id": "caixa-5", "nome": "Tainha", "gelo_padrao_kg": 5.5, "canal": ""}
    assert len(caixas) == 5 and len(CAIXAS) == 4      # a lista original não muda
    caixas, mudada = cadastro.salvar_caixa(CAIXAS, {"nome": "Tilápia", "gelo_padrao_kg": 6.0, "canal": "123"}, "caixa-1", usados)
    assert caixas[0]["gelo_padrao_kg"] == 6.0 and caixas[0]["id"] == "caixa-1"
    caixas, erro = cadastro.excluir_caixa(CAIXAS, PRODUTOS, "caixa-1")
    assert erro == "A caixa Tilápia guarda Tilápia (filé). Mude o produto de caixa antes de excluir."
    caixas, erro = cadastro.excluir_caixa(CAIXAS, [], "caixa-1")
    assert erro is None and len(caixas) == 3
    assert len(cadastro.excluir_produto(PRODUTOS, "produto-1")) == 3
    assert cadastro.nome_da_caixa(CAIXAS, "caixa-2") == "Queijo"
    assert cadastro.nome_da_caixa(CAIXAS, "") == "Sem caixa"
