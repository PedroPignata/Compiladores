# Demonstração para a professora

Instalação no README. Com ambiente ativado e dentro de MiniForge, executar separadamente. Erros retornam 1 intencionalmente.

## python -m miniforge exemplos/fatorial.mini

Código 0

```text
    n = 5
    f = 1
L1:
    t1 = n > 0
    ifFalse t1 goto L2
    t2 = f * n
    f = t2
    t3 = n - 1
    n = t3
    goto L1
L2:
    print f
```

## python -m miniforge exemplos/constantes.mini --tac

Código 0

```text
    t1 = 2 * 3
    t2 = t1 + 4
    base = t2
    t3 = base * 10
    lim = t3
    t4 = lim > 50
    ifFalse t4 goto L1
    print lim
    goto L2
L1:
    print 0
L2:
```

## python -m miniforge exemplos/constantes.mini --tac -O

Código 0

```text
    base = 10
    lim = 100
    print 100
```

## python -m miniforge exemplos/semantico.mini --contexto

Código 1

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

## python -m miniforge exemplos/erro_lexico.mini

Código 1

```text
1:3: erro léxico: caractere inválido '@', que trem é esse?
4:9: erro léxico: caractere inválido '$', que trem é esse?
```

## python -m miniforge exemplos/erro_sintatico.mini

Código 1

```text
3:8: erro sintático: faltou ':', sô: achei 'inteirim'
```

## python -m miniforge exemplos/if_else.mini --tipos

Código 0

```text
Programa
├── Decl valor: inteirim
│   └── Num 3 : inteirim
├── Decl pequeno: booleanim
│   └── Binario < : booleanim
│       ├── Var valor : inteirim
│       └── Num 5 : inteirim
├── Print
│   └── Var pequeno : booleanim
└── If
    ├── Binario > : booleanim
    │   ├── Var valor : inteirim
    │   └── Num 5 : inteirim
    ├── Bloco
    │   └── Print
    │       └── Num 1 : inteirim
    └── Bloco
        └── Print
            └── Num 0 : inteirim
```

## Conferências adicionais

```bash
python -m miniforge exemplos/fatorial.mini --tokens
python -m miniforge exemplos/escopos.mini --tac
python -m pytest -q tests/test_ir.py tests/test_otimizador.py tests/test_middleend.py
python -m pytest -q
```

Sem ganho: compare fatorial.mini com e sem -O; laços exigem conservadorismo.
Segurança: mostre o caso divisão por zero em test_middleend.py; a instrução permanece.
Plano B: saídas deste documento e PDF local. Não prometer imprimir 120: print f é TAC.


## Calculadora com entrada pelo teclado

Na raiz MiniForge/, abrir:

```bash
python3 -m exemplos.calculadora.interativa --detalhes
```

1. Escolher 1, digitar 18 e 6: observar o fonte mineirês, o TAC e o resultado 24.
2. Escolher 4, digitar 10 e 0: observar a mensagem e o retorno ao menu.
3. Escolher 4, digitar -7 e 2: resultado -3, divisão truncada para zero.
4. Escolher 0 para sair. Sem `--detalhes`, aparece apenas a interface de uso.

Explicação: Python faz a interface de teclado. A conta vira fonte mineirês e
passa pelas fases do MiniForge. O otimizador dobra a expressão e a interface
apresenta o literal final. Não há leitura pelo teclado na linguagem nem execução
geral de TAC. Essa distinção pode ser demonstrada pelo modo detalhado.
