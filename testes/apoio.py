"""Funções de apoio dos testes."""
import tkinter

import customtkinter

import janela
import thingspeak

# Um dia de leituras que passa por todos os estados, de 20 em 20 segundos.
FEEDS_DE_UM_DIA = [
    {"created_at": "2026-11-15T15:00:00Z", "field1": "3.0", "field2": "0", "field3": "0", "field4": "0.0", "field5": "240"},
    {"created_at": "2026-11-15T15:00:20Z", "field1": "4.6", "field2": "0", "field3": "1", "field4": "2.0", "field5": "240"},
    {"created_at": "2026-11-15T15:00:40Z", "field1": "5.4", "field2": "1", "field3": "1", "field4": "2.4", "field5": "239"},
    {"created_at": "2026-11-15T15:01:00Z", "field1": "7.8", "field2": "140", "field3": "2", "field4": "1.2", "field5": "100"},
    {"created_at": "2026-11-15T15:01:20Z", "field1": "999", "field2": "140", "field3": "4", "field4": "0.0", "field5": "100"},
    {"created_at": "2026-11-15T15:01:40Z", "field1": "3.9", "field2": "250", "field3": "3", "field4": "-1.5", "field5": "0"},
]


def leituras_de_um_dia():
    """As leituras de exemplo já interpretadas."""
    return thingspeak.interpretar_feeds(FEEDS_DE_UM_DIA)


def textos_da_tela(widget):
    """Junta os textos de todos os rótulos e botões dentro de um widget."""
    textos = []
    for filho in widget.winfo_children():
        try:
            textos.append(str(filho.cget("text")))
        except Exception:
            pass
        textos.extend(textos_da_tela(filho))
    return textos


def abrir_area():
    """Cria uma janela escondida com uma área para montar uma tela no teste."""
    raiz = customtkinter.CTk()
    raiz.withdraw()
    area = customtkinter.CTkFrame(raiz)
    area.pack(fill="both", expand=True)
    return raiz, area


def janela_fora_da_tela(pasta, largura, altura=680):
    """Abre a janela do painel de verdade, invisível e fora da tela, para medir o desenho."""
    raiz = janela.criar(pasta)
    raiz.attributes("-alpha", 0.0)
    raiz.geometry(f"{largura}x{altura}+-4000+0")
    raiz.update()
    return raiz


def rotulos_dentro(widget):
    """Junta todos os rótulos (CTkLabel) que estão dentro de um widget."""
    rotulos = []
    for filho in widget.winfo_children():
        if isinstance(filho, customtkinter.CTkLabel):
            rotulos.append(filho)
        else:
            rotulos.extend(rotulos_dentro(filho))
    return rotulos


def problemas_no_cartao(cartao):
    """Procura num cartão o texto cortado e o que fica em cima da borda. Devolve a lista de problemas."""
    problemas = []
    largura, altura = cartao.winfo_width(), cartao.winfo_height()
    borda = cartao.cget("border_width")
    for filho in cartao.winfo_children():
        if isinstance(filho, tkinter.Canvas):
            continue
        direita = filho.winfo_x() + filho.winfo_width()
        baixo = filho.winfo_y() + filho.winfo_height()
        if filho.winfo_x() < borda or filho.winfo_y() < borda or direita > largura - borda or baixo > altura - borda:
            problemas.append(f"em cima da borda de um cartão de {largura}x{altura}: {filho}")
    for rotulo in rotulos_dentro(cartao):
        if rotulo.winfo_reqwidth() > rotulo.winfo_width() + 1:
            problemas.append(f"texto cortado ({rotulo.winfo_reqwidth()} px num espaço de "
                             f"{rotulo.winfo_width()} px): {rotulo.cget('text')!r}")
    return problemas


def problemas_nos_cartoes(widget):
    """Procura problemas de desenho em todos os cartões (quadros com borda) dentro de um widget.

    O seletor de abas (CTkSegmentedButton) também é um quadro com borda, mas os botões dele ficam
    em cima da borda de propósito, então ele fica de fora.
    """
    problemas = []
    for filho in widget.winfo_children():
        if isinstance(filho, customtkinter.CTkSegmentedButton):
            continue
        if isinstance(filho, customtkinter.CTkFrame) and filho.cget("border_width") > 0:
            problemas.extend(problemas_no_cartao(filho))
        else:
            problemas.extend(problemas_nos_cartoes(filho))
    return problemas
