import os
from datetime import date

import dados
import tela_cadastro
import tela_historico
import tela_inicio
from apoio import FEEDS_DE_UM_DIA, abrir_area, textos_da_tela

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


def test_historico_sem_internet_usa_as_leituras_salvas(tmp_path, sem_internet):
    estado = dados.carregar_tudo(str(tmp_path / "dados"), HOJE)
    estado["caixas"][0]["canal"] = "123"
    estado["leituras"]["123"] = {"salvo_em": "2026-11-15T12:30:00-03:00", "feeds": FEEDS_DE_UM_DIA}
    raiz, area = abrir_area()
    try:
        tela_historico.montar(area, estado)
        raiz.update()
        textos = " ".join(textos_da_tela(area))
        assert "Mostrando as leituras salvas de domingo, 15/11 às 12h30." in textos
        assert "Descarte" in textos and "12h00" in textos
    finally:
        raiz.destroy()


def test_historico_sem_caixa_com_sensor(tmp_path):
    estado = dados.carregar_tudo(str(tmp_path / "dados"), HOJE)
    estado["caixas"][0]["canal"] = ""
    raiz, area = abrir_area()
    try:
        tela_historico.montar(area, estado)
        raiz.update()
        assert "Nenhuma caixa tem sensor ligado. Coloque o número do canal em Caixas e produtos." in textos_da_tela(area)
    finally:
        raiz.destroy()
