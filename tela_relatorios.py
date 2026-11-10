"""Tela "Relatórios": como foi cada feira e cada semana."""
from datetime import timedelta

import customtkinter

import formatos
import graficos
import relatorios
import visual
from config import CORES

campos = {}
contexto = {"area": None, "estado": None, "tipo": "Da feira", "feira": None, "semana": None, "feira_atual": None}


def montar(area, estado):
    """Desenha a tela de relatórios, começando pela feira mais nova."""
    contexto["area"] = area
    contexto["estado"] = estado
    contexto["tipo"] = "Da feira"
    contexto["feira"] = None
    contexto["semana"] = None
    desenhar()


def desenhar():
    """Redesenha a tela com o relatório escolhido."""
    area = contexto["area"]
    visual.limpar(area)
    campos.clear()
    visual.titulo_da_tela(area, "Relatórios", "Como foi cada feira e cada semana.")
    if len(contexto["estado"]["feiras"]) == 0:
        visual.rotulo(area, "Ainda não tem feira fechada. Use Fechar a feira.", cor="apagado").pack(fill="x", padx=24)
        return
    abas = customtkinter.CTkSegmentedButton(area, values=["Da feira", "Da semana"], command=trocar_relatorio,
                                            font=visual.fonte(15, negrito=True), selected_color=CORES["marca"])
    abas.set(contexto["tipo"])
    abas.pack(anchor="w", padx=24, pady=(0, 8))
    corpo = customtkinter.CTkScrollableFrame(area, fg_color="transparent")
    corpo.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    if contexto["tipo"] == "Da feira":
        desenhar_feira(corpo)
    else:
        desenhar_semana(corpo)


def rotulo_da_feira(feira):
    """Escreve o nome da feira na lista, como domingo, 08/11/2026."""
    data = relatorios.data_da_feira(feira)
    if data is None:
        return str(feira.get("data", "feira sem data"))
    return f"{formatos.dia_da_semana(data)}, {formatos.formatar_data(data)}"


def desenhar_feira(pai):
    """Mostra o relatório de uma feira: números, tabelas, frases e o botão do PDF."""
    opcoes = []
    por_rotulo = {}
    for feira in contexto["estado"]["feiras"]:
        rotulo = rotulo_da_feira(feira)
        opcoes.insert(0, rotulo)
        por_rotulo[rotulo] = feira
    escolhida = contexto["feira"]
    if escolhida not in por_rotulo:
        escolhida = opcoes[0]
    feira = por_rotulo[escolhida]
    contexto["feira_atual"] = feira
    linha = customtkinter.CTkFrame(pai, fg_color="transparent")
    linha.pack(fill="x", padx=12, pady=(0, 8))
    menu = customtkinter.CTkOptionMenu(linha, values=opcoes, command=escolher_feira, width=240,
                                       font=visual.fonte(15), fg_color=CORES["marca"], button_color=CORES["marca"])
    menu.set(escolhida)
    menu.pack(side="left")
    visual.botao(linha, "Salvar em PDF", salvar_pdf).pack(side="left", padx=8)
    campos["mensagem"] = visual.mensagem(pai)
    campos["mensagem"].pack(fill="x", padx=12)
    resumo = relatorios.resumo_da_feira(feira)
    visual.numeros_da_feira(pai, resumo).pack(fill="x", padx=12, pady=(4, 8))
    visual.rotulo(pai, "Caixas térmicas", tamanho=17, negrito=True).pack(fill="x", padx=12, pady=(6, 4))
    visual.tabela(pai, relatorios.CABECALHO_CAIXAS, relatorios.linhas_das_caixas(feira)).pack(fill="x", padx=12)
    visual.rotulo(pai, "Mercadoria", tamanho=17, negrito=True).pack(fill="x", padx=12, pady=(10, 4))
    visual.tabela(pai, relatorios.CABECALHO_PRODUTOS, relatorios.linhas_dos_produtos(feira)).pack(fill="x", padx=12)
    visual.rotulo(pai, "Resumo", tamanho=17, negrito=True).pack(fill="x", padx=12, pady=(10, 4))
    for frase in relatorios.frases_da_feira(resumo):
        visual.rotulo(pai, frase).pack(fill="x", padx=12)


def desenhar_semana(pai):
    """Mostra o relatório de uma semana: tabela, totais, comparação e gráfico."""
    feiras = contexto["estado"]["feiras"]
    opcoes = []
    por_rotulo = {}
    for domingo in relatorios.semanas_com_feira(feiras):
        segunda = domingo - timedelta(days=6)
        rotulo = (f"semana de {segunda.day:02d}/{segunda.month:02d} "
                  f"a {domingo.day:02d}/{domingo.month:02d}")
        opcoes.append(rotulo)
        por_rotulo[rotulo] = domingo
    escolhida = contexto["semana"]
    if escolhida not in por_rotulo:
        escolhida = opcoes[0]
    resumo = relatorios.resumo_da_semana(feiras, por_rotulo[escolhida])
    menu = customtkinter.CTkOptionMenu(pai, values=opcoes, command=escolher_semana, width=260,
                                       font=visual.fonte(15), fg_color=CORES["marca"], button_color=CORES["marca"])
    menu.set(escolhida)
    menu.pack(anchor="w", padx=12, pady=(0, 8))
    cabecalho = ("Feira", "Trouxe", "Aproveitado", "Xepa rendeu", "Doado", "Descartado")
    visual.tabela(pai, cabecalho, relatorios.linhas_da_semana(resumo)).pack(fill="x", padx=12)
    visual.rotulo(pai, relatorios.texto_da_semana(resumo["totais"])).pack(fill="x", padx=12, pady=(10, 2))
    visual.rotulo(pai, resumo["comparacao"], negrito=True).pack(fill="x", padx=12, pady=(0, 6))
    grafico = visual.cartao(pai)
    grafico.pack(fill="x", padx=12, pady=6)
    visual.grafico(grafico, graficos.grafico_da_semana(resumo))


def trocar_relatorio(valor):
    """Troca entre o relatório da feira e o da semana."""
    match valor:
        case "Da semana":
            contexto["tipo"] = "Da semana"
        case _:
            contexto["tipo"] = "Da feira"
    desenhar()


def escolher_feira(valor):
    """Mostra o relatório da feira escolhida na lista."""
    contexto["feira"] = valor
    desenhar()


def escolher_semana(valor):
    """Mostra o relatório da semana escolhida na lista."""
    contexto["semana"] = valor
    desenhar()


def salvar_pdf():
    """Salva o relatório da feira mostrada em PDF, na pasta relatorios."""
    feira = contexto["feira_atual"]
    caminho = relatorios.caminho_do_pdf(contexto["estado"]["pasta"], feira["data"])
    erro = relatorios.gerar_pdf_da_feira(feira, caminho)
    if erro is None:
        visual.mostrar_mensagem(campos["mensagem"], f"PDF salvo em {caminho}", "ok")
    else:
        visual.mostrar_mensagem(campos["mensagem"], erro, "erro")
