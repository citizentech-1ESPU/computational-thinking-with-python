"""Fechamento da feira: conferir o que a pessoa anotou e gravar no histórico."""
import config
import formatos
import regras
import thingspeak

ESTADOS_FINAIS = ("Venda normal", "Complete o gelo", "Hora da xepa", "Descarte")


def dados_do_sensor(leituras, data):
    """Resume o que a caixa com sensor mandou no dia, para preencher o fechamento (None sem leituras)."""
    do_dia = thingspeak.leituras_do_dia(leituras, data)
    if len(do_dia) == 0:
        return None
    resumo = thingspeak.resumir_leituras(do_dia)
    acabou = ""
    if resumo["aviso_de_gelo"] is not None:
        acabou = formatos.formatar_hora(resumo["aviso_de_gelo"])
    estado = ""
    if resumo["estado_final"] in (0, 1, 2, 3):
        estado = regras.info_do_estado(resumo["estado_final"])[1]
    return {"acabou": acabou, "estado": estado, "max_c": resumo["max_c"], "minutos_fora": resumo["acumulado_final"]}


def validar_linha_caixa(caixa, textos, do_sensor):
    """Confere gelo, hora em que o gelo acabou e como a caixa terminou. Devolve (linha, erros)."""
    erros = {}
    gelo, erro = formatos.ler_numero(textos["gelo"], 0.5, 30)
    if erro is not None:
        erros["gelo"] = erro
    acabou, erro = formatos.ler_hora(textos["acabou"], obrigatoria=False)
    encher = config.HORA_DE_ENCHER_AS_CAIXAS
    if erro is not None:
        erros["acabou"] = erro
    elif acabou is not None and formatos.minutos_do_dia(acabou) <= formatos.minutos_do_dia(encher):
        erros["acabou"] = f"O gelo não pode acabar antes de encher a caixa ({formatos.hora_curta(encher)})."
    estado_final = regras.codigo_do_texto(textos["estado"])
    if estado_final not in (0, 1, 2, 3):
        erros["estado"] = "Escolha como a caixa terminou."
    linha = {"caixa_id": caixa["id"], "nome": caixa["nome"], "gelo_kg": gelo, "gelo_acabou": acabou,
             "estado_final": estado_final, "max_c": None, "minutos_fora": None, "fonte": "manual"}
    if do_sensor is not None:
        linha["max_c"] = do_sensor["max_c"]
        linha["minutos_fora"] = do_sensor["minutos_fora"]
        linha["fonte"] = "sensor"
    return linha, erros


def validar_linha_produto(produto, textos, estado_da_caixa):
    """Confere os pesos e o preço da xepa de um produto e a regra da sobra. Devolve (linha, erros)."""
    erros = {}
    trouxe, erro = formatos.ler_numero(textos["trouxe"], 0, 1000)
    if erro is not None:
        erros["trouxe"] = erro
    quantidades = {}
    for chave in ("vendido", "xepa", "doado", "descartado"):
        valor, erro = formatos.ler_numero(textos[chave], 0, 1000, vazio=0.0)
        quantidades[chave] = valor
        if erro is not None:
            erros[chave] = erro
    preco_xepa, erro = formatos.ler_numero(textos["preco_xepa"], 0.01, 1000)
    if erro is not None:
        erros["preco_xepa"] = erro
    elif preco_xepa >= produto["preco_kg"]:
        erros["preco_xepa"] = "O preço da xepa precisa ser menor que o normal."
    linha = {"produto_id": produto["id"], "nome": produto["nome"], "preco_kg": produto["preco_kg"],
             "preco_xepa_kg": preco_xepa, "trouxe_kg": trouxe, "vendido_kg": quantidades["vendido"],
             "xepa_kg": quantidades["xepa"], "doado_kg": quantidades["doado"],
             "descartado_kg": quantidades["descartado"]}
    if len(erros) > 0:
        return linha, erros
    soma = linha["vendido_kg"] + linha["xepa_kg"] + linha["doado_kg"] + linha["descartado_kg"]
    if soma > trouxe + 0.001:
        erros["soma"] = f"A soma passou do que você trouxe ({formatos.formatar_kg(trouxe)})."
    elif sobra_guardada(linha) > 0:
        match estado_da_caixa:
            case 2:
                erros["soma"] = ("A caixa terminou em Hora da xepa: o que sobrou não volta para a geladeira. "
                                 "Lance como xepa, doação ou descarte.")
            case 3:
                erros["soma"] = "A caixa terminou em Descarte: o que sobrou vai para o descarte."
            case _:
                pass
    return linha, erros


def sobra_guardada(linha):
    """Calcula o que voltou para o frio: o que trouxe menos o que saiu da banca."""
    return round(linha["trouxe_kg"] - linha["vendido_kg"] - linha["xepa_kg"] - linha["doado_kg"]
                 - linha["descartado_kg"], 1)


def montar_feira(data, temperatura, linhas_caixas, linhas_produtos):
    """Monta o registro de uma feira para gravar no histórico."""
    return {"data": data.isoformat(), "temperatura_ar_c": temperatura,
            "caixas": linhas_caixas, "produtos": linhas_produtos}


def ja_fechada(feiras, data):
    """Diz se já existe fechamento gravado para a data."""
    for feira in feiras:
        if feira["data"] == data.isoformat():
            return True
    return False


def gravar_fechamento(feiras, feira):
    """Devolve uma lista nova com a feira no lugar certo (substitui a da mesma data)."""
    nova_lista = []
    for atual in feiras:
        if atual["data"] != feira["data"]:
            nova_lista.append(atual)
    posicao = len(nova_lista)
    for indice in range(len(nova_lista)):
        if nova_lista[indice]["data"] > feira["data"]:
            posicao = indice
            break
    nova_lista.insert(posicao, feira)
    return nova_lista
