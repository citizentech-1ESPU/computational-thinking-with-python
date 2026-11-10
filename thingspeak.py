"""Leituras da caixa térmica no ThingSpeak: buscar, interpretar, guardar e resumir."""
import math
from datetime import datetime, timedelta

import config
import formatos
import internet
import regras


def numero_ou_nada(valor):
    """Converte o texto que veio do ThingSpeak em número (None quando não é um número de verdade)."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    if math.isnan(numero) or math.isinf(numero):
        return None
    return numero


def inteiro_ou_nada(numero):
    """Devolve o número como inteiro quando ele não tem casas decimais (senão, do jeito que veio)."""
    if numero is not None and numero == int(numero):
        return int(numero)
    return numero


def leitura_completa(temperatura, acumulado, estado, taxa, restantes):
    """Confere a leitura com a regra do site: faixa do sensor, cinco números, estado de 0 a 4."""
    if not regras.leitura_valida(temperatura):
        return False
    for numero in (acumulado, estado, taxa, restantes):
        if numero is None:
            return False
    if estado not in (0, 1, 2, 3, 4):
        return False
    if acumulado < 0 or restantes < 0:
        return False
    return True


def interpretar_feed(feed):
    """Transforma uma entrada do ThingSpeak numa leitura (None se não for uma entrada de verdade)."""
    if not isinstance(feed, dict) or "created_at" not in feed:
        return None
    try:
        # o Python 3.10 não entende o Z do fim, que quer dizer UTC
        quando = datetime.fromisoformat(str(feed["created_at"]).replace("Z", "+00:00"))
    except ValueError:
        return None
    temperatura = numero_ou_nada(feed.get("field1"))
    acumulado = inteiro_ou_nada(numero_ou_nada(feed.get("field2")))
    estado = inteiro_ou_nada(numero_ou_nada(feed.get("field3")))
    taxa = numero_ou_nada(feed.get("field4"))
    restantes = inteiro_ou_nada(numero_ou_nada(feed.get("field5")))
    return {"quando": quando, "temperatura": temperatura, "acumulado": acumulado, "estado": estado,
            "taxa": taxa, "restantes": restantes,
            "valida": leitura_completa(temperatura, acumulado, estado, taxa, restantes)}


def interpretar_feeds(feeds):
    """Transforma a lista do ThingSpeak em leituras, pulando o que não for entrada de verdade."""
    leituras = []
    for feed in feeds:
        leitura = interpretar_feed(feed)
        if leitura is not None:
            leituras.append(leitura)
    return leituras


def buscar_feeds(canal):
    """Busca as últimas entradas do canal no ThingSpeak. Devolve (feeds, erro)."""
    url = config.URL_THINGSPEAK.format(canal=canal)
    resposta, erro = internet.baixar_json(url, {"results": config.LEITURAS_POR_BUSCA})
    if erro == internet.NAO_ENCONTRADO:
        return [], "Canal do ThingSpeak não encontrado. Confira o número em Caixas e produtos."
    if erro is not None:
        return [], erro
    if not isinstance(resposta, dict) or not isinstance(resposta.get("feeds"), list):
        # canal fechado: o ThingSpeak responde -1
        return [], "O canal do ThingSpeak não está aberto para leitura. Confira se ele é público."
    return resposta["feeds"], None


def leituras_da_caixa(caixa, cache, agora):
    """Busca as leituras da caixa; sem internet, usa as últimas salvas. Devolve (leituras, aviso)."""
    canal = caixa["canal"]
    if canal == "":
        return [], "Sem sensor ligado. Coloque o número do canal em Caixas e produtos."
    feeds, erro = buscar_feeds(canal)
    if erro is None:
        cache[canal] = {"salvo_em": agora.isoformat(), "feeds": feeds}
        return interpretar_feeds(feeds), None
    try:
        salvo = datetime.fromisoformat(cache[canal]["salvo_em"]).astimezone(config.FUSO_SAO_PAULO)
        feeds_salvos = cache[canal]["feeds"]
    except (KeyError, TypeError, ValueError):
        return [], erro
    aviso = (f"{erro} Mostrando as leituras salvas de {formatos.formatar_dia(salvo.date())} "
             f"às {formatos.formatar_hora(salvo)}.")
    return interpretar_feeds(feeds_salvos), aviso


def leitura_antiga(quando, agora):
    """Diz se a última leitura tem mais de 2 minutos (ou se não tem leitura)."""
    if quando is None:
        return True
    return agora - quando > timedelta(minutes=config.LEITURA_ANTIGA_MIN)


def situacao_da_caixa(caixa, leituras, aviso, agora):
    """Junta o que o cartão da caixa mostra: estado, cores, temperatura, tempo fora do frio e avisos."""
    cartao = {"nome": caixa["nome"], "tem_sensor": caixa["canal"] != "", "estado": None, "texto": "Sem sensor",
              "cor_texto": config.CORES["apagado"], "cor_fundo": config.CORES["linha"], "temperatura": "--",
              "detalhe": "", "mensagem": ""}
    if aviso is not None:
        cartao["mensagem"] = aviso
    if not cartao["tem_sensor"]:
        return cartao
    if len(leituras) == 0:
        codigo = 4
    else:
        codigo = regras.estado_da_leitura(leituras[-1])
    nome, texto, apoio, cor_texto, cor_fundo = regras.info_do_estado(codigo)
    cartao["estado"] = codigo
    cartao["texto"] = texto
    cartao["cor_texto"] = cor_texto
    cartao["cor_fundo"] = cor_fundo
    if len(leituras) == 0:
        if aviso is None:
            cartao["mensagem"] = "Ainda não chegou nenhuma leitura desta caixa."
        return cartao
    ultima = leituras[-1]
    if ultima["valida"]:
        cartao["temperatura"] = formatos.formatar_temperatura(ultima["temperatura"])
    if ultima["acumulado"] is not None and ultima["restantes"] is not None:
        cartao["detalhe"] = (f"Fora do frio: {formatos.formatar_duracao(ultima['acumulado'])} · "
                             f"Restam {formatos.formatar_duracao(ultima['restantes'])}")
    if leitura_antiga(ultima["quando"], agora):
        cartao["mensagem"] = (f"Sem leitura recente da caixa (última às {formatos.formatar_hora(ultima['quando'])}). "
                              "Confira a conexão.")
    return cartao


def leituras_do_dia(leituras, data):
    """Separa as leituras de um dia, contando o dia no fuso de São Paulo."""
    do_dia = []
    for leitura in leituras:
        if leitura["quando"].astimezone(config.FUSO_SAO_PAULO).date() == data:
            do_dia.append(leitura)
    return do_dia


def datas_com_leitura(leituras):
    """Lista os dias que têm leitura, do mais novo para o mais antigo."""
    datas = []
    for leitura in leituras:
        data = leitura["quando"].astimezone(config.FUSO_SAO_PAULO).date()
        if data not in datas:
            datas.append(data)
    datas.sort(reverse=True)
    return datas


def resumir_leituras(leituras):
    """Resume as leituras: máxima, mínima, fora do frio, como terminou, aviso de gelo e tempo em cada estado."""
    resumo = {"quantidade": len(leituras), "invalidas": 0, "max_c": None, "min_c": None,
              "acumulado_final": None, "estado_final": 4, "aviso_de_gelo": None,
              "minutos_por_estado": {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}}
    for leitura in leituras:
        if not leitura["valida"]:
            resumo["invalidas"] = resumo["invalidas"] + 1
            continue
        temperatura = leitura["temperatura"]
        if resumo["max_c"] is None or temperatura > resumo["max_c"]:
            resumo["max_c"] = temperatura
        if resumo["min_c"] is None or temperatura < resumo["min_c"]:
            resumo["min_c"] = temperatura
        resumo["acumulado_final"] = leitura["acumulado"]
    for leitura in leituras:
        if regras.estado_da_leitura(leitura) == 1:
            resumo["aviso_de_gelo"] = leitura["quando"]
            break
    if len(leituras) > 0:
        resumo["estado_final"] = regras.estado_da_leitura(leituras[-1])
    for indice in range(len(leituras) - 1):
        intervalo = (leituras[indice + 1]["quando"] - leituras[indice]["quando"]).total_seconds() / 60
        # intervalo maior que 5 minutos é caixa desligada, e não conta para nenhum estado
        if 0 <= intervalo <= 5:
            codigo = regras.estado_da_leitura(leituras[indice])
            resumo["minutos_por_estado"][codigo] = resumo["minutos_por_estado"][codigo] + intervalo
    return resumo
