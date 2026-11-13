# Gramática da MiniForge

Versão final da aula 12 (11/09), usada pelo parser recursivo descendente da
aula 14 (`miniforge/parser.py`). Ela parte do rascunho de `v0.0-spec`, sem
ambiguidade e sem recursão à esquerda, pronta para parsing descendente LL(1).

**Mineirês do grupo, integrado em v0.5-otimizacao-sem-vm.** Os terminais agora são as palavras do mineirês (`trem`,
`inteirim`, `booleanim`, `eh_memo`, `num_eh`, `uai`, `sinao`,
`enquanto_tiver`, `mostra_so`). A estrutura original foi preservada; a extensão de leitura e texto está abaixo.
Os os não
terminais mantêm os nomes técnicos (`decl`, `if`, `while`, `print`), que são
também os nomes dos métodos do parser, e os conjuntos FIRST continuam
disjuntos, porque cada palavra reservada nova substitui exatamente uma antiga.

## Notação

| Notação | Significado |
| --- | --- |
| `{ x }` | `x` repetido zero ou mais vezes |
| `[ x ]` | `x` opcional |
| `a \| b` | alternativa |
| `"x"`, MAIÚSC. | terminais (tokens do lexer) |

`ID`, `NUM`, `TEXTO` e `EOF` são tokens do lexer. `ID` segue `[A-Za-z_][A-Za-z0-9_]*`,
excluídas as reservadas; `NUM` segue `[0-9]+`. Espaços e comentários `//` são
removidos pelo lexer antes do parser. `EOF` representa o fim do arquivo.
Chaves entre aspas (`"{"`, `"}"`) são caracteres da linguagem, não a notação
de repetição.

## Gramática G = (V, T, P, S)

- **V** (não terminais): `programa`, `comando`, `decl`, `tipo`, `atrib`,
  `print`, `leitura`, `if`, `while`, `bloco`, `expr`, `soma`, `termo`, `fator`.
- **T** (terminais): os tokens de `miniforge/tokens.py`.
- **P** (produções): abaixo.
- **S** (símbolo inicial): `programa`.

```ebnf
programa → { comando } EOF
comando  → decl | atrib | print | leitura | if | while | bloco

decl     → "trem" ID ":" tipo "=" expr ";"
tipo     → "inteirim" | "booleanim"
atrib    → ID "=" expr ";"
print    → "mostra_so" "(" (expr | TEXTO) ")" ";"
leitura  → "le_so" "(" ID ")" ";"
if       → "uai" "(" expr ")" bloco [ "sinao" bloco ]
while    → "enquanto_tiver" "(" expr ")" bloco
bloco    → "{" { comando } "}"

expr     → soma [ ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) soma ]
soma     → termo { ( "+" | "-" ) termo }
termo    → fator { ( "*" | "/" ) fator }
fator    → NUM | "eh_memo" | "num_eh" | ID
         | "(" expr ")" | "-" fator
```

## Decisões de projeto

- **Um nível por precedência.** Cada nível de precedência é um não terminal;
  quanto mais abaixo na gramática, mais forte o operador se liga:
  `expr` (comparação) < `soma` (`+ -`) < `termo` (`* /`) < `fator` (`-` unário,
  parênteses, literais). Assim `1 + 2 * 3` só pode agrupar como `1 + (2 * 3)`.
- **Sem recursão à esquerda.** O rascunho clássico `soma → soma "+" termo |
  termo` faria o parser descendente entrar em laço infinito (`RecursionError`).
  Aplicando `A → A α | β ⇒ A → β { α }`, fica `soma → termo { "+" termo }`.
  O laço `{ }` vira um `while` do Python no parser e mantém a associatividade à
  esquerda: `10 - 3 - 2 = (10 - 3) - 2`.
- **Comparação não associativa.** `expr` usa `[ ]`, não `{ }`: `a < b < c` é
  erro sintático (o parser para depois de `a < b` e acusa `faltou ';'`).
  Comparações agrupadas com parênteses, como `(a < b) == eh_memo`, são aceitas
  pela gramática; a semântica confere os tipos.
- **Blocos obrigatórios.** `uai` e `enquanto_tiver` exigem `{ }`. Isso elimina a
  ambiguidade do *else* pendente sem nenhuma regra extra: cada `sinao` pertence
  ao `uai` cujo bloco acabou de fechar.
- **`-` unário recursivo.** `fator → "-" fator` permite `- -4` e liga mais
  forte que qualquer binário: `-2 * 3 = (-2) * 3`.
- **O que a gramática não verifica.** Tipos, declaração antes do uso e
  escopos são da análise semântica (aulas 20 e 22). A gramática aceita
  `mostra_so(ausente);` e `trem b: booleanim = 1 + 2;`; a semântica os rejeita.

## Teste de ambiguidade

Com a gramática acima, cada cadeia tem uma única árvore de derivação.

`1 + 2 * 3` — só existe a árvore em que `*` fica mais abaixo:

```text
                soma
       ┌─────────┼──────────┐
     termo      "+"       termo
       │             ┌──────┼──────┐
     fator         fator   "*"   fator
       │             │             │
       1             2             3          agrupa 1 + (2 * 3)
```

A outra árvore, `(1 + 2) * 3`, exigiria um `termo` contendo `+`, o que não
existe: `termo` só gera `*` e `/` entre `fator`es, e `fator` só volta a gerar
`+` dentro de parênteses.

`1 - 2 - 3` — o laço `{ }` gera os termos da esquerda para a direita, e o
parser monta a AST acumulando à esquerda:

```text
           soma                               AST
  ┌─────┬───┼───┬─────┐                       Binario -
termo  "-" termo "-" termo                    ├── Binario -
  │         │         │                       │   ├── Num 1
fator     fator     fator                     │   └── Num 2
  │         │         │                       └── Num 3
  1         2         3                       agrupa (1 - 2) - 3
```

## Condição LL(1): conjuntos FIRST

Para escolher a produção olhando um único token, os FIRST das alternativas
de cada não terminal precisam ser disjuntos.

| Alternativa de `comando` | FIRST |
| --- | --- |
| `decl` | `trem` |
| `atrib` | `ID` |
| `print` | `mostra_so` |
| `if` | `uai` |
| `while` | `enquanto_tiver` |
| `bloco` | `{` |

| Alternativa de `fator` | FIRST |
| --- | --- |
| `NUM` | `NUM` |
| `"eh_memo"` | `eh_memo` |
| `"num_eh"` | `num_eh` |
| `ID` | `ID` |
| `"(" expr ")"` | `(` |
| `"-" fator` | `-` |

Os dois conjuntos são disjuntos, então `comando()` e `fator()` decidem com um
`if` do Python por token, sem voltar atrás. Também valem:

- `FIRST(expr) = FIRST(soma) = FIRST(termo) = FIRST(fator) =
  { NUM, eh_memo, num_eh, ID, (, - }`.
- `tipo`: `inteirim` e `booleanim` são disjuntos.
- Repetições e opcionais: o laço de `programa` para em `EOF`; o de `bloco`,
  em `}`; o de `soma` continua só com `+`/`-`; o de `termo`, com `*`/`/`; o
  `[ "sinao" bloco ]` entra só com `sinao`; o comparador de `expr`, só com um
  dos seis operadores relacionais. Nenhum desses tokens pode começar o que
  vem depois da repetição ou do opcional, então não há conflito FIRST/FOLLOW.

Qualquer outro token onde se espera um comando (por exemplo `1 = x;`, `sinao`
solto ou um `}` sobrando) gera `comando fora do lugar`; onde se espera um fator,
`faltou uma expressão`.

**Atenção para o futuro.** `atrib` começa com `ID`. Se a linguagem ganhar
chamada de função `f(x);`, que também começa com `ID`, os FIRST deixam de ser
disjuntos e será preciso olhar 2 tokens (`ID "="` × `ID "("`).

## Derivação mais à esquerda

Caso `tests/casos/validos/derivacao.mini`: `trem x: inteirim = 1 + 2 * 3;`. Em cada
passo, reescreve-se o não terminal mais à esquerda.

| # | Forma sentencial | Produção usada |
| --- | --- | --- |
| 1 | `programa` | símbolo inicial |
| 2 | `comando EOF` | `programa → { comando } EOF` (uma repetição) |
| 3 | `decl EOF` | `comando → decl` |
| 4 | `trem x : tipo = expr ; EOF` | `decl → "trem" ID ":" tipo "=" expr ";"` (`ID` é `x`) |
| 5 | `trem x : inteirim = expr ; EOF` | `tipo → "inteirim"` |
| 6 | `trem x : inteirim = soma ; EOF` | `expr → soma` (sem comparador) |
| 7 | `trem x : inteirim = termo + termo ; EOF` | `soma → termo { "+" termo }` (uma repetição) |
| 8 | `trem x : inteirim = fator + termo ; EOF` | `termo → fator` (zero repetições) |
| 9 | `trem x : inteirim = 1 + termo ; EOF` | `fator → NUM` |
| 10 | `trem x : inteirim = 1 + fator * fator ; EOF` | `termo → fator { "*" fator }` (uma repetição) |
| 11 | `trem x : inteirim = 1 + 2 * fator ; EOF` | `fator → NUM` |
| 12 | `trem x : inteirim = 1 + 2 * 3 ; EOF` | `fator → NUM` |

Só restam terminais: a cadeia pertence à linguagem. A AST correspondente,
impressa por `python -m miniforge tests/casos/validos/derivacao.mini --ast`:

```text
Programa
└── Decl x: inteirim
    └── Binario +
        ├── Num 1
        └── Binario *
            ├── Num 2
            └── Num 3
```

## Banco de casos (`tests/casos/`)

- `validos/`: 11 programas que precisam gerar AST sem erro (precedência,
  associatividade, aninhamento, `uai`/`sinao`, comparadores, booleanos,
  unário, blocos, programa vazio, fatorial e o caso da derivação).
- `invalidos/`: 13 programas, cada um com um único erro sintático. A 1ª linha
  é o comentário `// ERRO: <mensagem>` com a mensagem esperada, lida por
  `tests/test_casos.py`.

| Arquivo inválido | Código | 1ª linha (erro esperado) |
| --- | --- | --- |
| `falta_dois_pontos.mini` | `trem x inteirim = 1;` | `// ERRO: faltou ':'` |
| `expressao_incompleta.mini` | `x = 1 + ;` | `// ERRO: faltou uma expressão` |
| `if_sem_parenteses.mini` | `uai x > 1 { }` | `// ERRO: faltou '('` |
| `falta_ponto_virgula.mini` | `mostra_so(x)` | `// ERRO: faltou ';'` |
| `bloco_nao_fechado.mini` | `enquanto_tiver (x) { x = x - 1;` | `// ERRO: faltou '}'` |
| `comando_inesperado.mini` | `1 = x;` | `// ERRO: comando fora do lugar` |
| `parentese_nao_fechado.mini` | `trem b: booleanim = (1 + 2;` | `// ERRO: faltou ')'` |
| `nome_invalido.mini` | `trem 1x: inteirim = 0;` | `// ERRO: faltou um nome` |
| `comparacao_encadeada.mini` | `trem c: booleanim = 1 < 2 < 3;` | `// ERRO: faltou ';'` |
| `chave_sobrando.mini` | `x = 1; }` | `// ERRO: comando fora do lugar` |
| `tipo_invalido.mini` | `trem x: float = 1;` | `// ERRO: faltou o tipo ('inteirim' ou 'booleanim')` |
| `while_sem_bloco.mini` | `enquanto_tiver (x > 0) x = x - 1;` | `// ERRO: faltou '{'` |
| `falta_inicializacao.mini` | `trem x: inteirim;` | `// ERRO: faltou '='` |

O parser informa a mensagem completa no formato
`linha:coluna: erro sintático: <mensagem>, sô: achei '<lexema ou EOF>'`. A
posição é a do token em que o erro foi percebido: em `mostra_so(x)` sem `;`, o
erro aparece no `EOF`; se houver uma linha seguinte, aparece no primeiro
token dela (como GCC e Clang, que dizem "expected ';' before …").

## Desafio: `&&`, `||` e `!`

Não fazem parte da MiniForge (a especificação congelada não tem operadores
lógicos e o lexer rejeita `!` sozinho), mas a resposta do desafio é esta.
Seguindo C, Java e Python, `||` tem a menor precedência, depois `&&`, depois as
comparações; `!` é unário e liga tanto quanto o `-` unário:

```ebnf
expr  → ou
ou    → e { "||" e }
e     → comp { "&&" comp }
comp  → soma [ ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) soma ]
soma  → termo { ( "+" | "-" ) termo }
termo → fator { ( "*" | "/" ) fator }
fator → NUM | "eh_memo" | "num_eh" | ID | "(" expr ")" | "-" fator | "!" fator
```

Justificativa: `&&` abaixo de `||` faz `a || b && c` valer `a || (b && c)`,
como na álgebra booleana (o produto antes da soma); `!` em `fator` nega só o
operando seguinte. Árvore única de `!a || b && c` (AST):

```text
              ||
        ┌─────┴─────┐
        !           &&
        │        ┌──┴──┐
        a        b     c          agrupa (!a) || (b && c)
```

Se `!` ficasse acima de `||` (negando a expressão inteira), `!a || b` viraria
`!(a || b)`, contrariando a leitura usual.

## Extensão interativa de 13/11

`le_so` é reservada. `TEXTO` é um literal entre aspas duplas, sem escapes
e sem quebra de linha. Só aparece no comando de saída, não em `fator`.
Contrato semântico e execução: [execucao.md](execucao.md).
