"""Constantes do painel da banca.

As regras da caixa são as mesmas da caixa do Wokwi e do site (design, seção 6.1).
Mudou alguma, avise o grupo.
"""
import os
from datetime import timedelta, timezone

# Regras da caixa
LIMITE_FRIO_C = 5.0          # acima disso, o relógio corre
XEPA_APOS_MIN = 120          # 2h fora do frio: vender ou doar hoje
DESCARTE_APOS_MIN = 240      # 4h fora do frio: descarte
AVISO_GELO_MIN = 15          # antecedência do aviso de completar o gelo
TEMP_MIN_VALIDA_C = -30.0    # fora desta faixa, a leitura é inválida
TEMP_MAX_VALIDA_C = 60.0
LEITURA_ANTIGA_MIN = 2       # mais de 2 min sem leitura nova: avisar
CAIXA_DESLIGADA_MIN = 5      # mais de 5 min entre duas leituras: a caixa estava desligada
FIM_DA_FEIRA = "14:00"
DESCONTO_XEPA = 0.25         # preço sugerido da xepa: 25% menos
FUSO_SAO_PAULO = timezone(timedelta(hours=-3))   # sem horário de verão desde 2019

# Banca de exemplo (dados fictícios, design 6.6)
NOME_DA_BANCA = "Banca Mar Azul"
DIAS_DE_FEIRA = (3, 6)       # quinta e domingo (segunda é 0)
HORA_DE_ENCHER_AS_CAIXAS = "05:30"
LATITUDE = -23.50            # Zona Norte de São Paulo, perto da feira
LONGITUDE = -46.66
CATEGORIAS = ("peixe", "queijo", "frios", "fruta", "verdura", "outro")

# Gelo (modelo da Matemática: o gelo dura K x kg de gelo / temperatura do ar)
GELO_PADRAO_KG = 5.0
CONSTANTE_GELO_PADRAO = 2500.0   # minutos x °C por kg, calibrado pela entrevista
TEMP_AR_MINIMA_DO_MODELO = 10.0  # abaixo disso, a conta usa 10 °C
MARGEM_DO_GELO_MIN = 30
PASSO_DO_GELO_KG = 0.5
LIMITE_DE_DEFEITO = 0.8          # caixa com menos de 80% do K das outras
FEIRAS_PARA_DEFEITO = 4
VEZES_PARA_DEFEITO = 3

# Internet
CANAL_THINGSPEAK_CAIXA_1 = "3571880"    # canal público "Xepa Certa · Caixa 1", do circuito no Wokwi (design 6.4)
URL_THINGSPEAK = "https://api.thingspeak.com/channels/{canal}/feeds.json"
LEITURAS_POR_BUSCA = 2000
URL_OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
TEMPO_LIMITE_S = 8

# Pastas: sempre ao lado deste arquivo, para funcionar com dois cliques ou de outra pasta
PASTA_DO_PROGRAMA = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(PASTA_DO_PROGRAMA, "dados")

# Cores do protótipo (design 6.3) e fontes (sem a fonte instalada, o sistema usa a padrão)
CORES = {
    "marca": "#1D4E89",
    "ok": "#15803D", "ok_fundo": "#DCFCE7",
    "aviso": "#8A5A00", "aviso_forte": "#EAB308", "aviso_fundo": "#FEF3C7",
    "perigo": "#B91C1C", "perigo_fundo": "#FEE2E2",
    "gelo": "#075985", "gelo_fundo": "#E0F2FE",
    "fundo": "#F5F3EE", "cartao": "#FFFFFF", "texto": "#17181C",
    "apagado": "#5B616E", "linha": "#E2DED5",
}
FONTE_TEXTO = "Atkinson Hyperlegible"
FONTE_TITULO = "Archivo"
