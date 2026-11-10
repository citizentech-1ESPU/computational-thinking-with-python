"""Funções de apoio dos testes."""
import customtkinter


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
