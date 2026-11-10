"""Leitura e gravação dos arquivos JSON do painel e os dados de exemplo da primeira vez."""
import json
import os
from datetime import date, timedelta

import config
import formatos
import regras

NOMES_DOS_ARQUIVOS = ("caixas", "produtos", "feiras")

# Feiras de exemplo, da mais antiga para a mais nova (as 8 quintas e domingos antes do dia de hoje).
# Temperaturas inventadas. A hora do fim do gelo saiu do modelo de gelo (gelo.py), com
# K = 2500 na Tilápia, 2450 no Queijo, 2600 na Sardinha e 1900 na Pescada (tampa ruim).
TEMPERATURAS_EXEMPLO = (26.0, 23.0, 28.0, 22.0, 27.0, 33.0, 30.0, 31.0)
GELO_ACABOU_EXEMPLO = {
    "caixa-1": ("13:30", None, "12:56", None, "13:12", "11:48", "12:26", "12:13"),
    "caixa-2": ("11:46", "12:36", "11:20", "12:55", "11:32", "10:26", "10:56", "10:46"),
    "caixa-3": ("13:50", None, "13:14", None, "13:31", "12:03", "12:43", "12:29"),
    "caixa-4": ("11:35", "12:23", "11:09", "12:41", "11:21", "10:17", "10:46", "10:36"),
}
TROUXE_EXEMPLO = {"produto-1": 12.0, "produto-2": 6.0, "produto-3": 8.0, "produto-4": 10.0}   # domingo: 25% a mais


def caminho(nome, pasta):
    """Monta o caminho do arquivo JSON de um tipo de dado, como dados/caixas.json."""
    return os.path.join(pasta, nome + ".json")


def ler_json(caminho_do_arquivo, padrao):
    """Lê um arquivo JSON. Devolve (valor, aviso); sem o arquivo, devolve o padrão sem aviso."""
    try:
        with open(caminho_do_arquivo, encoding="utf-8") as arquivo:
            valor = json.load(arquivo)
    except FileNotFoundError:
        return padrao, None
    except (json.JSONDecodeError, UnicodeDecodeError):
        return guardar_copia_do_quebrado(caminho_do_arquivo, padrao)
    if not isinstance(valor, type(padrao)):
        return guardar_copia_do_quebrado(caminho_do_arquivo, padrao)
    return valor, None


def guardar_copia_do_quebrado(caminho_do_arquivo, padrao):
    """Renomeia o arquivo com defeito para .quebrado e devolve o padrão com um aviso."""
    nome = os.path.basename(caminho_do_arquivo)
    try:
        os.replace(caminho_do_arquivo, caminho_do_arquivo + ".quebrado")
    except OSError:
        pass
    return padrao, f"O arquivo {nome} estava com defeito. Guardei uma cópia em {nome}.quebrado e comecei de novo."


def gravar_json(caminho_do_arquivo, valor):
    """Grava o valor num arquivo JSON. Devolve a mensagem de erro, ou None quando deu certo."""
    try:
        os.makedirs(os.path.dirname(caminho_do_arquivo), exist_ok=True)
        with open(caminho_do_arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(valor, arquivo, ensure_ascii=False, indent=2)
    except OSError:
        nome = os.path.basename(caminho_do_arquivo)
        return f"Não deu para salvar {nome}. Confira se a pasta pode ser alterada."
    return None


def datas_de_exemplo(hoje, quantidade=8):
    """Lista as últimas quintas e domingos antes de hoje, da mais antiga para a mais nova."""
    datas = []
    dia = hoje - timedelta(days=1)
    while len(datas) < quantidade:
        if dia.weekday() in config.DIAS_DE_FEIRA:
            datas.insert(0, dia.isoformat())
        dia = dia - timedelta(days=1)
    return datas


def fracoes_do_dia(temperatura, caixa_ruim):
    """Divide a mercadoria de exemplo entre venda, xepa, doação e descarte, conforme o calor."""
    if caixa_ruim and temperatura >= 28:
        return (0.60, 0.20, 0.10, 0.10)
    elif temperatura >= 30:
        return (0.68, 0.16, 0.08, 0.04)
    elif temperatura >= 26:
        return (0.75, 0.12, 0.06, 0.02)
    else:
        return (0.82, 0.08, 0.05, 0.00)


def caixas_de_exemplo():
    """Cria as 4 caixas da Banca Mar Azul, as mesmas do site."""
    return [
        {"id": "caixa-1", "nome": "Tilápia", "gelo_padrao_kg": 5.0, "canal": config.CANAL_THINGSPEAK_CAIXA_1},
        {"id": "caixa-2", "nome": "Queijo", "gelo_padrao_kg": 4.0, "canal": ""},
        {"id": "caixa-3", "nome": "Sardinha", "gelo_padrao_kg": 5.0, "canal": ""},
        {"id": "caixa-4", "nome": "Pescada", "gelo_padrao_kg": 5.0, "canal": ""},
    ]


def produtos_de_exemplo():
    """Cria os 4 produtos da banca, com os nomes e preços do site."""
    return [
        {"id": "produto-1", "nome": "Tilápia (filé)", "categoria": "peixe", "preco_kg": 39.9, "caixa_id": "caixa-1"},
        {"id": "produto-2", "nome": "Queijo minas frescal", "categoria": "queijo", "preco_kg": 34.0, "caixa_id": "caixa-2"},
        {"id": "produto-3", "nome": "Sardinha", "categoria": "peixe", "preco_kg": 18.0, "caixa_id": "caixa-3"},
        {"id": "produto-4", "nome": "Pescada (posta)", "categoria": "peixe", "preco_kg": 32.0, "caixa_id": "caixa-4"},
    ]


def linha_de_caixa_de_exemplo(caixa, indice, temperatura):
    """Monta como uma caixa terminou numa feira de exemplo."""
    linha = {"caixa_id": caixa["id"], "nome": caixa["nome"], "gelo_kg": caixa["gelo_padrao_kg"],
             "gelo_acabou": GELO_ACABOU_EXEMPLO[caixa["id"]][indice], "estado_final": 0,
             "max_c": None, "minutos_fora": None, "fonte": "manual"}
    if caixa["id"] == "caixa-4" and temperatura >= 28:
        linha["estado_final"] = 2
    if caixa["id"] == "caixa-1":
        # a Tilápia é a caixa com sensor (o circuito do Wokwi)
        linha["fonte"] = "sensor"
        if temperatura >= 28:
            linha["max_c"], linha["minutos_fora"] = 6.2, 25
        else:
            linha["max_c"], linha["minutos_fora"] = 4.6, 0
    return linha


def linha_de_produto_de_exemplo(produto, temperatura, domingo):
    """Monta quanto de um produto foi vendido, para a xepa, doado e descartado numa feira de exemplo."""
    trouxe = TROUXE_EXEMPLO[produto["id"]]
    if domingo:
        trouxe = trouxe * 1.25
    caixa_ruim = produto["caixa_id"] == "caixa-4"
    vendido, xepa, doado, descartado = fracoes_do_dia(temperatura, caixa_ruim)
    linha = {"produto_id": produto["id"], "nome": produto["nome"], "preco_kg": produto["preco_kg"],
             "preco_xepa_kg": regras.preco_xepa_sugerido(produto["preco_kg"]), "trouxe_kg": trouxe,
             "vendido_kg": round(trouxe * vendido, 1), "xepa_kg": round(trouxe * xepa, 1),
             "doado_kg": round(trouxe * doado, 1)}
    if caixa_ruim and temperatura >= 28:
        # a caixa terminou na xepa e nada volta para o frio: o que sobra vai para o descarte
        linha["descartado_kg"] = round(trouxe - linha["vendido_kg"] - linha["xepa_kg"] - linha["doado_kg"], 1)
    else:
        linha["descartado_kg"] = round(trouxe * descartado, 1)
    return linha


def dados_de_exemplo(hoje):
    """Cria o cadastro e as 8 feiras simuladas que o painel mostra na primeira vez."""
    caixas = caixas_de_exemplo()
    produtos = produtos_de_exemplo()
    datas = datas_de_exemplo(hoje)
    feiras = []
    for indice in range(len(datas)):
        temperatura = TEMPERATURAS_EXEMPLO[indice]
        domingo = date.fromisoformat(datas[indice]).weekday() == 6
        linhas_caixas = []
        for caixa in caixas:
            linhas_caixas.append(linha_de_caixa_de_exemplo(caixa, indice, temperatura))
        linhas_produtos = []
        for produto in produtos:
            linhas_produtos.append(linha_de_produto_de_exemplo(produto, temperatura, domingo))
        feiras.append({"data": datas[indice], "temperatura_ar_c": temperatura,
                       "caixas": linhas_caixas, "produtos": linhas_produtos})
    return {"caixas": caixas, "produtos": produtos, "feiras": feiras}


def carregar_tudo(pasta=config.PASTA_DADOS, hoje=None):
    """Lê os arquivos do painel (na primeira vez, cria os dados de exemplo) e devolve o estado."""
    if hoje is None:
        hoje = formatos.agora_em_sao_paulo().date()
    primeira_vez = True
    for nome in NOMES_DOS_ARQUIVOS:
        if os.path.exists(caminho(nome, pasta)):
            primeira_vez = False
    estado = {"pasta": pasta, "avisos": []}
    if primeira_vez:
        exemplo = dados_de_exemplo(hoje)
        for nome in NOMES_DOS_ARQUIVOS:
            estado[nome] = exemplo[nome]
            erro = gravar_json(caminho(nome, pasta), exemplo[nome])
            if erro is not None:
                estado["avisos"].append(erro)
    else:
        for nome in NOMES_DOS_ARQUIVOS:
            valor, aviso = ler_json(caminho(nome, pasta), [])
            estado[nome] = valor
            if aviso is not None:
                estado["avisos"].append(aviso)
    leituras, aviso = ler_json(caminho("leituras", pasta), {})
    estado["leituras"] = leituras
    if aviso is not None:
        estado["avisos"].append(aviso)
    return estado


def salvar(estado, nome):
    """Grava uma parte do estado (caixas, produtos, feiras ou leituras). Devolve o erro ou None."""
    return gravar_json(caminho(nome, estado["pasta"]), estado[nome])


def restaurar_exemplo(estado, hoje=None):
    """Troca caixas, produtos e feiras pelos de exemplo e grava. Devolve o primeiro erro ou None."""
    if hoje is None:
        hoje = formatos.agora_em_sao_paulo().date()
    exemplo = dados_de_exemplo(hoje)
    primeiro_erro = None
    for nome in NOMES_DOS_ARQUIVOS:
        estado[nome] = exemplo[nome]
        erro = salvar(estado, nome)
        if erro is not None and primeiro_erro is None:
            primeiro_erro = erro
    return primeiro_erro
