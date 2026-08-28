# Mini C Compiler — Análise e Melhoria Individual

Projeto educacional escrito em **C** para estudo das etapas envolvidas no processamento de uma pequena linguagem.

Apesar do nome **Mini C Compiler**, a implementação atual funciona tecnicamente como um **interpretador baseado em AST**, pois o programa analisa o código-fonte e executa diretamente a árvore sintática, sem gerar código de máquina, assembly ou bytecode.

Este repositório contém a análise individual realizada para a disciplina de **Compiladores**, incluindo testes, documentação, evidências e uma melhoria no parser.

---

## Fluxo do programa

O processamento ocorre da seguinte forma:

```text
Arquivo-fonte
     ↓
read_file()
     ↓
Lexer
     ↓
Tokens
     ↓
Parser
     ↓
AST
     ↓
Interpretador
     ↓
Resultado
```

As principais etapas são:

1. **Leitura do arquivo** — carrega o código-fonte para a memória;
2. **Lexer** — transforma os caracteres em tokens;
3. **Parser** — organiza os tokens e constrói a AST;
4. **Interpretador** — percorre a AST e executa o programa;
5. **Tabela de símbolos** — armazena os valores das variáveis durante a execução.

---

## Estrutura do repositório

```text
mini-c-compiler/
├── docs/
├── evidencias/
├── examples/
├── include/
├── src/
├── testes/
├── .gitignore
├── LICENSE
├── README.md
└── RELATORIO.md
```

### Diretórios principais

- `src/` — implementação do lexer, parser, interpretador, utilitários e `main`;
- `include/` — arquivos de cabeçalho;
- `examples/` — exemplo de programa;
- `testes/` — casos de teste utilizados durante a análise;
- `evidencias/` — saídas completas dos testes T01 a T10;
- `docs/` — documentação existente no projeto original.

### Arquivos principais

- `RELATORIO.md` — relatório completo da atividade;
- `README.md` — visão geral e instruções de execução;
- `LICENSE` — licença preservada do projeto original.

---

## Requisitos

Para compilar e executar o projeto é necessário:

- sistema com compilador C;
- GCC ou compilador compatível;
- terminal.

Nenhuma biblioteca externa é necessária.

---

## Compilação

Na raiz do projeto:

```bash
gcc src/main.c src/lexer.c src/parser.c src/interpreter.c src/utils.c -Iinclude -o mini-c
```

O comando gera o executável local:

```text
mini-c
```

Esse executável está incluído no `.gitignore` e não é versionado.

---

## Execução

Para executar um programa:

```bash
./mini-c caminho/do/arquivo.txt
```

Exemplo:

```bash
./mini-c testes/T01_programa_original.txt
```

Entrada:

```c
let x = 5 + 3;
let y = 1 + 1;
print(x + y);
```

Saída final:

```text
10
```

Durante a execução, o programa também apresenta:

- código-fonte;
- tokens;
- AST;
- resultado da interpretação.

---

## Construções suportadas

A implementação atual reconhece:

### Declaração e atribuição

```c
let x = 5;
```

### Expressões aritméticas

```c
let x = 5 + 3 * 2;
```

Operadores disponíveis:

```text
+
-
*
/
```

### Parênteses

```c
let x = (5 + 3) * 2;
```

### Impressão

```c
print(x);
```

### Variáveis

```c
let x = 5;
let y = 10;
print(x + y);
```

---

## Tratamento de erros

Alguns erros analisados durante a atividade foram:

### Caractere desconhecido

```c
let valor = 10 @ 2;
```

Resultado:

```text
Unknown character: @
```

Classificação: **erro léxico**.

### Ausência de `=`

```c
let resultado 10 + 5;
```

Resultado:

```text
Syntax error: expected '=' at pos=2
```

Classificação: **erro sintático**.

### Ausência de `;`

```c
let resultado = 10 + 5
```

Resultado:

```text
Syntax error: expected ';' at pos=6
```

Classificação: **erro sintático**.

### Variável não definida

```c
print(x);
```

Resultado:

```text
Runtime error: undefined variable 'x'
```

A verificação acontece durante a interpretação.

### Divisão por zero

```c
let x = 10 / 0;
print(x);
```

Resultado:

```text
Runtime error: division by zero
```

---

## Testes da atividade

Foram executados os casos mínimos T01 a T10:

| ID | Finalidade |
|---|---|
| T01 | Programa original válido |
| T02 | Caractere desconhecido |
| T03 | Ausência de `=` |
| T04 | Ausência de `;` |
| T05 | Parêntese incompleto |
| T06 | Variável não definida |
| T07 | Divisão por zero |
| T08 | Precedência |
| T09 | Associatividade |
| T10 | Melhoria individual |

As saídas completas estão disponíveis em:

```text
evidencias/
```

A análise detalhada está em:

```text
RELATORIO.md
```

---

## Melhoria individual — precedência dos operadores

Durante os testes foi identificado um problema no parser original.

A expressão:

```c
print(2 * 3 + 4);
```

deveria resultar em:

```text
10
```

mas originalmente produzia:

```text
14
```

O parser tratava os operadores `+`, `-`, `*` e `/` no mesmo nível e construía determinadas expressões com agrupamento incorreto.

### Solução implementada

O parser foi reorganizado em níveis:

```text
parse_expression()
        ↓
parse_additive()
        ↓
parse_multiplicative()
        ↓
parse_primary()
```

Responsabilidades:

- `parse_primary()` — números, variáveis e parênteses;
- `parse_multiplicative()` — `*` e `/`;
- `parse_additive()` — `+` e `-`;
- `parse_expression()` — ponto de entrada da análise de expressões.

Após a alteração:

```c
print(2 * 3 + 4);
```

passou a produzir:

```text
10
```

Outro teste utilizado foi:

```c
let x = (10 + 2) * 3 - 4 / 2;
print(x);
```

Resultado original:

```text
12
```

Resultado após a correção:

```text
34
```

A estratégia adotada também corrigiu a associatividade à esquerda no teste:

```c
print(10 - 3 - 2);
```

que passou de:

```text
9
```

para:

```text
5
```

---

## Limitações observadas

Algumas limitações que permanecem no projeto:

- vetor de tokens com capacidade fixa;
- tabela de símbolos com capacidade fixa;
- ausência de linha e coluna nos tokens;
- variável indefinida detectada somente durante a execução;
- impressão de tokens não apresenta explicitamente os parênteses;
- impressão da AST não mostra adequadamente todos os comandos em alguns programas com múltiplas instruções;
- não existe geração de código de máquina, assembly ou bytecode.

Essas limitações são discutidas com mais detalhes no `RELATORIO.md`.

---

## Classificação da implementação

O fluxo termina com:

```c
interpret(ast);
```

Portanto, a AST é executada diretamente.

A versão atual deve ser classificada como:

**interpretador baseado em AST**

e não como compilador completo ou transpiler.

---

## Projeto original

Código-base:

```text
ironrinox/mini-c-compiler
```

Os créditos e a licença do projeto original foram preservados.

---

## Documentação da atividade

Para a análise completa, resultados dos testes, ASTs, explicação da melhoria e limitações encontradas, consulte:

```text
RELATORIO.md
```