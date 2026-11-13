# Demonstração da versão vigente

Na pasta MiniForge/, com Python ativo, execute cada comando separadamente.
As saídas abaixo foram obtidas na revisão documental de 13/11/2026. Erros
intencionais retornam código 1. Sem --executar há compilação, não execução.
Instalação: [README](../README.md). Guias: [programas](../exemplos/README.md).

## Fatorial: gerar TAC

```bash
python -m miniforge exemplos/fatorial.mini
```

Código 0. Saída em stdout.

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

## Fatorial: executar

```bash
python -m miniforge exemplos/fatorial.mini --executar
```

Código 0. Saída em stdout.

```text
120
```

## Constantes: TAC original

```bash
python -m miniforge exemplos/constantes.mini --tac
```

Código 0. Saída em stdout.

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

## Constantes: TAC otimizado

```bash
python -m miniforge exemplos/constantes.mini --tac -O
```

Código 0. Saída em stdout.

```text
    base = 10
    lim = 100
    print 100
```

## Erros independentes com contexto

```bash
python -m miniforge exemplos/semantico.mini --verificar --contexto
```

Código 1. Diagnósticos em stderr.

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

## Erro léxico

```bash
python -m miniforge exemplos/erro_lexico.mini --verificar
```

Código 1. Diagnósticos em stderr.

```text
1:3: erro léxico: caractere inválido '@', que trem é esse?
4:9: erro léxico: caractere inválido '$', que trem é esse?
```

## Erro sintático

```bash
python -m miniforge exemplos/erro_sintatico.mini --verificar
```

Código 1. Diagnósticos em stderr.

```text
3:8: erro sintático: faltou ':', sô: achei 'inteirim'
```

## Árvore anotada

```bash
python -m miniforge exemplos/if_else.mini --tipos
```

Código 0. Saída em stdout.

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

## Calculadora Mineira

```bash
python -m miniforge exemplos/calculadora/interativa.mini --executar
python -m miniforge exemplos/calculadora/interativa.mini --executar -O
```

Na sessão, escolher 1, digitar 18 e 6: resultado 24. Escolher 4, digitar 2 e 5:
mensagem de resultado inválido sem mostrar zero truncado. Comparar com 0 / 5,
que é zero válido. Divisor zero também retorna ao menu. A opção 0 encerra.
Inspecione o fonte e o TAC numa chamada separada, sem combinar execução e inspeção.

## Adivinha o trem, sô!

```bash
python -m miniforge exemplos/adivinha/adivinha.mini --executar
python -m miniforge exemplos/adivinha/adivinha.mini --tac -O
```

O segredo é aleatório entre 1 e 100. Siga as dicas ou use 0 para abandonar.
Mostrar a chamada sorteia_so fora do laço e a instrução random preservada no TAC.
Não prometer que 40/80/65 acertam; são só exemplo de uma partida que sorteasse 65.
Para acerto previsível, configure temporariamente minimo e maximo iguais a 42,
execute e digite 42. Restaure os limites depois para manter a configuração padrão.
O [manual do jogo](../exemplos/adivinha/README.md) explica como editar o intervalo.

## Testes e plano de apoio

```bash
python -m pytest -q
python -m pytest -q tests/test_adivinha.py tests/test_sorteio.py
```

Resultado vigente em [testes.md](testes.md). A tabela de otimização é estática,
não medição de velocidade. Se não houver oportunidade segura de redução no
fatorial, isso é resultado esperado, não falha. Os dois TAC e as saídas reais
deste documento servem como apoio; não substituem afirmar o que foi executado.
A apresentação local não foi atualizada por esta revisão dos documentos do Git.
