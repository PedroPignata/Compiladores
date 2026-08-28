# Relatório — Análise do Mini C Compiler

## 1. Identificação do estudante

**Nome:** Pedro Rafael Santos Pignata
**Disciplina:** Compiladores
**Instituição:** IDP

---

## 2. Identificação do projeto original

O projeto analisado é o **Mini C Compiler**, desenvolvido em C com finalidade educacional.

**Projeto original:** `ironrinox/mini-c-compiler`
**Repositório individual:** `PedroPignata/mini-c-compiler`

O projeto original foi clonado e posteriormente publicado em um repositório individual, no qual foram adicionados testes, evidências, documentação e a melhoria implementada.

Os créditos e a licença original foram preservados.

---

## 3. Objetivo da atividade

O objetivo da atividade foi compreender o funcionamento do projeto desde a leitura do arquivo-fonte até sua execução.

Fluxo principal:

```text
Arquivo-fonte
→ read_file()
→ Lexer
→ Tokens
→ Parser
→ AST
→ Interpretador
→ Resultado
```

Também foram realizados testes válidos e inválidos, análise de precedência e associatividade e uma melhoria individual no parser.

A melhoria escolhida foi a **correção da precedência dos operadores**.

---

## 4. Preparação do ambiente

A atividade foi desenvolvida em Linux utilizando:

* Git;
* GCC;
* terminal;
* Visual Studio Code;
* GitHub;
* GitHub CLI.

Foram configurados:

```text
origin   → repositório individual
upstream → repositório original
```

O executável `mini-c` foi incluído no `.gitignore`.

---

## 5. Procedimento de compilação e execução

Compilação:

```bash
gcc src/main.c src/lexer.c src/parser.c src/interpreter.c src/utils.c -Iinclude -o mini-c
```

Execução:

```bash
./mini-c examples/test.txt
```

Também foram executados arquivos da pasta `testes/`.

A saída do programa apresenta:

1. código-fonte;
2. tokens;
3. AST;
4. resultado da interpretação.

---

## 6. Arquitetura e responsabilidades dos arquivos

| Arquivo                 | Responsabilidade                   |
| ----------------------- | ---------------------------------- |
| `src/main.c`            | Coordena o fluxo do programa       |
| `src/utils.c`           | Lê o arquivo-fonte                 |
| `include/lexer.h`       | Define tokens e estruturas léxicas |
| `src/lexer.c`           | Transforma caracteres em tokens    |
| `include/parser.h`      | Define a AST                       |
| `src/parser.c`          | Constrói e imprime a AST           |
| `include/interpreter.h` | Define a tabela de símbolos        |
| `src/interpreter.c`     | Executa a AST                      |
| `examples/test.txt`     | Programa de exemplo                |

Principais funções analisadas:

```text
read_file()
lex()
parse()
parse_statement()
parse_expression()
interpret()
eval_expression()
set_symbol()
lookup_symbol()
```

Após a melhoria também passaram a ser utilizadas:

```text
parse_primary()
parse_multiplicative()
parse_additive()
```

---

## 7. Análise do ponto de entrada

O ponto de entrada está em:

```c
int main(int argc, char* argv[])
```

O caminho do arquivo é recebido através de:

```c
argv[1]
```

Se nenhum arquivo for informado, `argc < 2`, e o programa apresenta uma mensagem de uso e encerra a execução.

Trecho principal:

```c
char* source_code = read_file(argv[1]);
TokenList tokens = lex(source_code);
ASTNode* ast = parse(&tokens);
interpret(ast);
```

A ordem das chamadas é:

```text
read_file()
→ lex()
→ parse()
→ interpret()
```

Assim:

* `read_file()` lê o arquivo;
* `lex()` produz os tokens;
* `parse()` constrói a AST;
* `interpret()` executa a AST.

---

## 8. Análise da leitura do arquivo

A função responsável é:

```c
read_file()
```

em `src/utils.c`.

Seu funcionamento é:

```text
fopen()
→ fseek()/ftell()
→ malloc()
→ fread()
→ '\0'
→ fclose()
→ retorno do buffer
```

A memória é alocada dinamicamente porque o tamanho do arquivo só é conhecido durante a execução.

O caractere:

```c
'\0'
```

marca o final da string em C.

Se `fopen()` falhar, o programa apresenta erro e encerra a execução.

A memória retornada por `read_file()` é posteriormente liberada no `main()`:

```c
free(source_code);
```

---

## 9. Análise léxica

O lexer está em:

```text
include/lexer.h
src/lexer.c
```

Tokens reconhecidos:

```text
T_NUMBER
T_PLUS
T_MINUS
T_MULT
T_DIV
T_LET
T_IDENTIFIER
T_EQUAL
T_PRINT
T_SEMICOLON
T_LPAREN
T_RPAREN
T_EOF
```

A função principal é:

```c
TokenList lex(const char* source)
```

O lexer utiliza:

* `isspace()` para espaços;
* `isdigit()` para números;
* `isalpha()` e `isalnum()` para identificadores;
* `strcmp()` para `let` e `print`;
* `switch` para operadores e símbolos.

### 9.1 Teste válido

Entrada:

```c
let valor1 = 123 + 4;
print(valor1);
```

Tokens principais:

```text
LET
IDENT(valor1)
EQUAL
NUMBER(123)
PLUS
NUMBER(4)
SEMICOLON
PRINT
IDENT(valor1)
SEMICOLON
EOF
```

Resultado:

```text
127
```

### 9.2 Teste inválido

Entrada:

```c
let valor = 10 @ 2;
```

Resultado:

```text
Unknown character: @
```

* caractere: `@`;
* arquivo: `src/lexer.c`;
* função: `lex()`;
* classificação: **erro léxico**.

### 9.3 Perguntas obrigatórias

**Como `let` é diferenciado de um identificador?**
O lexer constrói a palavra e utiliza `strcmp()` para compará-la com as palavras reservadas `let` e `print`. Caso não exista correspondência, o nome é classificado como `T_IDENTIFIER`.

**Como números de vários dígitos são construídos?**

O lexer acumula cada novo dígito utilizando:

```c
value = value * 10 + (source[i] - '0');
```

Assim, uma sequência como `123` é convertida progressivamente para o valor inteiro correspondente.

**`nota1` é aceito?**
Sim. O primeiro caractere deve ser uma letra, reconhecida por `isalpha()`, e os seguintes podem conter letras ou números, pois são verificados com `isalnum()`.

**Identificadores iniciados por número são aceitos?**
Não como um único identificador. Como o lexer reconhece primeiro sequências iniciadas por dígitos como números, uma entrada como `1nota` não é gerada como um único `T_IDENTIFIER`.

**O lexer registra linha e coluna?**
Não. A estrutura `Token` não possui campos para armazenar linha e coluna, e a implementação utiliza apenas a posição percorrida durante a análise.

**Existe limite de tokens?**
Sim. O lexer reserva espaço para 128 tokens:

```c
malloc(128 * sizeof(Token))
```

A implementação não possui redimensionamento automático desse vetor.

**O que pode ocorrer acima desse limite?**
O programa pode tentar escrever fora da região de memória reservada, provocando comportamento indefinido, como corrupção de memória ou falha durante a execução.

---

## 10. Análise sintática

O parser está em:

```text
include/parser.h
src/parser.c
```

Ele recebe os tokens e constrói uma AST.

As formas principais são:

```text
let IDENTIFICADOR = EXPRESSAO ;
print ( EXPRESSAO ) ;
```

Expressões podem conter números, identificadores, operadores e parênteses.

### 10.1 Teste válido

```c
let resultado = (10 + 5) * 2;
print(resultado);
```

Resultado:

```text
30
```

### 10.2 Ausência de `=`

```c
let resultado 10 + 5;
```

Resultado:

```text
Syntax error: expected '=' at pos=2
```

Detectado em `parse_statement()`.

### 10.3 Ausência de `;`

```c
let resultado = 10 + 5
```

Resultado:

```text
Syntax error: expected ';' at pos=6
```

Detectado em `parse_statement()`.

### 10.4 Parêntese incompleto

```c
print((10 + 5);
```

Resultado:

```text
Syntax error: expected ')' at pos=7
```

Após a melhoria, essa verificação ocorre em `parse_primary()`.

Todos são classificados como **erros sintáticos**.

---

## 11. Análise da AST

Os tipos de nós disponíveis são:

```c
AST_NUMBER
AST_BINARY_OP
AST_VAR
AST_ASSIGN
AST_PRINT
```

Cada nó possui:

```c
ASTNodeType type;
int value;
char name[32];
ASTNode* left;
ASTNode* right;
```

Para:

```c
let x = 5 + 3;
print(x);
```

a atribuição é representada como:

```text
AST_ASSIGN(x)
  AST_BINARY_OP(+)
    AST_NUMBER(5)
    AST_NUMBER(3)
```

* `AST_ASSIGN` representa a atribuição;
* `x` é armazenado em `name`;
* `AST_NUMBER` representa os números;
* `AST_BINARY_OP(+)` representa a soma;
* `left` e `right` representam os operandos.

Em operações binárias:

```text
       +
      / \
     5   3
```

O projeto também utiliza `right` para encadear comandos, o que gera algumas limitações na impressão da AST.

---

## 12. Análise da tabela de símbolos

A tabela de símbolos é definida em `include/interpreter.h`.

Cada símbolo possui:

```c
char name[32];
int value;
```

Exemplo:

```text
x → 5
idade → 30
```

Principais funções:

* `init_symbol_table()`: inicializa;
* `set_symbol()`: adiciona ou atualiza;
* `lookup_symbol()`: consulta.

A tabela suporta até 128 símbolos.

---

## 13. Análise do interpretador

O interpretador está em:

```text
src/interpreter.c
```

Fluxo:

```text
interpret()
→ exec_statement()
→ eval_expression()
→ lookup_symbol()/set_symbol()
```

`interpret()` percorre os comandos.

`exec_statement()` executa atribuições e impressões.

`eval_expression()` avalia números, variáveis e operações aritméticas.

### Variável definida

```c
let idade = 30;
print(idade);
```

Resultado:

```text
30
```

### Variável não definida

```c
print(x);
```

Resultado:

```text
Runtime error: undefined variable 'x'
```

A falha ocorre em `lookup_symbol()`.

É um **erro semântico detectado durante a execução**.

O parser aceita o identificador porque seu uso é sintaticamente válido. A verificação da existência da variável ocorre posteriormente no interpretador.

### Divisão por zero

```c
let x = 10 / 0;
print(x);
```

Resultado:

```text
Runtime error: division by zero
```

A falha é detectada em `eval_expression()` e é classificada como **erro de execução**.

---

## 14. Classificação do projeto

Apesar do nome **Mini C Compiler**, a versão analisada funciona como um **interpretador baseado em AST**.

O projeto não gera:

* código de máquina;
* assembly;
* bytecode;
* código C;
* outro programa de saída.

A execução termina com:

```c
interpret(ast);
```

Ou seja, a AST é percorrida e executada diretamente.

O GCC compila o interpretador escrito em C, e não os programas escritos na linguagem Mini C.

Portanto, o projeto atual é um **interpretador**, e não um compilador ou transpiler.

---

## 15. Resultados dos testes

| ID  | Teste                | Esperado         | Obtido                   | Situação |
| --- | -------------------- | ---------------- | ------------------------ | -------- |
| T01 | Programa original    | `10`             | `10`                     | Aprovado |
| T02 | Caractere `@`        | Erro léxico      | `Unknown character: @`   | Aprovado |
| T03 | Ausência de `=`      | Erro sintático   | `expected '='`           | Aprovado |
| T04 | Ausência de `;`      | Erro sintático   | `expected ';'`           | Aprovado |
| T05 | Parêntese incompleto | Erro sintático   | `expected ')'`           | Aprovado |
| T06 | Variável indefinida  | Erro em execução | `undefined variable 'x'` | Aprovado |
| T07 | Divisão por zero     | Erro em execução | `division by zero`       | Aprovado |
| T08 | `2 * 3 + 4`          | `10`             | `10` após melhoria       | Aprovado |
| T09 | `10 - 3 - 2`         | `5`              | `5` após melhoria        | Aprovado |
| T10 | Expressão complexa   | `34`             | `34`                     | Aprovado |

As saídas completas estão na pasta:

```text
evidencias/
```

---

## 16. Análise de precedência e associatividade

Os testes foram executados inicialmente na implementação original.

| Expressão    | Esperado | Obtido | Diagnóstico                 |
| ------------ | -------: | -----: | --------------------------- |
| `2 * 3 + 4`  |       10 |     14 | Problema de precedência     |
| `10 - 3 - 2` |        5 |      9 | Problema de associatividade |
| `2 + 3 * 4`  |       14 |     14 | Correto nesse caso          |

No primeiro caso, a AST representava:

```text
2 * (3 + 4)
```

em vez de:

```text
(2 * 3) + 4
```

No segundo:

```text
10 - (3 - 2)
```

em vez de:

```text
(10 - 3) - 2
```

Também foi testado:

```c
let x = (10 + 2) * 3 - 4 / 2;
print(x);
```

Resultado original:

```text
12
```

Resultado convencional:

```text
34
```

A causa estava em `parse_expression()`, que tratava:

```text
+ - * /
```

no mesmo nível e utilizava uma nova chamada recursiva para analisar o operando da direita.

---

## 17. Descrição da melhoria individual

### 17.1 Problema ou limitação escolhida

Foi escolhida a **correção da precedência dos operadores**, opção nº 9 da atividade.

### 17.2 Comportamento anterior

A expressão:

```c
print(2 * 3 + 4);
```

produzia:

```text
14
```

quando deveria produzir `10`.

A expressão:

```c
let x = (10 + 2) * 3 - 4 / 2;
print(x);
```

produzia `12`, em vez de `34`.

### 17.3 Comportamento desejado

O parser deveria respeitar:

```text
* e / → maior precedência
+ e - → menor precedência
```

Assim:

```text
2 * 3 + 4
```

deveria ser interpretado como:

```text
(2 * 3) + 4
```

### 17.4 Arquivo alterado

```text
src/parser.c
```

### 17.5 Funções alteradas ou criadas

Foram utilizadas:

```text
parse_expression()
parse_additive()
parse_multiplicative()
parse_primary()
```

Nova hierarquia:

```text
parse_expression()
→ parse_additive()
→ parse_multiplicative()
→ parse_primary()
```

### 17.6 Decisões de implementação

`parse_primary()` trata:

* números;
* variáveis;
* parênteses.

`parse_multiplicative()` trata:

```text
* /
```

`parse_additive()` trata:

```text
+ -
```

`parse_expression()` passa a chamar:

```c
return parse_additive(tokens, pos);
```

Dessa forma, multiplicação e divisão são construídas antes de soma e subtração.

Os laços `while` também fazem operações do mesmo nível serem agrupadas progressivamente pela esquerda.

### 17.7 Casos de teste e resultado obtido

| Expressão              | Antes | Depois | Esperado |
| ---------------------- | ----: | -----: | -------: |
| `2 * 3 + 4`            |    14 |     10 |       10 |
| `10 - 3 - 2`           |     9 |      5 |        5 |
| `2 + 3 * 4`            |    14 |     14 |       14 |
| `(10 + 2) * 3 - 4 / 2` |    12 |     34 |       34 |

O T10 utilizado foi:

```c
let x = (10 + 2) * 3 - 4 / 2;
print(x);
```

Resultado:

```text
34
```

### 17.8 Testes de regressão

Após a alteração foram novamente testados:

* atribuição;
* soma;
* multiplicação;
* parênteses;
* variável indefinida;
* divisão por zero;
* ausência de `=`;
* ausência de `;`;
* múltiplas variáveis.

Os comportamentos anteriores continuaram funcionando.

### 17.9 Limitações que permaneceram

A melhoria corrigiu a precedência e também o agrupamento à esquerda observado nos testes.

Outras limitações permanecem e são apresentadas na próxima seção.

---

## 18. Limitações encontradas

### Lista de tokens fixa

O lexer reserva espaço para apenas 128 tokens e não redimensiona o vetor.

### Ausência de linha e coluna

Os tokens não armazenam linha e coluna, reduzindo a precisão das mensagens de erro.

### Tabela de símbolos fixa

A tabela suporta no máximo 128 variáveis.

### Variável indefinida somente em execução

Não existe uma fase semântica separada que verifique previamente a existência das variáveis.

### Impressão incompleta de parênteses

O lexer reconhece `T_LPAREN` e `T_RPAREN`, mas `print_tokens()` não os apresenta explicitamente na saída observada.

### Impressão parcial da AST

`print_ast()` pode não mostrar todos os comandos em programas com múltiplas instruções.

### Encadeamento de comandos

O campo `right` também é utilizado para encadear statements, enquanto em operações binárias representa o operando da direita.

Uma estrutura específica para lista de comandos seria mais adequada.

---

## 19. Conclusão

A atividade permitiu compreender o fluxo:

```text
arquivo-fonte
→ lexer
→ tokens
→ parser
→ AST
→ interpretador
→ resultado
```

Foram analisados o lexer, parser, AST, tabela de símbolos, interpretador e diferentes tipos de erro.

Também foi possível concluir que a implementação atual funciona como um **interpretador baseado em AST**.

Os testes revelaram uma falha nas regras de precedência e associatividade do parser original.

A solução foi reorganizar o parser em níveis:

```text
parse_expression()
→ parse_additive()
→ parse_multiplicative()
→ parse_primary()
```

Após a alteração, os resultados passaram a respeitar a precedência convencional, e os testes anteriores continuaram funcionando.

Assim, a atividade permitiu identificar uma limitação real do projeto, implementar uma solução e validá-la por meio de testes.

---

## 20. Referências

IRONRINOX. **Mini C Compiler**. GitHub.

Repositório original:

```text
ironrinox/mini-c-compiler
```

Repositório individual:

```text
PedroPignata/mini-c-compiler
```

Material da disciplina de Compiladores disponibilizado pelo professor.

**Atividade Individual — Análise do Mini C Compiler.** Disciplina de Compiladores, 2026.

---

## Registro de uso de ferramentas de IA

Durante a atividade foi utilizada ferramenta de inteligência artificial como apoio para compreensão do código, análise dos testes e revisão da documentação.

Os comandos, alterações e testes apresentados foram executados e verificados no ambiente local.

A compreensão, validação e apresentação do trabalho permanecem sob responsabilidade do estudante.

Repositório do Git: https://github.com/PedroPignata/mini-c-compiler