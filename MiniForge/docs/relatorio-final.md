# Relatório final do projeto MiniForge

**Disciplina:** Compiladores, 2026.2

**Professora:** Lorena Bezerra

**Integrantes:** Pedro Dutra, Pedro Pignata, Lucas Rocha Dantas e Renato Portilho

**Data:** 13/11/2026

**Projeto:** MiniForge. **Linguagem:** mineirês. **Implementação:** Python 3.10+.

## 1. Resumo

O MiniForge é um compilador didático de uma linguagem própria chamada mineirês.
O trabalho transforma texto em tokens, constrói uma árvore sintática abstrata,
verifica nomes e tipos, gera código de três endereços (TAC) e aplica cinco passes
de otimização até um ponto fixo. A Calculadora Mineira é a aplicação demonstrativa, com fontes escritos nessa
linguagem, agora incluindo leitura pelo teclado e execução explícita. O relatório descreve a implementação e suas evidências,
sem atribuir resultados de execução ao código que apenas foi compilado.

O marco inicial terminava na otimização do código intermediário. Por solicitação
posterior de uma aplicação interativa na própria linguagem, a revisão atual
adicionou entrada, mensagens literais e um executor TAC. A CLI imprime TAC por
padrão e só executa com --executar. Não há bytecode de pilha.

## 2. Objetivos e motivação

O objetivo acadêmico é implementar as responsabilidades de cada fase de um
compilador, com interfaces explícitas e testes. A linguagem pequena permite
acompanhar uma expressão desde o lexema até a instrução intermediária.
O vocabulário regional diferencia a linguagem sem aumentar excessivamente a
gramática. Python implementa o compilador, mas o fonte que ele aceita é mineirês:
`uai (x > 0) { mostra_so(x); }` não é código Python e não é encaminhado a `eval`.

A calculadora demonstra uma aplicação compreensível: recebe dois inteiros e
uma operação no terminal e executa o programa mineirês compilado. Exemplos fixos também mostram seleção e validade. Sua leitura
permite explicar decisões de projeto sem depender de interface gráfica.

## 3. Continuidade e método de desenvolvimento

O projeto começou com estrutura, especificação, gramática e exemplos. O grupo
continuou o mesmo trabalho e produziu a versão completa preservada no ZIP
`MiniForge-v0.6-mineires.zip`. A integração anterior publicou o frontend na tag
`v0.3-semantica`. A versão `v0.5-otimizacao-sem-vm` incorporou TAC e otimização,
com adaptações de dependências e testes para o escopo final solicitado.

O PR #2 foi integrado à `main`, no commit
`749a919c7468a9bc3ffd1502d617b614a02a7054`. A calculadora e este relatório são
complementos posteriores a esse marco. Não representam novas fases do compilador.
O histórico real e os créditos coletivos foram preservados. Os arquivos completos
do ZIP permanecem referência, sem duplicar a implementação integral no repositório.

A metodologia foi comparar requisitos dos slides e contratos do código, integrar
somente fases autorizadas, testar regressões e riscos, medir o TAC gerado e
registrar os limites das conclusões. A matriz detalhada é
[matriz-requisitos.md](matriz-requisitos.md). O roteiro inicial de organização
está na página física 5, identificada como 4/5 da aula 06. TAC está nas páginas
42–46 e otimização nas páginas 52–56 do PDF da professora.

## 4. Linguagem e decisões

| Palavra | Significado | Exemplo |
|---|---|---|
| `le_so` | Entrada inteira | `le_so(x);` |
| `trem` | Declara variável inicializada | `trem x: inteirim = 18;` |
| `inteirim` | Tipo inteiro | `trem y: inteirim = 6;` |
| `booleanim` | Tipo booleano | `trem ok: booleanim = eh_memo;` |
| `eh_memo` | Literal verdadeiro | `ok = eh_memo;` |
| `num_eh` | Literal falso | `ok = num_eh;` |
| `uai` | Condicional | `uai (y != 0) { mostra_so(x / y); }` |
| `sinao` | Alternativa | `uai (ok) { mostra_so(1); } sinao { mostra_so(0); }` |
| `enquanto_tiver` | Repetição | `enquanto_tiver (x > 0) { x = x - 1; }` |
| `mostra_so` | Comando de saída representado no TAC | `mostra_so(x);` |

Os tipos internos são `int` e `bool`; não há coerção implícita entre eles.
A aritmética recebe inteiros, comparações ordenadas produzem booleanos e igualdade
exige tipos iguais. Condições exigem booleanos. A divisão inteira trunca para zero,
inclusive com operandos negativos. Comentários começam em `//`; o fonte é UTF-8.
As chaves são obrigatórias, declarações precisam de inicialização e comparações
não podem ser encadeadas. Multiplicação e divisão têm prioridade sobre soma e
subtração, e parênteses alteram o agrupamento. O menos unário tem prioridade maior.

Cada bloco abre escopo. Redeclaração no mesmo escopo é erro, mas sombreamento
interno é permitido. A análise do inicializador ocorre antes de inserir o novo
nome. A especificação completa está em [especificacao.md](especificacao.md) e a
EBNF em [gramatica.md](gramatica.md).

## 5. Organização e interfaces

```text
MiniForge/
  miniforge/
    __init__.py       pacote
    __main__.py       CLI e controle das fases
    tokens.py         categorias e palavras reservadas
    lexer.py          texto para tokens e posições
    ast.py            nós e apresentação da árvore
    parser.py         tokens para AST
    simbolos.py       símbolos e pilha de escopos
    semantica.py      resolução e verificação de tipos
    ir.py             AST validada para instruções TAC
    constantes.py     avaliação estrita de uma operação literal
    otimizador.py     cinco passes e ponto fixo
    execucao.py       executor genérico de TAC, entrada e saída
  tests/              regressões e cenários por fase
  exemplos/           fontes .mini
    calculadora/      interface interativa, fontes, README e TAC de referência
  docs/               contratos, requisitos, relatórios e demonstração
  README.md           instalação e uso
  pytest.ini          configuração dos testes
  requirements-dev.txt
```

O nome genérico `minilang/` do roteiro corresponde a `miniforge/` neste projeto.
`constantes.py` é um auxiliar do middle-end. A organização mantém um arquivo por
responsabilidade e separa implementação, dados de exemplo e documentação.

## 6. Análise léxica

`Lexer(fonte).tokens()` devolve tokens com categoria, lexema e posição. O scanner
lê o identificador inteiro antes de consultar as reservadas, portanto nomes como
`enquanto_tiver2` continuam identificadores. Reconhece operadores de dois
caracteres antes de seus prefixos, ignora comentários e espaços e termina com EOF.
Caracteres inválidos geram diagnósticos; a leitura continua para listar outros
erros léxicos. A CLI interrompe o avanço antes do parser se houver erros.

Na declaração `trem primeiro: inteirim = 18;`, o lexer distingue a reservada de
declaração, o nome, dois-pontos, tipo, atribuição, literal e ponto e vírgula.
A posição preservada permite localizar o problema nas fases seguintes.

## 7. Gramática, parser e AST

`Parser(tokens).programa()` constrói a AST por análise descendente recursiva.
Níveis diferentes de expressão implementam precedência. O agrupamento está nos
nós, não nos delimitadores: `2 + 3 * 4` contém uma multiplicação dentro da soma;
`(2 + 3) * 4` contém a soma dentro da multiplicação. Os comandos possuem nós de
declaração, atribuição, saída, bloco, condicional e laço.

Erros como ponto e vírgula ausente ou chave não fechada impedem a geração de AST
completa. `--ast` permite examinar a árvore sintática sem exigir semântica válida.
A representação de saída e repetição na árvore não executa esses comandos.

## 8. Símbolos e análise semântica

`TabelaSimbolos` mantém uma pilha de dicionários. Símbolos registram nome, tipo,
categoria, linha da declaração e nível de escopo. A busca começa no bloco mais
interno. Ao encerrar um bloco, os nomes locais deixam de ser visíveis.

O visitante semântico percorre a AST, resolve nomes, verifica operadores e anota
expressões com tipo. As cinco regras centrais são declaração antes do uso,
redeclaração proibida no mesmo escopo, compatibilidade em inicialização e
atribuição, condições booleanas e operandos adequados aos operadores.
Expressão inválida não fornece tipo válido aos pais, evitando mensagens em
cascata; erros independentes continuam sendo acumulados. Avisos de nomes sem
uso não impedem a compilação. `--contexto` acrescenta a linha e o marcador `^`.

## 9. Geração de TAC

`gerar_tac(programa)` rejeita AST semanticamente inválida e usa `GeradorTAC`.
Expressões são percorridas em pós-ordem: primeiro os operandos, depois a operação.
Cada resultado intermediário recebe um temporário. `Instr` guarda operação,
destino, operandos e linha de origem. A formatação é uma instrução por linha.

```text
// Fonte: mostra_so(primeiro + segundo);
    t1 = primeiro + segundo
    print t1
```

Condicionais usam `iffalse`, `goto` e rótulos. A condição de laço fica após seu
rótulo inicial para ser alcançada novamente pelo salto de retorno. Variáveis
sombreadas recebem identidades distintas. Nomes do usuário como `t1` são
adaptados internamente para não colidir com temporários. A geração é determinística.

## 10. Otimizador e segurança

Cada passe recebe TAC e devolve `(novo_codigo, mudou)`. `otimizar()` repete os
cinco passes até não haver alteração. A entrada não é modificada inesperadamente.

| Passe | Transformação e cuidado |
|---|---|
| Propagação de constantes | Substitui leituras por literais conhecidos dentro do bloco básico; invalida destinos escritos e esquece valores em limites de fluxo |
| Dobramento de constantes | Avalia operações literais com tipos estritos e divisão inteira sem conversão para float |
| Saltos constantes | Resolve condição literal, criando oportunidades de remover caminhos inalcançáveis |
| Código morto | Remove código inalcançável e temporários dispensáveis, preservando divisões alcançáveis potencialmente falhas |
| Limpeza de rótulos | Remove rótulos sem referência e saltos para o ponto imediatamente seguinte |

Não se aplica `0 / x = 0` sem garantia sobre o divisor. Divisões por zero não
são dobradas. Propagar constantes anteriores a um laço como se fossem invariantes
seria incorreto; os limites de blocos evitam essa suposição. A avaliação literal
em `constantes.py` não percorre programas nem executa saltos.

## 11. Aplicação: Calculadora Mineira

### 11.1. Programa interativo na própria linguagem

O fonte `exemplos/calculadora/interativa.mini` contém todo o menu, leitura,
validação de opção, escolha da conta e repetição. O comando para executar é
`python -m miniforge exemplos/calculadora/interativa.mini --executar`.
A opção `-O` permite executar a versão otimizada. Não existe aplicativo Python
específico selecionando as contas ou produzindo programas para cada solicitação.

Foi necessário ampliar a linguagem com `le_so(nome);`, que exige variável
inteira declarada, e mensagens literais em `mostra_so("texto");`. O lexer ganhou
os tokens READ e TEXTO; o parser cria Leitura e Mensagem; a semântica verifica
as leituras e o gerador produz read/texto. Mensagens não são expressões de um
novo tipo: só podem aparecer como saída literal, sem escapes ou interpolação.

O novo módulo `miniforge/execucao.py` executa o TAC válido usando memória de
nomes internos e contador de instruções. A aritmética usa as regras já existentes,
inclusive divisão truncada para zero. O programa mineirês usa um laço para
repetir o menu e condicionais para escolher a operação e evitar divisor zero.
O visual usa molduras e mensagens mineiras. Uma verificação adicional impede
apresentar zero quando um numerador não nulo dividido por outro inteiro gera
quociente truncado zero (como 2 / 5). Zero verdadeiro, como 0 / 5, continua válido.
Essa validação pertence ao programa interativo, sem alterar o operador da linguagem.
Entrada decimal ou texto é rejeitada pelo leitor inteiro, que solicita novamente.
EOF e divisão por zero não protegida geram erro com linha de origem.

Isso é uma extensão efetiva de execução/backend em relação ao marco anterior,
autorizada pela necessidade posterior de uma aplicação interativa em mineirês.
Não se descreve o novo produto como um compilador sem execução. Python continua
sendo a linguagem de implementação do compilador e do executor, e mineirês é a
linguagem em que a aplicação está escrita. O arquivo `interativa.py` anterior foi
removido. Contratos e testes estão em [execucao.md](execucao.md).

### 11.2. Fonte fixo com seleção

O exemplo fixo está em `exemplos/calculadora/calculadora.mini`. Configura
`primeiro`, `segundo` e `operacao` com inteiros. Códigos 1, 2, 3 e 4 selecionam
soma, subtração, multiplicação e divisão. Condicionais aninhadas substituem um
comando de seleção que a linguagem não possui. Divisão por zero e código de
operação desconhecido atribuem falso à variável `valido`.

A calculadora representa primeiro a validade e depois o resultado, apenas se
válido. Essa separação evita usar um número especial como erro, pois zero e
negativos também são respostas legítimas. Os operandos ficam no fonte porque
a linguagem não possui entrada de dados. O programa é compilável e a aplicação
fixa é demonstrada pela tradução e otimização. O programa interativo completo
está descrito na seção 11.1.

O segundo fonte, `constantes.mini`, demonstra todas as operações, truncamento
negativo, precedência e parênteses. Os TAC originais e otimizados estão ao lado
dos fontes para comparação. O README próprio explica todas as configurações,
comandos, cenários e limitações: [Calculadora Mineira](../exemplos/calculadora/README.md).

## 12. Medições e forma de validação

Contagem estática exclui instruções `label` e inclui cópias, saídas e saltos.
Redução percentual: `100 * (antes - depois) / antes`.

| Programa e configuração | Antes | Depois | Redução |
|---|---:|---:|---:|
| Calculadora: 18, 6, operação 1 | 34 | 8 | 76,47% |
| Contas diretas da calculadora | 19 | 9 | 52,63% |
| Exemplo anterior `constantes.mini` na raiz de exemplos | 10 | 3 | 70,00% |
| Fatorial | 10 | 10 | 0,00% |

Na calculadora padrão, o TAC final contém `print eh_memo` e `print 24`. São
instruções geradas. Nas contas diretas, os operandos de `print` são 24, 12, 108,
3, -3, 14 e 20. As expectativas foram conferidas manualmente e por testes do
TAC. Essas medidas históricas não incluem velocidade. A revisão atual acrescenta
testes de execução com e sem otimização para os cenários da calculadora.
Zero redução no fatorial é compatível com uma otimização local conservadora.

Os testes cobrem fases do frontend, geração por construção, identidade de nomes,
alvos de saltos, origem das instruções, cada passe, ponto fixo, não mutação,
divisão por zero e inteiros grandes, CLI e importação independente de VM.
`tests/test_calculadora.py` acrescenta cenários da aplicação e comparação das
referências. `tests/test_calculadora_interativa.py` verifica execução real com
e sem otimização, leitura, mensagens, entradas inválidas, EOF, erros de execução,
repetição e contratos das novas fases. Comandos e resultados da execução atual estão em
[testes-calculadora.md](testes-calculadora.md). Os 696 testes anteriores são um
resultado histórico da integração, não a contagem da suíte ampliada.

Testes estruturais e parametrizados oferecem evidências para os casos cobertos.
Não constituem prova geral de equivalência semântica. A revisão atual inclui
testes de execução da aplicação com e sem otimização, com alcance restrito aos
casos cobertos.

## 13. Reproduzir a entrega

A partir da pasta `MiniForge/`, com Python 3.10+ instalado:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m miniforge exemplos/calculadora/interativa.mini --executar
python -m miniforge exemplos/calculadora/calculadora.mini --verificar
python -m miniforge exemplos/calculadora/calculadora.mini --tokens
python -m miniforge exemplos/calculadora/calculadora.mini --ast
python -m miniforge exemplos/calculadora/calculadora.mini --tipos
python -m miniforge exemplos/calculadora/calculadora.mini --tac
python -m miniforge exemplos/calculadora/calculadora.mini --tac -O
```

No Windows: `py -m venv .venv` e `.venv\Scripts\Activate.ps1` no PowerShell.
Inspeções podem ser combinadas. `-O` com inspeção exige `--tac`; por exemplo,
`--tipos --tac -O` é válido, mas `--tipos -O` retorna erro de uso.
Códigos: 0 para sucesso, 1 para leitura/análise e 2 para argumentos inválidos.
Erros e avisos vão para stderr. Uma fase com erro bloqueia as seguintes.

Para apresentar diagnósticos, use `exemplos/erro_lexico.mini`,
`exemplos/erro_sintatico.mini` e `exemplos/erro_semantico.mini` com
`--verificar --contexto`. Consulte também [demonstracao.md](demonstracao.md).

## 14. Conclusão e limites

O grupo criou uma linguagem própria e implementou o caminho do texto ao TAC
otimizado. A separação de fases permite localizar responsabilidades e erros.
A calculadora dá uma aplicação concreta às decisões da linguagem e demonstra
como constantes e fluxo de controle oferecem oportunidades de simplificação.

O produto inclui compilação até otimização e execução explícita de TAC para
a aplicação interativa. Não inclui funções, variáveis string, floats, vetores
ou operadores lógicos. A extensão de entrada e saída é restrita e documentada. A documentação
e os testes registram o que foi efetivamente construído e o alcance das evidências.

## 15. Referências do trabalho

- Material da disciplina: `Compiladores_2026-2_Aulas_Praticas_Projeto.pdf`.
- Versão completa do mesmo grupo: `MiniForge-v0.6-mineires.zip`.
- Repositório: https://github.com/PedroPignata/Compiladores/tree/main/MiniForge
- Integração principal: https://github.com/PedroPignata/Compiladores/pull/2
- Documentos internos: especificação, gramática, arquitetura, matriz,
  integração, testes e otimização, na pasta `docs/`.

## 16. Revisão de clareza e apresentação

Os comentários do código foram reduzidos a explicações de contratos e decisões
específicas, removendo referências a aulas e desafios. A lógica dos módulos
Python foi comparada por AST sem docstrings para assegurar que essa limpeza
não alterou a implementação. Comentários de casos de erro usados pelos testes
continuam presentes quando funcionam como expectativas dos arquivos de referência.

O terminal da calculadora recebeu uma moldura, opções alinhadas e frases
mineiras. A verificação de frações truncadas para zero fica no programa
interativo: se o numerador é não nulo e o quociente inteiro é zero, a resposta
é inválida. Zero matematicamente verdadeiro continua permitido. Essa decisão
não muda o contrato de divisão do compilador nem dos exemplos fixos.
A revisão anterior passou com 766 testes; o registro detalhado está em testes-calculadora.md.

## 17. Primeira versão do segundo programa (histórico)

O segundo programa completo fica em `exemplos/adivinha/adivinha.mini`. Ele é
inteiramente mineirês e usa os recursos existentes: declarações, entrada inteira,
saída de texto e valores, condicionais, comparações e repetição. Nenhum módulo
do compilador precisou mudar para acomodar o jogo.

O objetivo é descobrir um segredo fixo, padrão 65, no intervalo de 1 a 100.
O jogador recebe dicas para aumentar ou diminuir o próximo palpite. O contador
incrementa somente quando o inteiro está dentro do intervalo. Palpites válidos
repetidos contam novamente. Zero abandona a partida. Ao acertar, o programa
mostra a quantidade de tentativas e encerra; uma nova partida exige rodar de novo.
O segredo não é aleatório e deve ser alterado no fonte antes da compilação.

A configuração valida mínimo positivo, ordem dos limites e segredo dentro do
intervalo. Se houver incoerência, apresenta mensagem e não pede teclado.
A escolha de mínimo positivo preserva zero como comando de saída. Textos e
decimais no lugar de palpite são recusados pelo leitor de inteiros.

Na organização do roteiro, fontes e manuais das aplicações ficam em exemplos/,
testes em tests/, módulos em miniforge/ e registros técnicos em docs/. O novo
`exemplos/README.md` ensina a instalar, executar, inspecionar, editar os dois
programas e criar um fonte mínimo. Cada aplicação possui README próprio com
mapa do código, regras, personalizações e dificuldades frequentes. A estrutura
foi conferida novamente com a página física 5 (4/5) do material da professora.

Os 26 testes novos cobrem CLI original/otimizada, dicas, contagem, limites,
saída, personalização e invariantes do TAC. A suíte ampliada passou com
**792 testes em 14,21 s**. Foi também conferida uma sessão de terminal otimizada
com palpites 40, 80 e 65, encerrando com três tentativas e código 0.
O TAC padrão passou de 66 a 46 instruções sem rótulos (30,30% de redução
estática). Esses números não medem velocidade nem equivalência geral.

Na revisão inicial foi encontrada uma expectativa antiga da despedida nos
testes da calculadora. O fonte atual foi preservado e os testes passaram a
exigir “Até mais, sô!”, sem retirar asserções das operações ou dos erros.
Detalhes em [testes-programas.md](testes-programas.md). Guias:
[programas](../exemplos/README.md), [calculadora](../exemplos/calculadora/README.md)
e [jogo](../exemplos/adivinha/README.md).


## 18. Jogo com segredo aleatório

A versão atual substitui o segredo fixo por `sorteia_so(minimo, maximo)`.
Essa expressão inteira foi implementada no lexer, parser, AST, semântica,
TAC, otimizador e executor, mantendo a arquitetura de um módulo por fase.
O jogo sorteia uma vez, antes do laço, após validar os limites. Cada nova
partida chama novamente o gerador, podendo repetir um número por acaso.

O executor usa SystemRandom, sem semente fixa. A instrução random é efeito
observável e não pode ser dobrada nem removida quando alcançável por falta
de uso. A execução otimizada também sorteia normalmente. Não há aplicativo
Python auxiliar decidindo o segredo fora do programa mineirês.

Os guias agora ensinam a personalizar limites em vez de fixar a resposta.
Para demonstração previsível, um intervalo de um elemento é permitido.
O TAC passou de 62 para 48 instruções sem rótulos (22,58% de redução estática).
Resultados da validação completa em testes-sorteio.md e contrato em sorteio.md.
