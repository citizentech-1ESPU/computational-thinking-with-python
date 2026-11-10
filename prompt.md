# Uso de IA no painel da banca (Python)

> **Rascunho para revisão:** esta versão descreve o desenvolvimento como pair programming assistido por IA. 

Registro da parceria no desenvolvimento do painel, com as cinco partes pedidas pela FIAP (PDF, pág. 31). Pedro conduziu o trabalho com objetivos, referências, escolhas e pedidos de ajuste. As ferramentas de IA atuaram como parceiras técnicas no planejamento, implementação e revisão. Onde os registros dizem que a IA escreveu código ou testes, essa autoria continua explícita. Revisões pessoais que ainda não foram feitas ficam marcadas como pendentes.

## 1. Ferramentas e finalidades

- **Claude Code** (assistente de programação da Anthropic, usado no terminal, dentro da pasta do projeto): foi a principal parceira de implementação. Ajudou a organizar o plano, escreveu os testes e módulos previstos, analisou os resultados e aplicou ajustes pedidos por Pedro.
- **Codex** (assistente de programação da OpenAI, usado no terminal, dentro da pasta do projeto): ajudou a pesquisar a estrutura do tkinter, pensar a organização visual e buscar referências de projetos relacionados.
- **Como foi o pair programming:** Pedro definiu o objetivo, trouxe ideias, referências e blocos de código, escolheu a interface e aprovou o plano. A IA implementou as tarefas e verificou os resultados registrados abaixo. Pedro direcionou a sequência e pediu mudanças concretas. A revisão manual completa de Pedro ainda está pendente, por isso não afirmo que ele conferiu cada linha ou executou pessoalmente todos os testes.

## 2. Prompts, decisões e direcionamento

Pedidos e escolhas de Pedro Corsini, preservando as palavras registradas:
- 08/11: pediu sugestões de bibliotecas, interface visual e funcionalidades para o painel Python ligado à caixa térmica. As funcionalidades aprovadas entraram no readme.md.
- 09/11: “Vamos iniciar python, vamos ao com o planejamento”. Na decisão sobre interface, escolheu “Só a janela”.
- 09/11: apresentou blocos de código, ideias e referências. A IA organizou esse material num plano de construção. Pedro aprovou o plano por estar de acordo com seus conhecimentos e com o código de referência dele.
- 09/11: pediu para seguir o plano tarefa por tarefa (“manda bala no desenvolvimento dele”).
- 10/11: pediu para vincular o repositório da organização, seguir as regras de commits sem coautoria e conferir os commits antes do envio. Escolheu manter apenas a parte Python no repositório e deixá-lo público.
- 10/11: pediu um ajuste nos cartões das telas Início e Gelo, descrevendo o texto que aparecia cortado e o estado sem leitura.
- 10/11: pediu que o gráfico do histórico mostrasse o período das 3h às 22h.

## 3. Funcionalidades feitas, sugeridas ou modificadas com IA

- **Implementadas pela IA a partir do plano e das decisões de Pedro:** seis telas (Início, Histórico da caixa, Fechar a feira, Relatórios, Gelo da próxima feira, Caixas e produtos), módulos de regra e testes automáticos.
- **Sugestões da IA aprovadas por Pedro:** painel em janela e bibliotecas; relatório PDF para fiscalização; aviso de caixa com defeito; resumo da feira na tela Início; dados de exemplo com uma caixa de tampa ruim; banca com feiras às quintas e domingos; modelo de gelo alinhado à parte de Matemática.
- **Ajustes feitos em parceria:** tabelas do PDF alinhadas à esquerda e com coluna do produto mais larga após conferir a primeira versão; descarte da sobra da caixa na xepa corrigido para respeitar a regra de não voltar à geladeira; PDF ajustado para caracteres não suportados pela fonte; fechamento corrigido para associar as leituras do sensor à data em que foram puxadas; cartões ajustados para não cortar texto e ocultar temperatura quando não há leitura; gráfico ajustado para mostrar das 3h às 22h e interromper a linha quando a caixa fica desligada. Além disso, a encomendação de gelo pela previsão da Open-Meteo;

## 4. Como verificamos, testamos e ajustamos

- **Testes automatizados:** durante a implementação, Pedro Corsini especificou que a IA rodasse os testes antes do código em cada tarefa, executou-os para observar as falhas esperadas e voltou a executá-los depois das mudanças. 
- **Contas e regras:** valores dos testes de exemplo, do gelo e das perdas foram calculados em rascunho e comparados com o programa. As regras seguem os números e mensagens combinados com a caixa e o site.
- **Telas e serviços:** foram registrados testes das telas sem internet, verificações da janela em larguras diferentes, busca no ThingSpeak e consulta à Open-Meteo. O canal ao vivo da caixa do Wokwi foi usado posteriormente para desenhar e conferir o gráfico do histórico.
- **Estilo da disciplina:** o registro informa que o código foi conferido quanto a classes, lambda, compreensões de lista e docstrings; o readme.md aponta onde os conceitos pedidos aparecem.

## 5. Análise crítica

- **Benefícios:** o pair programming permitiu transformar as ideias e decisões de Pedro em um painel com seis telas. O plano dividiu a implementação em partes verificáveis, e a escrita de testes antes do código ajudou a conferir as regras. Os pedidos de ajuste levaram a mudanças concretas nas telas e no gráfico.
- **Limitações:** a implementação dos módulos e dos testes foi feita pela IA, então Pedro ainda precisou estudar o código e fazer sua revisão para conseguir explicar cada parte. A conferência visual dependeu de verificações automatizadas e de imagens; os dados de exemplo são simulados. As bibliotecas de janela, gráfico e PDF vão além do conteúdo da disciplina, e o uso precisa ser confirmado com o professor.
- **Dificuldades:** foi necessário verificar a compatibilidade do CustomTkinter com Python 3.14 e Tcl/Tk 9.0. No início, o canal da caixa no ThingSpeak ainda não existia, deixando o teste ao vivo pendente naquela etapa. Também foi preciso ajustar o PDF para caracteres que a fonte não suportava e corrigir o desenho do gráfico quando havia intervalos sem leitura.

---

## Registro das sessões

Os registros abaixo descrevem o que a IA implementou e as decisões ou pedidos de Pedro que orientaram cada etapa. Os totais de testes em cada tarefa são históricos; o total atual informado no readme.md é 93.

### 08/11 · Planejamento do painel (Claude Code)
- Pedido: sugestões de bibliotecas, interface visual e funcionalidades para o programa em Python ligado à caixa térmica.
- O que a IA fez com o direcionamento de Pedro: Pedro definiu o problema e escolheu as funcionalidades que fariam sentido para a banca; a IA propôs a janela em CustomTkinter e as bibliotecas. As funcionalidades aprovadas foram registradas no readme.md.
- Como conferimos: funcionalidades aprovadas por Pedro e registradas no readme.md.

### 09/11 · Tarefa 1: Ambiente e janela com menu (Claude Code)
- Pedido: “Pode iniciar o desenvolvimento do projeto, seguindo o fluxo de trabalho task by task.” (executar o plano de construção do painel).
- O que a IA fez com o direcionamento de Pedro: Pedro autorizou iniciar pelo plano. A IA preparou o ambiente, conferiu a abertura do CustomTkinter no Python 3.14, e escreveu config.py, visual.py, janela.py, main.py e os testes test_config.py e test_janela.py.
- Como conferimos: 5 testes automáticos passaram; aviso de biblioteca ausente conferido num Python sem as bibliotecas; janela aberta a partir de outra pasta.

### 09/11 · Tarefa 2: Regras da caixa e formatos (Claude Code)
- Pedido: continuar o plano do painel.
- O que a IA fez com o direcionamento de Pedro: a IA escreveu primeiro test_formatos.py e test_regras.py e, depois, formatos.py e regras.py. Pedro já havia aprovado a interface e as regras gerais do plano.
- Como conferimos: 19 testes automáticos passaram.

### 09/11 · Tarefa 3: Dados de exemplo e cadastro (Claude Code)
- Pedido: continuar o plano do painel.
- O que a IA fez com o direcionamento de Pedro: a IA escreveu testes para dados, cadastro e telas e implementou dados.py, cadastro.py e tela_cadastro.py, incluindo JSON, dados simulados, validações e confirmação antes de excluir ou restaurar.
- Como conferimos: 35 testes passaram; fluxos de edição de gelo, exclusão protegida, cadastro, preço inválido e reabertura foram rodados por script.

### 09/11 · Tarefa 4: Leituras da caixa e tela Início (Claude Code)
- Pedido: continuar o plano do painel.
- O que a IA fez com o direcionamento de Pedro: a IA escreveu os testes e implementou internet.py, thingspeak.py e tela_inicio.py. A tela mostra saudação, próxima feira e um cartão por caixa.
- Como conferimos: 48 testes passaram; buscas reais num canal público de exemplo do ThingSpeak e num canal inexistente retornaram os resultados esperados. O teste com o canal do Wokwi ficou pendente até existir o canal.

### 09/11 · Tarefa 5: Histórico da caixa (Claude Code)
- Pedido: continuar o plano do painel.
- O que a IA fez com o direcionamento de Pedro: a IA escreveu testes para resumo, fuso de São Paulo, gráfico e tela; ampliou thingspeak.py; e implementou graficos.py e tela_historico.py.
- Como conferimos: 55 testes passaram. Naquela etapa, o teste com o Wokwi ainda estava pendente.

### 09/11 · Tarefa 6: Fechar a feira (Claude Code)
- Pedido: continuar o plano do painel.
- O que a IA fez com o direcionamento de Pedro: a IA escreveu os testes e implementou clima.py, fechamento.py e tela_fechamento.py, com consulta de previsão, validações do fechamento e opção para puxar dados da caixa.
- Como conferimos: 66 testes passaram; erros de formulário foram verificados por script; consulta real da previsão retornou 15,8 °C naquele dia.

### 09/11 · Tarefa 7: Relatórios e PDF (Claude Code)
- Pedido: continuar o plano do painel.
- O que a IA fez com o direcionamento de Pedro: a IA escreveu os testes e implementou relatorios.py, o gráfico semanal, tela_relatorios.py e a seção “Última feira” no Início.
- Como conferimos: 78 testes passaram; PDF de exemplo foi aberto e conferido quanto a acentos, tabelas e frases. O alinhamento das tabelas foi ajustado após olhar a primeira versão.

### 09/11 · Tarefa 8: Gelo da próxima feira e caixa com defeito (Claude Code)
- Pedido: continuar o plano do painel.
- O que a IA fez com o direcionamento de Pedro: a IA escreveu os testes e implementou gelo.py e tela_gelo.py, além do aviso de defeito no Início. A fórmula e os números do teste foram comparados com uma conta de rascunho.
- Como conferimos: 86 testes passaram; tela rodada com a previsão disponível, calculando 21,5 kg de gelo e exibindo o aviso da Pescada.

### 09/11 · Tarefa 9: Revisão, readme.md e prompt.md (Claude Code)
- Pedido: continuar o plano do painel.
- O que a IA fez com o direcionamento de Pedro: a IA conferiu o estilo previsto, abriu as telas, reescreveu o readme.md para a entrega e redigiu o registro de uso de IA.
- Como conferimos: 86 testes passaram; tabela de conceitos do readme.md conferida por busca no código.

### 09/11 · Revisão final do branch (Claude Code)
- Pedido: revisar o código inteiro antes da entrega.
- O que a IA fez com o direcionamento de Pedro: a IA revisou o código juntamente do Pedro e juntos, corrigiram dois problemas identificados, cada um coberto por um teste: caracteres especiais que quebravam o PDF e leituras do sensor associadas à data errada no fechamento. Quatro pontos menores ficaram anotados para possível correção.
- Como conferimos: 88 testes passaram; ZIP gerado novamente e testado numa pasta limpa.

### 10/11 · Repositório próprio no GitHub (Claude Code)
- Pedido: criar e vincular o repositório da organização, seguir as regras de commit sem coautoria e conferir os commits antes do envio.
- O que a IA fez com o direcionamento de Pedro: Pedro escolheu manter somente a parte Python no repositório e torná-lo público. A IA conferiu as regras de Git, criou .gitignore e .gitattributes, atualizou o link no readme.md e separou a pasta com o histórico de commits.
- Como conferimos: 88 testes passaram na cópia separada; ZIP refeito sem .gitignore e .gitattributes.


### 10/11 · Horário do gráfico do histórico (Claude Code)
- Pedido: “no historico da caixa, ajuste as horas do grafico para desde 3h da manha até 22h”.
- O que a IA fez com o direcionamento de Pedro: a IA escreveu testes e ajustou graficos.py para fixar o eixo entre 3h e 22h e interromper a linha quando há mais de cinco minutos entre leituras. A constante correspondente foi registrada em config.py.
- Como conferimos: 93 testes passaram; gráfico desenhado com leituras do canal da caixa nas larguras mínima e padrão da janela e conferido na imagem.
