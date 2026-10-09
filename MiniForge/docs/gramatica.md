# Gramática inicial da MiniLang

Rascunho EBNF para a entrega `v0.0-spec`, alinhado à proposta base e à gramática
da aula 12. Será revisado na etapa de gramática e testes.

`{ x }` significa repetição zero ou mais vezes; `[ x ]`, opcional; `|`, alternativa.
Elementos entre aspas são terminais. `ID`, `NUM` e `EOF` são tokens do lexer.
Chaves entre aspas são caracteres da linguagem, não a notação de repetição.

```ebnf
programa    = { comando }, EOF ;
comando     = declaracao | atribuicao | saida | condicional | repeticao | bloco ;
declaracao  = "var", ID, ":", tipo, "=", expr, ";" ;
tipo        = "int" | "bool" ;
atribuicao  = ID, "=", expr, ";" ;
saida       = "print", "(", expr, ")", ";" ;
condicional = "if", "(", expr, ")", bloco, [ "else", bloco ] ;
repeticao   = "while", "(", expr, ")", bloco ;
bloco       = "{", { comando }, "}" ;

expr        = soma, [ comparador, soma ] ;
comparador  = "==" | "!=" | "<" | ">" | "<=" | ">=" ;
soma        = termo, { ( "+" | "-" ), termo } ;
termo       = fator, { ( "*" | "/" ), fator } ;
fator       = NUM | "true" | "false" | ID | "(", expr, ")" | "-", fator ;
```

`ID` segue `[A-Za-z_][A-Za-z0-9_]*`, excluídas as reservadas; `NUM` segue
`[0-9]+`. Espaços e comentários `//` são removidos pelo lexer antes do parser.
EOF representa o fim do arquivo, não uma palavra escrita no fonte.

## Decisões para o parser futuro

- Um método por não terminal, sem recursão à esquerda.
- Repetições em `soma` e `termo` serão laços que constroem associatividade à
  esquerda: `10 - 3 - 2` forma `(10 - 3) - 2`.
- O nível `termo` dá a `*` e `/` prioridade sobre `+` e `-`.
- O comparador é opcional, sem repetição: `a < b < c` é rejeitado.
- Blocos obrigatórios eliminam a ambiguidade do `else` pendente.
- Tipos, declaração antes do uso e visibilidade são responsabilidade da análise
  semântica. A gramática pode aceitar `print(ausente);`, mas a semântica o rejeita.

| Alternativa de comando | Primeiro token |
| --- | --- |
| `declaracao` | `var` |
| `atribuicao` | `ID` |
| `saida` | `print` |
| `condicional` | `if` |
| `repeticao` | `while` |
| `bloco` | `{` |

Essas alternativas têm FIRST distintos e permitem escolher o comando com um
único token. As alternativas de `fator` começam com `NUM`, `true`, `false`,
`ID`, `(` e `-`, também distintos.
