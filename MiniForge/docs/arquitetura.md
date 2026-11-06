# Arquitetura do MiniForge

## Frontend entregue até 16/10/2026

A versão atual do grupo usa mineirês na superfície e mantém os contratos
internos do ZIP. O corte acadêmico inclui as aulas 06 a 22.

```text
Fonte .mini
    -> lexer.py + tokens.py          -> tokens com linha/coluna
    -> parser.py + ast.py            -> AST
    -> semantica.py + simbolos.py    -> AST validada e tipada
```

| Módulo | Responsabilidade | Contrato planejado |
| --- | --- | --- |
| `tokens.py` | Categorias e reservadas | `TipoToken`, `Token(tipo, lexema, linha, coluna)`, `RESERVADAS` |
| `lexer.py` | Converter texto em tokens | `Lexer(fonte).tokens()`, lista de erros léxicos e EOF |
| `ast.py` | Modelar a árvore | Dataclasses herdando de `No` (com `linha` e `coluna`): `Programa`, `Decl`, `Atrib`, `Print`, `Bloco`, `If`, `While`; expressões herdam de `Expr` (campo `tipo`): `Binario`, `Unario`, `Num`, `Bool`, `Var`; `formatar_ast` |
| `parser.py` | Reconhecer a gramática | `Parser(tokens).programa()` retorna `Programa`; `ErroSintatico` com posição |
| `simbolos.py` | Resolver nomes em escopos | `Simbolo(nome, tipo, categoria, linha, nivel)`, `TabelaSimbolos`: `entrar_escopo`, `sair_escopo`, `declarar` (devolve `None` na redeclaração), `buscar` |
| `semantica.py` | Validar nomes e tipos | `Visitor` (despacho por `visitar_<Nó>`), tabela `REGRAS` `(op, esq, dir) -> resultado`, `AnalisadorSemantico` acumula `erros` (com `posicoes`) e `avisos` e anota `no.tipo` em cada expressão, `analisar(programa)` |


O Visitor faz despacho por `visitar_<Nó>`. Cada expressão devolve `int`,
`bool` ou `None`; este último propaga erro sem emitir diagnósticos derivados.
O inicializador é visitado antes de declarar o nome. Cada bloco empilha um
dicionário e o desempilha ao terminar. `usos` permite avisos adicionais.

## Mineirês: só a superfície muda

`RESERVADAS` traduz as nove palavras mineiras em tipos de token como `T.VAR`
e `T.IF`. `TIPO_INTERNO` traduz `inteirim` e `booleanim` em `int` e `bool`.
`nome_tipo()` e `LITERAL_BOOL` preservam a linguagem na saída da AST e nas
mensagens. O parser e a semântica continuam usando seus contratos internos.
Não há aliases para as antigas palavras inglesas, que agora são nomes comuns.

## CLI e independência

A CLI padrão termina após a semântica e informa sucesso. Erros léxicos
impedem o parser; erros sintáticos impedem a semântica. Todos os diagnósticos
vão para stderr. A CLI não importa geradores, máquinas virtuais ou otimizador.
Os testes verificam essa independência estaticamente e em um processo real.
Consulte a tabela de combinações no README.

## Próximas integrações a partir do ZIP original

1. Aula 26 (30/10): incorporar `ir.py`, `test_ir.py` e seus contratos de
   temporários, rótulos e nomes internos únicos. Usar a AST já tipada.
2. Aula 28 (06/11): incorporar `vm.py` e testes de execução, preservando a
   divisão inteira exata, os booleanos mineiros e a opção explícita de verificar.
3. Aula 30 (13/11): incorporar `otimizador.py`, testes de equivalência e medir
   novamente os resultados. Depois preparar artigo e resultados da A2.

Essas datas pertencem ao cronograma. As fases acima estão concluídas no ZIP,
mas não fazem parte desta publicação. Reaplicar as alterações da CLI de forma
seletiva e preservar os testes de combinações adicionados nesta entrega.
Ver [integração](integracao.md) para inventário e hash da referência.
