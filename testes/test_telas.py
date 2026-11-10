import os
from datetime import date

import pytest

import dados
import internet
import janela
import tela_cadastro
import tela_fechamento
import tela_gelo
import tela_historico
import tela_inicio
import tela_relatorios
from apoio import (FEEDS_DE_UM_DIA, abrir_area, janela_fora_da_tela, problemas_nos_cartoes,
                   textos_da_tela)

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


def test_fechar_a_feira_pela_tela(tmp_path):
    estado = dados.carregar_tudo(str(tmp_path / "dados"), HOJE)
    raiz, area = abrir_area()
    try:
        tela_fechamento.montar(area, estado)
        tela_fechamento.salvar()
        assert tela_fechamento.campos[("produto-1", "erro")].cget("text") == "Trouxe: Preencha este campo."
        assert tela_fechamento.campos["erro_temperatura"].cget("text") == "Preencha este campo."
        tela_fechamento.campos["temperatura"].insert(0, "29")
        for produto in estado["produtos"]:
            tela_fechamento.campos[(produto["id"], "trouxe")].insert(0, "10")
            tela_fechamento.campos[(produto["id"], "vendido")].insert(0, "9")
        tela_fechamento.salvar()
        assert len(estado["feiras"]) == 9
        assert estado["feiras"][-1]["produtos"][0]["vendido_kg"] == 9.0
    finally:
        raiz.destroy()


def test_relatorios_da_feira_da_semana_e_pdf(tmp_path):
    estado = dados.carregar_tudo(str(tmp_path / "dados"), HOJE)
    raiz, area = abrir_area()
    try:
        tela_relatorios.montar(area, estado)
        raiz.update()
        assert "94% da mercadoria foi aproveitada e 2,6 kg foram para o descarte." in textos_da_tela(area)
        tela_relatorios.salvar_pdf()
        assert os.path.exists(tmp_path / "relatorios" / "relatorio-2026-11-08.pdf")
        tela_relatorios.trocar_relatorio("Da semana")
        raiz.update()
        assert "Você descartou 1,3 kg a mais que na semana anterior. Confira o gelo e as caixas." in textos_da_tela(area)
    finally:
        raiz.destroy()


def test_gelo_sem_internet_pede_a_temperatura(tmp_path, sem_internet):
    estado = dados.carregar_tudo(str(tmp_path / "dados"), HOJE)
    raiz, area = abrir_area()
    try:
        tela_gelo.montar(area, estado)
        raiz.update()
        assert "Sem conexão com o servidor. Tente de novo. Digite a temperatura esperada." in textos_da_tela(area)
        tela_gelo.campos["temperatura"].insert(0, "32")
        tela_gelo.calcular()
        raiz.update()
        textos = textos_da_tela(area)
        assert "Total para a feira: 31,5 kg de gelo." in textos
        assert "Esta caixa perde gelo rápido: confira a tampa e a borracha." in textos
    finally:
        raiz.destroy()


def test_dados_do_sensor_so_valem_para_o_dia_puxado(tmp_path, monkeypatch):
    feeds = []
    for feed in FEEDS_DE_UM_DIA:
        copia = dict(feed)
        copia["created_at"] = copia["created_at"].replace("2026-11-15", "2026-11-08")
        feeds.append(copia)
    def baixar_falso(url, parametros):
        return {"channel": {}, "feeds": feeds}, None
    monkeypatch.setattr(internet, "baixar_json", baixar_falso)
    estado = dados.carregar_tudo(str(tmp_path / "dados"), HOJE)
    estado["caixas"][0]["canal"] = "123"
    raiz, area = abrir_area()
    try:
        tela_fechamento.montar(area, estado)
        tela_fechamento.campos["data"].delete(0, "end")
        tela_fechamento.campos["data"].insert(0, "08/11/2026")
        tela_fechamento.puxar_da_caixa()
        assert tela_fechamento.campos[("caixa-1", "acabou")].get() == "12h00"
        tela_fechamento.campos["data"].delete(0, "end")
        tela_fechamento.campos["data"].insert(0, "06/11/2026")
        tela_fechamento.campos[("caixa-1", "acabou")].delete(0, "end")
        tela_fechamento.campos[("caixa-1", "estado")].set("Venda normal")
        tela_fechamento.campos["temperatura"].insert(0, "29")
        for produto in estado["produtos"]:
            tela_fechamento.campos[(produto["id"], "trouxe")].insert(0, "10")
            tela_fechamento.campos[(produto["id"], "vendido")].insert(0, "9")
        tela_fechamento.salvar()
        feira = estado["feiras"][-1]
        for candidata in estado["feiras"]:
            if candidata["data"] == "2026-11-06":
                feira = candidata
        assert feira["data"] == "2026-11-06"
        assert (feira["caixas"][0]["fonte"], feira["caixas"][0]["max_c"]) == ("manual", None)
    finally:
        raiz.destroy()


# Leituras antigas (de 10/11), para o cartão mostrar também o aviso de leitura antiga.
FEED_GELO_ANTIGO = {"created_at": "2026-11-10T18:08:05Z", "field1": "5.4", "field2": "1", "field3": "1",
                    "field4": "2.4", "field5": "239"}
FEED_SEM_LEITURA_ANTIGO = {"created_at": "2026-11-10T18:14:18Z", "field1": "8.0", "field2": "288", "field3": "4",
                           "field4": "0.0", "field5": "0"}


@pytest.mark.parametrize("largura", [1000, 1180])
def test_cartoes_cabem_sem_cortar_texto_nem_cobrir_a_borda(tmp_path, monkeypatch, largura):
    feeds = []
    def baixar_falso(url, parametros):
        if "thingspeak" in url:
            return {"channel": {}, "feeds": feeds}, None
        return None, "Sem conexão com o servidor. Tente de novo."
    monkeypatch.setattr(internet, "baixar_json", baixar_falso)
    raiz = janela_fora_da_tela(str(tmp_path / "dados"), largura)
    try:
        for feed in (FEED_GELO_ANTIGO, FEED_SEM_LEITURA_ANTIGO):
            feeds.clear()
            feeds.append(feed)
            janela.mostrar_tela("Início")
            raiz.update()
            assert problemas_nos_cartoes(janela.contexto["area"]) == []
        janela.mostrar_tela("Gelo da próxima feira")
        tela_gelo.campos["temperatura"].insert(0, "32")
        tela_gelo.calcular()
        raiz.update()
        assert problemas_nos_cartoes(janela.contexto["area"]) == []
    finally:
        raiz.destroy()
