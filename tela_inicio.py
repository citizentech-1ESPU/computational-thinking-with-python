"""Tela "Início": as caixas agora, a última feira e os avisos."""
import customtkinter

import config
import dados
import formatos
import gelo
import regras
import relatorios
import thingspeak
import visual

contexto = {"area": None, "estado": None}

# Largura (px) em que os textos do cartão quebram a linha: cabe no cartão até com a janela no tamanho mínimo.
LARGURA_DO_TEXTO = 136


def montar(area, estado):
    """Desenha a tela Início: saudação, avisos e um cartão por caixa."""
    contexto["area"] = area
    contexto["estado"] = estado
    agora = formatos.agora_em_sao_paulo()
    proxima = regras.proxima_feira(agora)
    subtitulo = (f"{formatos.saudacao(agora.hour)} {config.NOME_DA_BANCA} · "
                 f"próxima feira: {formatos.formatar_dia(proxima)}")
    visual.titulo_da_tela(area, "Início", subtitulo)
    for aviso in estado["avisos"]:
        rotulo = visual.mensagem(area)
        visual.mostrar_mensagem(rotulo, aviso, "aviso")
        rotulo.pack(fill="x", padx=24, pady=(0, 8))
    for defeito in gelo.caixas_com_defeito(estado["caixas"], estado["feiras"]):
        rotulo = visual.mensagem(area)
        visual.mostrar_mensagem(rotulo, defeito["mensagem"], "erro")
        rotulo.pack(fill="x", padx=24, pady=(0, 8))
    desenhar_caixas(area, estado, agora)
    visual.botao(area, "Atualizar", atualizar, tipo="leve").pack(anchor="w", padx=24, pady=(0, 8))
    desenhar_ultima_feira(area, estado)


def desenhar_caixas(area, estado, agora):
    """Busca as leituras e desenha um cartão por caixa, numa grade de 4 colunas."""
    visual.rotulo(area, "Suas caixas", tamanho=18, negrito=True).pack(fill="x", padx=24, pady=(4, 6))
    buscando = visual.rotulo(area, "Buscando as leituras das caixas...", tamanho=14, cor="apagado")
    buscando.pack(fill="x", padx=24)
    area.update()
    grade = customtkinter.CTkFrame(area, fg_color="transparent")
    grade.pack(fill="x", padx=24)
    alguma_com_canal = False
    indice = 0
    for caixa in estado["caixas"]:
        if caixa["canal"] != "":
            alguma_com_canal = True
        leituras, aviso = thingspeak.leituras_da_caixa(caixa, estado["leituras"], agora)
        cartao_da_caixa(grade, thingspeak.situacao_da_caixa(caixa, leituras, aviso, agora), indice)
        indice = indice + 1
    buscando.destroy()
    if alguma_com_canal:
        erro = dados.salvar(estado, "leituras")
        if erro is not None:
            rotulo = visual.mensagem(area)
            visual.mostrar_mensagem(rotulo, erro, "erro")
            rotulo.pack(fill="x", padx=24, pady=(0, 8))


def desenhar_ultima_feira(area, estado):
    """Mostra os quatro números da última feira fechada."""
    if len(estado["feiras"]) == 0:
        visual.rotulo(area, "Ainda não tem feira fechada. Use Fechar a feira.", cor="apagado").pack(fill="x", padx=24)
        return
    ultima = estado["feiras"][-1]
    data = relatorios.data_da_feira(ultima)
    if data is None:
        titulo = "Última feira"
    else:
        titulo = f"Última feira ({formatos.formatar_dia(data)})"
    visual.rotulo(area, titulo, tamanho=18, negrito=True).pack(fill="x", padx=24, pady=(4, 6))
    visual.numeros_da_feira(area, relatorios.resumo_da_feira(ultima)).pack(fill="x", padx=24)
    visual.rotulo(area, "Veja tudo em Relatórios.", tamanho=14, cor="apagado").pack(fill="x", padx=24, pady=(6, 12))


def cartao_da_caixa(grade, situacao, indice):
    """Desenha o cartão de uma caixa na sua posição da grade."""
    cartao = visual.cartao(grade)
    cartao.grid(row=indice // 4, column=indice % 4, padx=(0, 12), pady=(0, 12), sticky="nsew")
    grade.grid_columnconfigure(indice % 4, weight=1, uniform="caixas")
    miolo = visual.miolo_do_cartao(cartao)
    visual.rotulo(miolo, situacao["nome"], tamanho=18, negrito=True).pack(fill="x", pady=(0, 4))
    visual.etiqueta(miolo, situacao["texto"], situacao["cor_texto"], situacao["cor_fundo"]).pack(anchor="w")
    visual.rotulo(miolo, situacao["temperatura"], tamanho=28, negrito=True).pack(fill="x", pady=(6, 0))
    if situacao["detalhe"] != "":
        detalhe = visual.rotulo(miolo, situacao["detalhe"], tamanho=13, cor="apagado")
        detalhe.configure(wraplength=LARGURA_DO_TEXTO)
        detalhe.pack(fill="x")
    if situacao["mensagem"] != "":
        if situacao["tem_sensor"]:
            cor = "aviso"
        else:
            cor = "apagado"
        mensagem = visual.rotulo(miolo, situacao["mensagem"], tamanho=13, cor=cor)
        mensagem.configure(wraplength=LARGURA_DO_TEXTO)
        mensagem.pack(fill="x", pady=(4, 0))


def atualizar():
    """Busca de novo as leituras e redesenha a tela."""
    visual.limpar(contexto["area"])
    montar(contexto["area"], contexto["estado"])
