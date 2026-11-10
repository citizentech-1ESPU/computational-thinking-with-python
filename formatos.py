"""Leitura do que a pessoa digita e números, horas e datas escritos no jeito da feira."""
from datetime import datetime

from config import FUSO_SAO_PAULO

DIAS_DA_SEMANA = ("segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo")


def agora_em_sao_paulo():
    """Devolve a data e a hora de agora no fuso de São Paulo."""
    return datetime.now(FUSO_SAO_PAULO)


def ler_numero(texto, minimo, maximo, vazio=None):
    """Converte o número digitado (aceita 3,5 e R$ 1.234,56) e confere a faixa. Devolve (valor, erro)."""
    limpo = texto.strip().replace("R$", "").strip()
    if limpo == "":
        if vazio is not None:
            return vazio, None
        return None, "Preencha este campo."
    if "," in limpo:
        # no jeito brasileiro o ponto separa milhar e a vírgula separa os centavos
        limpo = limpo.replace(".", "").replace(",", ".")
    try:
        valor = float(limpo)
    except ValueError:
        return None, "Digite um número, como 3,5."
    if not (minimo <= valor <= maximo):
        return None, f"Use um número entre {formatar_numero(minimo)} e {formatar_numero(maximo)}."
    return valor, None


def ler_data(texto, hoje):
    """Converte a data digitada (dd/mm/aaaa) e confere que não é no futuro. Devolve (data, erro)."""
    limpo = texto.strip()
    if limpo == "":
        return None, "Preencha este campo."
    try:
        data = datetime.strptime(limpo, "%d/%m/%Y").date()
    except ValueError:
        return None, "Use o formato dd/mm/aaaa, como 15/11/2026."
    if data > hoje:
        return None, "A data não pode ser no futuro."
    return data, None


def ler_hora(texto, obrigatoria=True):
    """Converte a hora digitada (11:40 ou 11h40) para o formato HH:MM. Devolve (hora, erro)."""
    limpo = texto.strip().lower().replace("h", ":")
    if limpo == "":
        if obrigatoria:
            return None, "Preencha este campo."
        return None, None
    if limpo.endswith(":"):
        limpo = limpo + "00"
    try:
        hora = datetime.strptime(limpo, "%H:%M")
    except ValueError:
        return None, "Use o formato 11:40 ou 11h40."
    return f"{hora.hour:02d}:{hora.minute:02d}", None


def minutos_do_dia(hhmm):
    """Converte uma hora HH:MM em minutos desde a meia-noite."""
    horas, minutos = hhmm.split(":")
    return int(horas) * 60 + int(minutos)


def hora_do_dia(minutos):
    """Converte minutos desde a meia-noite numa hora HH:MM."""
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def hora_curta(hhmm):
    """Escreve a hora HH:MM no jeito da feira, como 11h40."""
    return hhmm.replace(":", "h")


def formatar_hora(momento):
    """Escreve a hora de um momento no fuso de São Paulo, como 13h50."""
    local = momento.astimezone(FUSO_SAO_PAULO)
    return f"{local.hour:02d}h{local.minute:02d}"


def formatar_data(data):
    """Escreve a data como 15/11/2026."""
    return f"{data.day:02d}/{data.month:02d}/{data.year}"


def dia_da_semana(data):
    """Devolve o nome do dia da semana, como domingo."""
    return DIAS_DA_SEMANA[data.weekday()]


def formatar_dia(data):
    """Escreve o dia como domingo, 15/11."""
    return f"{dia_da_semana(data)}, {data.day:02d}/{data.month:02d}"


def formatar_numero(valor):
    """Escreve um número sem zeros sobrando e com vírgula, como 0,5 ou 30."""
    if valor == 0:
        valor = 0          # evita escrever -0
    return f"{valor:g}".replace(".", ",")


def formatar_reais(valor):
    """Escreve um valor em reais, como R$ 1.234,50."""
    texto = f"{valor:,.2f}"
    # o Python escreve 1,234.50; trocamos vírgula e ponto de lugar passando por um caractere provisório
    texto = texto.replace(",", "_").replace(".", ",").replace("_", ".")
    return "R$ " + texto


def formatar_kg(valor):
    """Escreve um peso com até uma casa, como 2,5 kg."""
    return formatar_numero(round(valor, 1)) + " kg"


def formatar_temperatura(valor):
    """Escreve a temperatura com uma casa, como 4,6 °C (ou -- quando não tem)."""
    if valor is None:
        return "--"
    return f"{valor:.1f}".replace(".", ",") + " °C"


def formatar_duracao(minutos):
    """Escreve uma duração no jeito da feira: 45 min, 1h ou 2h20."""
    minutos = int(minutos)
    if minutos < 0:
        minutos = 0
    if minutos < 60:
        return f"{minutos} min"
    horas = minutos // 60
    resto = minutos % 60
    if resto == 0:
        return f"{horas}h"
    return f"{horas}h{resto:02d}"


def saudacao(hora):
    """Escolhe o cumprimento pela hora do dia."""
    if 5 <= hora < 12:
        return "Bom dia!"
    elif 12 <= hora < 18:
        return "Boa tarde!"
    else:
        return "Boa noite!"
