"""Tela "Histórico da caixa": as leituras que a caixa mandou para o ThingSpeak."""
import customtkinter

import dados
import formatos
import graficos
import regras
import thingspeak
import visual
from config import CORES

ULTIMAS = "Últimas leituras"
contexto = {"area": None, "estado": None, "caixa": None, "leituras": [], "aviso": None, "dia": ULTIMAS}


def caixas_com_sensor():
    """Lista as caixas que têm canal do ThingSpeak."""
    com_sensor = []
    for caixa in contexto["estado"]["caixas"]:
        if caixa["canal"] != "":
            com_sensor.append(caixa)
    return com_sensor


def montar(area, estado):
    """Desenha a tela do histórico, começando pela primeira caixa com sensor."""
    contexto["area"] = area
    contexto["estado"] = estado
    contexto["dia"] = ULTIMAS
    com_sensor = caixas_com_sensor()
    if len(com_sensor) == 0:
        visual.titulo_da_tela(area, "Histórico da caixa", "As leituras que a caixa mandou para o ThingSpeak.")
        visual.rotulo(area, "Nenhuma caixa tem sensor ligado. Coloque o número do canal em Caixas e produtos.",
                      cor="apagado").pack(fill="x", padx=24)
        return
    contexto["caixa"] = com_sensor[0]
    buscar()
    desenhar()


def buscar():
    """Busca as leituras da caixa escolhida (sem internet, usa as salvas)."""
    area = contexto["area"]
    buscando = visual.rotulo(area, "Buscando as leituras da caixa...", tamanho=14, cor="apagado")
    buscando.pack(fill="x", padx=24)
    area.update()
    estado = contexto["estado"]
    leituras, aviso = thingspeak.leituras_da_caixa(contexto["caixa"], estado["leituras"],
                                                   formatos.agora_em_sao_paulo())
    contexto["leituras"] = leituras
    contexto["aviso"] = aviso
    erro = dados.salvar(estado, "leituras")
    if erro is not None and aviso is None:
        contexto["aviso"] = erro
    buscando.destroy()


def leituras_escolhidas():
    """Devolve as leituras do dia escolhido (ou todas, em Últimas leituras)."""
    if contexto["dia"] == ULTIMAS:
        return contexto["leituras"]
    for data in thingspeak.datas_com_leitura(contexto["leituras"]):
        if formatos.formatar_dia(data) == contexto["dia"]:
            return thingspeak.leituras_do_dia(contexto["leituras"], data)
    return contexto["leituras"]


def desenhar():
    """Redesenha a tela com a caixa e o dia escolhidos."""
    area = contexto["area"]
    visual.limpar(area)
    visual.titulo_da_tela(area, "Histórico da caixa", "As leituras que a caixa mandou para o ThingSpeak.")
    corpo = customtkinter.CTkScrollableFrame(area, fg_color="transparent")
    corpo.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    desenhar_escolhas(corpo)
    if contexto["aviso"] is not None:
        aviso = visual.mensagem(corpo)
        visual.mostrar_mensagem(aviso, contexto["aviso"], "aviso")
        aviso.pack(fill="x", padx=12, pady=(0, 8))
    leituras = leituras_escolhidas()
    resumo = thingspeak.resumir_leituras(leituras)
    desenhar_resumo(corpo, resumo)
    grafico = visual.cartao(corpo)
    grafico.pack(fill="x", padx=12, pady=8)
    visual.grafico(grafico, graficos.grafico_temperatura(leituras))
    desenhar_lista(corpo, leituras)


def desenhar_escolhas(pai):
    """Desenha a escolha da caixa, a escolha do dia e o botão Atualizar."""
    linha = customtkinter.CTkFrame(pai, fg_color="transparent")
    linha.pack(fill="x", padx=12, pady=(0, 8))
    nomes = []
    for caixa in caixas_com_sensor():
        nomes.append(caixa["nome"])
    menu_caixa = customtkinter.CTkOptionMenu(linha, values=nomes, command=escolher_caixa, width=200,
                                             font=visual.fonte(15), fg_color=CORES["marca"],
                                             button_color=CORES["marca"])
    menu_caixa.set(contexto["caixa"]["nome"])
    menu_caixa.pack(side="left")
    dias = [ULTIMAS]
    for data in thingspeak.datas_com_leitura(contexto["leituras"]):
        dias.append(formatos.formatar_dia(data))
    menu_dia = customtkinter.CTkOptionMenu(linha, values=dias, command=escolher_dia, width=200,
                                           font=visual.fonte(15), fg_color=CORES["marca"],
                                           button_color=CORES["marca"])
    menu_dia.set(contexto["dia"])
    menu_dia.pack(side="left", padx=8)
    visual.botao(linha, "Atualizar", atualizar, tipo="leve").pack(side="left")


def desenhar_resumo(pai, resumo):
    """Desenha os cartões do resumo e o tempo em cada estado."""
    linha = customtkinter.CTkFrame(pai, fg_color="transparent")
    linha.pack(fill="x", padx=12, pady=(0, 4))
    if resumo["acumulado_final"] is None:
        fora = "--"
    else:
        fora = formatos.formatar_duracao(resumo["acumulado_final"])
    if resumo["aviso_de_gelo"] is None:
        aviso_de_gelo = "não teve"
    else:
        aviso_de_gelo = formatos.formatar_hora(resumo["aviso_de_gelo"])
    visual.numero(linha, "Máxima", formatos.formatar_temperatura(resumo["max_c"])).pack(side="left", padx=(0, 10))
    visual.numero(linha, "Fora do frio", fora).pack(side="left", padx=(0, 10))
    visual.numero(linha, "Aviso de gelo", aviso_de_gelo).pack(side="left", padx=(0, 10))
    terminou = visual.cartao(linha)
    terminou.pack(side="left")
    visual.rotulo(terminou, "Terminou em", tamanho=13, cor="apagado").pack(fill="x", padx=14, pady=(10, 4))
    nome, texto, apoio, cor_texto, cor_fundo = regras.info_do_estado(resumo["estado_final"])
    visual.etiqueta(terminou, texto, cor_texto, cor_fundo).pack(anchor="w", padx=14, pady=(0, 12))
    partes = []
    for codigo in range(5):
        minutos = resumo["minutos_por_estado"][codigo]
        if minutos > 0:
            partes.append(f"{regras.info_do_estado(codigo)[1]} {formatos.formatar_duracao(round(minutos))}")
    if len(partes) == 0:
        texto_dos_estados = "Tempo em cada estado: poucas leituras para contar."
    else:
        texto_dos_estados = "Tempo em cada estado: " + " · ".join(partes)
    visual.rotulo(pai, texto_dos_estados, tamanho=14, cor="apagado").pack(fill="x", padx=12, pady=(6, 0))


def desenhar_lista(pai, leituras):
    """Mostra as últimas 30 leituras, da mais nova para a mais antiga, com a cor do estado."""
    visual.rotulo(pai, "Últimas leituras", tamanho=17, negrito=True).pack(fill="x", padx=12, pady=(8, 4))
    ultimas = leituras[-30:]
    ultimas.reverse()
    for leitura in ultimas:
        nome, texto, apoio, cor_texto, cor_fundo = regras.info_do_estado(regras.estado_da_leitura(leitura))
        if leitura["valida"]:
            temperatura = formatos.formatar_temperatura(leitura["temperatura"])
            fora = formatos.formatar_duracao(leitura["acumulado"]) + " fora do frio"
        else:
            temperatura, fora = "--", "leitura inválida"
        linha = f"{formatos.formatar_hora(leitura['quando'])} · {temperatura} · {fora} · {texto}"
        customtkinter.CTkLabel(pai, text=linha, font=visual.fonte(14), text_color=cor_texto, fg_color=cor_fundo,
                               corner_radius=6, anchor="w").pack(fill="x", padx=12, pady=1)


def escolher_caixa(nome):
    """Troca a caixa mostrada e busca as leituras dela."""
    for caixa in caixas_com_sensor():
        if caixa["nome"] == nome:
            contexto["caixa"] = caixa
    contexto["dia"] = ULTIMAS
    buscar()
    desenhar()


def escolher_dia(valor):
    """Mostra só as leituras do dia escolhido."""
    contexto["dia"] = valor
    desenhar()


def atualizar():
    """Busca de novo as leituras da caixa e redesenha a tela."""
    buscar()
    desenhar()
