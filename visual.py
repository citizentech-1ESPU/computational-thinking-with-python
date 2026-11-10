"""Peças repetidas das telas do painel, para todas terem a mesma cara."""
import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import CORES, FONTE_TEXTO, FONTE_TITULO


def fonte(tamanho=15, negrito=False, titulo=False):
    """Cria a fonte do painel (só funciona depois que a janela existe)."""
    familia = FONTE_TEXTO
    if titulo:
        familia = FONTE_TITULO
    peso = "normal"
    if negrito:
        peso = "bold"
    return customtkinter.CTkFont(family=familia, size=tamanho, weight=peso)


def limpar(area):
    """Apaga tudo o que está desenhado dentro da área."""
    for filho in area.winfo_children():
        filho.destroy()


def titulo_da_tela(area, titulo, subtitulo):
    """Escreve o título e o subtítulo no alto da tela."""
    customtkinter.CTkLabel(area, text=titulo, font=fonte(26, negrito=True, titulo=True),
                           text_color=CORES["texto"], anchor="w").pack(fill="x", padx=24, pady=(20, 0))
    customtkinter.CTkLabel(area, text=subtitulo, font=fonte(15), text_color=CORES["apagado"],
                           anchor="w").pack(fill="x", padx=24, pady=(2, 12))


def cartao(pai):
    """Cria um cartão branco com borda, para agrupar uma parte da tela."""
    return customtkinter.CTkFrame(pai, fg_color=CORES["cartao"], corner_radius=12,
                                  border_width=1, border_color=CORES["linha"])


def rotulo(pai, texto, tamanho=15, cor="texto", negrito=False):
    """Cria um texto alinhado à esquerda, que quebra a linha quando é comprido."""
    return customtkinter.CTkLabel(pai, text=texto, font=fonte(tamanho, negrito), text_color=CORES[cor],
                                  anchor="w", justify="left", wraplength=900)


def botao(pai, texto, comando, tipo="principal"):
    """Cria um botão com as cores do tipo: principal, perigo ou leve."""
    match tipo:
        case "principal":
            fundo, passando, cor_do_texto, borda = CORES["marca"], "#163D6B", "#FFFFFF", 0
        case "perigo":
            fundo, passando, cor_do_texto, borda = CORES["perigo"], "#8F1515", "#FFFFFF", 0
        case _:
            fundo, passando, cor_do_texto, borda = "transparent", CORES["gelo_fundo"], CORES["marca"], 1
    return customtkinter.CTkButton(pai, text=texto, command=comando, fg_color=fundo, hover_color=passando,
                                   text_color=cor_do_texto, border_width=borda, border_color=CORES["marca"],
                                   height=38, font=fonte(15, negrito=True))


def etiqueta(pai, texto, cor_texto, cor_fundo):
    """Cria a pílula do estado da caixa: o estado vai sempre escrito, além da cor."""
    return customtkinter.CTkLabel(pai, text=texto, text_color=cor_texto, fg_color=cor_fundo, corner_radius=12,
                                  font=fonte(14, negrito=True), padx=10)


def campo(pai, valor="", largura=110):
    """Cria uma caixa de texto com o valor inicial já escrito."""
    entrada = customtkinter.CTkEntry(pai, width=largura, height=34, font=fonte(15))
    if valor != "":
        entrada.insert(0, valor)
    return entrada


def mensagem(pai):
    """Cria um rótulo vazio para os avisos da tela."""
    return customtkinter.CTkLabel(pai, text="", font=fonte(15), corner_radius=8, anchor="w",
                                  justify="left", wraplength=900)


def mostrar_mensagem(rotulo_da_mensagem, texto, tipo):
    """Escreve o aviso com as cores do tipo: ok, erro, aviso ou neutro."""
    match tipo:
        case "ok":
            cor_do_texto, fundo = CORES["ok"], CORES["ok_fundo"]
        case "erro":
            cor_do_texto, fundo = CORES["perigo"], CORES["perigo_fundo"]
        case "aviso":
            cor_do_texto, fundo = CORES["aviso"], CORES["aviso_fundo"]
        case _:
            cor_do_texto, fundo = CORES["texto"], CORES["fundo"]
    if texto == "":
        fundo = "transparent"
    rotulo_da_mensagem.configure(text=texto, text_color=cor_do_texto, fg_color=fundo)


def numero(pai, titulo, valor):
    """Cria um cartão pequeno com um título e um valor em destaque."""
    pequeno = cartao(pai)
    customtkinter.CTkLabel(pequeno, text=titulo, font=fonte(13), text_color=CORES["apagado"],
                           anchor="w").pack(fill="x", padx=14, pady=(10, 0))
    customtkinter.CTkLabel(pequeno, text=valor, font=fonte(24, negrito=True), text_color=CORES["texto"],
                           anchor="w").pack(fill="x", padx=14, pady=(0, 10))
    return pequeno


def grafico(pai, figura):
    """Coloca um gráfico do matplotlib dentro da tela."""
    tela_do_grafico = FigureCanvasTkAgg(figura, master=pai)
    tela_do_grafico.draw()
    widget = tela_do_grafico.get_tk_widget()
    widget.pack(fill="both", expand=True, padx=8, pady=8)
    return widget
