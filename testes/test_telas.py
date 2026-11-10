import os
from datetime import date

import dados
import tela_cadastro
import tela_inicio
from apoio import abrir_area, textos_da_tela

HOJE = date(2026, 11, 9)


def test_cadastro_lista_as_caixas(tmp_path):
    estado = dados.carregar_tudo(str(tmp_path / "dados"), HOJE)
    raiz, area = abrir_area()
    try:
        tela_cadastro.montar(area, estado)
        raiz.update()
        textos = " ".join(textos_da_tela(area))
        assert "Caixas e produtos" in textos and "Pescada" in textos
    finally:
        raiz.destroy()


def test_cadastrar_caixa_pela_tela(tmp_path):
    pasta = str(tmp_path / "dados")
    estado = dados.carregar_tudo(pasta, HOJE)
    raiz, area = abrir_area()
    try:
        tela_cadastro.montar(area, estado)
        tela_cadastro.salvar()
        assert tela_cadastro.campos["erro_nome"].cget("text") == "Preencha este campo."
        tela_cadastro.campos["nome"].insert(0, "Tainha")
        tela_cadastro.salvar()
        assert estado["caixas"][-1]["id"] == "caixa-5"
        salvas, aviso = dados.ler_json(os.path.join(pasta, "caixas.json"), [])
        assert salvas[-1]["nome"] == "Tainha" and salvas[-1]["gelo_padrao_kg"] == 5.0
    finally:
        raiz.destroy()


def test_inicio_sem_internet(tmp_path, sem_internet):
    estado = dados.carregar_tudo(str(tmp_path / "dados"), HOJE)
    estado["caixas"][0]["canal"] = "123"
    raiz, area = abrir_area()
    try:
        tela_inicio.montar(area, estado)
        raiz.update()
        textos = " ".join(textos_da_tela(area))
        assert "Início" in textos
        assert "Sem conexão com o servidor. Tente de novo." in textos
        assert "Sem sensor" in textos
    finally:
        raiz.destroy()
