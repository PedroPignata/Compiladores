# Parser do Mini C Compiler

O parser recebe TokenList de lex e constrói nós definidos em include/parser.h.
Os tipos reais são AST_NUMBER, AST_VAR, AST_BINARY_OP, AST_ASSIGN e AST_PRINT.
Não existem AST_LET ou AST_IDENTIFIER nesse enum.

```c
TokenList tokens = lex("let x = 5 + 3; print(x);");
ASTNode* root = parse(&tokens);
print_ast(root, 0);
```

## Precedência vigente

parse_expression chama parse_additive, que chama parse_multiplicative,
que chama parse_primary. Multiplicação e divisão têm precedência maior que
soma e subtração. Os laços associam operadores à esquerda. Parênteses são
tratados em parse_primary.

O comando let produz AST_ASSIGN, com o nome no campo name e a expressão em
left. print produz AST_PRINT, com a expressão em left. Os comandos sequenciais
são encadeados pelo campo right, também usado para operandos de nós binários.
Essa reutilização impõe limitações: a impressão recursiva não mostra toda a
sequência e expressões isoladas com right ocupado merecem cautela, conforme o
relatório da atividade. Não se descreve essa estrutura como uma AST genérica
sem limitações.

Exemplo conceitual da sequência:

```text
AST_ASSIGN(x)              right -> AST_PRINT
  left -> AST_BINARY_OP(+)           left -> AST_VAR(x)
            left -> AST_NUMBER(5)
            right -> AST_NUMBER(3)
```

Este diagrama explica campos; não é uma captura literal de print_ast, que não
imprime o encadeamento inteiro. Falhas sintáticas encerram o processo com
mensagem e código 1. Os tokens não guardam posição de linha/coluna.
Detalhes, evidências e limites: [RELATORIO.md](../RELATORIO.md).
