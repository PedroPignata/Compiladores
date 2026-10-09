# Especificação da MiniForge — v0.0-spec

MiniForge é o nome do projeto e da linguagem implementada. Esta
especificação adota a proposta base dos slides e explicita regras das etapas
posteriores para manter o pipeline consistente. Os módulos futuros ainda não
implementam essas regras nesta entrega.

## Elementos léxicos

- Fonte em UTF-8, arquivos com extensão `.mini`.
- Identificadores: `[A-Za-z_][A-Za-z0-9_]*`, sensíveis a maiúsculas.
- Inteiros: `[0-9]+`, decimais; o sinal negativo é um operador separado.
- Palavras reservadas: `var`, `int`, `bool`, `true`, `false`, `print`, `if`,
  `else`, `while`. Não podem ser nomes de variáveis.
- Espaços, tabulações e quebras de linha separam tokens e são ignorados.
- Comentários começam com `//` e terminam na quebra de linha ou no fim do arquivo.
- Delimitadores: `(`, `)`, `{`, `}`, `:`, `;`.
- Operadores: `=`, `+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`, `<=`, `>=`.
- O lexer futuro deverá reconhecer o maior lexema possível e guardar linha e
  coluna, contadas a partir de 1, além de emitir EOF.

## Tipos e operadores

Há dois tipos: `int` (inteiros) e `bool` (literais `true` e `false`). Não há
conversão implícita entre eles. Como decisão inicial, inteiros não têm limite
fixo de bits, seguindo a implementação de referência em Python.

| Operação | Tipos dos operandos | Resultado |
| --- | --- | --- |
| `+`, `-`, `*`, `/` | `int`, `int` | `int` |
| `-` unário | `int` | `int` |
| `<`, `>`, `<=`, `>=` | `int`, `int` | `bool` |
| `==`, `!=` | `int`, `int` ou `bool`, `bool` | `bool` |

`/` faz divisão inteira truncando para zero: `7 / 2` resulta em `3` e
`-7 / 2` em `-3`. Divisão por zero será erro de execução, com a linha do fonte.

## Comandos

| Construção | Forma | Regra |
| --- | --- | --- |
| Declaração | `var nome: tipo = expr;` | Inicialização obrigatória e com o tipo declarado |
| Atribuição | `nome = expr;` | Nome já declarado; expressão do mesmo tipo |
| Saída | `print(expr);` | Aceita `int` ou `bool`; imprime uma linha |
| Condicional | `if (expr) { ... } else { ... }` | Condição `bool`; `else` opcional |
| Repetição | `while (expr) { ... }` | Condição `bool`, reavaliada antes de cada iteração |
| Bloco | `{ ... }` | Zero ou mais comandos em um novo escopo |

Chaves são obrigatórias nos corpos de `if`, `else` e `while`. Declaração,
atribuição e `print` terminam em `;`; blocos não levam `;` final. Um programa
é uma sequência de comandos, inclusive vazia. A execução futura será sequencial.
`print` mostrará booleanos como `true` / `false` em minúsculas.

## Precedência e associatividade

Da menor para a maior precedência:

| Nível | Operadores | Associatividade |
| --- | --- | --- |
| 1 | `==`, `!=`, `<`, `>`, `<=`, `>=` | Não associativos |
| 2 | `+`, `-` binários | Esquerda |
| 3 | `*`, `/` | Esquerda |
| 4 | `-` unário | Direita |

Parênteses alteram o agrupamento. `1 + 2 * 3` equivale a `1 + (2 * 3)`;
`10 - 3 - 2` equivale a `(10 - 3) - 2`. `a < b < c` é erro sintático.
Comparações explicitamente agrupadas ainda precisam respeitar os tipos.

## Escopo e nomes

O programa possui escopo global e cada `{ ... }` cria um escopo léxico interno.
A busca vai do escopo mais interno ao global. Variáveis devem ser declaradas
antes do uso; redeclaração no mesmo escopo é erro. Sombreamento em escopo
interno é permitido. Ao sair do bloco, seus nomes deixam de ser visíveis e os
nomes externos voltam a ser encontrados.

O inicializador é analisado antes de inserir o novo símbolo. Portanto,
`var x: int = x + 1;` falha se não houver `x` externo, mas pode usar um `x`
externo quando declara uma variável interna de mesmo nome.

## Limites desta versão

Não há funções, strings, floats, arrays, entrada de dados, `for`, `break`,
`continue`, operadores lógicos ou comentários de bloco. As extensões opcionais
dos slides ficam para depois do pipeline completo. Mudanças nesta especificação
exigirão revisar gramática, lexer e testes.

## Exemplos da entrega

| Arquivo em `exemplos/` | Classificação | Resultado futuro / erro esperado |
| --- | --- | --- |
| `fatorial.mini` | Válido | `120` |
| `if_else.mini` | Válido | `true` e `0`, em linhas separadas |
| `escopos.mini` | Válido | `true`, `2`, `1`, em linhas separadas |
| `erro_sintatico.mini` | Inválido | Esperado `:` na declaração |
| `erro_semantico.mini` | Inválido | Variável `ausente` não declarada |

Na etapa atual, todos esses arquivos são apenas lidos e impressos pela CLI;
a classificação acima é feita pela especificação, ainda sem analisadores.
