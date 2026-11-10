"""Painel da banca · Xepa Certa (GS FIAP 2026.2, time SafeTech).

Pedro Passos Corsini (RM573493), Daniel Gomes Torres (RM573436),
Henrique Lira (RM571009) e Pedro Thyago de Araújo Santos (RM570939).
"""
import sys

COMANDO_DE_INSTALACAO = "python -m pip install customtkinter matplotlib requests fpdf2"


def bibliotecas_ok():
    """Confere se as bibliotecas estão instaladas e, se faltar alguma, explica como instalar."""
    try:
        import customtkinter
        import fpdf
        import matplotlib
        import requests
    except ImportError as erro:
        print(f"Falta instalar a biblioteca {erro.name}. Rode no terminal:")
        print(COMANDO_DE_INSTALACAO)
        return False
    return True


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("O painel precisa do Python 3.10 ou mais novo (ele usa match/case).")
    elif bibliotecas_ok():
        import janela
        janela.abrir()
