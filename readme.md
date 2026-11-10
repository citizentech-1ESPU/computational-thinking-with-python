# Painel da banca · Xepa Certa (Python)

Programa com janela que o feirante usa no computador, antes e depois da feira. É a parte de Computational Thinking with Python da Xepa Certa (GS CitizenTech 2026.2, time SafeTech). Responsável: Pedro Passos Corsini (RM573493).

> Situação: em planejamento. Este arquivo vira o `readme.md` da entrega (o descritivo do projeto) quando o programa estiver pronto.

## O que o painel faz

- Cadastra as caixas térmicas e os produtos da banca, guardando tudo em JSON (funciona sem internet).
- Puxa o histórico do canal do ThingSpeak (a caixa do Wokwi) e mostra cada caixa na cor do estado, com as mesmas regras da caixa e do site: 5 °C, 2h e 4h (seção 6.1 do documento de design).
- Registra o fechamento do dia: quanto foi vendido, para a xepa, doado e descartado, em kg e em reais.
- Gera o relatório do dia (também em PDF, para mostrar à fiscalização) e o da semana.
- Recomenda o gelo da próxima feira, cruzando o histórico com a previsão do tempo da Open-Meteo.
- Avisa quando uma caixa parece ter defeito (esquenta mais rápido que as outras em várias feiras).
- Foto da banca com IA para reconhecer fruta e verdura: só se sobrar tempo.

Bibliotecas previstas: customtkinter, matplotlib, requests e fpdf2 (e pytest nos testes). O PDF pede usar só o que foi visto na disciplina e evitar "bibliotecas externas muito avançadas", então o uso delas será confirmado com o professor. Plano de construção: `doc/planos/06-python-pedro-p.md`.

## O que a FIAP pede (PDF, págs. 29 a 32)

- [ ] Menu de opções com as principais funcionalidades
- [ ] Validação das entradas do usuário
- [ ] Tratamento de exceções com try/except
- [ ] Decisão com if/elif/else e com match/case
- [ ] Repetição com while e com for
- [ ] Funções com parâmetros e retorno
- [ ] Listas, tuplas e dicionários
- [ ] Leitura e gravação de arquivos JSON
- [ ] Boas práticas de programação
- [ ] Boa experiência de uso
- [ ] Solução ligada ao tema da GS, nada genérica

| Critério | Pontos |
|---|---|
| Aderência ao tema da GS | 20 |
| Código: aplicação dos conceitos de programação | 40 |
| Código: boas práticas | 10 |
| Código: interface com o usuário | 10 |
| Arquivos prompt e readme | 20 |

## Entrega

Um único ZIP na tarefa do Teams, com:
- o código em Python (arquivos `.py`);
- `prompt.md`, sobre o uso de IA (já começado nesta pasta);
- `readme.md`, este arquivo, com o descritivo do projeto.

Arquivo em formato diferente do pedido perde 10 pontos. A pág. 31 chama o arquivo de IA de `prompts.md`, e a lista da entrega, na pág. 32, de `prompt.md`; aqui vale o nome da lista da entrega, `prompt.md` (a confirmar com o professor).

## Dados

Tudo fictício ou simulado: caixas e produtos de exemplo, leituras vindas do circuito do Wokwi (com a temperatura ajustada à mão) e a previsão do tempo pública da Open-Meteo.
