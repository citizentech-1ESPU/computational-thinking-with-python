"""Tela "Gelo da próxima feira": quanto gelo levar em cada caixa, pela previsão do tempo."""
import customtkinter

import clima
import config
import formatos
import gelo
import regras
import visual

campos = {}
contexto = {"area": None, "estado": None, "resultado": None}


def montar(area, estado):
    """Desenha a tela do gelo e já calcula quando a previsão do tempo chega."""
    contexto["area"] = area
    contexto["estado"] = estado
    campos.clear()
    data = regras.proxima_feira(formatos.agora_em_sao_paulo())
    subtitulo = (f"{formatos.formatar_dia(data)} · conta das {formatos.hora_curta(config.HORA_DE_ENCHER_AS_CAIXAS)} "
                 f"às {formatos.hora_curta(config.FIM_DA_FEIRA)}, com meia hora de folga.")
    visual.titulo_da_tela(area, "Gelo da próxima feira", subtitulo)
    campos["previsao"] = visual.mensagem(area)
    campos["previsao"].pack(fill="x", padx=24, pady=(0, 8))
    linha = customtkinter.CTkFrame(area, fg_color="transparent")
    linha.pack(fill="x", padx=24)
    visual.rotulo(linha, "Temperatura do ar (°C)", tamanho=14, cor="apagado").pack(side="left")
    campos["temperatura"] = visual.campo(linha, "", 100)
    campos["temperatura"].pack(side="left", padx=8)
    visual.botao(linha, "Calcular", calcular).pack(side="left")
    campos["erro_temperatura"] = visual.rotulo(area, "", tamanho=13, cor="perigo")
    campos["erro_temperatura"].pack(fill="x", padx=24)
    resultado = customtkinter.CTkScrollableFrame(area, fg_color="transparent")
    resultado.pack(fill="both", expand=True, padx=12, pady=(4, 12))
    contexto["resultado"] = resultado
    visual.mostrar_mensagem(campos["previsao"], "Buscando a previsão do tempo...", "neutro")
    area.update()
    temperatura, erro = clima.temperatura_da_feira(data)
    if erro is not None:
        visual.mostrar_mensagem(campos["previsao"], erro, "aviso")
        return
    visual.mostrar_mensagem(campos["previsao"], "Previsão para o horário da feira: "
                            f"{formatos.formatar_temperatura(temperatura)} (Open-Meteo)", "neutro")
    campos["temperatura"].insert(0, formatos.formatar_numero(temperatura))
    calcular()


def calcular():
    """Lê a temperatura e mostra um cartão por caixa com o gelo recomendado e o total."""
    temperatura, erro = formatos.ler_numero(campos["temperatura"].get(), -5, 45)
    if erro is not None:
        campos["erro_temperatura"].configure(text=erro)
        return
    campos["erro_temperatura"].configure(text="")
    estado = contexto["estado"]
    resultado = contexto["resultado"]
    visual.limpar(resultado)
    recomendacao = gelo.recomendar_gelo(estado["caixas"], estado["feiras"], temperatura)
    com_defeito = []
    for aviso in gelo.caixas_com_defeito(estado["caixas"], estado["feiras"]):
        com_defeito.append(aviso["caixa_id"])
    grade = customtkinter.CTkFrame(resultado, fg_color="transparent")
    grade.pack(fill="x", padx=12, pady=(4, 8))
    indice = 0
    for item in recomendacao:
        cartao_do_gelo(grade, item, indice, item["caixa_id"] in com_defeito)
        indice = indice + 1
    total = formatos.formatar_kg(gelo.total_de_gelo(recomendacao))
    visual.rotulo(resultado, f"Total para a feira: {total} de gelo.", tamanho=17,
                  negrito=True).pack(fill="x", padx=12, pady=(0, 12))


def cartao_do_gelo(grade, item, indice, tem_defeito):
    """Desenha o cartão de uma caixa: quilos, explicação, perda por grau e o aviso de defeito."""
    cartao = visual.cartao(grade)
    cartao.grid(row=indice // 2, column=indice % 2, padx=(0, 12), pady=(0, 12), sticky="nsew")
    grade.grid_columnconfigure(indice % 2, weight=1, uniform="gelo")
    visual.rotulo(cartao, item["nome"], tamanho=18, negrito=True).pack(fill="x", padx=14, pady=(12, 0))
    visual.rotulo(cartao, formatos.formatar_kg(item["gelo_kg"]), tamanho=28, negrito=True).pack(fill="x", padx=14)
    textos = [(item["mensagem"], 14, "texto"),
              (f"Cada grau a mais tira uns {item['perda_por_grau']} min do gelo desta caixa.", 13, "apagado")]
    if tem_defeito:
        textos.append(("Esta caixa perde gelo rápido: confira a tampa e a borracha.", 13, "perigo"))
    for texto, tamanho, cor in textos:
        rotulo = visual.rotulo(cartao, texto, tamanho=tamanho, cor=cor)
        rotulo.configure(wraplength=380)
        rotulo.pack(fill="x", padx=14, pady=(2, 0))
    customtkinter.CTkFrame(cartao, height=10, fg_color="transparent").pack()
