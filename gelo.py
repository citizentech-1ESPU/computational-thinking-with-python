"""Gelo da próxima feira e caixa com defeito, pelo modelo de gelo da parte de Matemática.

Com M kg de gelo e o ar a T °C, o gelo dura K x M / T minutos. O K de cada caixa sai das feiras anteriores.
"""
import config
import formatos


def temperatura_do_modelo(temperatura_ar):
    """Usa pelo menos 10 °C nas contas, porque o modelo não vale perto de 0 °C."""
    return max(temperatura_ar, config.TEMP_AR_MINIMA_DO_MODELO)


def duracao_do_gelo(linha_caixa):
    """Diz quantos minutos o gelo durou numa feira; se não acabou, conta até as 14h (o lado seguro)."""
    acabou = linha_caixa.get("gelo_acabou")
    if acabou is None:
        # contar só até as 14h dá um K menor do que o de verdade, e por isso a conta pede mais gelo
        acabou = config.FIM_DA_FEIRA
    return formatos.minutos_do_dia(acabou) - formatos.minutos_do_dia(config.HORA_DE_ENCHER_AS_CAIXAS)


def constante_da_feira(gelo_kg, minutos, temperatura_ar):
    """Calcula o K de uma feira: minutos de gelo vezes a temperatura, dividido pelos quilos."""
    return minutos * temperatura_do_modelo(temperatura_ar) / gelo_kg


def minutos_de_gelo(gelo_kg, temperatura_ar, constante):
    """Calcula quantos minutos o gelo dura: K vezes os quilos, dividido pela temperatura."""
    return constante * gelo_kg / temperatura_do_modelo(temperatura_ar)


def perda_por_grau(gelo_kg, temperatura_ar, constante):
    """Calcula quantos minutos de gelo cada grau a mais tira (a derivada do modelo: K x M / T²)."""
    temperatura = temperatura_do_modelo(temperatura_ar)
    return constante * gelo_kg / (temperatura * temperatura)


def minutos_que_a_feira_precisa():
    """Conta os minutos de encher as caixas até o fim da feira, mais a folga."""
    return (formatos.minutos_do_dia(config.FIM_DA_FEIRA) - formatos.minutos_do_dia(config.HORA_DE_ENCHER_AS_CAIXAS)
            + config.MARGEM_DO_GELO_MIN)


def gelo_necessario(minutos, temperatura_ar, constante):
    """Calcula os quilos de gelo para durar os minutos pedidos, subindo de meio em meio quilo."""
    bruto = minutos * temperatura_do_modelo(temperatura_ar) / constante
    quilos = config.PASSO_DO_GELO_KG
    while quilos < bruto:
        quilos = quilos + config.PASSO_DO_GELO_KG
    return quilos


def estimar_constante(feiras, caixa_id):
    """Estima o K de uma caixa pela média das feiras anteriores (sem histórico, usa o K padrão)."""
    soma = 0.0
    quantidade = 0
    for feira in feiras:
        temperatura = feira.get("temperatura_ar_c")
        if temperatura is None:
            continue
        for linha in feira.get("caixas", []):
            gelo_kg = linha.get("gelo_kg")
            if linha.get("caixa_id") == caixa_id and gelo_kg is not None and gelo_kg > 0:
                soma = soma + constante_da_feira(gelo_kg, duracao_do_gelo(linha), temperatura)
                quantidade = quantidade + 1
    if quantidade == 0:
        return config.CONSTANTE_GELO_PADRAO
    return soma / quantidade


def recomendar_gelo(caixas, feiras, temperatura_ar):
    """Diz, para cada caixa, quantos quilos de gelo levar na próxima feira e por quê."""
    precisa = minutos_que_a_feira_precisa()
    encher = formatos.minutos_do_dia(config.HORA_DE_ENCHER_AS_CAIXAS)
    recomendacao = []
    for caixa in caixas:
        constante = estimar_constante(feiras, caixa["id"])
        padrao = caixa["gelo_padrao_kg"]
        quilos = gelo_necessario(precisa, temperatura_ar, constante)
        fim = encher + int(minutos_de_gelo(padrao, temperatura_ar, constante))
        acaba_as = None
        if fim < 24 * 60:
            acaba_as = formatos.hora_do_dia(fim)
        if quilos > padrao:
            mensagem = (f"Leve {formatos.formatar_kg(quilos)} de gelo "
                        f"({formatos.formatar_kg(quilos - padrao)} a mais que o normal).")
            if acaba_as is not None:
                mensagem = (mensagem + f" Com {formatos.formatar_kg(padrao)}, o gelo acaba perto das "
                            f"{formatos.hora_curta(acaba_as)}.")
        elif quilos < padrao:
            mensagem = (f"Dia mais fresco: {formatos.formatar_kg(quilos)} de gelo bastam "
                        f"({formatos.formatar_kg(padrao - quilos)} a menos que o normal).")
        else:
            mensagem = f"Os {formatos.formatar_kg(padrao)} de sempre bastam. O gelo deve durar a feira toda."
        recomendacao.append({"caixa_id": caixa["id"], "nome": caixa["nome"], "gelo_padrao_kg": padrao,
                             "constante": constante, "gelo_kg": quilos, "acaba_as": acaba_as,
                             "perda_por_grau": round(perda_por_grau(padrao, temperatura_ar, constante)),
                             "mensagem": mensagem})
    return recomendacao


def total_de_gelo(recomendacao):
    """Soma o gelo de todas as caixas, para saber quanto comprar."""
    total = 0.0
    for item in recomendacao:
        total = total + item["gelo_kg"]
    return total


def caixas_com_defeito(caixas, feiras):
    """Acha as caixas que perdem o gelo bem mais rápido que as outras em várias das últimas feiras."""
    ultimas = feiras[-config.FEIRAS_PARA_DEFEITO:]
    avisos = []
    for caixa in caixas:
        vezes = 0
        analisadas = 0
        for feira in ultimas:
            temperatura = feira.get("temperatura_ar_c")
            if temperatura is None:
                continue
            da_caixa = None
            das_outras = []
            for linha in feira.get("caixas", []):
                gelo_kg = linha.get("gelo_kg")
                if gelo_kg is None or gelo_kg <= 0:
                    continue
                constante = constante_da_feira(gelo_kg, duracao_do_gelo(linha), temperatura)
                if linha.get("caixa_id") == caixa["id"]:
                    da_caixa = constante
                else:
                    das_outras.append(constante)
            if da_caixa is None or len(das_outras) == 0:
                continue
            analisadas = analisadas + 1
            media = sum(das_outras) / len(das_outras)
            if da_caixa < config.LIMITE_DE_DEFEITO * media:
                vezes = vezes + 1
        if vezes >= config.VEZES_PARA_DEFEITO:
            mensagem = (f"A caixa {caixa['nome']} perde o gelo mais rápido que as outras "
                        f"({vezes} das últimas {analisadas} feiras). Confira a tampa e a borracha.")
            avisos.append({"caixa_id": caixa["id"], "nome": caixa["nome"], "vezes": vezes,
                           "analisadas": analisadas, "mensagem": mensagem})
    return avisos
