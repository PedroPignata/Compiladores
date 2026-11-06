# MiniForge — compilador de mineirês, sô

Projeto didático de Compiladores 2026.2, professora Lorena Bezerra.
**Pedro Dutra · Pedro Pignata · Lucas Rocha Dantas · Renato Portilho**

**Entrega `v0.3-semantica`, corte de 16/10/2026 (aula 22).** Esta atualização
integra o frontend da versão atual do grupo, entregue no ZIP v0.6-mineires,
sobre a estrutura inicial do mesmo projeto. A CLI valida léxico, sintaxe,
nomes, escopos e tipos, sem executar o programa-fonte. A data da integração
é 06/11/2026, sem reconstruir artificialmente entregas anteriores.

```text
trem n: inteirim = 5;
trem f: inteirim = 1;
enquanto_tiver (n > 0) {
    f = f * n;
    n = n - 1;
}
mostra_so(f);
```

Validar esse fatorial confirma a correção do frontend. Não calcula `120`.

## O mineirês em 1 minuto

| Mineirês | Papel | Conceito nos slides |
| --- | --- | --- |
| `trem x: inteirim = 1;` | declara variável inteira | `var x: int = 1;` |
| `trem ok: booleanim = eh_memo;` | declara variável booleana | `var ok: bool = true;` |
| `eh_memo` / `num_eh` | verdadeiro / falso | `true` / `false` |
| `uai (c) { ... } sinao { ... }` | condicional | `if (c) { ... } else { ... }` |
| `enquanto_tiver (c) { ... }` | repetição | `while (c) { ... }` |
| `mostra_so(x);` | saída | `print(x);` |

As palavras são escritas sem acento (o lexer aceita só ASCII em nomes); as
antigas (`var`, `while`...) viraram identificadores comuns. Operadores,
comentários `//`, blocos e regras de tipo e escopo não mudaram. As mensagens
também falam mineirês:

```text
1:3: erro léxico: caractere inválido '@', que trem é esse?
3:8: erro sintático: faltou ':', sô: achei 'inteirim'
linha 3: erro semântico: 'ausente' num foi declarado, sô
linha 2: erro semântico: 'b' é booleanim, mas tá recebendo inteirim
```

Especificação completa em [docs/especificacao.md](docs/especificacao.md); a
decisão de arquitetura que fez a troca caber em uma tabela está em
[docs/arquitetura.md](docs/arquitetura.md#mineirês-só-a-superfície-muda).

## Instalar e testar

Requer Python 3.10+. Dentro de `MiniForge/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

O compilador usa apenas a biblioteca padrão. O pytest serve aos testes.
A suíte desta entrega tem **377 testes**, incluindo os 42 arquivos de casos
(11 válidos, 13 inválidos sintáticos e 18 semânticos). Resultados, ambiente e
segunda revisão estão em [docs/testes.md](docs/testes.md).

## Comandos e combinações

```bash
python -m miniforge exemplos/fatorial.mini
python -m miniforge exemplos/fatorial.mini --tokens
python -m miniforge exemplos/fatorial.mini --ast
python -m miniforge exemplos/fatorial.mini --tipos
python -m miniforge exemplos/pao_de_queijo.mini --verificar
python -m miniforge exemplos/semantico.mini --contexto
```

| Opções | Última fase / saída |
| --- | --- |
| Sem opções, ou `--verificar` | Semântica e mensagem `tudo certim` |
| `--tokens` | Léxico e tokens, sem exigir sintaxe ou semântica |
| `--ast` | Parser e AST sem anotação, sem exigir semântica |
| `--tipos` | Semântica e AST anotada |
| `--tokens` com outras opções | Tokens primeiro, depois as fases solicitadas |
| `--ast --tipos` | AST sintática primeiro e AST anotada se a semântica passar |
| `--ast --verificar` | AST sintática e validação semântica |
| `--tipos --verificar` | AST anotada e mensagem de sucesso |
| `--contexto` | Acrescenta linha e `^` aos erros semânticos, sem mudar a fase escolhida |

Todas as combinações seguem essas regras, independentemente da ordem dos
argumentos. Saídas de fases anteriores podem aparecer se uma fase posterior
falhar. `--tac`, `--pilha`, `--vm-pilha`, `--stats` e `-O` são indisponíveis
e rejeitados com código 2. Não há geração de código, execução ou métricas.

Sucesso retorna 0. Leitura inválida ou análise com erro retorna 1. Argumentos
inválidos retornam 2. Erros e avisos vão para stderr. Avisos de variável não
lida não fazem a validação falhar e só aparecem quando não há erros.

A análise semântica verifica as 5 regras da aula 22 (declaração antes do
uso, sem redeclaração no mesmo escopo, tipo da expressão igual ao da variável
em `trem` e `=`, condição `booleanim` em `uai`/`enquanto_tiver` e a tabela de tipos dos
operadores) e lista todos os erros de uma vez, cada um com a linha do nó da
AST. Com erro, a CLI sai com código 1 e não segue para a geração de código. É a saída do slide de entrega adaptada ao mineirês:

```text
$ python -m miniforge exemplos/semantico.mini
linha 2: erro semântico: 'b' é booleanim, mas tá recebendo inteirim
linha 3: erro semântico: condição tem que ser booleanim, mas veio inteirim
linha 3: erro semântico: 'y' num foi declarado, sô
```

Não há erros em cascata: uma expressão com erro devolve `None` e quem a usa
não reclama de novo, então `mostra_so(z + 1 + 2);` gera só
`'z' num foi declarado, sô`. Uma declaração com inicializador errado ainda declara
o nome, para os usos seguintes não virarem `'x' num foi declarado, sô`.

Desafio da aula 22: `--contexto` mostra a linha do fonte com um `^` sob o
ponto do erro, no estilo GCC/Clang (os nós da AST agora guardam a coluna):

```text
$ python -m miniforge exemplos/semantico.mini --contexto
linha 2: erro semântico: 'b' é booleanim, mas tá recebendo inteirim
 2 | trem b: booleanim = x + 1;
   | ^
linha 3: erro semântico: condição tem que ser booleanim, mas veio inteirim
 3 | uai (x) { y = 2; }
   |      ^
linha 3: erro semântico: 'y' num foi declarado, sô
 3 | uai (x) { y = 2; }
   |           ^
```

Variáveis declaradas e nunca lidas geram só um aviso em stderr, sem mudar o
código de saída (se houver erros, só os erros são listados):

```text
$ python -m miniforge tests/casos/validos/derivacao.mini --verificar
linha 2: aviso: 'x' declarado e nunca usado, sô
tests/casos/validos/derivacao.mini: tudo certim, sem erros léxicos, sintáticos ou semânticos
```

`--tipos` imprime a AST depois da semântica, com o tipo anotado em cada
expressão (é o que a geração de TAC vai ler):

```text
$ python -m miniforge exemplos/if_else.mini --tipos
Programa
├── Decl valor: inteirim
│   └── Num 3 : inteirim
├── Decl pequeno: booleanim
│   └── Binario < : booleanim
│       ├── Var valor : inteirim
│       └── Num 5 : inteirim
...
```

## Estrutura e documentos

```text
miniforge/  __main__.py, tokens.py, lexer.py, ast.py, parser.py,
            simbolos.py, semantica.py, __init__.py
exemplos/   quatro programas válidos e quatro exemplos de erro
tests/      lexer, parser, casos, símbolos, semântica, tipos, mineirês e CLI
docs/       especificação, gramática, arquitetura, checkpoint e auditoria
apresentacao/  PPTX editável, PDF e roteiro desta entrega
```

- [Especificação](docs/especificacao.md) e [gramática](docs/gramatica.md).
- [Arquitetura e próximas fases](docs/arquitetura.md).
- [Checkpoint](docs/checkpoint.md) e [análise de lexer didático](docs/analise-lexer.md).
- [Matriz de requisitos](docs/matriz-requisitos.md).
- [Integração do ZIP e adaptações](docs/integracao.md).
- [Testes](docs/testes.md) e [demonstração](docs/demonstracao.md).

## Limitações e continuidade

Sem funções, strings, floats, vetores ou operadores lógicos. Os nomes usam
ASCII, comentários aceitam UTF-8. O parser para no primeiro erro sintático.
O atalho interno `parse(fonte)` pressupõe fonte lexicamente válido e não
inspeciona `Lexer.erros`; para validar arquivos use a CLI, que verifica todas
as fases. Não há limite de profundidade ou recuperação de estouro de recursão
para entradas patológicas, nem análise de valores ou de terminação de laços.

TAC, bytecode, VM, otimizações e artigo da A2 permanecem no ZIP completo
original para as próximas entregas. Não foram publicados como implementação
ativa. A branch `entrega/modulo-4-semantica` e o PR preservam o histórico,
sem merge automático ou criação retroativa de marcos.
