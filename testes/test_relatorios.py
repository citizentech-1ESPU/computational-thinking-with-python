from datetime import date

import pytest

import dados
import relatorios

EXEMPLO = dados.dados_de_exemplo(date(2026, 11, 9))
ULTIMA = EXEMPLO["feiras"][-1]          # domingo, 08/11, 31 °C


def test_numeros_do_produto():
    numeros = relatorios.numeros_do_produto(ULTIMA["produtos"][3])     # Pescada
    assert numeros["guardado_kg"] == 0.0
    assert numeros["receita_xepa"] == pytest.approx(60.0)              # 2,5 kg a R$ 24,00
    assert numeros["perda"] == pytest.approx(41.6)                     # 1,3 kg a R$ 32,00


def test_resumo_da_feira():
    resumo = relatorios.resumo_da_feira(ULTIMA)
    esperado = {"trouxe_kg": 45.0, "vendido_kg": 29.6, "xepa_kg": 7.7, "doado_kg": 3.8, "descartado_kg": 2.6,
                "guardado_kg": 1.3, "receita_normal": 942.78, "receita_xepa": 183.96, "valor_doado": 121.08,
                "perda": 82.94, "salvo_kg": 11.5}
    for chave, valor in esperado.items():
        assert resumo[chave] == pytest.approx(valor)
    assert resumo["aproveitamento"] == pytest.approx(94.2, abs=0.05)


def test_registro_antigo_sem_algum_campo_conta_como_zero():
    linha = {"produto_id": "produto-9", "nome": "Tainha", "preco_kg": 20.0, "trouxe_kg": 5.0, "vendido_kg": 5.0}
    resumo = relatorios.resumo_da_feira({"data": "2026-10-01", "temperatura_ar_c": 25.0, "caixas": [], "produtos": [linha]})
    assert (resumo["descartado_kg"], resumo["receita_xepa"], resumo["aproveitamento"]) == (0, 0, 100.0)
    vazia = relatorios.resumo_da_feira({"data": "2026-10-01", "temperatura_ar_c": 25.0, "caixas": [], "produtos": []})
    assert vazia["aproveitamento"] is None


def test_frases_da_feira():
    assert relatorios.frases_da_feira(relatorios.resumo_da_feira(ULTIMA)) == [
        "94% da mercadoria foi aproveitada e 2,6 kg foram para o descarte.",
        "A xepa rendeu R$ 183,96.",
        "3,8 kg viraram doação (R$ 121,08 em comida).",
        "Xepa e doação salvaram 11,5 kg do lixo.",
        "O descarte custou R$ 82,94.",
    ]
    assert relatorios.frases_da_feira(relatorios.resumo_da_feira(EXEMPLO["feiras"][1])) == [
        "100% da mercadoria foi aproveitada: nada foi para o descarte.",
        "A xepa rendeu R$ 85,98.",
        "2,3 kg viraram doação (R$ 73,72 em comida).",
        "Xepa e doação salvaram 5,9 kg do lixo.",
    ]


def test_linhas_das_tabelas():
    caixas = relatorios.linhas_das_caixas(ULTIMA)
    assert caixas[0] == ("Tilápia", "5 kg", "12h13", "6,2 °C", "25 min", "Venda normal")
    assert caixas[3] == ("Pescada", "5 kg", "10h36", "--", "--", "Hora da xepa")
    produtos = relatorios.linhas_dos_produtos(ULTIMA)
    assert produtos[3] == ("Pescada (posta)", "12,5 kg", "7,5 kg", "2,5 kg", "1,2 kg", "1,3 kg", "0 kg")


def test_semana():
    resumo = relatorios.resumo_da_semana(EXEMPLO["feiras"], date(2026, 11, 8))
    assert resumo["datas"] == ["2026-11-05", "2026-11-08"]
    assert resumo["totais"]["descartado_kg"] == pytest.approx(4.6)
    assert resumo["totais"]["perda"] == pytest.approx(147.09)
    assert resumo["comparacao"] == "Você descartou 1,3 kg a mais que na semana anterior. Confira o gelo e as caixas."
    assert relatorios.texto_da_semana(resumo["totais"]) == (
        "Na semana: 81 kg na banca, a xepa rendeu R$ 331,82, 6,9 kg viraram doação e o descarte custou R$ 147,09.")
    assert relatorios.linhas_da_semana(resumo)[0] == ("quinta, 05/11", "36 kg", "94%", "R$ 147,86", "3,1 kg", "2 kg")
    primeira = relatorios.resumo_da_semana(EXEMPLO["feiras"], date(2026, 10, 18))
    assert primeira["comparacao"] == "Ainda não dá para comparar com a semana anterior."


def test_semana_com_menos_descarte():
    feiras = [EXEMPLO["feiras"][6], dict(EXEMPLO["feiras"][1], data="2026-11-12")]   # 05/11 quente, 12/11 fresca
    resumo = relatorios.resumo_da_semana(feiras, date(2026, 11, 15))
    assert resumo["comparacao"] == "Você descartou 2 kg a menos que na semana anterior. Boa!"


def test_semanas_com_feira():
    assert relatorios.semanas_com_feira(EXEMPLO["feiras"]) == [
        date(2026, 11, 8), date(2026, 11, 1), date(2026, 10, 25), date(2026, 10, 18)]


def test_pdf_da_feira(tmp_path):
    caminho = relatorios.caminho_do_pdf(str(tmp_path / "dados"), "2026-11-08")
    assert caminho == str(tmp_path / "relatorios" / "relatorio-2026-11-08.pdf")
    assert relatorios.gerar_pdf_da_feira(ULTIMA, caminho) is None
    with open(caminho, "rb") as arquivo:
        assert arquivo.read(5) == b"%PDF-"


def test_pdf_onde_nao_pode_salvar(tmp_path):
    bloqueio = tmp_path / "bloqueio"
    bloqueio.write_text("x", encoding="utf-8")
    assert relatorios.gerar_pdf_da_feira(ULTIMA, str(bloqueio / "relatorio.pdf")) == (
        "Não deu para salvar o PDF. Se ele estiver aberto em outro programa, feche e tente de novo.")
