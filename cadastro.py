"""Regras do cadastro de caixas e produtos: conferir, salvar e excluir."""
import config
import formatos


def novo_id(prefixo, ids_usados):
    """Acha o primeiro número livre para um id novo, como caixa-5."""
    numero = 1
    while f"{prefixo}-{numero}" in ids_usados:
        numero = numero + 1
    return f"{prefixo}-{numero}"


def ids_em_uso(estado, prefixo):
    """Junta os ids do cadastro e os do histórico das feiras, para um id apagado não voltar."""
    if prefixo == "caixa":
        cadastro_atual, parte_da_feira, chave = estado["caixas"], "caixas", "caixa_id"
    else:
        cadastro_atual, parte_da_feira, chave = estado["produtos"], "produtos", "produto_id"
    usados = []
    for item in cadastro_atual:
        usados.append(item["id"])
    for feira in estado["feiras"]:
        for linha in feira.get(parte_da_feira, []):
            if linha.get(chave) not in usados:
                usados.append(linha.get(chave))
    return usados


def validar_nome(texto, itens, id_atual, maximo, repetido):
    """Confere o nome: preenchido, do tamanho certo e sem repetir o de outro item. Devolve (nome, erro)."""
    nome = texto.strip()
    if nome == "":
        return nome, "Preencha este campo."
    if len(nome) < 2 or len(nome) > maximo:
        return nome, f"Use de 2 a {maximo} letras."
    for item in itens:
        if item["id"] != id_atual and item["nome"].strip().lower() == nome.lower():
            return nome, repetido
    return nome, None


def id_da_caixa(caixas, nome):
    """Acha o id da caixa pelo nome escolhido na lista ("Sem caixa" vira vazio). Devolve (id, erro)."""
    if nome == "Sem caixa":
        return "", None
    for caixa in caixas:
        if caixa["nome"] == nome:
            return caixa["id"], None
    return "", "Escolha uma caixa da lista."


def validar_caixa(textos, caixas, id_atual):
    """Confere o formulário de caixa (nome, gelo e canal). Devolve (campos, erros)."""
    erros = {}
    nome, erro = validar_nome(textos["nome"], caixas, id_atual, 30, "Já existe uma caixa com esse nome.")
    if erro is not None:
        erros["nome"] = erro
    gelo, erro = formatos.ler_numero(textos["gelo"], 0.5, 30)
    if erro is not None:
        erros["gelo"] = erro
    canal = textos["canal"].strip()
    if canal != "" and not canal.isdigit():
        erros["canal"] = "O canal tem só números, como 2345678."
    return {"nome": nome, "gelo_padrao_kg": gelo, "canal": canal}, erros


def validar_produto(textos, produtos, caixas, id_atual):
    """Confere o formulário de produto (nome, categoria, preço e caixa). Devolve (campos, erros)."""
    erros = {}
    nome, erro = validar_nome(textos["nome"], produtos, id_atual, 40, "Já existe um produto com esse nome.")
    if erro is not None:
        erros["nome"] = erro
    categoria = textos["categoria"]
    if categoria not in config.CATEGORIAS:
        erros["categoria"] = "Escolha uma categoria da lista."
    preco, erro = formatos.ler_numero(textos["preco"], 0.01, 1000)
    if erro is not None:
        erros["preco"] = erro
    caixa_id, erro = id_da_caixa(caixas, textos["caixa"])
    if erro is not None:
        erros["caixa"] = erro
    return {"nome": nome, "categoria": categoria, "preco_kg": preco, "caixa_id": caixa_id}, erros


def salvar_item(itens, campos, id_atual, prefixo, ids_usados):
    """Devolve uma lista nova com o item criado (sem id_atual) ou trocado (com id_atual), e o item."""
    if id_atual is None:
        id_do_item = novo_id(prefixo, ids_usados)
    else:
        id_do_item = id_atual
    item = {"id": id_do_item}
    item.update(campos)
    nova_lista = []
    trocou = False
    for atual in itens:
        if atual["id"] == id_do_item:
            nova_lista.append(item)
            trocou = True
        else:
            nova_lista.append(atual)
    if not trocou:
        nova_lista.append(item)
    return nova_lista, item


def salvar_caixa(caixas, campos, id_atual, ids_usados):
    """Cria ou troca uma caixa. Devolve (lista nova, caixa salva)."""
    return salvar_item(caixas, campos, id_atual, "caixa", ids_usados)


def salvar_produto(produtos, campos, id_atual, ids_usados):
    """Cria ou troca um produto. Devolve (lista nova, produto salvo)."""
    return salvar_item(produtos, campos, id_atual, "produto", ids_usados)


def nome_da_caixa(caixas, caixa_id):
    """Acha o nome da caixa pelo id (ou "Sem caixa")."""
    for caixa in caixas:
        if caixa["id"] == caixa_id:
            return caixa["nome"]
    return "Sem caixa"


def excluir_caixa(caixas, produtos, caixa_id):
    """Tira a caixa do cadastro, se nenhum produto estiver nela. Devolve (lista nova, erro)."""
    for produto in produtos:
        if produto["caixa_id"] == caixa_id:
            nome = nome_da_caixa(caixas, caixa_id)
            return caixas, f"A caixa {nome} guarda {produto['nome']}. Mude o produto de caixa antes de excluir."
    nova_lista = []
    for caixa in caixas:
        if caixa["id"] != caixa_id:
            nova_lista.append(caixa)
    return nova_lista, None


def excluir_produto(produtos, produto_id):
    """Tira o produto do cadastro (as feiras antigas continuam iguais). Devolve a lista nova."""
    nova_lista = []
    for produto in produtos:
        if produto["id"] != produto_id:
            nova_lista.append(produto)
    return nova_lista
