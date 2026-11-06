# Demonstração reproduzível do frontend

Dentro de MiniForge, com o ambiente ativado, executar cada comando abaixo.
Os exemplos de erro retornam 1 intencionalmente. Reserve cerca de 3 minutos.

1. `python -m miniforge exemplos/fatorial.mini`

```text
exemplos/fatorial.mini: tudo certim, sem erros léxicos, sintáticos ou semânticos
```

2. `python -m miniforge exemplos/fatorial.mini --tokens`

Primeiras linhas (espaços de alinhamento podem variar por terminal):

```text
2:1   VAR          'trem'
2:6   ID           'n'
2:7   DOIS_PONTOS  ':'
2:9   INT          'inteirim'
```

3. `python -m miniforge exemplos/if_else.mini --tipos`

A AST começa em `Programa`, mostra `Decl valor: inteirim` e `Num 3 : inteirim`,
e depois `Decl pequeno: booleanim` e `Binario < : booleanim`.

4. `python -m miniforge exemplos/semantico.mini --contexto`

```text
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

5. `python -m pytest -q` termina com `377 passed` (tempo varia).

Opcional: demonstrar `--ast` com `erro_semantico.mini`, que aceita a sintaxe,
e depois repetir sem opções para mostrar o nome não declarado. Mostrar
`exemplos/escopos.mini --tipos` para comparar o `x` interno e o externo.

Plano B: os comandos e saídas estão neste documento e na apresentação PDF.
Não apresentar `120`, `72` ou `22` como resultados executados nesta entrega.
