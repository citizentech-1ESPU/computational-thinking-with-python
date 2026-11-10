"""Tela "Fechar a feira": o formulário do fim do dia."""
from tkinter import messagebox

import customtkinter

import clima
import dados
import fechamento
import formatos
import regras
import thingspeak
import visual
from config import CORES

ROTULOS = {"trouxe": "Trouxe", "vendido": "Vendido", "xepa": "Xepa", "preco_xepa": "Preço da xepa",
           "doado": "Doado", "descartado": "Descartado", "gelo": "Gelo", "acabou": "Gelo acabou",
           "estado": "Como terminou"}
CAMPOS_DO_PRODUTO = ("trouxe", "vendido", "xepa", "preco_xepa", "doado", "descartado")
ORDEM_DOS_ERROS_DO_PRODUTO = ("trouxe", "vendido", "xepa", "preco_xepa", "doado", "descartado", "soma")

campos = {}
contexto = {"area": None, "estado": None, "do_sensor": {}, "data_do_sensor": None}


def montar(area, estado):
    """Desenha o formulário do fechamento: dia, caixas e mercadoria."""
    contexto["area"] = area
    contexto["estado"] = estado
    contexto["do_sensor"] = {}
    contexto["data_do_sensor"] = None
    campos.clear()
    visual.titulo_da_tela(area, "Fechar a feira",
                          "Anote como foi o dia. Os números vão para os relatórios e para o cálculo do gelo.")
    corpo = customtkinter.CTkScrollableFrame(area, fg_color="transparent")
    corpo.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    desenhar_dia(corpo)
    desenhar_caixas(corpo)
    desenhar_produtos(corpo)
    rodape = customtkinter.CTkFrame(corpo, fg_color="transparent")
    rodape.pack(fill="x", padx=12, pady=(4, 16))
    visual.botao(rodape, "Salvar fechamento", salvar).pack(side="left")
    campos["mensagem"] = visual.mensagem(rodape)
    campos["mensagem"].pack(side="left", padx=12)


def pequeno(pai, texto, cor="perigo"):
    """Cria um rótulo baixinho, para avisos embaixo e ao lado dos campos."""
    return customtkinter.CTkLabel(pai, text=texto, font=visual.fonte(13), text_color=CORES[cor], height=18,
                                  anchor="w", justify="left")


def desenhar_dia(pai):
    """Desenha a data da feira e a temperatura do ar."""
    cartao = visual.cartao(pai)
    cartao.pack(fill="x", padx=12, pady=(0, 10))
    grade = customtkinter.CTkFrame(cartao, fg_color="transparent")
    grade.pack(fill="x", padx=16, pady=12)
    visual.rotulo(grade, "Data da feira", tamanho=14, cor="apagado").grid(row=0, column=0, sticky="w")
    visual.rotulo(grade, "Temperatura do ar (°C, média das 6h às 14h)", tamanho=14,
                  cor="apagado").grid(row=0, column=1, columnspan=2, sticky="w", padx=(16, 0))
    hoje = formatos.agora_em_sao_paulo().date()
    campos["data"] = visual.campo(grade, formatos.formatar_data(hoje), largura=140)
    campos["data"].grid(row=1, column=0, sticky="w")
    campos["temperatura"] = visual.campo(grade, "", largura=140)
    campos["temperatura"].grid(row=1, column=1, sticky="w", padx=(16, 0))
    visual.botao(grade, "Buscar na previsão", buscar_temperatura, tipo="leve").grid(row=1, column=2, padx=(10, 0))
    campos["erro_data"] = pequeno(grade, "")
    campos["erro_data"].grid(row=2, column=0, sticky="w")
    campos["erro_temperatura"] = pequeno(grade, "")
    campos["erro_temperatura"].grid(row=2, column=1, columnspan=2, sticky="w", padx=(16, 0))


def desenhar_caixas(pai):
    """Desenha uma linha por caixa: gelo, hora em que acabou e como terminou."""
    cartao = visual.cartao(pai)
    cartao.pack(fill="x", padx=12, pady=(0, 10))
    cabeca = customtkinter.CTkFrame(cartao, fg_color="transparent")
    cabeca.pack(fill="x", padx=16, pady=(12, 4))
    visual.rotulo(cabeca, "Caixas", tamanho=17, negrito=True).pack(side="left")
    visual.botao(cabeca, "Puxar da caixa", puxar_da_caixa, tipo="leve").pack(side="right")
    grade = customtkinter.CTkFrame(cartao, fg_color="transparent")
    grade.pack(fill="x", padx=16, pady=(0, 12))
    titulos = ("Caixa", "Gelo (kg)", "O gelo acabou às", "Como terminou")
    for coluna in range(len(titulos)):
        pequeno(grade, titulos[coluna], "apagado").grid(row=0, column=coluna, sticky="w", padx=(0, 12))
    linha = 1
    for caixa in contexto["estado"]["caixas"]:
        chave = caixa["id"]
        visual.rotulo(grade, caixa["nome"], negrito=True).grid(row=linha, column=0, sticky="w", padx=(0, 12))
        campos[(chave, "gelo")] = visual.campo(grade, formatos.formatar_numero(caixa["gelo_padrao_kg"]), 90)
        campos[(chave, "gelo")].grid(row=linha, column=1, sticky="w", padx=(0, 12), pady=2)
        campos[(chave, "acabou")] = visual.campo(grade, "", 120)
        campos[(chave, "acabou")].grid(row=linha, column=2, sticky="w", padx=(0, 12), pady=2)
        menu = customtkinter.CTkOptionMenu(grade, values=list(fechamento.ESTADOS_FINAIS), width=170,
                                           font=visual.fonte(14), fg_color=CORES["marca"],
                                           button_color=CORES["marca"])
        menu.set("Venda normal")
        menu.grid(row=linha, column=3, sticky="w", padx=(0, 12), pady=2)
        campos[(chave, "estado")] = menu
        campos[(chave, "sensor")] = pequeno(grade, "", "gelo")
        campos[(chave, "sensor")].grid(row=linha, column=4, sticky="w")
        campos[(chave, "erro")] = pequeno(grade, "")
        campos[(chave, "erro")].grid(row=linha + 1, column=0, columnspan=5, sticky="w")
        linha = linha + 2


def desenhar_produtos(pai):
    """Desenha uma linha por produto: quanto trouxe, vendeu, foi para a xepa, doou e descartou."""
    cartao = visual.cartao(pai)
    cartao.pack(fill="x", padx=12, pady=(0, 10))
    visual.rotulo(cartao, "Mercadoria (kg)", tamanho=17, negrito=True).pack(fill="x", padx=16, pady=(12, 4))
    grade = customtkinter.CTkFrame(cartao, fg_color="transparent")
    grade.pack(fill="x", padx=16, pady=(0, 12))
    titulos = ("Produto", "Trouxe", "Vendido", "Xepa", "Preço da xepa (R$)", "Doado", "Descartado")
    for coluna in range(len(titulos)):
        pequeno(grade, titulos[coluna], "apagado").grid(row=0, column=coluna, sticky="w", padx=(0, 10))
    linha = 1
    for produto in contexto["estado"]["produtos"]:
        chave = produto["id"]
        visual.rotulo(grade, produto["nome"], negrito=True).grid(row=linha, column=0, sticky="w", padx=(0, 10))
        sugerido = regras.preco_xepa_sugerido(produto["preco_kg"])
        coluna = 1
        for campo in CAMPOS_DO_PRODUTO:
            valor = ""
            if campo == "preco_xepa" and sugerido is not None:
                valor = f"{sugerido:.2f}".replace(".", ",")
            campos[(chave, campo)] = visual.campo(grade, valor, 80)
            campos[(chave, campo)].grid(row=linha, column=coluna, sticky="w", padx=(0, 10), pady=2)
            coluna = coluna + 1
        campos[(chave, "erro")] = pequeno(grade, "")
        campos[(chave, "erro")].grid(row=linha + 1, column=0, columnspan=7, sticky="w")
        linha = linha + 2


def escrever(rotulo, texto, cor="perigo"):
    """Escreve um aviso pequeno (texto vazio apaga o aviso)."""
    if texto is None:
        texto = ""
    rotulo.configure(text=texto, text_color=CORES[cor])


def ler_data_escolhida():
    """Lê a data do formulário e mostra o erro, se houver. Devolve a data ou None."""
    data, erro = formatos.ler_data(campos["data"].get(), formatos.agora_em_sao_paulo().date())
    escrever(campos["erro_data"], erro)
    return data


def buscar_temperatura():
    """Busca na previsão do tempo a temperatura do ar no horário da feira."""
    data = ler_data_escolhida()
    if data is None:
        return
    escrever(campos["erro_temperatura"], "Buscando a previsão do tempo...", "apagado")
    contexto["area"].update()
    temperatura, erro = clima.temperatura_da_feira(data)
    if erro is not None:
        escrever(campos["erro_temperatura"], erro, "aviso")
        return
    campos["temperatura"].delete(0, "end")
    campos["temperatura"].insert(0, formatos.formatar_numero(temperatura))
    escrever(campos["erro_temperatura"], "")


def puxar_da_caixa():
    """Preenche as caixas com sensor com o que elas mandaram ao ThingSpeak no dia."""
    data = ler_data_escolhida()
    if data is None:
        return
    estado = contexto["estado"]
    agora = formatos.agora_em_sao_paulo()
    contexto["do_sensor"] = {}
    contexto["data_do_sensor"] = data
    alguma_com_sensor = False
    for caixa in estado["caixas"]:
        if caixa["canal"] == "":
            continue
        alguma_com_sensor = True
        chave = caixa["id"]
        leituras, aviso = thingspeak.leituras_da_caixa(caixa, estado["leituras"], agora)
        sensor = fechamento.dados_do_sensor(leituras, data)
        if sensor is None:
            if aviso is None:
                aviso = "A caixa não mandou leituras nesse dia."
            escrever(campos[(chave, "sensor")], aviso, "aviso")
            continue
        contexto["do_sensor"][chave] = sensor
        campos[(chave, "acabou")].delete(0, "end")
        campos[(chave, "acabou")].insert(0, sensor["acabou"])
        if sensor["estado"] != "":
            campos[(chave, "estado")].set(sensor["estado"])
        if sensor["minutos_fora"] is None:
            fora = "--"
        else:
            fora = formatos.formatar_duracao(sensor["minutos_fora"])
        texto = f"Sensor: máx. {formatos.formatar_temperatura(sensor['max_c'])} · {fora} fora do frio"
        escrever(campos[(chave, "sensor")], texto, "gelo")
    if alguma_com_sensor:
        dados.salvar(estado, "leituras")
    else:
        visual.mostrar_mensagem(campos["mensagem"],
                                "Nenhuma caixa tem sensor ligado. Coloque o número do canal em Caixas e produtos.",
                                "aviso")


def primeiro_erro(erros, ordem):
    """Escolhe o primeiro erro da linha, com o nome do campo na frente (a conferência da soma vai sem nome)."""
    for chave in ordem:
        if chave in erros:
            if chave == "soma":
                return erros[chave]
            return f"{ROTULOS[chave]}: {erros[chave]}"
    return None


def salvar():
    """Confere o formulário inteiro e, se estiver tudo certo, grava a feira no histórico."""
    estado = contexto["estado"]
    tem_erro = False
    data = ler_data_escolhida()
    if data is None:
        tem_erro = True
    temperatura, erro = formatos.ler_numero(campos["temperatura"].get(), -5, 45)
    escrever(campos["erro_temperatura"], erro)
    if erro is not None:
        tem_erro = True
    linhas_caixas = []
    estado_de_cada_caixa = {}
    for caixa in estado["caixas"]:
        chave = caixa["id"]
        textos = {"gelo": campos[(chave, "gelo")].get(), "acabou": campos[(chave, "acabou")].get(),
                  "estado": campos[(chave, "estado")].get()}
        do_sensor = None
        if contexto["data_do_sensor"] == data:
            # o que a caixa mandou só vale para o dia que foi puxado
            do_sensor = contexto["do_sensor"].get(chave)
        linha, erros = fechamento.validar_linha_caixa(caixa, textos, do_sensor)
        escrever(campos[(chave, "erro")], primeiro_erro(erros, ("gelo", "acabou", "estado")))
        if len(erros) > 0:
            tem_erro = True
        linhas_caixas.append(linha)
        estado_de_cada_caixa[chave] = linha["estado_final"]
    linhas_produtos = []
    for produto in estado["produtos"]:
        chave = produto["id"]
        textos = {}
        for campo in CAMPOS_DO_PRODUTO:
            textos[campo] = campos[(chave, campo)].get()
        linha, erros = fechamento.validar_linha_produto(produto, textos, estado_de_cada_caixa.get(produto["caixa_id"]))
        escrever(campos[(chave, "erro")], primeiro_erro(erros, ORDEM_DOS_ERROS_DO_PRODUTO))
        if len(erros) > 0:
            tem_erro = True
        linhas_produtos.append(linha)
    if tem_erro:
        visual.mostrar_mensagem(campos["mensagem"], "Confira os campos em vermelho.", "erro")
        return
    if fechamento.ja_fechada(estado["feiras"], data):
        pergunta = f"Já existe o fechamento de {formatos.formatar_dia(data)}. Quer substituir?"
        if not messagebox.askyesno("Substituir fechamento", pergunta, parent=contexto["area"].winfo_toplevel()):
            return
    feira = fechamento.montar_feira(data, temperatura, linhas_caixas, linhas_produtos)
    estado["feiras"] = fechamento.gravar_fechamento(estado["feiras"], feira)
    erro = dados.salvar(estado, "feiras")
    if erro is None:
        visual.mostrar_mensagem(campos["mensagem"],
                                f"Feira de {formatos.formatar_dia(data)} fechada! O relatório já está em Relatórios.",
                                "ok")
    else:
        visual.mostrar_mensagem(campos["mensagem"], erro, "erro")
