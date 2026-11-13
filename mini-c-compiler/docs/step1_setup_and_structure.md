# Estrutura atual do Mini C Compiler

Esta aplicação está na pasta mini-c-compiler/ do repositório Compiladores.
O código já implementa lexer, parser e interpretador baseado em AST; não há
placeholders de uma etapa inicial aguardando implementação.

```text
mini-c-compiler/
  src/       main.c, lexer.c, parser.c, interpreter.c, utils.c
  include/   cabeçalhos das funções e estruturas
  testes/    programas usados na análise
  examples/  exemplo original
  evidencias/ saídas registradas da atividade
  docs/      descrição dos módulos
  README.md, RELATORIO.md, LICENSE
```

Da raiz Compiladores:

```bash
cd mini-c-compiler
gcc src/main.c src/lexer.c src/parser.c src/interpreter.c src/utils.c -Iinclude -o mini-c
./mini-c testes/T01_programa_original.txt
```

A AST é interpretada diretamente. Este projeto não usa os módulos Python,
TAC ou vocabulário mineirês do MiniForge.
Leia o [manual](../README.md), o [relatório](../RELATORIO.md), o
[lexer](step2_lexer.md), o [parser](step3_parser.md) e o
[interpretador](step4_interpreter.md).
