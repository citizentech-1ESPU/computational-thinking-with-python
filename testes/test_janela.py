import janela
from apoio import textos_da_tela

TEXTOS_DO_MENU = ("Início", "Histórico da caixa", "Fechar a feira", "Relatórios",
                  "Gelo da próxima feira", "Caixas e produtos")


def test_menu_tem_as_seis_opcoes():
    textos = []
    for texto, funcao in janela.MENU:
        textos.append(texto)
    assert tuple(textos) == TEXTOS_DO_MENU


def test_cada_opcao_abre_a_sua_tela(tmp_path, sem_internet):
    raiz = janela.criar(str(tmp_path / "dados"))
    raiz.withdraw()
    try:
        for texto, abrir_tela in janela.MENU:
            abrir_tela()
            raiz.update()
            assert texto in textos_da_tela(janela.contexto["area"])
    finally:
        raiz.destroy()
