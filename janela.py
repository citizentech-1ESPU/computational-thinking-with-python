"""Janela principal do painel: o menu lateral e a troca de telas."""
import customtkinter

import config
import dados
import tela_cadastro
import tela_historico
import tela_inicio
import visual
from config import CORES

estado = {}
contexto = {"raiz": None, "area": None, "botoes": {}}


def abrir_inicio():
    """Mostra a tela Início."""
    mostrar_tela("Início")


def abrir_historico():
    """Mostra a tela Histórico da caixa."""
    mostrar_tela("Histórico da caixa")


def abrir_fechamento():
    """Mostra a tela Fechar a feira."""
    mostrar_tela("Fechar a feira")


def abrir_relatorios():
    """Mostra a tela Relatórios."""
    mostrar_tela("Relatórios")


def abrir_gelo():
    """Mostra a tela Gelo da próxima feira."""
    mostrar_tela("Gelo da próxima feira")


def abrir_cadastro():
    """Mostra a tela Caixas e produtos."""
    mostrar_tela("Caixas e produtos")


MENU = (
    ("Início", abrir_inicio),
    ("Histórico da caixa", abrir_historico),
    ("Fechar a feira", abrir_fechamento),
    ("Relatórios", abrir_relatorios),
    ("Gelo da próxima feira", abrir_gelo),
    ("Caixas e produtos", abrir_cadastro),
)


def tela_em_construcao(opcao):
    """Mostra só o título de uma tela que ainda não foi feita."""
    visual.titulo_da_tela(contexto["area"], opcao, "Em construção.")


def destacar_botao(opcao):
    """Pinta o botão da opção escolhida e deixa os outros sem fundo."""
    for texto, botao in contexto["botoes"].items():
        if texto == opcao:
            botao.configure(fg_color=CORES["marca"], text_color="#FFFFFF")
        else:
            botao.configure(fg_color="transparent", text_color=CORES["texto"])


def mostrar_tela(opcao):
    """Troca o conteúdo da área principal pela tela escolhida no menu."""
    visual.limpar(contexto["area"])
    destacar_botao(opcao)
    match opcao:
        case "Início":
            tela_inicio.montar(contexto["area"], estado)
        case "Histórico da caixa":
            tela_historico.montar(contexto["area"], estado)
        case "Fechar a feira":
            tela_em_construcao(opcao)
        case "Relatórios":
            tela_em_construcao(opcao)
        case "Gelo da próxima feira":
            tela_em_construcao(opcao)
        case "Caixas e produtos":
            tela_cadastro.montar(contexto["area"], estado)
        case _:
            visual.titulo_da_tela(contexto["area"], "Opção desconhecida", "Escolha uma opção do menu.")


def criar(pasta=config.PASTA_DADOS):
    """Carrega os dados e monta a janela com o menu e a tela Início, sem começar a rodar."""
    estado.clear()
    estado.update(dados.carregar_tudo(pasta))
    customtkinter.set_appearance_mode("light")
    raiz = customtkinter.CTk()
    raiz.title("Xepa Certa · Painel da banca")
    raiz.geometry("1180x760")
    raiz.minsize(1000, 680)
    raiz.configure(fg_color=CORES["fundo"])
    contexto["raiz"] = raiz
    contexto["botoes"] = {}

    lateral = customtkinter.CTkFrame(raiz, width=230, fg_color=CORES["cartao"], corner_radius=0)
    lateral.pack(side="left", fill="y")
    lateral.pack_propagate(False)
    customtkinter.CTkLabel(lateral, text="Xepa Certa", font=visual.fonte(22, negrito=True, titulo=True),
                           text_color=CORES["marca"], anchor="w").pack(fill="x", padx=18, pady=(22, 0))
    customtkinter.CTkLabel(lateral, text="Painel da banca", font=visual.fonte(13),
                           text_color=CORES["apagado"], anchor="w").pack(fill="x", padx=18, pady=(0, 18))
    for texto, funcao in MENU:
        botao = customtkinter.CTkButton(lateral, text=texto, command=funcao, anchor="w", height=40,
                                        fg_color="transparent", hover_color=CORES["gelo_fundo"],
                                        text_color=CORES["texto"], font=visual.fonte(15, negrito=True))
        botao.pack(fill="x", padx=12, pady=3)
        contexto["botoes"][texto] = botao
    customtkinter.CTkLabel(lateral, text="Time SafeTech · GS FIAP 2026.2", font=visual.fonte(12),
                           text_color=CORES["apagado"]).pack(side="bottom", pady=16)

    area = customtkinter.CTkFrame(raiz, fg_color="transparent")
    area.pack(side="right", fill="both", expand=True)
    contexto["area"] = area
    mostrar_tela("Início")
    return raiz


def abrir():
    """Cria a janela e deixa o painel rodando até a pessoa fechar."""
    raiz = criar()
    raiz.mainloop()
