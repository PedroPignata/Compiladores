# Checkpoint v0.2 — lexer, parser e AST (aula 16)

Autoavaliação dos 8 critérios do slide, reavaliada na integração de 06/11/2026. A demonstração em sala permanece pendente.

| # | Critério | Evidência | Situação |
| --- | --- | --- | --- |
| 1 | Lexer completo | `--tokens` reconhece todos os tokens da especificação (`test_todas_as_reservadas`, `test_todos_os_operadores_e_delimitadores`) | ok |
| 2 | Erros léxicos | Mensagem com `linha:coluna`; não aborta no primeiro erro (`exemplos/erro_lexico.mini` lista `1:3` e `4:9`) | ok |
| 3 | Parser completo | Todos os 11 casos de `tests/casos/validos/` e os exemplos válidos geram AST | ok |
| 4 | Erros sintáticos | Os 13 casos de `tests/casos/invalidos/` falham com a mensagem anotada na 1ª linha | ok |
| 5 | Precedência e associatividade | `test_precedencia` (`1+2*3`) e `test_associatividade_esquerda` (`10-3-2`) | ok |
| 6 | Testes automatizados | `python -m pytest -q`: 377 testes aprovados na entrega semântica | ok |
| 7 | Repositório | Histórico inicial preservado; atualização única do trabalho do grupo, sem inventar commits individuais | ver PR e tag `v0.3-semantica` |
| 8 | Documentação | README (instalar, executar, testar); `especificacao.md` e `gramatica.md` atualizados | ok |

O critério 7 só fica "ok" depois do commit, da tag e do push no GitHub
(comandos no README). Não se cria tag retroativa `v0.2-checkpoint`. A demonstração presencial não foi realizada por esta integração.

## Roteiro da demonstração (3 min)

```bash
git log --oneline | head -5
pytest -q
python -m miniforge exemplos/fatorial.mini --tokens
python -m miniforge exemplos/fatorial.mini --ast
python -m miniforge exemplos/erro_lexico.mini
python -m miniforge exemplos/erro_sintatico.mini
```

Saídas esperadas dos dois últimos comandos:

```text
1:3: erro léxico: caractere inválido '@', que trem é esse?
4:9: erro léxico: caractere inválido '$', que trem é esse?
3:8: erro sintático: faltou ':', sô: achei 'inteirim'
```

## Problemas comuns conferidos (slide 5)

| Sintoma | Situação no MiniForge |
| --- | --- |
| Parser entra em laço infinito | Todo caminho consome um token ou lança `ErroSintatico`; `consumir()` não passa do EOF |
| `10 - 3 - 2` resulta em `(10-(3-2))` | `soma` e `termo` usam `while` do Python (`test_associatividade_esquerda`) |
| `RecursionError` em `soma` | Gramática sem recursão à esquerda: `soma → termo { op termo }` |
| `whilex` vira `WHILE` + `x` | Lexer lê o lexema completo antes de consultar `RESERVADAS` |
| `<=` vira `<` e `=` | Operadores de 2 caracteres testados antes |
| Coluna errada após quebra de linha | Em `\n`: `linha += 1`, `coluna = 1` (`test_posicao`) |
| `x = 1; }` é aceito sem erro | `programa()` repete até `EOF`; `comando()` acusa o `}` (`invalidos/chave_sobrando.mini`) |

## O que cada fase garante para a próxima

O lexer garante que só existem tokens válidos. O parser garante que a
sequência de tokens obedece à gramática. Nenhum dos dois sabe se `x` foi
declarada ou se `eh_memo + 1` faz sentido: isso é trabalho da análise
semântica, a próxima fase (tabela de símbolos na aula 20).
