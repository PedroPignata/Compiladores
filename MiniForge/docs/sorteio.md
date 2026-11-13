# Sorteio inteiro em mineirês

## Uso

```text
trem numero: inteirim = sorteia_so(1, 100);
mostra_so(numero);
```

`sorteia_so(minimo, maximo)` é uma expressão de tipo `inteirim`. Recebe duas
expressões inteiras e retorna um inteiro no intervalo **inclusivo**. Os limites
podem ser iguais (42 a 42 retorna 42), negativos ou calculados por expressões.
Booleanos não são convertidos em inteiros. Limites invertidos são erro de
execução com linha de origem, mesmo se o resultado não for usado.

A expressão não é uma função definida pelo usuário. Trata-se de uma operação
reservada da linguagem, implementada em todas as fases pertinentes.
O identificador completo continua sendo reconhecido antes da consulta às
reservadas: `sorteia_so2` é um nome comum, não uma chamada de sorteio.

## Momento e fonte do sorteio

O sorteio acontece **durante a execução**, a cada vez que a chamada é alcançada.
Compilar e imprimir tokens, AST ou TAC não sorteia valores. Rodar o mesmo TAC
novamente produz uma nova chamada ao gerador. Resultados podem se repetir.
Não se promete que partidas consecutivas sempre tenham segredos diferentes.

O executor usa `random.SystemRandom().randint`, alimentado pela aleatoriedade
do sistema operacional, sem semente fixa e sem dependência externa. Não há
opção de semente na CLI. Os limites são avaliados da esquerda para a direita;
chamadas aninhadas mantêm essa ordem.

## Integração por fase

| Fase | Alteração |
|---|---|
| Tokens/lexer | Reservada sorteia_so e delimitador vírgula |
| Parser | Reconhece dois argumentos separados por vírgula no nível fator |
| AST | Sorteio(minimo, maximo), com posição e filhos visitáveis |
| Semântica | Visita ambos os limites, exige int, anota int sem cascata |
| TAC | Emite random para temporário novo; texto: `t1 = sorteia 1, 100` |
| Otimizador | Invalida destino escrito, preserva sorteio alcançável e não dobra a chamada |
| Executor | Resolve limites, verifica ordem e sorteia no instante da instrução |

`random` usa os campos a1/a2 para limites e dest para resultado. A origem do
fonte acompanha a instrução. O sorteio é efeito observável e potencialmente
falho; um temporário não lido não autoriza remover a instrução. Código
comprovadamente inalcançável pode ser removido pelos passes normais.
Essa implementação mantém as pastas e responsabilidades do projeto.

## Aplicação no jogo

Depois de validar os limites, o fonte faz:

```text
uai (jogando) {
    segredo = sorteia_so(minimo, maximo);
}
```

A chamada fica antes do laço de palpites, de modo que o segredo permanece o
mesmo durante a partida. Ao iniciar outra execução, há novo sorteio. O jogo
exige mínimo positivo porque zero é seu comando para sair; essa restrição é
do jogo, não da expressão sorteia_so.

## Evidência

Os testes controlam somente a fonte de aleatoriedade para verificar dicas,
contagem e ordem de chamadas sem fragilidade probabilística. Também existem
execuções com SystemRandom real verificando limites, inclusive negativos e
grandes, e CLI com intervalo de um elemento. Os testes não exigem resultados
aleatórios diferentes como condição para passar.
Registro atual em [testes-sorteio.md](testes-sorteio.md).
