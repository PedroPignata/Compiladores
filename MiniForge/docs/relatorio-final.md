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
de otimização até um ponto fixo. A Calculadora Mineira é a aplicação demonstrativa
escrita nessa linguagem. O relatório descreve a implementação e suas evidências,
sem atribuir resultados de execução ao código que apenas foi compilado.

A entrega final termina na otimização do código intermediário. A CLI imprime TAC
original ou otimizado. Não há executor, backend, bytecode nem entrada pelo teclado.
Essa delimitação é importante para interpretar os comandos de demonstração.

## 2. Objetivos e motivação

O objetivo acadêmico é implementar as responsabilidades de cada fase de um
compilador, com interfaces explícitas e testes. A linguagem pequena permite
acompanhar uma expressão desde o lexema até a instrução intermediária.
O vocabulário regional diferencia a linguagem sem aumentar excessivamente a
gramática. Python implementa o compilador, mas o fonte que ele aceita é mineirês:
`uai (x > 0) { mostra_so(x); }` não é código Python e não é encaminhado a `eval`.

A calculadora demonstra uma aplicação compreensível: configura dois inteiros e
uma operação, seleciona a conta e representa a validade e o resultado. Sua leitura
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
  tests/              regressões e cenários por fase
  exemplos/           fontes .mini
    calculadora/      aplicação, README e TAC de referência
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

A aplicação está em `exemplos/calculadora/calculadora.mini`. Configura
`primeiro`, `segundo` e `operacao` com inteiros. Códigos 1, 2, 3 e 4 selecionam
soma, subtração, multiplicação e divisão. Condicionais aninhadas substituem um
comando de seleção que a linguagem não possui. Divisão por zero e código de
operação desconhecido atribuem falso à variável `valido`.

A calculadora representa primeiro a validade e depois o resultado, apenas se
válido. Essa separação evita usar um número especial como erro, pois zero e
negativos também são respostas legítimas. Os operandos ficam no fonte porque
a linguagem não possui entrada de dados. O programa é compilável e a aplicação
é demonstrada pela tradução e otimização, sem alegar interface interativa.

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
TAC. Não há medição de velocidade nem execução comparativa antes/depois.
Zero redução no fatorial é compatível com uma otimização local conservadora.

Os testes cobrem fases do frontend, geração por construção, identidade de nomes,
alvos de saltos, origem das instruções, cada passe, ponto fixo, não mutação,
divisão por zero e inteiros grandes, CLI e importação independente de VM.
`tests/test_calculadora.py` acrescenta cenários da aplicação e comparação das
referências. Comandos e resultados da execução atual estão em
[testes-calculadora.md](testes-calculadora.md). Os 696 testes anteriores são um
resultado histórico da integração, não a contagem da suíte ampliada.

Testes estruturais e parametrizados oferecem evidências para os casos cobertos.
Não constituem prova geral de equivalência semântica. Também não substituem
testes de execução, que estão fora do produto implementado.

## 13. Reproduzir a entrega

A partir da pasta `MiniForge/`, com Python 3.10+ instalado:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
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

O produto final limita-se à compilação até otimização. Não inclui funções,
strings, floats, vetores, operadores lógicos, leitura interativa nem execução.
A ausência desses recursos limita o tipo de aplicação possível, mas não exige
modificar a linguagem para demonstrar as fases implementadas. A documentação
e os testes registram o que foi efetivamente construído e o alcance das evidências.

## 15. Referências do trabalho

- Material da disciplina: `Compiladores_2026-2_Aulas_Praticas_Projeto.pdf`.
- Versão completa do mesmo grupo: `MiniForge-v0.6-mineires.zip`.
- Repositório: https://github.com/PedroPignata/Compiladores/tree/main/MiniForge
- Integração principal: https://github.com/PedroPignata/Compiladores/pull/2
- Documentos internos: especificação, gramática, arquitetura, matriz,
  integração, testes e otimização, na pasta `docs/`.
