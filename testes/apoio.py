"""Funções de apoio dos testes."""
import customtkinter

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
