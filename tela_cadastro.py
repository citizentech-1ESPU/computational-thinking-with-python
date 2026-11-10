"""Tela "Caixas e produtos": o cadastro da banca."""
from tkinter import messagebox

import customtkinter

import cadastro
import config
import dados
import formatos
import visual
from config import CORES

campos = {}
contexto = {"area": None, "estado": None, "aba": "Caixas", "id_atual": None}


def montar(area, estado):
    """Desenha a tela de cadastro dentro da área, começando pela aba Caixas."""
    contexto["area"] = area
    contexto["estado"] = estado
    contexto["aba"] = "Caixas"
    contexto["id_atual"] = None
    desenhar()


def itens_da_aba():
    """Devolve a lista da aba aberta: as caixas ou os produtos."""
    if contexto["aba"] == "Caixas":
        return contexto["estado"]["caixas"]
    return contexto["estado"]["produtos"]


def item_atual():
    """Devolve o item que está sendo editado (ou None, quando é um item novo)."""
    for item in itens_da_aba():
        if item["id"] == contexto["id_atual"]:
            return item
    return None


def desenhar():
    """Redesenha a tela inteira com a aba e o item escolhidos."""
    area = contexto["area"]
    visual.limpar(area)
    campos.clear()
    visual.titulo_da_tela(area, "Caixas e produtos", "Cadastre as caixas térmicas e o que você vende.")
    abas = customtkinter.CTkSegmentedButton(area, values=["Caixas", "Produtos"], command=trocar_aba,
                                            font=visual.fonte(15, negrito=True), selected_color=CORES["marca"])
    abas.set(contexto["aba"])
    abas.pack(anchor="w", padx=24, pady=(0, 12))

    corpo = customtkinter.CTkFrame(area, fg_color="transparent")
    corpo.pack(fill="both", expand=True, padx=24)
    lista = visual.cartao(corpo)
    lista.pack(side="left", fill="both", expand=True, padx=(0, 12))
    formulario = visual.cartao(corpo)
    formulario.pack(side="left", fill="both", expand=True)
    match contexto["aba"]:
        case "Caixas":
            desenhar_lista_de_caixas(lista)
            desenhar_formulario_de_caixa(formulario)
        case _:
            desenhar_lista_de_produtos(lista)
            desenhar_formulario_de_produto(formulario)

    rodape = customtkinter.CTkFrame(area, fg_color="transparent")
    rodape.pack(fill="x", padx=24, pady=16)
    visual.botao(rodape, "Restaurar dados de exemplo", restaurar, tipo="leve").pack(side="left")


def desenhar_lista_de_caixas(pai):
    """Mostra uma linha para cada caixa cadastrada."""
    visual.rotulo(pai, "Suas caixas", tamanho=17, negrito=True).pack(fill="x", padx=16, pady=(14, 6))
    for caixa in contexto["estado"]["caixas"]:
        if caixa["canal"] == "":
            sensor = "sem sensor"
        else:
            sensor = "canal " + caixa["canal"]
        texto = f"{caixa['nome']} · {formatos.formatar_kg(caixa['gelo_padrao_kg'])} de gelo · {sensor}"
        visual.rotulo(pai, texto).pack(fill="x", padx=16, pady=2)


def desenhar_lista_de_produtos(pai):
    """Mostra uma linha para cada produto cadastrado."""
    visual.rotulo(pai, "Seus produtos", tamanho=17, negrito=True).pack(fill="x", padx=16, pady=(14, 6))
    caixas = contexto["estado"]["caixas"]
    for produto in contexto["estado"]["produtos"]:
        if produto["caixa_id"] == "":
            onde = "fora de caixa"
        else:
            onde = "caixa " + cadastro.nome_da_caixa(caixas, produto["caixa_id"])
        texto = (f"{produto['nome']} · {produto['categoria']} · "
                 f"{formatos.formatar_reais(produto['preco_kg'])} o kg · {onde}")
        visual.rotulo(pai, texto).pack(fill="x", padx=16, pady=2)


def menu_de_edicao(pai, primeira_opcao):
    """Cria o menu "Editar:" com a opção de item novo e os nomes cadastrados."""
    visual.rotulo(pai, "Editar:", tamanho=14, cor="apagado").pack(fill="x", padx=16, pady=(14, 0))
    opcoes = [primeira_opcao]
    for item in itens_da_aba():
        opcoes.append(item["nome"])
    menu = customtkinter.CTkOptionMenu(pai, values=opcoes, command=escolher_item, width=280,
                                       font=visual.fonte(15), fg_color=CORES["marca"],
                                       button_color=CORES["marca"])
    atual = item_atual()
    if atual is None:
        menu.set(primeira_opcao)
    else:
        menu.set(atual["nome"])
    menu.pack(anchor="w", padx=16, pady=(0, 6))


def campo_com_rotulo(pai, nome_do_campo, chave, valor=""):
    """Cria o nome do campo, a caixa de texto e o rótulo de erro, e guarda os dois em campos."""
    visual.rotulo(pai, nome_do_campo, tamanho=14, cor="apagado").pack(fill="x", padx=16, pady=(8, 0))
    campos[chave] = visual.campo(pai, valor, largura=280)
    campos[chave].pack(anchor="w", padx=16)
    campos["erro_" + chave] = visual.rotulo(pai, "", tamanho=13, cor="perigo")
    campos["erro_" + chave].configure(wraplength=380)
    campos["erro_" + chave].pack(fill="x", padx=16)


def lista_com_rotulo(pai, nome_do_campo, chave, opcoes, escolhida):
    """Cria o nome do campo, uma lista de opções e o rótulo de erro, e guarda os dois em campos."""
    visual.rotulo(pai, nome_do_campo, tamanho=14, cor="apagado").pack(fill="x", padx=16, pady=(8, 0))
    campos[chave] = customtkinter.CTkOptionMenu(pai, values=opcoes, width=280, font=visual.fonte(15),
                                                fg_color=CORES["marca"], button_color=CORES["marca"])
    campos[chave].set(escolhida)
    campos[chave].pack(anchor="w", padx=16)
    campos["erro_" + chave] = visual.rotulo(pai, "", tamanho=13, cor="perigo")
    campos["erro_" + chave].pack(fill="x", padx=16)


def botoes_do_formulario(pai):
    """Cria os botões Salvar e Excluir e o rótulo de mensagem do formulário."""
    linha = customtkinter.CTkFrame(pai, fg_color="transparent")
    linha.pack(fill="x", padx=16, pady=(12, 6))
    visual.botao(linha, "Salvar", salvar).pack(side="left")
    botao_excluir = visual.botao(linha, "Excluir", excluir, tipo="perigo")
    if contexto["id_atual"] is None:
        botao_excluir.configure(state="disabled")
    botao_excluir.pack(side="left", padx=8)
    campos["mensagem"] = visual.mensagem(pai)
    campos["mensagem"].configure(wraplength=380)
    campos["mensagem"].pack(fill="x", padx=16, pady=(0, 14))


def desenhar_formulario_de_caixa(pai):
    """Desenha o formulário de caixa, já preenchido quando é para editar."""
    menu_de_edicao(pai, "Nova caixa")
    atual = item_atual()
    if atual is None:
        nome, gelo, canal = "", formatos.formatar_numero(config.GELO_PADRAO_KG), ""
    else:
        nome, gelo, canal = atual["nome"], formatos.formatar_numero(atual["gelo_padrao_kg"]), atual["canal"]
    campo_com_rotulo(pai, "Nome", "nome", nome)
    campo_com_rotulo(pai, "Gelo de sempre (kg)", "gelo", gelo)
    campo_com_rotulo(pai, "Canal do ThingSpeak (opcional)", "canal", canal)
    botoes_do_formulario(pai)


def desenhar_formulario_de_produto(pai):
    """Desenha o formulário de produto, já preenchido quando é para editar."""
    menu_de_edicao(pai, "Novo produto")
    caixas = contexto["estado"]["caixas"]
    nomes_das_caixas = ["Sem caixa"]
    for caixa in caixas:
        nomes_das_caixas.append(caixa["nome"])
    atual = item_atual()
    if atual is None:
        nome, categoria, preco, caixa = "", config.CATEGORIAS[0], "", "Sem caixa"
    else:
        nome, categoria = atual["nome"], atual["categoria"]
        preco = f"{atual['preco_kg']:.2f}".replace(".", ",")
        caixa = cadastro.nome_da_caixa(caixas, atual["caixa_id"])
    campo_com_rotulo(pai, "Nome", "nome", nome)
    lista_com_rotulo(pai, "Categoria", "categoria", list(config.CATEGORIAS), categoria)
    campo_com_rotulo(pai, "Preço do kg (R$)", "preco", preco)
    lista_com_rotulo(pai, "Caixa", "caixa", nomes_das_caixas, caixa)
    botoes_do_formulario(pai)


def trocar_aba(valor):
    """Abre a aba escolhida (Caixas ou Produtos) com o formulário vazio."""
    contexto["aba"] = valor
    contexto["id_atual"] = None
    desenhar()


def escolher_item(valor):
    """Preenche o formulário com o item escolhido no menu "Editar:"."""
    contexto["id_atual"] = None
    for item in itens_da_aba():
        if item["nome"] == valor:
            contexto["id_atual"] = item["id"]
    desenhar()


def salvar():
    """Confere o formulário e, se estiver tudo certo, salva a caixa ou o produto."""
    estado = contexto["estado"]
    match contexto["aba"]:
        case "Caixas":
            textos = {"nome": campos["nome"].get(), "gelo": campos["gelo"].get(), "canal": campos["canal"].get()}
            valores, erros = cadastro.validar_caixa(textos, estado["caixas"], contexto["id_atual"])
            chaves = ("nome", "gelo", "canal")
        case _:
            textos = {"nome": campos["nome"].get(), "categoria": campos["categoria"].get(),
                      "preco": campos["preco"].get(), "caixa": campos["caixa"].get()}
            valores, erros = cadastro.validar_produto(textos, estado["produtos"], estado["caixas"],
                                                      contexto["id_atual"])
            chaves = ("nome", "categoria", "preco", "caixa")
    for chave in chaves:
        campos["erro_" + chave].configure(text=erros.get(chave, ""))
    if len(erros) > 0:
        visual.mostrar_mensagem(campos["mensagem"], "Confira os campos em vermelho.", "erro")
        return
    if contexto["aba"] == "Caixas":
        usados = cadastro.ids_em_uso(estado, "caixa")
        estado["caixas"], salvo = cadastro.salvar_caixa(estado["caixas"], valores, contexto["id_atual"], usados)
        erro = dados.salvar(estado, "caixas")
        texto_ok = "Caixa salva!"
    else:
        usados = cadastro.ids_em_uso(estado, "produto")
        estado["produtos"], salvo = cadastro.salvar_produto(estado["produtos"], valores, contexto["id_atual"], usados)
        erro = dados.salvar(estado, "produtos")
        texto_ok = "Produto salvo!"
    contexto["id_atual"] = salvo["id"]
    desenhar()
    if erro is None:
        visual.mostrar_mensagem(campos["mensagem"], texto_ok, "ok")
    else:
        visual.mostrar_mensagem(campos["mensagem"], erro, "erro")


def excluir():
    """Exclui a caixa ou o produto escolhido, depois de confirmar com a pessoa."""
    estado = contexto["estado"]
    atual = item_atual()
    if atual is None:
        return
    if contexto["aba"] == "Caixas":
        nova_lista, erro = cadastro.excluir_caixa(estado["caixas"], estado["produtos"], atual["id"])
        if erro is not None:
            visual.mostrar_mensagem(campos["mensagem"], erro, "erro")
            return
        pergunta = f"Excluir a caixa {atual['nome']}? As feiras antigas continuam no histórico."
        nome, texto_ok = "caixas", "Caixa excluída."
    else:
        nova_lista = cadastro.excluir_produto(estado["produtos"], atual["id"])
        pergunta = f"Excluir o produto {atual['nome']}? As feiras antigas continuam no histórico."
        nome, texto_ok = "produtos", "Produto excluído."
    if not messagebox.askyesno("Excluir", pergunta, parent=contexto["area"].winfo_toplevel()):
        return
    estado[nome] = nova_lista
    erro = dados.salvar(estado, nome)
    contexto["id_atual"] = None
    desenhar()
    if erro is None:
        visual.mostrar_mensagem(campos["mensagem"], texto_ok, "ok")
    else:
        visual.mostrar_mensagem(campos["mensagem"], erro, "erro")


def restaurar():
    """Volta o cadastro e as feiras para os dados de exemplo, depois de confirmar."""
    pergunta = "Isso troca o cadastro e as feiras pelos dados de exemplo. Continuar?"
    if not messagebox.askyesno("Restaurar dados de exemplo", pergunta, parent=contexto["area"].winfo_toplevel()):
        return
    erro = dados.restaurar_exemplo(contexto["estado"])
    contexto["id_atual"] = None
    desenhar()
    if erro is None:
        visual.mostrar_mensagem(campos["mensagem"], "Dados de exemplo restaurados.", "ok")
    else:
        visual.mostrar_mensagem(campos["mensagem"], erro, "erro")
