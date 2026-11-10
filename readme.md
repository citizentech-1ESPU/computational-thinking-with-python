# Painel da banca · Xepa Certa

Programa com janela que o feirante usa no computador, antes e depois da feira: acompanha as caixas térmicas da Xepa Certa, anota o fechamento do dia, gera os relatórios (com PDF para a fiscalização) e calcula o gelo da próxima feira pela previsão do tempo.

GS CitizenTech 2026.2 · Engenharia de Software, 1º ano · Computational Thinking with Python · time SafeTech

Repositório: https://github.com/citizentech-1ESPU/computational-thinking-with-python

| Integrante | RM |
|---|---|
| Pedro Passos Corsini | RM573493 |
| Daniel Gomes Torres | RM573436 |
| Henrique Lira | RM571009 |
| Pedro Thyago de Araújo Santos | RM570939 |

## O problema

Peixe e queijo ficam em caixas térmicas com gelo durante a feira. Em dia quente o gelo acaba antes do esperado, e o feirante só percebe quando o produto já esquentou. Na entrevista que a equipe fez numa feira da Zona Norte de São Paulo, o feirante contou que perde de R$ 100 a R$ 200 por semana com mercadoria estragada, que a fiscalização pergunta como ele conserva o peixe e que a xepa e a doação acontecem sem planejamento.

A Xepa Certa tem três partes: a caixa térmica com sensor (ESP32 no Wokwi), que acende verde, amarelo ou vermelho; o site, onde a xepa vira oferta para fregueses e ONGs; e este painel, que olha para trás (o que aconteceu em cada feira) e para a frente (quanto gelo levar na próxima).

## O que o painel faz

| Tela | O que faz |
|---|---|
| Início | saudação, próxima feira, avisos (como a caixa que perde gelo rápido), um cartão por caixa com o estado ao vivo e os números da última feira |
| Histórico da caixa | as leituras que a caixa mandou ao ThingSpeak: resumo do dia, gráfico da temperatura com a linha dos 5 °C e as últimas leituras, coloridas pelo estado |
| Fechar a feira | formulário do dia: temperatura do ar (busca na previsão ou digita), gelo de cada caixa, hora em que o gelo acabou, como a caixa terminou e, para cada produto, quanto trouxe, vendeu, foi para a xepa, doou e descartou |
| Relatórios | da feira (tabelas, frases do dia e "Salvar em PDF") e da semana (tabela, comparação com a semana anterior e gráfico) |
| Gelo da próxima feira | previsão para o horário da feira e, por caixa, quantos quilos de gelo levar, quando o gelo de sempre acaba e quantos minutos cada grau a mais tira |
| Caixas e produtos | cadastro das caixas e dos produtos, com "Restaurar dados de exemplo" |

## Como rodar

Precisa do Python 3.10 ou mais novo (o programa usa `match/case`). Foi testado com o Python 3.14 no macOS.

No terminal, dentro da pasta do programa:

```bash
python -m pip install customtkinter matplotlib requests fpdf2
python main.py
```

No macOS, se o comando for `python3`, use `python3 -m pip ...` e `python3 main.py`. Se faltar alguma biblioteca, o próprio `main.py` avisa qual é e mostra o comando para instalar.

Testes automáticos (88 testes):

```bash
python -m pip install pytest
python -m pytest
```

## Primeiro uso

- Na primeira vez, o programa cria a pasta `dados/` ao lado do `main.py`, com uma banca de exemplo e 8 feiras simuladas, para todas as telas já terem o que mostrar.
- A caixa Tilápia já vem ligada ao canal público 3571880 do ThingSpeak, que recebe as leituras do circuito da caixa no Wokwi (https://wokwi.com/projects/480215731510086657). As leituras só chegam enquanto a simulação está rodando: abra o link e aperte o play. O número do canal pode ser trocado em **Caixas e produtos**.
- Os PDFs ficam na pasta `relatorios/`, também ao lado do `main.py`.
- **Restaurar dados de exemplo**, em Caixas e produtos, volta tudo para o começo.
- Sem internet, o painel continua funcionando: mostra as últimas leituras salvas e pede a temperatura do ar para calcular o gelo.

## Onde está cada conceito pedido

| Conceito | Onde está (arquivo: função) |
|---|---|
| Menu de opções | `janela.py`: `MENU` (tupla com o texto e a função de cada botão do menu lateral) e `mostrar_tela`, que escolhe a tela com `match/case` |
| Validação das entradas | `formatos.py`: `ler_numero`, `ler_data` e `ler_hora` (aceitam `3,5`, `R$ 39,90` e `11h40`); `cadastro.py`: `validar_caixa` e `validar_produto`; `fechamento.py`: `validar_linha_caixa` e `validar_linha_produto`. O erro aparece ao lado do campo |
| try/except | `dados.py`: `ler_json` (arquivo que não existe ou quebrado) e `gravar_json`; `internet.py`: `baixar_json` (sem conexão, conexão lenta, servidor fora); `formatos.py`: `ler_numero`, `ler_data` e `ler_hora`; `thingspeak.py`: `numero_ou_nada` e `interpretar_feed`; `relatorios.py`: `gerar_pdf_da_feira`; `main.py`: `bibliotecas_ok` |
| if/elif/else | `regras.py`: `decidir_estado` (a prioridade da caixa); `formatos.py`: `saudacao`; `dados.py`: `fracoes_do_dia`; `relatorios.py`: `frases_da_feira` e `resumo_da_semana`; `gelo.py`: `recomendar_gelo` |
| match/case | `regras.py`: `info_do_estado`; `janela.py`: `mostrar_tela`; `visual.py`: `botao` e `mostrar_mensagem`; `fechamento.py`: `validar_linha_produto`; `tela_cadastro.py`: `desenhar`; `tela_relatorios.py`: `trocar_relatorio` |
| while | `regras.py`: `proxima_feira`; `dados.py`: `datas_de_exemplo`; `cadastro.py`: `novo_id`; `gelo.py`: `gelo_necessario` |
| for | `thingspeak.py`: `resumir_leituras`; `relatorios.py`: `resumo_da_feira`; `gelo.py`: `caixas_com_defeito`; e todas as telas |
| Funções com parâmetros e retorno | todos os módulos: 188 funções, cada uma com docstring; as regras têm testes automáticos |
| Listas | as caixas, os produtos e as feiras são listas de dicionários |
| Tuplas | `regras.info_do_estado` devolve uma tupla; `config.DIAS_DE_FEIRA` e `config.CATEGORIAS`; as funções que podem falhar devolvem `(valor, erro)` |
| Dicionários | cada caixa, produto, feira e leitura; `config.CORES`; os campos da tela de fechamento ficam num dicionário com tuplas como chave, como `("produto-1", "trouxe")` |
| JSON (leitura e gravação) | `dados.py`: `ler_json` e `gravar_json`, com os arquivos `caixas.json`, `produtos.json`, `feiras.json` e `leituras.json` |

Boas práticas: um módulo por responsabilidade (as regras não sabem que existe janela, e as telas não abrem arquivo nem chamam a internet direto), constantes compartilhadas em `config.py`, nomes em português, testes com pytest e commits pequenos no Git.

## Regras e contas

- **Estados da caixa** (os mesmos da caixa do Wokwi e do site): acima de 5 °C o relógio corre; com 2 horas fora do frio é **Hora da xepa** (vender ou doar no dia, não volta para a geladeira); com 4 horas é **Descarte**. O aviso **Complete o gelo** aparece quando a caixa vai passar de 5 °C em até 15 minutos.
- **Modelo do gelo** (o mesmo da parte de Matemática): com M kg de gelo e o ar a T °C (média das 6h às 14h), o gelo dura K × M ÷ T minutos. O K de cada caixa sai das feiras anteriores (sem histórico, vale 2.500, calibrado pela entrevista). A derivada, K × M ÷ T², dá quantos minutos de gelo cada grau a mais tira. O painel recomenda gelo para durar das 5h30 às 14h, com meia hora de folga, de meio em meio quilo.
- **Caixa com defeito:** nas últimas 4 feiras, a caixa cujo K fica abaixo de 80% da média das outras em 3 feiras ou mais ganha o aviso "Confira a tampa e a borracha".
- **Preço da xepa sugerido:** 25% menos, arredondado para baixo em 10 centavos (igual ao site).

## Dados

Tudo é fictício ou simulado, sem dados pessoais:
- a Banca Mar Azul e as caixas Tilápia, Queijo, Sardinha e Pescada são inventadas (as mesmas do site);
- as 8 feiras de exemplo foram simuladas pelo modelo do gelo, com temperaturas inventadas; a caixa da Pescada foi simulada com a tampa ruim, para mostrar o aviso de defeito, e as perdas de uma semana quente (cerca de R$ 150) batem com o relato da entrevista;
- as leituras ao vivo vêm do circuito da caixa no Wokwi, pelo canal público do ThingSpeak, com a temperatura mudada à mão na simulação;
- a previsão do tempo é a pública da Open-Meteo, para a Zona Norte de São Paulo.

## Arquivos

```text
main.py              abre o painel: confere o Python e as bibliotecas
config.py            constantes: regras da caixa, banca, gelo, internet, pastas e cores
janela.py            janela, menu lateral e troca de telas
visual.py            peças repetidas das telas: fontes, títulos, cartões, botões, tabelas
regras.py            estados da caixa, preço da xepa e próxima feira
formatos.py          leitura do que se digita; números, horas e datas no jeito da feira
dados.py             JSON: ler, gravar e dados de exemplo
cadastro.py          validar, salvar e excluir caixas e produtos
internet.py          busca na internet com tempo limite e mensagens
thingspeak.py        leituras da caixa: interpretar, guardar e resumir
clima.py             temperatura da feira pela Open-Meteo
fechamento.py        conferir e gravar o fechamento da feira
relatorios.py        números, frases, tabelas e PDF dos relatórios
graficos.py          gráficos da temperatura e da semana
gelo.py              gelo da próxima feira e caixa com defeito
tela_*.py            uma tela para cada opção do menu
testes/              testes automáticos (pytest)
prompt.md            uso de IA
readme.md            este arquivo
```

## Uso de IA

Como a IA foi usada, com os pedidos, o que foi feito e como conferimos, está no `prompt.md`.
