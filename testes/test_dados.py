import os
from datetime import date

import config
import dados

HOJE = date(2026, 11, 9)


def test_arquivo_que_nao_existe_devolve_o_padrao(tmp_path):
    assert dados.ler_json(str(tmp_path / "feiras.json"), []) == ([], None)


def test_arquivo_quebrado_vira_copia_e_recomeca(tmp_path):
    caminho = tmp_path / "feiras.json"
    caminho.write_text("{ isto não é json", encoding="utf-8")
    valor, aviso = dados.ler_json(str(caminho), [])
    assert valor == []
    assert aviso == "O arquivo feiras.json estava com defeito. Guardei uma cópia em feiras.json.quebrado e comecei de novo."
    assert os.path.exists(str(caminho) + ".quebrado")


def test_arquivo_com_tipo_errado_tambem_recomeca(tmp_path):
    caminho = tmp_path / "caixas.json"
    caminho.write_text('{"a": 1}', encoding="utf-8")
    valor, aviso = dados.ler_json(str(caminho), [])
    assert valor == [] and "caixas.json" in aviso


def test_grava_e_le_com_acento(tmp_path):
    caminho = str(tmp_path / "caixas.json")
    assert dados.gravar_json(caminho, [{"nome": "Tilápia"}]) is None
    assert dados.ler_json(caminho, []) == ([{"nome": "Tilápia"}], None)
    with open(caminho, encoding="utf-8") as arquivo:
        assert "Tilápia" in arquivo.read()


def test_gravar_onde_nao_pode_devolve_mensagem(tmp_path):
    bloqueio = tmp_path / "bloqueio"
    bloqueio.write_text("sou um arquivo, não uma pasta", encoding="utf-8")
    erro = dados.gravar_json(str(bloqueio / "caixas.json"), [])
    assert erro == "Não deu para salvar caixas.json. Confira se a pasta pode ser alterada."


def test_primeira_vez_cria_os_dados_de_exemplo(tmp_path):
    pasta = str(tmp_path / "dados")
    estado = dados.carregar_tudo(pasta, HOJE)
    assert (len(estado["caixas"]), len(estado["produtos"]), len(estado["feiras"])) == (4, 4, 8)
    assert estado["leituras"] == {} and estado["avisos"] == [] and estado["pasta"] == pasta
    for nome in ("caixas.json", "produtos.json", "feiras.json"):
        assert os.path.exists(os.path.join(pasta, nome))


def test_segunda_vez_mantem_o_que_mudou(tmp_path):
    pasta = str(tmp_path / "dados")
    estado = dados.carregar_tudo(pasta, HOJE)
    estado["caixas"][0]["nome"] = "Tainha"
    assert dados.salvar(estado, "caixas") is None
    assert dados.carregar_tudo(pasta, HOJE)["caixas"][0]["nome"] == "Tainha"


def test_restaurar_volta_ao_exemplo(tmp_path):
    estado = dados.carregar_tudo(str(tmp_path / "dados"), HOJE)
    estado["caixas"] = []
    assert dados.restaurar_exemplo(estado, HOJE) is None
    assert len(estado["caixas"]) == 4


def test_dados_de_exemplo():
    exemplo = dados.dados_de_exemplo(HOJE)
    assert dados.datas_de_exemplo(HOJE) == ["2026-10-15", "2026-10-18", "2026-10-22", "2026-10-25",
                                           "2026-10-29", "2026-11-01", "2026-11-05", "2026-11-08"]
    assert exemplo["caixas"][0] == {"id": "caixa-1", "nome": "Tilápia", "gelo_padrao_kg": 5.0,
                                    "canal": config.CANAL_THINGSPEAK_CAIXA_1}
    assert exemplo["produtos"][3] == {"id": "produto-4", "nome": "Pescada (posta)", "categoria": "peixe",
                                      "preco_kg": 32.0, "caixa_id": "caixa-4"}
    ultima = exemplo["feiras"][-1]
    assert (ultima["data"], ultima["temperatura_ar_c"]) == ("2026-11-08", 31.0)
    tilapia = ultima["caixas"][0]
    assert (tilapia["gelo_acabou"], tilapia["fonte"], tilapia["max_c"], tilapia["minutos_fora"]) == ("12:13", "sensor", 6.2, 25)
    assert ultima["caixas"][3]["estado_final"] == 2
    pescada = ultima["produtos"][3]
    assert (pescada["trouxe_kg"], pescada["vendido_kg"], pescada["xepa_kg"],
            pescada["doado_kg"], pescada["descartado_kg"]) == (12.5, 7.5, 2.5, 1.2, 1.3)
    assert pescada["preco_xepa_kg"] == 24.0
