"""Relatórios do painel: números, frases e tabelas da feira e da semana, e o PDF para a fiscalização."""
import os
from datetime import date, timedelta

from fpdf import FPDF

import config
import formatos
import regras

CHAVES_DO_RESUMO = ("trouxe_kg", "vendido_kg", "xepa_kg", "doado_kg", "descartado_kg", "guardado_kg",
                    "receita_normal", "receita_xepa", "valor_doado", "perda")
CABECALHO_CAIXAS = ("Caixa", "Gelo", "Gelo acabou", "Máxima", "Fora do frio", "Como terminou")
CABECALHO_PRODUTOS = ("Produto", "Trouxe", "Vendido", "Xepa", "Doado", "Descartado", "Guardado")


def numero_da_linha(linha, chave):
    """Lê um número da linha; campo que falta (registro antigo ou editado à mão) conta como zero."""
    valor = linha.get(chave)
    if valor is None:
        return 0
    return valor


def numeros_do_produto(linha):
    """Calcula a sobra guardada e quanto cada destino do produto valeu em reais."""
    trouxe = numero_da_linha(linha, "trouxe_kg")
    vendido = numero_da_linha(linha, "vendido_kg")
    xepa = numero_da_linha(linha, "xepa_kg")
    doado = numero_da_linha(linha, "doado_kg")
    descartado = numero_da_linha(linha, "descartado_kg")
    preco = numero_da_linha(linha, "preco_kg")
    preco_xepa = numero_da_linha(linha, "preco_xepa_kg")
    return {"guardado_kg": round(trouxe - vendido - xepa - doado - descartado, 1),
            "receita_normal": round(vendido * preco, 2), "receita_xepa": round(xepa * preco_xepa, 2),
            "valor_doado": round(doado * preco, 2), "perda": round(descartado * preco, 2)}


def completar_resumo(totais):
    """Arredonda os totais e calcula o aproveitamento e o que a xepa e a doação salvaram do lixo."""
    resumo = {}
    for chave in CHAVES_DO_RESUMO:
        if chave.endswith("_kg"):
            resumo[chave] = round(totais[chave], 1)
        else:
            resumo[chave] = round(totais[chave], 2)
    if resumo["trouxe_kg"] > 0:
        aproveitado = (resumo["trouxe_kg"] - resumo["descartado_kg"]) / resumo["trouxe_kg"] * 100
        resumo["aproveitamento"] = round(aproveitado, 1)
    else:
        resumo["aproveitamento"] = None
    resumo["salvo_kg"] = round(resumo["xepa_kg"] + resumo["doado_kg"], 1)
    return resumo


def totais_zerados():
    """Cria o dicionário dos totais, com tudo valendo zero."""
    totais = {}
    for chave in CHAVES_DO_RESUMO:
        totais[chave] = 0
    return totais


def resumo_da_feira(feira):
    """Soma a mercadoria da feira: quilos de cada destino, reais e aproveitamento."""
    totais = totais_zerados()
    for linha in feira.get("produtos", []):
        for chave in ("trouxe_kg", "vendido_kg", "xepa_kg", "doado_kg", "descartado_kg"):
            totais[chave] = totais[chave] + numero_da_linha(linha, chave)
        numeros = numeros_do_produto(linha)
        for chave in numeros:
            totais[chave] = totais[chave] + numeros[chave]
    return completar_resumo(totais)


def somar_resumos(resumos):
    """Junta os resumos de várias feiras num resumo só."""
    totais = totais_zerados()
    for resumo in resumos:
        for chave in CHAVES_DO_RESUMO:
            totais[chave] = totais[chave] + resumo[chave]
    return completar_resumo(totais)


def frases_da_feira(resumo):
    """Escreve as frases do dia: aproveitamento, xepa, doação, o que se salvou e o custo do descarte."""
    if resumo["aproveitamento"] is None:
        return ["Nenhuma mercadoria anotada nesta feira."]
    frases = []
    # int() arredonda para baixo, para nunca prometer 100% quando teve descarte
    aproveitado = int(resumo["aproveitamento"])
    if resumo["descartado_kg"] == 0:
        frases.append(f"{aproveitado}% da mercadoria foi aproveitada: nada foi para o descarte.")
    else:
        frases.append(f"{aproveitado}% da mercadoria foi aproveitada e "
                      f"{formatos.formatar_kg(resumo['descartado_kg'])} foram para o descarte.")
    if resumo["xepa_kg"] > 0:
        frases.append(f"A xepa rendeu {formatos.formatar_reais(resumo['receita_xepa'])}.")
    else:
        frases.append("Nada foi para a xepa.")
    if resumo["doado_kg"] > 0:
        frases.append(f"{formatos.formatar_kg(resumo['doado_kg'])} viraram doação "
                      f"({formatos.formatar_reais(resumo['valor_doado'])} em comida).")
    else:
        frases.append("Nada foi doado desta vez.")
    if resumo["salvo_kg"] > 0:
        frases.append(f"Xepa e doação salvaram {formatos.formatar_kg(resumo['salvo_kg'])} do lixo.")
    if resumo["perda"] > 0:
        frases.append(f"O descarte custou {formatos.formatar_reais(resumo['perda'])}.")
    return frases


def linhas_das_caixas(feira):
    """Monta a tabela das caixas: gelo, hora em que acabou, máxima, tempo fora do frio e como terminou."""
    linhas = []
    for caixa in feira.get("caixas", []):
        if caixa.get("gelo_acabou") is None:
            acabou = "não acabou"
        else:
            acabou = formatos.hora_curta(caixa["gelo_acabou"])
        if caixa.get("minutos_fora") is None:
            fora = "--"
        else:
            fora = formatos.formatar_duracao(caixa["minutos_fora"])
        terminou = regras.info_do_estado(caixa.get("estado_final"))[1]
        linhas.append((caixa.get("nome", ""), formatos.formatar_kg(numero_da_linha(caixa, "gelo_kg")), acabou,
                       formatos.formatar_temperatura(caixa.get("max_c")), fora, terminou))
    return linhas


def linhas_dos_produtos(feira):
    """Monta a tabela da mercadoria: quanto trouxe e para onde foi cada quilo."""
    linhas = []
    for linha in feira.get("produtos", []):
        numeros = numeros_do_produto(linha)
        linhas.append((linha.get("nome", ""),
                       formatos.formatar_kg(numero_da_linha(linha, "trouxe_kg")),
                       formatos.formatar_kg(numero_da_linha(linha, "vendido_kg")),
                       formatos.formatar_kg(numero_da_linha(linha, "xepa_kg")),
                       formatos.formatar_kg(numero_da_linha(linha, "doado_kg")),
                       formatos.formatar_kg(numero_da_linha(linha, "descartado_kg")),
                       formatos.formatar_kg(numeros["guardado_kg"])))
    return linhas


def data_da_feira(feira):
    """Converte a data da feira (None quando ela está estragada no arquivo)."""
    try:
        return date.fromisoformat(feira["data"])
    except (KeyError, TypeError, ValueError):
        return None


def feiras_entre(feiras, inicio, fim):
    """Separa as feiras entre duas datas, contando as duas pontas."""
    escolhidas = []
    for feira in feiras:
        data = data_da_feira(feira)
        if data is not None and inicio <= data <= fim:
            escolhidas.append(feira)
    return escolhidas


def semanas_com_feira(feiras):
    """Lista o domingo de cada semana que tem feira, do mais novo para o mais antigo."""
    domingos = []
    for feira in feiras:
        data = data_da_feira(feira)
        if data is None:
            continue
        domingo = data + timedelta(days=6 - data.weekday())
        if domingo not in domingos:
            domingos.append(domingo)
    domingos.sort(reverse=True)
    return domingos


def resumo_da_semana(feiras, fim):
    """Soma as feiras da semana que termina no domingo `fim` e compara o descarte com a semana anterior."""
    inicio = fim - timedelta(days=6)
    da_semana = feiras_entre(feiras, inicio, fim)
    anteriores = feiras_entre(feiras, inicio - timedelta(days=7), inicio - timedelta(days=1))
    resumos = []
    datas = []
    for feira in da_semana:
        resumos.append(resumo_da_feira(feira))
        datas.append(feira["data"])
    totais = somar_resumos(resumos)
    if len(anteriores) == 0:
        comparacao = "Ainda não dá para comparar com a semana anterior."
    else:
        resumos_anteriores = []
        for feira in anteriores:
            resumos_anteriores.append(resumo_da_feira(feira))
        diferenca = round(totais["descartado_kg"] - somar_resumos(resumos_anteriores)["descartado_kg"], 1)
        if diferenca > 0:
            comparacao = (f"Você descartou {formatos.formatar_kg(diferenca)} a mais que na semana anterior. "
                          "Confira o gelo e as caixas.")
        elif diferenca < 0:
            comparacao = f"Você descartou {formatos.formatar_kg(-diferenca)} a menos que na semana anterior. Boa!"
        else:
            comparacao = "O descarte ficou igual ao da semana anterior."
    return {"inicio": inicio, "fim": fim, "datas": datas, "feiras": da_semana, "totais": totais,
            "comparacao": comparacao}


def linhas_da_semana(resumo_semana):
    """Monta a tabela da semana, uma linha por feira."""
    linhas = []
    for feira in resumo_semana["feiras"]:
        resumo = resumo_da_feira(feira)
        if resumo["aproveitamento"] is None:
            aproveitado = "--"
        else:
            aproveitado = f"{int(resumo['aproveitamento'])}%"
        linhas.append((formatos.formatar_dia(data_da_feira(feira)), formatos.formatar_kg(resumo["trouxe_kg"]),
                       aproveitado, formatos.formatar_reais(resumo["receita_xepa"]),
                       formatos.formatar_kg(resumo["doado_kg"]), formatos.formatar_kg(resumo["descartado_kg"])))
    return linhas


def texto_da_semana(totais):
    """Escreve o resumo da semana numa frase."""
    return (f"Na semana: {formatos.formatar_kg(totais['trouxe_kg'])} na banca, a xepa rendeu "
            f"{formatos.formatar_reais(totais['receita_xepa'])}, {formatos.formatar_kg(totais['doado_kg'])} "
            f"viraram doação e o descarte custou {formatos.formatar_reais(totais['perda'])}.")


def caminho_do_pdf(pasta_dados, data_iso):
    """Monta o caminho do PDF da feira, na pasta relatorios ao lado da pasta dos dados."""
    return os.path.join(os.path.dirname(pasta_dados), "relatorios", f"relatorio-{data_iso}.pdf")


def texto_para_pdf(texto):
    """Troca por ? as letras que a fonte do PDF não tem, como aspas curvas e emoji."""
    return str(texto).encode("latin-1", "replace").decode("latin-1")


def titulo_no_pdf(pdf, texto):
    """Escreve o título de uma parte do relatório."""
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, texto, new_x="LMARGIN", new_y="NEXT")


def tabela_no_pdf(pdf, cabecalho, linhas, larguras):
    """Escreve uma tabela no PDF, com o cabeçalho em negrito e as colunas nas larguras dadas."""
    pdf.set_font("Helvetica", "", 10)
    with pdf.table(line_height=6, text_align="LEFT", col_widths=larguras) as tabela:
        linha_do_pdf = tabela.row()
        for texto in cabecalho:
            linha_do_pdf.cell(texto_para_pdf(texto))
        for linha in linhas:
            linha_do_pdf = tabela.row()
            for texto in linha:
                linha_do_pdf.cell(texto_para_pdf(texto))


def gerar_pdf_da_feira(feira, caminho):
    """Gera o relatório da feira em PDF, para mostrar à fiscalização. Devolve o erro ou None."""
    # a fonte Helvetica só tem os caracteres do Latin-1 (acentos, ° e ·); o resto passa por texto_para_pdf
    data = data_da_feira(feira)
    if data is None:
        dia = feira.get("data", "")
    else:
        dia = f"{formatos.dia_da_semana(data)}, {formatos.formatar_data(data)}"
    temperatura = formatos.formatar_temperatura(feira.get("temperatura_ar_c"))
    try:
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Xepa Certa · Relatório da feira", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, texto_para_pdf(f"{config.NOME_DA_BANCA} · {dia} · ar a {temperatura} (média das 6h às 14h)"),
                 new_x="LMARGIN", new_y="NEXT")
        titulo_no_pdf(pdf, "Caixas térmicas")
        tabela_no_pdf(pdf, CABECALHO_CAIXAS, linhas_das_caixas(feira), (1.2, 0.8, 1, 0.9, 1, 1.4))
        titulo_no_pdf(pdf, "Mercadoria")
        tabela_no_pdf(pdf, CABECALHO_PRODUTOS, linhas_dos_produtos(feira), (2, 1, 1, 1, 1, 1.1, 1))
        titulo_no_pdf(pdf, "Resumo")
        pdf.set_font("Helvetica", "", 11)
        for frase in frases_da_feira(resumo_da_feira(feira)):
            pdf.multi_cell(0, 6, texto_para_pdf(frase), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        pdf.multi_cell(0, 6, "Regras da caixa: acima de 5 °C o relógio corre; 2 horas fora do frio é hora da xepa "
                             "(vender ou doar no dia); 4 horas é descarte.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, "Gerado pelo painel da Xepa Certa. Dados simulados para a GS FIAP 2026.2 (time SafeTech).",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.output(caminho)
    except OSError:
        return "Não deu para salvar o PDF. Se ele estiver aberto em outro programa, feche e tente de novo."
    return None
