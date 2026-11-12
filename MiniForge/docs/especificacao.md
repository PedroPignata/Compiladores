# Especificação do mineirês — v0.5-otimizacao-sem-vm

MiniForge é o nome do projeto e do compilador. A linguagem do grupo é o
**mineirês**, com as decisões da versão v0.6 do ZIP. Esta publicação entrega
léxico, sintaxe, símbolos, semântica, TAC e otimização até a aula 30 (13/11/2026), sem VM.
A semântica dinâmica descrita abaixo orienta a execução futura, ainda ausente.

## Elementos léxicos

- Fonte em UTF-8, arquivos com extensão `.mini`.
- Identificadores: `[A-Za-z_][A-Za-z0-9_]*`, sensíveis a maiúsculas.
- Inteiros: `[0-9]+`, decimais; o sinal negativo é um operador separado.
- Palavras reservadas (todas em minúsculas e sem acento, para o fonte
  funcionar em qualquer terminal e editor):

  | Mineirês | Papel | Conceito nos slides | De onde vem |
  | --- | --- | --- | --- |
  | `trem` | declara variável | `var` | "trem" é qualquer coisa em Minas |
  | `inteirim` | tipo inteiro | `int` | diminutivo mineiro de "inteiro" |
  | `booleanim` | tipo booleano | `bool` | idem |
  | `eh_memo` | verdadeiro | `true` | "é mêmo" |
  | `num_eh` | falso | `false` | "num é" |
  | `uai` | condicional | `if` | a interjeição mais mineira que há |
  | `sinao` | senão | `else` | "sinão" |
  | `enquanto_tiver` | repetição | `while` | "enquanto tiver" |
  | `mostra_so` | saída | `print` | "mostra, sô" |

  Não podem ser nomes de variáveis. As palavras antigas (`var`, `while`...)
  agora são identificadores comuns.
- O `_` faz parte das palavras: `enquanto_tiver` é um token só (maior
  casamento), e `enquanto_tiver2` é um identificador.
- Acentos continuam fora do alfabeto: `mostra_sô` gera erro léxico no `ô`.
  Por isso as palavras são escritas sem acento (`mostra_so`, `sinao`,
  `eh_memo`); comentários `//` aceitam qualquer caractere.
- Espaços, tabulações e quebras de linha separam tokens e são ignorados.
- Comentários começam com `//` e terminam na quebra de linha ou no fim do arquivo.
- Delimitadores: `(`, `)`, `{`, `}`, `:`, `;`.
- Operadores: `=`, `+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`, `<=`, `>=`.
- O lexer reconhece o maior lexema possível e guarda linha e coluna,
  contadas a partir de 1, além de emitir EOF.
- Erros léxicos (caractere fora do alfabeto, como `@`, `$`, `!` sozinho ou
  letras acentuadas) são reportados como
  `linha:coluna: erro léxico: caractere inválido 'c', que trem é esse?`; o caractere é
  descartado e a análise continua, para listar todos os erros de uma vez.
- `12ab` não é erro léxico: vira `NUM` seguido de `ID` (maior casamento), e o
  erro aparece na análise sintática.

## Tipos e operadores

Há dois tipos: `inteirim` (inteiros) e `booleanim` (literais `eh_memo` e
`num_eh`). Por dentro do compilador eles se chamam `int` e `bool` (é o que
aparece em `REGRAS`, em `no.tipo` e nos testes das fases internas); para o
programador, mensagens e a AST impressa usam sempre os nomes mineiros. Não há
conversão implícita entre eles. Como decisão inicial, inteiros não têm limite
fixo de bits, seguindo a implementação de referência em Python.

| Operação | Tipos dos operandos | Resultado |
| --- | --- | --- |
| `+`, `-`, `*`, `/` | `inteirim`, `inteirim` | `inteirim` |
| `-` unário | `inteirim` | `inteirim` |
| `<`, `>`, `<=`, `>=` | `inteirim`, `inteirim` | `booleanim` |
| `==`, `!=` | `inteirim`, `inteirim` ou `booleanim`, `booleanim` | `booleanim` |

`/` faz divisão inteira truncando para zero: `7 / 2` resulta em `3` e
`-7 / 2` em `-3`. A execução dessa regra e a detecção de divisão por zero ficam para a VM
(em etapa futura). O frontend verifica somente os tipos dos operandos.

## Comandos

| Construção | Forma | Regra |
| --- | --- | --- |
| Declaração | `trem nome: tipo = expr;` | Inicialização obrigatória e com o tipo declarado |
| Atribuição | `nome = expr;` | Nome já declarado; expressão do mesmo tipo |
| Saída | `mostra_so(expr);` | Aceita `inteirim` ou `booleanim`; imprime uma linha |
| Condicional | `uai (expr) { ... } sinao { ... }` | Condição `booleanim`; `sinao` opcional |
| Repetição | `enquanto_tiver (expr) { ... }` | Condição `booleanim`, reavaliada antes de cada iteração |
| Bloco | `{ ... }` | Zero ou mais comandos em um novo escopo |

Chaves são obrigatórias nos corpos de `uai`, `sinao` e `enquanto_tiver`.
Declaração, atribuição e `mostra_so` terminam em `;`; blocos não levam `;`
final. Um programa é uma sequência de comandos, inclusive vazia. A execução é
sequencial. `mostra_so` escreve booleanos como `eh_memo` / `num_eh`, do mesmo
jeito que no fonte.

Exemplo (`exemplos/pao_de_queijo.mini`, validado sem execução nesta entrega):

```text
trem fornada: inteirim = 1;
trem paes: inteirim = 0;
enquanto_tiver (fornada <= 3) {
    paes = paes + fornada * 12;
    fornada = fornada + 1;
}
mostra_so(paes);
trem sobrou: booleanim = paes > 50;
uai (sobrou) {
    mostra_so(paes - 50);     // pra visita, sô
} sinao {
    mostra_so(0);
}
```

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

**Decisão da turma (aula 20): sombreamento.** Redeclarar no **mesmo** escopo
é erro; declarar o mesmo nome em um escopo interno é permitido, com qualquer
tipo. Os corpos de `uai`, `sinao` e `enquanto_tiver` são blocos e, portanto,
escopos.

Cada nome declarado vira um símbolo com cinco atributos: nome, tipo
(`int` ou `bool`, os nomes internos), categoria (`variavel`, a única nesta versão), linha da
declaração e nível do escopo (0 é o global). A tabela de símbolos é uma pilha
de dicionários com as operações `entrar_escopo`, `sair_escopo`,
`declarar(nome, tipo, linha)` e `buscar(nome)`.

O inicializador é analisado antes de inserir o novo símbolo. Portanto,
`trem x: inteirim = x + 1;` falha se não houver `x` externo, mas pode usar um `x`
externo quando declara uma variável interna de mesmo nome.

## Regras semânticas e mensagens (aula 22)

A análise semântica é estática: tudo é decidido olhando a AST, sem executar o
programa. O que não puder ser decidido assim (como divisão por zero com valor
calculado) fica para a VM, em tempo de execução. As 5 regras são:

1. Toda variável é declarada antes do uso.
2. Não há redeclaração no mesmo escopo.
3. Em `trem x: T = e;` e `x = e;`, o tipo de `e` é igual ao de `x`.
4. A condição de `uai` e `enquanto_tiver` é `booleanim`.
5. Cada operador recebe os tipos da tabela da seção "Tipos e operadores".

Não há conversão implícita: o mineirês é fortemente tipado (`uai (1)` é erro;
`0` não vale como `num_eh`). Exemplos: `1 + 2` é `inteirim`, `1 < 2` é
`booleanim`, `eh_memo == num_eh` é `booleanim`; `eh_memo + 1`, `1 == eh_memo` e
`uai (1)` são erros.

Erros semânticos têm o formato `linha L: erro semântico: <mensagem>` e são
todos acumulados antes de a CLI sair com código 1. Cada mensagem diz onde
(linha), a fase (semântico), o quê (nome ou operador envolvido) e, nos erros
de tipo, esperado × encontrado:

| Regra | Situação | Mensagem |
| --- | --- | --- |
| 1 | Uso ou atribuição de nome sem declaração visível | `'x' num foi declarado, sô` |
| 2 | Redeclaração no mesmo escopo | `'x' já foi declarado neste escopo, uai` |
| 3 | Inicializador ou valor atribuído de outro tipo | `'b' é booleanim, mas tá recebendo inteirim` |
| 4 | Condição de `uai`/`enquanto_tiver` que não é `booleanim` | `condição tem que ser booleanim, mas veio inteirim` |
| 5 | Operador binário com tipos fora da tabela | `operador '+' num serve pra booleanim e inteirim` |
| 5 | `-` unário aplicado a `booleanim` | `operador '-' num serve pra booleanim` |

**Sem erros em cascata.** Uma expressão que contém erro não tem tipo, e quem
a usa não reporta de novo: `mostra_so(z + 1 + 2);` gera só `'z' não foi
declarada`. Uma declaração com inicializador errado ainda declara o nome com
o tipo escrito, para os usos seguintes não gerarem `'x' num foi declarado, sô`.
Se houver erros, os avisos não são listados.

**AST anotada.** Cada nó de expressão recebe o campo `tipo` (`int` ou
`bool` por dentro; a CLI imprime `inteirim` ou `booleanim`). Uma AST sem erros semânticos está toda tipada, e as fases seguintes
não precisam checar mais nada. A CLI mostra essa árvore com `--tipos`.

Variáveis declaradas e nunca lidas geram um **aviso**, não um erro
(`linha L: aviso: 'x' declarado e nunca usado, sô`, como o `-Wunused-variable` do
GCC). Atribuir um valor não conta como uso.

## Limites desta versão

Não há funções, strings, floats, arrays, entrada de dados, `for`, `break`,
`continue`, operadores lógicos ou comentários de bloco. As extensões opcionais
dos slides ficam para depois do pipeline completo. Mudanças nesta especificação
exigirão revisar gramática, lexer e testes.

## Exemplos da entrega

`fatorial.mini`, `if_else.mini`, `escopos.mini` e `pao_de_queijo.mini` são
válidos. `erro_lexico.mini` falha no lexer, `erro_sintatico.mini` no parser,
`erro_semantico.mini` e `semantico.mini` na semântica. Este último relata os
três erros independentes da aula 22. A CLI padrão gera TAC após a validação; -O seleciona TAC otimizado.
Não executa os comandos de saída e repetição.

O significado dinâmico descrito acima é o contrato da linguagem para a
execução futura. A entrega implementa frontend e middle-end, sem execução.
